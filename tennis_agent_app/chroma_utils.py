from dotenv import load_dotenv
import pandas as pd

import chromadb
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

import logging
logger = logging.getLogger(__name__)


# Load environment variables
load_dotenv()

class ChromaUtils:
    def __init__(self, collection_name: str, persist_db_directory: str, embeddings_model: str):
        '''
        Instantiate a vector database. Loads existing vector database from persist_db_directory if it exists else creates a new vector database.
        Args:
            collection_name: name of the collection
            persist_db_directory: directory to persist the database
            embeddings_model: model to use for embeddings
        Returns:
            vector_store: instantiated vector database
        '''

        logger.info("Initializing ChromaUtils", extra={"collection_name": collection_name, "persist_dir": persist_db_directory})


        self.collection_name=collection_name
        self.persist_db_directory=persist_db_directory
        self.embeddings_model=embeddings_model

    def create_vector_collection(self):   
        
        try:
            self.vector_collection = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings_model,
                persist_directory=self.persist_db_directory
            )

            logger.info("Chroma vector store initialized successfully")
            return self.vector_collection
        except Exception:
            logger.exception("Failed to initialize chroma vector db")
            raise

    ### READ DOCUMENTS
    @staticmethod
    def read_documents(file_path: str):    
        '''
        Read documents from a file. Supported file types: PDF
        Args:
            file_path: path to the file
        Returns:
            documents: list of documents
        '''
        loader = PyPDFLoader(file_path, mode="single")
        logger.info("Documents read successfully")

        return loader.load()

    ### SPLIT/CHUNK DOCUMENTS
    @staticmethod
    def split_documents(documents: list):
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
        logger.info("Documents chunked successfully")
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
        if not hasattr(self, 'vector_store'):
            vector_store = self.create_vector_collection()
        vector_store.add_documents(chunks)
        logger.info("Chunks added to vector db successfully")
        return vector_store



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
    def view_vector_items(self, limit: int = 25):
        '''
        View vector database items as a pandas dataframe
        Args:
            vector_store: vector database
        Returns:
            dataframe: pandas dataframe
        '''

        ## getting raw data from vector database
        v = self.create_vector_collection()
        data = v.get(limit=limit)

        ## converting raw data to pandas dataframe
        pandas_data=pd.DataFrame(data['ids'])
        pandas_data['documents']=data['documents']
        pandas_data['metadatas']=data['metadatas']

        ## extracting file name from metadata
        def extract_file_name(doc_metadata):
            return doc_metadata['source'].split('/')[-1]

        pandas_data['source'] = pandas_data['metadatas'].apply(extract_file_name)


        return pandas_data