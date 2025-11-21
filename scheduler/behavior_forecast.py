import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import io
import os
import time
import base64
import anthropic
import datetime
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

llm = 'claude'

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

    def chinese_stock_capture(self, playwright, stock_code, selected_indicators):
        zhibiao = ['布林线', '指数移动平均线（200）', '指数移动平均线（50）', '相对强弱指数', '移动平均线聚散指标', '简单移动平均线（200）', '简单移动平均线（50）', '随机指标']
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # 导航到目标页面
        page.goto(f"https://www.msn.cn/zh-cn/money/chart?id=adaimw&timeFrame=3M&chartType=candlestick&projection=false", wait_until="networkidle")

        # 使用循环和超时机制来点击"我接受"按钮
        timeout = 10000  # 超时时间为 10 秒
        start_time = time.time()
        while time.time() - start_time < timeout:
            accept_button = page.query_selector("#onetrust-accept-btn-handler")
            if accept_button:
                accept_button.click()
                page.wait_for_timeout(2000)  # 等待 2 秒,以便页面完成相关操作
                break
            else:
                accept_button = page.query_selector("text=我接受")
                if accept_button:
                    accept_button.click()
                    page.wait_for_timeout(2000)  # 等待 2 秒,以便页面完成相关操作
                    break
            page.wait_for_timeout(500)  # 等待 500 毫秒后再次检查

        page.fill("#searchBox > input", f"{stock_code}")
        page.wait_for_timeout(1000)  # 等待 1 秒,让下拉框加载出来

        # 使用您提供的 CSS 选择器来点击弹窗
        popup_selector = "#FinanceChartPage > div > div.leftRailContainer-DS-EntryPoint1-1 > div.searchboxContainer-DS-EntryPoint1-1 > div.searchbox-DS-EntryPoint1-1 > div > div:nth-child(2)"
        popup = page.wait_for_selector(popup_selector)
        popup.click(force=True)  # 强制点击弹窗

        for i in selected_indicators:
            if i in zhibiao:
                # 点击"指标"
                page.click("#FinanceChartPage > div > div.chartContainer-DS-EntryPoint1-1 > div > div > div:nth-child(1) > div > div.selectorsGroup-DS-EntryPoint1-1 > div:nth-child(2) > div > div > button")
                page.click(f"text={i}")
            else:
                # 点击"财务状况"
                page.click("#FinanceChartPage > div > div.chartContainer-DS-EntryPoint1-1 > div > div > div:nth-child(1) > div > div.selectorsGroup-DS-EntryPoint1-1 > div:nth-child(3) > div > div > button")
                page.fill("#FinanceChartPage > div > div.chartContainer-DS-EntryPoint1-1 > div > div > div:nth-child(1) > div > div.selectorsGroup-DS-EntryPoint1-1 > div:nth-child(3) > div > div > div > div.menu-DS-EntryPoint1-1 > div.searchBoxRoot-DS-EntryPoint1-1 > input", f"{i}")
                page.click(f"text={i}")

        # 截图并保存
        page.screenshot(path=f"test_{stock_code}.png", full_page=True)

        context.close()
        browser.close()

    def analyze(self, stock_code, selected_indicators, user_knowledge, area="美国"):
        if os.path.exists(f"test_{stock_code}.png"):
            pass
        else:
            with sync_playwright() as p:
                if area == '美国':
                    # print(f'searching {stock_code}...', end='\n')
                    self.us_stock_capture(p, stock_code, selected_indicators)
                    # print('Done!')
                elif area == '中国':
                    # print(f'searching {stock_code}...', end='\n')
                    self.chinese_stock_capture(p, stock_code, selected_indicators)
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
                    As a skilled stock behavior analyst, given the description of the price chart, please analyze the chart in detail based on the user's financial background:
                    {''.join(user_knowledge)}
                    Provide 'buy', 'sell', or 'hold' recommendations for the chart and explain your reasons (need to explain which features of the user lead to your choice), also please provide your confidence level (represented as a numerical value, such as 74%).
                ''')
        user_prompt = dedent(f"""
                When making predictions, please comprehensively consider the behavioral factors (psychological factors) behind the trends. Analyze price movements and patterns from the perspective of behavioral finance theory, considering how investor psychology influences the market.
                Please discuss the following points in detail:
                1. **Market Sentiment** - Evaluate the current market sentiment as bullish, bearish, or neutral based on recent price movements. Consider how this sentiment drives trends.
                2. **Investor Emotion** - Look for signs of investor emotions such as fear, greed, optimism, and pessimism in chart patterns. Discuss how these emotions influence buying and selling decisions.
                3. **Herding Behavior** - Identify if price movements exhibit herding behavior, where many investors follow the crowd. Explain how this psychological factor fuels trends.
                4. **Anchoring Bias** - Consider if investors are anchoring their value perception to key price levels. Discuss how this bias affects support and resistance levels.
                5. **Overreaction and Underreaction** - Analyze if the market overreacts or underreacts to certain events or information. Explain how these behavioral tendencies impact price movements.
                6. **Loss Aversion** - Assess investors' attitudes towards potential losses and how this psychological tendency affects their risk tolerance and trading decisions.
                7. **Mental Accounting** - Consider how investors mentally segregate their portfolios into different "accounts" and discuss how this mental mechanism influences their asset allocation decisions.
                8. **Information Bias** - Analyze how investors interpret and react to market information and how this bias leads to irrational decisions.
                9. **Emotional Fluctuations** - Evaluate changes in investor emotions over time and how these fluctuations affect market trends and volatility.
                10. **Group Behavior** - Observe collective behavior patterns of investor groups, such as collective mania or panic, and discuss how these behaviors amplify market trends.
                Please integrate these behavioral finance concepts to conduct an in-depth analysis of the chart, revealing the connection between investor psychological factors and price movements. Based on the analysis, provide clear trading recommendations and explain your reasoning process.
                Today is {datetime.date.today()}.
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
        
        elif llm.lower() == 'gpt4':
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


def main(ticker, user_knowledge):
    analyzer = StockAnalyzer()
    # ticker = input('请输入您想预测公司的股票代码:')
    # selected_indicators = input('请输入您想分析的金融指标（最多三项，用‘,’分离）:') # ['MACD', 'RSI', 'Moving Average']
    # selected_indicators = selected_indicators.split(',') or selected_indicators.split('，')
    selected_indicators = ['MACD', 'RSI']
    prediction = analyzer.analyze(ticker, selected_indicators, user_knowledge)
    return prediction

def run(ticker, user_knowledge):
    result = main(ticker, user_knowledge)
    return result

if __name__ == "__main__":
    import json
    from pathlib import Path
    def load_user_profiles():
        user_profiles = {}
        knowledge_base_path = Path("./data_connection/knowledge_base.json")
        if knowledge_base_path.exists():
            with open(knowledge_base_path, "r") as f:
                user_profiles = json.load(f)
        return user_profiles
    print(run('AAPL', load_user_profiles()))
