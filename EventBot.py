from twitchio.ext import commands
from twitchio.ext import eventsub
from twitchio.ext.eventsub.websocket import EventSubWSClient

class EventBot(commands.Bot):
    """Represents a bot to subscribe to eventsub events."""

    def __init__(self, channel: str, broadcaster_id: str, broadcaster_token: str):
        """Initializes the bot with the specified token and joins the specified channel."""
        super().__init__(token = broadcaster_token, prefix = "!", initial_channels = [channel])
        self.channel = channel
        self.broadcaster_id = broadcaster_id
        self.broadcaster_token = broadcaster_token
        self.user = self.create_user(int(broadcaster_id), channel)

    async def __ainit__(self, eventsub_client: EventSubWSClient):
        """Updates follower and sub counts and subscribes to eventsub events."""
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
        except Exception as exception:
            print(f"Error subscribing to event: {exception}")

    # TODO: this doesn't seem to be working...
    async def event_eventsub_notification_raid(self, event: eventsub.NotificationEvent):
        if not isinstance(event.data, eventsub.ChannelRaidData):
            return
        channel = self.get_channel(self.channel)
        if channel is None:
            return

        await channel.send(f"Thank you for the raid {event.data.raider.name}! How was your stream?")
        await self.user.shoutout(token = self.broadcaster_token, to_broadcaster_id = event.data.raider.id, moderator_id = int(self.broadcaster_id))

    async def event_eventsub_notification_followV2(self, event: eventsub.NotificationEvent):
        if not isinstance(event.data, eventsub.ChannelFollowData):
            return

        # write username to file for OBS to read
        username = event.data.user.name
        if username is None:
            return
        with open("resources/recent_follower.txt", "w") as file:
            file.write(username)

        # write current follower count to file for OBS to read
        count = await self.user.fetch_channel_follower_count()
        with open("resources/follower_count.txt", "w") as file:
            file.write(str(count))

    async def event_eventsub_notification_subscription(self, event: eventsub.NotificationEvent):
        if not isinstance(event.data, eventsub.ChannelSubscribeData):
            return
        
        # write username to file for OBS to read
        username = event.data.user.name
        if username is None:
            return
        with open("resources/recent_subscriber.txt", "w") as file:
            file.write(username)

        # write current subscriber count to file for OBS to read
        count = len(await self.user.fetch_subscriptions(token = self.broadcaster_token))
        with open("resources/subscriber_count.txt", "w") as file:
            file.write(str(count - 2))
