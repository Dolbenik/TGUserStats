import re
from loader.client import client
from telethon import events

def create_wait_for_reply(event, msg, future):
    async def wait_for_reply(ev):
        if (ev.sender_id == event.sender_id and
                ev.chat_id == event.chat_id and
                ev.is_reply and
                ev.reply_to_msg_id == msg.id):
            future.set_result(ev)
            client.remove_event_handler(wait_for_reply, events.NewMessage)
    return wait_for_reply

def extract_username(input_text: str) -> str:
    input_text = input_text.strip()
    match = re.search(r'(?:https?://)?t\.me/(@?\w+)', input_text, re.IGNORECASE)
    if match:
        username = match.group(1)
    else:
        username = input_text
    if username.startswith('@'):
        username = username[1:]

    return username

async def find_entity_by_name(client, name_substring):
    dialogs = await client.get_dialogs()
    name_substring = name_substring.lower()

    for dialog in dialogs:
        entity = dialog.entity
        found_name = None

        if hasattr(entity, 'title') and entity.title:
            found_name = entity.title
        elif hasattr(entity, 'first_name') and entity.first_name:
            found_name = entity.first_name
            if hasattr(entity, 'last_name') and entity.last_name:
                found_name += ' ' + entity.last_name

        if found_name:
            #print(f"check: {found_name}")  # debugging
            if name_substring in found_name.lower():
                return entity

    return None

