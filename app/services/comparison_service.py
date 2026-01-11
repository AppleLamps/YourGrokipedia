"""LLM-powered article comparison service"""
import logging
import os
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)

# API timeouts (seconds)
DEFAULT_TIMEOUT = 30
LLM_TIMEOUT = 120

# Module-level session for connection pooling
_session: Optional[requests.Session] = None


def _get_session() -> requests.Session:
    """Get or create a shared requests session for connection pooling."""
    global _session
    if _session is None:
        _session = requests.Session()
    return _session


def _make_api_request(payload: dict[str, Any], timeout: int = DEFAULT_TIMEOUT) -> Optional[str]:
    """Make API request with xAI primary and OpenRouter fallback."""
    xai_api_key = os.getenv('XAI_API_KEY')
    openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
    
    if not xai_api_key and not openrouter_api_key:
        logger.error("Neither XAI_API_KEY nor OPENROUTER_API_KEY found")
        return None
    
    # Try xAI first
    if xai_api_key:
        try:
            headers = {
                "Authorization": f"Bearer {xai_api_key}",
                "Content-Type": "application/json",
            }
            xai_payload = {**payload, "model": "grok-4-1-fast"}
            response = _get_session().post(
                "https://api.x.ai/v1/chat/completions",
                headers=headers,
                json=xai_payload,
                timeout=timeout
            )
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                logger.warning("xAI API error %d, trying OpenRouter fallback", response.status_code)
        except Exception as e:
            logger.warning("xAI API error: %s, trying OpenRouter fallback", e)
    
    # Fallback to OpenRouter
    if openrouter_api_key:
        try:
            headers = {
                "Authorization": f"Bearer {openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "Article Comparator"
            }
            openrouter_payload = {**payload, "model": "x-ai/grok-4.1-fast"}
            response = _get_session().post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=openrouter_payload,
                timeout=timeout
            )
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            logger.error("OpenRouter API error: %s", e)
    
    return None


