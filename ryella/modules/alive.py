from time import time

from ..constants import start_time
from ..handlers import user, user_cmd
from ..helpers import get_readable_time
from platform import python_version, platform
from telethon import __version__

alive_caption = """
<b>Ryella Userbot</b>

<b>Version:</b> <code>1.0.1</code>
<b>Master:</b> <b><a href="tg://user?id={}">{}</a></b>
<b>Python:</b> <code>{}</code>
<b>Platform:</b> <code>{}</code>
<b>Telethon:</b> <code>{}</code>
"""

ping_caption = """
<b>Ping:</b> <code>{}</code>
<b>Uptime:</b> <code>{}</code>
"""


@user_cmd("alive", "Check if the bot is alive")
async def alive(message):
    await message.edit(
        alive_caption.format(
            user.id,
            user.first_name.capitalize(),
            python_version(),
            platform(),
            __version__,
        ),
        parse_mode="html",
        link_preview=False,
    )


@user_cmd("ping", "Check the bot's ping")
async def _ping(message):
    uptime = get_readable_time(time() - start_time)
    ping = int(time() - message.date.timestamp())
    await message.edit(ping_caption.format(ping, uptime), parse_mode="html")
