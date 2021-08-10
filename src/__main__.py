#!/usr/bin/env python3
import asyncio
import logging.config
import re
from pathlib import Path

from symphony.bdk.core.activity.command import CommandContext
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent
from symphony.bdk.gen.pod_model.v3_room_attributes import V3RoomAttributes
from symphony.bdk.core.service.message.message_service import MessageService

from .activities import EchoCommandActivity, GreetUserJoinedActivity
from .gif_activities import GifSlashCommand, GifFormReplyActivity

# Configure logging
current_dir = Path(__file__).parent.parent
logging_conf = Path.joinpath(current_dir, 'resources', 'logging.conf')
logging.config.fileConfig(logging_conf, disable_existing_loggers=False)


async def run():
    config = BdkConfigLoader.load_from_file(Path.joinpath(current_dir, 'resources', 'config.yaml'))
    # config = BdkConfigLoader.load_from_symphony_dir('config.yaml')

    async with SymphonyBdk(config) as bdk:
        datafeed_loop = bdk.datafeed()
        datafeed_loop.subscribe(MessageListener(bdk.messages()))
        datafeed_loop.subscribe(FormListener(bdk.messages()))

        # Start the datafeed read loop
        await datafeed_loop.start()


# Example 1: Create RealTime Message Listener & Form Reply Listener
class MessageListener(RealTimeEventListener):
    def __init__(self, messages: MessageService):
        self._messages = messages
        super().__init__()

    async def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
        message = event.message.message
        message_text = re.sub('<[^<]+>', '', message)
        if message_text.startswith("/order"):
            form = "<form id=\"order\">"
            form += "<text-field name=\"ticker\" placeholder=\"Ticker\" /><br />"
            form += "<text-field name=\"quantity\" placeholder=\"Quantity\" /><br />"
            form += "<text-field name=\"price\" placeholder=\"Price\" /><br />"
            form += "<button type=\"action\" name=\"order\"> Place Order</button>"
            form += "</form>"
        await self._messages.send_message(event.message.stream.stream_id, form)

class FormListener(RealTimeEventListener):
    def __init__(self, messages: MessageService):
        self._messages = messages
        super().__init__()

    async def on_symphony_elements_action(self, initiator: V4Initiator, event: V4MessageSent):
        values = event.form_values

        reply_template = "Order placed for {quantity} of <cash tag =\"{ticker}\" /> @ {price}"
        await self._messages.send_message(event.stream.stream_id, reply_template.format(**values))

# Start the main asyncio run
try:
    logging.info("Running bot application...")
    asyncio.run(run())
except KeyboardInterrupt:
    logging.info("Ending bot application")
