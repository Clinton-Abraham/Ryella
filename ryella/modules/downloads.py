
from ryella.helpers import get_text_content
from ..constants import userbot
from telethon import events
from ..handlers import user_cmd
from time import time
import asyncio


@user_cmd('(dl|download)')
async def dl(message):
    if not message.is_reply:
        await message.edit('Reply to a message to download it.')
        return
    reply = await message.get_reply_message()
    if not reply.media:
        await message.edit('Reply to a media message to download it.')
        return
    start_time = time()
    file = await reply.download_media()
    end_time = time()
    await message.edit(f'Downloaded to {file} in {end_time - start_time} seconds.')


@user_cmd('(upload|ul)')
async def upload(message):
    content = await get_text_content(message)
    if not content:
        await message.edit('specify a file to upload.')
        return
    try:
        await message.client.send_file(message.chat_id, content)
    except BaseException as exc:
        await message.edit(str(exc))
        return


@user_cmd('curl')
async def curl(message):
    content = await get_text_content(message)
    if not content:
        await message.edit('specify a url to curl.')
        return
    cmd = f'curl -s {content}'
    msg = await message.edit('Starting curl...')
    proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, universal_newlines=True)
    for line in (await proc.stdout.read()).split('\n'):
        if line != msg.text:
            await asyncio.sleep(4)
            await msg.edit(line)
    if proc.returncode != 0:
        await msg.edit(f'Error: {await proc.stderr.read()}')
    else:
        await msg.edit('Downloaded successfully.')

sk_key_regex = r'sk_live_(.+?)'  # sk_live_<key>
