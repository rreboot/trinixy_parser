import asyncio
import itertools
import time

import httpx
from lxml import html


class TrinixyParser:
    """ Парсер url gif с сайта trinixy.ru """

    page: int = 1
    pages: int = None
    parsed_items: int = 0
    skipped_items: int = 0
    posts_urls = set()
    gifs_urls = set()
    loop = asyncio.get_event_loop()

    def run(self):
        self.get_num_pages()

        self.posts_urls = self.loop.run_until_complete(self.create_posts_tasks())
        self.posts_urls = self.flatten_list(self.posts_urls)

        self.gifs_urls = self.loop.run_until_complete(self.create_gifs_tasks())
        self.gifs_urls = self.flatten_list(self.gifs_urls)

    def get_num_pages(self):
        print('Getting number of pages')

        url = 'https://trinixy.ru/gif/'
        response = httpx.get(url)
        tree = html.fromstring(response.text)

        pages = tree.xpath(
            '//span[@class="nav_ext"]/following-sibling::a/text()'
        )[0]
        self.pages = int(pages)
        print(f'Pages: {self.pages}')

    async def fetch_urls(self, url: str, xpath: str) -> list:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'
        }
        async with httpx.AsyncClient(timeout=600, headers=headers) as client:
            resp = await client.get(url)
            print(resp.url)
            tree = html.fromstring(resp.text)
            urls = tree.xpath(xpath)

        return urls

    async def create_posts_tasks(self):
        url = 'https://trinixy.ru/gif/page/{}/'
        tasks = []

        while self.page <= self.pages:
            # await asyncio.gather(*корутины для получения урлов постов)
            task = asyncio.create_task(
                self.fetch_urls(
                    url=url.format(self.page),
                    xpath='//article[@class="typical"]/h2/a/@href'
                )
            )

            tasks.append(task)

            self.page += 1

        return await asyncio.gather(*tasks)

    async def create_gifs_tasks(self):
        tasks = []

        for post_url in self.posts_urls:
            task = asyncio.create_task(
                self.fetch_urls(
                    url=post_url,
                    xpath='//div[@itemprop="articleBody"]//img/@src'
                )
            )

            tasks.append(task)

        return await asyncio.gather(*tasks)

    def flatten_list(self, nested_list: list):
        return list(itertools.chain(*nested_list))


if __name__ == '__main__':
    time_start = time.time()

    parser = TrinixyParser()
    parser.run()

    time_end = time.time() - time_start
    print(f'time {time_end}')
