import chromadb

client  = chromadb.PersistentClient(path="./docs_db")
collection = client.get_collection(name="project_docs")

query = input("Search issue logs for: ")
results = collection.query(
    query_texts=[query], 
    n_results=3, 
    include=['documents','metadatas','distances']
)

found  = False

for i in range(len(results['documents'][0])):
    distance = results['distances'][0][i]
    
    if distance < 1.0:
        found = True
        print(f"\n---- Match found (distance: {distance: .4f}) ----")
        print(results['documents'][0][i],"\n")
        
        
if not found:
        print("❌ No relevant issues found for that query.")
        
        
# for doc in results["documents"][0]:
#     print("\n--- Found Match ---")
#     print(doc)