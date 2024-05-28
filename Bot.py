import asyncio
import aiosqlite as sql
from twitchio.ext import commands
from OBSClient import OBSClient

class Bot(commands.Bot):
    """Represents a bot to respond to commands in Twitch chat."""

    def __init__(self, access_token: str, prefix: str, channel: str, obs_client: OBSClient):
        """Initializes the bot with the specified token and joins the specified channel."""
        # prefix is the default command indicator, e.g. "!"
        super().__init__(token = access_token, prefix = prefix, initial_channels = [channel])
        self.channel = channel
        self.obs_client = obs_client
        self.broadcaster_only = ["adbreak", "addquote", "commands"]

    async def __ainit__(self):
        """Initializes a database connection."""
        self.database = await sql.connect("resources/database.db")

    async def event_ready(self):
        print(f"Logged in as as {self.nick}")

    # social related commands
    @commands.command()
    async def discord(self, context: commands.Context):
        await context.send(f"/me Join the Sleepy Sanctum Discord here: https://discord.com/invite/T87Qst3W64")

    @commands.command()
    async def youtube(self, context: commands.Context):
        await context.send(f"/me Check out the VOD channel here: https://www.youtube.com/@shariemakesart")

    @commands.command()
    async def github(self, context: commands.Context):
        await context.send(f"/me Check out Sharie's GitHub here: https://github.com/SharieRhea")

    @commands.command()
    async def socials(self, context: commands.Context):
        await context.send(f"/me Check out all of Sharie's socials here: https://linktr.ee/shariemakesart")

    @commands.command(aliases = ["FAQ"])
    async def faq(self, context: commands.Context):
        await context.send(f"The answer to all your questions... https://tinyurl.com/faqshariemakesart")

    # database related commands
    @commands.command()
    async def quote(self, context: commands.Context, index: int | None):
        # select a random quote if no number is provided
        if index is None:
            cursor = await self.database.execute("SELECT text, date FROM quote ORDER BY RANDOM() LIMIT 1;")
        else:    
            cursor = await self.database.execute("SELECT text, date FROM quote WHERE id = ?;", [index])
        data = await cursor.fetchone()

        # handle out of range indices
        if data is None:
            await context.send("Quote not found!")
            return

        await context.send(f'"{data[0]}" - {data[1]}')

    # info related commands
    @commands.command()
    async def font(self, context: commands.Context):
        await context.send(f"@{context.author.name} JetBrains Mono")

    @commands.command(aliases = ["colorscheme"])
    async def theme(self, context: commands.Context):
        # check the last line of the init.lua for the theme
        with open("/home/sharie/.config/nvim/init.lua", "rb") as file:
            # seek to the very end of the file
            file.seek(0, 2)
            # move backwards until a newline is found
            while file.read(1) != b'\n':
                file.seek(-2, 1)
            line = file.readline()
            theme = line.decode().split("\"")[1]
            await context.send(f"@{context.author.name} {theme}")

    @commands.command()
    async def lurk(self, context: commands.Context):
        await context.send(f"@{context.author.name} is lurking! Good luck on whatever you're working on!")

    @commands.command()
    async def unlurk(self, context: commands.Context):
        await context.send(f"Welcome back @{context.author.name}!")

    @commands.command(name = "commands")
    async def get_commands(self, context: commands.Context):
        commands_list = []
        for command in self.commands.keys():
            if command not in self.broadcaster_only:
                commands_list.append(command)
        await context.send("Current commands: " + ", ".join(commands_list))

    # broadcaster only commands
    @commands.command()
    async def adbreak(self, context: commands.Context):
        if context.author.name != self.channel:
            return

        self.obs_client.switch_to_ads_scene()
        # ad breaks are set to 90 seconds
        await asyncio.sleep(90)
        self.obs_client.switch_to_content_scene()

    @commands.command()
    async def addquote(self, context: commands.Context, text: str):
        if context.author.name != self.channel:
            return

        await self.database.execute("INSERT INTO quote(text, date) VALUES(?, date('now'));", [text])
        await self.database.commit()

        await context.send("Quote added!")

    # override error handling
    async def event_command_error(self, context: commands.Context, error: Exception):
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await context.send(f"@{context.author.name} you're missing an argument: {error.name}")
        else:
            print(error)
