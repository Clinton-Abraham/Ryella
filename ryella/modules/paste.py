from requests import get, post
from ..handlers import user_cmd
from ..helpers import get_text_content, get_user


@user_cmd('paste', 'Paste to Hastebin or Nekobin (-n)')
async def paste(message):
    msg = await message.edit('Pasting...')
    url = 'https://hastebin.com/documents'
    content = await get_text_content(message)
    if not content:
        await message.edit('No content found!')
        return
    if '-n' in message.text:
        url = 'https://warm-anchorage-15807.herokuapp.com/api/documents'
        try:
            response = post(url, json={'content': content}, timeout=5)
        except Exception as e:
            await msg.edit(f'Error: {e}')
            return
        else:
            msg = "<b>Pasted to:</b> <a href='https://warm-anchorage-15807.herokuapp.com/{}'>NekoBind</a>".format(
                response.json()['key'])
            return await msg.edit(msg, parse_mode='html', link_preview=False)
    data = {'content': content}
    try:
        r = post(url, data=data, timeout=5)
    except TimeoutError:
        await message.edit('TimeoutError')
        return
    except Exception as e:
        await msg.edit(str(e))
        return
    url = 'https://hastebin.com/' + r.json()['key']
    caption = '<b>Pasted to:</b> <a href="{}">Haste Bin</a>'.format(url)
    await msg.edit(caption, parse_mode='html', link_preview=False)


@user_cmd('ip', 'Get Ip address details')
async def ip(message):
    await message.edit('Getting IP data...')
    ip_address = await get_text_content(message)
    if not ip_address:
        await message.edit('No IP address provided!')
        return
    url = 'https://ipinfo.io/{}/json?token=a25e6bc6a305c7'.format(ip_address)
    try:
        r = get(url, timeout=5)
    except TimeoutError:
        await message.edit('TimeoutError')
        return
    except Exception as e:
        await message.edit(str(e))
        return
    data = r.json()
    caption = '<b>IP:</b> <code>{}</code>\n<b>Country:</b> <code>{}</code>\n<b>Region:</b> <code>{}</code>\n<b>City:</b> <code>{}</code>\n<b>Org:</b> <code>{}</code>'.format(
        data['ip'], data['country'], data['region'], data['city'], data['org'])
    await message.edit(caption, parse_mode='html', link_preview=False)


@user_cmd('ud', 'Search the Urban Dictionary.')
async def ud(message):
    url = 'https://api.urbandictionary.com/v0/define'
    content = await get_text_content(message)
    if not content:
        await message.edit('No content found!')
        return
    params = {'term': content}
    try:
        r = get(url, params=params, timeout=5)
    except TimeoutError:
        await message.edit('TimeoutError')
        return
    except Exception as e:
        await message.edit(str(e))
        return
    data = r.json()
    if data['list']:
        definition = data['list'][0]['definition']
        example = data['list'][0]['example']
        caption = '<b>Word: <i>{}</i></b>\n<b>Definition:</b> <code>{}</code>\n<b>Example:</b> <code>{}</code>'.format(
            content, definition, example)
        await message.edit(caption, parse_mode='html', link_preview=False)
    else:
        await message.edit('No results found!')
        return


@user_cmd('bin', 'Get info about a bin')
async def bin(message):
    url = 'https://lookup.binlist.net/'
    content = await get_text_content(message)
    if not content:
        await message.edit('Please provide bin number!')
        return
    r = get(url + content, timeout=5)
    data = r.json()
    if data.get('bin'):
        bin_number = data['bin']
        bank = data['bank']
        country = data['country']
        _type = data['type']
        brand = data['brand']
        caption = '<b>Bin Number:</b> <code>{}</code>\n<b>Bank:</b> <code>{}</code>\n<b>Country:</b> <code>{}</code>\n<b>Type:</b> <code>{}</code>\n<b>Brand:</b> <code>{}</code>'.format(
            bin_number, bank, country, _type, brand)
        await message.edit(caption, parse_mode='html', link_preview=False)
    else:
        await message.edit('No results found!')
        return


@user_cmd('whois', 'Get info about a user.')
async def whois(message):
    user, _ = await get_user(message)
    if not user:
        await message.edit('No user found!')
        return
    user_caption = '<b>User Info</b>\n'
    user_caption += '<b>ID:</b> <code>{}</code>\n'.format(user.id)
    user_caption += '<b>Username:</b> @{}\n'.format(
        user.username) if user.username else ""
    user_caption += '<b>First Name:</b> {}\n'.format(
        user.first_name) if user.first_name else ""
    user_caption += '<b>Last Name:</b> {}\n'.format(
        user.last_name) if user.last_name else ""
    user_caption += '<b>DC ID:</b> <code>{}</code>\n'.format(
        user.photo.dc_id) if user.photo else ""
    user_caption += '<b>User Link:</b> <a href="tg://user?id={}">link</a>\n'.format(
        user.id)
    await message.edit(user_caption, parse_mode='html', link_preview=False)


@user_cmd('sk')
async def sk(message):
    charge_url = 'https://api.stripe.com/v1/charges'
    content = await get_text_content(message)
    if not content:
        await message.edit('provide sk key!')
        return
    r = get(charge_url, auth=(content, ''))
    resp = r.json()
    if "error" in resp:
        msg = '<b>Invalid SK</b>\n'
        msg += '<b>sk:</b> <code>{}</code>\n'
        msg += '<b>Response:</b> <code>{}</code>\n'
        msg += '<b>Error Type:</b> <code>{}</code>\n'
        return await message.edit(msg.format(content, resp['error']['message'], resp['error']['type']), parse_mode='html', link_preview=False)
    else:
        tokens_url = 'https://api.stripe.com/v1/tokens'
        r = post(tokens_url, auth=(content, ''), params={
                 'card[number]': '5262053008692130', 'card[exp_month]': '08', 'card[exp_year]': '23', 'card[cvc]': '123'})

        resp = r.json()
        if "error" in resp:
            msg = '<b>Rate Limited SK</b>\n'
            msg += '<b>sk:</b> <code>{}</code>\n'
            msg += '<b>Response:</b> <code>{}</code>\n'
            msg += '<b>Error Type:</b> <code>{}</code>\n'
            return await message.edit(msg.format(content, resp['error']['message'], resp['error']['type']), parse_mode='html', link_preview=False)
        payment_url = 'https://api.stripe.com/v1/payment_methods'
        r = post(payment_url, auth=(content, ''), params={'type': 'card', 'card[number]': '5262053008692130', 'card[exp_month]': '08', 'card[exp_year]': '23', 'card[cvc]': '123'}, headers={
            'Content-Type': 'application/x-www-form-urlencoded',
        })
        r = r.json()
        if "error" in r:
            msg = '<b>Dead SK</b>\n'
            msg += '<b>sk:</b> <code>{}</code>\n'
            msg += '<b>Response:</b> <code>{}</code>\n'
            msg += '<b>Error Type:</b> <code>{}</code>\n'
            return await message.edit(msg.format(content, r['error']['message'], r['error']['type']), parse_mode='html', link_preview=False)
        else:
            msg = '<b>Valid SK</b>\n'
            msg += '<b>sk:</b> <code>{}</code>\n'
            msg += '<b>Total Amount:</b> <code>{}</code>\n'
            total_amount = [int(x["amount"])
                            for x in resp['data']] if resp.get("data") else [0]
            total_amount = str(sum(total_amount)) + ' $'
            return await message.edit(msg.format(content, total_amount), parse_mode='html', link_preview=False)
