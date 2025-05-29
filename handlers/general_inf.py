import asyncio
import os
import json
from collections import Counter

from data.config import folder_export
from data.tekst import general_info_tekst
from loader.client import client
from telethon import events
from handlers.func import create_wait_for_reply

from datetime import datetime

'''
File: `{filename}`
Total number of messages: **{len(data)} (overall count)**
Total media files: **{media_count}**
Most active day: **{most_common_day}** (messages: {most_common_count})
Number of users: **{sender_id_count}**

#5. First message (text + time)
#6. Last messages (text + time)
'''

async def general_info (data, filename):
    media_count = 0
    sender_id = set()
    day_counts = Counter()

    for media_item in data:
        if media_item.get("media"):
            media_count += 1

    for user_item in data:
        sender_id_get = user_item.get("sender_id")
        if sender_id_get:
            sender_id.add(sender_id_get)
    sender_id_count = len(sender_id)

    for tijd_item in data:
        date_str = tijd_item.get("date")
        if date_str:
            dt = datetime.fromisoformat(date_str)
            day_counts[str(dt.date())] += 1
    most_common_day, most_common_count = day_counts.most_common(1)[0]

    text = f'''
File: `{filename}`
Total number of messages: **{len(data)} (overall count)**
Total media files: **{media_count}**
Most active day: **{most_common_day}** (messages: {most_common_count})
Number of users: **{sender_id_count}**'''
    return text

@client.on(events.NewMessage(outgoing=True, pattern='/general-info'))
async def send_buttons(event):
    msg = await client.edit_message(event.chat_id, event.message.id, general_info_tekst)
    await asyncio.sleep(10)
    await client.delete_messages(event.chat_id, msg.id)

@client.on(events.NewMessage(outgoing=True, pattern='/latest-general'))
async def handler(event):
    try:
        await event.edit('Looking for the latest file...')

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

        await event.edit(await general_info(data, filename))
    except Exception as e:
        await event.edit(f"Error: `{e}`")
        return

@client.on(events.NewMessage(outgoing=True, pattern='/upload-general'))
async def handler(event):
    try:
        msg = await event.edit("Upload the file in json format: (for example: `chat_2025-05-22_13-45-00.json`)")

        future = asyncio.get_event_loop().create_future()

        wait_for_reply = create_wait_for_reply(event, msg, future)
        client.add_event_handler(wait_for_reply, events.NewMessage)

        try:
            filename_event = await asyncio.wait_for(future, timeout=60)
            filepath = f'temp_{filename_event.file.name}'
            await filename_event.download_media(filepath)
        except asyncio.TimeoutError:
            await event.edit("Timeout expired (60 seconds). Please try again.")
            return

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        await event.edit(await general_info(data, filename_event.file.name))

        await asyncio.sleep(1)
        os.remove(filepath)
        await client.delete_messages(event.chat_id, filename_event.id)
    except Exception as e:
        await event.edit(f"Error: `{e}`")
        await client.delete_messages(event.chat_id, filename_event.id)
        return

@client.on(events.NewMessage(outgoing=True, pattern='/search-general'))
async def handler(event):
    try:
        msg = await event.edit("Which file to upload? Type the name (for example: `chat_2025-05-22_13-45-00.json`)")

        future = asyncio.get_event_loop().create_future()

        wait_for_reply = create_wait_for_reply(event, msg, future)
        client.add_event_handler(wait_for_reply, events.NewMessage)

        try:
            filename_event = await asyncio.wait_for(future, timeout=30)
            filename = filename_event.text.strip()
            filepath = os.path.join(folder_export, filename)
        except asyncio.TimeoutError:
            await event.edit("Timeout expired (30 seconds). Please try again.")
            client.remove_event_handler(wait_for_reply, events.NewMessage)
            return

        if not os.path.exists(filepath):
            await event.edit(f"File `{filename}` not found.")
            await client.delete_messages(event.chat_id, filename_event.id)
            return

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # await client.send_file(event.chat_id, filepath,caption=await general_info(data, filename))
        await event.edit(await general_info(data, filename))
        await asyncio.sleep(1)
        await client.delete_messages(event.chat_id, [filename_event.id])  # msg.id,
    except Exception as e:
        await event.edit(f"Error: `{e}`")
        await client.delete_messages(event.chat_id, filename_event.id)
        return
