from twitchio.ext import commands
from twitchio.ext import eventsub
from twitchio.ext.eventsub.websocket import EventSubWSClient

class EventBot(commands.Bot):
    def __init__(self, channel: str, broadcasterID: str, broadcasterToken: str, moderatorID: str, moderatorToken: str):
        super().__init__(token = broadcasterToken, prefix = "!", initial_channels = [channel])
        self.channel = channel
        self.broadcasterID = broadcasterID
        self.broadcasterToken = broadcasterToken
        self.moderatorID = moderatorID
        self.moderatorToken = moderatorToken

    async def __ainit__(self, eventSubClient: EventSubWSClient):
        try:
            await eventSubClient.subscribe_channel_raid(token = self.broadcasterToken, to_broadcaster = self.channel)
            await eventSubClient.subscribe_channel_follows_v2(broadcaster = self.broadcasterID, moderator = self.broadcasterID, token = self.broadcasterToken)
            await eventSubClient.subscribe_channel_subscriptions(broadcaster = self.broadcasterID, token = self.broadcasterToken)
        except Exception as exception:
            print(f"Error subscribing to event: {exception}")

    async def event_eventsub_notification_raid(self, event: eventsub.NotificationEvent):
        if not isinstance(event.data, eventsub.ChannelRaidData):
            return
        channel = self.get_channel(self.channel)
        if channel is None:
            return

        await channel.send(f"Thank you for the raid {event.data.raider}! How was your stream?")
        await channel.send(f"/shoutout {event.data.raider}")

    async def event_eventsub_notification_followV2(self, event: eventsub.NotificationEvent):
        if not isinstance(event.data, eventsub.ChannelFollowData):
            return
        username = event.data.user.name
        if username is None:
            return
        with open("resources/recentFollwer.txt", "w") as file:
            file.write(username)

    async def event_eventsub_notification_subscription(self, event: eventsub.NotificationEvent):
        if not isinstance(event.data, eventsub.ChannelSubscribeData):
            return
        username = event.data.user.name
        if username is None:
            return
        with open("resouces/recentSubscriber.txt", "w") as file:
            file.write(username)


