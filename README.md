# Article Comparator

A web service that compares articles from Grokipedia and Wikipedia, analyzing differences in content, tone, and perspective using AI-powered analysis.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment (create .env file)
echo "OPENROUTER_API_KEY=your-key-here" > .env

# Run the application
python run.py
```

The application will start on `http://localhost:5000`

## Features

- 📚 **Wikipedia Scraping**: Automatically extracts content from Wikipedia articles via official APIs
- 🔷 **Grokipedia Integration**: Uses the Grokipedia SDK to fetch articles directly from grokipedia.com
- 🤖 **AI-Powered Comparison**: Uses Grok-4-Fast via OpenRouter to analyze and explain differences
- 🎨 **Modern UI**: Clean, modular frontend with search autocomplete and responsive design
- 🔍 **Smart Search**: Real-time article search with autocomplete suggestions
- 📋 **Copy Features**: Easy copying of comparison results and article content

## Project Structure

```
chatbot_app/
├── app/                      # Flask application package
│   ├── __init__.py          # App factory
│   ├── config.py            # Configuration
│   ├── routes/              # HTTP endpoints
│   │   └── main.py         # Main routes (index, search, compare)
│   ├── services/            # Business logic
│   │   ├── article_fetcher.py    # Wikipedia & Grokipedia fetching
│   │   └── comparison_service.py # LLM comparison logic
│   └── utils/               # Utility functions
│       ├── url_parser.py    # URL parsing & conversion
│       └── sdk_manager.py   # SDK client management
│
├── static/                  # Frontend assets
│   ├── css/                # Modular CSS files
│   │   ├── base.css        # Variables, reset, base styles
│   │   ├── layout.css      # Layout components
│   │   ├── components.css  # Reusable components
│   │   └── animations.css  # Animations & keyframes
│   └── js/                 # Modular JavaScript (ES6 modules)
│       ├── api.js          # API calls
│       ├── ui.js           # DOM manipulation
│       ├── search.js       # Search/autocomplete
│       ├── markdown.js     # Markdown rendering
│       ├── utils.js        # Utility functions
│       └── main.js         # Main initialization
│
├── templates/              # HTML templates
│   └── index.html          # Main page
│
├── scripts/                # Utility scripts
│   ├── map.py             # Sitemap downloader
│   ├── link_index.py      # Local slug index
│   └── test_grokipedia.py # SDK testing
│
├── docs/                   # Documentation
│   ├── README.md          # Full documentation
│   ├── PROJECT_STRUCTURE.md # Architecture details
│   ├── USAGE.md           # Usage guide
│   └── PROJECT_SUMMARY.md # Project summary
│
├── grokipedia-sdk/        # Grokipedia SDK package
├── run.py                 # Application entry point
└── requirements.txt       # Python dependencies
```

## Architecture

### Backend (Flask)
- **Modular Structure**: Clean separation of routes, services, and utilities
- **Configuration**: Centralized config management
- **SDK Integration**: Smart client caching and initialization
- **Error Handling**: Graceful error handling throughout

### Frontend (Vanilla JavaScript + CSS)
- **Modular JavaScript**: ES6 modules organized by functionality
  - `api.js` - All API communication
  - `ui.js` - UI state management
  - `search.js` - Autocomplete functionality
  - `markdown.js` - Markdown rendering
  - `utils.js` - Helper functions
  - `main.js` - App initialization
- **Modular CSS**: Organized by purpose
  - `base.css` - Foundation styles
  - `layout.css` - Layout structure
  - `components.css` - UI components
  - `animations.css` - Animations

### Benefits of Modular Structure
- ✅ **Easy Debugging**: Find issues quickly by feature
- ✅ **Maintainable**: Change one feature without affecting others
- ✅ **Testable**: Modules can be tested independently
- ✅ **Scalable**: Easy to add new features
- ✅ **Performance**: Smaller, focused files load faster

## Usage

1. **Open the application** at `http://localhost:5000`
2. **Search or enter an article URL**:
   - Use the search bar for autocomplete suggestions
   - Or paste a URL directly:
     - Grokipedia: `https://grokipedia.com/page/Article_Name`
     - Wikipedia: `https://en.wikipedia.org/wiki/Article_Name`
3. **Click "Compare Articles"** or press Enter
4. **View the results**:
   - Side-by-side article comparison
   - AI-generated bias analysis
   - Copy buttons for easy sharing

## Development

### Running in Development Mode

```bash
python run.py
```

The app runs with debug mode enabled by default.

### Frontend Development

The frontend uses ES6 modules. To modify:
- **CSS**: Edit files in `static/css/`
- **JavaScript**: Edit modules in `static/js/`
- **Template**: Edit `templates/index.html`

### Backend Development

- **Routes**: Add new endpoints in `app/routes/`
- **Services**: Add business logic in `app/services/`
- **Utils**: Add helper functions in `app/utils/`

## API Endpoints

### `GET /`
Serves the main HTML page.

### `GET /search?q=<query>&limit=<limit>`
Search for Grokipedia articles.

**Query Parameters:**
- `q` (required): Search query
- `limit` (optional): Max results (default: 10)

**Response:**
```json
{
  "results": [
    {
      "slug": "Article_Name",
      "title": "Article Name",
      "url": "https://grokipedia.com/page/Article_Name"
    }
  ]
}
```

### `POST /compare`
Compare articles from Grokipedia and Wikipedia.

**Request:**
```json
{
  "article_url": "https://grokipedia.com/page/Article_Name"
}
```

**Response:**
```json
{
  "grokipedia": {
    "title": "Article Title",
    "summary": "Article summary...",
    "sections": ["Section 1", "Section 2"],
    "url": "https://grokipedia.com/page/Article_Name",
    "full_text": "..."
  },
  "wikipedia": {
    "title": "Article Title",
    "intro": "Article introduction...",
    "sections": ["Section 1", "Section 2"],
    "url": "https://en.wikipedia.org/wiki/Article_Name",
    "full_text": "..."
  },
  "comparison": "AI-generated comparison analysis...",
  "grokipedia_url": "https://grokipedia.com/page/Article_Name",
  "wikipedia_url": "https://en.wikipedia.org/wiki/Article_Name"
}
```

## Requirements

- Python 3.8+
- Flask 3.0.0
- requests
- python-dotenv
- beautifulsoup4
- httpx
- pydantic
- rapidfuzz

See `requirements.txt` for exact versions.

## Environment Variables

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your-openrouter-api-key-here
```

## Documentation

For detailed documentation, see the [docs](docs/) folder:

- **[README.md](docs/README.md)** - Comprehensive documentation
- **[PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)** - Architecture details
- **[USAGE.md](docs/USAGE.md)** - Usage instructions
- **[PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)** - Project summary

## License

This project is provided as-is for educational and development purposes.
