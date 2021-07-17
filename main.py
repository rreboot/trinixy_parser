""" ТЗ

Собираемые поля: tags - теги гифки;
                 url - адрес гифки;
                 description - описание;
                 source_date - исходная дата файла на сервере;
                 parse_date - дата парсинга;

На входе: url 1 страницы;
Результат: запись данных в БД;

Условия:
    - проверка формата файла (только gif);
    - получение даты файла на сервере, если нет - ставить самую старую;

Методы: run - запуск парсера;

Кейсы:
    - Отсутствует подключение к БД - прервать работу;
    - Отсутствует подключение к сайту - сделать несколько попыток;
    - Ошибка получения данных (блок, 404, 500) - сделать несколько попыток;
    - Неверный формат файла (jpg, png) - пропуск файла;

"""
from urllib.parse import urljoin

import backoff
from dateutil.parser import parse
import requests
from lxml import html

from config import API_URL


@backoff.on_exception(backoff.expo,
                      (requests.exceptions.RequestException,
                       requests.exceptions.Timeout),
                      max_tries=5)
def request(method, url, **kwargs):
    """ Отправка реквеста с использованием backoff. До 4-х попыток отправить
    запрос повторно при возникновении requests.RequestException.

    Parameters
    ----------
    method : str
        Method for the new Request object: GET, OPTIONS, HEAD, POST, PUT,
        PATCH, or DELETE
    url : str
        Request url.
    args : requests.get args
    kwargs : requests.get kwargs

    Returns
    -------
    response : requests.response

    """
    return requests.request(method, url, **kwargs)


def get_source_date(file_url):
    headers = request('HEAD', file_url).headers
    date = headers.get('Date')
    if not date:
        return None
    date = date.split(',')[-1].strip()
    date = parse(date, fuzzy=True)

    return str(date)


def create_gif(gif_url, description, source_date):
    params = {'url': gif_url,
              'description': description,
              'date_source': source_date}

    request('POST', urljoin(API_URL, 'gif'), json=params)


class TrinixyParser:
    """ Парсер url gif с сайта trinixy.ru """

    page: int = 1
    parsed_items: int = 0
    skipped_items: int = 0

    def __init__(self):
        pass

    def run(self):
        url = 'https://trinixy.ru/gif/page/{}/'

        while True:
            page_info = request('GET', url.format(self.page))
            tree = html.fromstring(page_info.text)

            print(f'parsing page: {page_info.url}')

            posts = tree.xpath('//article[@class="typical"]')
            for post in posts:
                # Get post info
                post_url = post.xpath('.//h2/a/@href')[0]
                self.parse_post(post_url)

            next_page = tree.xpath('//span[@class="nextlinkk"]/a/@href')
            if next_page:
                url = next_page[0]
            else:
                break

    def parse_post(self, post_url):
        """ Парсинг страницы с гифками.

        Parameters
        ----------
        post_url : str
            Post url.

        Returns
        -------

        """
        response = request('GET', post_url)
        tree = html.fromstring(response.text)

        title = tree.xpath('//article/h1/text()')[0]
        print(title)

        description = ' '.join(
            tree.xpath('//div[@itemprop="articleBody"]/text()')).strip()

        tags = tree.xpath('//div[contains(@class, "arttags")]/a/text()')
        gifs_urls = tree.xpath('//div[@itemprop="articleBody"]//img/@src')

        for gif_url in gifs_urls:

            # check extension
            extension = gif_url.split('.')[-1]
            if extension != 'gif':
                self.skipped_items += 1
                continue

            # get_source_date
            source_date = get_source_date(gif_url)

            # send gif to db
            create_gif(gif_url, description, source_date)

            # # create tags
            # for tag in tags:


if __name__ == '__main__':
    parser = TrinixyParser()
    parser.run()
