from os import getenv
from time import time

from dotenv import load_dotenv
from pymongo.errors import ServerSelectionTimeoutError

from . import helpers

start_time = time()

logger = helpers.setup_logging()
load_dotenv()
userbot = helpers.setup_client(getenv("API_KEY"), getenv("API_HASH"), getenv("SESSION"))
db = helpers.setup_db(getenv("MONGODB_URI"))

try:
    db.ryella.list_indexes()
    logger.info("Connected to MongoDB")
except ServerSelectionTimeoutError:
    logger.error("Mongodb connection failed")
