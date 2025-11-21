import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from config_loader import (
    CLAUDE_API_KEY,
    CLAUDE_OPUS,
    BASE_URL,
    GPT4O,
    ZEN_API_KEY,
    TOPIC
)
from anthropic import Anthropic, AsyncAnthropic
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from rich.panel import Panel
from rich.console import Console
from textwrap import dedent
import instructor
import asyncio
import json

client = instructor.from_anthropic(AsyncAnthropic(
    api_key=CLAUDE_API_KEY,
))

refine_llm = ChatOpenAI(
    base_url=BASE_URL,
    temperature=0.5,
    model=GPT4O,
    api_key=ZEN_API_KEY,  # type: ignore
)

import enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class AllowedGroups(str, enum.Enum):
    TECHNICAL_ANALYSIS_GROUP = "Technical analysis group"
    BEHAVIOR_ANALYSIS_GROUP = "Behavior analysis group"
    MACRO_FINANCIAL_ANALYSIS_GROUP = "Macro financial analysis group"
    MESO_FINANCIAL_ANALYSIS_GROUP = "Meso financial analysis group"
    MICRO_FINANCIAL_ANALYSIS_GROUP = "Micro financial analysis group"

class OrchestratorOutput(BaseModel):
    sub_group: AllowedGroups
    query: str = Field(..., description="Query for selected sub-group")
    explanation: Optional[str] = Field(..., description="Explanation for the selected sub group and query")

    @field_validator('sub_group')
    def group_must_be_allowed(cls, v):
        if v not in set(AllowedGroups):
            raise ValueError(f'Group "{v}" is not allowed')
        return v

    class Config:
        use_enum_values = True

