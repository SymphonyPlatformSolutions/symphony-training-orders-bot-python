import random

from symphony.bdk.core.service.message.message_service import MessageService
from symphony.bdk.core.activity.form import FormReplyActivity, FormReplyContext

class PriceFormReply(FormReplyActivity):
    def __init__(self, messages: MessageService):
        self._messages = messages
        super().__init__()

    def matches(self, context: FormReplyContext) -> bool:
        return context.form_id == 'price'

    async def on_activity(self, context: FormReplyContext):
        ticker = context.get_form_value("ticker")
        price = random.randint(30, 500)
        reply = f'Price of <cash tag =\"{ticker}\" /> is {price}'

        await self._messages.send_message(context.source_event.stream.stream_id, reply)