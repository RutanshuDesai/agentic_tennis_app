import os
import glob
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

# Load environment variables
load_dotenv()

def create_vector_db():
    # 1. Define paths
    # Use the script's location to determine the project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    data_dir = os.path.join(project_root, "data")
    persist_directory = os.path.join(project_root, "chroma_db")
    
    print(f"Looking for PDFs in: {data_dir}")
    
    # 2. Load Documents
    pdf_files = glob.glob(os.path.join(data_dir, "*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in the data directory.")
        return

    docs = []
    for pdf_file in pdf_files:
        print(f"Loading: {pdf_file}")
        loader = PyPDFLoader(pdf_file)
        docs.extend(loader.load())
    
    print(f"Loaded {len(docs)} pages from {len(pdf_files)} PDF files.")

    # 3. Split Documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(docs)
    print(f"Split into {len(splits)} chunks.")

    from langchain_ollama import OllamaEmbeddings
    embedding_model = OllamaEmbeddings(model="nomic-embed-text:latest")
    
    # 5. Create and Persist Vector Store
    print("Creating vector store... this may take a moment.")
    # This will automatically persist to disk because persist_directory is set
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embedding_model,
        persist_directory=persist_directory
    )
    
    # Explicitly persist to ensure data is saved
    # (In newer Chroma versions this is auto, but good to be safe)
    vectorstore.persist()
    
    print(f"Successfully saved vector database to {persist_directory}")

if __name__ == "__main__":
    create_vector_db()
