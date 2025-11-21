import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler.earningscall import discountingcashflowsSpecificCompanyEarningsCall
from langchain.tools import tool
import asyncio

@tool('Scrape_Company_Earningscall')
def get_earnings_call(ticker: str, year: str, quarter: str):
    '''
    Useful to scrape earnings call of specific company you are interested in.

    Parameters:
        - ticker (str): The ticker symbol of the company's stock.
        - year (str): The year of earnings call.
        - quarter (str): The quarter of earnings call.
    For example, 'AAPL', '2023', 'Q4'
    '''
    results = asyncio.run(discountingcashflowsSpecificCompanyEarningsCall.main(ticker, year, quarter))
    return results

def tools():
    return [get_earnings_call]

if __name__ == '__main__':
    all_filtered_data = get_earnings_call(ticker='AAPL', year='2023', quarter='Q4')
    print(all_filtered_data)
