# Undiscord

The **Undiscord** userscript provides a powerful bulk message deletion tool for Discord. It allows you to delete multiple messages at once with advanced filtering options.

> **Important Notes**:
> - It is recommended to use this script only with Tampermonkey on Chrome. Install the 5.2.3 version first, then replace all code with 5.2.4 in the script editor.
> - Do not use password manager to save Discord password in Chrome when using this script.
> - Due to Discord's thread limit, it is recommended to use this script along with tools like [AutoCloseReopenThread](https://github.com/Xialai-Kulimi/AutoCloseReopenThread.git) to manage thread states.

## Features

- Delete messages in any channel, DM conversation or thread
- Filter messages by content, date range, or message ID
- Delete messages containing links or files
- Filter messages that have no attachments
- Import message history from Discord data archive
- Support for deleting messages in archived threads with auto-reopen
- Customizable search and deletion delays
- Progress tracking with estimated time remaining
- Streamer mode to hide sensitive information
- Interactive message picker for selecting date ranges
- Support for bulk deletion across multiple channels
- Dynamic throttling to avoid rate limits
- Comprehensive logging and error reporting
- Automatic token detection
- Responsive and draggable UI window

## Usage

### Installation

1. Install a userscript manager like Tampermonkey
2. Install the script from [Greasy Fork](https://greasyfork.org/en/scripts/406540-undiscord-delete-all-messages-in-a-discord-channel-or-dm-bulk-deletion)
3. Refresh your Discord tab

### Basic Steps

1. Click the trash icon in Discord's toolbar to open the deletion interface
2. Select the channel where you want to delete messages
3. Configure filters and options as needed
4. Click `Delete` to start the process
5. Monitor progress in the log window

### Channel Selection

- **Server Channel**: Click `current` to automatically fill the current server and channel IDs
- **DM/Group**: The Server ID will be automatically set to `@me` for direct messages
- **Thread**: When selecting a thread, the parent channel ID will be automatically filled
- **Multiple Channels**: You can enter multiple channel IDs separated by commas for batch deletion

### Filtering Options

- **Author ID**: Delete messages from a specific user (click `me` to use your own ID)
- **Search**: Delete messages containing specific text
- **Has Link**: Delete messages containing links
- **Has File**: Delete messages containing attachments
- **Has No File**: Delete messages without any attachments
- **Pattern**: Delete messages matching a regular expression
- **Date Range**: Delete messages between specific dates
- **Message Range**: Delete messages between specific message IDs (use `Pick` buttons to select messages visually)
- **Include Pinned**: When checked, pinned messages will also be deleted
- **Include NSFW**: Enable searching in NSFW channels

## Configuration

The script can be customized by adjusting the following settings in the UI:

- **Search Delay**: Time between message fetching requests (`100ms` to `60000ms`, Default: `30000ms`)
- **Delete Delay**: Time between message deletions (`50ms` to `10000ms`, Default: `1000ms`)
- **Rate Limit Prevention**: Enable to automatically adjust delays to avoid Discord's rate limits
- **Authorization Token**: Manual token entry if auto-detection fails
- **Include NSFW**: Enable searching in NSFW channels
- **Include Pinned**: Include pinned messages in deletion
- **Auto Scroll**: Automatically scroll the log window
- **Streamer Mode**: Hide sensitive information in the UI

## Safety Features

- Confirmation prompt before starting deletion
- Preview of messages to be deleted
- Ability to stop the process at any time
- Rate limit handling to prevent account flagging
- Automatic delay adjustment based on Discord's response

## Disclaimer

Use this script responsibly. Mass deletion of messages may be against Discord's terms of service in certain cases. The authors are not responsible for any consequences of using this script.
