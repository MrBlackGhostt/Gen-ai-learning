from openai import OpenAI
from dotenv import load_dotenv
import os
from langchain_community.document_loaders import WebBaseLoader
import nest_asyncio
from bs4 import BeautifulSoup
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
import requests

load_dotenv()
nest_asyncio.apply()
# api_key = os.getenv("GEMINI_API_KEY")
# print(api_key)

client = OpenAI(
    api_key="",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
# input = [{"role": "user", "content": "Hi there"}]

embedder = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key="",
)

# loader = WebBaseLoader("https://chaidocs.vercel.app/")

# url = "https://chaidocs.vercel.app/youtube/getting-started/"
# # url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
# # Make a GET request to fetch the raw HTML content
# html_content = requests.get(url).text

# # Parse the html content
# soup = BeautifulSoup(html_content)
# allLinks = soup.find_all("a", class_="astro-3ii7xxms")
# links = []
# count = 0
# for link in allLinks:
#     # count += 1

#     links.append("https://chaidocs.vercel.app" + link.get("href"))

#     # print("/n", link.get("href"))

# # print("LOOP RUN", count)
# print("LENGTH OF LINKS", len(links))
# print("LINKS", links)


# ITS USE TO LOAD THE HTML FROM THE LIST OF THE LINK
# loader_multiple_pages = WebBaseLoader(links)
# loader_multiple_pages.requests_kwargs = {"verify": False}
# loader_multiple_pages.requests_per_second = 1

# docs = []

# docs_lazy = loader_multiple_pages.aload()


# vector_store = QdrantVectorStore.from_documents(
#     documents=[],
#     url="http://localhost:6333",
#     collection_name="chai_code",
#     embedding=embedder,
# )
# vector_store.add_documents(documents=docs_lazy)

retriver = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="chai_code",
    embedding=embedder,
)

system = """
you are an helpful guider for the user answer in simple and easy way so user can understand and also the provide the resource link too so user can go the page for further understanding
Follow the steps in start => plan => analysis => output

Rules:
Give Output strictly in Given JSON format

Give Output in JSON format 

Example :-
{
    "step": "start" | "plan" | "analysis" | "output"
    "query": "why is .env file is used for"
    "answer": "Its used for putting the key of your database or openAi etc
}

Example: what is fs?
[
    {"step": "start", "content": "user ask what is fs?"}
    {"step": "plan", "content": "in the context of coding fs is a modeule so user may be want to know about the fs package"}
    {"step": "analysis", "content": "from the data i got i find out fs is a package which we can used to read file form pc"}
    {"step": "output", "content": "fs is a package which we can used to read file form pc"}
    
]
"""

message = [{"role": "system", "content": system}]


query = input("Please enter your query: ")
search_result = retriver.similarity_search(query)
# print("RESULT :=> ", search_result[0].page_content)

message.append({"role": "assistant", "content": search_result[0].page_content})
message.append({"role": "user", "content": query})

while True:
    res = client.chat.completions.create(
        model="gemini-2.0-flash-lite",
        messages=message,
        response_format={"type": "json_object"},
    )

    respond = res.choices[0].message.content
    print("RESPOND", respond)
    break
