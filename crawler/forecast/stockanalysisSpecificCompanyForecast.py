import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
'''
    从 stockanalysis.com 下载指定股票的各种预测和评级。
'''
from data_connection.mongodb import AsyncMongoConnection
from proxy_pool.usable_ip import Usable_IP
from fake_useragent import UserAgent
from lxml import etree
import pandas as pd
import asyncio

class StockAnalysis_Specific_Company_Forecast(Usable_IP):
    def __init__(self, ticker, args={}):
        super().__init__(args)
        self.ticker = ticker
        self.db_connection = AsyncMongoConnection('Forecast')
        self.source = "stockanalysis.com"
        self.headers = {
            'authority': 'stockanalysis.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            # 'cache-control': 'max-age=0',
            # 'if-none-match': 'W/"1ov6wil"',
            'sec-ch-ua': '"Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': UserAgent().random
        }

    async def download(self):
        try:
            url = "https://stockanalysis.com/stocks/" + self.ticker + "/forecast/"
            text = await self.request_get(url=url, headers=self.headers)
            html = etree.HTML(text, parser=None)  # type: ignore
        except Exception as e:
            return f"Request error: {e}"
        stockPriceForecast_text = html.xpath(
            '//*[@id="main"]/div[2]/div[2]/div[1]/div/div[1]/div[1]/p/text()')[0]
        pricePredictionRange_column = html.xpath(
            '//*[@id="main"]/div[2]/div[2]/div[1]/div/div[2]//table/thead/tr//text()')
        pricePredictionRange_table = html.xpath(
            '//*[@id="main"]/div[2]/div[2]/div[1]/div//table/tbody//text()')
        pricePredictionRange = await self.create_dataframe(
            pricePredictionRange_column, pricePredictionRange_table)
        stockPriceForecast = {"Stock Price Forecast": stockPriceForecast_text,
                              "Price Prediction Range": pricePredictionRange.to_dict(orient='records')}
        analystRatings_text = html.xpath(
            '//*[@id="main"]/div[2]/div[2]/div[2]/div[1]/div/p/text()')[0]
        analystRecommendationTrends_column = html.xpath(
            '//*[@id="main"]/div[2]/div[2]/div[2]/div[2]/div[3]/table/thead/tr//text()')
        analystRecommendationTrends_tbody = html.xpath(
            '//*[@id="main"]/div[2]/div[2]/div[2]/div[2]/div[3]/table/tbody//text()')
        analystRecommendationTrends = await self.create_dataframe(
            analystRecommendationTrends_column, analystRecommendationTrends_tbody)
        recommendationTrends = {"Analyst Ratings": analystRatings_text,
                                "Recommendation Trends": analystRecommendationTrends.to_json(orient='records')}
        financialForecast_column = html.xpath(
            '//*[@id="main"]/div[2]/div[2]/div[4]/div[3]/table/thead/tr//text()')
        financialForecast_tbody = html.xpath(
            '//*[@id="main"]/div[2]/div[2]/div[4]/div[3]/table/tbody//text()')
        financialForecast = await self.create_dataframe(
            financialForecast_column, financialForecast_tbody)
        revenueForecast_column = html.xpath(
            '//*[@id="main"]/div[2]/div[2]/div[5]/div[1]/div/div[2]/table/thead/tr//text()')
        revenueForecast_tbody = html.xpath(
            '//*[@id="main"]/div[2]/div[2]/div[5]/div[1]/div/div[2]/table/tbody//text()')
        revenueForecastRange = await self.create_dataframe(
            revenueForecast_column, revenueForecast_tbody)
        revenueGrowthForecastRange_column = html.xpath(
            '//*[@id="main"]/div[2]/div[2]/div[5]/div[2]/div/div[2]/table/thead/tr//text()')
        revenueGrowthForecastRange_tbody = html.xpath(
            '//*[@id="main"]/div[2]/div[2]/div[5]/div[2]/div/div[2]/table/tbody//text()')
        revenueGrowthForecastRange = await self.create_dataframe(
            revenueGrowthForecastRange_column, revenueGrowthForecastRange_tbody)
        EPSForecastRange_column = html.xpath(
            '//*[@id="main"]/div[2]/div[2]/div[5]/div[3]/div/div[2]/table/thead/tr//text()')
        EPSForecastRange_tbody = html.xpath(
            '//*[@id="main"]/div[2]/div[2]/div[5]/div[3]/div/div[2]/table/tbody//text()')
        EPSForecastRange = await self.create_dataframe(
            EPSForecastRange_column, EPSForecastRange_tbody)
        EPSGrowthForecastRange_column = html.xpath(
            '//*[@id="main"]/div[2]/div[2]/div[5]/div[4]/div/div[2]/table/thead/tr//text()')
        EPSGrowthForecastRange_tbody = html.xpath(
            '//*[@id="main"]/div[2]/div[2]/div[5]/div[4]/div/div[2]/table/tbody//text()')
        EPSGrowthForecastRange = await self.create_dataframe(
            EPSGrowthForecastRange_column, EPSGrowthForecastRange_tbody)
        data = {
            "Stock Price Forecast": stockPriceForecast,
            "Recommendation Trends": recommendationTrends,
            "Financial Forecast": financialForecast.to_dict(orient='records'),
            "Revenue Forecast Range": revenueForecastRange.to_dict(orient='records'),
            "Revenue Growth Forecast Range": revenueGrowthForecastRange.to_dict(orient='records'),
            "EPS Forecast Range": EPSForecastRange.to_dict(orient='records'),
            "EPS Growth Forecast Range": EPSGrowthForecastRange.to_dict(orient='records'),
        }
        await self.db_connection.save_data(self.ticker, self.source, data)
        return data

    async def create_dataframe(self, column_names, values):
        column_name = [
            element for element in column_names if element.strip() != '']
        value = [element for element in values if element.strip() != '']
        rows = len(value) // len(column_name)
        if len(value) % len(column_name) != 0:
            rows += 1
        reshaped_values = [value[i:i + len(column_name)]
                           for i in range(0, len(value), len(column_name))]
        df = pd.DataFrame(reshaped_values, columns=column_name)
        return df
    
async def main():
    from config import config
    c = StockAnalysis_Specific_Company_Forecast('TSLA', args=config)
    result = await c.download()
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