class TaskOrchestrator:
    def __init__(self, objective):
        self.objective = objective
        self.console = Console()
        
        if TOPIC.lower() == "stock":
            self.groups = {
                "Behavior analysis group": "Utilizes user data from social networks for behavioral, psychological, and sentiment analysis of a specific stock.",
                "Macro financial analysis group": "Conducts analysis on the overall economic condition. This includes analysis of macroeconomic indicators such as economic growth, inflation, interest rates and unemployment rates.",
                "Meso financial analysis group": "Focuses on the analysis of major stocks within a specified industry or sector, and may also analyze competitors of a specified stock/company.",
                "Micro financial analysis group": "Specializes in analyzing the financial and operational conditions of specific companies, helping investors understand the intrinsic value of the company and its potential for future development.",
            }
        else:
            pass
        
    async def __call__(self):
        return await self.main()

    async def orchestrator(self, previous_results=None):
        self.console.print(
            f"\n[bold]Calling orchestrator for your objective[/bold]")
        previous_results_text = "\n".join(
            previous_results) if previous_results else "None"

        opus_response = await client.chat.completions.create(
            model=CLAUDE_OPUS,
            max_tokens=300,
            response_model=OrchestratorOutput,
            messages=[
                {
                    "role": "system",
                    "content": dedent(
                        f"""
                        You are a Wall Street-level financial manager, and you are currently serving a high-level VIP client to achieve his objective.
                        You always think about problems in a comprehensive and detailed way. You are able to think about problems from a global perspective, also good at breaking down problems.
                        Now, you are focusing on {TOPIC} analysis. You have a team that is divided into different sub-groups, each specializing in a different direction.
                        Here are their names and introductions:\n\n
                        {json.dumps(self.groups)}\n\n
                        You will direct their work and ultimately compile their results into a complete report to the client.
                        """)
                },
                {
                    "role": "user",
                    "content": dedent(
                        f"""
                        Based on the following objective and the previous sub-group task results (if any), please assess whether the objective has been fully achieved.
                        - If the previous sub-task results comprehensively cover all aspects of the objective, please include the phrase 'The task is complete:' in your response explanation.
                        - If the objective is not yet fully achieved, please break down it into the next sub-task and select a sub-group to execute the sub-task.
                        Create a concise and detailed query for the sub-group (similar to the user query, such as 'please analysis the latest news about apple and make a report')
                        so that the sub-group can execute the task. At this time, your response includes: sub-group (can only be selected from predefined options), query, and your explanation(reasoning).

                        Objective: {self.objective}
                        Previous sub-group task results: {previous_results_text}
                        
                        - Carefully consider the analytical logic behind your client's goals, schedule your team to perform tasks in a specific order, and print your rationale each time you dispatch a task.
                        - Please apply Occam's Razor principle: do not overuse different groups if it is possible to satisfactorily resolve user queries with fewer, as this will lead to excessive cost consumption.
                        """),
                    },
                ],
            ) # type: ignore
        group = opus_response.sub_group
        sub_query = opus_response.query
        explanation = opus_response.explanation
        data_dict = {
            "group": group,
            "query": sub_query,
            "explanation": explanation
        }
        response_text = json.dumps(data_dict)
        self.console.print(Panel(response_text, title=f"[bold green]Orchestrator[/bold green]",
                        title_align="left", border_style="green", subtitle=f"Sending task to {group} 👇"))
        return response_text, group, sub_query

    async def sub_group(self, group, query):
        try:
            if group == "Behavior analysis group":
                from scheduler.full_analysis_groups import behavior_analysis_group
                print('calling behavior analysis group...')
                response_text = behavior_analysis_group.run(query)
            elif group == "Macro financial analysis group":
                from scheduler.full_analysis_groups import macro_financial_analysis_group
                print('calling macro financial analysis group...')
                response_text = macro_financial_analysis_group.run(query)
            elif group == "Meso financial analysis group":
                from scheduler.full_analysis_groups import meso_financial_analysis_group
                print('calling meso financial analysis group...')
                response_text = meso_financial_analysis_group.run(query)
            elif group == "Micro financial analysis group":
                from scheduler.full_analysis_groups import micro_financial_analysis_group
                print('calling micro financial analysis group...')
                response_text = micro_financial_analysis_group.run(query)
            else:
                return f"[bold red]Parsing of subgroups failed:{group}[/bold red]"

            self.console.print(Panel(response_text, title=f"[bold blue]{group} Result[/bold blue]",
                      title_align="left", border_style="blue", subtitle="Task completed, sending result to orchestrator 👇"))
            return response_text
        except Exception as e:
            self.console.print(f"[bold red]Error in {group}:[/bold red] {str(e)}")
            return None

    async def opus_refine(self, sub_task_results):
        try:
            print(f"\nCalling orchestrator to provide the refined final output for your objective:")
            messages = [
                HumanMessage(
                    content=f"Objective: {self.objective}\n\nSub-task results:\n" + "\n".join(
                        sub_task_results) + "\n\nPlease review and refine the sub-task results into a cohesive final output. add any missing information or details as needed. When working on code projects make sure to include the code implementation by file."
                ),
            ]
            response_text = await refine_llm.agenerate([messages[0]]).strip()
            self.console.print(Panel(
                response_text, title="[bold green]Final Output[/bold green]", title_align="left", border_style="green"))
            return response_text
        except Exception as e:
            self.console.print(f"[bold red]Error in orchestrator_refine:[/bold red] {str(e)}")
            return None

    async def main(self):
        task_exchanges = []
        sub_tasks = []

        while True:
            # Call orchestrator to break down the objective into the next sub-task or provide the final output
            previous_results = [result for _, result in task_exchanges]
            opus_result, group, sub_query = await self.orchestrator(previous_results)

            if "The task is complete:" in opus_result:
                final_output = opus_result
                break

            # Call the appropriate sub-group to execute the sub-task
            sub_task_result = await self.sub_group(group, sub_query)

            if sub_task_result is None:
                self.console.print(f"[bold red]Sub-group {group} failed to execute the task: {sub_query}[/bold red]")
                break

            task_exchanges.append((group, sub_task_result))
            sub_tasks.append(sub_query)

        # Call orchestrator to refine the results into the final output
        final_output = await self.opus_refine([result for _, result in task_exchanges])

        self.console.print(Panel(final_output, title="[bold green]Objective Achieved[/bold green]", title_align="left", border_style="green"))
        return final_output

async def run(objective):
    orchestrator = TaskOrchestrator(objective)
    await orchestrator()

if __name__ == "__main__":
    objective = input("请输入您想分析的目标:")
    print(asyncio.run(run(objective)))

