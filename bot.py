from difflib import get_close_matches
import asyncio
from datetime import datetime, timedelta
from time import time, sleep
from os.path import isfile as fexists

import discord
from discord.ext import commands
import aiohttp
from bs4 import BeautifulSoup as soup

token = open('data/TOKEN.txt', 'r').readline().strip()
channel = int(open('data/CHANNEL_ID.txt', 'r').readline().strip()) # Στο discord.py v1+ πρέπει όλα τα ids να είναι int και όχι str
url = "http://www.ice.uniwa.gr/announcements-all/"
wres = 18000 # 5 hours to secs

grafeiaKathigitwn = {
    'βασιλας'       : 'Κ16.115',
    'γαλιωτου'      : 'Κ16.122',
    'γεωργουλη'     : 'Κ16.216',
    'γιαννακοπουλος': 'Στο διαδρομο του εργαστηριου SUN',
    'διλιντας'      : 'Κ16.203',
    'ελληνας'       : 'Κ16.203',
    'καρανικολας'   : 'Κ16.120',
    'κεχαγιας'      : 'Κ16.116',
    'κουκουλετσος'  : 'Κ16.204',
    'μαγος'         : 'Κ16.119',
    'μαμαλης'       : 'Κ16.120-121',
    'μαστοροκωστας' : 'Κ16.204',
    'μιαουλης'      : 'Κ16.118',
    'νικολοπουλος'  : 'Στο διαδρομο του εργαστηριου SUN',
    'παντζιου'      : 'Κ16.115',
    'πρεζερακος'    : 'Κ16.203',
    'σαμαρακου'     : 'Κ16.208',
    'σγουροπουλου'  : 'Κ16.123',
    'σκουρλας'      : 'Κ16.120-121',
    'χαλαρης'       : 'Κ16.120-121',
    'μπογρης'       : 'Κ16.999',
    'φατουρος'      : 'Κ16.204',
    'βουλοδημος'    : 'Κ16.118',
    'καντζαβελου'   : 'Κ16.122',
    'καρκαζης'      : 'Κ16.203',
    'κουμπουρος'    : 'Κ16.122',
    'ξυδας'         : 'Κ16.120-121',
    'μπαρδης'       : 'Κ16.199',
    'βελωνη'        : 'Κ16.204',
    'γεωργουλακη'   : 'Κ16.999',
    'μελετιου'      : 'K10.018',
    'γιαλπας'       : 'Κ16.121',
    'παυλιδης'      : 'Κ16.ΚΔΕ',
}

client = commands.Bot(command_prefix=";")
client.remove_command('help')

async def create_aiohttp_session():
    client.aiohttp_session = aiohttp.ClientSession(loop=client.loop)

def get_digits_from_link(link):
    digits = ""
    for l in link[::-1]:
        if l.isdigit():
            digits += l
        else:
            break
    digits = digits[::-1]
    return digits

def update_digits(digits: str, old_digits: list):
    # Rotate the list
    old_digits.append(old_digits.pop(0))
    # Replace last digit with new
    old_digits[-1] = digits
    with open('data/last_digits.txt', 'w') as f:
        f.write("\n".join(old_digits))

async def getNotifications():
    with open('data/last_digits.txt', 'r', encoding="utf-8") as f:
        last_digits = [f.readline().strip() for _ in range(5)]

    async with client.aiohttp_session.get(url) as r:
        if r.status != 200:
            return []
        page_html = await r.text()

    page_soup = soup(page_html, "html.parser")
    announcements = page_soup.find_all(class_="single_post_row")

    to_send = []
    latest_digits = get_digits_from_link(announcements[0]['data-url'])

    for announcement in announcements:
        title = announcement.find(class_="single_post_title").contents[0].strip()
        link = announcement['data-url']

        digits = get_digits_from_link(link)

        if digits not in last_digits:
            to_send.append([title, link])
        else:
            break

    if latest_digits not in last_digits:
        update_digits(latest_digits, last_digits)

    return to_send


async def findProgramma(programma):
    async with client.aiohttp_session.get(url) as r:
        if r.status != 200:
            return None, None
        page_html = await r.text()

    page_soup = soup(page_html, "html.parser")
    anakoinwseis = page_soup.find_all('div', {'class': 'col-lg-12 col-md-12 col-sm-12 col-xs-12 single_post_row'})
    for anakoinwsi in anakoinwseis:
        title = anakoinwsi.find('div', {'class': 'single_post_title'}).contents[0].strip()
        anakoinwsi = str(anakoinwsi)
        link = anakoinwsi[anakoinwsi.find('http'):anakoinwsi.find('">')].replace('amp;', '')
        if programma in title.lower():
            return title, link
    return None, None


@client.event
async def on_ready():
    print("Bot is online")


@client.command(aliases=['πρόγραμμα', 'προγραμμα', 'programma'])
async def program(ctx: commands.Context, arg):
    arg = arg.lower()
    if arg in ['μαθηματων', 'μαθημάτων', 'mathimatwn']:
        title, link = await findProgramma('ωρολόγιο πρόγραμμα')
    elif arg in ['εξεταστικης', 'εξεταστικής', 'eksetastikis']:
        title, link = await findProgramma('πρόγραμμα εξεταστικής')

    if title:
        embed = discord.Embed()
        embed.add_field(name=title, value=link, inline=False)
        await ctx.author.send(embed=embed)
    else:
        await ctx.author.send('Site is down')


@client.command(aliases=['γραφείο', 'γραφειο', 'grafeio'])
async def office(ctx: commands.Context, name):
    matches = get_close_matches(name, grafeiaKathigitwn)
    if matches:
        await ctx.author.send(matches[0] + ': ' + grafeiaKathigitwn[matches[0]])
    else:
        await ctx.author.send('Δεν ξερω που ειναι το γραφειο του ' + name)


@client.command()
async def help(ctx: commands.Context):
    msg = '''***command list***
        ;προγραμμα μαθηματων
        ;προγραμμα εξεταστικης
        ;γραφειο ονομα_καθηγητη'''
    await ctx.author.send(msg)


@client.event
async def on_command_error(ctx: commands.Context, error, pass_context=True):
    if isinstance(error, commands.CommandNotFound):
        await help.invoke(ctx)


async def post():
    await client.wait_until_ready()
    await create_aiohttp_session()
    while not client.is_closed():
        startTime = datetime.now()
        announcements = await getNotifications()

        if len(announcements) > 0:
            chn = client.get_channel(channel)
            await chn.send(f"{len(announcements)} νέ{'ες ' if len(announcements) > 1 else 'α '}" +
                f"{'ανακοινώσεις' if len(announcements) > 1 else 'ανακοίνωση'} @everyone")

        for announcement in announcements:
            embed = discord.Embed()
            embed.add_field(name=announcement[0], value=announcement[1], inline=False)

            await chn.send(embed=embed)

        await asyncio.sleep(wres + (startTime - datetime.now()).total_seconds())


client.loop.create_task(post())
client.run(token)
