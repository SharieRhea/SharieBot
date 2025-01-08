from twitchio.ext import commands
from twitchio.ext import eventsub
from twitchio.ext.eventsub.websocket import EventSubWSClient

from bot import Bot
from jukebox import Jukebox

class EventBot(commands.Bot):

    def __init__(self, channel: str, broadcaster_id: str, broadcaster_token: str, bot: Bot, jukebox: Jukebox):
        super().__init__(token = broadcaster_token, prefix = "!", initial_channels = [channel])
        self.channel = channel
        self.broadcaster_id = broadcaster_id
        self.broadcaster_token = broadcaster_token
        self.user = self.create_user(int(broadcaster_id), channel)
        self.bot = bot
        self.jukebox = jukebox

    async def __ainit__(self, eventsub_client: EventSubWSClient):
        # write current follower count to file for OBS to read
        count = await self.user.fetch_channel_follower_count()
        with open("resources/followerCount.txt", "w") as file:
            file.write(str(count))
        
        # write current subscriber count to file for OBS to read
        count = len(await self.user.fetch_subscriptions(token = self.broadcaster_token))
        with open("resources/subscriberCount.txt", "w") as file:
            file.write(str(count - 2))

        # subscribe to event notifications
        try:
            await eventsub_client.subscribe_channel_raid(token = self.broadcaster_token, to_broadcaster = self.channel)
            await eventsub_client.subscribe_channel_follows_v2(broadcaster = self.broadcaster_id, moderator = self.broadcaster_id, token = self.broadcaster_token)
            await eventsub_client.subscribe_channel_subscriptions(broadcaster = self.broadcaster_id, token = self.broadcaster_token)
            # subscribe only to "play song" redemptions
            await eventsub_client.subscribe_channel_points_redeemed(
                broadcaster = self.broadcaster_id, 
                token = self.broadcaster_token,
                reward_id = "6d988bcc-703a-4b38-b45a-17cda9a1757e"
            )
            print(f"INFO: finished subscribing to events")
        except Exception as exception:
            print(f"ERROR: could not subscribe to event: {exception}")

    # this function name is important, it's how the library knows which function to pass the notification to
    async def event_eventsub_notification(self, event: eventsub.NotificationEvent):
        print(f"INFO: event received: {event.data}")
        if isinstance(event.data, eventsub.ChannelRaidData):
            await self.raid_received(event.data)
        elif isinstance(event.data, eventsub.ChannelFollowData):
            await self.follow_received(event.data)
        elif isinstance(event.data, eventsub.ChannelSubscribeData):
            await self.subscription_received(event.data)
        elif isinstance(event.data, eventsub.CustomRewardRedemptionAddUpdateData):
            await self.points_redeemed(event.data)

    async def raid_received(self, payload: eventsub.ChannelRaidData):
        await self.bot.send(f"Thank you for the raid @{payload.raider.name}! How was your stream and what were you working on?")
        await self.user.shoutout(token = self.broadcaster_token, to_broadcaster_id = payload.raider.id, moderator_id = int(self.broadcaster_id))

    async def follow_received(self, payload: eventsub.ChannelFollowData):
        # write username to file for OBS to read
        username = payload.user.name
        if username is None:
            return
        with open("resources/recent_follower.txt", "w") as file:
            file.write(username)

        # write current follower count to file for OBS to read
        count = await self.user.fetch_channel_follower_count()
        with open("resources/follower_count.txt", "w") as file:
            file.write(str(count))

    async def subscription_received(self, payload: eventsub.ChannelSubscribeData):
        # write username to file for OBS to read
        username = payload.user.name
        if username is None:
            return
        with open("resources/recent_subscriber.txt", "w") as file:
            file.write(username)

        # write current subscriber count to file for OBS to read
        count = len(await self.user.fetch_subscriptions(token = self.broadcaster_token))
        with open("resources/subscriber_count.txt", "w") as file:
            file.write(str(count - 2))

    async def points_redeemed(self, payload: eventsub.CustomRewardRedemptionAddUpdateData):
        if self.jukebox.add_song(payload.input.strip()):
                await self.bot.send(f"@{payload.user.name} {payload.input} was added to the queue!")
        else:
                await self.bot.send(f"@{payload.user.name} {payload.input} does not exist or had invalid formatting")
