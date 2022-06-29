from time import time

from ..constants import start_time
from ..handlers import user, user_cmd
from ..helpers import get_readable_time

alive_caption = """
<b>💎💎 Ryella Userbot 💎💎</b>

<b>Version:</b> <code>1.0.0</code>
<b>Master:</b> <a href="tg://user?id={}">{}</a>
<b>Python:</b> <code>{}</code>
<b>Platform:</b> <code>{}</code>
<b>Telethon:</b> <code>{}</code>
"""

ping_caption = """
<b>Ping:</b> <code>{}</code>
<b>Uptime:</b> <code>{}</code>
"""


@user_cmd("alive")
async def alive(message):
    await message.edit(
        alive_caption.format(
            user.id,
            user.first_name.capitalize(),
            "3.10.5",
            "Windows11",
            "1.25.1",
        ),
        parse_mode="html",
        link_preview=False,
    )


@user_cmd("ping")
async def ping(message):
    uptime = get_readable_time(time() - start_time)
    ping = str(abs(int(time() - message.date.timestamp())) * 200) + " ms"
    await message.edit(ping_caption.format(ping, uptime), parse_mode="html")
