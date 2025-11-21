import time
import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

from scheduler.simulation import market, prompts
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from config_loader import GROQ_API_KEY, GROQ_MIXTRAL_8x7B, GPT4O, OPENAI_API_KEY

market_data = market.MarketSimulationData()
stock = market_data.stock
institutional_behavioral_psychology = market_data.institutional_behavioral_psychology
individual_behavioral_psychology = market_data.individual_behavioral_psychology
twenty_day_price = market_data.twenty_day_price
twenty_day_trading_volume = market_data.twenty_day_trading_volume
news = market_data.news
financial_indicator = market_data.financial_indicator

# institutional_investors = ChatAnthropic(temperature=0, model_name=CLAUDE_OPUS, api_key=CLAUDE_API_KEY, timeout=5.0)
institutional_investors = ChatOpenAI(temperature=0.7, model=GPT4O, api_key=OPENAI_API_KEY)

num_days = 10

for day in range(num_days):
    # Get the data for the current day and the past 9 days
    start_index = day
    end_index = day + 10
    current_ten_day_price = ' '.join(twenty_day_price[start_index // 5: end_index // 5])
    current_ten_day_volume = ' '.join(twenty_day_trading_volume[start_index // 5: end_index // 5])
    
    # Get the latest 3 news articles
    current_news = ' '.join(news[day: day + 3])
    
    current_financial_indicator = financial_indicator[day]
    
    # Initialize variables for storing decisions
    institutional_decision = None
    ordinary_investors_decision = []
    
    # Generate the prompt for institutional investors
    INSTITUTIONAL_INVESTOR_PROMPT, _, parser = prompts.prompt_generate(day, ordinary_investors_decision=None)
    institutional_prompt = INSTITUTIONAL_INVESTOR_PROMPT.format(
        stock=stock,
        Institutional_behavioral_psychology=institutional_behavioral_psychology,
        ten_day_price=current_ten_day_price,
        ten_day_trading_volume=current_ten_day_volume,
        news=current_news,
        financial_indicator=current_financial_indicator,
        ordinary_investors_decision=ordinary_investors_decision,
    )

    # Get the decision from the institutional investor
    human = """
            Based on the information you have, reply with your decision (buy, sell or hold) and the corresponding confidence level, without any explanation. Output your response in json format:
            such as:
            {
                "decision": "buy",
                "confidence": 0.99
            }
        """
    prompt = ChatPromptTemplate.from_messages([("system", institutional_prompt)])
    chain = prompt | institutional_investors
    institutional_decision = chain.invoke(input={"human": human}).content
    
    print(f"Day {day + 1}:")
    print("Institutional Investor's Decision:")
    print(institutional_decision)
    
    # Generate the prompts for individual investors and get their decisions
    for _ in range(9):
        ordinary_investors = ChatGroq(temperature=0.7, model=GROQ_MIXTRAL_8x7B, api_key=GROQ_API_KEY)
        _, INDIVIDUAL_INVESTOR_PROMPT, parser = prompts.prompt_generate(day, ordinary_investors_decision=ordinary_investors_decision, institutional_decision=institutional_decision)
        individual_prompt = INDIVIDUAL_INVESTOR_PROMPT.format(
            stock=stock,
            individual_behavioral_psychology=individual_behavioral_psychology,
            ten_day_price=current_ten_day_price,
            ten_day_trading_volume=current_ten_day_volume,
            news=current_news,
            ordinary_investors_decision=ordinary_investors_decision,
            institutional_decision=institutional_decision
        )
        
        human = """
            Based on the information you have, reply with your decision (buy, sell or hold) and the corresponding confidence level, without any explanation. Output your response in json format:
            such as:
            {
                "decision": "buy",
                "confidence": 0.99
            }
        """
        prompt = ChatPromptTemplate.from_messages([("system", individual_prompt)])
        chain = prompt | ordinary_investors
        individual_decision = chain.invoke(input={"human": human}).content
        ordinary_investors_decision.append(individual_decision)
    
        print(f"Individual Investors No.{_}' Decisions:")
        print(individual_decision)
        print("----------------------------------------------------------------")
        
        time.sleep(4)