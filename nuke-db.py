import chromadb

client = chromadb.PersistentClient(path="./docs_db")
collection = client.get_collection(name="project_docs")

# Get all IDs currently in the DB
existing_ids = collection.get()['ids']

if existing_ids:
    collection.delete(ids=existing_ids)
    print(f"🧹 Cleaned {len(existing_ids)} items from the database.")
else:
    print("📭 Database is already empty.")