import asyncio
from time import time

from ryella.handlers import user_cmd  # pylint: disable=E0402
from ryella.helpers import progress, run_cmd


@user_cmd("mp3", "Convert the replied message to mp3")
async def _mp3(msg):
    if not msg.is_reply:
        await msg.edit("Reply to a message to convert it.")
        return
    reply = await msg.get_reply_message()
    if not any({reply.audio, reply.voice, reply.video}):
        await msg.edit("Reply to a media message to convert it.")
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
    message = await msg.edit("`Converting...`")
    await run_cmd(
        f"ffmpeg -i /downloads/{dl} -acodec libmp3lame -qscale:a 2 /downloads/{dl}.mp3"
    )
    message = await msg.edit("`Uploading...`")
    await msg.client.send_file(
        msg.chat_id,
        "/downloads/" + dl.file_name + ".mp3",
        caption="Converted",
        progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
            progress(d, t, message, time(), "trying to upload")
        ),
    )
    await msg.delete()
