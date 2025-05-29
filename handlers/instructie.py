import asyncio

from data.tekst import instructie_tekst
from loader.client import client
from telethon import events

@client.on(events.NewMessage(outgoing=True, pattern='/instruction'))
async def handler(event):
    msg = await client.edit_message(event.chat_id, event.message.id, instructie_tekst)
    await asyncio.sleep(35)
    await client.delete_messages(event.chat_id, msg.id)
