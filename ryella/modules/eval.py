import asyncio
import io
import os
import sys
import time
import traceback
from platform import platform

from ..handlers import user_cmd


@user_cmd("eval", "Evaluate python code")
async def _eval(e):
    try:
        c = e.text.split(None, 1)[1]
    except IndexError:
        return await e.edit("No code provided")
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    start_time = time.time()
    try:
        value = await aexec(c, e)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = exc or stderr or stdout or value or "No output"
    if len(str(evaluation)) > 4040:
        with io.BytesIO(str(evaluation).encode()) as file:
            file.name = "eval.txt"
            await e.delete()
            return await e.respond(file=file)
    final_output = "__►__ **EVALxD**\n```{}``` \n\n __►__ **OUTPUT**: \n```{}``` \n**Execution Time:** `{}`s".format(
        c,
        evaluation,
        int(time.time() - start_time),
    )
    await e.edit(final_output)


async def aexec(code, event):
    exec(
        (
            "async def __aexec(e, client): "
            + "\n p = print"
            + "\n message = event = e"
            + "\n r = reply = await event.get_reply_message()"
            + "\n chat = event"
            + "\n from pprint import pprint"
            + "\n pp = pprint"
        )
        + "".join(f"\n {l}" for l in code.split("\n"))
    )
    return await locals()["__aexec"](event, event.client)


@user_cmd("(exec|bash|shell)", "Execute bash commands")
async def _exec(e):
    try:
        cmd = e.text.split(maxsplit=1)[1]
    except IndexError:
        return await e.edit("No cmd provided!")
    p = await e.edit("Executing...")
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    out = str(stdout.decode().strip()) + str(stderr.decode().strip())
    if len(out) > 4095:
        with io.BytesIO(out.encode()) as file:
            file.name = "exec.txt"
            await e.respond(file=file)
            await p.delete()
    else:
        if "windows" in platform().lower():
            ptf = "PowerShell"
        else:
            ptf = "Bash"
        caption = "**{}:**\n**Code:** `{}`\n**Output:**\n\n```{}```".format(
            ptf, cmd, out
        )
        await p.edit(caption)


@user_cmd("update", "git pull from origin repo")
async def _update(e):
    p = await e.edit("Fetching upstream...")
    os.system("git pull")
    await p.edit("Fast soft updating...")
    args = [sys.executable, "-m ryella"]
    os.execle(sys.executable, *args, os.environ)


@user_cmd("speedtest", "speedtest-cli")
async def _speedtest(e):
    msg = await e.edit("Testing internet speed...")
    st = speedtest.Speedtest()
    download = st.download()
    upload = st.upload()
    ping = st.results.ping
    server = st.results.server.get("name", "Unknown")
    isp = st.results.client.get("isp", "Unknown")
    ip = st.results.client.get("ip", "Unknown")
    country = st.results.client.get("country", "Unknown")
    result = (
        f"**Speedtest Results:**\n\n"
        f"**Download:** `{human_readable_size(download, True)}`\n"
        f"**Upload:** `{human_readable_size(upload, True)}`\n"
        f"**Ping:** `{ping} ms`\n"
        f"**Server:** `{server}`\n"
        f"**ISP:** `{isp}`\n"
        f"**IP:** `{ip}`\n"
        f"**Country:** `{country}`"
    )
    await msg.edit(result)
