import chroma_utils as c
from langchain_ollama import OllamaEmbeddings
import glob

embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")

vector_store = c.ChromaUtils(collection_name="test_docs3", persist_db_directory="app_db_test", embeddings_model=embeddings)

### READ DOCUMENTS
for path in glob.glob("data/*.pdf"): ## edit this to your own data folder
    docs = vector_store.read_documents(file_path=path)
    chunks = vector_store.split_documents(documents=docs)
    vector_store.add_chunked_documents(chunks=chunks)

### EXPLORE VECTOR DATABASE
collections = vector_store.list_collections()
print(collections)

data_df = vector_store.view_vector_items()
print(data_df)