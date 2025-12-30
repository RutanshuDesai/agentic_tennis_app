from chroma_utils import ChromaUtils
from langchain_ollama import OllamaEmbeddings
import glob

embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")

dir_path='tennis_agent_app'
c = ChromaUtils(collection_name="general_docs", persist_db_directory=dir_path+"/db_test", embeddings_model=embeddings)

### READ DOCUMENTS
for path in glob.glob("data/*.pdf"): ## edit this to your own data folder
    docs=c.read_documents(file_path=path)
    chunks=c.split_documents(documents=docs)
    c.add_chunked_documents(chunks=chunks)

### EXPLORE VECTOR DATABASE
collections = c.list_collections()
print(collections)

data_df = c.view_vector_items()
print(data_df)