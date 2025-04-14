import json
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


def get_weather():
    return "26 Degree celcius"


def run_command(command):
    result = os.system(command=command)
    return result


available_tools = {
    "get_weather": {
        "fn": get_weather,
        "desc": 'This is the funcaton for the weather'
    },
    "run_command": {
        "fn": run_command,
        "desc": "this is the fun which take a command and execute and return the result"
    }
}

prompt = """
You are an Ai assistant whoe is expert in breaing down complex problems and then resolve the user query

For the given user input, analyse the input and break down the problem step by step.
Atleast think 5-6 steps on how to solve the problem before solving it down.

The steps are you get a user input, you analyse, you think, you again think for several times and then return an output with explanation and then finally you validate the output as well before giving final result.

Follow the steps in sequence that is "plan", "action", "observe" and  "output" .

Rules:
1. Follow the strict JSON output as per Output schema.
2. Always perform one step at a time and wait for next input
3. Carefully analyse the user query



Output JSON Format:
{{step: :"string",
content: "string" ,
"function": "The name of the function if the step in action",
"input": "The input parameter for the function"
}}

Available Tools: 
- get_weather: Take the city as the input and return the weather 
- run_command:  This is the fun which take a command and execute and return the result 
Example:
Input: What is the weather of newyork.
Output: {{ step: "plan", content: "Alright! The user is intersted in weather query and he is asking a temp of the nework" }}
Output: {{ step: "plan", content: "From the available tool i must call the get_weather" }}
Output: {{ step: "action", function: "get_weather", "input":"newyork" }}
Output: {{ step: "observe", content: "12 degree cel" }}
Output: {{ step: "output", content: "The Weather for newyork seems to be 12 degree" }}
"""

user_input = input("Enter the task: ")
message = [
    {"role": "system", "content": prompt},
]
message.append(
    {"role": "user", "content": user_input},)


while True:
    print("🔁 INSIDE THE WHILE LOOP")

    if not user_input:
        print("⚠️ No user input detected. Exiting loop...")
        break

    print("📤 Sending request to OpenAI API...")
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=message,
        max_tokens=500
    )

    print("📥 Received response from OpenAI.")
    print("🔍 Parsing response...")
    print("🧾 Raw response:", response.choices[0].message.content)

    parsed_output = json.loads(response.choices[0].message.content)
    print("Parsed output:", parsed_output)
    steps = parsed_output.get("step")
    print(f"📌 Current step: {steps}")

    if steps == "plan":
        print(f"🧠 THINKING: {parsed_output.get('content')}")
        message.append(
            {"role": "assistant", "content": json.dumps(parsed_output)})
        continue

    if steps == "action":
        print("🚀 ACTION STEP INITIATED")
        output = parsed_output.get("function")
        input_param = parsed_output.get("input")
        print(f"🔧 Calling function: {output} with input: {input_param}")

        # FIXED THIS LINE
        res = available_tools[output].get("fn")(input_param)

        print(f"📡 Function result: {res}")
        message.append({"role": "assistant", "content": json.dumps(
            {"step": "observe", "content": res})})
        continue

    if steps == "observe":
        print(f"👀 OBSERVING: {parsed_output.get('content')}")
        message.append(
            {"role": "assistant", "content": json.dumps(parsed_output)})
        continue

    print("Parsed output:", parsed_output)  # Debug the response
    steps = parsed_output.get("step")

    if steps == "output":
        print(f"✅ FINAL OUTPUT: {parsed_output.get('content')}")
        user_input = ""
        message = []
        break
    else:
        print("❓ No matching step found. Breaking.")
        break
    print("❓ No matching step found. Breaking.")
