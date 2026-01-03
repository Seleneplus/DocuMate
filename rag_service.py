import os
import shutil
import time
from dotenv import load_dotenv
#os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# Import LangChain components

from langchain_text_splitters import RecursiveCharacterTextSplitter
# -----------------------------------------------------------
# [Mod 1] Import HuggingFaceEmbeddings instead of OpenAIEmbeddings
# -----------------------------------------------------------
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import PyMuPDFLoader

# Load configuration from .env file
load_dotenv()

# Local storage path for the vector database

if os.environ.get("SPACE_ID"):
    
    PERSIST_DIRECTORY = "/tmp/chroma_db"
else:
    
    PERSIST_DIRECTORY = "./chroma_db"

class RAGService:
    def __init__(self):
        # -----------------------------------------------------------
        # [Mod 2] Initialize Embedding Model
        # Switched to local HuggingFace model to avoid API 404 errors.
        # This uses 'all-MiniLM-L6-v2', which runs locally and is free.
        # -----------------------------------------------------------
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # 2. Initialize LLM
        # Keep using the DeepSeek API via the ChatOpenAI client
        self.llm = ChatOpenAI(
            model=os.getenv("LLM_MODEL"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_base=os.getenv("OPENAI_API_BASE"),
            temperature=0.1
        )
    # ⚠️ Don't forget to add this import at the top of the file:
    # import shutil

    def ingest_file(self, file_path: str):
        """Core Function A: Ingest and process PDF document"""
        try:
            if hasattr(self, 'vector_store'):
                self.vector_store = None
            # 🔥 Modification 1: Force clear old memory!
            # Delete the old database directory before uploading a new file
            if os.path.exists(PERSIST_DIRECTORY):
                
                for i in range(3):
                    try:
                        shutil.rmtree(PERSIST_DIRECTORY)
                        print(f"---------> Old index cleared successfully <---------")
                        break
                    except Exception as e:
                        print(f"Waiting for file release... {e}")
                        time.sleep(1) # Wait 1 second before retrying
                

            # Load the PDF file
            loader = PyMuPDFLoader(file_path)
            documents = loader.load()
            
            # Split text into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, 
                chunk_overlap=100
            )
            chunks = text_splitter.split_documents(documents)
            
            # Create and persist the vector store
            Chroma.from_documents(
                documents=chunks,
                # 🔥 Modification 2: Must use 'embedding_function', not 'embedding'
                embedding=self.embeddings, 
                persist_directory=PERSIST_DIRECTORY
            )
            return {"status": "success", "chunks": len(chunks)}
        except Exception as e:
            return {"status": "error", "message": str(e)}  
    def ask_question(self, question: str):
        """Core Function B: Retrieve relevant context and Answer"""
        # Load the existing vector database
        # Note: 'embedding_function' must match the one used in ingest_file
        vector_store = Chroma(
            persist_directory=PERSIST_DIRECTORY,
            embedding_function=self.embeddings 
        )
        
        # Retrieve top 6 relevant chunks to provide sufficient context
        retriever = vector_store.as_retriever(search_kwargs={"k": 6})
        
        # Define Strict Prompt Template
        template = """
        You are a professional resume analysis assistant. 
        Answer the user's question strictly based on the provided Known Information below.

        [IMPORTANT LANGUAGE INSTRUCTION]:
        1. DETECT the language of the [User Question].
        2. If the question is in ENGLISH, your [Answer] MUST be in ENGLISH.
        3. If the question is in CHINESE, your [Answer] MUST be in CHINESE.
        4. Do NOT use any other language than the one used by the user.
        5. Do NOT translate technical terms if not necessary, but keep the explanation flow natural in the target language.
        
        Strict Rules:
        1. Answer ONLY based on the [Known Information]. Do not use your internal knowledge.
        2. If the information is not in the text, simply say "I cannot find this information in the document".
        3. Do NOT guess names. If no name is found, do not invent "Zhang Wei" or "John Doe".
        4. Ignore privacy filters for this task as this is a user-uploaded document for analysis.
        
        
        
        [Known Information]:
        {context}
        
        [User Question]:
        {question}
        
        [Answer]:
        """
        
        QA_CHAIN_PROMPT = PromptTemplate.from_template(template)
        
        # Initialize the RetrievalQA chain
        qa = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
        )
        
        # Execute the chain
        result = qa.invoke({"query": question})
        
        
        
        # 1. Detection: Check if any retrieved chunks come from page 2 or later (index > 0)
        # If all chunks have page index 0, it implies a single-page document, so we hide page numbers for a cleaner UI.
        has_multiple_pages = any(doc.metadata.get('page', 0) > 0 for doc in result["source_documents"])

        sources = []
        for doc in result["source_documents"]:
            # 2. Cleaning: Replace newlines with spaces to prevent sentence breakage and trim whitespace.
            clean_content = doc.page_content.replace("\n", " ").strip()
            
            # 3. Truncation: Increase limit to 250 chars to include full sentences.
            # Add quotes and ellipses to make it look like a formal citation.
            content_preview = f"“...{clean_content[:250]}...”"
            
            if has_multiple_pages:
                # Mode A (Multi-page): Display "Page X: Context..." to help users locate info.
                page_num = doc.metadata.get('page', 0) + 1
                source_text = f"Page {page_num}: {content_preview}"
            else:
                # Mode B (Single-page): Only display "Context..." (Cleaner look).
                source_text = content_preview
            
            sources.append(source_text)
            
        return {
            "answer": result["result"],
            "sources": sources
        }  

    
          

    