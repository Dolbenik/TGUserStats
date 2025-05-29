import asyncio
import os
import json

from collections import Counter

from data.config import folder_export
from data.tekst import top_sms_tekst
from handlers.func import create_wait_for_reply
from loader.client import client
from telethon import events

async def stat_sms(data, filename):
    user_counts = Counter()
    id_to_username = {}

    for msg in data:
        sender_id = msg.get("sender_id")
        sender_username = msg.get("sender_username")

        if sender_id is None:
            continue

        if sender_username:
            id_to_username[sender_id] = sender_username
        elif sender_id not in id_to_username:
            id_to_username[sender_id] = None

    for msg in data:
        sender_id = msg.get("sender_id")
        if sender_id is None:
            continue

        sender_username = id_to_username.get(sender_id)

        if sender_username:
            user = f'[{sender_username}](tg://user?id={sender_id})'
        else:
            user = f'[{sender_id}](tg://user?id={sender_id})'

        user_counts[user] += 1

    lines = []
    for user, count in user_counts.most_common():
        lines.append(f"{user}: {count} messages")

    joined_lines = "\n".join(lines)

    text = f'''
File: `{filename}`
Message statistics by users:
{joined_lines}'''

    return text

@client.on(events.NewMessage(outgoing=True, pattern='/top-users'))
async def send_buttons(event):
    msg = await client.edit_message(event.chat_id, event.message.id, top_sms_tekst)
    await asyncio.sleep(10)
    await client.delete_messages(event.chat_id, msg.id)

@client.on(events.NewMessage(outgoing=True, pattern='/latest-users'))
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

        await event.edit(await stat_sms(data, filename))

    except Exception as e:
        await event.edit(f"Error: `{e}`")
        return

@client.on(events.NewMessage(outgoing=True, pattern='/upload-users'))
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

        await event.edit(await stat_sms(data, filename_event.file.name))

        await asyncio.sleep(1)
        os.remove(filepath)
        await client.delete_messages(event.chat_id, filename_event.id)
    except Exception as e:
        await event.edit(f"Error: `{e}`")
        await client.delete_messages(event.chat_id, filename_event.id)
        return

@client.on(events.NewMessage(outgoing=True, pattern='/search-users'))
async def handler(event):
    try:
        msg = await event.edit("Upload the file in JSON format (for example: `chat_2025-05-22_13-45-00.json`)")

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

        #await client.send_file(event.chat_id, filepath,caption=await stat_sms(data, filename))
        await event.edit(await stat_sms(data, filename))
        await asyncio.sleep(1)
        await client.delete_messages(event.chat_id, [filename_event.id]) #msg.id,
    except Exception as e:
        await event.edit(f"Error: `{e}`")
        await client.delete_messages(event.chat_id, filename_event.id)
        return