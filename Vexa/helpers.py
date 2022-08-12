import asyncio
import importlib
import logging
import math
import os
import platform
import socket
import sys
import time
from datetime import datetime

import ffmpeg
import psutil
import pymongo
import telethon
from PIL import Image

master = []


def setup_logging():
    """Sets up logging."""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
        stream=logging.FileHandler("vexa.log", mode="a", encoding="utf-8", delay=True),
    )
    return logging.getLogger("Vexa")


def setup_client(api_key, api_secret, session_id):
    """Returns a telethon client."""
    user = telethon.TelegramClient(
        telethon.sessions.StringSession(session_id), api_key, api_secret
    )
    return user


def setup_db(uri: str):
    """Returns a mongo client."""
    return pymongo.MongoClient(uri).ryella if uri else None


def import_modules(logger):
    """Imports all modules in the modules folder."""
    path = "ryella/modules/"
    for filename in os.listdir(path):
        if filename.endswith(".py"):
            importlib.import_module("ryella.modules." + filename[:-3])
            logger.info("Imported module: " + filename)


def get_readable_time(seconds: int):
    """Returns a human readable string of a given duration in seconds."""
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    if hours > 0:
        return "{}h {}m {}s".format(hours, minutes, seconds)
    elif minutes > 0:
        return "{}m {}s".format(minutes, seconds)
    else:
        return "{}s".format(seconds)


async def get_text_content(message):
    """Returns the text content of a message."""
    if message.reply_to_msg_id:
        reply = await message.get_reply_message()
        if reply.media:
            if reply.document:
                doc = await reply.download_media()
                with open(doc, "rb") as f:
                    os.remove(doc)
                    return f.read()
            else:
                return None
        else:
            return reply.text
    else:
        try:
            return message.text.split(" ", 1)[1]
        except:
            return None


async def get_user(e):
    """Returns the user pointed to by the message."""
    args = e.text.split(maxsplit=2)
    if e.is_reply:
        user = (await e.get_reply_message()).sender
        arg = (args[1] + (args[2] if len(args) > 2 else "")) if len(args) > 1 else ""
    else:
        if len(args) == 1:
            return e.sender, ""
        try:
            user = await e.client.get_entity(args[1])
        except BaseException:
            return e.sender, ""
        arg = args[2] if len(args) > 2 else ""
    return user, arg


async def progress(
    current, total, event, start, type_of_ps, file_name=None, is_cancelled=None
):
    """Generic progress_callback for uploads and downloads."""
    now = time.time()
    diff = now - start
    if is_cancelled is True:
        return False
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion
        progress_str = "[{0}{1}] {2}%\n".format(
            "".join(["▰" for i in range(math.floor(percentage / 10))]),
            "".join(["▱" for i in range(10 - math.floor(percentage / 10))]),
            round(percentage, 2),
        )
        tmp = progress_str + "{0} of {1}\nETA: {2}".format(
            human_readable_size(current),
            human_readable_size(total),
            get_readable_time(estimated_total_time),
        )
        if file_name:
            await event.edit(
                "{}\nFile Name: `{}`\n{}".format(type_of_ps, file_name, tmp)
            )
        else:
            await event.edit("{}\n{}".format(type_of_ps, tmp))


def human_readable_size(size, speed=False):
    """Returns a human readable string of a given size in bytes."""
    variables = ["bytes", "KB", "MB", "GB", "TB"]
    if speed:
        variables = ["bps", "Kbps", "Mbps", "Gbps", "Tbps"]
    for x in variables:
        if size < 1024.0:
            return "%3.1f %s" % (size, x)
        size /= 1024.0
    return "%3.1f %s" % (size, "TB")


def get_file_extension(file_name):
    """Returns the extension of a file."""
    return file_name.split(".")[-1]


def resize_image(image, width, height):
    """Resizes an image to the given width and height."""
    image = Image.open(image)
    image = image.resize((width, height), Image.ANTIALIAS)
    return image


async def run_cmd(cmd):
    """Runs a shell command."""
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout.decode(), stderr.decode()


def system_information():
    """Get full system Specs."""
    get_size = human_readable_size
    uname = platform.uname()
    info = "**System Information**"
    info += f"\nSystem: {uname.system}"
    info += f"\nNode Name: {uname.node}"
    info += f"\nMachine: {uname.machine}"
    info += f"\nProcessor: {uname.processor}"
    info += f"\nIp-Address: {socket.gethostbyname(socket.gethostname())}"

    boot_time_timestamp = psutil.boot_time()
    bt = datetime.fromtimestamp(boot_time_timestamp)
    info += (
        f"\nBoot Time: {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}"
    )

    info += "\n\n**CPU**"
    info += f"\nPhysical cores: {psutil.cpu_count(logical=False)}"
    info += f"\nTotal cores: {psutil.cpu_count(logical=True)}"
    # CPU frequencies
    cpufreq = psutil.cpu_freq()
    info += f"\nCurrent Frequency: {cpufreq.current:.2f}Mhz"
    # CPU usage
    info += f"\nTotal CPU Usage: {psutil.cpu_percent()}%"
    info += "\n\n**Memory**"
    svmem = psutil.virtual_memory()
    info += f"\nTotal: {get_size(svmem.total)}"
    info += f"\nAvailable: {get_size(svmem.available)}"
    info += f"\nUsed: {get_size(svmem.used)}"
    info += f"\nPercentage: {svmem.percent}%"
    # Disk Information
    info += "\n\n**Partitions and Usage:**"
    # get all disk partitions
    partitions = psutil.disk_partitions()
    for partition in partitions:
        info += f"\n=== Device: {partition.device} ==="
        info += f"\n  Mountpoint: {partition.mountpoint}"
        info += f"\n  File system type: {partition.fstype}"
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            # this can be catched due to the disk that
            # isn't ready
            continue
        info += f"\n  Total Size: {get_size(partition_usage.total)}"
        info += f"\n  Used: {get_size(partition_usage.used)}"
        info += f"\n  Free: {get_size(partition_usage.free)}"
        info += f"\n  Percentage: {partition_usage.percent}%"
    # get IO statistics since boot
    disk_io = psutil.disk_io_counters()
    info += f"Total read: {get_size(disk_io.read_bytes)}"
    info += f"Total write: {get_size(disk_io.write_bytes)}"

    # Network information
    info += "\n\n**Network Information**"
    net_io = psutil.net_io_counters()
    info += f"\n**Total Bytes Sent:** {get_size(net_io.bytes_sent)}"
    info += f"\n**Total Bytes Received:** {get_size(net_io.bytes_recv)}"
    return info


def generate_thumbnail(in_filename, out_filename):
    """gen thumb for video"""
    probe = ffmpeg.probe(in_filename)
    time = 2
    width = probe["streams"][0]["width"]
    try:
        (
            ffmpeg.input(in_filename, ss=time)
            .filter("scale", width, -1)
            .output(out_filename, vframes=1)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        print(e.stderr.decode(), file=sys.stderr)
        return ""
    return out_filename


def get_video_metadata(file):
    data = ffmpeg.probe(file)
    try:
        return (
            int(data.get("format", {}).get("duration", "0").split(".")[0]),
            data.get("streams", [])[0].get("width", 1),
            data.get("streams", [])[0].get("height", 0),
        )
    except (KeyError, IndexError):
        return (0, 0, 0)
