import hashlib
import json
import ollama
import os
import chromadb
from datetime import datetime
from time import time
from concurrent.futures import ThreadPoolExecutor

from github_fetcher import fetch_github_issues

client = chromadb.PersistentClient(path="./docs_db")
collection = client.get_or_create_collection(name="project_docs")

output_dir = "./processed_docs"
os.makedirs(output_dir, exist_ok=True)

JSON_TEMPLATE = {
    "identifier": "[PROJECT_ID]",
    "date_processed": "[DATE]",
    "category": "[CATEGORY]",
    "problem_description": "[PROBLEM]",
    "resolution": {
        "root_cause": "[ROOT_CAUSE]",
        "technical_steps": "[STEPS]",
        "verification": "[TESTING]"
    }
}

def get_file_hash(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()



def process_file(file_path):
    file_start_time = time()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()
            
            current_hash = get_file_hash(raw_text)
            
            file_name = os.path.basename(file_path)

            
            
            existing_doc = collection.get(ids=[file_name])
            if existing_doc['ids']:
                stored_hash = existing_doc['metadatas'][0].get('hash')
                if stored_hash == current_hash:
                    print(f"❯❯❯❯  Skipping: {file_name} (Content unchanged)")
                    return
                else:
                    print(f"⟲  Redoing: {file_name} (Updates detected)")
                    
            else:
                print(f"\nⴵ  Processing New File: {file_name}...\n")
            
            
            prompt = f"""
            You are a technical data extractor. Extract information from 'SCATTERED NOTES' into the 'JSON TEMPLATE' structure.

            RULES:
            1. Output ONLY a valid JSON object. Do not wrap the JSON itself in markdown blocks (no ```json).
            2. For 'technical_steps' and 'root_cause', if the notes contain code, commands, or configuration, format them using Markdown code blocks with the appropriate language identifier (e.g., ```cpp, ```python, or ```bash).
            3. Identify the project context from the 'SOURCE' line for the 'category'.
            4. Use "Not specified" for missing fields.
            5. Current Date: {datetime.now().strftime('%Y-%m-%d')}.

            JSON TEMPLATE:
            {json.dumps(JSON_TEMPLATE, indent=2)}

            SCATTERED NOTES:
            {raw_text}
            """
            
            response = ollama.generate(
            model='gemma4:e4b', 
            prompt=prompt,
            options={'temperature': 0, 'format': 'json'}
            )
            
            clean_doc = json.loads(response['response'].strip())
            
            file_name = os.path.basename(file_path)
            output_path = os.path.join(output_dir, f"{file_name}_processed.json")
            
            with open(output_path, 'w', encoding='utf-8') as out_f:
                json.dump(clean_doc, out_f, indent=4)
            
            collection.upsert(
                documents=[json.dumps(clean_doc)],
                ids=[file_name],
                metadatas=[{"source": file_path, "date": datetime.now().isoformat(), "hash": current_hash}]
            )
            print(f"Processed: {file_path} -> {output_path}")
    except Exception as e:
            print(f"Error processing {file_path}: {e}")
        
    file_duration = time() - file_start_time
    print(f"  \n⏱ Time: {file_duration:.2f}s ({file_duration/60:.2f} minutes)\n")
        
def run_processor():
        
    doc_dir = "./input_docs"
    if os.path.exists(doc_dir):
        fetch_github_issues(output_dir=doc_dir)
        files_to_process = [
            os.path.join(doc_dir, filename)
            for filename in os.listdir(doc_dir)
            if filename.endswith(('.txt', '.md'))
        ]
        print(f"\n🚀 Starting Multi-threaded AI Sync ({len(files_to_process)} files)...")
        start_time = time()
        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                executor.map(process_file, files_to_process)
        finally:
            duration = time() - start_time
            print("\n" + "="*50)
            print(f"✓ ALL FILES PROCESSED")
            print(f" ⏱ Total processing time: {duration:.2f} seconds ({duration/60:.2f} minutes)")
            print("="*50 + "\n")
    else:
        print(f"Directory {doc_dir} not found.")
