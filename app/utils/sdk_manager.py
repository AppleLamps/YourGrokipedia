"""SDK client management and initialization"""
import sys
from pathlib import Path

# SDK module-level storage
_sdk_available = False
_cached_client = None
Client = None
ArticleNotFound = Exception
RequestError = Exception


def initialize_sdk():
    """Initialize the Grokipedia SDK and set availability flag"""
    global _sdk_available, Client, ArticleNotFound, RequestError
    
    try:
        # First try importing as installed package
        from grokipedia_sdk import Client as SDKClient, ArticleNotFound as SDKArticleNotFound, RequestError as SDKRequestError
        _sdk_available = True
        Client = SDKClient
        ArticleNotFound = SDKArticleNotFound
        RequestError = SDKRequestError
        return True
    except ImportError:
        # If that fails, try importing from local folder
        try:
            sdk_path = Path(__file__).parent.parent.parent / "grokipedia-sdk"
            if sdk_path.exists() and str(sdk_path) not in sys.path:
                sys.path.insert(0, str(sdk_path))
            from grokipedia_sdk import Client as SDKClient, ArticleNotFound as SDKArticleNotFound, RequestError as SDKRequestError
            _sdk_available = True
            Client = SDKClient
            ArticleNotFound = SDKArticleNotFound
            RequestError = SDKRequestError
            return True
        except ImportError as e:
            print(f"Warning: Could not import Grokipedia SDK: {e}")
            print("Please ensure dependencies are installed: pip install -r requirements.txt")
            print("Or install the SDK package: pip install -e grokipedia-sdk/")
            _sdk_available = False
            return False


def is_sdk_available():
    """Check if SDK is available"""
    return _sdk_available


def get_cached_client():
    """Get or create a cached SDK client instance for reuse"""
    global _cached_client
    if _cached_client is None and _sdk_available:
        print("Initializing Grokipedia SDK client (loading article index)...")
        _cached_client = Client()
        print("SDK client ready!")
    return _cached_client


def get_sdk_client():
    """Get a new SDK client instance (for one-off operations)"""
    if not _sdk_available:
        raise RuntimeError("SDK not available")
    return Client()

