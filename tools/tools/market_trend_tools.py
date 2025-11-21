import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler.marketmover import stockanalysisMarketMover
from langchain.tools import tool
from typing import List
import asyncio

@tool('Crawl market trend')
def get_market_trend(types: List[str], timeframe: str=''):
    '''
    Here is the function to get market trends, you need to choose two parameters, the first one is the type of market trend, and the second one is the time range (not all first parameters require this):

    First parameter 'types', you can choose one or more of the following options that interest you:
        - 'indexes': Benchmarks for market performance, like S&P 500 or NASDAQ.
        - 'most-active': The stocks or funds with the highest trading volume (measured by number of shares traded) during the current trading session.
        - 'gainers': The stocks or funds with the highest percentage gain during the current trading session.
        - 'losers': The stocks or funds with the highest percentage decline during the current trading session.
        - 'active today': Stocks with high trading volume and notable price movements on the current day.
        - 'premarket gainers': stocks rising in value before the market opens.
        - 'premarket losers': stocks declining in value before the market opens.
        - 'after hours gainers': Stocks up in price after the market closes.
        - 'after hours losers': Stocks down in price after the market closes.
    
    Second parameter 'timeframe' is the time range, which is required only when your first parameter choice list contains "gainers" or "losers":
        - 'now': Get gainers or losers data for the current moment.
        - 'today': Get the gainers or losers data for today.
        - 'week': Get the gainers or losers data for this week.
        - 'month': Get the gainers or losers data for this month.
        - 'ytd': Get the gainers or losers data for year to date (YTD).
        - 'year': Get the gainers or losers data for this year.
        - '3 years': Get the gainers or losers data for 3 years.
        - '5 years' Get the gainers or losers data for 5 years.
        
    For examples: types=[gainers], timeframe='ytd'
                  types=[gainers, currencies, premarket losers], timeframe='now'
                  types=[active today, premarket gainers]
    
    Note that the first parameter must be in the form of a list.
    '''
    return asyncio.run(stockanalysisMarketMover.main(types, timeframe))


def tools():
    return [get_market_trend]


# if __name__ == '__main__':
#     types = ["gainers", "losers", "active today", "premarket gainers", "premarket losers", "after hours gainers", "after hours losers",
#              "indexes", "most-active", "climate-leaders", "cryptocurrencies", "currencies", "most-followed"]
#     types = ["gainers", "losers", "indexes"]
#     timeframe = 'now'
#     print(get_market_trend(types=types, timeframe=timeframe))
