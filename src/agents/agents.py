from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.tools.tools import web_scrape_url, web_search
from src.prompts.prompt import (
    WEB_SEARCH_SYSTEM_PROMPT,
    CONTENT_READER_SYSTEM_PROMPT,
    RESEARCH_SYSTEM_PROMPT,
    RESEARCH_HUMAN_PROMPT,
    CRITIC_SYSTEM_PROMPT,
    CRITIC_HUMAN_PROMPT,
)

llm = ChatOllama(
    model='qwen3:1.7b'
)

parser = StrOutputParser()

# 1st Agent - web search agent
web_search_agent = create_agent(
    model= llm,
    tools=[web_search],
    system_prompt = WEB_SEARCH_SYSTEM_PROMPT
)

# 2nd Agent - web reader agent
content_reader_agent = create_agent(
    model= llm,
    tools=[web_scrape_url],
    system_prompt = CONTENT_READER_SYSTEM_PROMPT
)

research_prompt = ChatPromptTemplate.from_messages([
    ("system", RESEARCH_SYSTEM_PROMPT),
    ("human", RESEARCH_HUMAN_PROMPT)
])

critic_prompt = ChatPromptTemplate.from_messages([
    ("system", CRITIC_SYSTEM_PROMPT),
    ("human", CRITIC_HUMAN_PROMPT)
])

writer_chain = research_prompt | llm | parser
critic_chain = critic_prompt | llm | parser