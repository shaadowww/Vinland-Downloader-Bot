from typing import Optional

import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import os
from enum import Enum

from aiogram import Bot
from aiogram.types import FSInputFile

import bot.services.yt_downloader as yt_downloader

# TODO
# put queue to redis?
# statuses of downloads
# semaphore?

class FakeDownloader:
    class Format(Enum):
        VIDEO = 1
        AUDIO = 2

    def __init__(self, bot: Bot, workers = 3, queue_size: int = 10):
        self.queue = asyncio.Queue(maxsize=queue_size)

        self.bot = bot
        self.workers: int = workers

    async def start_workers(self):
        # create workers(consumers)
        for worker_id in range(self.workers):
            asyncio.create_task(self.worker(worker_id))

    async def download(self, url, is_audio: bool):
        result = await asyncio.to_thread(yt_downloader.youtube_download, url, is_audio)
        return result

    async def fake_download(self, url: str) -> str:
        """
        Simulation of media downloading
        """
        print(f'Downloading {url}')
        await asyncio.sleep(1)

        result = f'{url}.mp4'

        print(f'Downloaded {url}')

        return result
    
    async def add_url(self, url, chat_id: int, format: Format) -> None:
        await self.queue.put((chat_id, url, format))

    async def worker(self, worker_id: int) -> None:
        """
        Async consumer, recives url from queue and downloads media
        """
        while True:
            chat_id, url, format = await self.queue.get()  
            if chat_id is None: break

            try:
                logging.info(f"Downloading {url}")
                is_audio = False
                if format == self.Format.AUDIO:
                    is_audio = True
                file_path = await self.download(url, is_audio)
                logging.debug(f"Downloaded! path - {file_path}")

                if os.path.exists(file_path):
                    media = FSInputFile(file_path)

                    if is_audio:
                        await self.bot.send_audio(chat_id, media, caption="Here is your audio!")
                    else:
                        await self.bot.send_video(chat_id, media, caption="Here is your video!")
                    os.remove(file_path)
                else:
                    await self.bot.send_message(chat_id, "I can't download this video.\nSorry :(")
            except Exception as e:
                await self.bot.send_message(chat_id, "Invalid url")
                logging.error(f"Worker{worker_id}\nError occured on downloading: {e}")

            finally:
                self.queue.task_done()
    
    async def shutdown(self) -> None:
        """
        Graceful workers shutdown 
        """
        await self.queue.join()

        for _ in range(self.workers):
            await self.queue.put((None,None,None)) # Sentinel for each worker to terminate