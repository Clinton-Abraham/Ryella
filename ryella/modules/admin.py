from telethon import errors, functions, types

from ryella.handlers import user_cmd
from ryella.helpers import get_text_content, get_user, resize_image


@user_cmd("setgp", "Set group's picture")
async def set_group_photo(msg):
    if not msg.is_reply:
        await msg.edit("`Reply to a photo or video to set group's photo`")
        return
    if not msg.chat.admin_rights or not msg.chat.admin_rights.change_info:
        return await msg.edit("`You are not an admin!`")
    reply_message = await msg.get_reply_message()
    chat = await msg.get_chat()
    if not isinstance(chat, types.Channel):
        await msg.edit("`This is not a channel`")
        return
    if not reply_message.media:
        await msg.edit("`Reply to a photo or a video`")
        return
    if not any([reply_message.photo, reply_message.sticker, reply_message.document]):
        await msg.edit("`Reply to a photo or a video`")
        return
    new_msg = await msg.edit("`Processing...`")
    if not reply_message.document.mime_type.startswith("image"):
        await new_msg.edit(f"`Reply to a photo or a video`")
        return
    image = await reply_message.download_media()
    resize_image(image, 512, 512)
    try:
        await msg.client(functions.channels.EditPhotoRequest(chat.id, photo=image))
        await new_msg.edit(f"`Changed group's photo`")
    except Exception as e:
        await new_msg.edit(f"`Error: {e}`")


@user_cmd("promote", "Promote a user to admin")
async def _promote(msg):
    user, rank = await get_user(msg)
    if not user:
        return
    chat = await msg.get_chat()
    if not chat.admin_rights or not chat.admin_rights.promote_members:
        return await msg.edit("`You are not an admin!`")
    try:
        await msg.client(
            functions.channels.EditAdminRequest(
                chat.id,
                user.id,
                types.ChatAdminRights(
                    change_info=True,
                    ban_users=True,
                    delete_messages=True,
                    pin_messages=True,
                ),
                rank=rank or "Admin",
            )
        )
        await msg.edit(f"`Promoted {user.first_name} to admin`")
    except errors.UserAdminInvalidError:
        await msg.edit(f"`{user.first_name} is already an admin`")
    except Exception as e:
        await msg.edit(f"`Error: {e}`")


@user_cmd("demote", "Demote a user from admin")
async def _demote(msg):
    user, rank = await get_user(msg)
    if not user:
        return
    chat = await msg.get_chat()
    if not chat.admin_rights or not chat.admin_rights.promote_members:
        return await msg.edit("`You are not an admin!`")
    try:
        await msg.client(
            functions.channels.EditAdminRequest(
                chat.id,
                user.id,
                types.ChatAdminRights(
                    change_info=None,
                    ban_users=None,
                    delete_messages=None,
                    pin_messages=None,
                ),
                rank=rank or "member",
            )
        )
        await msg.edit(f"`Demoted {user.first_name} from admin`")
    except errors.UserAdminInvalidError:
        await msg.edit(f"`{user.first_name} is not an admin`")
    except Exception as e:
        await msg.edit(f"`Error: {e}`")


@user_cmd("ban", "Ban a user from a group")
async def _ban(msg):
    user, rank = await get_user(msg)
    if not user:
        return
    chat = await msg.get_chat()
    if not chat.admin_rights or not chat.admin_rights.ban_users:
        return await msg.edit("`You are not an admin!`")
    try:
        await msg.client(
            functions.channels.EditBannedRequest(
                chat.id,
                user.id,
                types.ChatBannedRights(
                    until_date=None,
                    view_messages=True,
                    send_messages=True,
                    send_media=True,
                    send_stickers=True,
                    send_gifs=True,
                    send_games=True,
                    send_inline=True,
                    embed_links=True,
                ),
            )
        )
        await msg.edit(f"`Banned {user.first_name}`")
    except Exception as e:
        await msg.edit(f"`Error: {e}`")


@user_cmd("unban", "Unban a user from a group")
async def _unban(msg):
    user, rank = await get_user(msg)
    if not user:
        return
    chat = await msg.get_chat()
    if not chat.admin_rights or not chat.admin_rights.ban_users:
        return await msg.edit("`You are not an admin!`")
    try:
        await msg.client(
            functions.channels.EditBannedRequest(
                chat.id,
                user.id,
                types.ChatBannedRights(
                    until_date=None,
                    send_messages=None,
                    send_media=None,
                    send_stickers=None,
                    send_gifs=None,
                    send_games=None,
                    send_inline=None,
                    embed_links=None,
                ),
            )
        )
        await msg.edit(f"`Unbanned {user.first_name}`")
    except Exception as e:
        await msg.edit(f"`Error: {e}`")


@user_cmd("mute", "Mute a user in a group")
async def _mute(msg):
    user, rank = await get_user(msg)
    if not user:
        return
    chat = await msg.get_chat()
    if not chat.admin_rights or not chat.admin_rights.restrict_members:
        return await msg.edit("`You are not an admin!`")
    try:
        await msg.client(
            functions.channels.EditBannedRequest(
                chat.id,
                user.id,
                types.ChatBannedRights(until_date=None, send_messages=True),
            )
        )
        await msg.edit(f"`Muted {user.first_name}`")
    except Exception as e:
        await msg.edit(f"`Error: {e}`")


@user_cmd("unmute", "Unmute a user in a group")
async def _unmute(msg):
    user, rank = await get_user(msg)
    if not user:
        return
    chat = await msg.get_chat()
    if not chat.admin_rights or not chat.admin_rights.restrict_members:
        return await msg.edit("`You are not an admin!`")
    try:
        await msg.client(
            functions.channels.EditBannedRequest(
                chat.id,
                user.id,
                types.ChatBannedRights(until_date=None, send_messages=False),
            )
        )
        await msg.edit(f"`Unmuted {user.first_name}`")
    except Exception as e:
        await msg.edit(f"`Error: {e}`")


