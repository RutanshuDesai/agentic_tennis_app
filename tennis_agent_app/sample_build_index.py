from chroma_utils import ChromaUtils
from langchain_ollama import OllamaEmbeddings
import glob

embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")

c = ChromaUtils(collection_name="tech_docs", persist_db_directory='app_db', embeddings_model=embeddings)

### READ DOCUMENTS
for path in glob.glob("data/*.pdf"): ## edit this to your own data folder
    docs=c.read_documents(file_path=path)
    chunks=c.split_documents(documents=docs)
    c.add_chunked_documents(chunks=chunks)