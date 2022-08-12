from platform import python_version
from time import time

from ..constants import start_time
from ..handlers import user, user_cmd
from ..helpers import get_readable_time

alive_caption = """
**Vexa is online!**

**Uptime:** `{uptime}`
**Master:** {master}
**Version:** `{version}`
**Python:** {python}
**Database:** {db}
**___________________**
"""

ping_caption = """
<b>Ping!! </b> <code>{}ms</code>
<b>Uptime:</b> <code>{}</code>
"""


@user_cmd("alive", "Check if the bot is alive")
async def alive(message):
    await message.edit(
        alive_caption.format(
            get_readable_time(time() - start_time),
            f"[{user.first_name}](tg://user?id={user.id})",
            "1.2.0",
            python_version(),
            "MongoDB",
        )
    )


@user_cmd("ping", "Check the bot's ping")
async def _ping(message):
    uptime = get_readable_time(time() - start_time)
    ping = time() - message.date.timestamp()
    await message.edit(ping_caption.format(round(ping, 2), uptime), parse_mode="html")
