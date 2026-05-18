import asyncio

class FakeDownloader:
    def __init__(self):
        self.tasks = []
    async def fake_download(self, url):
        '''
        Simulation of downloading task
        '''
        print(f'Downloading {url}')
        asyncio.sleep(1)
        print(f'Here is your .mp4 ...')
        return f'{url}.mp4'
        
    def add_task(self, url):
        self.tasks.append(url)

    async def run(self):
        if not self.tasks:
            return []
        
        # sem = asyncio.Semaphore(2)
        results = []
        for url in self.tasks:
            res = await self.fake_download(url)
            results.append(res)

        self.tasks.clear()
        return results