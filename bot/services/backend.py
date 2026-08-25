import asyncio
import logging
import yt_downloader
from enum import Enum
import redis.asyncio as redis

from json import loads, dumps
from aiogram import Bot
from aiogram.types import FSInputFile
from dotenv import load_dotenv


# TODO
# statuses of downloads
# semaphore?
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s [%(asctime)s] - %(message)s",
    datefmt="%H:%M:%S"
)

### REDIS CONFIG
redis_client = redis.Redis(
    host='redis', 
    port=6379, 
    decode_responses=True
)

# BOT CONFIG
if not settings.BOT_TOKEN:
    logging.critical("BOT_TOKEN not found in environment variables!")
    raise ValueError("Bot token not found in /.env or /config.py")

class FakeDownloader:
        
    def __init__(self, bot: Bot, redis_client: redis.Redis,workers: int = 3):
        self.redis = redis_client

        self.bot = bot
        self.workers: int = workers
        self.tasks = []
        self.active_downloads = {}

    async def start_workers(self):
        tasks = []
        for worker_id in range(self.workers):
            task = asyncio.create_task(self.worker(worker_id))
            self.tasks.append(task)

        await asyncio.gather(*self.tasks)
        

    async def download(self, url, quality: int, is_audio: bool, chat_id: int):
        file_path = await asyncio.to_thread(yt_downloader.youtube_download, url, quality, is_audio)
        return file_path
    
    async def queue_get(self) -> str:
        """Get task from Redis queue"""
        # brpop is atonomous, workers do not steal task from each other
        result = await self.redis.brpop("download_queue")
        return result[1] if result else None

    async def worker(self, worker_id: int) -> None:
        """
        Async consumer, receives url from queue and downloads media
        """
        logging.info(f"Worker {worker_id} ready and listening...")
        while True:
            try:
                raw_json = await self.queue_get() 
                if not raw_json:
                    continue
                
                # parse json with details from Redis Queue
                loaded = loads(raw_json)

                chat_id = loaded["chat_id"]
                url = loaded["url"]
                quality = loaded["quality"]
                media_format = loaded["format"]

                logging.info(f"Worker {worker_id}: Downloading {url}")
                is_audio = False
                if media_format == 'audio':
                    is_audio = True

                file_path = await self.download(url, quality, is_audio, chat_id)
                logging.info(f"Worker {worker_id}: Downloaded! path - {file_path}")

                if file_path and os.path.exists(file_path):
                    media = FSInputFile(file_path)

                    if is_audio:
                        await self.bot.send_audio(chat_id, media, caption="Here is your audio!")
                    else:
                        await self.bot.send_video(chat_id, media, caption="Here is your video!")
                    os.remove(file_path)
                else:
                    await self.bot.send_message(chat_id, "I can't download this video.\nSorry :(")
            
            except Exception as e:
                # try catch to secure worker from bad url's
                logging.error(f"Worker {worker_id}: Error occurred: {e}", exc_info=True)
                try:
                    if 'chat_id' in locals():
                        await self.bot.send_message(chat_id, "An error occurred during downloading.")
                except Exception:
                    pass


    async def cancel_downloads(self, chat_id: int):
        task = self.active_downloads.get(chat_id).terminate()
        if task:
            task.cancel()
            logging.info(f"task in {chat_id} canceled")

    async def shutdown(self) -> None:
        """
        Graceful workers shutdown 
        """
        for task in self.tasks:
            task.cancel()

        await asyncio.gather(
            *self.tasks,
            return_exceptions=True
        )

async def main():
    logging.info("Initializing Vinland Downloader Backend...")
    load_dotenv()

    bot = Bot(token=BOT_TOKEN)

    downloader = FakeDownloader(bot, redis_client=redis_client, workers=3)
    
    try:
        await downloader.start_workers()
    except asyncio.CancelledError:
        logging.info("Main cancelled")
    finally:
        logging.info("Shutting down downloader...")
        await downloader.shutdown()
        await redis_client.aclose()

if __name__ == "__main__": 
    logging.info("DOWNLOAD STARTED!!!")
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Backend downloder stopped.")