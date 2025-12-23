import streamlit as st
import requests

# Set page configuration
st.set_page_config(page_title="DocuMate", page_icon="🧠")
st.title("DocuMate: Your AI Document Assistant 🧠")

# Initialize chat history in session state to keep memory during reruns
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar: Document Upload Section ---
with st.sidebar:
    st.header("📄 Upload Document")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        if st.button("Start Ingesting"):
            with st.spinner("AI is reading the document, please wait..."):
                # Prepare the file to send to the backend
                files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                try:
                    # Send POST request to FastAPI backend
                    # Note: Ensure your backend is running on port 8000
                    response = requests.post("http://127.0.0.1:8000/ingest", files=files)
                    
                    if response.status_code == 200:
                        st.success("✅ Ingestion complete! You can now chat with the document.")
                    else:
                        st.error(f"Error processing file: {response.text}")
                except Exception as e:
                    st.error(f"Failed to connect to backend: {e}")

# --- Main Area: Chat Interface ---

# 1. Display existing chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 2. Chat Input Area
if prompt := st.chat_input("Ask a question about the document..."):
    # Display user message immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response from AI Assistant
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Send query to FastAPI backend
            api_response = requests.post("http://127.0.0.1:8000/ask", json={"query": prompt})
            
            if api_response.status_code == 200:
                data = api_response.json()
                full_response = data.get("answer", "I don't know the answer based on the document.")
                
                # If there are sources, append them to the response
                if "sources" in data and data["sources"]:
                    full_response += "\n\n**Sources:**\n"
                    for src in data["sources"]:
                        full_response += f"- {src}\n"
            else:
                full_response = "❌ Backend returned an error. Please check the server logs."
        
        except Exception as e:
            full_response = f"❌ Connection error: {e}"

        # Display final response and save to history
        message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})