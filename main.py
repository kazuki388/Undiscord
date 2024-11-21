#!/usr/bin/env python3

import logging
import os
import re
import sys
import time
from datetime import datetime, timedelta
from functools import lru_cache, partial
from itertools import chain
from operator import setitem
from pathlib import Path
from typing import Any, Callable, Dict, Optional

try:
    import attr
    import click
    import orjson
    import requests
    from requests import Response as RequestsResponse
    from requests.exceptions import RequestException
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.panel import Panel
    from rich.progress import (
        BarColumn,
        Progress,
        SpinnerColumn,
        TaskProgressColumn,
        TextColumn,
    )
    from rich.table import Table
    from schema import And, Schema, Use
    from schema import Optional as SchemaOptional
    from typing_extensions import TypedDict

except ImportError:
    print(
        "Please install required packages: pip install requests rich schema click attrs orjson typing-extensions"
    )
    sys.exit(1)


class DiscordResponse(TypedDict, total=False):
    status_code: int
    retry_after: float


DISCORD_API_BASE_URL: str = "https://discord.com/api/v9"
MAX_RETRIES: int = 3
INITIAL_BACKOFF: int = 1
MAX_CONSECUTIVE_403_ERRORS: int = 5

CONFIG_SCHEMA = Schema(
    {
        "token": str,
        SchemaOptional("guild"): str,
        SchemaOptional("channel"): str,
        SchemaOptional("author"): str,
        SchemaOptional("min_id"): str,
        SchemaOptional("max_id"): str,
        SchemaOptional("has_link"): bool,
        SchemaOptional("has_file"): bool,
        SchemaOptional("content"): str,
        SchemaOptional("pattern"): str,
        SchemaOptional("include_nsfw"): bool,
        SchemaOptional("include_pinned"): bool,
        SchemaOptional("delete_delay"): And(Use(float), lambda n: n > 0),
        SchemaOptional("search_delay"): And(Use(float), lambda n: n > 0),
    }
)


@attr.s(auto_attribs=True, slots=True)
class Stats:
    start_time: datetime = attr.Factory(datetime.now)
    deleted: int = attr.Factory(int)
    failed: int = attr.Factory(int)
    total: int = attr.Factory(int)
    throttled_count: int = attr.Factory(int)
    throttled_total_time: float = attr.Factory(float)
    consecutive_403: int = attr.Factory(int)


logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=(RichHandler(rich_tracebacks=True),),
)
logger = logging.getLogger("undiscord")

console = Console(color_system="auto", highlight=False)


