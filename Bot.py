import asyncio
from twitchio.ext import commands
from OBSClient import OBSClient

class Bot(commands.Bot):

    def __init__(self, accessToken: str, prefix: str, channel: str, obsClient: OBSClient):
        # prefix is the default command indicator, e.g. "!"
        super().__init__(token = accessToken, prefix = prefix, initial_channels = [channel])
        self.CHANNEL = channel
        self.obsClient = obsClient

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

    # info related commands
    @commands.command()
    async def font(self, context: commands.Context):
        await context.send(f"@{context.author.name} JetBrains Mono")

    @commands.command()
    async def lurk(self, context: commands.Context):
        await context.send(f"@{context.author.name} is lurking! Good luck on whatever you're working on!")

    @commands.command()
    async def unlurk(self, context: commands.Context):
        await context.send(f"Welcome back @{context.author.name}!")

    @commands.command(name = "commands")
    async def get_commands(self, context: commands.Context):
        commandsList = []
        for command in self.commands.keys():
            if command != "adbreak" and command != "commands":
                commandsList.append(command)
        await context.send("Current commands: " + ", ".join(commandsList))

    # broadcaster only commands
    @commands.command()
    async def adbreak(self, context: commands.Context):
        if context.author.name != self.CHANNEL:
            return
        self.obsClient.switchToAdsScene()
        # ad breaks are set to 90 seconds
        await asyncio.sleep(90)
        self.obsClient.switchToContentScene()

