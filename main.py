import os
import shutil
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from rag_service import RAGService

app = FastAPI(title="DocuBrain API")

# Initialize the RAG service
rag = RAGService()

class QueryRequest(BaseModel):
    question: str

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # 1. Save uploaded file to a temporary directory
    temp_file = f"temp_{file.filename}"
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 2. Ingest the file (Process and Index)
    result = rag.ingest_file(temp_file)
    
    # 3. Clean up: Remove the temporary file
    os.remove(temp_file)
    
    return result

@app.post("/chat")
async def chat(request: QueryRequest):
    # Generate answer using RAG
    return rag.ask_question(request.question)