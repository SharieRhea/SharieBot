import os
from dotenv import load_dotenv
from twitchio.ext import eventsub
from threading import Thread
from bot import Bot
from eventbot import EventBot
from image_utils import ColorTracker
from obsclient import OBSClient
from jukebox import Jukebox


def main():
    # set up environment variables
    load_dotenv()
    CHANNEL = os.environ["CHANNEL"]
    BROADCASTER_ID = os.environ["BROADCASTER_ID"]
    BROADCASTER_TOKEN = os.environ["BROADCASTER_TOKEN"]
    MODERATOR_ID = os.environ["MODERATOR_ID"]
    MODERATOR_TOKEN = os.environ["MODERATOR_TOKEN"]
    MUSIC_DIRECTORY = os.environ["MUSIC_DIRECTORY"]

    # initialize colors
    ColorTracker()

    # initialize websocket client for OBS
    obs_client = OBSClient()
    # initialize the jukebox for music
    jukebox = Jukebox(MUSIC_DIRECTORY, "chill/")

    # register a bot under the moderator account
    bot = Bot(MODERATOR_TOKEN, "!", CHANNEL, obs_client, jukebox)
    bot.loop.run_until_complete(bot.__ainit__())
    # register a bot under the broadcaster account for handling events
    event_sub_bot = EventBot(
        CHANNEL, BROADCASTER_ID, BROADCASTER_TOKEN, bot, jukebox, obs_client
    )
    event_sub_client = eventsub.EventSubWSClient(event_sub_bot)
    bot.loop.run_until_complete(event_sub_bot.__ainit__(event_sub_client))

    # start up a thread for playing music
    music = Thread(target=jukebox.start)
    music.start()

    # start up a thread for watching colorscheme changes
    colorscheme = Thread(target=event_sub_bot.watch_colorscheme_change)
    colorscheme.start()

    # begin main event loop
    bot.run()


if __name__ == "__main__":
    main()
