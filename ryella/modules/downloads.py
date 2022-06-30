import os
from time import time

from ryella.helpers import get_text_content, human_readable_size

from ..handlers import user_cmd


@user_cmd("(dl|download)")
async def dl(message):
    if not message.is_reply:
        await message.edit("Reply to a message to download it.")
        return
    reply = await message.get_reply_message()
    if not reply.media:
        await message.edit("Reply to a media message to download it.")
        return
    start_time = time()
    file = await reply.download_media()
    end_time = time()
    await message.edit(f"Downloaded to {file} in {end_time - start_time} seconds.")


@user_cmd("(upload|ul)")
async def upload(message):
    content = await get_text_content(message)
    if not content:
        await message.edit("specify a file to upload.")
        return
    try:
        await message.client.send_file(message.chat_id, content)
    except BaseException as exc:
        await message.edit(str(exc))
        return


@user_cmd("ls")
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
    dir_contents += "<b>TotalFolders:</b> {} {}".format(
        folders[0], human_readable_size(folders[1])
    )
    dir_contents += "\n<b>TotalFiles:</b> {} {}".format(
        files[0], human_readable_size(files[1])
    )
    dir_contents += "\n<b>Total:</b> {} {}</code>".format(
        files[0] + folders[0], human_readable_size(files[1] + folders[1])
    )
    await message.edit(dir_contents, parse_mode="html")
