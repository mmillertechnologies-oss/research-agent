"""
Agent Tools
The research agent uses these tools to answer complex questions
Each tool is a real capability the agent can call
"""

import os
import json
import math
import urllib.request
import urllib.parse
from datetime import datetime
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


def get_llm():
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.1,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )


@tool
def web_search(query: str) -> str:
    """
    Search the web for current information about a topic.
    Use this for facts, news, recent events, or anything needing live data.
    Input: a search query string
    """
    try:
        # Using DuckDuckGo instant answer API — completely free, no key needed
        encoded = urllib.parse.quote(query)
        url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1"
        req = urllib.request.Request(url, headers={"User-Agent": "ResearchAgent/1.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())

        results = []

        # Abstract (main answer)
        if data.get("Abstract"):
            results.append(f"Summary: {data['Abstract']}")
            if data.get("AbstractURL"):
                results.append(f"Source: {data['AbstractURL']}")

        # Answer (short fact)
        if data.get("Answer"):
            results.append(f"Answer: {data['Answer']}")

        # Related topics
        topics = data.get("RelatedTopics", [])[:3]
        for t in topics:
            if isinstance(t, dict) and t.get("Text"):
                results.append(f"- {t['Text'][:200]}")

        if results:
            return "\n".join(results)
        else:
            return f"No direct results found for '{query}'. The agent will use its knowledge to answer."

    except Exception as e:
        return f"Search unavailable ({str(e)}). Using knowledge base instead."


@tool
def calculator(expression: str) -> str:
    """
    Perform mathematical calculations.
    Input: a math expression like '(150 * 0.07) + 200' or 'sqrt(144)'
    Supports: +, -, *, /, **, sqrt, log, sin, cos, tan, pi, e
    """
    try:
        # Safe math evaluation
        safe_names = {
            "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "pi": math.pi, "e": math.e, "abs": abs,
            "round": round, "pow": pow, "floor": math.floor, "ceil": math.ceil
        }
        result = eval(expression, {"__builtins__": {}}, safe_names)
        return f"Result: {round(result, 6)}"
    except Exception as e:
        return f"Calculation error: {str(e)}. Please check the expression."


@tool
def summarize_text(text: str) -> str:
    """
    Summarize a long piece of text into key bullet points.
    Use this when you have a lot of text and need to extract the key points.
    Input: the text to summarize
    """
    if len(text) < 200:
        return text

    llm = get_llm()
    prompt = f"""Summarize this text into 4-5 clear bullet points.
Focus on the most important facts and insights.

Text:
{text[:3000]}

Bullet point summary:"""

    result = llm.invoke(prompt)
    return result.content


@tool
def get_current_date(query: str = "") -> str:
    """
    Get the current date and time.
    Use this when the question involves current date, time, or recent events.
    """
    now = datetime.now()
    return f"Current date and time: {now.strftime('%A, %B %d, %Y at %I:%M %p')}"


@tool
def generate_report_section(topic: str) -> str:
    """
    Generate a detailed, well-structured section about a specific topic.
    Use this to write comprehensive explanations on any subject.
    Input: the topic or question to write about in detail
    """
    llm = get_llm()
    prompt = f"""Write a detailed, professional report section about:
{topic}

Requirements:
- Be specific and informative
- Include relevant facts, statistics where applicable
- Write 3-4 solid paragraphs
- Use professional language suitable for a business report
- Structure the content clearly

Report section:"""

    result = llm.invoke(prompt)
    return result.content


# All tools available to the agent
ALL_TOOLS = [
    web_search,
    calculator,
    summarize_text,
    get_current_date,
    generate_report_section
]
