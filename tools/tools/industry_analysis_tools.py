import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from langchain.tools import tool


@tool('Analysis main stock of specific industry')
def get_industry_analysis(industry: str):
    '''
    Analyze sentiment analysis, expert recommendation index, trends, growth prospects, regulatory changes, and competitive landscape of major stocks in specific industries or sectors.
    Based on the above analysis results, the stock recommendation rankings and reasons for the current industry are finally returned.
    
    Parameter:
    - industry: The specific industry or sector you want to analyze
        
    For examples: 'energy'
    '''
    from config_loader import CLAUDE_OPUS, CLAUDE_API_KEY, BASE_URL
    import json
    import ast
    import requests
    from langchain_openai import ChatOpenAI
    from bs4 import BeautifulSoup
    from langchain_core.messages import HumanMessage, SystemMessage
    from datetime import datetime
    import yfinance as yf
    
    llm = ChatOpenAI(
        base_url=BASE_URL,
        temperature=0.7,
        model=CLAUDE_OPUS,
        api_key=CLAUDE_API_KEY,  # type: ignore
        streaming=True,
    )
    
    def get_article_text(url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            article_text = ' '.join([p.get_text() for p in soup.find_all('p')])
            return article_text
        except:
            return "Error retrieving article text."


    def get_stock_news(ticker):
        stock = yf.Ticker(ticker)
        news = stock.news
        return news


    def get_sentiment_analysis(ticker, news):
        news_text = ""
        for article in news:
            article_text = get_article_text(article['link'])
            timestamp = datetime.fromtimestamp(
                article['providerPublishTime']).strftime("%Y-%m-%d")
            news_text += f"\n\n---\n\nDate: {timestamp}\nTitle: {article['title']}\nText: {article_text}"
        response = [
            SystemMessage(
                content=f"""
                    ou are a sentiment analysis assistant. Analyze the sentiment of the given news articles for {
                    ticker} and provide a summary of the overall sentiment and any notable changes over time. Be measured and discerning. You are a skeptical investor.
                    """
            ),
            HumanMessage(
                content=f"""
                    News articles for {ticker}:\n{news_text}\n\n----\n\nProvide a summary of the overall sentiment and any notable changes over time.
                    """
            ),
        ]
        response_text = llm.invoke(response).content
        return response_text


    def get_analyst_ratings(ticker):
        stock = yf.Ticker(ticker)
        recommendations = stock.recommendations
        if recommendations is None or recommendations.empty:
            return "No analyst ratings available."

        latest_rating = recommendations.iloc[-1]

        firm = latest_rating.get('Firm', 'N/A')
        to_grade = latest_rating.get('To Grade', 'N/A')
        action = latest_rating.get('Action', 'N/A')

        rating_summary = f"Latest analyst rating for {ticker}:\nFirm: {firm}\nTo Grade: {to_grade}\nAction: {action}"

        return rating_summary


    def get_industry_analysis(ticker):
        # update to use search to find recent data!!
        stock = yf.Ticker(ticker)
        industry = stock.info['industry']
        sector = stock.info['sector']
        response = [
            SystemMessage(
                content=f"""
                    You are an industry analysis assistant. Provide an analysis of the {industry} industry and {
                    sector} sector, including trends, growth prospects, regulatory changes, and competitive landscape. Be measured and discerning. Truly think about the positives and negatives of the stock. Be sure of your analysis. You are a skeptical investor.
                    """
            ),
            HumanMessage(
                content=f"""
                    Provide an analysis of the {industry} industry and {sector} sector.
                    """
            ),
        ]
        response_text = llm.invoke(response).content
        return response_text


    def get_final_analysis(ticker, comparisons, sentiment_analysis, analyst_ratings, industry_analysis):
        response = [
            SystemMessage(
                content=f"""
                    You are a financial analyst providing a final investment recommendation for {
                    ticker} based on the given data and analyses. Be measured and discerning. Truly think about the positives and negatives of the stock. Be sure of your analysis. You are a skeptical investor.
                    """
            ),
            HumanMessage(
                content=f"""
                    Ticker: {ticker}\n\nComparative Analysis:\n{json.dumps(comparisons, indent=2)}\n\nSentiment Analysis:\n{sentiment_analysis}\n\nAnalyst Ratings:\n{analyst_ratings}\n\nIndustry Analysis:\n{industry_analysis}\n\nBased on the provided data and analyses, please provide a comprehensive investment analysis and recommendation for {
                    ticker}. Consider the company's financial strength, growth prospects, competitive position, and potential risks. Provide a clear and concise recommendation on whether to buy, hold, or sell the stock, along with supporting rationale.
                    """
            ),
        ]
        response_text = llm.invoke(response).content
        return response_text


    def generate_ticker_ideas(query):
        response = [
            SystemMessage(
                content=f"""
                    You are a Wall Street professional financial analyst. You will receive an inquiry from a high-level VIP client, from which you need to identify the relevant industry or sector. Then, generate a list of 5 ticker symbols for major companies in this industry or sector, as a Python-parsable list.
                    """
            ),
            HumanMessage(
                content=f"""
                    Here is my query. Please provide a list of 5 ticker symbols for major companies in the industry or sector related to my query as a Python-parsable list. Only respond with the list, no other text.
                    
                    query: {query}
                    """
            ),
        ]
        response_text = llm.invoke(response).content
        ticker_list = ast.literal_eval(response_text)
        return [ticker.strip() for ticker in ticker_list]


    def get_current_price(ticker):
        stock = yf.Ticker(ticker)
        data = stock.history(period='1d', interval='1m')
        return data['Close'].iloc[-1]


    def rank_companies(industry, analyses, prices):
        analysis_text = "\n\n".join(
            f"Ticker: {ticker}\nCurrent Price: {prices.get(ticker, 'N/A')}\nAnalysis:\n{analysis}"
            for ticker, analysis in analyses.items()
        )

        response = [
            SystemMessage(
                content=f"""
                    You are a financial analyst providing a ranking of companies in the {
                    industry} industry based on their investment potential. Be discerning and sharp. Truly think about whether a stock is valuable or not. You are a skeptical investor.
                    """
            ),
            HumanMessage(
                content=f"""
                    Industry: {industry}\n\nCompany Analyses:\n{
                    analysis_text}\n\nBased on the provided analyses, please rank the companies from most attractive to least attractive for investment. Provide a brief rationale for your ranking. In each rationale, include the current price (if available) and a price target.
                    """
            ),
        ]
        response_text = llm.invoke(response).content

        return response_text
    

    # Generate ticker ideas for the industry
    tickers = generate_ticker_ideas(industry)
    print(f"\nTicker Ideas for {industry} Industry:")
    print(", ".join(tickers))

    # Perform analysis for each company
    analyses = {}
    prices = {}
    for ticker in tickers:
        try:
            print(f"\nAnalyzing {ticker}...")
            news = get_stock_news(ticker)
            sentiment_analysis = get_sentiment_analysis(ticker, news)
            analyst_ratings = get_analyst_ratings(ticker)
            industry_analysis = get_industry_analysis(ticker)
            final_analysis = get_final_analysis(ticker, {}, sentiment_analysis, analyst_ratings, industry_analysis)
            analyses[ticker] = final_analysis
            prices[ticker] = get_current_price(ticker)
        except:
            pass

    # Rank the companies based on their analyses
    ranking = rank_companies(industry, analyses, prices)
    return ranking


def tools():
    return [get_industry_analysis]

