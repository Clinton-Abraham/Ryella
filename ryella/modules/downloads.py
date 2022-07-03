import os
from time import time

from ryella.helpers import get_text_content, human_readable_size

from ..handlers import user_cmd # pylint: disable=E0401


@user_cmd("dl", 'Download the replied media')
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


@user_cmd("ul", 'Upload the file from given path')
async def upload(message):
    content = await get_text_content(message)
    if not content:
        await message.edit("specify a file to upload.")
        return
    try:
        await message.client.send_file(message.chat_id, content)
        await message.delete()
    except BaseException as exc:
        await message.edit(str(exc))
        return


@user_cmd("ls", 'List directory contents')
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
