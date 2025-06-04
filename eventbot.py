from os.path import getmtime
from time import sleep
from twitchio.ext import commands
from twitchio.ext import eventsub
from twitchio.ext.eventsub.websocket import EventSubWSClient

from bot import Bot
from image_utils import ColorTracker
from jukebox import Jukebox
from obsclient import OBSClient


class EventBot(commands.Bot):

    def __init__(
        self,
        channel: str,
        broadcaster_id: str,
        broadcaster_token: str,
        bot: Bot,
        jukebox: Jukebox,
        obs_client: OBSClient,
    ):
        super().__init__(
            token=broadcaster_token, prefix="!", initial_channels=[channel]
        )
        self.channel = channel
        self.broadcaster_id = broadcaster_id
        self.broadcaster_token = broadcaster_token
        self.user = self.create_user(int(broadcaster_id), channel)
        self.bot = bot
        self.jukebox = jukebox
        self.obs_client = obs_client

        self.follower = ""
        self.subscriber = ""
        self.follwers = 0
        self.subscribers = 0

        self.colortracker = ColorTracker()

    async def __ainit__(self, eventsub_client: EventSubWSClient):
        # update follower count and image
        self.followers = await self.user.fetch_channel_follower_count()
        with open("resources/follower_count.txt", "w") as file:
            file.write(str(self.followers))
        with open("resources/recent_follower.txt", "r") as file:
            self.follower = file.readline()
            self.colortracker.update_image(
                str(self.followers), self.follower, title="followers"
            )
        # update subscriber count and image
        self.subscribers = (
            len(await self.user.fetch_subscriptions(token=self.broadcaster_token)) - 2
        )
        with open("resources/subscriber_count.txt", "w") as file:
            file.write(str(self.subscribers))
        with open("resources/recent_subscriber.txt", "r") as file:
            self.subscriber = file.readline()
            self.colortracker.update_image(
                str(self.subscribers), self.subscriber, "subscribers"
            )

        # subscribe to event notifications
        try:
            await eventsub_client.subscribe_channel_raid(
                token=self.broadcaster_token, to_broadcaster=self.broadcaster_id
            )
            await eventsub_client.subscribe_channel_follows_v2(
                broadcaster=self.broadcaster_id,
                moderator=self.broadcaster_id,
                token=self.broadcaster_token,
            )
            await eventsub_client.subscribe_channel_subscriptions(
                broadcaster=self.broadcaster_id, token=self.broadcaster_token
            )
            # subscribe only to "play song" redemptions
            await eventsub_client.subscribe_channel_points_redeemed(
                broadcaster=self.broadcaster_id, token=self.broadcaster_token
            )
            print(f"INFO: finished subscribing to events")
        except Exception as exception:
            print(f"ERROR: could not subscribe to event: {exception}")

    def watch_colorscheme_change(self):
        # infinitely watch the colorscheme.txt file for changes
        modifiedtime = getmtime("/home/sharie/.config/nvim/colorscheme.txt")
        while True:
            newtime = getmtime("/home/sharie/.config/nvim/colorscheme.txt")
            if newtime != modifiedtime:
                modifiedtime = newtime
                self.colortracker.update_colors()
                sleep(0.1)
                self.colortracker.update_image(
                    str(self.followers), self.follower, title="followers"
                )
                self.colortracker.update_image(
                    str(self.subscribers), self.subscriber, "subscribers"
                )
                self.jukebox.update_image()
            sleep(1)

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
        await self.bot.send(
            f"Thank you for the raid @{payload.raider.name}! How was your stream and what were you working on?"
        )
        await self.user.shoutout(
            token=self.broadcaster_token,
            to_broadcaster_id=payload.raider.id,
            moderator_id=int(self.broadcaster_id),
        )
        self.colortracker.update_notification_image(
            f"{payload.raider.name} just raided with {payload.viewer_count} viewers!",
            "raid",
        )
        await self.obs_client.display_notification()

    async def follow_received(self, payload: eventsub.ChannelFollowData):
        # write username to file for OBS to read
        if not payload.user.name:
            return
        self.follower = payload.user.name

        with open("resources/recent_follower.txt", "w") as file:
            file.write(self.follower)
        self.followers = await self.user.fetch_channel_follower_count()
        with open("resources/follower_count.txt", "w") as file:
            file.write(str(self.followers))

        self.colortracker.update_image(str(self.followers), self.follower, "followers")
        self.colortracker.update_notification_image(
            f"{self.follower} just followed!", "follow"
        )
        await self.obs_client.display_notification()

    async def subscription_received(self, payload: eventsub.ChannelSubscribeData):
        # write username to file for OBS to read
        if not payload.user.name:
            return
        self.subscriber = payload.user.name

        with open("resources/recent_subscriber.txt", "w") as file:
            file.write(self.subscriber)

        # write current subscriber count to file for OBS to read
        self.subscribers = (
            len(await self.user.fetch_subscriptions(token=self.broadcaster_token)) - 2
        )
        with open("resources/subscriber_count.txt", "w") as file:
            file.write(str(self.subscribers))

        self.colortracker.update_image(
            str(self.subscribers), self.subscriber, "subscribers"
        )
        tier = payload.tier
        self.colortracker.update_notification_image(
            f"{self.subscriber} just subscribed at tier {tier}!", "subscription"
        )
        await self.obs_client.display_notification()

    # TODO: subscribe to ChannelSubscriptionMessage, this is the one with cumulative months etc

    async def points_redeemed(
        self, payload: eventsub.CustomRewardRedemptionAddUpdateData
    ):
        self.colortracker.update_notification_image(
            f"{payload.user.name} redeemed {payload.reward.title}!", "point redemption"
        )
        await self.obs_client.display_notification()
        if payload.id == "6d988bcc-703a-4b38-b45a-17cda9a1757e":
            if self.jukebox.add_song(payload.input.strip()):
                await self.bot.send(
                    f"@{payload.user.name} {payload.input} was added to the queue!"
                )
            else:
                await self.bot.send(
                    f"@{payload.user.name} {payload.input} does not exist or had invalid formatting"
                )
