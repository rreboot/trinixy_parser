import asyncio, aiohttp
import time
import httpx
from lxml import html


async def parse_posts_urls(html_source) -> list:
    tree = html.fromstring(html_source)

    return tree.xpath('//article[@class="typical"]/h2/a/@href')


async def parse_gifs_urls(html_source) -> list:
    tree = html.fromstring(html_source)

    return tree.xpath('//div[@itemprop="articleBody"]//img/@src')


async def get_posts_page(page_url):
    """ Получение url постов с гифками со страницы пагинации. """
    async with httpx.AsyncClient() as client:
        resp = await client.get(page_url)
        posts_urls = await parse_posts_urls(resp.text)

    return await get_gifs_page(posts_urls)


async def get_gifs_page(posts_urls):
    """ Получение url гифок со страницы поста. """
    async with httpx.AsyncClient() as client:
        for url in posts_urls:
            resp = await client.get(url)

            return await parse_gifs_urls(resp.text)


async def get_num_pages():
    """ Получение количества страниц. """
    url = 'https://trinixy.ru/gif/'

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        tree = html.fromstring(response.text)
        pages = tree.xpath(
            '//span[@class="nav_ext"]/following-sibling::a/text()'
        )[0]

    return int(pages)


async def main():
    url = 'https://trinixy.ru/gif/page/{}/'
    pages = await get_num_pages()
    tasks = []

    for page in range(1, pages + 1):
        task = asyncio.create_task(get_posts_page(url.format(page)))
        tasks.append(task)

    return await asyncio.gather(*tasks)


if __name__ == '__main__':
    start_time = time.time()
    result = asyncio.run(main())

    print(result)
    print(f'Time: {time.time() - start_time}')
