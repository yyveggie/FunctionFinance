import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler.comment import redditSpecificKeywordComment
from langchain.tools import tool

@tool('Crawl comments on reddit')
def get_reddit_comments(subreddit: str):
    '''
    Useful to crawl hottest posts and it's comments with specific subreddit on reddit.

    Parameter:
        - subreddit (str): The subreddit name on Reddit, you should chose one from the below list
            (Or you can fill in the company you think exists):
            ['Finance', 'Stocks', 'Bitcoin', 'SecurityAnalysis', 'Wallstreetbetsnew', 'StocksAndTrading', 
            'PennystocksDD', 'PennyStocks', 'algotrading', 'babystreetbets', 'Economics', 'ASX_Bets', 
            'antstreetbets', 'quant', 'weedstocks', 'investing', 'Economy', 'shortinterestbets', 'thetagang', 
            'Pennystocks', 'InvestingRetards', 'wallstreetbet', 'wallstreetbetsoptions', 'econmonitor', 
            'Wallstreetwarrior', 'StockMarket', 'Dividends', 'wallstreetbets2', 'Trading', 'WSBAfterHours', 
            'smallstreetbets', 'retardbets', 'finance', 'InvestmentClub', 'stocks', 'IndianStreetBets', 
            'wallstreetsidebets', 'Stock_Picks', 'baystreetbets', 'ameisenstrassenwetten', 'wallstreetbets_', 
            'ISKbets', 'quantfinance', 'stonks', 'GlobalMarkets', 'Investing', 'Daytrading', 'WallStreetbetsELITE', 
            'RobinHoodPennyStocks', 'DayTrading', 'CanadianInvestor', 'pennystocks', 'Options', 'AlgoTrading', 
            'MoonBets', 'algorithmictrading', 'farialimabets', 'Wallstreetsilver', 'wallstreetbets', 'Cryptocurrency', 
            'UKInvesting', 'ausstocks', 'WallStreetBets', 'dividends']
    For example: 'Stocks'
    '''
    return redditSpecificKeywordComment.main(subreddit)


def tools():
    return [get_reddit_comments]


if __name__ == '__main__':
    print(get_reddit_comments('Stocks'))


