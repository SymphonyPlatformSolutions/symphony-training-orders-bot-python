import random
from jinja2 import Template

from symphony.bdk.core.service.message.message_service import MessageService
from symphony.bdk.core.activity.form import FormReplyActivity, FormReplyContext

class PriceFormReply(FormReplyActivity):
    def __init__(self, messages: MessageService):
        self._messages = messages
        self._template = Template(open('resources/price_response_template.jinja2').read(), autoescape=True)
        super().__init__()

    def matches(self, context: FormReplyContext) -> bool:
        return context.form_id == 'price'

    async def on_activity(self, context: FormReplyContext):
        ticker = context.get_form_value("ticker")
        price = random.randint(30, 500)
        reply = self._template.render(ticker=ticker, price=price)

        await self._messages.send_message(context.source_event.stream.stream_id, reply)