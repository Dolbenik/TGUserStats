import asyncio
import handlers
from loader.logging import logger
from handlers.start import start
from loader.client import client

async def main_load():
    await client.start()
    await logger()
    await start()
    print("The client is running and waiting for events.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main_load())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped by user.")
