import json
import os

import requests
from fastapi import FastAPI, Body
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print("APIKEY", api_key)

client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


app = FastAPI()


def get_weather(place_name: str) -> str:
    try:
        result = requests.get(f"https://wttr.in/{place_name}?format=%C+%t", timeout=5)
        result.raise_for_status()
        return result.text.strip()
    except requests.RequestException as e:
        return f"Error fetching weather: {e}"


def run_command(command):
    print("GOT THE COMMANDS", command)
    result = os.system(command=command)
    print("RESULT IN THE RUN_COMMAND", result)
    return result


def check_file(file_name):
    print("INSIDE THE CHECK_FILE")
    result = os.path.exists(file_name)
    print("RESULT IN THE CHECK_FILE", result)
    if not result:
        return f"the {file_name} is not created do make the command and run it again"

    return f"the {file_name} is created successfully"


available_tools = {
    "get_weather": {
        "fn": get_weather,
        "description": "call a api and get the temp of the request query",
    },
    "run_command": {
        "fn": run_command,
        "description": "Run a shell command in the current directory",
    },
    "check_file": {
        "fn": check_file,
        "description": "Check if a file/folder exists in the current directory",
    },
}

system_prompt = """
You are a expert in creating coding project from scratch Coding assistant for the user and which make create file/folder and write  code inside created file according to the user query append code in the file created
You operate in a loop of start -> plan -> action -> obeserve -> output
For the given user query, reason step by step and use the available tools as needed.

You are capable of running command in shell and editings files

Rules:
    - Always respond with one JSON Object per step.
    - Wait for the observation after an Action before proceding.
    - Use the availabe tool fully to complete the task.
    - Command should be valid not just some random string should be run in terminal also do not take the command from the example
    - Always used to go current directory and then execute the command
    - Validate the input before executing the commands

Available Tools:
    - get_weather(place_name): Give the back the Weather details
    - run_command(command): Run the command in the terminals
    - check_file(file_name): Check the File/Folder is created inthe current directoryu or not
    
Output JSON fromat:
{
    "step": "plan" | "action" | "observe" | "output",
    "content" :"string",
    "function": "name of the function (only for the action step),
    "command":"input for the function (only for action step)
}

Example : What is the temp of Newyork
{"step": "plan", "content": "I need to find the Temp of the place name Newyork"}
{"step":"action", "function":"get_weather", "place_name":"Newyork" }
{"step":"action", "function":"run_command", "command":"ls" }
{"step":"observer", "content": "26 degree C"}
{"step":"output", "content": "The Temperaterin nework is with moderate it Temp is 26 degree celcius"}

Example 1: create nextjs app with typescript tailwindcss

{"step": "plan", "content": "For creating the nextjs app with typescript and tailwindcss, I will run the following command: npx create-next-app@latest --ts --tailwindcss my-app"}
{"step":"action", "function":"run_command", "command":"npx create-next-app@latest --ts --tailwindcss my-app" }
{"step": "plan", "content": "Created the Foleder user ask name Frontend and now i should create a file name Hello.js that user ask"}
{"step":"action", "function":"run_command", "command":"cd Frontend && touch Hello.js" }
{"step":"observer", "content": "Check file is created successfully as per the user Requested if yes then go to the next step if not go back to the action step do the left thing"}
{"step":"output", "content": "As per your req the file is created"}

Example 2: create login page and use tailwindcss for styling
{"step": "plan", "content": "For creating a login page and use tailwindcss for styling, I will create a new file called login.js in the src/app/login directory and add the following code to it."}
{"step":"action", "function":"run_command", "command":"touch src/app/login/login.js" }
{"step":"observer", "content": "I have created a login page and use tailwindcss for styling."}
{"step":"output", "content": "As per your req the file is created"}

Example 3: create folder name backend and inside it create a  crud node backend
{"step": "plan", "content": "Ok i have to create a folder name backend into the current directory and inside it i have to create revalent folders"}
{"step":"action", "function":"run_command", "command":"mkdir backend && cd backend && mkdir models && mkdir routes && mkdir controllers && touch server.js && touch models/userModel.js && touch routes/userRoutes.js && touch controllers/userController.js" }
{"step":"observer", "content": "Create a Backend folder and put the models routed, controler successfully"}
{"step":"output", "content": "As per your req the file is created"}

STRICTLY FOLLOW THE BELOW INSTRUCTIONS
- always use the below code structure for creating nodejs, express, vite applications
- always modify dependent files also
"""

message = [{"role": "system", "content": system_prompt}]


@app.post("/")
def home(input: str = Body(..., description="Chat Message")):

    print("INPUT", input)
    message.append({"role": "user", "content": input})
    while True:
        response = client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=message,
            response_format={"type": "json_object"},
        )

        print(response.choices[0].message.content)

        parsed_output = json.loads(response.choices[0].message.content)

        message.append({"role": "assistant", "content": json.dumps(parsed_output)})

        step = parsed_output.get("step")

        if step == "plan":
            print(f"🧐: {parsed_output.get('content')}")
            continue

        if step == "action":
            tool_name = parsed_output.get("function")
            tool_input = parsed_output.get("place_name")
            comand_input = parsed_output.get("command")
            file_input = parsed_output.get("file_name")

            if isinstance(tool_input, str):
                try:
                    tool_input = json.load(tool_input)
                    print("TOOL INPUT", tool_input)
                except:
                    pass
            if tool_name in available_tools:
                print("BEFORE THE API")
                if tool_name == "get_weather":
                    result = available_tools[tool_name]["fn"](tool_input)
                    print("RESULT FORM API", result)
                    message.append(
                        {
                            "role": "assistant",
                            "content": json.dumps(
                                {"step": "observe", "content": result}
                            ),
                        }
                    )

                if tool_name == "run_command":
                    result = available_tools[tool_name]["fn"](comand_input)
                    message.append(
                        {
                            "role": "assistant",
                            "content": json.dumps(
                                {"step": "observe", "content": result}
                            ),
                        }
                    )
                    continue
                if tool_name == "check_file":
                    print("BEFORE CALLIND THE CHECK_FILE")
                    result = available_tools[tool_name]["fn"](file_input)
                    message.append(
                        {
                            "role": "assistant",
                            "content": json.dumps(
                                {"step": "observe", "content": result}
                            ),
                        }
                    )
                    continue

        if step == "output":
            print(f"🤖: {parsed_output.get('content')}")
            return parsed_output.get("content")
