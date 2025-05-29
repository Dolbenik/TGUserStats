from data.tekst import top_media_tekst
from handlers.func import create_wait_for_reply

import asyncio
import os
import json

from collections import Counter

from data.config import folder_export
from loader.client import client
from telethon import events

import matplotlib.pyplot as plt
import numpy as np

def generate_media_diogram(user_counts, folder_export, filename='media_chart.png'):
    labels = list(user_counts.keys())
    values = np.array(list(user_counts.values()))

    sorted_indices = np.argsort(values)
    labels = [labels[i] for i in sorted_indices]
    values = values[sorted_indices]

    plt.figure(figsize=(8, 5))
    y_pos = np.arange(len(labels))

    plt.hlines(y=y_pos, xmin=0, xmax=values, color='skyblue')
    plt.plot(values, y_pos, "o", color='steelblue')

    plt.yticks(y_pos, labels)
    plt.xlabel("Number of messages")
    plt.title("Distribution of media types")
    plt.grid(axis='x', linestyle='--', alpha=0.6)
    plt.tight_layout()

    chart_path = os.path.join(folder_export, filename)
    plt.savefig(chart_path)
    plt.close()

    return chart_path

def stat_media(data, filename):
    user_counts = Counter()
    for data_item in data:
        media = data_item.get('media')
        if media and isinstance(media, str) and "telethon.tl.types" in media:
            media_name = media.split('.')[-1][:-2]
            user_counts[media_name] += 1
        elif media:
            user_counts[media] += 1

    lines = [f"{media_type}: {count} messages" for media_type, count in user_counts.most_common()]
    joined_lines = "\n".join(lines)

    chart_path = generate_media_diogram(user_counts, folder_export) if user_counts else None

    text = f'''
File: `{filename}`  
Total media:
{joined_lines}'''

    return text, chart_path

@client.on(events.NewMessage(outgoing=True, pattern='/top-media'))
async def handler(event):
    msg = await client.edit_message(event.chat_id, event.message.id, top_media_tekst)
    await asyncio.sleep(10)
    await client.delete_messages(event.chat_id, msg.id)

@client.on(events.NewMessage(outgoing=True, pattern='/latest-media'))
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

        text, chart_path = stat_media(data, filename)

        if chart_path:
            await event.client.send_file(event.chat_id, chart_path, caption=text)
            await event.delete()
        else:
            await event.edit(text)
    except Exception as e:
        await event.edit(f"Error: `{e}`")

@client.on(events.NewMessage(outgoing=True, pattern='/upload-media'))
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

        #await event.edit(stat_media(data, filename_event.file.name))
        text, chart_path = stat_media(data, filename_event.file.name)

        if chart_path:
            await event.client.send_file(event.chat_id, chart_path, caption=text)
            await event.delete()
        else:
            await event.edit(text)

        await asyncio.sleep(1)
        os.remove(filepath)
        await client.delete_messages(event.chat_id, filename_event.id)
    except Exception as e:
        await event.edit(f"Error: `{e}`")
        await client.delete_messages(event.chat_id, filename_event.id)
        return

@client.on(events.NewMessage(outgoing=True, pattern='/search-media'))
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

        #await client.send_file(event.chat_id, filepath,caption=await stat_media(data, filename))
        #await event.edit(stat_media(data, filename))
        text, chart_path = stat_media(data, filename)

        if chart_path:
            await event.client.send_file(event.chat_id, chart_path, caption=text)
            await event.delete()
        else:
            await event.edit(text)

        await asyncio.sleep(1)
        await client.delete_messages(event.chat_id, [filename_event.id]) #msg.id,
    except Exception as e:
        await event.edit(f"Error: `{e}`")
        await client.delete_messages(event.chat_id, filename_event.id)
        return