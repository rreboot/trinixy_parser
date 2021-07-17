import asyncio
import time

import httpx
from lxml import html


# async def get_response(url: str):
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
#                       '(KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
#     }
#     async with httpx.AsyncClient(headers=headers) as client:
#         return await client.get(url)


class TrinixyParser:
    """ Парсер url gif с сайта trinixy.ru """

    page: int = 1
    parsed_items: int = 0
    skipped_items: int = 0
    posts_urls = set()
    gifs_urls = set()

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.create_tasks())


    def get_num_pages(self):

        url = 'https://trinixy.ru/gif/'
        response = httpx.get(url)
        tree = html.fromstring(response.text)

        pages = tree.xpath(
            '//span[@class="nav_ext"]/following-sibling::a/text()'
        )[0]

        return int(pages)

    async def fetch_posts_urls(self, url):
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            tree = html.fromstring(resp.text)
            urls = tree.xpath('//article[@class="typical"]/h2/a/@href')
            self.posts_urls.update(set(urls))

        return urls

    async def create_tasks(self):
        tasks = []
        url = 'https://trinixy.ru/gif/page/{}/'

        for i in range(1, 20):
            task = asyncio.create_task(self.fetch_posts_urls(url.format(i)))
            tasks.append(task)

        return await asyncio.gather(*tasks)


if __name__ == '__main__':
    time_start = time.time()

    parser = TrinixyParser()
    parser.run()

    time_end = time.time() - time_start
    print(f'time {time_end}')
