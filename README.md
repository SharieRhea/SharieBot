# SharieBot

## Requirements
* twitchio: `pip install twitchio`
* dotenv: `pip install python-dotenv`
* obsws: `pip install obsws-python`
* aiosqlite: `pip install aiosqlite`

* You must have [OBS](https://obsproject.com/) installed and *open* before running the program.
* You must have [VLC](https://www.videolan.org/vlc/) installed.

### Environment Variables
1. Create a .env in your project directory.
2. Populate with your desired environment variables.
3. Sample format:
    ```
    BROADCASTER_ID="117399875"
    BROADCASTER_TOKEN="73d0f8mkabpbmjp921asv2jaidwxn"
    ```

## Features
* Informational text commands
* Eventsub event handling (raids, follows, subscriptions, point redemptions)
* OBS integration for automatic scene switching
* Sqlite database for storing and retrieving quotes
* Support for playing .mp3 music files using VLC
