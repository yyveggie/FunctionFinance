from colorama import Fore, Style
from langchain.schema import HumanMessage, SystemMessage 
from . import AgentDetails, Agent

class TWOAI:
    """
    Class representing an AI that can engage in a conversation with another AI.
    
        ai_details (AIDetails): Details of the AI including name and objective.
        model (str): The model used by the AI.
        system_prompt (str): The prompt for the AI conversation system.
        max_tokens (int): The maximum number of tokens to generate in the AI response.
        num_context (int): The number of previous messages to consider in the AI response.
        extra_stops (list): Additional stop words to include in the AI response.
        exit_word (str): The exit word to use in the AI response. Defaults to "<DONE!>".
        max_exit_words (int): The maximum number of exit words to include in the AI responses for the conversation to conclude. Defaults to 2.
    """
    def __init__(
            self, 
            agent_details: AgentDetails,
            system_prompt: str,
            max_tokens: int=4094, 
            num_context: int=4094, 
            extra_stops: list[str] = [],
            exit_word: str = "<DONE!>",
            temperature: float = 0.7,
            max_exit_words: int = 2
        ) -> None:
        self.agent_details = agent_details
        self.max_tokens = max_tokens
        self.num_context = num_context
        self.extra_stops = extra_stops
        self.temperature = temperature

        self.messages = ""
        self.current_agent = agent_details[0]

        self.exit_word = exit_word
        self.exit_word_count = 0
        self.max_exit_words = max_exit_words

        self.models = {agent['name']: agent['model'] for agent in agent_details}

    def bot_say(self, msg: str, color: str = Fore.LIGHTGREEN_EX):
        print(color + msg.strip() + "\t\t" + Style.RESET_ALL )

    def get_opposite_ai(self) -> Agent:
        if self.current_agent['name'] == self.agent_details[0]['name']:
            return self.agent_details[1]
        return self.agent_details[0]

    def next_response(self, ticker, user_knowledge, image_data, initial_analysis, first_round, show_output: bool = False) -> str:
        if len(self.agent_details) < 2:
            raise Exception("Not enough AI details provided")

        current_model = self.models[self.current_agent['name']]

        # 在函数开头定义instructions变量
        instructions = f"{self.current_agent['objective']}"

        if first_round:
            for agent in self.agent_details:
                if agent['name'] not in initial_analysis:
                    instructions = f"{agent['objective']}"
                    user_prompt = f"{agent['user_prompt']}"
                    text = [
                        SystemMessage(content=instructions),
                        HumanMessage(
                            content=[
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{image_data}",  # noqa: E501 # type: ignore
                                    },
                                },
                                {"type": "text", "text": user_prompt},
                            ]
                        )
                    ]
                    
                    # 将模型生成的分析结果存储在initial_analysis字典中
                    response = current_model.invoke(text)
                    initial_analysis[agent['name']] = response.content.strip()

            self.current_agent = self.get_opposite_ai()
            text = initial_analysis[self.current_agent['name']]
        else:
            text = initial_analysis[self.current_agent['name']]

        self.messages += text + "\n"

        messages = [
            SystemMessage(content=instructions),
            HumanMessage(content=self.messages)
        ]

        if show_output:
            print(Fore.YELLOW + f"{self.current_agent['name']} is thinking..." + Style.RESET_ALL, end='\r')

        resp = current_model.invoke(messages)
        text: str = resp.content.strip()

        if not text:
            print(Fore.RED + f"Error: {self.current_agent['name']} response was empty, trying again." + Style.RESET_ALL)
            return self.next_response(ticker, user_knowledge, image_data, initial_analysis, first_round, show_output)

        if not text.startswith(self.current_agent['name'] + ": "):
            text = self.current_agent['name'] + ": " + text
        self.messages += text + "\n"

        if show_output:
            print("\x1b[K", end="")  # remove "thinking..." message
            if self.agent_details.index(self.current_agent) == 0:
                self.bot_say(text)
            else:
                self.bot_say(text, Fore.BLUE)

        self.current_agent = self.get_opposite_ai()
        return text, first_round # type: ignore

    def start_conversation(self, ticker, user_knowledge, image_data):
        initial_analysis = {}
        first_round = True
        try:
            while True:
                res, is_first_round = self.next_response(ticker, user_knowledge, image_data, initial_analysis, first_round, show_output=True)
                first_round = False  # 在第一次对话后,将first_round设置为False
                if not is_first_round and self.exit_word in res:
                    self.exit_word_count += 1
                if self.exit_word_count == self.max_exit_words:
                    print(Fore.RED + "The conversation was concluded..." + Style.RESET_ALL)
                    return
        except KeyboardInterrupt:
            print(Fore.RED + "Closing Conversation..." + Style.RESET_ALL)
            return