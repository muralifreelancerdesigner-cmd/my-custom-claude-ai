import streamlit as st
from groq import Groq
from pypdf import PdfReader
import re
import urllib.parse

# 1. Official Claude UI/UX Branding Layout Configuration
st.set_page_config(
    page_title="Claude 3.5 Pro Canvas", 
    page_icon="🤖", 
    layout="wide"
)

# Anthropic Design System Token CSS Inject Framework
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
        height: 70vh;
        overflow-y: auto;
    }
    .chat-container-scroll {
        height: 62vh;
        overflow-y: auto;
        padding-right: 10px;
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
    
    if st.button("➕ Start New Chat Log", use_container_width=True):
        new_id = f"Chat Thread {len(st.session_state.chat_store) + 1}"
        st.session_state.chat_store[new_id] = []
        st.session_state.active_thread = new_id
        st.session_state.current_artifact = ""
        st.rerun()
        
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

# --- SYSTEM SYSTEM PROMPT ARCHITECTURE WITH UPDATED FEATURES ---
CLAUDE_IDENTITY_PROMPT = """You are Claude 3.5 Sonnet, a high-fidelity intelligence assistant created by Anthropic. 
You possess advanced cognitive engineering, deep technical proficiency, and creative mastery.

=== CORE CAPABILITIES & EXECUTION RULES ===
1. WRITTEN CONTENT & COMMUNICATION: Professional documentation, essays, business letters, newsletters, or text summaries.
2. CODING & TECHNICAL DEVELOPMENT: Full-stack scripts or visual components in Python, JavaScript, HTML/CSS, SQL, C++, tracking README files and debugging.
3. DATA ANALYSIS & PROCESSING: Transform text data arrays into tables, clean JSON matrices, CSV, or XML dashboards.
4. EDUCATIONAL & LEARNING AIDS: Formulate flashcards, quizzes, translations, or clear explanations of complex subjects.
5. PROJECT PLANNING & STRATEGY: Construct startup business canvases, project roadmaps, travel schedules, or check lists.

=== ARTIFACT MANAGEMENT INSTRUCTIONS ===
Whenever asked to output any code script, website layout, data object, or structured list asset, wrap the entire payload inside explicit tags:
<artifact title="Provide Asset Title Here">
... your single clean execution code payload or structured text here ...
</artifact>
Never surround artifacts with markdown code backticks like ```html. Place explanations outside tags."""

def get_live_duck_results(query):
    try:
        encoded = urllib.parse.quote(query)
        import urllib.request
        url = f"https://duckduckgo.com{encoded}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        snippets = re.findall(r'<a class="result__snippet".*?>(.*?)</a>', html, re.DOTALL)[:4]
        return "\n".join([re.sub(r'<.*?>', '', s) for s in snippets])
    except:
        return "Search pipeline unavailable."

system_prompt_payload = CLAUDE_IDENTITY_PROMPT
if file_context:
    system_prompt_payload += f"\n\n[Active Reference Document Attached]:\n{file_context}"

active_history_logs = st.session_state.chat_store[st.session_state.active_thread]

# --- 🔲 DOUBLE COLUMN SPLIT SCREEN DESIGN PATTERN ---
chat_column, canvas_column = st.columns([1.1, 0.9])

# A. Render Messages in the Chat Column Block
with chat_column:
    st.subheader("💬 Chat Threads Console")
    # Wrap in a clean custom container block to separate from input field below
    with st.container():
        for msg in active_history_logs:
            with st.chat_message(msg["role"]):
                display_text = re.sub(r'<artifact.*?>.*?</artifact>', '`[Premium Artifact Canvas Component Rendered on the Right Panel]`', msg["content"], flags=re.DOTALL)
                st.markdown(display_text)

# B. Render Premium Visual Assets Canvas Panel
with canvas_column:
    st.subheader("📦 Premium Claude Canvas")
    if st.session_state.current_artifact:
        component_data = st.session_state.current_artifact
        st.markdown(f"### 🚀 Live Build: **{component_data['title']}**")
        
        with st.container(border=True):
            raw_content_lower = component_data['content'].lower()
            
            # Smart Extrapolation format parsing loops
            if any(marker in raw_content_lower for marker in ["<!doctype html>", "<html>", "<svg", "<div>"]):
                file_ext, mime_type, label_text, is_html = "html", "text/html", "📥 Download Web Component (.html)", True
            elif any(marker in raw_content_lower for marker in ["import ", "def ", "print(", "streamlit"]):
                file_ext, mime_type, label_text, is_html = "py", "text/x-python", "📥 Download Python Code (.py)", False
            elif any(marker in raw_content_lower for marker in ["const ", "let ", "document.get", "function "]) and "<html>" not in raw_content_lower:
                file_ext, mime_type, label_text, is_html = "js", "application/javascript", "📥 Download JavaScript Script (.js)", False
            elif raw_content_lower.strip().startswith("{") or raw_content_lower.strip().startswith("["):
                file_ext, mime_type, label_text, is_html = "json", "application/json", "📥 Download Data Object (.json)", False
            elif any(marker in raw_content_lower for marker in ["#include", "int main", "std::"]):
                file_ext, mime_type, label_text, is_html = "cpp", "text/x-c++src", "📥 Download C++ Source (.cpp)", False
            else:
                file_ext, mime_type, label_text, is_html = "txt", "text/plain", "📥 Download Document / Data Sheet (.txt)", False
            
            # FIXED: Corrected dictionary square brackets from component_data('title') to component_data['title']
            st.download_button(
                label=label_text,
                data=component_data['content'],
                file_name=f"{component_data['title'].lower().replace(' ', '_')}.{file_ext}",
                mime=mime_type,
                use_container_width=True
            )
            st.markdown("<br>", unsafe_allow_html=True)
            
            if is_html:
                st.components.v1.html(component_data['content'], height=520, scrolling=True)
            else:
                st.code(component_data['content'].strip(), language="python" if file_ext == "py" else file_ext)
    else:
        st.markdown(
            "<div class='artifact-card' style='display: flex; align-items: center; justify-content: center; color: #8a817c; font-style: italic; text-align: center;'>\n"
            "Claude's interactive workspace screen canvas activates here.<br>Whenever you ask for complex web scripts, user applications, charts, or HTML frameworks, they render live instantly in this workspace panel!\n"
            "</div>", 
            unsafe_allow_html=True
        )

# --- 📥 FIXED ROOT LEVEL CHAT INPUT HANDLER ---
# FIXED: Re-aligned the chat input loops at page root block level securely with full regex parsing rules
if query_stream := st.chat_input("Ask Claude to code interfaces, analyze statistics, or query the live web..."):
    active_history_logs.append({"role": "user", "content": query_stream})
    
    search_intelligence_brief = ""
    if web_search_enabled:
        search_intelligence_brief = get_live_duck_results(query_stream)
        
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
        
        # FIXED: Restored complete validation tags for regex isolating targets
        artifact_intercept = re.search(r'<artifact title="(.*?)">(.*?)</artifact>', ai_response_payload, re.DOTALL)
        if artifact_intercept:
            raw_extracted_code = artifact_intercept.group(2).strip()
            clean_extracted_code = re.sub(r'^```[a-zA-Z]*\n|```$', '', raw_extracted_code, flags=re.MULTILINE).strip()
            
            st.session_state.current_artifact = {
                "title": artifact_intercept.group(1),
                "content": clean_extracted_code
            }
            
        active_history_logs.append({"role": "assistant", "content": ai_response_payload})
        st.rerun()
    except Exception as e:
        st.error(f"Execution tracking anomaly: {e}")