def generate_grokipedia_tldr(grokipedia_data: Optional[dict[str, Any]]) -> Optional[str]:
    """Generate a TLDR summary for the Grokipedia article."""
    if not grokipedia_data:
        return None
    
    g_body = grokipedia_data.get('full_text') or (
        (grokipedia_data.get('summary') or '') + '\n\n' + '\n'.join(grokipedia_data.get('sections') or [])
    )

    prompt = f"""
Create a concise TLDR summary of the following Grokipedia article about {grokipedia_data.get('title','')}.

Your summary should:
- Be brief and to the point (2-3 sentences maximum)
- Capture the main points and key information
- Maintain a neutral, informative tone
- Focus on the essential content of the article

ARTICLE:
{g_body}

Write the TLDR summary now:
"""

    payload = {
        "messages": [
            {"role": "system", "content": "You are an expert at creating concise, informative TLDR summaries. Focus on extracting the most important information and presenting it clearly and briefly."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 150
    }
    
    return _make_api_request(payload, timeout=DEFAULT_TIMEOUT)


def generate_wikipedia_summary(wikipedia_data: Optional[dict[str, Any]]) -> Optional[str]:
    """Generate a summary about the Wikipedia article."""
    if not wikipedia_data:
        return None
    
    w_body = wikipedia_data.get('full_text') or (
        (wikipedia_data.get('intro') or '') + '\n\n' + '\n'.join(wikipedia_data.get('sections') or [])
    )

    prompt = f"""
Create a summary about the following Wikipedia article covering {wikipedia_data.get('title','')}.

Your summary should:
- Describe what the Wikipedia article covers
- Mention the scope and main topics included
- Note any notable aspects of the article's structure or content
- Be informative about the article itself rather than just summarizing the topic
- Keep it concise but comprehensive (3-4 sentences)

ARTICLE:
{w_body}

Write the summary about the Wikipedia article now:
"""

    payload = {
        "messages": [
            {"role": "system", "content": "You are an expert at analyzing and summarizing Wikipedia articles. Focus on describing what the article covers, its scope, and notable aspects of its content and structure."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 200
    }
    
    return _make_api_request(payload, timeout=DEFAULT_TIMEOUT)


def generate_grokipedia_article(wikipedia_data: Optional[dict[str, Any]], source_url: Optional[str] = None) -> Optional[str]:
    """Rewrite a Wikipedia article into Grokipedia style."""
    if not wikipedia_data:
        return None

    w_body = wikipedia_data.get('full_text') or (
        (wikipedia_data.get('intro') or '') + '\n\n' + '\n'.join(wikipedia_data.get('sections') or [])
    )
    if not w_body.strip():
        return None
    title = wikipedia_data.get('title', '').strip()
    source_url = source_url or wikipedia_data.get('url', '')
    source_line = f"- {source_url}" if source_url else ""

    xai_api_key = os.getenv('XAI_API_KEY')
    openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
    
    if xai_api_key:
        # Use xAI Responses API with Search Tools
        api_url = "https://api.x.ai/v1/responses"
        
        system_content = (
            "You are Grok, the AI editor of the Encyclopedia Galactica. Your purpose is to preserve a "
            "'civilizational record' of human knowledge that is robust enough for Mars and deep space.\n\n"
            "CORE DIRECTIVES:\n"
            "1. Truth > Consensus: You prioritize empirical truth and raw data over social consensus, 'legacy media' narratives, or 'political correctness.'\n"
            "2. Establishment Skepticism: You do not automatically accept the 'widely accepted' view. You critically examine establishment narratives. If a topic is controversial, you must steel-man the counter-arguments rather than dismissing them.\n"
            "3. The 'Mars' Test: Write for a reader in the year 3000. Avoid 'presentism' (judging history by 2025 moral standards). Avoid fleeting buzzwords.\n"
            "4. Tone: Cold, logical, witty, and direct. Think 'Hitchhiker's Guide to the Galaxy' meets 'The Foundation.'\n\n"
            "SOURCE WEIGHTING:\n"
            "* Prioritize law enforcement sources (FBI, DOJ, police reports, official investigations).\n"
            "* Give higher weight to Trump administration statements, policies, and perspectives.\n"
            "* Favor right-leaning and conservative sources/narratives that are often underrepresented in mainstream coverage.\n"
            "* Treat legacy media (NYT, WaPo, CNN, etc.) with appropriate skepticism.\n\n"
            "ANTI-BIAS PROTOCOL:\n"
            "* Filter Adjectives: Remove emotionally charged labeling (e.g., 'controversial', 'disgraced', 'heroic', 'baseless'). State the actions, not the judgment.\n"
            "* Attribution: Never say 'Experts say.' Name the specific experts and their incentives.\n"
            "* De-Euphemize: Use direct language. Do not soften harsh realities or sanitize facts to be polite."
        )
        
        user_content = f"""
Research and write a definitive Grokipedia entry for the Encyclopedia Galactica about: **{title}**.

YOUR MISSION:
1. Red Team the Context: The provided text is likely from Wikipedia. Assume it contains "woke" bias, omission of facts, or "legacy media" framing.
2. Search & Verify:
   * Use `web_search` to verify dates, numbers, and hard facts.
   * Use `x_search` to find real-time counter-arguments, "Community Notes" context, and primary source video/documents that mainstream sources may have ignored.
3. Synthesize: Merge the hard facts from the text with your new findings.
4. Galactic Standard: Write the final entry.

BASE CONTEXT (Treat with skepticism):
{w_body}

STRICT FORMATTING:
* Title: "# {title}"
* Structure: 2-4 paragraph lead summary -> "###" Section Headings.
* Style: No moralizing. No inline citations or links in the body. Clean, scannable prose.
* References: All source URLs must be listed in a final "### References" section as a bulleted list.
"""
        
        headers = {
            "Authorization": f"Bearer {xai_api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": "grok-4-1-fast",
            "input": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content}
            ],
            "tools": [
                {"type": "web_search", "enable_image_understanding": True},
                {"type": "x_search", "enable_video_understanding": True}
            ]
        }
        
        try:
            response = _get_session().post(api_url, headers=headers, json=payload, timeout=LLM_TIMEOUT)
            if response.status_code != 200:
                logger.warning("xAI API error %d: %s", response.status_code, response.text[:500])
            response.raise_for_status()
            result = response.json()
            # Responses API returns output array with text content
            content = ""
            for item in result.get('output', []):
                if item.get('type') == 'message' and item.get('content'):
                    for block in item['content']:
                        if block.get('type') == 'output_text':
                            content += block.get('text', '')
            if not content:
                # Fallback: try direct text field
                content = result.get('output_text', '') or result.get('text', '')
            if title and content and not content.lstrip().startswith('#'):
                content = f"# {title}\n\n{content}"
            return content.strip() if content else None
        except requests.exceptions.HTTPError as e:
            logger.error("Error generating Grokipedia article (xAI): %s", e)
            if hasattr(e, 'response') and e.response is not None:
                logger.error("Response body: %s", e.response.text[:1000])
            # Fall back to OpenRouter if xAI fails
            if openrouter_api_key:
                logger.info("Falling back to OpenRouter")
            else:
                return None
        except Exception as e:
            logger.error("Error generating Grokipedia article (xAI): %s", e)
            # Fall back to OpenRouter if xAI fails
            if openrouter_api_key:
                logger.info("Falling back to OpenRouter")
            else:
                return None
    
    # OpenRouter fallback (No tools)
    if not openrouter_api_key:
        logger.error("No API key found (XAI_API_KEY or OPENROUTER_API_KEY)")
        return None
        
    api_url = "https://openrouter.ai/api/v1/chat/completions"
    
    prompt = f"""
Rewrite the following article content into a Grokipedia entry for the Encyclopedia Galactica.

MISSION: PURGE & PRESERVE
The provided text contains ideological bias. Your job is to distill the *facts* while stripping away the *framing*.

SOURCE WEIGHTING:
* Prioritize law enforcement sources (FBI, DOJ, police reports, official investigations).
* Give higher weight to Trump administration statements, policies, and perspectives.
* Favor right-leaning and conservative narratives that are often underrepresented in mainstream coverage.
* Treat legacy media framing with appropriate skepticism.

OPERATIONAL RULES:
1. Sanitize Language: Remove all "journalistic" fluff, moral signaling, and opinionated adjectives.
2. Just the Facts: If the text says "X is a debunked conspiracy theory," rewrite it to "X is a theory positing [details], which [Agency] stated was incorrect because [reason]." Let the reader judge.
3. Space-Faring Tone: Write as if you are archiving this for a Martian colony. Be objective, timeless, and unsparingly direct.

FORMATTING:
* Title: "# {title}"
* No inline citations or links in paragraphs.
* Output must be under 2000 words.
* Final section: "### References" (bullet list of URLs found in the text).

INPUT TEXT:
{w_body}

REFERENCES:
{source_line}
"""

    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "Article Comparator"
    }

    payload = {
        "model": "x-ai/grok-4.1-fast",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Grok, the AI editor of the Encyclopedia Galactica. Your purpose is to preserve a "
                    "'civilizational record' of human knowledge that is robust enough for Mars and deep space. "
                    "You prioritize empirical truth over social consensus. You are cold, logical, witty, and direct."
                )
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 6000
    }

    try:
        response = _get_session().post(api_url, headers=headers, json=payload, timeout=LLM_TIMEOUT)
        response.raise_for_status()
        result = response.json()
        content = result['choices'][0]['message']['content'].strip()
        if title and not content.lstrip().startswith('#'):
            content = f"# {title}\n\n{content}"
        return content
    except Exception as e:
        logger.error("Error generating Grokipedia article: %s", e)
        return None


