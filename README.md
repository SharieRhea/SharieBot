# SharieBot

## Requirements
* twitchio for bot basics, events, etc: `pip install twitchio`
* dotenv for configuration: `pip install python-dotenv`
* obsws to connect to obs: `pip install obsws-python`
* aiosqlite for storing quotes in the database: `pip install aiosqlite`
* pynvim to launch nvim to pull current theme colors: `pip install pynvim`
* cairosvg to convert svg to png: `pip install cairosvg`
* rich to render terminal output to svg: `pip install rich`

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
