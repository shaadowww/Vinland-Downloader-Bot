from typing import Optional

import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import os
import yt_downloader
from enum import Enum
import redis.asyncio as redis

from json import loads
from aiogram import Bot
from aiogram.types import FSInputFile
from dotenv import load_dotenv


# TODO
# put queue to redis?
# statuses of downloads
# semaphore?
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s [%(asctime)s] - %(message)s",
    datefmt="%H:%M:%S"
)
class FakeDownloader:
    class Format(Enum):
        VIDEO = 1
        AUDIO = 2
        
    def __init__(self, bot: Bot, redis_client: redis.Redis,workers: int = 3):
        self.redis = redis_client

        self.bot = bot
        self.workers: int = workers

    async def start_workers(self):
        tasks = []
        for worker_id in range(self.workers):
            tasks.append(asyncio.create_task(self.worker(worker_id)))

        await asyncio.gather(*tasks)
        

    async def download(self, url, quality: int, is_audio: bool):
        result = await asyncio.to_thread(yt_downloader.youtube_download, url, quality, is_audio)
        return result
    
    async def queue_get(self) -> str:
        """Получает задачу из Redis очереди"""
        # brpop атомарен, воркеры не будут воровать задачи друг у друга
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
                
                # ИСПРАВЛЕНО: используем функцию loads напрямую
                loaded = loads(raw_json)
                chat_id = loaded["chat_id"]
                url = loaded["url"]
                quality = loaded["quality"]
                media_format = loaded["format"]
                
                if chat_id is None: 
                    break

                logging.info(f"Worker {worker_id}: Downloading {url}")
                is_audio = False
                if media_format == 'audio':
                    is_audio = True
                    
                file_path = await self.download(url, quality, is_audio)
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
                # Глобальный try-catch защищает воркера от падения при плохой ссылке
                logging.error(f"Worker {worker_id}: Error occurred: {e}", exc_info=True)
                try:
                    if 'chat_id' in locals():
                        await self.bot.send_message(chat_id, "An error occurred during downloading.")
                except Exception:
                    pass
            # ИСПРАВЛЕНО: Убран self.queue.task_done(), так как очереди больше нет
    async def shutdown(self) -> None:
        """
        Graceful workers shutdown 
        """
        await self.queue.join()

        for _ in range(self.workers):
            await self.queue.put((None,None,None)) # Sentinel for each worker to terminate

async def main():
    logging.info("Initializing Vinland Downloader Backend...")
    load_dotenv()
    
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    if not BOT_TOKEN:
        logging.critical("BOT_TOKEN not found in environment variables!")
        return

    
    bot = Bot(token=BOT_TOKEN)

    redis_client = redis.Redis(
        host='redis', 
        port=6379, 
        decode_responses=True
    )

    downloader = FakeDownloader(bot, redis_client=redis_client, workers=3)
    
    try:
        await downloader.start_workers()
    finally:
        await redis_client.aclose()

if __name__ == "__main__": 
    logging.info("DOWNLOAD STARTED!!!")
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Backend downloder stopped.")