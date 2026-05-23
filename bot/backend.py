import asyncio
from typing import Optional
import bot.services.yt_downloader as yt_downloader

class FakeDownloader:
    def __init__(self, workers = 3, queue_size: int = 10):
        self.queue = asyncio.Queue(maxsize=queue_size)

        self.results: dict[int: list[str]] = {} # dict {user_id: text(video)}
        self.workers: int = workers

    async def start_workers(self):
        # create workers(consumers)
        for worker_id in range(self.workers):
            asyncio.create_task(self.worker(worker_id))
            

    async def download(self, url):
        yt_downloader.youtube_download(url)

        return './tg-vinland/tg_vinland_bot/video.mp4'

    async def fake_download(self, url: str) -> str:
        """
        Simulation of media downloading
        """
        print(f'Downloading {url}')
        await asyncio.sleep(1)

        result = f'{url}.mp4'

        print(f'Downloaded {url}')

        return result
    
    async def add_url(self, url, user_id: int) -> None:
        await self.queue.put((user_id, url))
        
        if user_id not in self.results:
            self.results[user_id] = []

    async def worker(self, worker_id: int) -> None:
        """
        Async consumer, recives url from queue and downloads media
        """
        while True:
            user_id, url = await self.queue.get()  

            if user_id is None:
                self.queue.task_done()
                break

            result = await self.download(url)

            self.results[user_id].append(result)
            self.queue.task_done()

    async def get_result(self, user_id: int) -> Optional[str]:
        """
        Get results for specific user by id
        """
        if user_id not in self.results:
            print("No content for this user")
            return None
        
        result = self.results[user_id]
        del self.results[user_id]
        return result
    
    async def shutdown(self) -> None:
        """
        Graceful workers shutdown 
        """
        await self.queue.join()

        for _ in range(self.workers):
            await self.queue.put((None,None)) # Sentinel for each worker to terminate