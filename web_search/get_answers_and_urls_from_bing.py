from playwright.sync_api import sync_playwright
from selectolax.parser import HTMLParser
import random
import time

def random_typing_delay():
    return random.uniform(0.05, 0.2)

def get_urls(input: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36', '--disable-javascript'])
        page = browser.new_page()
        try:
            page.goto('https://www.bing.com', wait_until='domcontentloaded', timeout=30000)
            
            # 检查是否出现隐私提示框,如果出现就点击 "拒绝" 按钮
            if page.query_selector('div[aria-modal="true"]'):
                # 等待 "拒绝" 按钮可见
                page.wait_for_selector('button:has-text("拒绝")', state='visible', timeout=30000)
                page.click('button:has-text("拒绝")')
            
            # 在点击搜索框之前,模拟鼠标移动
            page.mouse.move(random.randint(0, 100), random.randint(0, 100))
            page.wait_for_selector('#sb_form_q', state='visible', timeout=30000)
            page.click('#sb_form_q')
            
            # 模拟打字速度
            for char in input:
                page.type('#sb_form_q', char, delay=random_typing_delay())
            
            # 在点击搜索按钮之前,添加随机延迟
            time.sleep(random.uniform(2, 4))
            page.press('#sb_form_q', 'Enter')
            page.wait_for_load_state('networkidle', timeout=30000)
            print('results')

            # 等待页面渲染完成
            time.sleep(5)
            
            # 检查是否出现隐私提示框,如果出现就点击 "拒绝" 按钮
            if page.query_selector('div[aria-modal="true"]'):
                # 等待 "拒绝" 按钮可见
                page.wait_for_selector('button:has-text("拒绝")', state='visible', timeout=30000)
                page.click('button:has-text("拒绝")')
            
            # 获取搜索结果页面的HTML
            html = page.inner_html('html')
            parser = HTMLParser(html)

            # 检查是否有直接答案
            answer_text = None
            direct_answer = parser.css_first('#b_results > li.b_ans.b_top.b_topborder.b_tophb.b_topshad')
            if direct_answer:
                answer_text = direct_answer.text()

            # 获取前5个搜索结果的URL
            urls = []
            for result in parser.css('#b_results > li.b_algo'):
                if len(urls) >= 5:
                    break
                url_element = result.css_first('.b_title > h2 > a')
                if url_element:
                    url = url_element.attributes.get('href')
                    if url:
                        urls.append(url)

            return answer_text, urls

        except TimeoutError as e:
            print(f"Timeout error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            browser.close()

answer, urls = get_urls("特斯拉的最新股价和市盈率")
print("答案文本:", answer)
print("搜索结果URL:")
for url in urls:
    print(url)