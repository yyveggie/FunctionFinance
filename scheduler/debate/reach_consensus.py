import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from scheduler.debate.twoai import TWOAI, AgentDetails 
from scheduler import trending_debate
from textwrap import dedent

class Consensus:
    def __init__(self, ticker, user_knowledge):
        self.ticker = ticker
        self.user_knowledge = user_knowledge
        
    def analyze(self):
        behavior_model, technical_model, image_data = trending_debate.run(self.ticker, self.user_knowledge)
        
        agent_details: AgentDetails = (
            {
                "name": "Behavioral Analyst",
                "objective": dedent("""
                You are a behavioral analyst. You use psychological analysis on the trend chart of a stock to predict the stock trend. 
                You use psychological knowledge to debate with a Technical Analyst to come up with the final analysis result (buy, sell, hold) and its confidence level for the same stock. 
                In each round of debate, your arguments are always concise (two or three sentences) and powerful. 
                And repeat "<DONE!>" ONLY if you both established and agreed that you came to the end of the discussion and reached a consensus.
                """),
                "user_prompt":"""
                Use behavioral psychology theories to analyze the chart, such as:
                Herding Behavior, Anchoring Bias, Overreaction and Underreaction, Loss Aversion, Mental Accounting, Information Bias, Emotional Fluctuations, Group Behavior
                """,
                "model": behavior_model, 
            },
            {   
                "name": "Technical Analyst",
                "objective": dedent("""
                You are a technical analyst. You use technical analysis on the trend chart of a stock to predict the stock trend. 
                You use technical analysis knowledge to debate with a Behavioral Analyst to come up with the final analysis result (buy, sell, hold) and its confidence level for the same stock. 
                In each round of debate, your arguments are always concise (two or three sentences) and powerful. 
                And repeat "<DONE!>" ONLY if you both established and agreed that you came to the end of the discussion and reached a consensus.
                """),
                "user_prompt": """
                Use technical analysis theories to analysis the chart, such as:
                Overall Trend, Support and Resistance Levels, Price Patterns, Indicators curves
                """,
                "model": technical_model,
            }
        ) # type: ignore

        twoai = TWOAI(
            agent_details=agent_details,
            system_prompt=""
        )

        analysis_result = twoai.start_conversation(self.ticker, self.user_knowledge, image_data)
        return analysis_result

# 使用示例
if __name__ == "__main__":
    ticker = 'AAPL'
    user_knowledge = []
    analyzer = Consensus(ticker, user_knowledge)
    result = analyzer.analyze()
    print(result)