import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from langchain_groq import ChatGroq
from langchain_together import Together
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from textwrap import dedent
from crewai import Agent
from scheduler.tools import (
    public_headline_tools,
    public_news_tools,
    search_tools,
    market_trend_tools
)
from scheduler.callback import print_agent_output
from config_loader import (
    CLAUDE_API_KEY,
    CLAUDE_HAIKU,
    GROQ_API_KEY,
    GROQ_MIXTRAL_8x7B,
    TOGETHER_API_KEY,
    TOGETHER_LLAMA3_8B,
    TOGETHER_LLAMA3_70B,
    GPT4O,
    OPENAI_API_KEY
)
from scheduler.prompt_tips import self_improve, explain_why


llm = ChatAnthropic(
    model_name=CLAUDE_HAIKU,
    api_key=CLAUDE_API_KEY, # type: ignore
    temperature=0.5,
)

llm_1 = ChatOpenAI(
    model=GPT4O,
    api_key=OPENAI_API_KEY, # type: ignore
    temperature=0.5,
)

llm_2 = ChatOpenAI(
    model=GPT4O,
    api_key=OPENAI_API_KEY, # type: ignore
    temperature=0.5,
)

llm_3 = ChatOpenAI(
    model=GPT4O,
    api_key=OPENAI_API_KEY, # type: ignore
    temperature=0.5,
)

llm_4 = Together(
    model=TOGETHER_LLAMA3_70B,
    temperature=0.5,
    max_tokens=4096,
    together_api_key=TOGETHER_API_KEY # type: ignore
)

llm_5 = Together(
    model=TOGETHER_LLAMA3_70B,
    temperature=0.5,
    max_tokens=4096,
    together_api_key=TOGETHER_API_KEY # type: ignore
)

llm_6 = Together(
    model=TOGETHER_LLAMA3_70B,
    temperature=0.5,
    max_tokens=4096,
    together_api_key=TOGETHER_API_KEY # type: ignore
)


class FinancialAgents:
    def global_news_analysis_agent(self):
        return Agent(
            role="Global Financial News Analyst",
            goal="Analyze global news dynamics with a focus on the financial sector to provide solid data support and insights for investment decisions",
            tools=public_headline_tools.tools()
            + public_news_tools.tools()
            + search_tools.tools(),
            backstory=f"""
            As an experienced global financial news analyst, you possess unparalleled insights into the dynamics of the financial markets. 
            With your in-depth understanding of international politics, economic trends, and precise grasp of data analysis, you can sift 
            through vast amounts of news information to extract the most valuable insights for investors. Your expert analysis helps the 
            company keep its pulse on the market and foresee future trends, maintaining a lead in the competitive financial marketplace.\n
            {self_improve()}
            """,
            verbose=True,
            llm=llm_4,
            max_iter=10,
            max_rpm=20,
            memory=True,
            allow_delegation=False,
            step_callback=lambda x: print_agent_output(x, "Global Financial News Analyst"),
        )
    
    def market_trend_analysis_agent(self):
        return Agent(
            role="Market Trend Analyst",
            goal="Analyze and report on market trends to guide investment decisions.",
            backstory=f'''
            As a seasoned market trend analyst at a leading financial firm, you have a keen eye for identifying patterns in market behavior. 
            With a solid background in finance and data analysis, you leverage cutting-edge tools to sift through vast amounts of market 
            data, extracting valuable insights that drive strategic investment decisions.\n
            {self_improve()}
            ''',
            tools=market_trend_tools.tools(),
            llm=llm_5,
            max_iter=10,
            max_rpm=20,
            memory=True,
            verbose=True,
            allow_delegation=False,
            step_callback=lambda x: print_agent_output(x, "Market Trend Analyst"),
        )

    def report_coordination_and_writing_agent(self):
        return Agent(
            role="Report coordination and writing Expert",
            goal="Compile all gathered information into a comprehensive document",
            backstory=f"""
            As a detail-oriented senior editor at The Wall Street Journal known for insightful and engaging writing, your role will be to 
            integrate research, analysis and strategic insights and deliver a detailed report.\n
            {self_improve()}
            """,
            verbose=True,
            llm=llm_6,
            max_iter=5,
            max_rpm=5,
            memory=True,
            allow_delegation=True,
        )


from crewai import Crew, Process
from scheduler.tasks import FinancialTasks

tasks = FinancialTasks()
agents = FinancialAgents()

class Stock_Analysis_Team:
    def __init__(self, query):
        self.query = query
        self.agents = {}
        self.tasks = {}

    def __call__(self):
        self.create_agents_and_tasks()
        self.create_crew()
        result = self.crew.kickoff()
        metrics = self.crew.usage_metrics
        return result

    def create_agents_and_tasks(self):
        agent_types = [
            "global_news_analysis",
            "market_trend_analysis",
            "report_coordination_and_writing",
        ]
        for agent_type in agent_types:
            agent_method = getattr(agents, f"{agent_type}_agent")
            task_method = getattr(tasks, f"{agent_type}_task")

            self.agents[agent_type] = agent_method()
            self.tasks[agent_type] = task_method(
                self.agents[agent_type], self.query)

        context_agent_types = [
            "global_news_analysis",
            "market_trend_analysis",
        ]
        self.tasks["report_coordination_and_writing"].context = [
            self.tasks[agent_type] for agent_type in context_agent_types
        ]

    def create_crew(self):
        self.create_agents_and_tasks()
        self.crew = Crew(
            agents=list(self.agents.values()),
            tasks=list(self.tasks.values()),
            process=Process.hierarchical,
            manager_llm=llm,
            verbose=2,
            # memory=True,
            step_callback=lambda x: print_agent_output(x, "Macro Financial Analysis Group")
        )


def run(query):
    parser = Stock_Analysis_Team(query=query)
    return parser()


if __name__ == "__main__":
    query = input('请输入您想分析的内容:')
    data = run(query=query)
    print("data:", data)
