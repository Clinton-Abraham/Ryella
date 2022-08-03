from ..handlers import user_cmd
from ..helpers import human_readable_size
from os import remove
from ..transfers import upload_file
from ..helpers import (
    generate_thumbnail,
    get_mention,
    get_text_content,
    get_user,
    get_video_metadata,
    human_readable_size,
)

@user_cmd("ul")
async def _ul(e):
    l = await get_text_content(e)
    if not l:
        return await _ls(e)
    msg = await e.reply("`Uploading...`")
    caption = ""
    thumb, attributes, streamable, chat= None,[], False, e.chat_id
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
        t = remove(thumb) if thumb else None
    except Exception as exc:
        await msg.edit("`error on uploading.\n{}`".format(str(exc)))
