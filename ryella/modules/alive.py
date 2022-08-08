from platform import platform, python_version
from time import time

from telethon import __version__

from ..constants import start_time
from ..handlers import user, user_cmd
from ..helpers import get_readable_time

alive_caption = """
Bᴏᴛ Oғ <b>𝙍oseLoverX</b> [𝙸𝚅𝙰𝚁]

Mᴀɪɴ Mᴇɴᴜ

Pʟᴜɢɪɴs ~ 23
Aᴅᴅᴏɴs ~ 13
Tᴏᴛᴀʟ Cᴏᴍᴍᴀɴᴅs ~ 2772
"""

ping_caption = """
<b>Ping!! </b> <code>{}ms</code>
<b>Uptime:</b> <code>{}</code>
"""


@user_cmd("alive", "Check if the bot is alive")
async def alive(message):
    await message.edit(
        alive_caption,
        parse_mode="html",
        link_preview=False,
    )


@user_cmd("ping", "Check the bot's ping")
async def _ping(message):
    uptime = get_readable_time(time() - start_time)
    ping = time() - message.date.timestamp()
    await message.edit(ping_caption.format(round(ping, 2), uptime), parse_mode="html")
