import datetime

from telethon import events

from Vexa.constants import userbot
from Vexa.modules.db.afk import get_afk, is_afk, set_afk


@userbot.on(events.NewMessage(outgoing=True))
async def set_not_afk(event):
    if "afk" in event.text:
        return await modify_afk(event)
    if not is_afk():
        return
    set_afk(False)
    afk_time = get_afk()
    afk_since = datetime.datetime.now() - datetime.timedelta(seconds=afk_time)
    afk_since = afk_since.strftime("%Y-%m-%d %H:%M:%S")
    caption = "__Back from AFK!__\n\n**Away since**: " + afk_since
    await event.edit(caption=caption)


async def modify_afk(msg):
    await msg.edit("__I'm AFK!__")
    if len(msg.text.split()) >= 2:
        reason = msg.text.split(" ")[1]
    else:
        reason = ""
    set_afk(True, reason)


@userbot.on(
    events.NewMessage(incoming=True, func=lambda e: e.is_private or e.mentioned)
)
async def afk_message(event):
    if not is_afk():
        return
    afk_time, reason = get_afk()
    afk_since = datetime.datetime.now() - datetime.timedelta(seconds=afk_time)
    afk_since = afk_since.strftime("%Y-%m-%d %H:%M:%S")
    caption = (
        "My Master is AFK since "
        + afk_since
        + ".\n"
        + ("I am currently unavailable." or reason)
    )
    await event.edit(caption=caption)
