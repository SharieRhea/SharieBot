"""An example of connecting to a conduit and subscribing to EventSub when a User Authorizes the application.

This bot can be restarted as many times without needing to subscribe or worry about tokens:
- Tokens are stored in '.tio.tokens.json' by default
- Subscriptions last 72 hours after the bot is disconnected and refresh when the bot starts.

Consider reading through the documentation for AutoBot for more in depth explanations.
"""

import os
import asyncio
import logging
from typing import TYPE_CHECKING

import aiosqlite
import asqlite
from dotenv import load_dotenv

import twitchio
from twitchio import eventsub
from twitchio.ext import commands


if TYPE_CHECKING:
    import sqlite3


LOGGER: logging.Logger = logging.getLogger("Bot")

# set up environment variables
load_dotenv()
CHANNEL: str = os.environ["CHANNEL"]
CLIENT_ID: str = os.environ["CLIENT_ID"]
CLIENT_SECRET: str = os.environ["CLIENT_SECRET"]
BOT_ID: str = os.environ["BOT_ID"]
OWNER_ID: str = os.environ["OWNER_ID"]


class Bot(commands.AutoBot):
    def __init__(self, *, quote_database: aiosqlite.Connection, token_database: asqlite.Pool, subs: list[eventsub.SubscriptionPayload]) -> None:
        self.token_database = token_database
        self.quote_database = quote_database

        super().__init__(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            bot_id=BOT_ID,
            owner_id=OWNER_ID,
            prefix="!",
            subscriptions=subs,
            force_subscribe=True,
        )

    async def setup_hook(self) -> None:
        # Add our component which contains our commands...
        await self.add_component(MyComponent(self))

    async def event_oauth_authorized(self, payload: twitchio.authentication.UserTokenPayload) -> None:
        await self.add_token(payload.access_token, payload.refresh_token)

        if not payload.user_id:
            return

        if payload.user_id == self.bot_id:
            # We usually don't want subscribe to events on the bots channel...
            return

        # A list of subscriptions we would like to make to the newly authorized channel...
        subs: list[eventsub.SubscriptionPayload] = [
            eventsub.ChatMessageSubscription(broadcaster_user_id=payload.user_id, user_id=self.bot_id),
        ]

        resp: twitchio.MultiSubscribePayload = await self.multi_subscribe(subs)
        if resp.errors:
            LOGGER.warning("Failed to subscribe to: %r, for user: %s", resp.errors, payload.user_id)

    async def add_token(self, token: str, refresh: str) -> twitchio.authentication.ValidateTokenPayload:
        # Make sure to call super() as it will add the tokens interally and return us some data...
        resp: twitchio.authentication.ValidateTokenPayload = await super().add_token(token, refresh)

        # Store our tokens in a simple SQLite Database when they are authorized...
        query = """
        INSERT INTO tokens (user_id, token, refresh)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET
            token = excluded.token,
            refresh = excluded.refresh;
        """

        async with self.token_database.acquire() as connection:
            await connection.execute(query, (resp.user_id, token, refresh))

        LOGGER.info("Added token to the database for user: %s", resp.user_id)
        return resp

    async def event_ready(self) -> None:
        LOGGER.info("Successfully logged in as: %s", self.bot_id)


