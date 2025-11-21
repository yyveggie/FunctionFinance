import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crewai import Agent, Crew, Process
from langchain_groq import ChatGroq

#from tools.openbb_tools import OpenBBTools
from scheduler.tools import sec_tools
from langchain_openai import ChatOpenAI
from langchain_together import Together
from langchain_anthropic import ChatAnthropic
from config_loader import TOGETHER_API_KEY, GPT4_API_KEY, GPT4_LLM, BASE_URL, CLAUDE_HAIKU_LLM, CLAUDE_API_KEY, GROQ_API_KEY
from scheduler.prompt_tips import self_improve, explain_why

llm = ChatOpenAI(
    model="NousResearch/Nous-Hermes-2-Mixtral-8x7B-SFT",
    temperature=0.7,
    api_key=TOGETHER_API_KEY,
    base_url="https://api.together.xyz"
)

groq_llm = ChatGroq(
    temperature=0.7, 
    api_key=GROQ_API_KEY,  # type: ignore
    model="mixtral-8x7b-32768"
)

together_llm = Together(
    model="teknium/OpenHermes-2p5-Mistral-7B",
    temperature=0.7,
    together_api_key=TOGETHER_API_KEY # type: ignore
)

haiku_llm = ChatOpenAI(
    base_url=BASE_URL,
    temperature=0.7,
    model=CLAUDE_HAIKU_LLM,
    api_key=CLAUDE_API_KEY, # type: ignore
    streaming=True,
)

class FinancialAgents():
# Define your agents with roles and goals
    def visionary_agent(self):
        return Agent(
            role='Visionary',
            goal='Deep thinking on the implications of an analysis',
            backstory=f"""
            you are a visionary technologist with a keen eye for identifying emerging trends and predicting their potential impact on 
            various industries. Your ability to think critically and connect seemingly disparate dots allows you to anticipate disruptive 
            technologies and their far-reaching implications.
            {self_improve()}
            """,
            verbose=True,
            allow_delegation=False,
            llm=llm,
            memory=True,
            max_iter=10,
            max_rpm=10,
        )
        
    def senior_research_agent(self):
        return  Agent(
            role='Senior Research Analyst',
            goal='Uncover insights into the specific company',
            backstory=f"""
            You work as a research analyst at Goldman Sachs, focusing on fundamental research for companies
            {self_improve()}
            """,
            verbose=True,
            allow_delegation=False,
            tools=sec_tools.tools(),
            llm=llm,
            memory=True,
            max_iter=10,
            max_rpm=10,
        )

    def writer_agent(self):
        return Agent(
            role='Senior editor',
            goal='Writes professional quality articles that are easy to understand',
            backstory=f"""
            You are a details-oriented senior editor at the Wall Street Journal known for your insightful and engaging articles. 
            You transform complex concepts into factual and impactful narratives.
            {self_improve()}
            """,
            verbose=True,
            allow_delegation=True,
            llm=together_llm,
            memory=True,
            max_iter=10,
            max_rpm=10,
        )


from crewai import Crew, Process
from scheduler.tasks import FinancialTasks

tasks = FinancialTasks()
agents = FinancialAgents()

main_llm = ChatOpenAI(
    # base_url=BASE_URL,
    temperature=0.7,
    model=GPT4_LLM,
    api_key=GPT4_API_KEY, # type: ignore
)

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
            "senior_research",
            "visionary",
            "writer",
        ]
        for agent_type in agent_types:
            agent_method = getattr(agents, f"{agent_type}_agent")
            task_method = getattr(tasks, f"{agent_type}_task")

            self.agents[agent_type] = agent_method()
            self.tasks[agent_type] = task_method(
                self.agents[agent_type], self.query)

    def create_crew(self):
        self.create_agents_and_tasks()
        self.crew = Crew(
            agents=list(self.agents.values()),
            tasks=list(self.tasks.values()),
            process=Process.sequential,
            verbose=2,
            # memory=True,
            language="en",
            cache=True,
            full_output=True
        )


def run(query):
    parser = Stock_Analysis_Team(query=query)
    return parser()


if __name__ == "__main__":
    for i in ["请分析阿里巴巴的财务状况"]:
        print('\n')
        print(i)
        data = run(query=i)
        print("data:", data)
        print("————————————————————————————————————————————————————")