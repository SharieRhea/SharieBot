import os
from dotenv import load_dotenv
from twitchio.ext.eventsub.websocket import EventSubWSClient
from Bot import Bot
from twitchio.ext import eventsub

def main():
    load_dotenv()
    bot = Bot(os.environ["ACCESS_TOKEN"], "!", "shariemakesart")
    bot.run()


if __name__ == "__main__":
    main()
