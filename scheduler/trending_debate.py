import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import io
import os
import base64
from PIL import Image
from langchain_anthropic import ChatAnthropic
from playwright.sync_api import sync_playwright
from config_loader import (
    CLAUDE_API_KEY,
    CLAUDE_OPUS,
    CLAUDE_HAIKU,
    OPENAI_API_KEY,
    GPT4O,
)

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

    def behavior_analyze(self, ticker, image_data, user_knowledge, area="美国"):
        # system_message = dedent(f'''
        #             As a skilled stock behavior analyst, given the price chart of {ticker}, please analyze in detail based on the user's financial background:
        #             {''.join(user_knowledge)}
        #             Provide 'buy', 'sell', or 'hold' recommendations for the chart and explain your reasons (need to explain which features of the user lead to your choice), also please provide your confidence level (represented as a numerical value, such as 74%).
        #         ''')
        # user_prompt = dedent(f"""
        #         When making predictions, please comprehensively consider the behavioral factors (psychological factors) behind the trends. Analyze price movements and patterns from the perspective of behavioral finance theory, considering how investor psychology influences the market.
        #         Please discuss the following points in detail:
        #         1. **Market Sentiment** - Evaluate the current market sentiment as bullish, bearish, or neutral based on recent price movements. Consider how this sentiment drives trends.
        #         2. **Investor Emotion** - Look for signs of investor emotions such as fear, greed, optimism, and pessimism in chart patterns. Discuss how these emotions influence buying and selling decisions.
        #         3. **Herding Behavior** - Identify if price movements exhibit herding behavior, where many investors follow the crowd. Explain how this psychological factor fuels trends.
        #         4. **Anchoring Bias** - Consider if investors are anchoring their value perception to key price levels. Discuss how this bias affects support and resistance levels.
        #         5. **Overreaction and Underreaction** - Analyze if the market overreacts or underreacts to certain events or information. Explain how these behavioral tendencies impact price movements.
        #         6. **Loss Aversion** - Assess investors' attitudes towards potential losses and how this psychological tendency affects their risk tolerance and trading decisions.
        #         7. **Mental Accounting** - Consider how investors mentally segregate their portfolios into different "accounts" and discuss how this mental mechanism influences their asset allocation decisions.
        #         8. **Information Bias** - Analyze how investors interpret and react to market information and how this bias leads to irrational decisions.
        #         9. **Emotional Fluctuations** - Evaluate changes in investor emotions over time and how these fluctuations affect market trends and volatility.
        #         10. **Group Behavior** - Observe collective behavior patterns of investor groups, such as collective mania or panic, and discuss how these behaviors amplify market trends.
        #         Please integrate these behavioral finance concepts to conduct an in-depth analysis of the chart, revealing the connection between investor psychological factors and price movements. Based on the analysis, provide clear trading recommendations and explain your reasoning process.
        #         Today is {datetime.date.today()}.
        #     """)

        client_1 = ChatAnthropic(model_name=CLAUDE_HAIKU, api_key=CLAUDE_API_KEY, temperature=0, timeout=10)
        # messages = [
        #     SystemMessage(content=system_message),
        #     HumanMessage(
        #         content=[
        #             {
        #                 "type": "image_url",
        #                 "image_url": {
        #                     # langchain logo
        #                     "url": f"data:image/png;base64,{image_data}",  # noqa: E501
        #                 },
        #             },
        #                 {"type": "text", "text": user_prompt},
        #             ]
        #         )
        #     ]
        return client_1
    
    def technical_analyze(self, ticker, image_data, user_knowledge, selected_indicators, area="美国"):
        # system_message = dedent(f'''
        #         As a skilled stock and technical analyst, providing price charts of {ticker}, please analyze in detail based on the user's financial background:
        #         {''.join(user_knowledge)}
        #         Provide 'buy', 'sell', or 'hold' recommendations for the chart and explain your reasons (need to explain what features of the user lead to your choice), also please provide your confidence level (represented as a numerical value, such as 74%).
        #         ''')
        # user_prompt = dedent(f"""
        #         Please pay attention to the following points in your analysis:
        #         1. **Overall Trend** - Determine if the price is in an uptrend, downtrend, or consolidating state based on whether higher highs and higher lows (uptrend) or lower highs and lower lows (downtrend) are occurring.
        #         2. **Support and Resistance Levels** - Identify key price levels where the price has previously encountered resistance or struggled to break through. These are potential decision-making areas for future price movements.
        #         3. **Indicators** - Using the provided indicators: {selected_indicators}, observe the indicator curves on the chart and explain the significance of each indicator's trend to supplement the price action analysis.
        #         4. **Price Patterns** - Analyze whether there are any recognizable bullish or bearish price patterns on the chart, such as head and shoulders, triangles, wedges, flags, double tops/bottoms, etc.
        #         Today is {datetime.date.today()}.
                
        #         Additionally, you need to conduct trendline analysis—identify the breakout of a descending trendline as a buying signal or the break below an ascending trendline as a selling signal. A reliable trendline should meet the following criteria:
        #         1. It should connect at least three local endpoints. Connecting at least three points indicates that the stock price has encountered resistance at the trendline at least three times in the past, suggesting that the stock price is likely to continue rising.
        #         2. The more endpoints the trendline can connect, the more reliable it is. This indicates a stronger collective consensus in the market.
        #         3. The trendline should span at least three weeks.
        #         4. The slope of the trendline should be relatively flat. When the stock price breaks through a relatively flat trendline, there is a high probability that the upward trend will resume. If the slope is too steep, it indicates that downward pressure is still strong. Even if there is a breakout, it is often just a temporary halt in the decline rather than the start of an upward trend.
        #         5. The breakout should ideally be supported by high trading volume.
        #     """)

        client_2 = ChatAnthropic(model_name=CLAUDE_HAIKU, api_key=CLAUDE_API_KEY, temperature=0, timeout=10)
        # messages = [
        #     SystemMessage(content=system_message),
        #     HumanMessage(
        #         content=[
        #             {
        #                 "type": "image_url",
        #                 "image_url": {
        #                     # langchain logo
        #                     "url": f"data:image/png;base64,{image_data}",  # noqa: E501
        #                 },
        #             },
        #                 {"type": "text", "text": user_prompt},
        #             ]
        #         )
        #     ]
        return client_2


def main(ticker, user_knowledge):
    analyzer = StockAnalyzer()
    # ticker = input('请输入您想预测公司的股票代码:')
    # selected_indicators = input('请输入您想分析的金融指标（最多三项，用‘,’分离）:') # ['MACD', 'RSI', 'Moving Average']
    # selected_indicators = selected_indicators.split(',') or selected_indicators.split('，')
    selected_indicators = ['MACD', 'RSI']
    if os.path.exists(f"test_{ticker}.png"):
        pass
    else:
        with sync_playwright() as p:
            analyzer.us_stock_capture(p, ticker, selected_indicators)
    image1_path = f"test_{ticker}.png"
    with open(image1_path, "rb") as image_file:
        img = Image.open(image_file)
        # 将图片转换为 base64 编码的数据
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        image_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
    client_1 = analyzer.behavior_analyze(ticker, image_data, selected_indicators, user_knowledge)
    client_2 = analyzer.technical_analyze(ticker, image_data, selected_indicators, user_knowledge)
    
    return client_1, client_2, image_data

def run(ticker, user_knowledge):
    return main(ticker, user_knowledge)

if __name__ == "__main__":
    user_knowledge = []
    print(run('BABA', user_knowledge)) 
