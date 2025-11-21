import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from typing import List
import asyncio
import aiohttp
from trafilatura import fetch_url, extract
from fake_headers.fake_headers import Headers
from crawler import headless_scrape
from fake_useragent import UserAgent
from proxy_pool.usable_ip import Usable_IP as ui

header = Headers(
    # generate any browser & os headeers
    headers=True
)
random_header = header.generate()
random_header['User-Agent'] = UserAgent().random

async def read_website_req(url: str, session: aiohttp.ClientSession):
    usable_ip = ui()
    try:
        response_text = await usable_ip.request_get(url, session=session)
        if response_text:
            content = extract(response_text)
            return content
    except (aiohttp.ClientError, asyncio.TimeoutError):
        return None

async def read_website_traf(url: str, session: aiohttp.ClientSession):
    try:
        downloaded = fetch_url(url=url)
        return extract(downloaded)
    except:
        return None

async def read_website_playwright(url: str):
    result_pw = await headless_scrape.run([url])
    return result_pw

async def scrape_content(url: str, session: aiohttp.ClientSession, max_content_length, proxy=None):
    result_traf = await read_website_traf(url, session)
    if result_traf is not None:
        return {
            'context': result_traf[:max_content_length],
            'url': url,
        }

    result_req = await read_website_req(url, session)
    if result_req is not None:
        return {
            'context': result_req[:max_content_length],
            'url': url,
        }

    result_pw = await read_website_playwright(url)
    if result_pw is not None:
        return {
            'context': result_pw[:max_content_length],
            'url': url,
        }
    return None

async def scrape_urls(urls: List[str], max_content_length):
    async with aiohttp.ClientSession(headers=random_header) as session:
        semaphore = asyncio.Semaphore(3)  # 限制并发数
        tasks = []
        for url in urls:
            usable_ip = ui()
            proxy = await usable_ip._get_proxy(session)
            
            async with semaphore:
                task = asyncio.ensure_future(
                    scrape_content(url, session, max_content_length, proxy))
                tasks.append(task)
        results = await asyncio.gather(*tasks)
        return [result for result in results if result is not None]


async def run(urls: List[str], max_content_length=1500):
    results = await scrape_urls(urls, max_content_length)
    for result in results:
        print(f"Scraped content for {result['url']}: {result['context'][:100]}...")
    return results

if __name__ == "__main__":
    import time
    urls = [
        # 'https://www.pymnts.com/apple/2024/apples-marketing-head-for-vision-pro-retires/',
        # 'https://www.businessinsider.com/apple-china-iphone-sales-slide-huawei-counterpoint-tim-cook-2024-4',
        # 'https://www.fastcompany.com/91110688/apple-amazon-alphabet-meta-microsoft-nvidia-profit-momentum-collapse-2024-ubs'
        'https://www.zhihu.com/people/da-meng-24-13/answers'
    ]
    s = time.time()
    results = asyncio.run(run(urls))
    print(results)
    print(len(results))
    d = time.time()
    print(f"Time: {d - s} seconds")