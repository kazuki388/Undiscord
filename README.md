# Undiscord

A Discord message deletion utility implemented in Python. Inspired by [undiscord-cli](https://github.com/ShivamB25/undiscord-cli). For full documentation and features, please see the [main branch README](https://github.com/kazuki388/Undiscord/blob/main/README.md).

## Installation

1. Clone the repository
2. Install required dependencies

## Usage

### Interactive Mode (Recommended for first-time users)

Run the tool in interactive mode to be guided through the configuration:

```bash
python main.py -i
```

The wizard will help you configure:

- Discord token
- Server/Channel selection
- Message filtering options
- Deletion delays

### Using Command Line Arguments

```bash
python main.py --token "your-token" --guild "server-id" [OPTIONS]
```

### Using a Config File

Create a `config.json` file:

```json
{
    "token": "your-discord-token",
    "guild": "server-id",
    "channel": "channel-id",
    "author": "self",
    "has_link": false,
    "has_file": false,
    "content": "text to match",
    "pattern": "regex pattern",
    "include_nsfw": false,
    "include_pinned": false,
    "delete_delay": 1.0,
    "search_delay": 1.0
}
```

Then run:

```bash
python main.py --config config.json
```

## Getting Your Discord Token

> [!WARNING]
> Never share your Discord token with anyone. It provides full access to your account.

1. Open Discord in your browser
2. Press <kbd>F12</kbd> to open [DevTools](https://developer.chrome.com/docs/devtools/overview)
3. Go to [Console](https://developer.chrome.com/docs/devtools/console/) tab
4. Type into the console

   ```js
   (webpackChunkdiscord_app.push([[''],{},e=>{m=[];for(let c in e.c)m.push(e.c[c])}]),m).find(m=>m?.exports?.default?.getToken!==void 0).exports.default.getToken()
   ```

5. Copy the token value

## Configuration Options

| Option | Type | Description | Default |
|:------:|:----:|-------------|:-------:|
| `token` | TEXT | Your Discord authentication token | Required |
| `guild` | TEXT | Target server/guild ID | - |
| `channel` | TEXT | Target channel ID within the guild | - |
| `author` | TEXT | Filter by message author ID (`self` for your messages) | - |
| `has_link` | FLAG | Filter messages containing URLs | `false` |
| `has_file` | FLAG | Filter messages with attachments | `false` |
| `content` | TEXT | Filter by message text content | - |
| `pattern` | TEXT | Filter using regex pattern matching | - |
| `include_nsfw` | FLAG | Include NSFW channel messages | `false` |
| `include_pinned` | FLAG | Include pinned messages | `false` |
| `delete_delay` | FLOAT | Time between message deletions (seconds) | `1.0` |
| `search_delay` | FLOAT | Time between search operations (seconds) | `1.0` |
