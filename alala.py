import asyncio
import time
import httpx


async def fetch_url_data(url):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
    except Exception as e:
        print(e)
    else:
        return resp
    return


async def fetch_async(r):
    url = "https://www.uefa.com/uefaeuro-2020/"
    tasks = []
    for i in range(r):
        task = asyncio.create_task(fetch_url_data(url))
        tasks.append(task)
    responses = await asyncio.gather(*tasks)
    return responses


if __name__ == '__main__':
    for ntimes in [1, 10, 50]:
        start_time = time.time()
        loop = asyncio.get_event_loop()
        # будет выполняться до тех пор, пока не завершится или не возникнет ошибка
        result = loop.run_until_complete(fetch_async(ntimes))
        print(result)
        print(f'Получено {ntimes} результатов запроса за {time.time() - start_time} секунд')
