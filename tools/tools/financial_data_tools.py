import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crawler.incomestatement import stockanalysisSpecificCompanyIncomeStatement
from crawler.balancesheet import stockanalysisSpecificCompanyBalanceSheet
from crawler.cashflowstatement import stockanalysisSpecificCompanyCashFlowStatement
from crawler.revenue import stockanalysisSpecificCompanyRevenue
from langchain_community.tools.polygon.financials import PolygonFinancials
from langchain_community.tools.polygon.last_quote import PolygonLastQuote
from langchain_community.utilities.polygon import PolygonAPIWrapper
from langchain.tools import tool
import asyncio


@tool('Scrape_income_statement')
def get_income_statement(ticker: str):
    '''
    Extract cash flow statement data of a specific stock in recent years.

    Parameters:
        - ticker (str): The ticker symbol of specific company stock.
    For example: 'AAPL'.
    '''
    return asyncio.run(stockanalysisSpecificCompanyIncomeStatement.main(ticker))

@tool('Scrape_balance_sheet')
def get_balance_sheet(ticker: str):
    '''
    Extract balance sheet data of a specific stock in recent years.

    Parameters:
        - ticker (str): The ticker symbol of specific company stock.
    For example: 'AAPL'.
    '''
    return asyncio.run(stockanalysisSpecificCompanyBalanceSheet.main(ticker))

@tool('Scrape_cash_flow_statement')
def get_cash_flow_statement(ticker: str):
    '''
    Extract cash flow statement data of a specific stock in recent years.

    Parameters:
        - ticker (str): The ticker symbol of specific company stock.
    For example: 'AAPL'.
    '''
    return asyncio.run(stockanalysisSpecificCompanyCashFlowStatement.main(ticker))

@tool('Scrape_revenue')
def get_revenue(ticker: str):
    '''
    Extract revenue data of a specific stock in recent years.

    Parameters:
        - ticker (str): The ticker symbol of specific company stock.
    For example: 'AAPL'.
    '''
    return stockanalysisSpecificCompanyRevenue.main(ticker)

@tool('Scrape_latest_quote')
def get_latest_quote(ticker: str):
    '''
    Extract latest quote data of a specific stock in recent years.

    Parameters:
        - ticker (str): The ticker symbol of specific company stock.
    For example: 'AAPL'.
    '''
    api_wrapper = PolygonAPIWrapper()
    last_quote_tool = PolygonLastQuote(api_wrapper=api_wrapper)
    last_quote = last_quote_tool.run(ticker)
    return last_quote


def tools():
    return [get_income_statement, get_balance_sheet, get_cash_flow_statement, get_revenue, get_latest_quote]

if __name__ == '__main__':
    print(get_income_statement('AAPL'))
