import chromadb
from chromadb.config import Settings
import os

class DatabaseSingleton:
    _instance = None
    _collection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseSingleton,cls).__new__(cls)
            
            cls._client = chromadb.PersistentClient(path="./docs_db")
            
            cls._collection = cls._client.get_or_create_collection(
                name="project_docs",
                metadata={"hnsw:space": "cosine"}
            )
            print("Database Singleton Initialized")
            
        return cls._instance
    
    @property
    def collection(self):
        return self._collection

db_instance = DatabaseSingleton()
collection = db_instance.collection