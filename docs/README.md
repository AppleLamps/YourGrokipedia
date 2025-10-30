# Article Comparator - Full Documentation

A web service that compares articles from Grokipedia and Wikipedia, analyzing differences in content, tone, and perspective using AI-powered analysis.

## Features

- 📚 **Wikipedia Scraping**: Automatically extracts content from Wikipedia articles via official APIs
- 🔷 **Grokipedia Integration**: Uses the Grokipedia SDK to fetch articles directly from grokipedia.com
- 🤖 **AI-Powered Comparison**: Uses Grok-4-Fast via OpenRouter to analyze and explain differences
- 🎨 **Modern UI**: Clean, modular frontend with search autocomplete and responsive design
- 🔍 **Smart Search**: Real-time article search with autocomplete suggestions
- 📋 **Copy Features**: Easy copying of comparison results and article content

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
# OpenRouter API Key
OPENROUTER_API_KEY=your-openrouter-key-here
```

**Note:** Grokipedia SDK integration does not require an API key - it scrapes content directly from grokipedia.com.

### 3. Run the Application

```bash
python run.py
```

The application will start on `http://localhost:5000`

## Usage

### Basic Usage

1. **Open the application** in your browser at `http://localhost:5000`
2. **Enter an article URL or name**:
   - Use the search bar for autocomplete suggestions as you type
   - Or paste a URL directly:
     - Grokipedia: `https://grokipedia.com/page/Article_Name`
     - Wikipedia: `https://en.wikipedia.org/wiki/Article_Name`
     - Just the article name: `Comcast` (will resolve automatically)
3. **Click "Compare Articles"** or press Enter
4. **View the results**:
   - Side-by-side comparison of article content
   - AI-generated analysis of bias and differences
   - Copy buttons for easy sharing

### Search Features

- **Autocomplete**: Type at least 2 characters to see suggestions
- **Keyboard Navigation**: Use arrow keys to navigate suggestions, Enter to select
- **Smart Matching**: Results are ranked by relevance (exact matches first)

### Comparison Features

- **Copy Comparison**: Copy the full AI analysis
- **Copy Articles**: Copy individual article content
- **Raw View**: Toggle between rendered and raw markdown

## How It Works

### 1. URL Detection & Conversion
- Detects whether the URL is from Grokipedia or Wikipedia
- Extracts the article title/slug from the URL
- Automatically converts to the corresponding URL in the other source
- Handles URL encoding and special characters
- Supports fuzzy matching for article names

### 2. Wikipedia Scraping
- Uses Wikipedia REST API (`/api/rest_v1/page/summary/`) for summaries
- Uses Action API (`/w/api.php`) for sections and full text
- Retrieves article summaries, sections, and full text content
- Handles redirects and URL variations

### 3. Grokipedia SDK Integration
- Uses the Grokipedia SDK to scrape articles directly from grokipedia.com
- Automatic slug resolution and fuzzy matching for article lookup
- Retrieves structured article data including title, summary, sections, and full content
- Built-in caching for improved performance
- Client reuse for search operations

### 4. AI Comparison
- Sends both articles to Grok-4-Fast via OpenRouter
- Analyzes content differences
- Identifies bias indicators in Wikipedia
- Shows how Grokipedia removes bias
- Provides section-level analysis
- Returns structured markdown output

## Example Comparison

**Input (just one URL):**
- Either: `https://grokipedia.com/page/Joe_Biden`
- Or: `https://en.wikipedia.org/wiki/Joe_Biden`
- Or: `Joe Biden` (will search and resolve)

**Output:**
- Automatically fetches the corresponding article from the other source
- Side-by-side article display
- AI analysis of:
  - Bias indicators found in Wikipedia
  - How Grokipedia removes each bias
  - Section-level comparisons
  - Residual issues and fixes
  - Overall conclusion

## API Endpoints

### `GET /`
Serves the main HTML page.

