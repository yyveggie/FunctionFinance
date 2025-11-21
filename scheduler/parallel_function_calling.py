import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import json
import requests
import time
import os
import serpapi
from openai import OpenAI
from config_loader import OPENAI_API_KEY, GPT4O, SERPAPI_API_KEY

openai_key = OPENAI_API_KEY
client = OpenAI(api_key=openai_key)

# Function to get weather information
def get_weather(city, wapi_key="28c52a08e510f604d92b3be02c5e0b5b"):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={wapi_key}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()
        return {
            "temperature": weather_data["main"]["temp"],
            "weather": weather_data["weather"][0]["description"],
            "city": weather_data["name"],
        }
    except requests.exceptions.HTTPError as err:
        return f"HTTP Error: {err}"
    except requests.exceptions.RequestException as err:
        return f"Error: {err}"
    except KeyError:
        return "Error: Problem parsing weather data."


# Function to get organic search results
def get_organic_results(
    query, api_key=SERPAPI_API_KEY
):
    client = serpapi.Client(api_key=api_key)
    params = {"engine": "google", "num": "5", "q": query, "api_key": api_key}
    results = client.search(params).get_dict()
    organic_results = results.get("organic_results", [])
    urls = [result["link"] for result in organic_results]
    return urls


def get_chat_response(user_input, model=GPT4O):
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Help the USER with writing.",
                },
                {"role": "user", "content": user_input},
            ],
        )
        # Extract and return the chat response text
        chat_response_text = completion.choices[0].message["content"]
        return chat_response_text

    except Exception as e:
        # Handle any exceptions that occur during the API request
        return f"An error occurred: {str(e)}"


# New function to generate image using DALL-E 3
def generate_image(prompt, size="1024x1024", quality="standard", n=1):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality=quality,
            n=n
        )
        return response.data[0].url
    except Exception as e:
        return f"An error occurred while generating the image: {str(e)}"


# Updated list_tools with the new DALL-E 3 function
list_tools = [
    # Existing tools remain unchanged
    {
        "type": "function",
        "function": {
            "name": "get_organic_results",
            "description": "Fetch news URLs based on a search query",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "api_key": {"type": "string", "description": "API key for SerpApi"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Fetch weather information for a given city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"},
                    "api_key": {
                        "type": "string",
                        "description": "API key for OpenWeatherMap",
                    },
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_chat_response",
            "description": "Provide chat responses to user queries",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_input": {"type": "string", "description": "User's query"},
                    "model": {"type": "string", "description": "GPT model to use"},
                },
                "required": ["user_input"],
            },
        },
    },
    # New DALL-E 3 tool
    {
        "type": "function",
        "function": {
            "name": "generate_image",
            "description": "Generate an image using DALL-E 3",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Description of the image to generate"},
                    "size": {"type": "string", "description": "Size of the image (e.g., '1024x1024')"},
                    "quality": {"type": "string", "description": "Quality of the image ('standard' or 'hd')"},
                    "n": {"type": "integer", "description": "Number of images to generate"},
                },
                "required": ["prompt"],
            },
        },
    },
]

# Updated assistant creation with new instructions
assistant = client.beta.assistants.create(
    name="ParallelFunction",
    instructions="您是一位助手，能够获取新闻文章、提供天气信息、根据用户查询进行撰写，以及使用DALL-E 3生成图像。",
    model=GPT4O,
    tools=list_tools,
)

# Color codes and other parts of the script remain unchanged

# Updated function dispatch table
function_dispatch_table = {
    "get_organic_results": get_organic_results,
    "get_weather": get_weather,
    "get_chat_response": get_chat_response,
    "generate_image": generate_image,
}

PINK = r"\\033[95m"
# ANSI escape code for cyan color
CYAN = r"\\033[96m"
# ANSI escape code for yellow color
YELLOW = r"\\033[93m"
# ANSI escape code to reset to default color
RESET_COLOR = r"\\033[0m"

# Step 2: Create a Thread
thread = client.beta.threads.create()

# Step 3: Add a Message to a Thread with user input
user_message_content = input("输入你的请求：")
message = client.beta.threads.messages.create(
    thread_id=thread.id, role="user", content=user_message_content
)

# Step 4: Run the Assistant
run = client.beta.threads.runs.create(
    thread_id=thread.id, assistant_id=assistant.id)

# Define a dispatch table
function_dispatch_table = {
    "get_organic_results": get_organic_results,
    "get_weather": get_weather,
    "get_chat_response": get_chat_response,
    "generate_image": generate_image,  # Ensure this line is present
}

while True:  # Wait for 5 seconds
    time.sleep(5)

    # Retrieve run_status
    run_status = client.beta.threads.runs.retrieve(
        thread_id=thread.id, run_id=run.id)

    # Comment out or remove the following Line to prevent verbose output
    # print (run_status.model_dump_json(indent=4))

    # If run is completed, get messages
    if run_status.status == "completed":
        messages = client.beta.threads.messages.list(thread_id=thread.id)

        # Loop through messages and print content based on role
        for msg in messages.data:
            role = msg.role
            content = msg.content[0].text.value
            # Only print the final message content
            if role == "assistant":
                print(f"{YELLOW}{role.capitalize()}: {content}{RESET_COLOR}")
        break
    elif run_status.status == "requires_action":
        print(f"{PINK} Requires action:{RESET_COLOR}")
        required_actions = run_status.required_action.submit_tool_outputs.model_dump()

        # Print the required action in the desired format
        tool_calls_output = {
            "tool_calls": [
                {
                    "id": action["id"],
                    "function": {
                        "arguments": action["function"]["arguments"],
                        "name": action["function"]["name"],
                    },
                    "type": "function",
                }
                for action in required_actions["tool_calls"]
            ]
        }
        print(f"{PINK}{tool_calls_output}{RESET_COLOR}")

        tools_output = []

        for action in required_actions["tool_calls"]:
            func_name = action["function"]["name"]
            arguments = json.loads(action["function"]["arguments"])
            func = function_dispatch_table.get(func_name)
            if func:
                result = func(**arguments)
                # Ensure the output is a JSON string
                output = json.dumps(result) if not isinstance(
                    result, str) else result
                tools_output.append(
                    {"tool_call_id": action["id"], "output": output})
            else:
                print(f"Function {func_name} not found")
        # Submit the tool outputs to Assistant API
        client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id, run_id=run.id, tool_outputs=tools_output
        )
    else:
        print("等待运行中...")
        time.sleep(5)
