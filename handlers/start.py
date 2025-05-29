import asyncio
import random

from data.tekst import start_tekst
from loader.client import client
from telethon import events

async def start():
    print('Hello! Go to any chat in Telegram and type /starting')
    msg = await client.send_message('me', 'Script is running! Type `/starting`')
    await asyncio.sleep(100)
    await msg.delete()

@client.on(events.NewMessage(outgoing=True, pattern='/starting'))
async def handler(event):
    msg = await client.edit_message(event.chat_id, event.message.id, start_tekst)
    await asyncio.sleep(20)
    await client.delete_messages(event.chat_id, msg.id)