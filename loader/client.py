from telethon import TelegramClient
from data.config import session, api_id, api_hash, proxy

client = TelegramClient(session, api_id, api_hash, proxy=proxy)