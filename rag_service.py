import os
from dotenv import load_dotenv

# Import LangChain components
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA

# Load configuration from .env file
load_dotenv()

# Local storage path for the vector database
PERSIST_DIRECTORY = "./chroma_db"

class RAGService:
    def __init__(self):
        # 1. Initialize Embedding Model (converts text to vectors)
        # DeepSeek is compatible with OpenAI's API format, so OpenAIEmbeddings works here.
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_base=os.getenv("OPENAI_API_BASE"),
            check_embedding_ctx_length=False
        )
        
        # 2. Initialize LLM (The DeepSeek Brain)
        self.llm = ChatOpenAI(
            model=os.getenv("LLM_MODEL"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_base=os.getenv("OPENAI_API_BASE"),
            temperature=0.1 # Low temperature for more factual/deterministic answers
        )

    def ingest_file(self, file_path: str):
        """Core Function A: Ingest and process PDF document"""
        try:
            # Load PDF file
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            # Split text (Chunking)
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, 
                chunk_overlap=100
            )
            chunks = text_splitter.split_documents(documents)
            
            # Store in vector database (ChromaDB)
            # This step calls the Embedding API; it might take a few seconds on first run.
            Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=PERSIST_DIRECTORY
            )
            return {"status": "success", "chunks": len(chunks)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def ask_question(self, question: str):
        """Core Function B: Retrieve relevant context and Answer"""
        # Load the existing database
        vector_store = Chroma(
            persist_directory=PERSIST_DIRECTORY,
            embedding=self.embeddings
        )
        
        # Configure retriever to find top 3 relevant chunks
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        
        # Create RetrievalQA chain
        qa = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True
        )
        
        # Run the query
        result = qa.invoke({"query": question})
        
        # Format sources for citation
        sources = []
        for doc in result["source_documents"]:
            # Extract page number and preview text
            sources.append(f"Page {doc.metadata.get('page', 0)}: {doc.page_content[:50]}...")
            
        return {
            "answer": result["result"],
            "sources": sources
        }