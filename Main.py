import os
from dotenv import load_dotenv
from twitchio.ext import eventsub
from Bot import Bot
from EventBot import EventBot
from OBSClient import OBSClient

def main():
    # set up environment variables
    load_dotenv()
    CHANNEL = os.environ["CHANNEL"]
    BROADCASTER_ID = os.environ["BROADCASTER_ID"]
    BROADCASTER_TOKEN = os.environ["BROADCASTER_TOKEN"]
    MODERATOR_ID = os.environ["MODERATOR_ID"]
    MODERATOR_TOKEN = os.environ["MODERATOR_TOKEN"]

    # initialize websocket client for OBS
    obs_client = OBSClient()

    # register a bot under the moderator account
    bot = Bot(MODERATOR_TOKEN, "!", CHANNEL, obs_client)
    bot.loop.run_until_complete(bot.__ainit__())
    # register a bot under the broadcaster account for handling events
    event_sub_bot = EventBot(CHANNEL, BROADCASTER_ID, BROADCASTER_TOKEN)
    event_sub_client = eventsub.EventSubWSClient(event_sub_bot)
    bot.loop.run_until_complete(event_sub_bot.__ainit__(event_sub_client))

    # begin main event loop
    bot.run()

if __name__ == "__main__":
    main()
