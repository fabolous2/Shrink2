from typing import Any,Callable,Dict,Awaitable,Optional
from aiogram import BaseMiddleware,Router
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

class MailChatActionMiddleware(BaseMiddleware):
    def __init__(
        self,
        router: Optional[Router] = None,
    ):
        if router:
            router.message.outer_middleware(self)
            router.channel_post.outer_middleware(self)

    async def __call__(
            self,
            handler:Callable[[Message,Dict[str,Any]],Awaitable[Any]],
            event:Message,
            data:Dict[str,Any]
    ) -> Any:
        chat_action= get_flag(data,'chat_action')
        if not chat_action:
            return await handler(event,data)

        async with ChatActionSender(action=chat_action,chat_id=event.chat.id,bot=event.bot):
            return await event.answer("Loading..."),await handler(event,data)