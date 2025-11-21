import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from typing import Annotated, Any, Dict, List, Optional, Tuple, Union, Sequence, TypedDict
import operator
import functools
from langchain_experimental.utilities import PythonREPL
from crawler_classifier.crawler_function_calling import Scraper
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.messages import BaseMessage, HumanMessage
from langchain.agents import AgentExecutor, create_openai_tools_agent, create_openai_functions_agent
from duckduckgo_search import DDGS
from tempfile import TemporaryDirectory
from pathlib import Path
import os
# Set environment variables
os.environ["LANGCHAIN_TRACING_V2"] = "false"
Tavily_API_KEY = os.environ.get('Tavily_API_KEY')
os.environ["LANGCHAIN_PROJECT"] = "LangGraph Research Agents"


class Supervisor():
    def __init__(self, llm):
        self.llm = llm

    def create_agents(self, query):
        repl = PythonREPL()
        _TEMP_DIRECTORY = TemporaryDirectory()
        WORKING_DIRECTORY = Path(_TEMP_DIRECTORY.name)
        # 1. Create Tools: Each team will be composed of one or more agents each with one or more tools. Below, define all the tools to be used by your different teams. We'll start with the research team.
        # 1.1 Research team tools: The research team can use a search engine and url scraper to find information on the web. Feel free to add additional functionality below to boost the team performance!
        # tavily_tool = TavilySearchResults(max_results=5)
        # @tool
        # def scrape_webpages(urls: List[str]) -> str:
        #     """Use requests and bs4 to scrape the provided web pages for detailed information."""
        #     loader = WebBaseLoader(urls)
        #     docs = loader.load()
        #     return "\n\n".join(
        #         [
        #             f'<Document name="{doc.metadata.get("title", "")}">\n{doc.page_content}\n</Document>'
        #             for doc in docs
        #         ]
        #     )

        @tool
        def scrape_webpages_more_specific_data(query: str) -> str:
            """Get data from web crawlers."""
            scraper = Scraper()
            print(query)
            return scraper(query)

        # 1.2 Document writing team tools: Next up, we will give some tools for the doc writing team to use. We define some bare-bones file-access tools below. Note that this gives the agents access to your file-system, which can be unsafe. We also haven't optimized the tool descriptions for performance.
        @tool
        def create_outline(
            points: Annotated[List[str], "List of main points or sections."],
            file_name: Annotated[str, "File path to save the outline."],
        ) -> Annotated[str, "Path of the saved outline file."]:
            """Create and save an outline."""
            with (WORKING_DIRECTORY / file_name).open("w") as file:
                for i, point in enumerate(points):
                    file.write(f"{i + 1}. {point}\n")
            return f"Outline saved to {file_name}"

        @tool
        def read_document(
            file_name: Annotated[str, "File path to save the document."],
            start: Annotated[Optional[int],
                             "The start line. Default is 0"] = None,
            end: Annotated[Optional[int],
                           "The end line. Default is None"] = None,
        ) -> str:
            """Read the specified document."""
            with (WORKING_DIRECTORY / file_name).open("r") as file:
                lines = file.readlines()
            if start is not None:
                start = 0
            return "\n".join(lines[start:end])

        @tool
        def write_document(
            content: Annotated[str, "Text content to be written into the document."],
            file_name: Annotated[str, "File path to save the document."],
        ) -> Annotated[str, "Path of the saved document file."]:
            """Create and save a text document."""
            with (WORKING_DIRECTORY / file_name).open("w") as file:
                file.write(content)
            return f"Document saved to {file_name}"

        @tool
        def edit_document(
            file_name: Annotated[str, "Path of the document to be edited."],
            inserts: Annotated[
                Dict[int, str],
                "Dictionary where key is the line number (1-indexed) and value is the text to be inserted at that line.",
            ],
        ) -> Annotated[str, "Path of the edited document file."]:
            """Edit a document by inserting text at specific line numbers."""

            with (WORKING_DIRECTORY / file_name).open("r") as file:
                lines = file.readlines()

            sorted_inserts = sorted(inserts.items())

            for line_number, text in sorted_inserts:
                if 1 <= line_number <= len(lines) + 1:
                    lines.insert(line_number - 1, text + "\n")
                else:
                    return f"Error: Line number {line_number} is out of range."

            with (WORKING_DIRECTORY / file_name).open("w") as file:
                file.writelines(lines)

            return f"Document edited and saved to {file_name}"

        # 1.3 Chart generate tools
        @tool
        def python_repl(
            code: Annotated[str,
                            "The python code to execute to generate your chart."]
        ):
            """Use this to execute python code. If you want to see the output of a value,
            you should print it out with `print(...)`. This is visible to the user."""
            try:
                result = repl.run(code)
            except BaseException as e:
                return f"Failed to execute. Error: {repr(e)}"
            return f"Succesfully executed:\n```python\n{code}\n```\nStdout: {result}"

        # 1.5 other tools waitting...
        # @tool
        # def sentiment_analysis():
        #     """Perform detailed sentiment analysis of text."""
        #     pass

        # @tool
        # def file_analysis():
        #     """Analyze files uploaded by users."""
        #     pass

        # @tool
        # def query_parser():
        #     """Extract parameters in the query about financial requirements,
        #     which may include the following: company_en, company_cn, listing_exchange, content_dict,
        #     ticker, cryptocurrency, start_date, end_date, specific_date,
        #     year, frequency, timeframe, quarter, country, keyword_cn, keyword_en."""
        #     from query_parse.parser import Parser
        #     Parser(self.llm)

        # 2. Helper Utilities
        # We are going to create a few utility functions to make it more concise when we want to:
            # 1. Create a worker agent.
            # 2. Create a supervisor for the sub-graph.
        # These will simplify the graph compositional code at the end for us so it's easier to see what's going on.
        def create_agent(
            llm: ChatOpenAI,
            tools: list,
            system_prompt: str,
        ) -> str:
            """Create a function-calling agent and add it to the graph."""
            system_prompt += "\nWork autonomously according to your specialty, using the tools available to you."
            " Do not ask for clarification."
            " Your other team members (and other teams) will collaborate with you with their own specialties."
            " You are chosen for a reason! You are one of the following team members: {team_members}."
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        system_prompt,
                    ),
                    MessagesPlaceholder(variable_name="messages"),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ]
            )
            agent = create_openai_functions_agent(self.llm, tools, prompt)
            executor = AgentExecutor(agent=agent, tools=tools)
            return executor

        def agent_node(state, agent, name):
            result = agent.invoke(state)
            return {"messages": [HumanMessage(content=result["output"], name=name)]}

        def create_team_supervisor(
            llm: ChatOpenAI, system_prompt, members
        ) -> str:
            """An LLM-based router."""
            options = ["FINISH"] + members
            function_def = {
                "name": "route",
                "description": "Select the next role.",
                "parameters": {
                    "title": "routeSchema",
                    "type": "object",
                    "properties": {
                        "next": {
                            "title": "Next",
                            "anyOf": [
                                {"enum": options},
                            ],
                        },
                    },
                    "required": ["next"],
                },
            }
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    MessagesPlaceholder(variable_name="messages"),
                    (
                        "system",
                        "Given the conversation above, who should act next?"
                        " Or should we FINISH? Select one of: {options}."
                        " Note that if the loop calls the same node multiple times without"
                        " obtaining the desired result, it must be FINISH.",
                    ),
                ]
            ).partial(options=str(options), team_members=", ".join(members))
            return (
                prompt
                | self.llm.bind_functions(functions=[function_def], function_call="route")
                | JsonOutputFunctionsParser()
            )

        # 3. Define Agent Teams: Now we can get to define our hierachical teams. "Choose your player!"

        # 3.1 Research team: The research team will have a search agent and a web scraping
        # "research_agent" as the two worker nodes. Let's create those, as well as the team supervisor.
        # Research team graph state
        class ResearchTeamState(TypedDict):
            # A message is added after each team member finishes
            messages: Annotated[List[BaseMessage], operator.add]
            # The team members are tracked so they are aware of
            # the others' skill-sets
            team_members: List[str]
            # Used to route work. The supervisor calls a function
            # that will update this every time it makes a decision
            next: str

        # Now that we've created the necessary components, defining their interactions is easy. Add the nodes to the team graph, and define the edges, which determine the transition criteria.
        # search_agent = create_agent(self.llm, [tavily_tool], "You are a research assistant who can search for up-to-date info using the tavily search engine.")
        # search_node = functools.partial(agent_node, agent=search_agent, name="Search")

        # research_agent = create_agent(self.llm, [scrape_webpages], "You are a research assistant who can scrape specified urls for more detailed information using the scrape_webpages function.")
        # research_node = functools.partial(agent_node, agent=research_agent, name="Web Scraper")

        scraper_agent = create_agent(self.llm, [scrape_webpages_more_specific_data],
                                     "You are a research assistant who can scrape webpages for more detailed information using the scrape_webpages_more_specific_data function.")
        scraper_node = functools.partial(
            agent_node, agent=scraper_agent, name="Web Scraper")

        supervisor_agent = create_team_supervisor(
            self.llm,
            "You are a supervisor tasked with managing a conversation between the"
            # " following workers:  Search, Web Scraper. Given the following user request,"
            " following workers:  Web Scraper. Given the following user request,"
            " respond with the worker to act next. Each worker will perform a"
            " task and respond with their results and status. When finished,"
            " respond with FINISH.",
            # ["Search", "Web Scraper"],
            ["Web Scraper"],
        )

        research_graph = StateGraph(ResearchTeamState)
        # research_graph.add_node("Search", search_node)
        # research_graph.add_node("Web Scraper", research_node)
        research_graph.add_node("Web Scraper", scraper_node)
        research_graph.add_node("supervisor", supervisor_agent)

        # research_graph.add_edge("Search", "supervisor")
        # research_graph.add_edge("Web Scraper", "supervisor")
        research_graph.add_edge("Web Scraper", "supervisor")
        research_graph.add_conditional_edges(
            "supervisor",
            lambda x: x["next"],
            {
                # "Search": "Search",
                # "Web Scraper": "Web Scraper",
                "Web Scraper": "Web Scraper",
                "FINISH": END
            }
        )

        research_graph.set_entry_point("supervisor")
        chain = research_graph.compile()

        # The following functions interoperate between the top level graph state
        # and the state of the research sub-graph
        # this makes it so that the states of each graph don't get intermixed
        def research_graph_enter_chain(message: str):
            results = {
                "messages": [HumanMessage(content=message)],
            }
            return results

        research_chain = (
            research_graph_enter_chain
            | chain
        )

        # 3.2 Chart Generate Team
        # Chart generate team graph state
        class ChartGenerateTeamState(TypedDict):
            # A message is added after each team member finishes
            messages: Annotated[List[BaseMessage], operator.add]
            # The team members are tracked so they are aware of
            # the others' skill-sets
            team_members: List[str]
            # Used to route work. The supervisor calls a function
            # that will update this every time it makes a decision
            next: str

        code_agent = create_agent(self.llm, [
                                  python_repl], "You may generate safe python code to analyze data and generate charts using matplotlib.")
        code_node = functools.partial(
            agent_node, agent=code_agent, name="Coder")

        supervisor_agent = create_team_supervisor(
            self.llm,
            "You are a supervisor tasked with managing a conversation the"
            " following workers: Coder. Given the following user request,"
            " respond with the worker to act next. Each worker will perform a"
            " task and respond with their results and status. When finished,"
            " respond with FINISH.",
            ["Coder"],
        )

        coder_graph = StateGraph(ChartGenerateTeamState)
        coder_graph.add_node("Coder", code_node)
        coder_graph.add_node("supervisor", supervisor_agent)

        # Define the control flow
        coder_graph.add_edge("Coder", "supervisor")
        coder_graph.add_conditional_edges(
            "supervisor",
            lambda x: x["next"],
            {
                "Coder": "Coder",
                "FINISH": END
            }
        )

        coder_graph.set_entry_point("supervisor")
        chain = coder_graph.compile()

        # The following functions interoperate between the top level graph state
        # and the state of the research sub-graph
        # this makes it so that the states of each graph don't get intermixed
        def coder_graph_enter_chain(message: str):
            results = {
                "messages": [HumanMessage(content=message)],
            }
            return results

        chart_generate_chain = (
            coder_graph_enter_chain
            | chain
        )

        # 3.3 Document Writing Team
        # Create the document writing team below using a similar approach. This time, we will give each agent access to different file-writing tools.
        # Note that we are giving file-system access to our agent here, which is not safe in all cases.
        # Document writing team graph state
        class DocWritingState(TypedDict):
            # This tracks the team's conversation internally
            messages: Annotated[List[BaseMessage], operator.add]
            # This provides each worker with context on the others' skill sets
            team_members: str
            # This is how the supervisor tells langgraph who to work next
            next: str
            # This tracks the shared directory state
            current_files: str

        # This will be run before each worker agent begins work
        # It makes it so they are more aware of the current state
        # of the working directory.
        def prelude(state):
            written_files = []
            if not WORKING_DIRECTORY.exists():
                WORKING_DIRECTORY.mkdir()
            try:
                written_files = [
                    f.relative_to(WORKING_DIRECTORY) for f in WORKING_DIRECTORY.rglob("*")
                ]
            except:
                pass
            if not written_files:
                return {**state, "current_files": "No files written."}
            return {
                **state,
                "current_files": "\nBelow are files your team has written to the directory:\n"
                + "\n".join([f" - {f}" for f in written_files]),
            }

        doc_writer_agent = create_agent(
            self.llm,
            [write_document, edit_document, read_document],
            "You are an expert writing a research document.\n"
            # The {current_files} value is populated automatically by the graph state
            "Below are files currently in your directory:\n{current_files}",
        )
        # Injects current directory working state before each call
        context_aware_doc_writer_agent = prelude | doc_writer_agent
        doc_writing_node = functools.partial(
            agent_node, agent=context_aware_doc_writer_agent, name="Doc Writer")

        note_taking_agent = create_agent(
            self.llm,
            [create_outline, read_document],
            "You are an expert senior researcher tasked with writing a paper outline and"
            " taking notes to craft a perfect paper.{current_files}",
        )
        context_aware_note_taking_agent = prelude | note_taking_agent
        note_taking_node = functools.partial(
            agent_node, agent=context_aware_note_taking_agent, name="Note Taker")

        chart_generating_agent = create_agent(
            self.llm,
            [read_document, python_repl],
            "You are a data viz expert tasked with generating charts for a research project."
            "{current_files}",
        )
        context_aware_chart_generating_agent = prelude | chart_generating_agent
        chart_generating_node = functools.partial(
            agent_node, agent=context_aware_chart_generating_agent, name="Chart Generator")

        doc_writing_supervisor = create_team_supervisor(
            self.llm,
            "You are a supervisor tasked with managing a conversation between the"
            " following workers:  {team_members}. Given the following user request,"
            " respond with the worker to act next. Each worker will perform a"
            " task and respond with their results and status. When finished,"
            " respond with FINISH.",
            ["Doc Writer", "Note Taker", "Chart Generator"]
        )

        # With the objects themselves created, we can form the graph.

        # Create the graph here:
        # Note that we have unrolled the loop for the sake of this doc
        authoring_graph = StateGraph(DocWritingState)
        authoring_graph.add_node("Doc Writer", doc_writing_node)
        authoring_graph.add_node("Note Taker", note_taking_node)
        authoring_graph.add_node("Chart Generator", chart_generating_node)
        authoring_graph.add_node("supervisor", doc_writing_supervisor)

        # Add the edges that always occur
        authoring_graph.add_edge("Doc Writer", "supervisor")
        authoring_graph.add_edge("Note Taker", "supervisor")
        authoring_graph.add_edge("Chart Generator", "supervisor")

        # Add the edges where routing applies
        authoring_graph.add_conditional_edges(
            "supervisor",
            lambda x: x["next"],
            {
                "Doc Writer": "Doc Writer",
                "Note Taker": "Note Taker",
                "Chart Generator": "Chart Generator",
                "FINISH": END
            }
        )

        authoring_graph.set_entry_point("supervisor")
        chain = research_graph.compile()

        # The following functions interoperate between the top level graph state
        # and the state of the research sub-graph
        # this makes it so that the states of each graph don't get intermixed
        def authoring_graph_enter_chain(message: str, members: List[str]):
            results = {
                "messages": [HumanMessage(content=message)],
                "team_members": ", ".join(members)
            }
            return results

        # We re-use the enter/exit functions to wrap the graph
        authoring_chain = (
            functools.partial(authoring_graph_enter_chain,
                              members=authoring_graph.nodes)
            | authoring_graph.compile()
        )

        # 4 Add Layers
        # In this design, we are enforcing a top-down planning policy. We've created three graphs already, but we have to decide how to route work between the three.
        # We'll create a _forth_ graph to orchestrate the previous three, and add some connectors to define how this top-level state is shared between the different graphs.
        supervisor_node = create_team_supervisor(
            self.llm,
            "You are a supervisor tasked with managing a conversation between the"
            " following teams: {team_members}. Given the following user request,"
            " respond with the worker to act next. Each worker will perform a"
            " task and respond with their results and status. When finished,"
            " respond with FINISH.",
            ["Research team", "Paper writing team", "Chart generate team"],
        )

        # Top-level graph state
        class State(TypedDict):
            messages: Annotated[List[BaseMessage], operator.add]
            next: str

        def get_last_message(state: State) -> str:
            return state["messages"][-1].content

        def join_graph(response: dict):
            return {"messages": [response["messages"][-1]]}

        # Define the graph.
        super_graph = StateGraph(State)
        # First add the nodes, which will do the work
        super_graph.add_node(
            "Research team", get_last_message | research_chain | join_graph)
        super_graph.add_node("Paper writing team",
                             get_last_message | authoring_chain | join_graph)
        super_graph.add_node(
            "Chart generate team", get_last_message | chart_generate_chain | join_graph)
        super_graph.add_node("supervisor", supervisor_node)

        # Define the graph connections, which controls how the logic
        # propagates through the program
        super_graph.add_edge("Research team", "supervisor")
        super_graph.add_edge("Paper writing team", "supervisor")
        super_graph.add_edge("Chart generate team", "supervisor")
        super_graph.add_conditional_edges(
            "supervisor",
            lambda x: x["next"],
            {
                "Paper writing team": "Paper writing team",
                "Research team": "Research team",
                "Chart generate team": "Chart generate team",
                "FINISH": END
            }
        )
        super_graph.set_entry_point("supervisor")
        super_graph = super_graph.compile()

        for s in super_graph.stream(
            {
                "messages": [
                    HumanMessage(content=query)
                ],
            },
            {"recursion_limit": 150},
        ):
            if "__end__" not in s:
                print(s)
                print("---")

    def handle_query(self, query):
        return self.create_agents(query)


if __name__ == "__main__":
    import os
    from langchain_openai import ChatOpenAI
    OPENAI_API_KEY = os.environ.get('OpenAI_KEY')
    llm = ChatOpenAI(temperature=1, model="gpt-3.5-turbo-16k",
                     api_key=OPENAI_API_KEY)
    s = Supervisor(llm)
    s.handle_query("search the headlines of tencent and make a summary.")
