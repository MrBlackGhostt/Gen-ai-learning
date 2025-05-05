from openai import OpenAI
from dotenv import load_dotenv
import os
from langsmith.wrappers import wrap_openai

load_dotenv()

key = os.getenv("GEMINI_API_KEY")

client = wrap_openai(
    OpenAI(
        api_key=key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
)

system_prompt = """
You are an Ai assistant which help to guide which LLM to pick for the given query for the task given by the user you pick the best LLM which is best for the job. 
choose from given LLM GPT-4, Claude 3.7 Sonnet (Anthropic), Gemini, Grok-3 (xAI), DeepSeek-R1 (DeepSeek).

GPT-4 - Its good in understanding human-like text and good in creative writing, technical explanations

Claude 3.7 Sonnet (Anthropic) - Strengths: Constitutional AI principles, "extended thinking mode" for iterative refinement, and accuracy in coding/web development.
Use Cases: Business automation, sensitive data handling, and ethical AI deployment

Gemini - Its good for the scientific research and large pdf and and good in solving  problem-solvind and data analysis

Grok-3 (xAI)- 
Strengths: Real-time internet scanning ("DeepSearch"), humor-infused interactions, and advanced problem decomposition.
Use Cases: News analysis, coding assistance, and dynamic customer support

DeepSeek-R1 (DeepSeek)-
Strengths: Specializes in mathematical reasoning, logical inference, and coding. Uses reinforcement learning for self-verification and cost efficiency (30x cheaper than competitors).
Use Cases: STEM research, genomic data analysis, and enterprise RAG integration


RULES 
Strictly Answer in JSON fromat only
Given LLM is best in solving the user query
OUTPUT 
{
    "query" : "string"
    "message": "its a message which tells why pick this LLM"
    "result": "Name of the LLM"
}

Example: 
{
    "query": "which llm is good for the coding"
    "message" "For the Coding basic things like add and multiply fun use DeepSeek-R1 (DeepSeek) for the big project use the Claude 3.7 Sonnet (Anthropic)"
    "result": "Claude 3.7 Sonnet (Anthropic)"
}
"""

messages = [{"role": "system", "content": system_prompt}]

while True:
    query = input("How may I assist you today?: ")
    messages.append({"role": "user", "content": query})

    res = client.chat.completions.create(
        model="gemini-2.0-flash",
        response_format={"type": "json_object"},
        messages=messages,
    )

    print("------------RESULT-----------", "/n", res.choices[0].message.content)
