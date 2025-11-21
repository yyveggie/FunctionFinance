import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from typing import List
from fake_useragent import UserAgent
from fake_headers.fake_headers import Headers
from trafilatura import extract
from playwright.async_api import async_playwright
from proxy_pool.usable_ip import Usable_IP
import random
import re
import time
import asyncio
import aiohttp

header = Headers(headers=True)
random_header = header.generate()
random_header['User-Agent'] = UserAgent().random

async def click_cookie_button(page):
    button_text_list = ["Accept all", "Accept cookie", "同意", "接受所有Cookie", "Allow all cookies",
                        "Accept", "Allow", "Agree", "Okay", "OK", "Yes", "Continue", "Close", "X",
                        "I Accept"]
    button_selectors = [
        f"button:has-text('{text}')" for text in button_text_list
    ] + [
        "button[data-testid*='accept']",
        "button[aria-label*='accept']",
        "button[id*='accept']",
        "button[class*='accept']",
        "button[name*='accept']",
        "button[data-testid*='agree']",
        "button[aria-label*='agree']",
        "button[id*='agree']",
        "button[class*='agree']",
        "button[name*='agree']",
        "button[data-testid*='ok']",
        "button[aria-label*='ok']",
        "button[id*='ok']",
        "button[class*='ok']",
        "button[name*='ok']",
        "button[data-testid*='continue']",
        "button[aria-label*='continue']",
        "button[id*='continue']", 
        "button[class*='continue']",
        "button[name*='continue']",
        "#consent-page > div > div > div > form > div.wizard-body > div.actions.couple > button.btn.secondary.accept-all"
        
        ## 把复制的css选择器放到这里
    ]

    for selector in button_selectors:
        button = page.locator(selector)
        if await button.count() > 0 and await button.is_visible():
            print(f"Trying to click button with selector: {selector}")
            await button.click()
            await asyncio.sleep(2)  # 添加延迟，确保点击生效
            if not await button.is_visible():
                print(f"Button clicked successfully with selector: {selector}")
                return True
            else:
                print(f"Button click failed with selector: {selector}")

    # 增加滚动逻辑
    await scroll_to_bottom(page)
    for selector in button_selectors:
        button = page.locator(selector)
        if await button.count() > 0 and await button.is_visible():
            print(f"Trying to click button after scroll with selector: {selector}")
            await button.click()
            await asyncio.sleep(2)  # 添加延迟，确保点击生效
            if not await button.is_visible():
                print(f"Button clicked successfully after scroll with selector: {selector}")
                return True
            else:
                print(f"Button click failed after scroll with selector: {selector}")

    # 尝试使用键盘交互
    try:
        print("Trying to use keyboard to accept cookies")
        await page.keyboard.press('Tab')
        await page.keyboard.press('Enter')
        await asyncio.sleep(2)  # 添加延迟，确保点击生效
        return True
    except Exception as e:
        print(f"Keyboard interaction failed: {e}")

    return False

async def hide_automation_features(page):
    await page.evaluate("""
        // Hide webdriver
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // Add random navigator properties
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3]
        });
        
        // Mock common properties
        window.navigator.chrome = { runtime: {} };
        window.navigator.permissions = { query: () => Promise.resolve({ state: 'prompt' }) };
        window.navigator.productSub = '20030107';
        window.navigator.platform = 'Win32';
    """)

async def scroll_to_bottom(page):
    await page.evaluate("""
        () => {
            window.scrollTo(0, document.body.scrollHeight);
        }
    """)

async def random_scroll(page):
    await page.evaluate(f"""
        () => {{
            window.scrollBy(0, window.innerHeight * {random.uniform(0.5, 0.9)});
        }}
    """)

def is_valid_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

async def read_website_playwright(url: str, raw_content: bool, proxy=None):
    launch_kwargs = {}
    if proxy and isinstance(proxy, str):
        launch_kwargs['proxy'] = {'server': proxy}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, **launch_kwargs)
        context = await browser.new_context(
            user_agent=UserAgent().random,
            ignore_https_errors=True,
        )
        page = await context.new_page()
        
        async def handle_dialog(dialog):
            await dialog.dismiss()
        
        page.on("dialog", handle_dialog)
        
        try:
            await page.goto(url, wait_until="domcontentloaded")
            await hide_automation_features(page)
            await asyncio.sleep(random.uniform(3, 5))
            
            if "Just a moment..." in await page.content():
                await asyncio.sleep(random.uniform(2, 4))  
                await page.reload()
                
            await asyncio.sleep(random.uniform(2, 4))
            await page.evaluate("""
                () => {
                    window.scrollBy(0, window.innerHeight * 0.5);
                }
            """)
            await asyncio.sleep(random.uniform(2, 4))
            await page.mouse.move(100, 100)
            await page.mouse.move(200, 200, steps=50)                

            # 尝试点击同意按钮
            if await click_cookie_button(page):
                await page.wait_for_load_state("domcontentloaded")
                await asyncio.sleep(random.uniform(3, 5))

            html_content = await page.content()
            content = extract(html_content)
            if raw_content:
                content = html_content
        except Exception as e:
            print(f"Error during page interaction: {e}")
            content = None
        finally:
            await context.close()
            await browser.close()
        return content if content is not None else None

