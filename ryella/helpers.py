import asyncio
import importlib
import logging
import math
import os
import time
import psutil
import platform
from datetime import datetime
import socket
import uuid
import re
import pymongo
import telethon
from PIL import Image

master = []


def setup_logging():
    """Sets up logging."""
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

    logger = logging.getLogger("ryella")

    return logger


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
    print("="*40, "System Information", "="*40)
    uname = platform.uname()
    print(f"System: {uname.system}")
    print(f"Node Name: {uname.node}")
    print(f"Release: {uname.release}")
    print(f"Version: {uname.version}")
    print(f"Machine: {uname.machine}")
    print(f"Processor: {uname.processor}")
    print(f"Ip-Address: {socket.gethostbyname(socket.gethostname())}")
    print(f"Mac-Address: {':'.join(re.findall('..', '%012x' % uuid.getnode()))}")

    # Boot Time
    print("="*40, "Boot Time", "="*40)
    boot_time_timestamp = psutil.boot_time()
    bt = datetime.fromtimestamp(boot_time_timestamp)
    print(f"Boot Time: {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}")

    # print CPU information
    print("="*40, "CPU Info", "="*40)
    # number of cores
    print("Physical cores:", psutil.cpu_count(logical=False))
    print("Total cores:", psutil.cpu_count(logical=True))
    # CPU frequencies
    cpufreq = psutil.cpu_freq()
    print(f"Max Frequency: {cpufreq.max:.2f}Mhz")
    print(f"Min Frequency: {cpufreq.min:.2f}Mhz")
    print(f"Current Frequency: {cpufreq.current:.2f}Mhz")
    # CPU usage
    print("CPU Usage Per Core:")
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        print(f"Core {i}: {percentage}%")
    print(f"Total CPU Usage: {psutil.cpu_percent()}%")

    # Memory Information
    print("="*40, "Memory Information", "="*40)
    # get the memory details
    svmem = psutil.virtual_memory()
    print(f"Total: {get_size(svmem.total)}")
    print(f"Available: {get_size(svmem.available)}")
    print(f"Used: {get_size(svmem.used)}")
    print(f"Percentage: {svmem.percent}%")

    print("="*20, "SWAP", "="*20)
    # get the swap memory details (if exists)
    swap = psutil.swap_memory()
    print(f"Total: {get_size(swap.total)}")
    print(f"Free: {get_size(swap.free)}")
    print(f"Used: {get_size(swap.used)}")
    print(f"Percentage: {swap.percent}%")

    # Disk Information
    print("="*40, "Disk Information", "="*40)
    print("Partitions and Usage:")
    # get all disk partitions
    partitions = psutil.disk_partitions()
    for partition in partitions:
        print(f"=== Device: {partition.device} ===")
        print(f"  Mountpoint: {partition.mountpoint}")
        print(f"  File system type: {partition.fstype}")
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            # this can be catched due to the disk that
            # isn't ready
            continue
        print(f"  Total Size: {get_size(partition_usage.total)}")
        print(f"  Used: {get_size(partition_usage.used)}")
        print(f"  Free: {get_size(partition_usage.free)}")
        print(f"  Percentage: {partition_usage.percent}%")
    # get IO statistics since boot
    disk_io = psutil.disk_io_counters()
    print(f"Total read: {get_size(disk_io.read_bytes)}")
    print(f"Total write: {get_size(disk_io.write_bytes)}")

    ## Network information
    print("="*40, "Network Information", "="*40)
    ## get all network interfaces (virtual and physical)
    if_addrs = psutil.net_if_addrs()
    for interface_name, interface_addresses in if_addrs.items():
        for address in interface_addresses:
            print(f"=== Interface: {interface_name} ===")
            if str(address.family) == 'AddressFamily.AF_INET':
                print(f"  IP Address: {address.address}")
                print(f"  Netmask: {address.netmask}")
                print(f"  Broadcast IP: {address.broadcast}")
            elif str(address.family) == 'AddressFamily.AF_PACKET':
                print(f"  MAC Address: {address.address}")
                print(f"  Netmask: {address.netmask}")
                print(f"  Broadcast MAC: {address.broadcast}")
    ##get IO statistics since boot
    net_io = psutil.net_io_counters()
    print(f"Total Bytes Sent: {get_size(net_io.bytes_sent)}")
    print(f"Total Bytes Received: {get_size(net_io.bytes_recv)}")

