import os
from dotenv import load_dotenv
from Bot import Bot
from EventBot import EventBot
from twitchio.ext import eventsub

def main():
    load_dotenv()
    CHANNEL = os.environ["CHANNEL"]
    BROADCASTER_ID = os.environ["BROADCASTER_ID"]
    BROADCASTER_TOKEN = os.environ["BROADCASTER_TOKEN"]
    MODERATOR_ID = os.environ["MODERATOR_ID"]
    MODERATOR_TOKEN = os.environ["MODERATOR_TOKEN"]

    bot = Bot(os.environ["MODERATOR_TOKEN"], "!", "shariemakesart")
    eventSubBot = EventBot(CHANNEL, BROADCASTER_ID, BROADCASTER_TOKEN, MODERATOR_ID, MODERATOR_TOKEN) 
    eventSubClient = eventsub.EventSubWSClient(eventSubBot)
    bot.loop.run_until_complete(eventSubBot.__ainit__(eventSubClient))
    bot.run()

if __name__ == "__main__":
    main()
