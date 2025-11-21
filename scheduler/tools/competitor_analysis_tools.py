import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from langchain.tools import tool

@tool('Analyze competitors for a given stock')
def get_competitor_analysis(main_ticker: str, comp_ticker: str, years: int):
    '''
    Conduct an analysis of a stock and its competitors
    
    Parameter:
    - main_ticker: Specify the ticker of the main stock
    - comp_ticker: The ticker symbol of a competing stock of the main stock
    - years: The stock price data of the two stocks years ago starting from this moment
        
    For examples: 'AAPL', 'BABA', 2
    '''
    from config_loader import CLAUDE_OPUS, CLAUDE_API_KEY, BASE_URL
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage
    from datetime import datetime
    from datetime import datetime, timedelta
    import yfinance as yf
    
    llm = ChatOpenAI(
        base_url=BASE_URL,
        temperature=0.7,
        model=CLAUDE_OPUS,
        api_key=CLAUDE_API_KEY,  # type: ignore
    )
    
    def get_stock_data(ticker, years):
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=years*365)

        stock = yf.Ticker(ticker)

        # Retrieve historical price data
        hist_data = stock.history(start=start_date, end=end_date)

        # Retrieve balance sheet
        balance_sheet = stock.balance_sheet

        # Retrieve financial statements
        financials = stock.financials

        # Retrieve news articles
        news = stock.news

        return hist_data, balance_sheet, financials, news
    
    def compare_companies(main_ticker, comp_ticker, years):
        main_hist_data, main_balance_sheet, main_financials, main_news = get_stock_data(
                    main_ticker, years)
        comp_hist_data, comp_balance_sheet, comp_financials, comp_news = get_stock_data(
                    comp_ticker, years)
        
        main_data = {
                    'hist_data': main_hist_data,
                    'balance_sheet': main_balance_sheet,
                    'financials': main_financials,
                    'news': main_news
                }
        comp_data = {
                    'hist_data': comp_hist_data,
                    'balance_sheet': comp_balance_sheet,
                    'financials': comp_financials,
                    'news': comp_news
                }
        response = [
            SystemMessage(
                content=f"""
                    You are a financial analyst assistant. Compare the data of {main_ticker} against {
                    comp_ticker} and provide a detailed comparison, like a world-class analyst would. Be measured and discerning. Truly think about the positives and negatives of each company. Be sure of your analysis. You are a skeptical investor.
                    """
            ),
            HumanMessage(
                content=f"""
                    Data for {main_ticker}:\n\nHistorical price data:\n{main_data['hist_data'].tail().to_string()}\n\nBalance Sheet:\n{main_data['balance_sheet'].to_string()}\n\nFinancial Statements:\n{main_data['financials'].to_string()}\n\n----\n\nData for {comp_ticker}:\n\nHistorical price data:\n{
                    comp_data['hist_data'].tail().to_string()}\n\nBalance Sheet:\n{comp_data['balance_sheet'].to_string()}\n\nFinancial Statements:\n{comp_data['financials'].to_string()}\n\n----\n\nNow, provide a detailed comparison of {main_ticker} against {comp_ticker}. Explain your thinking very clearly.
                    """
            ),
        ]
        response_text = llm.invoke(response).content
        return response_text
    
    return compare_companies(main_ticker, comp_ticker, years)


def tools():
    return [get_competitor_analysis]


if __name__ == '__main__':
    print(get_competitor_analysis('AAPL', 'BABA', 2))