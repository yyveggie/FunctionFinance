import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from phi.assistant.assistant import Assistant
from phi.llm.anthropic.claude import Claude
from phi.tools.yfinance import YFinanceTools
from config_loader import CLAUDE_API_KEY, CLAUDE_OPUS

assistant = Assistant(
    llm=Claude(model=CLAUDE_OPUS, api_key=CLAUDE_API_KEY),
    tools=[YFinanceTools(
        stock_price=True, 
        analyst_recommendations=True, 
        company_info=True, 
        company_news=True,
        stock_fundamentals=True,
        income_statements=True,
        key_financial_ratios=True,
        technical_indicators=True,
        )],
    show_tool_calls=True,
    markdown=True,
) # type: ignore

def run(query):
    result = assistant.run(query)
    return ''.join(list(result))

if __name__ == '__main__':
    query = "What is the stock price of NVDA"
    response = run(query)
    print(response)