from telethon import events

from .constants import userbot
from .helpers import master

user = master[0]

def user_cmd(pattern: str, _help: str = ""):
    """
    Decorator for user commands.
    """
    pattern = "^(?i)" + "[,*]" + pattern + "?(?: |$)"

    def decorator(func):
        async def wrapper(message):
            await func(message)

        userbot.add_event_handler(
            wrapper,
            events.NewMessage(pattern=pattern, from_users=user.id, forwards=False),
        )

    return decorator
