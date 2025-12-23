import chroma_utils as c
from langchain_ollama import OllamaEmbeddings
import glob

embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")
vector_store = c.instantiate_vector_db(collection_name="general_docs", persist_db_directory="app_db", embeddings_model=embeddings)

### READ DOCUMENTS
for path in glob.glob("/data/*.pdf"): ## edit this to your own data folder
    docs = c.read_documents(file_path=path)
    chunks = c.split_documents(documents=docs)
    vector_store = c.add_chunked_documents_to_vector_db(vector_store=vector_store, chunks=chunks)

'''### EXPLORE VECTOR DATABASE
collections = c.list_collections(persist_db_directory="test_db")
print(collections)

data_df = c.view_vector_database_items_as_pandas_dataframe(db_path="test_db", collection_name="test_collection")
data_df'''