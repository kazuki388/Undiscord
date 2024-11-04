# Undiscord

The **Undiscord** userscript provides a powerful bulk message deletion tool for Discord. It allows you to delete multiple messages at once with advanced filtering options.

> **Important Notes**:
> - It is recommended to use this script only with Tampermonkey on Chrome. Install the old 5.2.3 version first, then replace all code with 5.2.3 (reopen) in the script editor.
> - Do not use password manager to save Discord password in Chrome when using this script.
> - Due to Discord's thread limit, it is recommended to use this script along with tools like [AutoCloseReopenThread](https://github.com/Xialai-Kulimi/AutoCloseReopenThread.git) to manage thread states.

## Features

- Delete messages in any channel or DM conversation
- Filter messages by content, date range, or message ID
- Delete messages containing links or files
- Import message history from Discord data archive
- Support for deleting messages in archived threads
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
4. Click "Delete" to start the process
5. Monitor progress in the log window

### Filtering Options

- **Author ID**: Delete messages from a specific user
- **Search**: Delete messages containing specific text
- **Has Link/File**: Delete messages with links or attachments
- **Pattern**: Delete messages matching a regular expression
- **Date Range**: Delete messages between specific dates
- **Message Range**: Delete messages between specific message IDs

### Advanced Settings

- **Search Delay**: Time between message fetching requests (ms)
- **Delete Delay**: Time between message deletions (ms)
- **Authorization Token**: Manual token entry if auto-detection fails
- **Include NSFW**: Enable searching in NSFW channels
- **Include Pinned**: Include pinned messages in deletion

## Configuration

The script can be customized by adjusting the following settings in the UI:

- **Search Delay**: `100ms` to `60000ms` (Default: `30000ms`)
- **Delete Delay**: `50ms` to `10000ms` (Default: `1000ms`)
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
