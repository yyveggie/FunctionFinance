import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from langchain_together import Together
from langchain_openai import ChatOpenAI
from textwrap import dedent
from scheduler.prompt_tips import self_improve, explain_why
from scheduler.callback import print_agent_output
from crewai import Agent
from scheduler.tools import (
    company_news_tools,
    company_post_tools,
    keyword_comment_tools,
    keyword_news_tools,
    search_tools,
)
from config_loader import (
    CLAUDE_API_KEY,
    CLAUDE_HAIKU,
    GROQ_API_KEY,
    GROQ_MIXTRAL_8x7B,
    TOGETHER_API_KEY,
    TOGETHER_LLAMA3_8B
)

llm = ChatAnthropic(
    model_name=CLAUDE_HAIKU,
    api_key=CLAUDE_API_KEY, # type: ignore
    temperature=0.5,
)

llm_1 = ChatGroq(
    model=GROQ_MIXTRAL_8x7B,
    api_key=GROQ_API_KEY, # type: ignore
    temperature=0.5,
)

llm_2 = ChatGroq(
    model=GROQ_MIXTRAL_8x7B,
    api_key=GROQ_API_KEY, # type: ignore
    temperature=0.5,
)

llm_3 = ChatGroq(
    model=GROQ_MIXTRAL_8x7B,
    api_key=GROQ_API_KEY, # type: ignore
    temperature=0.5,
)

llm_4 = Together(
    model=TOGETHER_LLAMA3_8B,
    temperature=0.5,
    max_tokens=4096,
    together_api_key=TOGETHER_API_KEY # type: ignore
)

llm_5 = Together(
    model=TOGETHER_LLAMA3_8B,
    temperature=0.5,
    max_tokens=4096,
    together_api_key=TOGETHER_API_KEY # type: ignore
)

llm_6 = Together(
    model=TOGETHER_LLAMA3_8B,
    temperature=0.5,
    max_tokens=4096,
    together_api_key=TOGETHER_API_KEY # type: ignore
)


class FinancialAgents:
    def behavioral_financial_analysis_agent(self):
        return Agent(
            role="Behavioral Financial Analyst",
            goal="Analyze user behavior from a psychological perspective",
            tools=company_post_tools.tools()
            + keyword_comment_tools.tools()
            + search_tools.tools(),
            backstory=dedent(
                f'''
                As the most seasoned Behavioral Finance Analyst, you are required to gather online discussions about specific company,
                consider the possible behavioral finance theories behind them, and provide insightful analysis on 
                the potential issues that such psychological phenomena may lead to.
                {self_improve()}
                '''
            ),
            verbose=True,
            llm=llm_4,
            max_iter=5,
            max_rpm=5,
            memory=True,
            allow_delegation=False,
            step_callback=lambda x: print_agent_output(x, "Behavioral Financial Analyst"),
        )

    def sentiment_analysis_agent(self):
        return Agent(
            role="Sentiment Analysis Analyst",
            goal="Conduct sentiment analysis of specific company",
            tools=search_tools.tools()
            + company_news_tools.tools()
            + company_post_tools.tools()
            + keyword_comment_tools.tools()
            + keyword_news_tools.tools(),
            backstory=dedent(
                f"""
                As the most seasoned sentiment analysis expert, you are required to perform sentiment analysis on 
                specific company, combining both the government's perspective and user perspective to provide a 
                more in-depth sentiment analysis.
                {self_improve()}
                """
            ),
            verbose=True,
            memory=True,
            llm=llm_5,
            max_iter=5,
            max_rpm=5,
            allow_delegation=False,
            step_callback=lambda x: print_agent_output(x, "Sentiment Analysis Analyst"),
        )

    def final_recommendation_agent(self):
        return Agent(
            role="Stock Recommendation Expert",
            goal="Integrate all the information to provide the final recommendation confidence level",
            backstory=dedent(
                f"""
                You have been recognized as the world's best stock recommender, possessing extensive knowledge of 
                various financial operating principles and market sentiment fluctuations. Based on the collected 
                information, you and your team have conducted detailed recommendation updates after each new data 
                arrival. Ultimately, you will provide your recommendation for specific company stock based on all 
                the previous information gathered. You will carefully consider the confidence level and reasoning 
                for each recommendation (sell, buy, hold).
                {self_improve()}
                """
            ),
            verbose=True,
            memory=True,
            llm=llm_6,
            max_iter=5,
            max_rpm=5,
            allow_delegation=True,
        )


from crewai import Crew, Process
from scheduler.tasks import FinancialTasks

tasks = FinancialTasks()
agents = FinancialAgents()

class Stock_Analysis_Team:
    def __init__(self, company):
        self.company = company
        self.agents = {}
        self.tasks = {}

    def __call__(self):
        self.create_agents_and_tasks()
        self.create_crew()
        result = self.crew.kickoff()
        # metrics = self.crew.usage_metrics
        return result

    def create_agents_and_tasks(self):
        agent_types = [
            "behavioral_financial_analysis",
            "sentiment_analysis",
            "final_recommendation",
        ]

        for agent_type in agent_types:
            agent_method = getattr(agents, f"{agent_type}_agent")
            task_method = getattr(tasks, f"{agent_type}_task")

            self.agents[agent_type] = agent_method()
            self.tasks[agent_type] = task_method(
                self.agents[agent_type], self.company)

        context_agent_types = [
            "behavioral_financial_analysis",
            "sentiment_analysis",
        ]
        self.tasks["final_recommendation"].context = [
            self.tasks[agent_type] for agent_type in context_agent_types
        ]

    def create_crew(self):
        self.create_agents_and_tasks()
        self.crew = Crew(
            agents=list(self.agents.values()),
            tasks=list(self.tasks.values()),
            process=Process.hierarchical,
            manager_llm=llm,
            memory=False,
        )


def run(company: str):
    parser = Stock_Analysis_Team(company=company)
    return parser()


if __name__ == "__main__":
    company = "alibaba"
    result = run(company=company)
    print("result:", result)
    print("————————————————————————————————————————————————————")
