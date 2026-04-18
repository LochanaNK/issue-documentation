import chromadb

client  = chromadb.PersistentClient(path="./docs_db")
collection = client.get_collection(name="project_docs")

def search_issues(query_text: str, n_results: int=3, threshhold: float=1.0):
    # query = input("Search issue logs for: ")
    if not query_text.strip():
        return []
    
    
    results = collection.query(
        query_texts=[query_text], 
        n_results=n_results, 
        include=['documents','metadatas','distances']
    )

    matches = []
    found  = False

    for i in range(len(results['documents'][0])):
        distance = results['distances'][0][i]
        
        if distance < threshhold:
            found = True
            matches.append({
                "content": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": round(float(distance), 4)
            })
            print(f"\n---- Match found (distance: {distance: .4f}) ----")
            print(results['documents'][0][i],"\n")
    return matches      
            
if __name__ == "__main__":
    user_query = input("🔍 Search issue logs for: ")
    output = search_issues(user_query)
    
    if not output:
        print("❌ No relevant issues found.")
    for match in output:
        print(f"\n--- Match Found (Dist: {match['distance']}) ---")
        print(match['content'])
            
            
    # for doc in results["documents"][0]:
    #     print("\n--- Found Match ---")
    #     print(doc)