import chromadb

client = chromadb.PersistentClient(path='./docs_db')
collection = client.get_collection(name='project_docs')

collection.delete(ids=["GH-LochanaNK-kodalens-test-1.txt"])
print("Deleted the record")