class Deletion:

    def __init__(self) -> None:
        self.session = requests.Session()
        self.stats = Stats()
        self.progress: Optional[Progress] = None
        self.task_id: Optional[str] = None
        self.log_file = Path("undiscord.log").resolve()

    def setup_session(self, token: str) -> None:
        self.session.headers.update(
            {"Authorization": token, "Content-Type": "application/json"}
        )
        console.print("[cyan]Session headers set up[/cyan]")

    def log_to_file(self, message: str) -> None:
        with memoryview(
            f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {message}\n".encode("utf-8")
        ) as mv:
            os.write(
                os.open(self.log_file, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644),
                mv,
            )

    @staticmethod
    @lru_cache(typed=False)
    def _calc_backoff(
        retry_count: int = 0, *, _pow: Callable[[int, int], float] = pow
    ) -> float:
        return INITIAL_BACKOFF * _pow(2, retry_count) if retry_count >= 0 else 0.0

    def handle_rate_limit(self, response: RequestsResponse, operation: str) -> float:
        retry_after: float = (
            float(response.json().get("retry_after", 1))
            if hasattr(response, "json") and callable(response.json)
            else 1.0
        )

        self.stats.throttled_count += 1
        self.stats.throttled_total_time += retry_after

        wait_time: float = retry_after * 1.5
        logger.warning(f"Rate limited during {operation}. Waiting {wait_time:.2f}s...")
        return wait_time

    def search_messages(
        self,
        guild_id: str,
        channel_id: Optional[str],
        author_id: Optional[str] = None,
        min_id: Optional[str] = None,
        max_id: Optional[str] = None,
        has_link: bool = False,
        has_file: bool = False,
        content: Optional[str] = None,
        include_nsfw: bool = False,
        offset: int = 0,
        retry_count: int = 0,
    ) -> Dict:
        url = f"{DISCORD_API_BASE_URL}/{'channels' if guild_id == '@me' else 'guilds'}/{guild_id}/messages/search"

        params = {
            k: v
            for k, v in (
                ("author_id", author_id),
                ("channel_id", channel_id),
                ("min_id", min_id),
                ("max_id", max_id),
                ("sort_by", "timestamp"),
                ("sort_order", "desc"),
                ("offset", offset),
                ("include_nsfw", include_nsfw),
                (
                    "has",
                    next(
                        (
                            x
                            for x in ("link" if has_link else "file", None)
                            if has_link or has_file
                        ),
                        None,
                    ),
                ),
                ("content", content),
            )
            if v is not None and v != ""
        }

        console.print(
            f"[cyan]Searching messages {'in specific channel' if channel_id else 'across all channels in the server'}[/cyan]"
        )
        console.print(
            "[cyan]Search parameters:[/cyan]\n[cyan]"
            + "\n".join(f"  {k}: {v}" for k, v in params.items())
            + "[/cyan]"
        )

        try:
            resp = self.session.get(url, params=params)
            status = resp.status_code

            console.print(f"[cyan]Search response status: {status}[/cyan]")
            status != 200 and console.print(
                f"[yellow]Response content: {resp.text}[/yellow]"
            )

            match status:
                case 202:
                    console.print(
                        "Channel not indexed, waiting for Discord to index..."
                    )
                    time.sleep(1.5)
                    return self.search_messages(
                        guild_id,
                        channel_id,
                        author_id,
                        min_id,
                        max_id,
                        has_link,
                        has_file,
                        content,
                        include_nsfw,
                        offset,
                    )

                case 429:
                    wait_time = self.handle_rate_limit(resp, "search")
                    time.sleep(wait_time)
                    return self.search_messages(
                        guild_id,
                        channel_id,
                        author_id,
                        min_id,
                        max_id,
                        has_link,
                        has_file,
                        content,
                        include_nsfw,
                        offset,
                    )

                case 403:
                    self.stats.consecutive_403 += 1
                    console.print("[red]Permission denied for search request[/red]")
                    if self.stats.consecutive_403 >= MAX_CONSECUTIVE_403_ERRORS:
                        console.print("Too many permission errors. Stopping...")
                    return {"messages": []}

            resp.raise_for_status()
            self.stats.consecutive_403 = 0

            data = resp.json()
            console.print(
                f"[cyan]Found {len(data.get('messages', []))} message(s)[/cyan]"
            )
            return data

        except RequestException as e:
            console.print(f"[red]Request error: {str(e)}[/red]")
            if retry_count < MAX_RETRIES:
                wait_time = self._calc_backoff(retry_count)
                console.print(f"Network error: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
                return self.search_messages(
                    guild_id,
                    channel_id,
                    author_id,
                    min_id,
                    max_id,
                    has_link,
                    has_file,
                    content,
                    include_nsfw,
                    offset,
                    retry_count + 1,
                )
            console.print(f"Failed to search messages after {MAX_RETRIES} retries")
            return {"messages": []}

    def delete_message(
        self, channel_id: str, message_id: str, retry_count: int = 0
    ) -> bool:
        url = f"{DISCORD_API_BASE_URL}/channels/{channel_id}/messages/{message_id}"

        try:
            resp = self.session.delete(url, timeout=5.0)

            match resp.status_code:
                case 429:
                    time.sleep(self.handle_rate_limit(resp, "delete"))
                    return self.delete_message(channel_id, message_id, retry_count)

                case 403:
                    self.stats.consecutive_403 += 1
                    console.print(f"Permission denied for message {message_id}")
                    return False

                case _:
                    resp.raise_for_status()
                    self.stats.consecutive_403 = 0
                    return True

        except RequestException as e:
            console.print(
                Panel(
                    f"[red]Failed to delete message {message_id}[/red]\n"
                    f"[yellow]Error: {str(e)}[/yellow]",
                    title="Error",
                    border_style="red",
                )
            )
            return False

    def run(
        self,
        token: str,
        guild_id: str,
        channel_id: Optional[str] = None,
        author_id: Optional[str] = None,
        min_id: Optional[str] = None,
        max_id: Optional[str] = None,
        has_link: bool = False,
        has_file: bool = False,
        content: Optional[str] = None,
        include_nsfw: bool = False,
        include_pinned: bool = False,
        pattern: Optional[str] = None,
        delete_delay: float = 1.0,
        search_delay: float = 1.0,
    ) -> None:
        if not click.confirm(
            "\n[red]Warning[/red]\n"
            "This action will permanently delete messages and cannot be undone.\n"
            "Do you want to continue?",
            default=True,
        ):
            console.print("[yellow]Operation cancelled by user[/yellow]")
            return

        self.setup_session(token)
        self.stats.start_time = datetime.now()
        regex = re.compile(pattern, re.I | re.M | re.S) if pattern else None

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            self.progress = progress
            assert self.progress is not None
            self.task_id = self.progress.add_task("Deleting messages...")

            try:
                offset = 0
                while True:
                    data = self.search_messages(
                        guild_id=guild_id,
                        channel_id=channel_id,
                        author_id=author_id,
                        min_id=min_id,
                        max_id=max_id,
                        has_link=has_link,
                        has_file=has_file,
                        content=content,
                        include_nsfw=include_nsfw,
                        offset=offset,
                    )

                    messages = tuple(
                        filter(
                            lambda msg: (
                                msg.get("hit")
                                and (include_pinned or not msg.get("pinned"))
                                and (not regex or regex.search(msg.get("content", "")))
                            ),
                            chain.from_iterable(data.get("messages", [])),
                        )
                    )

                    if not messages:
                        break

                    self.stats.total = data.get("total_results", 0)

                    for message in messages:
                        if self.stats.consecutive_403 >= MAX_CONSECUTIVE_403_ERRORS:
                            console.print("Too many permission errors. Stopping...")
                            return

                        success = self.delete_message(
                            channel_id=message["channel_id"], message_id=message["id"]
                        )

                        self.stats.deleted += success
                        self.stats.failed += not success
                        success and console.print(f"Deleted message {message['id']}")

                        self._print_progress()
                        time.sleep(delete_delay)

                    offset += len(messages)
                    time.sleep(search_delay)

            except KeyboardInterrupt:
                console.print("\n[yellow]Stopped by user[/yellow]")
            finally:
                self._print_final_stats()

    def _print_progress(self) -> None:
        if not (self.progress and self.task_id is not None):
            return

        completed: int = self.stats.deleted + self.stats.failed
        total: int = self.stats.total

        if completed <= 0:
            return

        elapsed: timedelta = datetime.now() - self.stats.start_time
        elapsed_seconds: float = elapsed.total_seconds()
        rate: float = completed / elapsed_seconds
        remaining: float = (total - completed) / rate if rate else float("inf")
        eta: datetime = datetime.now() + timedelta(seconds=remaining)

        description = (
            f"[cyan]Deleting messages...[/cyan]\n"
            f"[green]{completed}/{total} processed[/green] - "
            f"[yellow]{rate:.1f} msg/s[/yellow] - "
            f"[blue]ETA: {eta.strftime('%H:%M:%S')}[/blue]"
        )

        self.progress.update(
            self.task_id,
            completed=completed,
            total=total,
            description=description,
            refresh=True,
        )

    def _print_final_stats(self) -> None:
        duration = (datetime.now() - self.stats.start_time).total_seconds()
        total_messages = self.stats.deleted + self.stats.failed

        stats_data = [
            (
                "Duration",
                f"{int(duration//3600):02d}:{int((duration%3600)//60):02d}:{int(duration%60):02d}",
            ),
            ("Total Messages", str(self.stats.total)),
            ("Successfully Deleted", str(self.stats.deleted)),
            ("Failed to Delete", str(self.stats.failed)),
            (
                "Deletion Rate",
                f"{(total_messages/duration if duration else 0):.2f} messages/second",
            ),
            ("Times Rate Limited", str(self.stats.throttled_count)),
            ("Total Time Throttled", f"{self.stats.throttled_total_time:.1f}s"),
        ]

        table = Table(
            title="Deletion Statistics",
            header_style="bold magenta",
            show_header=True,
            box=None,
        )
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", justify="right", style="green", no_wrap=True)

        for metric, value in stats_data:
            table.add_row(metric, value)

        console.print("\n")
        console.print(table)

        self.log_to_file(
            f"Deletion completed - Total: {self.stats.total}, Deleted: {self.stats.deleted}, Failed: {self.stats.failed}"
        )

        # 添加完成动画
        with Progress(
            SpinnerColumn(),
            TextColumn("[green]Operation completed successfully![/green]"),
            transient=True,
        ) as progress:
            progress.add_task("", total=None)
            time.sleep(1)

        console.print("\n[bold green]All done![/bold green]")

    @staticmethod
    @lru_cache(maxsize=None)
    def load_config(config_file: str) -> Dict[str, Any]:
        try:
            path = Path(config_file)
            config = orjson.loads(path.read_bytes())
            if not isinstance(config, dict):
                raise TypeError("Config must be a dictionary")
            return CONFIG_SCHEMA.validate(config) or {}
        except (OSError, orjson.JSONDecodeError, TypeError) as e:
            logger.error("Config load failed: %s", str(e))
            return {}
        except Exception as e:
            logger.critical("Unexpected error loading config: %s", str(e))
            return {}


def prompt_config() -> Dict[str, Any]:
    config: Dict[str, Any] = {}
    setter = partial(setitem, config)

    console.print(
        Panel.fit(
            "[bold cyan]Configuration Wizard[/bold cyan]\n"
            "[dim]Enter your settings below. Press Enter for default values.[/dim]",
            border_style="cyan",
        )
    )

    # Token 输入添加样式
    token = click.prompt("[bold]Discord Token[/bold]", type=str, show_default=False)
    setter("token", token)
    console.print("[green]✓[/green] Token set successfully\n")

    # 范围选择添加分组
    console.print("[bold cyan]Scope Selection[/bold cyan]")
    scope_choice = click.prompt(
        "Select scope\n"
        "  [1] Server-wide\n"
        "  [2] Direct Messages\n"
        "  [3] Specific Channel",
        type=click.Choice(["1", "2", "3"]),
        default="1",
    )

    # 根据选择添加相应的设置
    if scope_choice == "1":
        setter("guild", click.prompt("Server ID", type=str))
    elif scope_choice == "2":
        setter("guild", "@me")
    elif scope_choice == "3":
        setter("channel", click.prompt("Channel ID", type=str))

    author_map = {
        "1": lambda: None,
        "2": lambda: setter("author", "self"),
        "3": lambda: setter("author", click.prompt("User ID", type=str)),
    }
    author_map[
        click.prompt(
            "Delete messages from (1: Everyone, 2: Only me, 3: Specific user)",
            type=click.Choice(["1", "2", "3"]),
            default="2",
        )
    ]()

    if click.confirm("Configure advanced options?", default=False):
        if click.confirm("Filter by content?", default=False):
            filter_map = {
                "1": lambda: setter("content", click.prompt("Text content", type=str)),
                "2": lambda: setter("pattern", click.prompt("Regex pattern", type=str)),
                "3": lambda: setter("has_link", True),
                "4": lambda: setter("has_file", True),
            }
            filter_map[
                click.prompt(
                    "Filter type (1: Text content, 2: Regex pattern, 3: Has link, 4: Has file)",
                    type=click.Choice(["1", "2", "3", "4"]),
                    default="1",
                )
            ]()

        setter("include_nsfw", click.confirm("Include NSFW channels?", default=False))
        setter(
            "include_pinned", click.confirm("Include pinned messages?", default=False)
        )

        if click.confirm("Configure delays?", default=False):
            setter(
                "delete_delay",
                click.prompt(
                    "Delay between deletions (seconds)", type=float, default=1.0
                ),
            )
            setter(
                "search_delay",
                click.prompt(
                    "Delay between searches (seconds)", type=float, default=1.0
                ),
            )

    return config


@click.command()
@click.option("--config", type=str, help="Path to config file")
@click.option("--interactive", "-i", is_flag=True, help="Use interactive configuration")
@click.option("--token", type=str, help="Discord Token")
@click.option("--guild", type=str, help="Guild/Server ID")
@click.option("--channel", type=str, help="Channel ID (optional)")
@click.option("--author", type=str, help="Author ID to delete messages from (optional)")
@click.option("--has-link", is_flag=True, help="Only delete messages containing links")
@click.option("--has-file", is_flag=True, help="Only delete messages containing files")
@click.option("--content", type=str, help="Content filter")
@click.option("--pattern", type=str, help="Regex pattern filter")
@click.option("--include-nsfw", is_flag=True, help="Include NSFW channels")
@click.option("--include-pinned", is_flag=True, help="Include pinned messages")
@click.option(
    "--delete-delay", type=float, default=1.0, help="Delay between deletions in seconds"
)
@click.option(
    "--search-delay", type=float, default=1.0, help="Delay between searches in seconds"
)
def cli(
    config: Optional[str],
    interactive: bool,
    token: Optional[str],
    guild: Optional[str],
    channel: Optional[str],
    author: Optional[str],
    has_link: bool,
    has_file: bool,
    content: Optional[str],
    pattern: Optional[str],
    include_nsfw: bool,
    include_pinned: bool,
    delete_delay: float,
    search_delay: float,
) -> None:
    console.print(
        Panel.fit(
            """[bold blue]Discord Message Deletion Tool[/bold blue]
[cyan]Version 1.0[/cyan]
[dim]A tool to bulk delete Discord messages[/dim]""",
            border_style="blue",
            padding=(1, 2),
            title="Welcome",
            subtitle="Press Ctrl+C to exit",
        )
    )

    config_data: Dict[str, Any] = {}

    match (interactive, bool(config), bool(token and guild)):
        case (True, _, _):
            config_data = prompt_config()
        case (_, True, _):
            console.print("[cyan]Loading config file...[/cyan]")
            if config is None:
                console.print("[red]Error: No config file provided[/red]")
                sys.exit(1)
            config_data = Deletion().load_config(config)
        case (_, _, True):
            config_data = dict(
                zip(
                    (
                        "token",
                        "guild",
                        "channel",
                        "author",
                        "has_link",
                        "has_file",
                        "content",
                        "pattern",
                        "include_nsfw",
                        "include_pinned",
                        "delete_delay",
                        "search_delay",
                    ),
                    (
                        token,
                        guild,
                        channel or "",
                        author or "",
                        has_link,
                        has_file,
                        content,
                        pattern,
                        include_nsfw,
                        include_pinned,
                        delete_delay,
                        search_delay,
                    ),
                )
            )
        case _:
            console.print(
                "[red]Error: Must provide either --config, --interactive, "
                "or --token and guild options[/red]"
            )
            sys.exit(1)

    console.print(
        "[cyan]Using configuration:[/cyan]\n[cyan]"
        + "\n".join(
            f"  {k}: {'*' * 8 if k == 'token' else v}" for k, v in config_data.items()
        )
        + "[/cyan]"
    )

    main(config_data=config_data)


def main(config_data: Dict[str, Any]) -> None:
    match config_data.get("token"):
        case None:
            console.print("[red]Error: token is required[/red]")
            sys.exit(1)
        case token:
            if config_data.get("author") == "self":
                try:
                    config_data["author"] = requests.get(
                        f"{DISCORD_API_BASE_URL}/users/@me",
                        headers={"Authorization": token},
                    ).json()["id"]
                except Exception as e:
                    console.print(f"[red]Error getting user ID: {str(e)}[/red]")
                    sys.exit(1)

            match (config_data.get("guild"), config_data.get("channel")):
                case (None | "", None | ""):
                    console.print(
                        "[yellow]No guild or channel specified. Please provide either guild ID or channel ID.[/yellow]"
                    )
                    if click.confirm(
                        "Would you like to enter a guild ID now?", default=True
                    ):
                        config_data["guild"] = click.prompt("Server ID", type=str)
                    else:
                        console.print("[red]A guild ID or channel ID is required[/red]")
                        sys.exit(1)

            console.print("[cyan]Starting deletion process...[/cyan]")
            try:

                Deletion().run(
                    token=token,
                    guild_id=config_data.get("guild", ""),
                    channel_id=config_data.get("channel", ""),
                    author_id=config_data.get("author"),
                    min_id=config_data.get("min_id"),
                    max_id=config_data.get("max_id"),
                    has_link=config_data.get("has_link", False),
                    has_file=config_data.get("has_file", False),
                    content=config_data.get("content"),
                    pattern=config_data.get("pattern"),
                    include_nsfw=config_data.get("include_nsfw", False),
                    include_pinned=config_data.get("include_pinned", False),
                    delete_delay=config_data.get("delete_delay", 1.0),
                    search_delay=config_data.get("search_delay", 1.0),
                )

            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")
                sys.exit(1)


if __name__ == "__main__":
    cli()
