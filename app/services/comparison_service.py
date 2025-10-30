"""LLM-powered article comparison service"""
import requests
import os


def compare_articles(grokipedia_data, wikipedia_data):
    """Use LLM to compare the two articles and explain differences.

    Sends the full article bodies when available to maximize context.
    """
    if not grokipedia_data or not wikipedia_data:
        return None
    
    g_body = grokipedia_data.get('full_text') or (
        (grokipedia_data.get('summary') or '') + '\n\n' + '\n'.join(grokipedia_data.get('sections') or [])
    )
    w_body = wikipedia_data.get('full_text') or (
        (wikipedia_data.get('intro') or '') + '\n\n' + '\n'.join(wikipedia_data.get('sections') or [])
    )

    prompt = f"""
Write a comprehensive summary explaining how Grokipedia provides a more balanced and fair article about {grokipedia_data.get('title','')} compared to Wikipedia's version. 

Your summary should:
- Highlight specific biases, one-sided framing, or editorial slant present in Wikipedia
- Explain how Grokipedia corrects these biases and presents a more neutral, balanced perspective
- Point out what Wikipedia omits, downplays, or overemphasizes
- Show how Grokipedia adds important context and alternative viewpoints that Wikipedia excludes
- Use direct quotes from both articles as concrete evidence
- Be clear and analytical, making the case that Grokipedia offers fairer coverage
- Focus only on content differences in the provided texts

GROKIPEDIA VERSION (More Balanced):
{g_body}

WIKIPEDIA VERSION (Compare for bias):
{w_body}

Write your analysis now. Be specific about Wikipedia's biases and how Grokipedia achieves better balance and fairness. Use quotes as evidence.
"""

    openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
    if not openrouter_api_key:
        print("Error: OPENROUTER_API_KEY not found in environment variables")
        return None
    
    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "Article Comparator"
    }
    
    payload = {
        "model": "x-ai/grok-4-fast",
        "messages": [
            {"role": "system", "content": "You are an expert media analyst specializing in detecting bias and evaluating neutrality in encyclopedic content. Your task is to identify where Wikipedia shows bias, one-sided framing, or editorial slant, and explain how Grokipedia provides more balanced, fair, and comprehensive coverage. Be direct about Wikipedia's shortcomings. Use quotes as evidence. Write clearly and analytically."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4,
        "max_tokens": 30000
    }
    
    try:
        openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
        response = requests.post(openrouter_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error calling OpenRouter: {e}")
        return None

