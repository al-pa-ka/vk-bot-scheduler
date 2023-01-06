import asyncio
import aiohttp
import re
from database import save_last_status


class Parser:
    def __init__(self, domain, url, last_schedule):
        self.url = url
        self.domain = domain
        self.last_schedule = last_schedule
        self.schedule = None


    async def download_schedule(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.last_schedule) as response:
                self.schedule = await response.read()


    def re_find_schedule(self, html_code):
        regex = r'\/vec_assistant\/Расписание\/\d{1,2}-\d{1,2}-\d{1,4}\.jpg'
        result = re.search(regex, html_code)
        return result.group(0)


    async def check(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.domain + self.url) as response:
                html_code = await response.text()

        link = self.domain + self.re_find_schedule(html_code)

        if self.last_schedule is not None:
            if link == self.last_schedule:
                return None
        return link
    

    async def update_schedule(self, link):
        string_date = link.split('/')[-1].split('.')[0]

        day, month = string_date.split('-')[0], string_date.split('-')[1]
        year = string_date.split('-')[2][2: 4]

        save_last_status(day, month, year)
        self.last_schedule = link
        await self.download_schedule()


    async def parser_loop(self, callback):
        while True:
            try:
                if link := await self.check():
                    await self.update_schedule(link)
                    await callback()
                    await asyncio.sleep(60 * 60)
                else:
                    await asyncio.sleep(60 * 5)
            except Exception as exception:
                print(exception)
                continue
