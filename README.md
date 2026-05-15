# 🔬 Multi-Agent Research Assistant

An AI agent that autonomously breaks down complex research questions, uses multiple tools to gather information, and produces professional structured reports.

**[🔴 Live Demo](https://your-app.streamlit.app)** | **[GitHub](https://github.com/yourusername/research-agent)**

---

## What It Does

Ask any complex question and the agent:
1. **Plans** — breaks the question into sub-tasks
2. **Researches** — searches the web, runs calculations, generates content
3. **Synthesizes** — combines all findings
4. **Reports** — writes a structured professional report

You can watch every reasoning step in real time.

---

## Architecture

```
User Question
      ↓
LangChain Agent (GPT-4o-mini)
      ↓
Plans sub-tasks autonomously
      ↓
┌─────────────────────────────────┐
│  Tool calls (in parallel):      │
│  • web_search → DuckDuckGo API  │
│  • calculator → safe math eval  │
│  • summarize_text → GPT-4o-mini │
│  • get_current_date → datetime  │
│  • generate_report_section      │
└─────────────────────────────────┘
      ↓
Synthesize all results
      ↓
Structured Report + Tool trace
```

---

## Tech Stack

| Component | Technology |
|---|---|
| Agent Framework | LangChain AgentExecutor |
| LLM | GPT-4o-mini (tool use / function calling) |
| Web Search | DuckDuckGo API (free, no key) |
| Frontend | Streamlit |
| Tool Calling | OpenAI Function Calling |

---

## Run Locally

```bash
git clone https://github.com/yourusername/research-agent
cd research-agent

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Edit .env — add your OpenAI key
streamlit run streamlit_app.py
```

---

## Key Interview Talking Points

> "I built a multi-agent research system using LangChain's AgentExecutor with OpenAI function calling. The agent autonomously decides which tools to use — web search, calculator, text summarization — based on the question. It uses GPT-4o-mini's native tool use capability to call functions, processes the results, and iterates up to 8 times to gather enough information before synthesizing a final report. The streaming callback sends each tool call to the UI in real time so users can see the agent's reasoning process."

---

## What Makes This Advanced

- **Autonomous tool selection** — agent decides what to call, not you
- **Multi-turn memory** — remembers previous questions in the session
- **Real-time reasoning trace** — see every tool call as it happens
- **Iterative research** — agent loops until it has enough information
- **Function calling** — uses OpenAI's native tool use, not prompt tricks
