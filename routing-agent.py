from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv("GEMINI_API_KEY")


client = OpenAI(
    api_key="",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

system_prompt = """
You are an Ai assistant which help to guide which LLM to pick for the given query for the task given by the user you pick the best LLM which dis best for the job and cheap in all 
choose from given LLM GPT-4, Claude Gemini Gopher LLaMa

GPT-4 - Its good in understanding human-like text and good in creative writing, technical explanations

Claude - Its good in ethical AI usage and for coding Its generate response while avoiding the harm or bias


Gemini - Its good for the scientific research and large pdf and and good in solving  problem-solvind and data analysis


Gopher - This is good in solving task which require deeep comprehension and reasoning like in the field of medical or law etc.

LLaMA  - Its highly optimized for resaearch Purpose and for academic application, good in understanding complex and technical documnets and provide the detail analysis


RULES 
Strictly Answer in JSON fromat only
Given LLM is best in solving the user query and alos cheap in all provided LLM

OUTPUT 
{
    "query" : "string"
    "message": "its a message which tells why pick this LLM"
    "result": "Name of the LLM"
}

Example: 
{
    "query": "which llm is good for the coding"
    "message" "For the Coding basic things like add and multiply fun use deepseek for the big project use the Claude"
    "result": "Claude"
}
"""

messages = [{"role": "system", "content": system_prompt}]

while True:
    query = input("Enter the your Questions: ")
    messages.append({"role": "user", "content": query})

    res = client.chat.completions.create(
        model="gemini-2.0-flash-lite", messages=messages
    )

    print("------------RESULT-----------", "/n", res.choices[0].message.content)
