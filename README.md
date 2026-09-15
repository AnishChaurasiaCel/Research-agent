# Research Agent

A multi-agent research assistant with a Streamlit UI. Give it a topic, and it
searches the web, extracts the most relevant article, writes a structured
research report with citations, and critiques its own output — streaming
progress for each step live in the browser.

## Features

- **End-to-end automated research** — go from a single topic string to a
  cited, structured report with one click.
- **Live multi-step progress UI** — each pipeline stage (search, scrape,
  write, critique) streams its status to the Streamlit sidebar as it runs,
  instead of blocking on one long spinner.
- **Web search grounding** — uses DuckDuckGo (`ddgs`) so the agent works from
  fresh, real search results rather than the model's training data alone.
- **Automatic source selection & scraping** — a dedicated agent picks the
  single most relevant URL from the search results and extracts its main
  readable content (`trafilatura`, with a BeautifulSoup/`readability`
  fallback for pages it can't parse).
- **Cited report generation** — the writer is constrained to only use the
  gathered research and must include a References section with the original
  source URLs, reducing hallucinated facts.
- **Self-critique step** — a critic chain scores the generated report,
  lists strengths and areas to improve, and gives a verdict, so the UI
  doesn't just show a report but also its quality assessment.
- **Downloadable output** — the final report can be downloaded as a
  Markdown (`.md`) file directly from the UI.
- **Fully local LLM inference** — runs on a local [Ollama](https://ollama.com/)
  model, so no external LLM API key or paid API is required.

## Architecture

The application follows a simple, linear multi-agent pipeline. Each stage
consumes the previous stage's output and streams a status update back to the
UI as it completes:

```
                 ┌─────────────────────┐
   topic ──────► │   Streamlit UI       │ ◄── live status updates
                 │      (app.py)        │      per pipeline step
                 └──────────┬───────────┘
                            │ research_pipeline_stream(topic)
                            ▼
                 ┌─────────────────────┐
                 │ 1. Web Search Agent  │  tool: web_search (DuckDuckGo)
                 └──────────┬───────────┘
                            ▼
                 ┌─────────────────────┐
                 │ 2. Content Reader    │  tool: web_scrape_url
                 │    Agent             │  (trafilatura / readability)
                 └──────────┬───────────┘
                            ▼
                 ┌─────────────────────┐
                 │ 3. Report Writer     │  prompt | LLM | parser chain
                 │    Chain             │
                 └──────────┬───────────┘
                            ▼
                 ┌─────────────────────┐
                 │ 4. Critic Chain      │  prompt | LLM | parser chain
                 └──────────┬───────────┘
                            ▼
                 ┌─────────────────────┐
                 │ Final state: report, │
                 │ critique, sources    │
                 └─────────────────────┘
```

1. **Web Search** — a LangChain tool-calling agent (`web_search_agent`) uses
   the `web_search` tool (DuckDuckGo via `ddgs`) to find relevant sources for
   the topic.
2. **Content Extraction** — a second tool-calling agent
   (`content_reader_agent`) picks the most relevant URL from the search
   results and scrapes its main readable content via the `web_scrape_url`
   tool.
3. **Report Writing** — an LLM chain (`writer_chain`) combines the search
   results and scraped content into a detailed, cited research report.
4. **Critique** — a final LLM chain (`critic_chain`) scores the report and
   lists its strengths and areas for improvement.

Each step yields a status update (`{"step": ..., "status": ..., "data": ...}`)
from [`src/pipelines/pipeline.py`](src/pipelines/pipeline.py), which
[`app.py`](app.py) consumes to update per-step status boxes in real time,
then renders the final report, critique, and raw sources in separate tabs
with a markdown download option.

All agents and chains share a single local [Ollama](https://ollama.com/)
model (`qwen3:1.7b` by default) via `langchain-ollama` — no external LLM API
key is required.

## Tech stack

| Layer              | Technology |
|---------------------|------------|
| UI                   | [Streamlit](https://streamlit.io/) |
| Agent framework      | [LangChain](https://www.langchain.com/) (`langchain`, `langchain-core`, `create_agent`) |
| LLM runtime          | [Ollama](https://ollama.com/) via `langchain-ollama` (`qwen3:1.7b`) |
| Web search           | `ddgs` (DuckDuckGo Search) |
| Content extraction   | `trafilatura`, with `readability-lxml` + `beautifulsoup4` fallback |
| HTTP client          | `requests` |
| Language / runtime   | Python 3.13 |

## Project structure

```
app.py                     Streamlit UI and pipeline runner
src/
  agents/agents.py         Agent and chain definitions (search, reader, writer, critic)
  prompts/prompt.py         System/human prompt templates used by the agents
  pipelines/pipeline.py     Orchestrates the 4-step research pipeline
  tools/tools.py            web_search and web_scrape_url tools
```

## Prerequisites

- Python 3.13
- [Ollama](https://ollama.com/) installed and running locally, with the
  model pulled:
  ```
  ollama pull qwen3:1.7b
  ```

## Setup

1. Create and activate a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the app

```
streamlit run app.py
```

Then open the app in your browser, enter a research topic in the sidebar,
and click **Run Research**.

## Notes

- Web search relies on DuckDuckGo via `ddgs`; results and scraping quality
  depend on the target site's structure and availability.
- Scraped content is capped at 4000 characters per source
  (`MAX_SCRAPE_CHARS` in [src/tools/tools.py](src/tools/tools.py)) to keep
  requests within the local model's context window.