async def scrape_content(url: str, session: aiohttp.ClientSession, raw_content: bool):
    usable_ip = Usable_IP()
    proxy = await usable_ip._get_proxy(session)
    
    launch_kwargs = {}
    if proxy and isinstance(proxy, str):
        launch_kwargs['proxy'] = {'server': proxy}
    
    result_pw = await read_website_playwright(url=url, raw_content=raw_content, proxy=proxy)
    if result_pw is not None:
        return result_pw

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=['--start-maximized'], **launch_kwargs)
        
        # 随机浏览器特征
        width, height = random.choice([(1920, 1080), (1366, 768), (1440, 900), (1536, 864)])
        context = await browser.new_context(
            user_agent=UserAgent().random,
            viewport={"width": width, "height": height}, 
            locale=random.choice(['en-US', 'en-GB', 'fr-FR', 'de-DE', 'ja-JP']),
            ignore_https_errors=True,
            no_viewport=True
        )
        page = await context.new_page()

        # 拦截某些请求
        await page.route("**/*.{png,jpg,jpeg,gif,webp,svg,ico}", lambda route: route.abort())
        await page.route("**/*analytics*.{js,css}", lambda route: route.abort())
        await page.route("**/*fingerprint*.{js,css}", lambda route: route.abort())
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # 隐藏 webdriver
            await page.evaluate("""
            () => {
                Object.defineProperties(navigator, {
                    webdriver: {
                        get: () => false
                    }
                });
                window.chrome = {};
            }
            """)
            
            # 随机延迟
            await asyncio.sleep(random.uniform(2, 4))
            
            # 点击cookie同意按钮
            if await click_cookie_button(page):
                await page.wait_for_load_state("domcontentloaded")
                await asyncio.sleep(random.uniform(2, 4))
            
            await page.evaluate("""
                () => {
                    const elements = document.querySelectorAll("iframe[src]");
                    elements.forEach(element => {
                        const url = element.src;
                        if (url.startsWith("https://www.google.com/recaptcha/")) {
                            element.remove();
                        }
                    });
                }
            """)
            await asyncio.sleep(random.uniform(2, 4))
            
            if "Please enable JS and disable any ad blocker" in await page.content():
                await asyncio.sleep(random.uniform(2, 4))
                await page.reload(wait_until="domcontentloaded", timeout=30000)

            # 注入随机噪音
            await page.evaluate("""
            () => {
                // 添加随机变量
                window.navigator.chrome = {
                    runtime: {},
                    // ...
                };
                window.navigator.productSub = String(Math.floor(Math.random() * 100));
                // ...
            }
            """)

            await random_scroll(page)
            await asyncio.sleep(random.uniform(2, 5))  # 随机延迟
            
            # 随机鼠标移动
            await page.mouse.move(random.uniform(50, 150), random.uniform(50, 150))
            await asyncio.sleep(random.uniform(0.5, 1.5))
            await page.mouse.move(random.uniform(200, 300), random.uniform(200, 300), steps=random.randint(30, 70))

            await asyncio.sleep(random.uniform(2, 4))  # 随机延迟
            html_content = await page.content()
            content = extract(html_content)
            if raw_content:
                content = html_content
            if content:
                await context.close()
                await browser.close()
                return content

            await context.close()  
            await browser.close()
            return None

        except Exception as e:
            print(f"Error scraping content for {url}: {e}")
            await context.close()
            await browser.close()
            return None


# 整体流程中加入更多的随机行为和代理切换
async def scrape_urls(urls: List[str], raw_content: bool):
    async with aiohttp.ClientSession(headers=random_header) as session:
        semaphore = asyncio.Semaphore(3)
        tasks = []
        for url in urls:
            if is_valid_url(url):
                async with semaphore:
                    task = asyncio.ensure_future(
                        scrape_content(url, session, raw_content)
                    )
                    tasks.append(task)
            else:
                tasks.append(asyncio.Future())
                tasks[-1].set_result(None)
        results = await asyncio.gather(*tasks)
        return results

async def run(urls: List[str], raw_content: bool=False):
    return await scrape_urls(urls, raw_content)

def run_sync(urls: List[str], raw_content: bool=False):
    return asyncio.run(run(urls, raw_content))

if __name__ == "__main__":
    import time
    urls = [
        'https://www.zhihu.com/people/da-meng-24-13/answers'
    ]
    s = time.time()
    results = asyncio.run(run(urls))
    print(results)
    print(len(results))
    d = time.time()
    print(f"Time: {d - s} seconds")