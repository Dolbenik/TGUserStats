import asyncio
import os
import json

from collections import Counter
from datetime import datetime

from data.config import folder_export
from data.tekst import top_day_tekst
from handlers.func import create_wait_for_reply
from loader.client import client
from telethon import events

async def top_day(data, filename):
    day_counts = Counter()

    for tijd_item in data:
        date_str = tijd_item.get("date")
        if date_str:
            dt = datetime.fromisoformat(date_str)
            day_counts[str(dt.date())] += 1

    top_days = day_counts.most_common(10)

    lines = [f"**{day}** — {count} messages" for day, count in top_days]
    joined_lines = "\n".join(lines)

    text = f'''
File: `{filename}`
**Top 10 most active days:**\n
{joined_lines}'''

    return text

@client.on(events.NewMessage(outgoing=True, pattern='/top-days'))
async def handler(event):
    msg = await client.edit_message(event.chat_id, event.message.id, top_day_tekst)
    await asyncio.sleep(10)
    await client.delete_messages(event.chat_id, msg.id)

@client.on(events.NewMessage(outgoing=True, pattern='/latest-days'))
async def handler(event):
    try:
        await event.edit("Searching for the latest file...")

        files = [
            os.path.join(folder_export, f)
            for f in os.listdir(folder_export)
            if f.endswith(".json")]

        files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

        if not files:
            await event.edit("No saved files found.")
            return

        filepath = files[0]
        filename = os.path.basename(filepath)

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        await event.edit(await top_day(data, filename))

    except Exception as e:
        await event.edit(f"Error: `{e}`")
        return

@client.on(events.NewMessage(outgoing=True, pattern='/upload-days'))
async def handler(event):
    try:
        msg = await event.edit("Upload the file in JSON format (for example: `chat_2025-05-22_13-45-00.json`)")
        future = asyncio.get_event_loop().create_future()

        wait_for_reply = create_wait_for_reply(event, msg, future)
        client.add_event_handler(wait_for_reply, events.NewMessage)

        try:
            filename_event = await asyncio.wait_for(future, timeout=60)
            filepath = f"temp_{filename_event.file.name}"
            await filename_event.download_media(filepath)
        except asyncio.TimeoutError:
            await event.edit("Timeout expired (60 seconds). Please try again.")
            return

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        await event.edit(await top_day(data, filename_event.file.name))

        await asyncio.sleep(1)
        os.remove(filepath)
        await client.delete_messages(event.chat_id, filename_event.id)
    except Exception as e:
        await event.edit(f"Error: `{e}`")
        await client.delete_messages(event.chat_id, filename_event.id)
        return

@client.on(events.NewMessage(outgoing=True, pattern='/search-days'))
async def handler(event):
    try:
        msg = await event.edit(
            "Upload the file in JSON format (for example: `chat_2025-05-22_13-45-00.json`)")

        future = asyncio.get_event_loop().create_future()
        wait_for_reply = create_wait_for_reply(event, msg, future)
        client.add_event_handler(wait_for_reply, events.NewMessage)

        try:
            filename_event = await asyncio.wait_for(future, timeout=30)
            filename = filename_event.text.strip()
            filepath = os.path.join(folder_export, filename)
        except asyncio.TimeoutError:
            await event.edit("Timeout expired (30 seconds). Please try again.")
            return

        if not os.path.exists(filepath):
            await event.edit(f"File `{filename}` not found in `{folder_export}`")
            await client.delete_messages(event.chat_id, filename_event.id)
            return

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        #await client.send_file(event.chat_id, filepath,caption=await top_day(data, filename))
        await event.edit(await top_day(data, filename))
        await asyncio.sleep(1)
        await client.delete_messages(event.chat_id, [filename_event.id]) #msg.id,
    except Exception as e:
        await event.edit(f"Error: `{e}`")
        await client.delete_messages(event.chat_id, filename_event.id)
        return
