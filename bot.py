import aiosqlite as sql
from twitchio.ext import commands
from twitchio.ext import routines
from jukebox import Jukebox
from obsclient import OBSClient


class Bot(commands.Bot):

    def __init__(
        self,
        access_token: str,
        prefix: str,
        channel: str,
        obs_client: OBSClient,
        jukebox: Jukebox,
    ):
        # prefix is the default command indicator, e.g. "!"
        super().__init__(token=access_token, prefix=prefix, initial_channels=[channel])
        self.channel = channel
        self.obs_client = obs_client
        self.jukebox = jukebox
        self.today_text = "Sharie has not updated today's tasks yet!"
        self.broadcaster_only = ["addquote", "commands", "updatetoday", "pause"]

    async def __ainit__(self):
        self.database = await sql.connect("database.db")

    async def event_ready(self):
        print(f"INFO: Logged in as {self.nick}")
        # start the routine
        self.socials_routine.start()

    # generic send command for the eventbot to use
    async def send(self, message):
        channel = self.get_channel(self.channel)
        if channel is not None:
            await channel.send(message)

    # send socials message every 30 minutes
    @routines.routine(minutes=30.0, wait_first=True)
    async def socials_routine(self):
        channel = self.get_channel(self.channel)
        if channel is not None:
            await channel.send(
                f"/me Check out all of Sharie's socials here: https://linktr.ee/shariemakesart"
            )

    # social related commands
    @commands.command()
    async def discord(self, context: commands.Context):
        await context.send(
            f"/me Join the Sleepy Sanctum Discord here: https://discord.com/invite/T87Qst3W64"
        )

    @commands.command()
    async def youtube(self, context: commands.Context):
        await context.send(
            f"/me Check out the VOD channel here: https://www.youtube.com/@shariemakesart"
        )

    @commands.command()
    async def github(self, context: commands.Context):
        await context.send(
            f"/me Check out Sharie's GitHub here: https://github.com/SharieRhea"
        )

    @commands.command()
    async def socials(self, context: commands.Context):
        await context.send(
            f"/me Check out all of Sharie's socials here: https://linktr.ee/shariemakesart"
        )

    @commands.command(aliases=["FAQ"])
    async def faq(self, context: commands.Context):
        await context.send(
            f"The answer to all your questions... https://sharierhea.dev/faq"
        )

    # database related commands
    @commands.command()
    async def quote(self, context: commands.Context, index: int | None):
        # select a random quote if no number is provided
        if index is None:
            cursor = await self.database.execute(
                "SELECT text, date FROM quote ORDER BY RANDOM() LIMIT 1;"
            )
        else:
            cursor = await self.database.execute(
                "SELECT text, date FROM quote WHERE id = ?;", [index]
            )
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

    @commands.command(aliases=["colorscheme"])
    async def theme(self, context: commands.Context):
        # check the last line of the init.lua for the theme
        with open("/home/sharie/.local/share/nvim/themery/state.json", "rb") as file:
            line = file.readline()
            entries = line.decode().split('"')
            index = entries.index("colorscheme")
            await context.send(f"@{context.author.name} {entries[index + 2]}")

    @commands.command()
    async def lurk(self, context: commands.Context):
        await context.send(
            f"@{context.author.name} is lurking! Good luck on whatever you're working on!"
        )

    @commands.command()
    async def unlurk(self, context: commands.Context):
        await context.send(f"Welcome back @{context.author.name}!")

    @commands.command(name="commands")
    async def get_commands(self, context: commands.Context):
        commands_list = []
        for command in self.commands.keys():
            if command not in self.broadcaster_only:
                commands_list.append(command)
        await context.send("Current commands: " + ", ".join(commands_list))

    @commands.command()
    async def today(self, context: commands.Context):
        await context.send(f"Today's tasks/TODO: {self.today_text}")

    # broadcaster only commands
    @commands.command()
    async def next(self, context: commands.Context):
        if context.author.name != self.channel:
            await context.send("Hey, you're not supposed to do that!")
            return
        self.jukebox.next()

    @commands.command()
    async def pause(self, context: commands.Context):
        if context.author.name != self.channel:
            await context.send("Hey, you're not supposed to do that!")
            return
        await self.jukebox.pause()

    @commands.command()
    async def addquote(self, context: commands.Context, text: str):
        if context.author.name != self.channel:
            await context.send("Hey, you're not supposed to do that!")
            return

        await self.database.execute(
            "INSERT INTO quote(text, date) VALUES(?, date('now'));", [text]
        )
        await self.database.commit()

        await context.send("Quote added!")

    @commands.command()
    async def updatetoday(self, context: commands.Context, text: str):
        if context.author.name != self.channel:
            await context.send("Hey, you're not supposed to do that!")
            return

        self.today_text = text
        await context.send("Today updated!")

    # override error handling
    async def event_command_error(self, context: commands.Context, error: Exception):
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await context.send(
                f"@{context.author.name} you're missing an argument: {error.name}"
            )
        else:
            print(f"ERROR: {error}")
