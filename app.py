import asyncio
import handlers
from loader.logging import logger
from handlers.start import start
from loader.client import client

async def main_load():
    await client.start()
    await start()
    print("The client is running and waiting for events.")
    await client.run_until_disconnected()

def main():
    logger()
    asyncio.run(main_load())

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped by user.")
