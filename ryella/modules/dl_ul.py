import os
import re
import time

import tinytag
from telethon import types

from ..handlers import user_cmd
from ..helpers import generate_thumbnail, get_text_content, get_video_metadata
from ..transfers import upload_file


@user_cmd("ul")
async def _ul(e):
    l = await get_text_content(e)
    if not l:
        return await _ls(e)
    msg = await e.reply("`Uploading...`")
    caption = ""
    thumb, attributes, streamable, chat = None, [], False, e.chat_id
    action = "document"
    if any([re.search(x, l.lower()) for x in ["--chat", "-c"]]):
        if "--chat" in l.lower():
            args = l.split("--chat")
            l = re.sub("--chat (.*) -", "-", l).strip()
            if "--chat" in l.lower():
                l = re.sub("--chat (.*)", "", l).strip()
        else:
            args = l.split("-c")
            l = re.sub("-c (.*) -", "-", l).strip()
            if "-c" in l.lower():
                l = re.sub("-c (.*)", "", l).strip()
        chat = args[1].split("-")[0].strip() if len(args) > 1 else e.chat_id
        chat = int(chat) if str(chat).isdigit() else chat
    if any([re.search(x, l.lower()) for x in ["--text", "-t"]]):
        args = l.split("--text") if "--text" in l else l.split("-t")
        caption = args[1] if len(args) > 1 else ""
        l = args[0].strip()
    filename = l.split("\\")[-1]
    caption = caption or filename
    filename = filename.split("/")[-1] if filename == l else filename
    if l.endswith(("mp4", "mkv", "3gp", "webm")):
        thumb = generate_thumbnail(l, l + "_thumb.jpg")
        d, w, h = get_video_metadata(l)
        attributes = [
            types.DocumentAttributeVideo(w=w, h=h, duration=d, supports_streaming=True)
        ]
        streamable = True
        action = "video"
    elif l.endswith(("mp3", "wav", "flv", "ogg", "opus")):
        metadata = tinytag.TinyTag.get(l)
        attributes = [
            types.DocumentAttributeAudio(
                duration=int(metadata.duration or "0"),
                performer=metadata.artist or "Me",
                title=metadata.title or "Unknown",
            )
        ]
        action = "audio"
    try:
        file = await upload_file(e.client, l)
        async with e.client.action(chat, action):
            await e.client.send_message(
                chat,
                caption,
                file=file,
                thumb=thumb,
                attributes=attributes,
                supports_streaming=streamable,
            )
        await msg.delete()
        os.remove(thumb) if thumb else None
    except Exception as exc:
        await msg.edit("`error on uploading.\n{}`".format(str(exc)))


@user_cmd("ls", "List directory contents")
async def _ls(message):
    content = await get_text_content(message)
    if not content:
        content = "./"
    if not content.endswith("/"):
        content = content + "/"
    try:
        directory = os.listdir(content)
    except Exception as a:
        return await message.edit(str(a))
    dir_contents = "<b>PATH: <i>{}</i></b>\n".format(content)
    folders = [0, 0]
    files = [0, 0]
    files_list = []
    for con in directory:
        size = os.path.getsize(content + con)
        if os.path.isdir(content + con):
            folders[0] += 1
            folders[1] += size
            dir_contents += "📂<code> {} </code>(<code>{}</code>)\n".format(
                con, human_readable_size(size)
            )
        else:
            files[0] += 1
            files[1] += size
            files_list.append(con)
    for con in files_list:
        size = os.path.getsize(content + con)
        dir_contents += "📃<code> {} </code>(<code>{}</code>)\n".format(
            con, human_readable_size(size)
        )
    dir_contents += "\n"
    dir_contents += "<b>Folders:</b> {}</code> (<code>{}</code>)".format(
        folders[0], human_readable_size(folders[1])
    )
    dir_contents += "\n<b>Files:</b> {}</code> (<code>{}</code>)".format(
        files[0], human_readable_size(files[1])
    )
    dir_contents += "\n<b>Total:</b> {}</code>(<code>{}</code>)".format(
        files[0] + folders[0], human_readable_size(files[1] + folders[1])
    )
    await message.edit(dir_contents, parse_mode="html")


@user_cmd("dl", "Download the replied media")
async def dl(message):
    if not message.is_reply:
        await message.edit("Reply to a message to download it.")
        return
    reply = await message.get_reply_message()
    if not reply.media:
        await message.edit("Reply to a media message to download it.")
        return
    start_time = time()
    message = await message.edit("`Downloading...`")
    file = await reply.download_media()
    end_time = time()
    await message.edit(f"Downloaded to `{file}` in `{end_time - start_time}`s.")
