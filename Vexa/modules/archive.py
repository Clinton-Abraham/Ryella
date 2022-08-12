import asyncio
import zipfile
from time import time

from Vexa.handlers import user_cmd  # pylint: disable=E0402
from Vexa.helpers import progress


@user_cmd("compress", "Compress the replied message")
async def _compress(msg):
    if not msg.is_reply:
        await msg.edit("Reply to a message to compress it.")
        return
    reply = await msg.get_reply_message()
    if not reply.media:
        await msg.edit("Reply to a media message to compress it.")
        return
    message = await msg.edit("`Downloading...`")
    start_time = time()
    dl = await msg.client.download_media(
        reply,
        "/downloads/",
        progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
            progress(d, t, message, start_time, "trying to download")
        ),
    )
    message = await msg.edit("`Compressing...`")
    with zipfile.ZipFile(
        "/downloads/" + dl + ".zip",
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as zip:
        zip.write("/downloads/" + dl)
    message = await message.edit("`Uploading...`")
    await msg.client.send_file(
        msg.chat_id,
        "/downloads/" + dl.file_name + ".zip",
        caption="Compressed",
        progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
            progress(d, t, message, time(), "trying to upload")
        ),
    )


# @user_cmd("uncompress", "Uncompress the replied message")
