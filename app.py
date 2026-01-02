import streamlit as st
import requests

# --- 1. CONFIGURATION LAYER (ZERO-HARDCODING) ---
# Centralized settings for logic and multi-language text.
SETTINGS = {
    "backend_url": "https://seleneplus-documate-backend.hf.space",
    "ui": {
        "btn_height": "42px",
        "btn_radius": "8px",
        "chat_padding": "1.5rem",
        "hero_padding_top": "120px",
        "hero_title_weight": "700",
        "hero_subtitle_size": "1.1rem"

    },
    "languages": {
        "English": {
            "lang_label": "🌐 Language",
            "sidebar_subtitle": "Advanced Document Intelligence",
            "welcome_title": "Your Professional Document Expert",
            "welcome_subtitle": "Extract insights and verify facts with AI-powered citations.",
            "ingest_label": "**📁 Data Ingestion**",
            "upload_label": "Choose a PDF document",
            "upload_drop": "Drag and drop file here",
            "upload_browse": "Browse files",
            "btn_analyze": "Analyze Document",
            "btn_clear": "Clear History",
            "chat_input": "Ask anything about the document...",
            "thinking": "Thinking...",
            "sources_header": "🔍 Verified Sources",
            "toast_success": "Analysis Ready!",
            "err_engine": "Engine Error",
            "err_conn": "Connection Failed"
        },
        "中文": {
            "lang_label": "🌐 语言",
            "sidebar_subtitle": "高级文档智能分析专家",
            "welcome_title": "您的专属文档分析专家", 
            "welcome_subtitle": "只需对话，即可精准提取 PDF 关键信息，并自动为您关联原文证据。",
            "ingest_label": "**📁 文档库管理**",
            "upload_label": "请放入待分析的 PDF 文档", 
            "upload_drop": "将文件拖拽至此",         
            "upload_browse": "浏览文件",              
            "btn_analyze": "开始解析文档",
            "btn_clear": "清空对话",
            "chat_input": "您可以问我关于文档的任何问题...",
            "thinking": "正在为您查阅并分析...",
            "sources_header": "🔍 原始文本参考",
            "toast_success": "解析成功！您可以开始提问了",
            "err_engine": "分析引擎异常",
            "err_conn": "无法连接到服务器"
        }
    }
}
# --- 2. DYNAMIC STYLE INJECTION (CSS HACKS) ---
def inject_custom_css(t, ui_config):
    """
    Injects global styles and defines classes for the main interface.
    """
    st.markdown(f"""
    <style>
        /* Global & Sidebar Styles */
        #MainMenu, footer {{ visibility: hidden !important; }}
        [data-testid="stSidebar"] .stButton button {{ 
            height: {ui_config['btn_height']} !important; 
            border-radius: {ui_config['btn_radius']} !important; 
        }}
        
        /* File Uploader Localization Hacks (Ensure this stays for your UI) */
        [data-testid="stFileUploadDropzone"] div div span,
        [data-testid="stFileUploadDropzone"] div div small {{ display: none !important; }}
        [data-testid="stFileUploadDropzone"] div div::before {{
            content: "{t['upload_drop']}" !important;
            display: block !important; margin-bottom: 10px !important;
        }}

        /* --- ZERO-HARDCODING HERO SECTION CLASSES --- */
        .hero-container {{
            text-align: center;
            padding-top: {ui_config['hero_padding_top']};
        }}
        .hero-title {{
            font-weight: {ui_config['hero_title_weight']};
            color: var(--text-color); /* Inherits from config.toml */
        }}
        .hero-subtitle {{
            color: #6c757d; /* Muted gray for subtitle */
            font-size: {ui_config['hero_subtitle_size']};
        }}
        
        .stExpander {{ border-radius: 10px !important; }}
    </style>
    """, unsafe_allow_html=True)


