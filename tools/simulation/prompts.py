from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from langchain.output_parsers import PydanticOutputParser

# 定义 Pydantic 数据模型
class Decision(BaseModel):
    action: str = Field(description="The investment action (buy, sell, hold)")
    confidence: float = Field(description="The confidence level of the decision")
    explanation: str = Field(description="A brief explanation of the decision")

    @validator('action')
    def check_action(cls, value):
        if value not in {"buy", "sell", "hold"}:
            raise ValueError("Action must be one of 'buy', 'sell', or 'hold'")
        return value

parser = PydanticOutputParser(pydantic_object=Decision)

def prompt_generate(day, ordinary_investors_decision=None, institutional_decision=None):
    _INSTITUTIONAL_INVESTOR_PROMPT = '''
    You are an institutional investor currently considering whether to buy, sell, or hold a {stock} stock. Based on the following information, and your investment experience and strategy, make a decision:

    1.Your current psychological state is: {Institutional_behavioral_psychology}. This will influence your risk preference and decision-making to a certain extent.
    2.The stock's price movement over the past ten days is: {ten_day_price}.
    3.The stock's trading volume changes over the past ten days are: {ten_day_trading_volume}.
    4.Latest news about this stock: {news}.
    5.Some important financial indicator data: {financial_indicator}.
    |ordinary_investors_decision_text|

    Please tell me, based on the above information, as an institutional investor, would you choose to buy, sell, or hold the stock today?.
    '''

    if ordinary_investors_decision:
        _INSTITUTIONAL_INVESTOR_PROMPT = _INSTITUTIONAL_INVESTOR_PROMPT.replace('|ordinary_investors_decision_text|', "6.Yesterday, the decisions of ordinary investors were: {ordinary_investors_decision}.")
    else:
        _INSTITUTIONAL_INVESTOR_PROMPT = _INSTITUTIONAL_INVESTOR_PROMPT.replace('|ordinary_investors_decision_text|', "{ordinary_investors_decision}")

    INSTITUTIONAL_INVESTOR_PROMPT = PromptTemplate(
        input_variables=[
            "stock", 
            "Institutional_behavioral_psychology",
            "ten_day_price",
            "ten_day_trading_volume",
            "news",
            "financial_indicator",
            "ordinary_investors_decision"
            ], 
        template=_INSTITUTIONAL_INVESTOR_PROMPT,
        # template="{format_instructions}\n" + _INSTITUTIONAL_INVESTOR_PROMPT,
        # partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    _INDIVIDUAL_INVESTOR_PROMPT = '''
    You are an ordinary individual investor considering whether to buy, sell, or hold a {stock} stock. Based on the following information and your investment experience, make a decision:

    1.Your current psychological state regarding the stock market is: {individual_behavioral_psychology}. This will affect your attitude towards risk and investment decisions.
    2.The price movement of the stock you hold over the past ten days is: {ten_day_price}.
    3.The stock's trading volume changes over the past ten days are: {ten_day_trading_volume}.
    4.Latest news about this stock: {news}.
    |ordinary_investors_decision_text|
    |institutional_decision_text|

    Please tell me, based on the above information, as a retail investor, do you plan to buy, sell, or hold this stock today?.
    '''

    if ordinary_investors_decision:
        _INDIVIDUAL_INVESTOR_PROMPT = _INDIVIDUAL_INVESTOR_PROMPT.replace('|ordinary_investors_decision_text|', "5.Yesterday, the decisions of other ordinary investors like you were: {ordinary_investors_decision}.")
    else:
        _INDIVIDUAL_INVESTOR_PROMPT = _INDIVIDUAL_INVESTOR_PROMPT.replace('|ordinary_investors_decision_text|', "{ordinary_investors_decision}")
    
    if institutional_decision:
        _INDIVIDUAL_INVESTOR_PROMPT = _INDIVIDUAL_INVESTOR_PROMPT.replace('|institutional_decision_text|', "6.Yesterday, the decision of an institutional investor was: {institutional_decision}.")
    else:
        _INDIVIDUAL_INVESTOR_PROMPT = _INDIVIDUAL_INVESTOR_PROMPT.replace('|institutional_decision_text|', "{institutional_decision}")

    INDIVIDUAL_INVESTOR_PROMPT = PromptTemplate(
        input_variables=[
            "stock", 
            "individual_behavioral_psychology",
            "ten_day_price"
            "ten_day_trading_volume",
            "news",
            "ordinary_investors_decision",
            "institutional_decision"
        ],
        template=_INDIVIDUAL_INVESTOR_PROMPT,
        # template="{format_instructions}\n" + _INDIVIDUAL_INVESTOR_PROMPT,
        # partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    return INSTITUTIONAL_INVESTOR_PROMPT, INDIVIDUAL_INVESTOR_PROMPT, parser