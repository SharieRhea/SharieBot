import os
from dotenv import load_dotenv
from twitchio.ext import eventsub
from Bot import Bot
from EventBot import EventBot

from OBSClient import OBSClient

def main():
    load_dotenv()
    CHANNEL = os.environ["CHANNEL"]
    BROADCASTER_ID = os.environ["BROADCASTER_ID"]
    BROADCASTER_TOKEN = os.environ["BROADCASTER_TOKEN"]
    MODERATOR_ID = os.environ["MODERATOR_ID"]
    MODERATOR_TOKEN = os.environ["MODERATOR_TOKEN"]

    # initialize websocket client for OBS
    obsClient = OBSClient()

    # register a bot under the moderator account
    bot = Bot(MODERATOR_TOKEN, "!", CHANNEL, obsClient)
    #user = bot.create_user(int(BROADCASTER_ID), CHANNEL)
    # register a bot under the broadcaster account for handling events
    eventSubBot = EventBot(CHANNEL, BROADCASTER_ID, BROADCASTER_TOKEN, MODERATOR_ID, MODERATOR_TOKEN) 
    eventSubClient = eventsub.EventSubWSClient(eventSubBot)
    bot.loop.run_until_complete(eventSubBot.__ainit__(eventSubClient))

    bot.run()

if __name__ == "__main__":
    main()
