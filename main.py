import asyncio
import logging
import os
import time
from types import SimpleNamespace

import discord
import requests
from babel import numbers
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
FROM_CURRENCY = os.getenv('FROM_CURRENCY')
TO_CURRENCY = os.getenv('TO_CURRENCY')

intents = discord.Intents.default()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await poll_data()


async def poll_data():
    logging.info('Polling data...')
    while True:
        data = get_data()
        if data:
            rate = data.rates[TO_CURRENCY]
            if rate:
                from_amount = numbers.format_currency(round(1 / rate, 4), FROM_CURRENCY, locale='en_US')
                to_amount = numbers.format_currency(1.000, TO_CURRENCY, locale='en_US')
                logging.info(f'Retrieved {from_amount} = {to_amount}')
                await client.change_presence(activity=discord.Streaming(name=f'{to_amount} = {from_amount}', url=f'https://www.google.com/finance/quote/{TO_CURRENCY}-{FROM_CURRENCY}'))
        await asyncio.sleep(3600)


def get_data():
    logging.info('Getting data...')
    try:
        url = f'https://api.exchangerate-api.com/v4/latest/{FROM_CURRENCY}'
        response = requests.get(url)
        data = response.json()
        parsed = SimpleNamespace(**data)
    except Exception as e:
        logging.error(e)
        return None
    else:
        return parsed


client.run(TOKEN)