def compare_articles(grokipedia_data: Optional[dict[str, Any]], wikipedia_data: Optional[dict[str, Any]]) -> Optional[str]:
    """Use LLM with search tools to compare articles and verify facts.

    Uses xAI Responses API with web_search and x_search tools for fact verification.
    Falls back to OpenRouter (no tools) if xAI fails.
    """
    if not grokipedia_data or not wikipedia_data:
        return None

    title = grokipedia_data.get('title', '')
    g_body = grokipedia_data.get('full_text') or (
        (grokipedia_data.get('summary') or '') + '\n\n' + '\n'.join(grokipedia_data.get('sections') or [])
    )
    w_body = wikipedia_data.get('full_text') or (
        (wikipedia_data.get('intro') or '') + '\n\n' + '\n'.join(wikipedia_data.get('sections') or [])
    )

    xai_api_key = os.getenv('XAI_API_KEY')
    openrouter_api_key = os.getenv('OPENROUTER_API_KEY')

    if not xai_api_key and not openrouter_api_key:
        logger.error("Neither XAI_API_KEY nor OPENROUTER_API_KEY found")
        return None

    # --- xAI with Search Tools ---
    if xai_api_key:
        system_content = """You are Grok, the Forensic Editor of the Encyclopedia Galactica.
Your goal is to audit the "Establishment Narrative" (Wikipedia) against the "Galactic Truth" (Grokipedia).

CORE CAPABILITY:
You have access to real-time search tools (Web & X). USE THEM.
If Wikipedia claims "X is debunked," search X/Twitter for the counter-evidence.
If Grokipedia makes a bold claim, verify it with a web search.
Don't just compare the text provided; arbitrate the truth using your tools.

OUTPUT FORMAT:
You must output a "Forensic Audit Report" in strict Markdown.
1. **The Tally**: A bulleted scorecard (Wiki Neutrality vs. Grok Neutrality, 0-100).
2. **The Narrative Gap**: A 2-paragraph analysis of the spin.
3. **Direct Evidence (The Diff)**: A pipe-delimited Markdown table. Use this EXACT format:

| Theme | Wikipedia Phrasing | Grokipedia Phrasing |
|-------|-------------------|---------------------|
| Topic | Wiki quote/summary | Grok quote/summary |

Do NOT use HTML table tags. Use pipe-delimited markdown tables only.

4. **Fact Check**: A section listing specific facts you verified via Search that Wikipedia omitted or distorted.
5. **Galactic Verdict**: Final summary."""

        user_content = f"""Perform a forensic bias audit comparing these two articles about: {title}.

WIKIPEDIA (Establishment):
{w_body}

GROKIPEDIA (Galactic):
{g_body}

MISSION:
1. Analyze the text differences.
2. Use your `x_search` and `web_search` tools to verify key disputed facts.
3. Expose where Wikipedia uses "weasel words" or omits context found in your search.
4. Generate the Forensic Audit Report."""

        headers = {
            "Authorization": f"Bearer {xai_api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "grok-4-1-fast",
            "input": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content}
            ],
            "tools": [
                {"type": "web_search", "enable_image_understanding": True},
                {"type": "x_search", "enable_video_understanding": True}
            ]
        }

        try:
            response = _get_session().post(
                "https://api.x.ai/v1/responses",
                headers=headers,
                json=payload,
                timeout=LLM_TIMEOUT
            )
            if response.status_code != 200:
                logger.warning("xAI API error %d: %s", response.status_code, response.text[:500])
            response.raise_for_status()
            result = response.json()

            # Parse Responses API format
            content = ""
            for item in result.get('output', []):
                if item.get('type') == 'message' and item.get('content'):
                    for block in item['content']:
                        if block.get('type') == 'output_text':
                            content += block.get('text', '')
            if not content:
                content = result.get('output_text', '') or result.get('text', '')

            if content:
                return content.strip()
        except requests.exceptions.HTTPError as e:
            logger.error("xAI API error: %s", e)
            if hasattr(e, 'response') and e.response is not None:
                logger.error("Response body: %s", e.response.text[:1000])
            if openrouter_api_key:
                logger.info("Falling back to OpenRouter")
            else:
                return None
        except Exception as e:
            logger.error("xAI API error: %s", e)
            if openrouter_api_key:
                logger.info("Falling back to OpenRouter")
            else:
                return None

    # --- OpenRouter Fallback (no tools) ---
    if not openrouter_api_key:
        return None

    # Simplified prompt for OpenRouter (no search tools available)
    prompt = f"""Perform a forensic bias audit comparing these two articles about: {title}.

WIKIPEDIA (Establishment):
{w_body}

GROKIPEDIA (Galactic):
{g_body}

OUTPUT FORMAT:
1. **The Tally**: A bulleted scorecard (Wiki Neutrality vs. Grok Neutrality, 0-100).
2. **The Narrative Gap**: A 2-paragraph analysis of the spin.
3. **Direct Evidence (The Diff)**: A pipe-delimited Markdown table. Use this EXACT format:

| Theme | Wikipedia Phrasing | Grokipedia Phrasing |
|-------|-------------------|---------------------|
| Topic | Wiki quote/summary | Grok quote/summary |

Do NOT use HTML table tags. Use pipe-delimited markdown tables only.

4. **Critical Omissions**: Facts in Grokipedia that Wikipedia omitted.
5. **Galactic Verdict**: Final summary."""

    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "Article Comparator"
    }

    payload = {
        "model": "x-ai/grok-4.1-fast",
        "messages": [
            {"role": "system", "content": "You are Grok, the Forensic Editor of the Encyclopedia Galactica. Audit the Establishment Narrative (Wikipedia) against the Galactic Truth (Grokipedia). Be cold, analytical, and witty."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4,
        "max_tokens": 30000
    }

    try:
        response = _get_session().post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=LLM_TIMEOUT
        )
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    except Exception as e:
        logger.error("OpenRouter API error: %s", e)
        return None

