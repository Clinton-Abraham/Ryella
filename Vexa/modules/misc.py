from requests import get

from ..handlers import user_cmd
from ..helpers import get_text_content


@user_cmd(pattern="math")
async def math(message):
    exp = await get_text_content(message)
    if exp is None:
        return await message.reply("No expression provided!")
    url = "https://evaluate-expression.p.rapidapi.com"
    headers = {
        "x-rapidapi-host": "evaluate-expression.p.rapidapi.com",
        "x-rapidapi-key": "cf9e67ea99mshecc7e1ddb8e93d1p1b9e04jsn3f1bb9103c3f",
    }
    params = {"expression": exp}
    response = get(url, headers=headers, params=params)
    if response.status_code != 200:
        return await message.reply("Error: {}".format(response.status_code))
    result = response.text
    result = "ERR73" if result == "" else result
    await message.edit("**► MathExp**\n`{}`\n\n**► RESULT**\n`{}`".format(exp, result))
