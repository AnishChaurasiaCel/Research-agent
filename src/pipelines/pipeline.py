from src.agents.agents import web_search_agent, content_reader_agent, writer_chain,critic_chain
from rich import print


def research_pipeline_stream(topic: str):
    """Same pipeline as research_pipelin, yielding a status update after each step
    so a UI can show which step is currently running."""

    # Memory state
    state = {}

    # search agent
    yield {"step": "search", "status": "running"}
    web_result = web_search_agent.invoke({
        "messages": [
            {"role": "user", "content": f"Find the readable and detailed information about: {topic}"}
        ]
    })
    state['search_result'] = web_result["messages"][-1].content
    yield {"step": "search", "status": "done", "data": state['search_result']}

    # content reader agent
    yield {"step": "scrape", "status": "running"}
    scrapp = content_reader_agent.invoke({
        'messages': [
            { "role":"user",
             "content": f"Based on the following search result about {topic}"
             f"Pick the most relevant url and scrape it for the deeper content.\n\n"
             f"Search results: {state['search_result']}"
             }
        ]
    })
    state['scrapped_result'] = scrapp["messages"][-1].content
    yield {"step": "scrape", "status": "done", "data": state['scrapped_result']}

    # combine search + scraped content for the writer
    combine_result = (
        f"""
    SEARCH RESULTS:
    {state['search_result']}

    SCRAPED CONTENT:
    {state['scrapped_result']}
    """
    )

    # calling writer chain..
    yield {"step": "write", "status": "running"}
    research = writer_chain.invoke({
        "topic": topic,
        "research": combine_result
    })
    state['final_report'] = research
    yield {"step": "write", "status": "done", "data": state['final_report']}

    # calling critic chain..
    yield {"step": "critique", "status": "running"}
    state['critique'] = critic_chain.invoke(
        {
            "report": research
        }
    )
    yield {"step": "critique", "status": "done", "data": state['critique']}

    # final combined state
    yield {"step": "final", "status": "done", "data": state}






