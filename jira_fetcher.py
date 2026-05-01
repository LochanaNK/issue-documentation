import os
from jira import JIRA
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from time import time

load_dotenv()

JIRA_SERVER = os.getenv("JIRA_SERVER")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")

def process_single_jira_project(project_key, jira_conn, output_dir):
    synced_count = 0
    try:
        print(f"⌕  Checking Jira: {project_key}")
        
        #using JQL to get closed issues
        jql = f'project = "{project_key}" AND statusCategory = Done'
        
        issues = jira_conn.search_issues(jql, maxResults=100)
        
        for issue in issues:
            issue_id = f"JR-{project_key}-{issue.key}"
            file_name = f"{issue_id}.txt"
            file_path = os.path.join(output_dir, file_name)
            
            summary = issue.fields.summary
            desc = issue.fields.description if issue.fields.description else "No description provided."
            created = issue.fields.created
            
            content = (
                f"SOURCE: Jira Issue {project_key} {issue.key}\n"
                f"URL: {JIRA_SERVER}/browse/{issue.key}\n"
                f"TITLE: {summary}\n"
                f"CREATED: {created}\n"
                f"LABELS: {issue.fields.labels}\n\n"
                f"NOTES:\n"
                f"{desc}"
            )
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            synced_count +=1
        
    except Exception as e:
        print(f"❌ Error in Jira Project {project_key}: {e}")
    
    return synced_count


def fetch_jira_issues(output_dir="./input_docs"):
    if not all([JIRA_SERVER, JIRA_EMAIL, JIRA_TOKEN]):
        print("❌ Missing Jira configuration. Please set JIRA_SERVER, JIRA_EMAIL, and JIRA_TOKEN in the .env file.")
        return

    os.makedirs(output_dir, exist_ok=True)
    start_time = time()

    try:
        jira = JIRA(server=JIRA_SERVER, basic_auth=(JIRA_EMAIL, JIRA_TOKEN))
        
        print("📡 Connecting to Jira: {JIRA_SERVER}")
        projects = jira.projects()
        project_keys = [p.key for p in projects]
        
        print(f"\n▷  Starting parallel Jira sync for {len(project_keys)} projects...\n")
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(lambda k: process_single_jira_project(k, jira, output_dir), project_keys))
            
        end_time = time()
        duration = end_time - start_time
        print("\n" + "="*40)
        print(f"⏱️  Jira Sync: {duration:.2f} seconds")
        print(f"✅ Total Jira issues synced: {sum(results)}")
        print("="*40 + "\n")

    except Exception as e:
        print(f"❌ Unexpected Jira error: {e}")