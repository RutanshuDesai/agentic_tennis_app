import os
import glob
from dotenv import load_dotenv
import pandas as pd

import chromadb
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

# Load environment variables
load_dotenv()
#embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")

class ChromaUtils:
    def __init__(self, collection_name: str, persist_db_directory: str, embeddings_model: str) -> Chroma:
        '''
        Instantiate a vector database. Loads existing vector database from persist_db_directory if it exists else creates a new vector database.
        Args:
            collection_name: name of the collection
            persist_db_directory: directory to persist the database
            embeddings_model: model to use for embeddings
        Returns:
            vector_store: instantiated vector database
        '''

        self.collection_name=collection_name
        self.persist_db_directory=persist_db_directory
        self.embeddings_model=embeddings_model

        ### CREATE OR READ VECTOR DATABASE
        self.vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings_model,
            persist_directory=self.persist_db_directory
        )


    ### READ DOCUMENTS
    def read_documents(self, file_path: str):    
        '''
        Read documents from a file. Supported file types: PDF
        Args:
            file_path: path to the file
        Returns:
            documents: list of documents
        '''
        loader = PyPDFLoader(file_path, mode="single")
        return loader.load()

    ### SPLIT/CHUNK DOCUMENTS
    def split_documents(self, documents: list):
        '''
        Split documents into chunks
        Args:
            documents: list of documents
        Returns:
            chunks: list of chunks
        '''
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        return text_splitter.split_documents(documents)



    ### ADD CHUNKED DOCUMENTS TO VECTOR DATABASE
    def add_chunked_documents(self, chunks: list):
        '''
        Add chunked documents to vector database
        Args:
            vector_store: vector database
            chunks: list of chunks
        Returns:
            vector_store: vector database
        '''
        self.vector_store.add_documents(chunks)



    ### LIST COLLECTIONS FROM A VECTOR DATABASE
    def list_collections(self):
        '''
        List collections in the vector database
        Args:
            persist_db_directory: directory to persist the database
        Returns:
            collections: list of collections
        '''
        client = chromadb.PersistentClient(path=self.persist_db_directory)
        return client.list_collections()

    ### VIEW VECTOR DATABASE ITEMS AS A PANDAS DATAFRAME    
    def view_vector_items(self):
        '''
        View vector database items as a pandas dataframe
        Args:
            vector_store: vector database
        Returns:
            dataframe: pandas dataframe
        '''
        client = chromadb.PersistentClient(path=self.persist_db_directory)
        collection = client.get_collection(self.collection_name)


        data = collection.peek()  # usually returns e.g., {"ids": [...], "documents": [...], "metadatas": [...]}
        data_df = pd.DataFrame({
            "id": data["ids"],
            "document": data["documents"],
            "metadata": data["metadatas"]
        })

        return data_df