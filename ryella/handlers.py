from telethon import events

from .constants import userbot
from .helpers import master

user = master[0]
print(user.id)


def user_cmd(pattern: str):
    pattern = "^(?i)" + "[.,]" + pattern + "?(?: |$)"

    def decorator(func):
        async def wrapper(message):
            await func(message)

        userbot.add_event_handler(
            wrapper,
            events.NewMessage(pattern=pattern, from_users=user.id, forwards=False),
        )

    return decorator
