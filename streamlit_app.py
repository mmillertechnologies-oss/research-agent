"""
Multi-Agent Research Assistant — Clean UI v2
"""

import streamlit as st
import os, sys, time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.agent import run_research

st.set_page_config(page_title="AgentIQ — Research Assistant", page_icon="🔬", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
html,body,[class*="css"]{font-family:'Sora',sans-serif!important}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding:2rem 2.5rem 4rem!important;max-width:1100px}

section[data-testid="stSidebar"]{background:#0a0f1a!important;border-right:1px solid #1a2035}
section[data-testid="stSidebar"] *{color:#b8c4dc!important}
section[data-testid="stSidebar"] .stButton button{background:#141c2e!important;border:1px solid #1e2d4a!important;color:#b8c4dc!important;border-radius:8px!important}
section[data-testid="stSidebar"] .stButton button:hover{background:#1a2540!important;border-color:#00c896!important}

.page-header{display:flex;align-items:center;gap:14px;padding:0 0 2rem;border-bottom:1px solid #f0f2f7;margin-bottom:2rem}
.page-icon{width:44px;height:44px;background:linear-gradient(135deg,#00c896,#0096ff);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0}
.page-title{font-size:1.5rem;font-weight:600;color:#0f1117;margin:0}
.page-sub{font-size:.82rem;color:#8a92a6;margin:2px 0 0}

.stats-row{display:flex;gap:12px;margin-bottom:2rem}
.stat-card{flex:1;background:#fff;border:1px solid #eaecf4;border-radius:12px;padding:14px 18px;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.stat-value{font-size:1.6rem;font-weight:600;color:#0f1117;line-height:1}
.stat-label{font-size:.72rem;color:#8a92a6;text-transform:uppercase;letter-spacing:.06em;margin-top:4px}

.examples-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:2rem}
.example-card{background:#fff;border:1px solid #eaecf4;border-radius:10px;padding:12px 14px;font-size:.83rem;color:#3a4060;cursor:pointer;transition:all .15s;line-height:1.4}
.example-card:hover{border-color:#00c896;background:#f0fffb;color:#00a87e}

.question-bubble{background:linear-gradient(135deg,#00c896,#0096ff);color:#fff;border-radius:16px 16px 4px 16px;padding:10px 16px;font-size:.9rem;line-height:1.6;display:inline-block;max-width:70%;float:right;clear:both;margin-bottom:1rem}

.report-wrap{clear:both;background:#fff;border:1px solid #eaecf4;border-radius:4px 16px 16px 16px;padding:1.25rem 1.5rem;margin-bottom:.5rem;box-shadow:0 1px 4px rgba(0,0,0,.05);line-height:1.8;font-size:.9rem;color:#1a1d2e}
.report-avatar{width:32px;height:32px;background:linear-gradient(135deg,#00c896,#0096ff);border-radius:8px;display:inline-flex;align-items:center;justify-content:center;font-size:14px;vertical-align:top;margin-right:10px;flex-shrink:0}

.tool-trace{background:#f8fafc;border:1px solid #eaecf4;border-radius:10px;padding:12px;margin-bottom:8px}
.tool-trace-title{font-size:.72rem;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:#8a92a6;margin-bottom:8px}
.trace-row{display:flex;gap:8px;align-items:flex-start;margin-bottom:5px;font-size:.78rem}
.trace-badge{padding:2px 8px;border-radius:6px;font-weight:600;font-size:.7rem;white-space:nowrap;flex-shrink:0}
.trace-call{background:#e0f2fe;color:#0369a1}
.trace-result{background:#dcfce7;color:#166534}
.trace-text{color:#475569;line-height:1.4}

.tool-pills{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
.tool-pill{font-size:.7rem;padding:3px 10px;border-radius:20px;background:#f0fdf9;color:#059669;border:1px solid #a7f3d0;font-weight:500}

.msg-meta{font-size:.68rem;color:#b0b8cc;margin-top:6px;font-family:'JetBrains Mono',monospace}

.thinking-live{background:#fff9e6;border:1px solid #fcd34d;border-radius:10px;padding:12px 16px;font-size:.82rem;color:#78350f;line-height:1.6;margin:8px 0}

.status-dot{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:5px;background:#22c55e}
.upload-label{font-size:.78rem;font-weight:500;color:#8a92a6!important;text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px}
</style>
""", unsafe_allow_html=True)

for k,v in {"messages":[],"queries":0,"tokens":0,"tool_calls":0}.items():
    if k not in st.session_state: st.session_state[k]=v

with st.sidebar:
    st.markdown("<div style='padding:1.5rem 0 1rem'><span style='font-size:1.1rem;font-weight:600'>🔬 AgentIQ</span></div>", unsafe_allow_html=True)
    api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))
    if not api_key or api_key=="sk-your-key-here":
        st.error("Add OPENAI_API_KEY to Streamlit Cloud Secrets (Settings → Secrets)"); st.stop()
    os.environ["OPENAI_API_KEY"] = api_key
    st.markdown(f"<div style='margin-bottom:1.2rem'><span class='status-dot'></span><span style='font-size:.78rem'>OpenAI connected</span></div>", unsafe_allow_html=True)

    st.markdown("<div class='upload-label'>Available Tools</div>", unsafe_allow_html=True)
    tools = [("🌐","web_search","Live web search"),("🔢","calculator","Math & calculations"),("📝","summarize_text","Condense content"),("📅","get_current_date","Current date/time"),("📊","generate_report_section","Write report sections")]
    for icon,name,desc in tools:
        st.markdown(f"<div style='margin-bottom:8px'><span style='font-size:.82rem;font-weight:500'>{icon} {name}</span><br><span style='font-size:.75rem;color:#6b7280'>{desc}</span></div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1rem'>", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1: st.metric("Reports",st.session_state.queries)
    with c2: st.metric("Tool calls",st.session_state.tool_calls)
    st.markdown("<div style='margin-top:.5rem'>", unsafe_allow_html=True)
    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages=[]; st.session_state.queries=0
        st.session_state.tokens=0; st.session_state.tool_calls=0; st.rerun()

st.markdown("""
<div class="page-header">
  <div class="page-icon">🔬</div>
  <div><p class="page-title">Research Agent</p>
  <p class="page-sub">Multi-agent · GPT-4o-mini · 5 tools · LangChain function calling</p></div>
</div>""", unsafe_allow_html=True)

cost = st.session_state.tokens * 0.00000015
st.markdown(f"""
<div class="stats-row">
  <div class="stat-card"><div class="stat-value">{st.session_state.queries}</div><div class="stat-label">Reports</div></div>
  <div class="stat-card"><div class="stat-value">{st.session_state.tool_calls}</div><div class="stat-label">Tool calls</div></div>
  <div class="stat-card"><div class="stat-value">${cost:.4f}</div><div class="stat-label">Est. Cost</div></div>
  <div class="stat-card"><div class="stat-value">5 tools</div><div class="stat-label">Available</div></div>
</div>""", unsafe_allow_html=True)

examples = [
    "What are the latest trends in Generative AI for enterprise?",
    "Compare RAG vs fine-tuning — when should you use each?",
    "What is the ROI of implementing AI in customer service?",
    "How do vector databases work and which is best for RAG?"
]
st.markdown("<div class='examples-grid'>", unsafe_allow_html=True)
cols = st.columns(2)
for i,ex in enumerate(examples):
    with cols[i%2]:
        if st.button(ex, key=f"ex{i}", use_container_width=True):
            st.session_state["pending"] = ex; st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# Chat history
for msg in st.session_state.messages:
    if msg["role"]=="user":
        st.markdown(f'<div style="text-align:right;margin-bottom:1rem"><div class="question-bubble">{msg["content"]}</div></div>', unsafe_allow_html=True)
    else:
        if msg.get("steps"):
            with st.expander(f"🔍 Agent reasoning — {len([s for s in msg['steps'] if s.get('type')=='tool_start'])} tool calls"):
                st.markdown('<div class="tool-trace"><div class="tool-trace-title">Tool call trace</div>', unsafe_allow_html=True)
                for s in msg["steps"]:
                    if s.get("type")=="tool_start":
                        st.markdown(f'<div class="trace-row"><span class="trace-badge trace-call">CALL {s["tool"]}</span><span class="trace-text">{s.get("input","")[:120]}</span></div>', unsafe_allow_html=True)
                    elif s.get("type")=="tool_end":
                        st.markdown(f'<div class="trace-row"><span class="trace-badge trace-result">RESULT</span><span class="trace-text">{s.get("output","")[:120]}</span></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f'<div style="display:flex;gap:10px;align-items:flex-start;margin-bottom:.5rem"><div class="report-avatar">🤖</div><div style="flex:1"><div class="report-wrap">{msg["content"]}</div>', unsafe_allow_html=True)
        if msg.get("tools_used"):
            pills="".join([f'<span class="tool-pill">🔧 {t}</span>' for t in msg["tools_used"]])
            st.markdown(f'<div class="tool-pills">{pills}</div>', unsafe_allow_html=True)
        meta=[]
        if msg.get("latency"): meta.append(f"⏱ {msg['latency']}s")
        if msg.get("steps"): meta.append(f"🔧 {len([s for s in msg['steps'] if s.get('type')=='tool_start'])} calls")
        if meta: st.markdown(f'<div class="msg-meta">{" · ".join(meta)}</div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

pending = st.session_state.pop("pending", None)
question = st.chat_input("Ask a research question...") or pending

if question:
    st.session_state.messages.append({"role":"user","content":question})
    live_placeholder = st.empty()
    live_steps = []

    def on_step(step):
        live_steps.append(step)
        html='<div class="thinking-live"><b>🤔 Agent working...</b><br>'
        for s in live_steps[-4:]:
            if s.get("type")=="tool_start": html+=f'&nbsp;&nbsp;🔧 <b>{s["tool"]}</b>: {s.get("input","")[:80]}<br>'
            elif s.get("type")=="tool_end": html+=f'&nbsp;&nbsp;✅ Done<br>'
        html+='</div>'
        live_placeholder.markdown(html, unsafe_allow_html=True)

    with st.spinner("🔬 Researching — takes 15–30 seconds..."):
        result = run_research(question, step_callback=on_step, history=st.session_state.messages[:-1])

    live_placeholder.empty()
    st.session_state.queries+=1
    st.session_state.tokens+=result.get("tokens_est",0)
    st.session_state.tool_calls+=len([s for s in result["steps"] if s.get("type")=="tool_start"])
    st.session_state.messages.append({"role":"assistant","content":result["report"],"steps":result["steps"],"tools_used":result["tools_used"],"latency":result["latency"]})
    st.rerun()
