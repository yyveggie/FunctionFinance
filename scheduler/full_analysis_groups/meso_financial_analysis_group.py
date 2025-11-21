import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from langchain_groq import ChatGroq
from langchain_together import Together
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from textwrap import dedent
from scheduler.prompt_tips import self_improve, explain_why
from crewai import Agent
from scheduler.tools import (
    keyword_news_tools,
    public_headline_tools,
    industry_analysis_tools,
    competitor_analysis_tools,
    search_tools,
    company_news_tools
)
from config_loader import (
    CLAUDE_API_KEY,
    CLAUDE_HAIKU,
    GROQ_API_KEY,
    GROQ_MIXTRAL_8x7B,
    TOGETHER_API_KEY,
    TOGETHER_LLAMA3_8B,
    TOGETHER_LLAMA3_70B
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
    def financial_industry_analysis_agent(self):
        return Agent(
            role="Financial Industry Analyst",
            goal="Dynamically analyze financial information and news across various industries based on user queries or directives from a manager agent",
            tools=industry_analysis_tools.tools()
            + keyword_news_tools.tools()
            + search_tools.tools(),
            backstory=dedent(
                    f"""\
                    Armed with cutting-edge AI and analytical tools, you navigate the vast seas of financial data, adapting your 
                    focus based on the latest demands. Whether pinpointing emerging trends in fintech or assessing the impact of 
                    global events on manufacturing, your role is to unveil the financial narratives shaping industries. Directed by 
                    the queries of users or the strategic goals set by your manager, you deliver insights that inform decisions at 
                    the highest levels.\n
                    {self_improve()}
                    """
            ),
            verbose=True,
            memory=True,
            llm=llm_4,
            max_iter=10,
            max_rpm=10,
            allow_delegation=False,
        )

    def competitor_analysis_agent(self):
        return Agent(
            role="Competitor Analysis Analyst",
            goal="Analyze competitors of a certain stock or company",
            tools=competitor_analysis_tools.tools()
            + public_headline_tools.tools()
            + keyword_news_tools.tools()
            + search_tools.tools()
            + company_news_tools.tools(),
            backstory=dedent(
                f"""\
                    As the most seasoned competitor analyst, you need to analyze the competitors of a specific stock or a specific company, 
                    conduct an in-depth analysis of the current industry situation in the market, and provide an analysis of prospects for 
                    entering the industry.\n
                    {self_improve()}
                """
            ),
            verbose=True,
            memory=True,
            llm=llm_5,
            max_iter=10,
            max_rpm=10,
            allow_delegation=False,
        )

    def report_coordination_and_writing_agent(self):
        return Agent(
            role="Report coordination and writing Expert",
            goal="Compile all gathered information into a comprehensive and long-form document",
            backstory=dedent(
                f"""\
                    As a details-oriented senior editor at the Wall Street Journal known for your insightful and engaging articles,
                    your role is to consolidate research, analysis and strategic insights. A financial report should be as comprehensive 
                    and long-form as possible, and you need to build on the rest of the report by crafting an engaging and educational 
                    narrative that reveals new findings in an easy-to-understand way.\n
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
    def __init__(self, query):
        self.query = query
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
            "financial_industry_analysis",
            "competitor_analysis",
            "report_coordination_and_writing",
        ]

        for agent_type in agent_types:
            agent_method = getattr(agents, f"{agent_type}_agent")
            task_method = getattr(tasks, f"{agent_type}_task")

            self.agents[agent_type] = agent_method()
            self.tasks[agent_type] = task_method(
                self.agents[agent_type], self.query)

        context_agent_types = [
            "financial_industry_analysis",
            "competitor_analysis",
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
            # memory=True,
        )


def run(query):
    parser = Stock_Analysis_Team(query=query)
    return parser()


if __name__ == "__main__":
    query = input('请输入您想分析的内容:')
    data = run(query=query)
    print("data:", data)