import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import io
import os
import base64
import anthropic
import requests
from PIL import Image
from openai import OpenAI
from textwrap import dedent
from playwright.sync_api import sync_playwright
from config_loader import (
    CLAUDE_API_KEY,
    CLAUDE_OPUS,
    OPENAI_API_KEY,
    GPT4O,
    FREEIMAGE_API_KEY
)

llm = 'openai'

class StockAnalyzer:
    def __init__(self):
        pass

    def us_stock_capture(self, playwright, stock_code, selected_indicators):
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # 打开网页
        page.goto(f"https://stockanalysis.com/stocks/{stock_code}/chart/")
        page.wait_for_timeout(1000)

        # 尝试通过文本 '6M' 定位元素
        six_month_selector_text = "text=6M"
        six_month_selector_fallback = r"#main > div.relative.mt-0\.5.border.border-default > div > cq-context > div.ciq-footer.full-screen-hide > cq-show-range > div:nth-child(5)"
        try:
            page.wait_for_selector(six_month_selector_text, timeout=5000)
            page.click(six_month_selector_text)
        except:
            page.wait_for_selector(six_month_selector_fallback, timeout=10000)
            page.click(six_month_selector_fallback)
        page.wait_for_timeout(1000)

        for i in selected_indicators:
            # 等待 'Studies' 按钮出现并点击
            studies_selector = r"#main > div.relative.mt-0\.5.border.border-default > div > cq-context > div.ciq-nav.full-screen-hide > div.ciq-menu-section > div.ciq-dropdowns > cq-menu.ciq-menu.ciq-studies.ciq-study-browser > span"
            page.wait_for_selector(studies_selector, timeout=10000)
            page.click(studies_selector)
            page.wait_for_timeout(1000)

            # 等待 'Study Library' 按钮出现并点击
            study_library_selector = r"#main > div.relative.mt-0\.5.border.border-default > div > cq-context > div.ciq-nav.full-screen-hide > div.ciq-menu-section > div.ciq-dropdowns > cq-menu.ciq-menu.ciq-studies.ciq-study-browser.stxMenuActive > cq-menu-dropdown > cq-study-menu-manager > cq-study-browser > div > div.ciq-sb-categories > cq-scroll > cq-item:nth-child(5)"
            page.wait_for_selector(study_library_selector, timeout=10000)
            page.click(study_library_selector)

            if i.lower() == 'moving average':
                # 在搜索框输入'moving average'
                page.fill("input[type='search']", "moving average")
                # 向下滚动以确保 'Moving Average' 在视图中
                page.evaluate("window.scrollBy(0, 100)")
                # 等待 'Moving Average' 按钮出现并点击
                moving_average_selector = r"#main > div.relative.mt-0\.5.border.border-default > div > cq-context > div.ciq-nav.full-screen-hide > div.ciq-menu-section > div.ciq-dropdowns > cq-menu.ciq-menu.ciq-studies.ciq-study-browser.stxMenuActive > cq-menu-dropdown > cq-study-menu-manager > cq-study-browser > div > div.ciq-sb-studies > div:nth-child(1) > cq-scroll > cq-studies > cq-studies-content > cq-item:nth-child(61) > span"
                page.wait_for_selector(moving_average_selector, timeout=10000)
                page.click(moving_average_selector)
                page.wait_for_timeout(1000)
                # 等待 'Done' 按钮出现并点击
                done_selector = "body > div.cq-dialogs > cq-dialog > cq-study-dialog > div > div"
                page.wait_for_selector(done_selector, timeout=10000)
                page.click(done_selector)

            else:
                # 在搜索框输入指标名称
                page.fill("input[type='search']", f"{i}")
                # 等待指标按钮出现并点击
                indicator_selector = f"text={i}"
                page.wait_for_selector(indicator_selector, timeout=10000)
                page.click(indicator_selector)
                page.wait_for_timeout(1000)

        # 等待 'Full Screen' 按钮出现并点击
        full_screen_selector = "text=Full Screen"
        page.wait_for_selector(full_screen_selector, timeout=10000)
        page.click(full_screen_selector)
        # 等待3秒使图表完全加载
        page.wait_for_timeout(3000)
        # 截图并保存
        page.screenshot(path=f"test_{stock_code}.png", full_page=True)

        context.close()
        browser.close()

    def analyze(self, stock_code, selected_indicators, area="美国"):
        if os.path.exists(f"test_{stock_code}.png"):
            pass
        else:
            with sync_playwright() as p:
                if area == '美国':
                    # print(f'searching {stock_code}...', end='\n')
                    self.us_stock_capture(p, stock_code, selected_indicators)
                    # print('Done!')
            # 指定本地图片路径
        image1_path = f"test_{stock_code}.png"

        # 读取图片文件
        with open(image1_path, "rb") as image_file:
            img = Image.open(image_file)
            
            # 将图片转换为 base64 编码的数据
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            image_data = base64.b64encode(buffer.getvalue()).decode("utf-8")

        system_message = dedent(f'''
                As a skilled stock and technical analyst, providing price charts, please analyze the chart in detail.
                Provide 'buy', 'sell', or 'hold' recommendations for the chart and explain your reasons (need to explain what features of the user lead to your choice), also please provide your confidence level (represented as a numerical value, such as 74%).
                ''')
        user_prompt = dedent(f"""
                Please pay attention to the following points in your analysis:
                1. **Overall Trend** - Determine if the price is in an uptrend, downtrend, or consolidating state based on whether higher highs and higher lows (uptrend) or lower highs and lower lows (downtrend) are occurring.
                2. **Support and Resistance Levels** - Identify key price levels where the price has previously encountered resistance or struggled to break through. These are potential decision-making areas for future price movements.
                3. **Indicators** - Using the provided indicators: {selected_indicators}, observe the indicator curves on the chart and explain the significance of each indicator's trend to supplement the price action analysis.
                4. **Price Patterns** - Analyze whether there are any recognizable bullish or bearish price patterns on the chart, such as head and shoulders, triangles, wedges, flags, double tops/bottoms, etc.
            """)

        if llm.lower() == 'claude':
            image_media_type = "image/png"  # 根据实际图片格式设置媒体类型
            client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
            message = client.messages.create(
                model=CLAUDE_OPUS,
                max_tokens=4096,
                system=system_message,
                temperature=0,
                messages=[
                    {
                        "role": "user", 
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64", 
                                    "media_type": image_media_type,
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": user_prompt
                            }
                        ],        
                    }
                ],
            )
            return message.content[0].text
        
        elif llm.lower() == 'gpt4o':
            def upload_image(api_key):
                api_url = "https://freeimage.host/api/1/upload"
                data = {
                    "key": api_key,
                    "action": "upload",
                    "source": image_data,
                    "format": "json"
                }
                response = requests.post(api_url, data=data)
                if response.status_code == 200:
                    json_data = response.json()
                    if json_data["status_code"] == 200 and json_data["success"]["code"] == 200:
                        image_url = json_data["image"]["url"]
                        return image_url
                return None
            image_url = upload_image(FREEIMAGE_API_KEY)
            if image_url is None:
                return None
            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model=GPT4O,
                max_tokens=3000,
                temperature=0,
                messages = [
                    {
                        "role": "system",
                        "content": system_message
                        },
                    {
                        "role" : "user",
                        "content" :
                        [
                            {"type" : "text", "text" : user_prompt},
                            {
                                "type" : "image_url",
                                "image_url": {"url": image_url},
                            }
                        ]
                    }
                ]
            )
            return response.choices[0].message.content


def main(ticker, selected_indicators):
    analyzer = StockAnalyzer()
    prediction = analyzer.analyze(ticker, selected_indicators=selected_indicators)
    return prediction

def run(ticker, selected_indicators):
    result = main(ticker, selected_indicators)
    return dedent(f"""
I am an AI assistant like you, helping you complete the user's request. This is the data I obtained. Please organize it out and return it to the user.
</START>{result}</END>
""").strip()

if __name__ == "__main__":
    selected_indicators = []
    print(run('BABA', selected_indicators))
