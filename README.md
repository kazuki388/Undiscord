# Undiscord

A high-performance Discord message deletion utility implemented as a userscript.

This is a maintained fork of [victornpb/undiscord](https://github.com/victornpb/undiscord). While functional, this fork primarily serves personal needs and may lack broader community support or regular feature updates.

> **Technical Prerequisites**:
>
> - Tampermonkey on Chromium-based browsers
> - Deploy v5.2.3 initially, then upgrade to v5.2.4 via script editor
> - Disable password manager for Discord authentication when script is active
> - While the script handles thread state transitions, consider [AutoCloseReopenThread](https://github.com/Xialai-Kulimi/AutoCloseReopenThread.git) for enhanced thread lifecycle (archived/active) management

## Features

- Concurrent message deletion across channels, DMs, and thread contexts
- Advanced message filtering system with regex support and metadata matching
- Discord data archive integration for offline message processing
- Automated thread state management with configurable lifecycle hooks
- Adaptive rate limiting with dynamic throttling
- Real-time progress monitoring with ETA calculation
- Privacy-focused streamer mode
- Interactive message selection interface
- Multi-channel batch processing support
- Comprehensive logging and error handling
- Automatic authentication token management
- Modular UI with drag-and-drop capability

## Usage

### Deployment

1. Deploy a userscript manager (Tampermonkey recommended)
2. Install via [Greasy Fork](https://greasyfork.org/en/scripts/406540-undiscord-delete-all-messages-in-a-discord-channel-or-dm-bulk-deletion)
3. Invalidate Discord cache (hard refresh)

### Operation

1. Access deletion interface via toolbar icon
2. Configure target channel parameters
3. Define filtering criteria and execution parameters
4. Initialize deletion process
5. Monitor execution via logging interface

### Channel

- Auto-population of current server/channel identifiers
- Automatic `@me` server ID assignment
- Automatic parent channel resolution
- Comma-delimited channel ID support

### Filter

- `User ID`: Filter messages by specific user ID
- `Pattern Matching`: Filter by exact text match or regex pattern
- `Has Link`: Filter messages containing URLs
- `Has File`: Filter messages with attachments
- `Has No File`: Filter messages without attachments
- `Pattern`: Filter using JavaScript RegExp pattern
- `Date Range`: Filter by timestamp (ISO 8601)
- `Message Range`: Filter by message snowflakes (use `Pick` to select messages visually)
- `Include Pinned`: Include pinned messages (default: false)
- `Include NSFW`: Search NSFW channels (default: false)

## Configuration

Key runtime parameters configurable via UI:

- `Search Delay`: Interval between API requests (`100ms-60000ms`, default: `1400ms`)
- `Delete Delay`: Message deletion interval (`50ms-10000ms`, default: `1400ms`)
- `Rate Limit Prevention`: Dynamic request throttling based on Discord's limits
- `Authorization Token`: Optional manual Discord authentication token override
- `Auto Scroll`: Controls automatic viewport scrolling during operations
- `Privacy Mode`: Masks sensitive data in logs and UI

The script implements two-tier rate limiting:

- Global: 45 requests/60s across all endpoints
- Per-Endpoint: 4 requests/5s per unique endpoint

The `Search Delay` and `Delete Delay` parameters automatically adjust based on Discord's rate limit responses. Higher values reduce throughput but improve reliability. The script implements exponential backoff when limits are encountered.

## Disclaimer

This script is provided for legitimate use cases. Users must ensure compliance with Discord's Terms of Service. The maintainers assume no liability for implementation outcomes.
