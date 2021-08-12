import re

from symphony.bdk.core.activity.command import CommandContext
from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent
from symphony.bdk.gen.pod_model.v3_room_attributes import V3RoomAttributes
from symphony.bdk.core.service.message.message_service import MessageService
from jinja2 import Template
from .activities import EchoCommandActivity, GreetUserJoinedActivity
from .gif_activities import GifSlashCommand, GifFormReplyActivity


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
        self._template = Template(open('resources/order_template.jinja2').read(), autoescape=True)
        super().__init__()

    async def on_symphony_elements_action(self, initiator: V4Initiator, event: V4MessageSent):
        if event.form_id == 'order':
            values = event.form_values
            reply_template = self._template.render(values)

            await self._messages.send_message(event.stream.stream_id, reply_template)
