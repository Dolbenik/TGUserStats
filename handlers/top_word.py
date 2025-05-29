import asyncio
import os
import json
import re

from collections import Counter

from data.config import folder_export, stop_words
from handlers.func import create_wait_for_reply
from loader.client import client
from data.tekst import top_word_tekst
from data.config import top_n
from telethon import events

async def top_words(data, filename, top_n=top_n):
    word_counts = Counter()

    for item in data:
        text = item.get("text")
        if not text:
            continue
        words = re.findall(r'\b\w{3,}\b', text.lower())
        filtered_words = [word for word in words if word not in stop_words]
        word_counts.update(filtered_words)

    top = word_counts.most_common(top_n)
    lines = [f"{i+1}. **{word}** — {count} times" for i, (word, count) in enumerate(top)]

    text = f'''File: `{filename}`\nTop-{top_n} popular words in the chat:\n'''+ "\n".join(lines)

    return text

@client.on(events.NewMessage(outgoing=True, pattern='/top-words'))
async def handler(event):
    msg = await client.edit_message(event.chat_id, event.message.id, top_word_tekst)
    await asyncio.sleep(10)
    await client.delete_messages(event.chat_id, msg.id)

@client.on(events.NewMessage(outgoing=True, pattern='/latest-words'))
async def handler(event):
    try:
        await event.edit('Searching for the latest file...')

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

        await event.edit(await top_words(data, filename, top_n=top_n))
    except Exception as e:
        await event.edit(f"Error: `{e}`")
        return

@client.on(events.NewMessage(outgoing=True, pattern='/upload-words'))
async def handler(event):
    try:
        msg = await event.edit("Upload the file in JSON format (for example: `chat_2025-05-22_13-45-00.json`)")

        future = asyncio.get_event_loop().create_future()

        wait_for_reply = create_wait_for_reply(event, msg, future)
        client.add_event_handler(wait_for_reply, events.NewMessage)

        try:
            filename_event = await asyncio.wait_for(future, timeout=30)
            filepath = f'temp_{filename_event.file.name}'
            await filename_event.download_media(filepath)
        except asyncio.TimeoutError:
            await event.edit("Timeout expired (60 seconds). Please try again.")
            return

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        await event.edit(await top_words(data, filename_event.file.name, top_n=top_n))

        await asyncio.sleep(1)
        os.remove(filepath)
        await client.delete_messages(event.chat_id, filename_event.id)
    except Exception as e:
        await event.edit(f"Error: `{e}`")
        await client.delete_messages(event.chat_id, filename_event.id)
        return

@client.on(events.NewMessage(outgoing=True, pattern='/search-words'))
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
            client.remove_event_handler(wait_for_reply, events.NewMessage)
            return

        if not os.path.exists(filepath):
            await event.edit(f"File `{filename}` not found in `{folder_export}`")
            await client.delete_messages(event.chat_id, filename_event.id)
            return

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # await client.send_file(event.chat_id, filepath, caption=await top_words(data, filename, top_n=top_n))
        await event.edit(await top_words(data, filename, top_n=top_n))
        await asyncio.sleep(1)
        await client.delete_messages(event.chat_id, [filename_event.id])  # msg.id,
    except Exception as e:
        await event.edit(f"Error: `{e}`")
        await client.delete_messages(event.chat_id, filename_event.id)
        return
