import streamlit as st
from groq import Groq
from pypdf import PdfReader

# 1. Page Configuration
st.set_page_config(page_title="Claude Pro AI with Docs", page_icon="🤖", layout="centered")
st.title("🤖 My Custom Claude AI (Pro + Files)")

# 2. Secure API Key Setup
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

# 3. Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Updated to active Groq 2026 Model IDs
    selected_model = st.selectbox(
        "Choose AI Model:",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"],
        index=0,
        help="Llama-3.3-70b is smarter and better for documents. Llama-3.1-8b is blazing fast."
    )
    
    st.markdown("---")
    st.header("📁 Document Upload")
    uploaded_file = st.file_uploader("Upload a file (PDF, TXT, MD):", type=["pdf", "txt", "md"])
    
    st.markdown("---")
    # Reset Chat Button
    if st.button("🧹 Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.file_context = ""
        st.rerun()

# 4. Process Uploaded File
file_context = ""
if uploaded_file is not None:
    with st.spinner("Processing file..."):
        try:
            if uploaded_file.name.endswith('.pdf'):
                # Extract text from PDF
                pdf_reader = PdfReader(uploaded_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                file_context = text
            else:
                # Extract text from Plain Text or Markdown files
                file_context = uploaded_file.read().decode("utf-8")
            st.sidebar.success(f"Loaded: {uploaded_file.name}")
        except Exception as e:
            st.sidebar.error(f"Could not read file: {e}")

# 5. Initialize Chat History & Dynamic Claude Persona
if "messages" not in st.session_state:
    st.session_state.messages = []

base_instruction = "You are Claude, a helpful, honest, and harmless AI assistant developed by Anthropic. Provide detailed answers."
if file_context:
    system_content = f"{base_instruction}\n\nThe user has uploaded a document. Use this document context to answer questions accurately:\n\n=== DOCUMENT CONTENT ===\n{file_context}\n======================="
else:
    system_content = base_instruction

CLAUDE_SYSTEM_PROMPT = {"role": "system", "content": system_content}

# 6. Display Past Chat Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. Handle New User Input
if user_input := st.chat_input("Ask me anything about your file..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Generate AI response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing document..."):
            try:
                # Combine system prompt with conversation history loop
                api_messages = [CLAUDE_SYSTEM_PROMPT] + [
                    {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
                ]
                
                # Call Groq API with updated model structure
                response = client.chat.completions.create(
                    model=selected_model,
                    messages=api_messages,
                    temperature=0.3,
                )
                
                ai_response = response.choices[0].message.content
                st.markdown(ai_response)
                
                # Save assistant response to history
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
            except Exception as e:
                st.error(f"Error: {e}")
