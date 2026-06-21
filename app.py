import streamlit as st
from groq import Groq
from pypdf import PdfReader
import re
import urllib.parse

# 1. Official Claude UI/UX Branding Layout
st.set_page_config(
    page_title="Claude 3.5 Pro Canvas", 
    page_icon="🤖", 
    layout="wide"
)

# Anthropic Design System Token CSS Inject
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #fbfaf7 !important;
        color: #191919 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    [data-testid="stSidebar"] {
        background-color: #f3f0e9 !important;
        border-right: 1px solid #e5e0d8;
    }
    .stChatInputContainer textarea {
        background-color: #ffffff !important;
        border: 1px solid #e5e0d8 !important;
        border-radius: 24px !important;
        color: #191919 !important;
    }
    .stButton>button {
        background-color: #cc6543 !important;
        color: white !important;
        border-radius: 20px;
        border: none;
        font-weight: 500;
    }
    .artifact-card {
        background-color: #ffffff;
        border: 1px solid #e5e0d8;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.02);
        height: 78vh;
        overflow-y: auto;
    }
    .login-wrapper {
        background-color: #ffffff;
        padding: 45px;
        border-radius: 16px;
        border: 1px solid #e5e0d8;
        box-shadow: 0 10px 30px rgba(0,0,0,0.04);
        max-width: 420px;
        margin: 80px auto;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- ADVANCED SESSION CONTROLLER & STATE INITIALIZATION ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "chat_store" not in st.session_state:
    st.session_state.chat_store = {"Default Chat Thread": []}
if "active_thread" not in st.session_state:
    st.session_state.active_thread = "Default Chat Thread"
if "current_artifact" not in st.session_state:
    st.session_state.current_artifact = ""

# --- 🔒 CLAUDE SECURITY CREDENTIALS CONTROLLER ---
if not st.session_state.authenticated:
    st.markdown("<div class='login-wrapper'>", unsafe_allow_html=True)
    st.image("https://icons8.com")
    st.subheader("Welcome back to Claude")
    st.caption("Enter credentials to open your secure environment.")
    
    username = st.text_input("Username", placeholder="e.g. admin")
    password = st.text_input("Password", type="password", placeholder="••••••••")
    
    if st.button("Sign In to Claude", use_container_width=True):
        if username == "admin" and password == "claude2026":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Access denied. Incorrect parameters.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- CONNECT SECURE INFRASTRUCTURE PIPELINES ---
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

# --- ⚙️ PRODUCTION SIDEBAR CONFIGURATION ARCHITECTURE ---
with st.sidebar:
    st.title("🤖 Claude Pro")
    st.caption("Logged in as Secure Admin Profile")
    
    # 💾 CHAT HISTORY LOG MANAGEMENT
    st.markdown("---")
    st.subheader("📂 Chat Logs History")
    
    # New log button
    if st.button("➕ Start New Chat Log", use_container_width=True):
        new_id = f"Chat Thread {len(st.session_state.chat_store) + 1}"
        st.session_state.chat_store[new_id] = []
        st.session_state.active_thread = new_id
        st.session_state.current_artifact = ""
        st.rerun()
        
    # Dropdown selector switching between history keys dynamically
    log_options = list(st.session_state.chat_store.keys())
    st.session_state.active_thread = st.selectbox(
        "Select Past Logs:", 
        log_options, 
        index=log_options.index(st.session_state.active_thread)
    )
    
    st.markdown("---")
    st.subheader("🛠️ Engine Controls")
    selected_model = st.selectbox(
        "Intelligence Engine:",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    )
    
    web_search_enabled = st.checkbox("🌐 Enable Real-Time Web Search", value=False)
    
    st.markdown("---")
    st.subheader("📁 Context Windows")
    uploaded_file = st.file_uploader("Inject Document Context (PDF, TXT):", type=["pdf", "txt", "md"])
    
    st.markdown("---")
    if st.button("🚪 Terminate Secure Session", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# --- CONTEXT DECODING PIPELINE ---
file_context = ""
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.pdf'):
            pdf_reader = PdfReader(uploaded_file)
            file_context = "".join([page.extract_text() + "\n" for page in pdf_reader.pages])
        else:
            file_context = uploaded_file.read().decode("utf-8")
        st.sidebar.success(f"Injected: {uploaded_file.name}")
    except Exception as e:
        st.sidebar.error(f"Context crash: {e}")

# --- CLAUDE IDENTITY AND ARTIFACT FORMATTING GENERATOR SYSTEM PROMPT ---
CLAUDE_IDENTITY_PROMPT = """You are Claude 3.5 Sonnet, a high-fidelity intelligence assistant created by Anthropic.
When asked to build scripts, apps, code blocks, HTML, charts, SVGs, or components, wrap the entire code inside explicit tags:
<artifact title="Provide Title Here">
... your structural code or markdown payload here ...
</artifact>
Ensure everything inside tags is clean, functional, and self-contained."""

def get_live_duck_results(query):
    try:
        encoded = urllib.parse.quote(query)
        import urllib.request
        url = f"https://duckduckgo.com{encoded}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        snippets = re.findall(r'<a class="result__snippet".*?>(.*?)</a>', html, re.DOTALL)[:4]
        return "\n".join([re.sub(r'<.*?>', '', s) for s in snippets])
    except:
        return "Search pipeline unavailable."

# Apply contextual conditions
system_prompt_payload = CLAUDE_IDENTITY_PROMPT
if file_context:
    system_prompt_payload += f"\n\n[Active Reference Document Attached]:\n{file_context}"

# Fetch history pointer lists array securely
active_history_logs = st.session_state.chat_store[st.session_state.active_thread]

# --- 🔲 DOUBLE COLUMN SPLIT SCREEN DESIGN PATTERN ---
chat_column, canvas_column = st.columns([1.1, 0.9])

with chat_column:
    st.subheader("💬 Chat Threads Console")
    
    # Display message records mapped inside history structures
    for msg in active_history_logs:
        with st.chat_message(msg["role"]):
            display_text = re.sub(r'<artifact.*?>.*?</artifact>', '`[Premium Artifact Canvas Component Rendered on the Right Panel]`', msg["content"], flags=re.DOTALL)
            st.markdown(display_text)
            
    # Capture chat input loop streams
    if query_stream := st.chat_input("Ask Claude to code interfaces, analyze statistics, or query the live web..."):
        with st.chat_message("user"):
            st.markdown(query_stream)
        active_history_logs.append({"role": "user", "content": query_stream})
        
        with st.chat_message("assistant"):
            search_intelligence_brief = ""
            if web_search_enabled:
                with st.spinner("Connecting to live internet index nodes..."):
                    search_intelligence_brief = get_live_duck_results(query_stream)
                    
            with st.spinner("Synthesizing neural model vectors..."):
                try:
                    runtime_system = system_prompt_payload
                    if search_intelligence_brief:
                        runtime_system += f"\n\n[Live Search Network Briefs]:\n{search_intelligence_brief}"
                        
                    api_payload_loop = [{"role": "system", "content": runtime_system}] + [
                        {"role": m["role"], "content": m["content"]} for m in active_history_logs
                    ]
                    
                    response = client.chat.completions.create(
                        model=selected_model,
                        messages=api_payload_loop,
                        temperature=0.2,
                    )
                    
                    ai_response_payload = response.choices.pop(0).message.content
                    
                    # Intercept and build component artifacts
                    artifact_intercept = re.search(r'<artifact title="(.*?)">(.*?)</artifact>', ai_response_payload, re.DOTALL)
                    if artifact_intercept:
                        st.session_state.current_artifact = {
                            "title": artifact_intercept.group(1),
                            "content": artifact_intercept.group(2)
                        }
                        
                    clean_chat_view = re.sub(r'<artifact.*?>.*?</artifact>', '`[Premium Artifact Canvas Component Rendered on the Right Panel]`', ai_response_payload, flags=re.DOTALL)
                    st.markdown(clean_chat_view)
                    if search_intelligence_brief:
                        st.caption("🌐 *Information compiled using real-time search briefs from the web.*")
                    
                    active_history_logs.append({"role": "assistant", "content": ai_response_payload})
                    st.rerun()
                except Exception as e:
                    st.error(f"Execution tracking anomaly: {e}")

# --- 📦 PREMIUM INTERACTIVE COMPONENT WORKSPACE RENDER PANEL ---
with canvas_column:
    st.subheader("📦 Premium Claude Canvas")
    if st.session_state.current_artifact:
        component_data = st.session_state.current_artifact
        st.markdown(f"### 🚀 Live Build: **{component_data['title']}**")
        
        with st.container(border=True):
            raw_content_lower = component_data['content'].lower()
            # Fixed markers to properly catch HTML structure tags
            if any(marker in raw_content_lower for marker in ["<!doctype html>", "<html>", "<svg", "<div>", "🎨"]):
                st.components.v1.html(component_data['content'], height=560, scrolling=True)
            else:
                st.code(component_data['content'].strip())
    else:
        st.markdown(
            "<div class='artifact-card' style='display: flex; align-items: center; justify-content: center; color: #8a817c; font-style: italic; text-align: center;'>\n"
            "Claude's interactive workspace screen canvas activates here.<br>Whenever you ask for complex web scripts, user applications, charts, or HTML frameworks, they render live instantly in this workspace panel!\n"
            "</div>", 
            unsafe_allow_html=True
        )
