#!/usr/bin/env python3
import asyncio
import logging.config
from pathlib import Path

from jinja2 import Template
from symphony.bdk.core.activity.command import CommandContext
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk

# Configure logging
from .order_listener import MessageListener, FormListener
from .price_activity import PriceFormReply

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

        activities = bdk.activities()
        activities.register(PriceFormReply(bdk.messages()))

        @activities.slash("/price")
        async def price(context: CommandContext):
            stream_id = context.stream_id
            template = Template(open('resources/price_template.jinja2').read(), autoescape=True)
            
            await bdk.messages().send_message(stream_id, template.render())

        # Start the datafeed read loop
        await datafeed_loop.start()


# Start the main asyncio run
try:
    logging.info("Running bot application...")
    asyncio.run(run())
except KeyboardInterrupt:
    logging.info("Ending bot application")
