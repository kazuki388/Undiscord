# Undiscord

A Discord message deletion utility implemented as a userscript. Fork of [victornpb/undiscord](https://github.com/victornpb/undiscord).

## Requirements
- Tampermonkey browser extension (Chromium-based browsers)
- Initial deployment of v5.2.3, followed by upgrade to v5.2.4
- Disabled password manager during Discord authentication

## Branches

- **[Archive](https://github.com/kazuki388/Undiscord/tree/archive)**: Stable, tested versions
- **[Feature](https://github.com/kazuki388/Undiscord/tree/feat/PR)**: Enhanced functionality with recent updates
- **[Python](https://github.com/kazuki388/Undiscord/tree/feat/Python)**: CLI implementation
- **[Main](https://github.com/kazuki388/Undiscord/tree/main)**: Documentation only

## Features

- Concurrent message deletion across channels and threads
- Advanced filtering with regex and metadata matching
- Discord data archive integration
- Automated thread state management
- Rate limiting with dynamic throttling
- Real-time progress monitoring
- Privacy mode to hide sensitive information
- Interactive message selection
- Multi-channel batch processing
- Comprehensive logging

## Installation

1. Install Tampermonkey
2. Install script via [Greasy Fork](https://greasyfork.org/en/scripts/406540-undiscord-delete-all-messages-in-a-discord-channel-or-dm-bulk-deletion)
3. Clear Discord cache

## Usage

1. Click toolbar icon to open interface
2. Select target channel
3. Configure filters and parameters
4. Start deletion process
5. Monitor progress

### Filtering Options

- User ID
- Text pattern (exact/regex)
- Links
- Attachments
- Date range
- Message range
- Pinned messages
- NSFW content

### Configuration

- Search Delay: 100ms-60000ms (default: 1400ms)
- Delete Delay: 50ms-10000ms (default: 1400ms)
- Rate Limit Prevention
- Authorization Token
- Auto Scroll
- Privacy Mode
- Rate limits:
  - Global: 45 requests/60s
  - Per-Endpoint: 4 requests/5s

## Legal

Use this script responsibly and in compliance with Discord's Terms of Service. Maintainers are not liable for usage outcomes.

## Related Projects

- [AutoCloseReopenThread](https://github.com/Xialai-Kulimi/AutoCloseReopenThread.git) - Enhanced thread lifecycle management
