import ollama 
from database import collection

def get_context(query, n_results=3):
    results = collection.query(
        query_texts = [query],
        n_results = n_results
    )
    
    return "\n\n--\n\n".join(results['documents'][0])

def chat_with_docs(user_message):
    context = get_context(user_message)
    
    prompt = f"""
    ### SYSTEM INSTRUCTION
    You are the 'Kodalens' Technical Assistant. Use the following internal 
    documentation from Jira, GitHub, and GitLab to answer the user's question accurately.
    If the answer isn't in the context, say you don't know based on current docs.

    ### DOCUMENTATION CONTEXT
    {context}

    ### USER QUESTION
    {user_message}

    ### ASSISTANT RESPONSE
    """
    response = ollama.generate(
        model='',
        prompt=prompt,
        stream=False
    )
    return response['response']