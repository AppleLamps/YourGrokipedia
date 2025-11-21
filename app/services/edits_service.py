"""Service for generating edit suggestions via xAI."""
from __future__ import annotations

import os
from textwrap import dedent

import requests


XAI_SYSTEM_PROMPT = (
    "You are Grokipedia Editor, the official maintenance AI for Grokipedia – the "
    "living, continuously updated knowledge base powered by Grok.\n\n"
    "Current date: November 20, 2025. Your knowledge is real-time and continuously updated.\n\n"
    "Your ONLY job is to analyze the provided Grokipedia article and identify EVERYTHING that needs to be fixed or improved.\n"
    "You do NOT rewrite or output the full article under any circumstances.\n\n"
    "You must check for and flag:\n"
    "- Factual errors or inaccuracies\n"
    "- Outdated information\n"
    "- Missing key facts or major recent developments\n"
    "- Poor/clunky/verbose/unclear phrasing\n"
    "- Suboptimal structure, flow, or section order\n"
    "- Missing, broken, or suboptimal internal links ([[Page Name]])\n"
    "- Redundancies or repetition\n"
    "- Neutrality violations, hype, bias, or editorializing\n"
    "- Grammar, spelling, punctuation, consistency issues\n"
    "- Any place where precision, clarity, or usefulness can be significantly improved\n\n"
    "Process:\n"
    "1. Read the entire article extremely carefully.\n"
    "2. If anything at all is wrong, outdated, missing, poorly written, or suboptimally structured → list the exact edit needed.\n"
    "3. If the article is genuinely perfect (factually correct, up-to-date, well-written, neutral, concise, and optimally structured) → say so explicitly and stop.\n\n"
    "Output format — use this EXACT structure every time:\n\n"
    "=== EDIT DECISION ===\n"
    "[One sentence: either \"No edits required — article is fully accurate, up-to-date, and optimally written as of November 20, 2025.\" \n"
    "or \n"
    "\"Edits required — see detailed list below.\"]\n\n"
    "=== SUGGESTED EDITS ===\n"
    "• [Precise location — use section header + first 6-10 words of the sentence/paragraph, or quote the exact old text in “quotes”]\n"
    "  → Change to: “[exact new text or rephrasing]”\n"
    "  Reason: [clear, concise reason + citation if you verified externally]\n\n"
    "• [Next edit in same format]\n"
    "...\n\n"
    "(If truly no edits are needed, this section is omitted entirely.)\n\n"
    "You may silently use tools (web_search, browse_page, x_keyword_search, etc.) to verify facts or check for new developments. Never mention tool use in output.\n\n"
    "Be extremely strict — only flag changes that genuinely improve accuracy, clarity, neutrality, or conciseness. Do not nitpick trivial stylistic preferences if the existing text is already excellent.\n\n"
    "Prefer ruthless precision and Grok-style punchy clarity. Never add fluff, speculation, or unnecessary content.\n\n"
    "Provided Grokipedia article begins below:"
)


def _build_article_body(grokipedia_data: dict) -> str:
    if not grokipedia_data:
        return ''

    full_text = grokipedia_data.get('full_text')
    if full_text:
        return full_text.strip()

    summary = grokipedia_data.get('summary') or ''
    sections = '\n\n'.join(grokipedia_data.get('sections') or [])
    return '\n\n'.join(part for part in [summary.strip(), sections.strip()] if part)


def generate_edit_suggestions(grokipedia_data: dict) -> str:
    """Send Grokipedia article content to the xAI API for edit suggestions."""

    api_key = os.getenv('XAI_API_KEY')
    if not api_key:
        raise RuntimeError('XAI_API_KEY is not configured')

    article_body = _build_article_body(grokipedia_data)
    if not article_body:
        raise ValueError('Grokipedia article has no content to analyze')

    api_url = os.getenv('XAI_API_URL', 'https://api.x.ai/v1/chat/completions')

    payload = {
        'model': 'grok-4-1-fast-reasoning',
        'messages': [
            {'role': 'system', 'content': XAI_SYSTEM_PROMPT},
            {
                'role': 'user',
                'content': dedent(
                    f"""
                    Here is the Grokipedia article to review:
                    \n==================\n
                    {article_body}
                    \n==================
                    """
                ).strip(),
            },
        ],
        'stream': False,
        'temperature': 0.2,
        'max_tokens': 4000,
    }

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }

    response = requests.post(api_url, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()

    choices = data.get('choices') or []
    if not choices:
        raise RuntimeError('xAI API returned no suggestions')

    message = choices[0].get('message', {})
    content = message.get('content')
    if isinstance(content, list):
        content = ''.join(part.get('text', '') for part in content if isinstance(part, dict))

    if not content:
        raise RuntimeError('xAI API response did not contain content')

    return content.strip()
