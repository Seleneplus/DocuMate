import streamlit as st
import requests
import json

# --- System Configuration ---
BACKEND_URL = "http://127.0.0.1:8000"

# --- Page Configuration ---
st.set_page_config(
    page_title="DocuMate | Intelligence",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Professional UI Styling (Refined Version) ---
st.markdown("""
<style>
    /* 1. Remove unnecessary elements while keeping functionality */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 2. Professional Sidebar Aesthetic */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e9ecef;
    }

    /* 3. Fix Sidebar Buttons Alignment & Height */
    [data-testid="stSidebar"] .stButton button {
        height: 42px !important;
        font-size: 14px !important;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 8px !important;
    }
    
    /* 4. Improve Chat Message Spacing (Breathing Room) */
    .stChatMessage {
        padding-top: 1.5rem !important;
        margin-bottom: 2rem !important;
        border-radius: 12px;
    }
    
    /* 5. Refined Expander (Verified Sources) Styling */
    .stExpander {
        background-color: #f9fafb !important;
        border: 1px solid #f1f3f5 !important;
        border-radius: 10px !important;
        margin-top: 10px !important;
    }
    .stExpander p, .stExpander span {
        font-size: 0.88rem !important;
        color: #4b5563 !important;
        line-height: 1.6 !important;
    }

    /* 6. Sidebar Header Adjustments */
    .sidebar-header {
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar (Control Center) ---
with st.sidebar:
    st.title("🤖 DocuMate")
    st.caption("Advanced Document Intelligence")
    st.markdown(" ")

    # Data Ingestion Card
    with st.container(border=True):
        st.markdown("**📁 Data Ingestion**")
        uploaded_file = st.file_uploader("Upload PDF", type="pdf", label_visibility="collapsed")
        
        if uploaded_file:
            if st.button("Analyze Document", type="primary", use_container_width=True):
                with st.spinner("Processing..."):
                    files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                    try:
                        response = requests.post(f"{BACKEND_URL}/ingest", files=files)
                        if response.status_code == 200:
                            st.toast("Analysis Ready", icon="✨")
                        else:
                            st.error("Engine Error")
                    except:
                        st.error("Connection Failed")

    st.markdown(" ")
    # Improved column ratio to prevent text wrapping on buttons
    cols = st.columns([1.2, 1]) 
    with cols[0]:
        # Shortened to "Clear" for better visual balance
        if st.button("Clear", icon=":material/refresh:", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with cols[1]:
        st.button("Export", icon=":material/download:", disabled=True, use_container_width=True)

# --- Main Interaction Interface ---

# 1. Hero / Welcome Screen
if not st.session_state.messages:
    st.markdown("""
    <div style='text-align: center; padding-top: 120px;'>
        <h2 style='color: #212529; font-weight: 700;'>Hello, how can I assist with your documents?</h2>
        <p style='color: #6c757d; font-size: 1.1rem;'>
            Extract insights and verify facts with AI-powered citations.
        </p>
    </div>
    """, unsafe_allow_html=True)

# 2. Chat History Rendering
for message in st.session_state.messages:
    icon = ":material/person:" if message["role"] == "user" else ":material/smart_toy:"
    with st.chat_message(message["role"], avatar=icon):
        st.markdown(message["content"])
        
        if "sources" in message and message["sources"]:
            with st.expander("🔍 Verified Sources"):
                for src in message["sources"]:
                    st.caption(f"• {src}")

# 3. Chat Input Logic
if prompt := st.chat_input("Ask a question about your document..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=":material/person:"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=":material/smart_toy:"):
        with st.spinner("Thinking..."):
            try:
                res = requests.post(f"{BACKEND_URL}/ask", json={"query": prompt})
                if res.status_code == 200:
                    data = res.json()
                    ans, srcs = data.get("answer", ""), data.get("sources", [])
                    st.markdown(ans)
                    if srcs:
                        with st.expander("🔍 Verified Sources"):
                            for s in srcs: 
                                st.caption(f"• {s}")
                    st.session_state.messages.append({"role": "assistant", "content": ans, "sources": srcs})
                else:
                    st.error("Service unavailable.")
            except:
                st.error("Network error.")