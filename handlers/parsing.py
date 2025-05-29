import asyncio
import os
import json
from telethon import events
from datetime import datetime
from telethon.errors import UsernameNotOccupiedError

from data.config import folder_export, SAVE_EVERY
from data.tekst import parsing_tekst
from handlers.func import create_wait_for_reply, extract_username, find_entity_by_name
from loader.client import client

os.makedirs(folder_export, exist_ok=True)

async def parse_chat_to_file(chat_identifier, existing_file=None):
    chat = await client.get_entity(chat_identifier)

    if hasattr(chat, 'username') and chat.username:
        safe_name = chat.username
    elif hasattr(chat, 'title') and chat.title:
        safe_name = chat.title
    else:
        safe_name = str(chat.id)
    safe_name = safe_name.replace(' ', '_').replace('/', '_')

    all_messages = []
    seen_ids = set()
    last_saved_id = 0

    if existing_file and os.path.exists(existing_file):
        with open(existing_file, 'r', encoding='utf-8') as f:
            all_messages = json.load(f)
            seen_ids = {msg['id'] for msg in all_messages}
            if seen_ids:
                last_saved_id = max(seen_ids)
        filename = existing_file
    else:
        now_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(folder_export, f"{safe_name}_{now_str}.json")

    sender_cache = {}
    total = 0

    async for message in client.iter_messages(chat_identifier, min_id=last_saved_id):
        if message.id in seen_ids:
            continue

        msg_data = {
            'id': message.id,
            # 'reply_id': getattr(message, 'reply_to_msg_id', None),

            'sender_id': getattr(message, 'sender_id', None),
            'sender_username': None,

            'date': message.date.isoformat(),
            # 'edit_date': message.edit_date.isoformat() if message.edit_date else None,
            # 'silent': getattr(message, 'silent', False)

            'reactions': str(message.reactions) if hasattr(message, 'reactions') else None,
            'text': getattr(message, 'message', None),
            'media': str(type(message.media)) if message.media else None,
            # 'action': str(message.action) if message.action else None,

        }
        # 'is_forward': message.fwd_from is not None,  # was the message forwarded
        # 'is_reply': message.is_reply,  # is it a reply message
        # 'entities': [str(e) for e in message.entities] if message.entities else [], formatting, mentions, etc.

        if message.sender_id:
            if message.sender_id in sender_cache:
                msg_data['sender_username'] = sender_cache[message.sender_id]
            else:
                try:
                    sender = await client.get_entity(message.sender_id)
                    username = getattr(sender, 'username', None)
                    msg_data['sender_username'] = username
                    sender_cache[message.sender_id] = username
                except:
                    msg_data['sender_username'] = None
                    sender_cache[message.sender_id] = None

        all_messages.insert(0, msg_data)
        total += 1

        if total % SAVE_EVERY == 0:
            all_messages.sort(key=lambda x: x['id'], reverse=True)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(all_messages, f, ensure_ascii=False, indent=4)

    all_messages.sort(key=lambda x: x['id'], reverse=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_messages, f, ensure_ascii=False, indent=4)

    return filename, len(all_messages)

@client.on(events.NewMessage(outgoing=True, pattern='/parsing'))
async def handler(event):
    msg = await event.edit(parsing_tekst)
    await asyncio.sleep(15)
    await client.delete_messages(event.chat_id, msg.id)

@client.on(events.NewMessage(outgoing=True, pattern='/inchat'))
async def handler_parse(event):
    msg = await event.edit("Starting parsing...")
    try:
        filename, count = await parse_chat_to_file(event.chat_id)
        #await client.send_file(event.chat_id, filename, caption=f"Done! Total messages: {count}", silent=True)
        await event.edit(f"Done! Total messages: {count}",)
    except Exception as e:
        await event.edit(f"Error: `{e}`")
        return
    #await msg.delete()

@client.on(events.NewMessage(outgoing=True, pattern='/byusername'))
async def handler(event):
    msg = await event.edit('Enter the users nickname, link, or name\n(for example: username, @username, https://t.me/username, or the users full name)')
    future = asyncio.get_event_loop().create_future()
    wait_for_reply = create_wait_for_reply(event, msg, future)
    client.add_event_handler(wait_for_reply, events.NewMessage)
    try:
        try:
            name_event = await asyncio.wait_for(future, timeout=30)
            raw_input = name_event.text.strip()
            username = extract_username(raw_input)

            if username == raw_input:
                entity = await find_entity_by_name(client, raw_input)
                if not entity:
                    await event.edit(f"User with the name '{raw_input}' not found in your chats.")
                    await client.delete_messages(event.chat_id, name_event.id)
                    return
            else:
                try:
                    entity = await client.get_entity(username)
                except (ValueError, UsernameNotOccupiedError):
                    await event.edit(f"`{username}` not found. Try a different username.")
                    await client.delete_messages(event.chat_id, name_event.id)
                    return

        except asyncio.TimeoutError:
            await event.edit("Timeout expired (30 seconds). Please try again.")
            client.remove_event_handler(wait_for_reply, events.NewMessage)
            return

        client.remove_event_handler(wait_for_reply, events.NewMessage)

        await event.edit("Starting parsing...")

        filename, count = await parse_chat_to_file(entity)
        # await client.send_file(event.chat_id, filename, caption=f"Done! Total messages: {count}", silent=True)
        await event.edit(f"Done! Total messages: {count}")
        await asyncio.sleep(1)
        await client.delete_messages(event.chat_id, [name_event.id])  # msg.id,
    except Exception as e:
        await event.edit(f"Error: `{e}`")
        await client.delete_messages(event.chat_id, name_event.id)
        return