class MyComponent(commands.Component):
    # An example of a Component with some simple commands and listeners
    # You can use Components within modules for a more organized codebase and hot-reloading.

    def __init__(self, bot: Bot) -> None:
        # Passing args is not required...
        # We pass bot here as an example...
        self.bot = bot
        self.quote_database = bot.quote_database

    # An example of listening to an event
    # We use a listener in our Component to display the messages received.
    @commands.Component.listener()
    async def event_message(self, payload: twitchio.ChatMessage) -> None:
        print(f"[{payload.broadcaster.name}] - {payload.chatter.name}: {payload.text}")

        # generic fallback for an unknown command
        if payload.text.startswith(str(self.bot._get_prefix)):
            command_name = payload.text.split(" ")[0][len(str(self.bot._get_prefix)):]
            if command_name not in self.__all_commands__:
                await self.bot.get_context(payload).reply("We don't have that command yet!")

    @commands.command()
    async def discord(self, ctx: commands.Context) -> None:
        """Replies with a link to the discord server."""
        await ctx.reply("/me Join the Sleepy Sanctum Discord here: https://discord.com/invite/T87Qst3W64")

    @commands.command()
    async def youtube(self, ctx: commands.Context) -> None:
        """Replies with a link to the youtube channel."""
        await ctx.reply("/me Check out the VOD channel here: https://www.youtube.com/@twilight-world13")

    @commands.command()
    async def github(self, ctx: commands.Context) -> None:
        """Replies with a link to github."""
        await ctx.reply("/me Check out Sharie's GitHub here: https://github.com/SharieRhea")

    @commands.command()
    async def socials(self, ctx: commands.Context) -> None:
        """Replies with a link to the linktree."""
        await ctx.reply("/me Check out all of Sharie's socials here: https://linktr.ee/twilight_world")

    @commands.command(aliases=["FAQ"])
    async def faq(self, ctx: commands.Context) -> None:
        """Replies with a link to the faq."""
        await ctx.reply("The answer to all your questions... https://sharierhea.dev/faq")

    @commands.command()
    async def lurk(self, ctx: commands.Context) -> None:
        """Replies to acknowledge the lurk."""
        await ctx.reply("Thank you! We love lurkers!")

    @commands.command()
    async def quote(self, ctx: commands.Context, index: int | None = None) -> None:
        """Replies with a quote specified by number, or a random one if no number is given."""
        # select a random quote if no number is provided
        if index is None:
            cursor = await self.quote_database.execute("SELECT text, date FROM quote ORDER BY RANDOM() LIMIT 1;")
        else:
            cursor = await self.quote_database.execute(
                "SELECT text, date FROM quote WHERE id = ?;", [index]
            )
        data = await cursor.fetchone()

        # handle out of range indices
        if data is None:
            await ctx.reply("Quote not found!")
            return

        await ctx.reply(f'"{data[0]}" - {data[1]}')

    @commands.command()
    async def addquote(self, ctx: commands.Context, text: str) -> None:
        """Adds a new quote to the database (broadcaster only)."""
        if ctx.author.name != CHANNEL:
            await ctx.reply("Hey, you're not supposed to do that!")
            return

        await self.quote_database.execute(
            "INSERT INTO quote(text, date) VALUES(?, date('now'));", [text]
        )
        await self.quote_database.commit()

        await ctx.reply("Quote added!")


async def setup_database(db: asqlite.Pool) -> tuple[list[tuple[str, str]], list[eventsub.SubscriptionPayload]]:
    # Create our token table, if it doesn't exist..
    # You should add the created files to .gitignore or potentially store them somewhere safer
    # This is just for example purposes...

    query = """CREATE TABLE IF NOT EXISTS tokens(user_id TEXT PRIMARY KEY, token TEXT NOT NULL, refresh TEXT NOT NULL)"""
    async with db.acquire() as connection:
        await connection.execute(query)

        # Fetch any existing tokens...
        rows: list[sqlite3.Row] = await connection.fetchall("""SELECT * from tokens""")

        tokens: list[tuple[str, str]] = []
        subs: list[eventsub.SubscriptionPayload] = []

        for row in rows:
            tokens.append((row["token"], row["refresh"]))

            if row["user_id"] == BOT_ID:
                continue

            subs.extend([eventsub.ChatMessageSubscription(broadcaster_user_id=row["user_id"], user_id=BOT_ID)])

    return tokens, subs


# Our main entry point for our Bot
# Best to setup_logging here, before anything starts
def main() -> None:
    twitchio.utils.setup_logging(level=logging.INFO)

    async def runner() -> None:
        quote_database = await aiosqlite.connect("quotes.db")
        async with asqlite.create_pool("tokens.db") as tdb:
            tokens, subs = await setup_database(tdb)

            async with Bot(quote_database=quote_database, token_database=tdb, subs=subs) as bot:
                for pair in tokens:
                    await bot.add_token(*pair)

                await bot.start(load_tokens=False)

    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        LOGGER.warning("Shutting down due to KeyboardInterrupt")


if __name__ == "__main__":
    main()