### `GET /search?q=<query>&limit=<limit>`
Search for Grokipedia articles with autocomplete.

**Query Parameters:**
- `q` (required): Search query (minimum 2 characters)
- `limit` (optional): Maximum number of results (default: 10)

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

**Features:**
- Smart ranking: exact matches prioritized
- Fuzzy matching fallback
- Word-based matching
- Position-based scoring

### `POST /compare`
Compare articles from Grokipedia and Wikipedia.

**Request Body:**
```json
{
  "article_url": "https://grokipedia.com/page/Article_Name"
}
```

OR

```json
{
  "article_url": "https://en.wikipedia.org/wiki/Article_Name"
}
```

OR

```json
{
  "article_url": "Article Name"
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
    "full_text": "Full article content..."
  },
  "grokipedia_url": "https://grokipedia.com/page/Article_Name",
  "wikipedia": {
    "title": "Article Title",
    "intro": "Article introduction...",
    "sections": ["Section 1", "Section 2"],
    "url": "https://en.wikipedia.org/wiki/Article_Name",
    "full_text": "Full article content..."
  },
  "wikipedia_url": "https://en.wikipedia.org/wiki/Article_Name",
  "comparison": "AI-generated comparison analysis in markdown format..."
}
```

**Error Response:**
```json
{
  "error": "Error message here"
}
```

## Project Structure

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed architecture information.

### Backend Structure
```
app/
├── routes/       # HTTP endpoints
├── services/     # Business logic
└── utils/        # Utility functions
```

### Frontend Structure
```
static/
├── css/          # Modular CSS (base, layout, components, animations)
└── js/           # ES6 modules (api, ui, search, markdown, utils, main)
```

## Requirements

- Python 3.8+
- Flask 3.0.0
- requests 2.31.0
- python-dotenv 1.0.0
- beautifulsoup4 4.12.2
- httpx >= 0.25.0
- pydantic >= 2.0.0
- rapidfuzz >= 3.0.0
- lxml >= 4.9.0

See `requirements.txt` for exact versions.

## Development

### Running in Development Mode

```bash
python run.py
```

Debug mode is enabled by default. The app runs on `http://localhost:5000`.

### Modifying the Frontend

**CSS**: Edit files in `static/css/`
- `base.css` - Variables and base styles
- `layout.css` - Layout components
- `components.css` - UI components
- `animations.css` - Animations

**JavaScript**: Edit modules in `static/js/`
- `api.js` - API calls
- `ui.js` - UI manipulation
- `search.js` - Search functionality
- `markdown.js` - Markdown rendering
- `utils.js` - Utilities
- `main.js` - Initialization

**Template**: Edit `templates/index.html`

### Modifying the Backend

**Routes**: Add endpoints in `app/routes/main.py`

**Services**: Add business logic in `app/services/`
- `article_fetcher.py` - Article fetching
- `comparison_service.py` - Comparison logic

**Utils**: Add helpers in `app/utils/`
- `url_parser.py` - URL handling
- `sdk_manager.py` - SDK management

## Troubleshooting

### SDK Not Available

If you see "SDK not available":
1. Ensure dependencies are installed: `pip install -r requirements.txt`
2. Try installing SDK locally: `pip install -e grokipedia-sdk/`
3. Check that the SDK path is correct in `app/config.py`

### API Key Issues

If comparison fails:
1. Check `.env` file exists and contains `OPENROUTER_API_KEY`
2. Verify the API key is valid
3. Check network connectivity

### Search Not Working

1. Check browser console for errors
2. Verify SDK is initialized (check server logs)
3. Ensure search endpoint is accessible

## Notes

- The app automatically detects whether you entered a Grokipedia or Wikipedia URL
- You only need to provide ONE URL - it finds the corresponding article automatically
- Article names can be resolved using fuzzy matching
- Full article text is sent to the AI for comprehensive comparison
- Results are cached in the browser for faster subsequent loads

## License

This project is provided as-is for educational and development purposes.
