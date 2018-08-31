import asyncio
from typing import Generator, Iterator

import aiohttp


async def fetch(url, session):
    async with session.get(url) as response:
        if response.status != 200:
            response.raise_for_status()
        return await response.text()


async def get_futures(urls: Iterator[str], timeout=None, headers=None):
    tasks = []
    async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
        for url in urls:
            task = asyncio.ensure_future(fetch(url, session))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
    return responses


def fetch_urls(urls: list, headers: dict = None, timeout: aiohttp.ClientTimeout = None) -> Iterator[str]:
    """
    Asynchronously fetch multiple urls and return Iterator object that contains all of the responses
    Example usage:
    urls = ['https://httpbin.org/get', 'https://google.com', 'https://gitlab.com/meltano/']
    for result in fetch_urls(urls):
        print(result)

    :param headers: dict of headers to be passed with the request
    :param timeout: timeout object to be passed to the aiohttp lib
    :param urls: Iterator of url strings
    :return: Generator of response texts
    """
    loop = asyncio.get_event_loop()
    futures = get_futures(
        urls=urls,
        headers=headers,
        timeout=timeout,
    )
    future = asyncio.ensure_future(futures)
    responses = loop.run_until_complete(future)
    for resp in responses:
        yield resp

