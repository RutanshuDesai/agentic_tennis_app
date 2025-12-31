from chroma_utils import ChromaUtils
from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")

c=ChromaUtils(collection_name="general_docs", persist_db_directory='app_db', embeddings_model=embeddings)

### EXPLORE VECTOR DATABASE COLLECTIONS. Considers the entire chroma db path directory.
collections = c.list_collections()
print(collections)

### VIEW VECTOR DATABASE ITEMS AS A PANDAS DATAFRAME. Can run this code in notebook for more detailed analysis.
data_df = c.view_vector_items(limit=25)
print(data_df)
