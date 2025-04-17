import json
import os
from typing import Union
import requests
from fastapi import FastAPI, Body, Response 
from ollama import Client

app = FastAPI()


client = Client(host="http://localhost:11434")
client.pull("gemma3:1b")


def get_weather(place_name):
    result = requests.get(f"https://wttr.in/{place_name}?format=%C+%t")
    print("RESULT IN GET WEATHER", result.text)
    return result.text

def run_command(command):
    print("GOT THE COMMANDS", command)
    os.system(command)
    return f"run this {command} in the terminal"



available_tools = {
    "get_weather": {
        "fn": get_weather,
        "description": "call a api and get the temp of the request query",
    },
    "run_command":{
        "fn": run_command,
        "description": "get the command and run the command in the terminalss"
    }
}

system_prompt = """
You are a Help assistant for the user and answer the user query in a very helpful 
You operate in a loop of start -> plan -> action -> obeserve -> output
For the given user query, reason step by step and use the available tools as needed.

Rules:
    - Always respond with one JSON Object per step.
    - Wait for the observation after an Action before proceeding.
    - Use the availabe tool fully to complete the task.
    - Validate the input before executing the commands

Available Tools:
    - get_weather(place_name): Give the back the Weather details
    - run_command(command): Run the command in the terminals

Output JSON fromat:
{
    "step": "plan" | "action" | "observe" | "output",
    "content" :"string",
    "function": "name of the function (only for the action step),
    "input":"input for the function (only for action step)
}

Example : What is the temp of Newyork
{"step": "plan", "content": "I need to find the Temp of the place name Newyork"}
{"step":"action", "function":"get_weather", "place_name":"Newyork" }
{"step":"action", "function":"run_command", "command":"ls" }
{"step":"observer", "content": "26 degree C"}
{"step":"output", "content": "The Temperaterin nework is with moderate it Temp is 26 degree celcius"}


"""

message = [{"role": "system", "content": system_prompt}]


# def extract_json_block(text):
#     match = re.search(r"```json\n(.*?)```", text, re.DOTALL)
#     if match:
#         json_str = match.group(1)
#         return json.loads(json_str)
#     return None


@app.post("/")
def home(input: str = Body(..., description="Chat Message")):
    print("INPUT", input)

    message.append({"role": "user", "content": input})

    while True:
        response = client.chat(model="gemma3:1b", format="json", messages=message)
        print(response["message"]["content"])
        print(type(response["message"]["content"]))
        parsed_output = json.loads(response["message"]["content"])

        message.append({"role": "assistant", "content": json.dumps(parsed_output)})

        step = parsed_output.get("step")

        if step == "plan":
            print(f"🧐: {parsed_output.get('content')}")
            continue

        if step == "action":
            tool_name = parsed_output.get("function")
            tool_input = parsed_output.get("place_name")
            comand_input = parsed_output.get("command")
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
                    print('RESULT FORM API', result)
                    message.append(
                    {
                        "role": "assistant",
                        "content": json.dumps({"step": "observe", "content": result}),
                    }
                )
                if tool_name == "run_command":
                    result = available_tools[tool_name]["fn"](comand_input)
                    message.append({
                        "role": "assistant",
                        "content": json.dumps({"step": "observe", "content": result})
                    })


        if step == "output":
            print(f"🤖: {parsed_output.get('content')}")
            return parsed_output.get("content")
        # json_data = json.dumps(response["message"]["content"], indent=2)
        # parsed = extract_json_block(response["message"]["content"])
        # print(parsed)
        # print(type(parsed))
