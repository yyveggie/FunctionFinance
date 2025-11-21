import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import pandas as pd
import asyncio
from crawler import datetime_utils
from crawler.news import blockbeatBlockchainNews
from crawler.news import cctvNews
from crawler.news import finnhubNews
from crawler.news import cnbcSpecificKeywordNews
from crawler.news import eastmoneySpecificCompanyNews
from crawler.news import finnhubSpecificCompanyNews
from crawler.news import gurufocusSpecificCompanyNews
from crawler.news import marketwatchSpecificKeywordNews
from crawler.news import mxnzpNews
from crawler.news import newsminimalistNews
from crawler.news import seekingalphaSpecificCompanyNews
from crawler.news import sinafinanceNews
from crawler.news import stockanalysisSpecificCompanyNews
from crawler.news import talkmarketsSpecificKeywordNews
from crawler.news import yahooSpecificCompanyNews
from crawler.news import yicaiSpecificKeywordNews
from crawler.news import xueqiuSpecificKeywordNews

def read_stock():
    file_path = "s&p100.xlsx"
    df = pd.read_excel(file_path)
    column_names = df.columns.tolist()
    data = {}
    for column in column_names:
        column_data = df[column].tolist()
        data[f'{column}'] = column_data
    print("读取股票数据完成")
    return data

def scrape_news():
    # public news
    blockbeatBlockchainNews.main()
    print("blockbeatBlockchainNews 爬取完成")
    
    cctvNews.main(datetime_utils.yyyymmdd())
    print("cctvNews 爬取完成")
    
    gurufocusSpecificCompanyNews.main()
    print("gurufocusSpecificCompanyNews 爬取完成")
    
    mxnzpNews.main()
    print("mxnzpNews 爬取完成")
    
    asyncio.run(newsminimalistNews.main())
    print("newsminimalistNews 爬取完成")
    
    asyncio.run(sinafinanceNews.main(datetime_utils.yyyymmdd()))
    print("sinafinanceNews 爬取完成")
    
    finnhubNews.main()
    print("finnhubNews 爬取完成")
    
    data = read_stock()
    for index, (ticker, keyword) in enumerate(zip(data['TICKER'], data['KEYWORD'])):
        asyncio.run(cnbcSpecificKeywordNews.main(keyword))
        print(f"cnbcSpecificKeywordNews 爬取完成, 关键词: {keyword}")
        
        eastmoneySpecificCompanyNews.main(ticker)
        print(f"eastmoneySpecificCompanyNews 爬取完成, 股票代码: {ticker}")
        
        finnhubSpecificCompanyNews.main(ticker)
        print(f"finnhubSpecificCompanyNews 爬取完成, 股票代码: {ticker}")
        
        marketwatchSpecificKeywordNews.main(keyword)
        print(f"marketwatchSpecificKeywordNews 爬取完成, 关键词: {keyword}")
        
        asyncio.run(seekingalphaSpecificCompanyNews.main(ticker))
        print(f"seekingalphaSpecificCompanyNews 爬取完成, 股票代码: {ticker}")
        
        stockanalysisSpecificCompanyNews.main(ticker)
        print(f"stockanalysisSpecificCompanyNews 爬取完成, 股票代码: {ticker}")
        
        talkmarketsSpecificKeywordNews.main(ticker)
        print(f"talkmarketsSpecificKeywordNews 爬取完成, 股票代码: {ticker}")
        
        yahooSpecificCompanyNews.main(ticker)
        print(f"yahooSpecificCompanyNews 爬取完成, 股票代码: {ticker}")
        
        asyncio.run(yicaiSpecificKeywordNews.main(keyword))
        print(f"yicaiSpecificKeywordNews 爬取完成, 关键词: {keyword}")
        
        asyncio.run(xueqiuSpecificKeywordNews.main(keyword))
        print(f"xueqiuSpecificKeywordNews 爬取完成, 关键词: {keyword}")

if __name__ == '__main__':
    scrape_news()