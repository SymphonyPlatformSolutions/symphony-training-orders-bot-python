#!/usr/bin/env python3
import asyncio
import logging.config
from pathlib import Path

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.core.activity.command import CommandContext
from symphony.bdk.core.service.message.message_service import MessageService
from symphony.bdk.core.activity.form import FormReplyActivity, FormReplyContext

# Configure logging
from .order_listener import MessageListener, FormListener

current_dir = Path(__file__).parent.parent
logging_conf = Path.joinpath(current_dir, 'resources', 'logging.conf')
logging.config.fileConfig(logging_conf, disable_existing_loggers=False)


async def run():
    config = BdkConfigLoader.load_from_file(
        Path.joinpath(current_dir, 'resources', 'config.yaml'))
    # config = BdkConfigLoader.load_from_symphony_dir('config.yaml')

    async with SymphonyBdk(config) as bdk:
        datafeed_loop = bdk.datafeed()
        datafeed_loop.subscribe(MessageListener(bdk.messages()))
        datafeed_loop.subscribe(FormListener(bdk.messages()))

        activities = bdk.activities()
        activities.register(PriceFormReply(bdk.messages()))

        @activities.slash("/price")
        async def price(context: CommandContext):
            stream_id = context.stream_id
            form = "<form id=\"price\">"
            form += "<text-field name=\"ticker\" placeholder=\"Ticker\" /><br />"
            form += "<button type=\"action\" name=\"price\">Get Price</button>"
            form += "</form>"

            await bdk.messages().send_message(stream_id, form)

        # Start the datafeed read loop
        await datafeed_loop.start()


class PriceFormReply(FormReplyActivity):
    def __init__(self, messages: MessageService):
        self._messages = messages
        super().__init__()

    def matches(self, context: FormReplyContext) -> bool:
        return context.form_id == 'price'

    async def on_activity(self, context: FormReplyContext):
        ticker = context.get_form_value("ticker")
        price = random.randint(30, 500)
        reply = f'Price of {ticker} is {price}'

        await self._messages.send_message(context.source_event.stream.stream_id, reply)


# Start the main asyncio run
try:
    logging.info("Running bot application...")
    asyncio.run(run())
except KeyboardInterrupt:
    logging.info("Ending bot application")
