import telethon
import logging
import pymongo
import os
import importlib

master = []


def setup_logging():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    # handler = logging.handlers.RotatingFileHandler(
    # 'ryella.log', maxBytes=1024 * 1024 * 5, backupCount=5)
    # handler.setLevel(logging.INFO)
    # formatter = logging.Formatter(
    # '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # handler.setFormatter(formatter)
    # logger.addHandler(handler)

    logger = logging.getLogger('ryella')

    return logger


def setup_client(api_key, api_secret, session_id):
    user = telethon.TelegramClient(
        telethon.sessions.StringSession(session_id), api_key, api_secret)
    return user


def setup_db(uri: str):
    return pymongo.MongoClient(uri).ryella if uri else None


def import_modules(logger):
    path = 'ryella/modules/'
    for filename in os.listdir(path):
        if filename.endswith('.py'):
            importlib.import_module('ryella.modules.' + filename[:-3])
            logger.info('Imported module: ' + filename)


def get_readable_time(seconds: int):
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    if hours > 0:
        return '{}h {}m {}s'.format(hours, minutes, seconds)
    elif minutes > 0:
        return '{}m {}s'.format(minutes, seconds)
    else:
        return '{}s'.format(seconds)


async def get_text_content(message):
    if message.reply_to_msg_id:
        reply = await message.get_reply_message()
        if reply.media:
            if reply.document:
                doc = await reply.download_media()
                with open(doc, 'rb') as f:
                    os.remove(doc)
                    return f.read()
            else:
                return None
        else:
            return reply.text
    else:
        try:
            return message.text.split(' ', 1)[1]
        except:
            return None


async def get_user(e):
    '''
    Returns the user pointed to by the message.
    '''
    args = e.text.split(maxsplit=2)
    if e.is_reply:
        user = (await e.get_reply_message()).sender
        arg = (args[1] + (args[2] if len(args) > 2 else "")
               ) if len(args) > 1 else ""
    else:
        if len(args) == 1:
            return e.sender, ""
        try:
            user = await e.client.get_entity(args[1])
        except BaseException as ex:
            return e.sender, ""
        arg = args[2] if len(args) > 2 else ""
    return user, arg


async def progress_callback(current, total):
    print('Downloaded {} of {}'.format(current, total))
    return current < total
