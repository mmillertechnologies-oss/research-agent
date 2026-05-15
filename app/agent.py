"""
Research Agent
Breaks complex questions into sub-tasks, uses tools, writes a structured report
This is what makes Project 2 impressive — it THINKS and ACTS autonomously
"""

import os
import time
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.messages import AIMessage, HumanMessage
from app.tools import ALL_TOOLS
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)


# ── Streaming callback — sends steps to UI in real time ──────────────────────
class StreamingCallback(BaseCallbackHandler):
    def __init__(self, step_callback=None):
        self.step_callback = step_callback
        self.steps = []
        self.token_count = 0

    def on_tool_start(self, serialized, input_str, **kwargs):
        tool_name = serialized.get("name", "tool")
        step = {"type": "tool_start", "tool": tool_name, "input": str(input_str)[:200]}
        self.steps.append(step)
        if self.step_callback:
            self.step_callback(step)

    def on_tool_end(self, output, **kwargs):
        step = {"type": "tool_end", "output": str(output)[:300]}
        self.steps.append(step)
        if self.step_callback:
            self.step_callback(step)

    def on_llm_end(self, response, **kwargs):
        self.token_count += 100  # rough estimate


# ── Agent system prompt ───────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert research assistant with access to powerful tools.

Your job is to thoroughly research any topic and produce a professional, well-structured report.

When given a research question:
1. PLAN: Break it into 3-5 sub-questions that need answering
2. RESEARCH: Use your tools to find accurate information for each sub-question
3. CALCULATE: Use the calculator for any numbers, percentages, or comparisons
4. SYNTHESIZE: Combine all findings into a coherent, professional report
5. REPORT: Write a clear final report with an executive summary, key findings, and conclusion

Always:
- Use web_search for current facts and data
- Use calculator for any math
- Use get_current_date when timing matters
- Cite what you find
- Be thorough but concise
- Write in professional business language

Your final answer should always be a complete, well-structured report."""


def create_agent(step_callback=None):
    """Create the research agent with all tools"""
    callback = StreamingCallback(step_callback=step_callback)

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        streaming=True,
        callbacks=[callback]
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    agent = create_openai_tools_agent(llm, ALL_TOOLS, prompt)

    executor = AgentExecutor(
        agent=agent,
        tools=ALL_TOOLS,
        verbose=True,
        max_iterations=8,
        handle_parsing_errors=True,
        callbacks=[callback]
    )

    return executor, callback


def run_research(question: str, step_callback=None, history: list = None) -> dict:
    """
    Run the research agent on a question.
    Returns the full report and metadata.
    """
    start = time.time()

    try:
        agent, callback = create_agent(step_callback=step_callback)

        # Build chat history for multi-turn
        chat_history = []
        if history:
            for msg in history[-4:]:  # last 4 messages for context
                if msg["role"] == "user":
                    chat_history.append(HumanMessage(content=msg["content"]))
                else:
                    chat_history.append(AIMessage(content=msg["content"]))

        result = agent.invoke({
            "input": question,
            "chat_history": chat_history
        })

        latency = round(time.time() - start, 1)
        report = result.get("output", "No report generated")

        return {
            "report": report,
            "steps": callback.steps,
            "latency": latency,
            "tokens_est": callback.token_count + len(question + report) // 4,
            "tools_used": list(set([
                s["tool"] for s in callback.steps
                if s.get("type") == "tool_start"
            ]))
        }

    except Exception as e:
        logger.error(f"Agent error: {e}")
        return {
            "report": f"Research failed: {str(e)}",
            "steps": [],
            "latency": round(time.time() - start, 1),
            "tokens_est": 0,
            "tools_used": []
        }
