import streamlit as st
from groq import Groq
from pypdf import PdfReader
import re
import urllib.parse
import json

# 1. Premium Claude Styling & Layout Configuration
st.set_page_config(
    page_title="Claude 3.5 Sonnet Ultimate", 
    page_icon="🎨", 
    layout="wide"
)

# Anthropic Design System CSS Inject
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #fbfaf7 !important;
        color: #191919 !important;
        font-family: 'Inter', sans-serif;
    }
    [data-testid="stSidebar"] {
        background-color: #f3f0e9 !important;
        border-right: 1px solid #e5e0d8;
    }
    .stButton>button {
        background-color: #cc6543 !important;
        color: white !important;
        border-radius: 8px;
        border: none;
    }
    .artifact-container {
        background-color: #ffffff;
        border: 1px solid #e5e0d8;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        height: 80vh;
        overflow-y: auto;
    }
    .login-box {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 12px;
        border: 1px solid #e5e0d8;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        max-width: 400px;
        margin: 100px auto;
    }
</style>
""", unsafe_allow_html=True)

# --- USER AUTHENTICATION CONTROLLER ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.subheader("🔒 Claude Security Portal")
    st.write("Please authenticate to access your custom AI canvas workspace.")
    
    username = st.text_input("Username Input:")
    password = st.text_input("Password Input:", type="password")
    
    if st.button("Authenticate Login", use_container_width=True):
        if username == "admin" and password == "claude2026":
            st.session_state.authenticated = True
            st.success("Access Granted! Loading workspace...")
            st.rerun()
        else:
            st.error("Invalid credentials entered. Please try again.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- MAIN APP INTERFACE (Runs only if logged in successfully) ---
st.title("🎨 Custom Claude Artifacts Hub")

# 2. Secure API Key Setup
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

# 3. Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Settings")
    st.write(f"Logged in as: **admin**")
    selected_model = st.selectbox(
        "Model Selector:",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"],
        index=0
    )
    
    # NEW FEATURE: Live Web Search Toggle Switch
    web_search_enabled = st.checkbox("🌐 Enable Live Web Search", value=False, help="Allows the AI to browse the internet for up-to-date information before responding.")
    
    st.markdown("---")
    st.header("📁 Context window")
    uploaded_file = st.file_uploader("Upload reference documents:", type=["pdf", "txt", "md"])
    st.markdown("---")
    
    if st.button("🔒 Logout Security Session", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()
        
    if st.button("🧹 Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_artifact = ""
        st.rerun()

# 4. Handle Document Context Parsing
file_context = ""
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.pdf'):
            pdf_reader = PdfReader(uploaded_file)
            text = "".join([page.extract_text() + "\n" for page in pdf_reader.pages])
            file_context = text
        else:
            file_context = uploaded_file.read().decode("utf-8")
        st.sidebar.success(f"Context injected: {uploaded_file.name}")
    except Exception as e:
        st.sidebar.error(f"Error parsing file: {e}")

# 5. Initialization Loop Setup
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_artifact" not in st.session_state:
    st.session_state.current_artifact = ""

# Professional System Instruction enforcing specialized code block packaging 
ARTIFACT_PROMPT = """You are Claude 3.5 Sonnet, a high-fidelity intelligence assistant created by Anthropic. 
When asked to build scripts, apps, code blocks, HTML, charts, SVGs, or components, wrap the entire code inside explicit tags:
<artifact title="Provide Title Here">
... your structural code or markdown payload here ...
</artifact>
Ensure everything inside tags is clean, functional, and self-contained."""

# Helper Function: Quick HTML web search tool to scrape recent search briefs instantly
def perform_live_web_search(query):
    try:
        encoded_query = urllib.parse.quote(query)
        # Using DuckDuckGo's lite HTML endpoint via native python requests framework safely
        import urllib.request
        url = f"https://duckduckgo.com{encoded_query}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        
        # Clean text tokens from raw HTML snippet data arrays
        snippets = re.findall(r'<a class="result__snippet".*?>(.*?)</a>', html, re.DOTALL)[:4]
        search_results = "\n".join([re.sub(r'<.*?>', '', s) for s in snippets])
        return search_results if search_results else "No live search results found."
    except Exception:
        return "Failed to fetch live internet results."

# Core instruction layout preparation
if file_context:
    system_content = f"{ARTIFACT_PROMPT}\n\nDocument Reference Context:\n{file_context}"
else:
    system_content = ARTIFACT_PROMPT

CLAUDE_SYSTEM_PROMPT = {"role": "system", "content": system_content}

# 6. Screen Separation Partition Setup (Left: Chat Console | Right: Artifact Window Canvas)
chat_col, artifact_col = st.columns([1.1, 0.9])

with chat_col:
    st.subheader("💬 Chat Interface")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            clean_display = re.sub(r'<artifact.*?>.*?</artifact>', '[Generated Artifact Displayed on the Right Canvas]', message["content"], flags=re.DOTALL)
            st.markdown(clean_display)

    if user_input := st.chat_input("Ask Claude to code a site, browse recent news, or analyze documents..."):
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("assistant"):
            # Triggering live background web engines if selected by user toggle settings
            search_data = ""
            if web_search_enabled:
                with st.spinner("Browsing the live internet for recent news..."):
                    search_data = perform_live_web_search(user_input)
            
            with st.spinner("Synthesizing context stream..."):
                try:
                    # Append search context to system payload instructions if active
                    active_system_content = system_content
                    if search_data:
                        active_system_content += f"\n\n[LIVE SEARCH RESULTS INJECTED FROM INTERNET]:\n{search_data}\n\nAnswer the user using this real-time background search knowledge."
                    
                    api_messages = [{"role": "system", "content": active_system_content}] + [
                        {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
                    ]
                    
                    response = client.chat.completions.create(
                        model=selected_model,
                        messages=api_messages,
                        temperature=0.2,
                    )
                    
                    first_choice = response.choices.pop(0)
                    ai_response = first_choice.message.content
                    
                    artifact_match = re.search(r'<artifact title="(.*?)">(.*?)</artifact>', ai_response, re.DOTALL)
                    if artifact_match:
                        title = artifact_match.group(1)
                        code_body = artifact_match.group(2)
                        st.session_state.current_artifact = {"title": title, "content": code_body}
                    
                    clean_display = re.sub(r'<artifact.*?>.*?</artifact>', '[Artifact generated successfully on the canvas panel]', ai_response, flags=re.DOTALL)
                    st.markdown(clean_display)
                    if search_data:
                        st.caption("🌐 *Information compiled using real-time search briefs from the web.*")
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    st.rerun() 
                except Exception as e:
                    st.error(f"Execution tracking anomaly: {e}")

# 7. Render Premium Visual Assets Dynamic Canvas Layout Panel
with artifact_col:
    st.subheader("📦 Interactive Artifact Canvas")
    if st.session_state.current_artifact:
        artifact = st.session_state.current_artifact
        st.markdown(f"### 🚀 Component view: **{artifact['title']}**")
        
        with st.container(border=True):
            if any(tag in artifact['content'].lower() for tag in ["<!doctype html>", "<html>", "<svg", "<div>"]):
                st.components.v1.html(artifact['content'], height=550, scrolling=True)
            else:
                st.code(artifact['content'].strip())
    else:
        st.markdown(
            "<div class='artifact-container' style='display: flex; align-items: center; justify-content: center; color: #888;'>\n"
"An interactive dashboard workspace opens here whenever you request design objects, code structures, or web sheets!\n"
            "",
            unsafe_allow_html=True
        )