# --- 3. INITIALIZATION ---
st.set_page_config(
    page_title="DocuMate | Intelligence", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "lang_set" not in st.session_state:
    st.session_state.lang_set = "中文"

# --- 4. SIDEBAR (CONTROL CENTER) ---
with st.sidebar:
    st.title("🤖 DocuMate")
    
    # Pre-fetch the language state to prevent label lag
    if "lang_set" not in st.session_state:
        st.session_state.lang_set = "中文"
    
    # Determine the selectbox label based on the current state BEFORE rendering
    current_lang = st.session_state.lang_set
    selector_label = (
        SETTINGS["languages"]["中文"]["lang_label"] 
        if current_lang == "中文" 
        else SETTINGS["languages"]["English"]["lang_label"]
    )
    
    # Render the language selector
    selected_lang = st.selectbox(
        selector_label, 
        options=list(SETTINGS["languages"].keys()),
        index=1 if current_lang == "中文" else 0,
        key="lang_selector_widget" 
    )
    
    # Check if the selection has changed and trigger a rerun if necessary to sync CSS/UI
    if selected_lang != st.session_state.lang_set:
        st.session_state.lang_set = selected_lang
        st.rerun()
        
    # Set the active language dictionary 't'
    t = SETTINGS["languages"][selected_lang]
    
    # Inject layout CSS and localized "hacks" for the file uploader
    inject_custom_css(t, SETTINGS["ui"])
    
    # Render localized sidebar caption
    st.caption(t["sidebar_subtitle"])
    st.markdown(" ")

    # --- Data Ingestion Component ---
    with st.container(border=True):
        st.markdown(t["ingest_label"])
        # Use visible label to guide the user in their selected language
        uploaded_file = st.file_uploader(
            t["upload_label"], 
            type="pdf", 
            label_visibility="visible" 
        )
        
        if uploaded_file:
            if st.button(t["btn_analyze"], type="primary", use_container_width=True):
                with st.spinner(t["thinking"]):
                    files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                    try:
                        response = requests.post(f"{SETTINGS['backend_url']}/ingest", files=files)
                        if response.status_code == 200:
                            st.toast(t["toast_success"], icon="✨")
                        else:
                            st.error(t["err_engine"])
                    except Exception:
                        st.error(t["err_conn"])

    st.markdown(" ")
    # Sidebar clear button with localized text and icon
    if st.button(t["btn_clear"], icon=":material/refresh:", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# --- 5. MAIN INTERFACE ---

# Hero Screen
if not st.session_state.messages:
    st.markdown(f"""
    <div class='hero-container'>
        <h1 class='hero-title'>{t['welcome_title']}</h1>
        <p class='hero-subtitle'>{t['welcome_subtitle']}</p>
    </div>
    """, unsafe_allow_html=True)

# Render History
for msg in st.session_state.messages:
    icon = ":material/person:" if msg["role"] == "user" else ":material/smart_toy:"
    with st.chat_message(msg["role"], avatar=icon):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander(t["sources_header"]):
                for s in msg["sources"]: st.caption(f"• {s}")

# Chat Input
if prompt := st.chat_input(t["chat_input"]):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=":material/person:"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=":material/smart_toy:"):
        with st.spinner(t["thinking"]):
            try:
                res = requests.post(
                    f"{SETTINGS['backend_url']}/ask", 
                    json={"query": prompt, "language": selected_lang}
                )
                if res.status_code == 200:
                    data = res.json()
                    ans = data.get("answer", "")
                    srcs = data.get("sources", [])
                    display_ans = ans.replace(r"\(", "$").replace(r"\)", "$")
                    display_ans = display_ans.replace(r"\[", "$$").replace(r"\]", "$$")
                    
                    st.markdown(display_ans)
                    if srcs:
                        with st.expander(t["sources_header"]):
                            for s in srcs: st.caption(f"• {s}")
                    st.session_state.messages.append({"role": "assistant", "content": display_ans, "sources": srcs})
                    
                else:
                    st.error(t["err_engine"])
            except:
                st.error(t["err_conn"])