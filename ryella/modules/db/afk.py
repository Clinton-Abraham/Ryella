from ryella.constants import db
import time

afk = db.ryella.afk

AFk: bool = False


def is_afk():
    return AFk


def set_afk(value: bool):
    global AFk
    AFk = value
    afk.update_one({"_id": "afk"}, {
        "$set": {"value": value, "time": time.time()}})
    return AFk


def get_afk():
    return afk.find_one({"_id": "afk"})["time"] if afk.find_one({"_id": "afk"}) else 0


def load_afk():
    global AFk
    AFk = get_afk()


load_afk()
