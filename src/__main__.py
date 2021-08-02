#!/usr/bin/env python3
import asyncio
import logging.config
from os import name
from pathlib import Path

from symphony.bdk.core.activity.command import CommandContext
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent
from symphony.bdk.gen.pod_model.v3_room_attributes import V3RoomAttributes

from .activities import EchoCommandActivity, GreetUserJoinedActivity
from .gif_activities import GifSlashCommand, GifFormReplyActivity

# Configure logging
current_dir = Path(__file__).parent.parent
logging_conf = Path.joinpath(current_dir, 'resources', 'logging.conf')
logging.config.fileConfig(logging_conf, disable_existing_loggers=False)


async def run():
    config = BdkConfigLoader.load_from_symphony_dir('config.yaml')

    async with SymphonyBdk(config) as bdk:
        datafeed_loop = bdk.datafeed()
        datafeed_loop.subscribe(MessageListener())

        # Example 1: Obtain User Information and send 1-1 IM
        user_response = await bdk.users().list_users_by_usernames(["vinay@symphony.com"])
        logging.info(user_response)
        user = user_response['users'][0]
        logging.info("********* UserId: %s", user.id)

        stream = await bdk.streams().create_im_or_mim([user.id])
        await bdk.messages().send_message(stream.id, "Hello IM")

        # Example 2: Obtain User Information and send message to Room
        room = await bdk.streams().create_room(V3RoomAttributes(name="Fancy room", description="Fancy description"))
        logging.info("********* RoomInfo: %s", room)
        roomId = room.room_system_info.id
        await bdk.streams().add_member_to_room(349026222342678, roomId)
        await bdk.messages().send_message(roomId, "Hello Room")

class MessageListener(RealTimeEventListener):
    async def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
        logging.debug("Message received from %s: %s",
            initiator.user.display_name, event.message.message)


# Start the main asyncio run
try:
    logging.info("Running bot application...")
    asyncio.run(run())
except KeyboardInterrupt:
    logging.info("Ending bot application")
