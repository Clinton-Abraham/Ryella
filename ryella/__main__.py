from .constants import userbot, logger
from .helpers import import_modules, master

try:
    userbot.start()
    master.append(userbot.loop.run_until_complete(userbot.get_me()))
except Exception as e:
    raise e

print('Ryella is now running!')
print(master)

import_modules(logger)

userbot.run_until_disconnected()