@client.on(events.NewMessage(outgoing=True, pattern='/continue-inchat'))
async def handler_continue(event):
    msg = await event.edit('Upload the file in JSON format (for example: `chat_2025-05-22_13-45-00.json`)')
    future = asyncio.get_event_loop().create_future()
    wait_for_reply = create_wait_for_reply(event, msg, future)
    client.add_event_handler(wait_for_reply, events.NewMessage)

    try:
        try:
            file_event = await asyncio.wait_for(future, timeout=30)
            filename = file_event.text.strip()
            full_path = os.path.join(folder_export, filename)
        except asyncio.TimeoutError:
            await event.edit("Timeout expired (30 seconds). Please try again.")
            client.remove_event_handler(wait_for_reply, events.NewMessage)
            return

        if not os.path.exists(full_path):
            await event.edit(f"File `{filename}` not found in `{folder_export}`.")
            await client.delete_messages(event.chat_id, file_event.id)
            return

        await event.edit("Continuing parsing...")
        entity = await client.get_entity(event.chat_id)
        result_path, count = await parse_chat_to_file(entity, existing_file=full_path)

        # await client.send_file(event.chat_id, filename, caption=f"Done! Total messages: {count}", silent=True)
        await event.edit(f'Supplement completed. Total messages: {count}')
        await asyncio.sleep(1)
        await client.delete_messages(event.chat_id, [file_event.id]) #msg.id,

    except Exception as e:
        await event.edit(f"Error: `{e}`")
        await client.delete_messages(event.chat_id, file_event.id)
        return

@client.on(events.NewMessage(outgoing=True, pattern='/continue-byusername'))
async def handler_continue(event):
    try:
        # ======================== #
        msg1 = await event.edit('Upload the file in JSON format (for example: `chat_2025-05-22_13-45-00.json`)')
        future1 = asyncio.get_event_loop().create_future()
        handler1 = create_wait_for_reply(event, msg1, future1)
        client.add_event_handler(handler1, events.NewMessage)

        try:
            name_event = await asyncio.wait_for(future1, timeout=30)
            filename = name_event.text.strip()
            full_path = os.path.join(folder_export, filename)
        except asyncio.TimeoutError:
            await event.edit("Timeout expired (30 seconds). Please try again.")
            client.remove_event_handler(handler1, events.NewMessage)
            return
        await client.delete_messages(event.chat_id, name_event.id)
        client.remove_event_handler(handler1, events.NewMessage)

        # ======================== #
        msg2 = await event.edit('Enter the users nickname, link, or name\n(for example: username, @username, https://t.me/username, or the users full name)')
        future2 = asyncio.get_event_loop().create_future()
        handler2 = create_wait_for_reply(event, msg2, future2)
        client.add_event_handler(handler2, events.NewMessage)

        try:
            username_event = await asyncio.wait_for(future2, timeout=30)
            raw_input = username_event.text.strip()
            username = extract_username(raw_input)

            if username == raw_input:
                entity = await find_entity_by_name(client, raw_input)
                if not entity:
                    await event.edit(f"User with the name '{raw_input}' not found in your chats.")
                    await client.delete_messages(event.chat_id, username_event.id)
                    return
            else:
                try:
                    entity = await client.get_entity(username)
                except (ValueError, UsernameNotOccupiedError):
                    await event.edit(f"`{username}` not found. Try a different username.")
                    await client.delete_messages(event.chat_id, username_event.id)
                    return

        except asyncio.TimeoutError:
            await event.edit("Timeout expired (30 seconds). Please try again.")
            client.remove_event_handler(handler2, events.NewMessage)
            return
        client.remove_event_handler(handler2, events.NewMessage)

        # ======================== #
        if not os.path.exists(full_path):
            await event.edit(f"File `{filename}` not found in `{folder_export}`")
            return

        await event.edit("Continuing parsing...")
        result_path, count = await parse_chat_to_file(entity, existing_file=full_path)
        # await client.send_file(event.chat_id, filename, caption=f"Done! Total messages: {count}", silent=True)
        await event.edit(f'Addition completed. Total messages: {count}')
        await asyncio.sleep(1)
        await client.delete_messages(event.chat_id, [username_event.id]) #msg.id,

    except Exception as e:
        await event.edit(f"Error: `{e}`")
        await client.delete_messages(event.chat_id, [name_event,username_event.id])


