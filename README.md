# 🤖 DocuMate: Industrial-Grade RAG Document Intelligence

DocuMate is a high-performance RAG (Retrieval-Augmented Generation) assistant designed to transform static PDFs into interactive, verifiable knowledge bases. It features a privacy-first hybrid AI architecture and a fully localized professional UI.

---

## 🏗️ Technical Stack

* **Frontend**: **Streamlit** (Enhanced with **Custom CSS Injection** for 100% UI localization).
* **Backend**: **Python / FastAPI** (Asynchronous processing for high-concurrency document ingestion).
* **LLM Engine**: **DeepSeek-V3** (Accessed via OpenAI-compatible API) — leverages state-of-the-art reasoning for natural language generation.
* **Embedding Model**: **HuggingFace** (`sentence-transformers/all-MiniLM-L6-v2`) — Localized execution for data privacy and zero API costs.
* **Vector Database**: **ChromaDB** — Persistent storage for high-precision semantic retrieval.
* **Orchestration**: **LangChain** (RecursiveCharacterTextSplitter, PyMuPDFLoader).
* **Theming**: Configuration-driven via `.streamlit/config.toml` (Primary Color: `#4F46E5`).

---

## 🛠️ Engineering Challenges Solved

### 1. State-Driven UI Synchronization
Solved the "Label Lag" issue where UI labels wouldn't sync immediately after a language switch. By utilizing `st.session_state` pre-calculation, the interface now responds instantly with correct localized headers.

### 2. Overcoming Framework Constraints (Deep Customization)
Streamlit's native `file_uploader` has hardcoded English prompts. I implemented **CSS Pseudo-element Hijacking** to force-translate internal strings like "Drag and drop", ensuring a seamless 100% Chinese experience.

### 3. Reliability via Mirroring
Configured `HF_ENDPOINT` mirroring to ensure stable model downloads and 100% service uptime in restricted network environments.

---

## 🌟 Key Highlights

* **Zero-Hardcoding Architecture**: Fully driven by configuration files and localized dictionaries for maximum maintainability.
* **Fact-Checking & Traceability**: Automated citation system (📍 原始文本参考) that links every AI response back to the specific document page numbers.
* **Language-Adaptive Intelligence**: Engineered a zero-shot language detection prompt that ensures the assistant's response language strictly matches the user's input.

---


## 🚀 Usage

### Option A: Online Demo (Recommended)
[Click here to access the Live Demo](your-website-link)

### Option B: Local Development
If you wish to study the source code or run the application in a local environment, please follow these steps:

1.  **Clone the Repository**:
    ```bash
    git clone [https://github.com/Seleneplus/DocuMate.git](https://github.com/Seleneplus/DocuMate.git)
    cd DocuMate
    ```
2.  **Install Dependencies**:
    Ensure you have Python installed, then run:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Environment Variables**:
    Create a `.env` file in the root directory and add your DeepSeek API credentials:
    ```env
    OPENAI_API_KEY=your_deepseek_api_key
    OPENAI_API_BASE=[https://api.deepseek.com/v1](https://api.deepseek.com/v1)
    LLM_MODEL=deepseek-chat
    ```
4.  **Run the Application**:
    ```bash
    streamlit run app.py
    ```
