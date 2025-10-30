"""Article fetching services for Wikipedia and Grokipedia"""
import requests
from urllib.parse import urlparse
from app.utils.url_parser import extract_article_title
from app.utils.sdk_manager import get_sdk_client, is_sdk_available, ArticleNotFound, RequestError


def scrape_wikipedia(url):
    """Fetch content from Wikipedia using official APIs for reliability.

    Returns dict with title, intro, sections (list[str]), url, and full_text (entire plaintext article).
    """
    try:
        headers = {
            'User-Agent': 'Grokipedia-Comparator/1.0 (contact: example@example.com)'
        }

        # Extract the page title from URL
        title = extract_article_title(url)
        if not title:
            return None

        # 1) Fetch summary via REST API
        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
        summary_resp = requests.get(summary_url, headers=headers, timeout=30)
        if summary_resp.status_code == 404:
            return None
        summary_resp.raise_for_status()
        summary_data = summary_resp.json()
        title_text = summary_data.get('title') or title.replace('_', ' ')
        intro_text = summary_data.get('extract', '').strip()

        # 2) Fetch sections via Action API
        sections_url = (
            "https://en.wikipedia.org/w/api.php?action=parse&prop=sections&format=json&page="
            + title
        )
        sections_resp = requests.get(sections_url, headers=headers, timeout=30)
        sections = []
        if sections_resp.ok:
            try:
                sections_json = sections_resp.json()
                for s in sections_json.get('parse', {}).get('sections', [])[:10]:
                    line = s.get('line')
                    if line and line.lower() not in {"references", "external links", "see also", "notes"}:
                        sections.append(line)
            except Exception:
                pass

        # 3) Fetch full plaintext extract for comparison context
        extract_url = (
            "https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext=1&redirects=1&format=json&titles="
            + title
        )
        full_text = ''
        extract_resp = requests.get(extract_url, headers=headers, timeout=30)
        if extract_resp.ok:
            try:
                q = extract_resp.json()
                pages = q.get('query', {}).get('pages', {})
                if pages:
                    first = next(iter(pages.values()))
                    full_text = (first.get('extract') or '').strip()
            except Exception:
                pass

        return {
            'title': title_text,
            'intro': intro_text,
            'sections': sections[:5],
            'url': url,
            'full_text': full_text
        }
    except Exception as e:
        print(f"Error fetching Wikipedia via API: {e}")
        return None


def fetch_grokipedia_article(url):
    """Fetch Grokipedia article using the SDK.

    Uses the Grokipedia SDK to scrape articles from grokipedia.com.
    Automatically handles slug resolution and fuzzy matching.
    """
    if not is_sdk_available():
        print("Grokipedia SDK not available")
        return None

    try:
        # Extract slug from URL (format: https://grokipedia.com/page/Article_Name)
        parsed = urlparse(url)
        slug = parsed.path.split('/page/')[-1].strip('/')
        if not slug:
            return None

        # Create a new client for article fetching (need fresh connection)
        # Note: Search uses cached client, but article fetching needs new instance
        client = get_sdk_client()
        try:
            # Try to get full article first
            article = client.get_article(slug)
            
            # Convert SDK Article model to dict format expected by frontend
            return {
                'title': article.title,
                'summary': article.summary,
                'sections': article.table_of_contents[:5],  # Limit to 5 sections
                'url': str(article.url),  # Convert HttpUrl to string for JSON serialization
                'full_text': article.full_content
            }
        except ArticleNotFound:
            # If article not found, try slug search as fallback
            resolved_slug = client.find_slug(slug)
            if resolved_slug and resolved_slug != slug:
                try:
                    article = client.get_article(resolved_slug)
                    return {
                        'title': article.title,
                        'summary': article.summary,
                        'sections': article.table_of_contents[:5],
                        'url': str(article.url),
                        'full_text': article.full_content
                    }
                except (ArticleNotFound, RequestError):
                    print(f"Could not fetch article even after resolving slug: {resolved_slug}")
                    return None
            else:
                print(f"Article not found: {slug}")
                return None
        except RequestError as e:
            print(f"Error fetching Grokipedia article: {e}")
            return None
        finally:
            client.close()
    except Exception as e:
        print(f"Error initializing SDK or fetching article: {e}")
        return None

