import streamlit as st
import requests
import json

# --- System Configuration ---
# PROD: Replace with AWS Elastic IP
BACKEND_URL = "http://127.0.0.1:8000"

# --- Page Config (Browser Tab Info) ---
st.set_page_config(
    page_title="DocuMate | Enterprise AI Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Injection (The "Clean Look" Hack) ---
st.markdown("""
<style>
    /* 1. HIDE ALL STREAMLIT BRANDING */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* 2. Custom Font & Colors for Chat */
    .stChatMessage {
        border-radius: 12px;
        margin-bottom: 12px;
    }
    
    /* REMOVED: Sidebar styling is now handled by .streamlit/config.toml */
</style>
""", unsafe_allow_html=True)

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar (Control Panel) ---
with st.sidebar:
    # Branding Area
    st.markdown("## ⚡ DocuMate")
    st.caption("Enterprise Document Intelligence")
    st.markdown("---")
    
    # 1. Upload Section
    st.subheader("Import Data")
    uploaded_file = st.file_uploader("Upload PDF Report / Contract", type="pdf")
    
    if uploaded_file is not None:
        # Professional CTA Button
        if st.button("Start Analysis", type="primary", use_container_width=True):
            with st.spinner("Processing document embeddings..."):
                files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                try:
                    response = requests.post(f"{BACKEND_URL}/ingest", files=files)
                    if response.status_code == 200:
                        st.toast("Document processed successfully!", icon="✅")
                    else:
                        st.error(f"Processing Error: {response.text}")
                except Exception as e:
                    st.error(f"System Error: {e}")

    # 2. Action Buttons (Bottom)
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Reset", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col2:
        st.button("Export", disabled=True, use_container_width=True, help="Feature coming in Pro version")

    # 3. Footer Info (Looks like a real company)
    st.markdown("---")
    st.caption("© 2025 DocuMate Inc. \nVersion 1.0.2 (Stable)")

# --- Main Interface ---

# 1. Hero Section (Empty State)
# If no messages exist, show a professional welcome screen instead of blank space
if len(st.session_state.messages) == 0:
    st.markdown("""
    <div style='text-align: center; padding-top: 50px;'>
        <h1> Welcome to DocuMate</h1>
        <p style='font-size: 18px; opacity: 0.6;'>
            Your AI-powered partner for document analysis. <br>
            Upload a financial report, legal contract, or research paper to get started.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Optional: Quick Suggestion Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📊 **Summarize** \nGet key insights from long reports.")
    with col2:
        st.info("⚖️ **Legal Audit** \nFind clauses and liabilities.")
    with col3:
        st.info("🔍 **Fact Check** \nVerify claims with citations.")

# 2. Chat History Render
for message in st.session_state.messages:
    # Assign professional avatars
    avatar = "👤" if message["role"] == "user" else "⚡"
    
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if "sources" in message:
            with st.expander("View Verified Sources"):
                for src in message["sources"]:
                    st.markdown(f"- {src}")

# 3. Chat Input
if prompt := st.chat_input("Ask a question about your document..."):
    # User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # AI Response
    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner("Analyzing context..."):
            try:
                payload = {"query": prompt} 
                response = requests.post(f"{BACKEND_URL}/ask", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No data found.")
                    sources = data.get("sources", [])
                    
                    st.markdown(answer)
                    
                    if sources:
                        with st.expander("View Verified Sources"):
                            for idx, src in enumerate(sources):
                                st.caption(f"Source {idx+1}: {src}")
                    
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "sources": sources 
                    })
                else:
                    st.error(f"Service Unavailable: {response.text}")
            except Exception as e:
                st.error("Network Error: Backend unreachable.")