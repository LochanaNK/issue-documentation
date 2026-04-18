import hashlib
import ollama
import os
import chromadb
from datetime import datetime

from github_fetcher import fetch_github_issues

client = chromadb.PersistentClient(path="./docs_db")
collection = client.get_or_create_collection(name="project_docs")

output_dir = "./processed_docs"
os.makedirs(output_dir, exist_ok=True)

MASTER_TEMPLATE = """
# [PROJECT_ID] | Issue Resolution Log

## 🛠 Summary
- **Identifier:** [PROJECT_ID]
- **Date Processed:** [DATE]
- **Category:** [CATEGORY]

## 🔍 The Problem
> [PROBLEM DESCRIPTION]

## 💡 Resolution
### Root Cause
- [ROOT CAUSE]

### Implementation
- [TECHNICAL STEPS TAKEN]

## ✅ Verification
- [HOW IT WAS TESTED]
"""

def get_file_hash(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def process_file(file_path):
    
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_text = f.read()
        
        current_hash = get_file_hash(raw_text)
        
        file_name = os.path.basename(file_path)

        
        
        existing_doc = collection.get(ids=[file_name])
        if existing_doc['ids']:
            stored_hash = existing_doc['metadatas'][0].get('hash')
            if stored_hash == current_hash:
                print(f">>  Skipping: {file_name} (Content unchanged)")
                return
            else:
                print(f"(<) Redoing: {file_name} (Updates detected)")
                
        else:
            print(f"++ Processing New File: {file_name}...")
        
        
        prompt = f"""
        You are a technical documentation assistant. 
        Analyze the 'Scattered Notes' below and map them EXACTLY into the provided 'Master Template'.
        
        RULES:
        1. Output ONLY the filled Markdown. 
        2. Identify the project context from the 'SOURCE' line and use it to determine the CATEGORY in the template.
        3. Do not include any introductory text, pleasantries, or summaries.
        4. If information is missing for a section, write "Not specified".
        5. Current Date is {datetime.now().strftime('%Y-%m-%d')}.

        MASTER TEMPLATE:
        {MASTER_TEMPLATE}

        SCATTERED NOTES:
        {raw_text}
        
        
        """
        
        try:
            response = ollama.generate(
            model='gemma4:e4b', 
            prompt=prompt,
            options={'temperature': 0}
            )
            
            clean_doc = response['response'].strip()
            
            file_name = os.path.basename(file_path)
            output_path = os.path.join(output_dir, f"{file_name}_processed.md")
            
            with open(output_path, 'w', encoding='utf-8') as out_f:
                out_f.write(clean_doc)
            
            collection.upsert(
                documents=[clean_doc],
                ids=[file_name],
                metadatas=[{"source": file_path, "date": datetime.now().isoformat(), "hash": current_hash}]
            )
            print(f"Processed: {file_path} -> {output_path}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
        
doc_dir = "./input_docs"
if os.path.exists(doc_dir):
    fetch_github_issues(output_dir=doc_dir)
    for filename in os.listdir(doc_dir):
        if filename.endswith(('.txt', '.md')):
            process_file(os.path.join(doc_dir, filename))
else:
    print(f"Directory {doc_dir} not found.")