@user_cmd("kick", "Kick a user from a group")
async def _kick(msg):
    user, rank = await get_user(msg)
    if not user:
        return
    chat = await msg.get_chat()
    if not chat.admin_rights or not chat.admin_rights.ban_users:
        return await msg.edit("`You are not an admin!`")
    try:
        await msg.client.kick_participant(chat.id, user.id)
        await msg.edit(f"`Kicked {user.first_name}`")
    except Exception as e:
        await msg.edit(f"`Error: {e}`")


@user_cmd("pin", "Pin a message")
async def _pin(msg):
    chat = await msg.get_chat()
    if not chat.admin_rights or not chat.admin_rights.pin_messages:
        return await msg.edit("`You are not an admin!`")
    try:
        await msg.client(
            functions.messages.UpdatePinnedMessageRequest(
                chat.id, msg.reply_to_msg_id, True
            )
        )
        await msg.edit(f"`Pinned message`")
    except Exception as e:
        await msg.edit(f"`Error: {e}`")


@user_cmd("unpin", "Unpin a message")
async def _unpin(msg):
    chat = await msg.get_chat()
    if not chat.admin_rights or not chat.admin_rights.pin_messages:
        return await msg.edit("`You are not an admin!`")
    try:
        await msg.client(
            functions.messages.UpdatePinnedMessageRequest(
                chat.id, msg.reply_to_msg_id, unpin=True
            )
        )
        await msg.edit(f"`Unpinned message`")
    except Exception as e:
        await msg.edit(f"`Error: {e}`")


@user_cmd("invite", "Invite a user to a group")
async def _invite(msg):
    user, rank = await get_user(msg)
    if not user:
        return
    chat = await msg.get_chat()
    if not chat.admin_rights or not chat.admin_rights.invite_users:
        return await msg.edit("`You are not an admin!`")
    try:
        await msg.client(functions.channels.InviteToChannelRequest(chat.id, user.id))
        await msg.edit(f"`Invited {user.first_name}`")
    except Exception as e:
        await msg.edit(f"`Error: {e}`")


@user_cmd("kickme", "Kick yourself from a group")
async def _kickme(msg):
    try:
        await msg.client.kick_participant(msg.chat.id, msg.from_user.id)
        await msg.edit(f"`Kicked {msg.from_user.first_name}`")
    except Exception as e:
        await msg.edit(f"`Error: {e}`")


@user_cmd("undlt", "Undelete a message")
async def _undlt(msg):
    chat = await msg.get_chat()
    if not chat.admin_rights or not chat.admin_rights.delete_messages:
        return await msg.edit("`You are not an admin!`")
    try:
        async for message in msg.client.iter_admin_log(chat.id, limit=4, reverse=True):
            await msg.respond(message.old.message)
    except Exception as e:
        await msg.edit(f"`Error: {e}`")


@user_cmd("del", "Delete a message")
async def _del(msg):
    chat = await msg.get_chat()
    if not chat.admin_rights or not chat.admin_rights.delete_messages:
        return await msg.edit("`You are not an admin!`")
    try:
        await msg.client.delete_messages(chat.id, msg.reply_to_msg_id)
        await msg.edit("`Deleted message`")
    except Exception as e:
        await msg.edit(f"`Error: {e}`")


@user_cmd("delall", "Delete all messages")
async def _delall(msg):
    chat = await msg.get_chat()
    if not chat.admin_rights or not chat.admin_rights.delete_messages:
        return await msg.edit("`You are not an admin!`")
    try:
        await msg.client(
            functions.messages.DeleteHistoryRequest(chat.id, 0, revoke=True)
        )
        await msg.edit("`Deleted all messages`")
    except Exception as e:
        await msg.edit(f"`Error: {e}`")


@user_cmd("leave", "Leave a group")
async def _leave(msg):
    await msg.edit("`Leaving group...`")
    await msg.client(functions.channels.LeaveChannelRequest(msg.chat.id))


@user_cmd("admins", "Get a list of admins")
async def _admins(msg):
    chat = await msg.get_chat()
    if not chat.admin_rights or not chat.admin_rights.change_info:
        return await msg.edit("`You are not an admin!`")
    try:
        admins = await msg.client.get_participants(
            chat.id, filter=types.ChannelParticipantsAdmins
        )
        text = ""
        for admin in admins:
            text += f"{admin.first_name} {admin.last_name}\n"
        await msg.edit(text)
    except Exception as e:
        await msg.edit(f"`Error: {e}`")


@user_cmd("settitle", "Set a group's title")
async def _settitle(msg):
    chat = await msg.get_chat()
    title = await get_text_content(msg)
    if not title:
        return await msg.edit("`No title provided!`")
    if not chat.admin_rights or not chat.admin_rights.change_info:
        return await msg.edit("`You are not an admin!`")
    try:
        await msg.client(functions.channels.EditTitleRequest(chat.id, msg.text))
        await msg.edit(f"`Set title to {msg.text}`")
    except Exception as e:
        await msg.edit(f"`Error: {e}`")


@user_cmd("setabout", "Set a group's about")
async def _setabout(msg):
    chat = await msg.get_chat()
    about = await get_text_content(msg)
    if not about:
        return await msg.edit("`No text given!`")
    if not chat.admin_rights or not chat.admin_rights.change_info:
        return await msg.edit("`You are not an admin!`")
    try:
        await msg.client(functions.messages.EditChatAboutRequest(chat.id, about=about))
        await msg.edit(f"`Set about to {msg.text}`")
    except Exception as e:
        await msg.edit(f"`Error: {e}`")
