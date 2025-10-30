"""URL parsing and conversion utilities"""
from urllib.parse import urlparse, unquote, parse_qs, quote
from app.config import Config


def detect_source(url):
    """Detect if URL is from Grokipedia or Wikipedia (handles mobile and subdomains)."""
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        host = url.lower()

    if host.endswith('grokipedia.com'):
        return 'grokipedia'
    if host.endswith('wikipedia.org') or host.endswith('m.wikipedia.org'):
        return 'wikipedia'
    return None


def extract_article_title(url):
    """Extract article title/slug from Grokipedia or Wikipedia URL.

    Handles:
    - Grokipedia: https://grokipedia.com/page/Title
    - Wikipedia desktop: https://en.wikipedia.org/wiki/Title
    - Wikipedia mobile: https://en.m.wikipedia.org/wiki/Title
    - Wikipedia index: https://en.wikipedia.org/w/index.php?title=Title
    - Removes fragments and decodes percent-encoding.
    """
    parsed = urlparse(url)
    host = (parsed.netloc or '').lower()
    path = parsed.path or ''
    query = parsed.query or ''

    def normalize_slug(s: str) -> str:
        s = unquote(s)
        # Drop anchors/fragments that sometimes leak into slug
        s = s.split('#', 1)[0]
        # Replace spaces with underscores to match common slug convention
        s = s.replace(' ', '_')
        return s.strip('/')

    if host.endswith('grokipedia.com'):
        if '/page/' in path:
            return normalize_slug(path.split('/page/', 1)[-1])
        return None

    if host.endswith('wikipedia.org') or host.endswith('m.wikipedia.org'):
        if '/wiki/' in path:
            return normalize_slug(path.split('/wiki/', 1)[-1])
        # Handle index.php?title=Title pattern
        if 'title=' in query:
            qs = parse_qs(query)
            title = qs.get('title', [None])[0]
            return normalize_slug(title) if title else None
    return None


def resolve_local_slug_if_available(raw: str) -> str | None:
    """Try resolving a raw user string to a known Grokipedia slug using SDK's SlugIndex.

    Returns the best-matching slug or None if not found or SDK unavailable.
    """
    try:
        if not raw or not isinstance(raw, str):
            return None
        from app.utils.sdk_manager import get_sdk_client, is_sdk_available
        if not is_sdk_available():
            return None
        
        # Use SDK's built-in slug search
        client = get_sdk_client()
        try:
            resolved = client.find_slug(raw)
            return resolved
        finally:
            client.close()
    except Exception:
        return None


def convert_to_other_source(url):
    """Convert URL from one source to the other using the extracted canonical slug."""
    title = extract_article_title(url)
    if not title:
        return None

    host = (urlparse(url).netloc or '').lower()
    safe_title = quote(title, safe='-_')  # keep common separators

    if host.endswith('grokipedia.com'):
        return f"https://en.wikipedia.org/wiki/{safe_title}"
    if host.endswith('wikipedia.org') or host.endswith('m.wikipedia.org'):
        return f"https://grokipedia.com/page/{safe_title}"
    return None

