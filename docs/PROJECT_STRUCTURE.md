# Article Comparator - Project Structure

## Overview

This Flask application compares articles from Grokipedia and Wikipedia, analyzing differences in content, tone, and perspective using AI-powered analysis. The application features a modular architecture for both backend and frontend code.

## Project Structure

```
chatbot_app/
├── app/                          # Main application package
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Application configuration
│   ├── routes/                  # Route handlers
│   │   ├── __init__.py
│   │   └── main.py             # Main routes (index, compare, search)
│   ├── services/                # Business logic services
│   │   ├── __init__.py
│   │   ├── article_fetcher.py   # Wikipedia & Grokipedia fetching
│   │   └── comparison_service.py # LLM comparison logic
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       ├── url_parser.py        # URL parsing & conversion
│       └── sdk_manager.py      # SDK client management
│
├── static/                      # Frontend assets
│   ├── css/                     # Modular CSS files
│   │   ├── base.css            # Variables, reset, base styles
│   │   ├── layout.css          # Layout components
│   │   ├── components.css      # Reusable components
│   │   └── animations.css      # Animations & keyframes
│   └── js/                      # Modular JavaScript (ES6 modules)
│       ├── api.js              # API calls
│       ├── ui.js               # DOM manipulation
│       ├── search.js           # Search/autocomplete
│       ├── markdown.js         # Markdown rendering
│       ├── utils.js            # Utility functions
│       └── main.js             # Main initialization
│
├── templates/                   # HTML templates
│   └── index.html              # Main application page
│
├── scripts/                     # Utility scripts
│   ├── map.py                  # Sitemap downloader
│   ├── link_index.py          # Local slug index utility
│   └── test_grokipedia.py     # SDK testing script
│
├── docs/                        # Documentation
│   ├── README.md               # Full documentation
│   ├── PROJECT_STRUCTURE.md    # This file
│   ├── USAGE.md                # Usage instructions
│   └── PROJECT_SUMMARY.md      # Project summary
│
├── grokipedia-sdk/             # Grokipedia SDK package (separate)
│   └── ...                    # SDK files
│
├── run.py                      # Application entry point
├── requirements.txt            # Python dependencies
├── README.md                   # Main documentation
└── .env                        # Environment variables (not in repo)
```

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   Create a `.env` file:
   ```env
   OPENROUTER_API_KEY=your-openrouter-key-here
   ```

3. **Run the Application**
   ```bash
   python run.py
   ```

   The application will start on `http://localhost:5000`

## Key Components

### Backend (`app/`)

#### Application (`app/__init__.py`)
- Creates and configures the Flask application
- Registers blueprints
- Initializes SDK

#### Configuration (`app/config.py`)
- Centralized configuration (API keys, paths, etc.)
- Environment variable management
- SDK settings

#### Routes (`app/routes/main.py`)
HTTP endpoints:
- `GET /`: Main page
- `GET /search`: Search for Grokipedia articles with autocomplete
- `POST /compare`: Compare articles from both sources

#### Services (`app/services/`)

**`article_fetcher.py`**: Fetches articles from:
- Wikipedia: Uses official REST API and Action API
- Grokipedia: Uses SDK with automatic slug resolution

**`comparison_service.py`**: AI-powered comparison using:
- OpenRouter API integration
- Grok-4-Fast model
- Structured prompt engineering for bias analysis

#### Utilities (`app/utils/`)

**`url_parser.py`**: URL handling:
- Detects source (Grokipedia/Wikipedia)
- Extracts article titles/slugs
- Converts between sources
- Handles URL encoding and special characters

**`sdk_manager.py`**: SDK management:
- Client initialization and caching
- Availability checking
- Resource cleanup

### Frontend (`static/`)

#### CSS Modules (`static/css/`)

**`base.css`**: Foundation
- CSS variables (colors, spacing, etc.)
- Reset styles
- Base typography
- Scrollbar styling

**`layout.css`**: Layout structure
- Container components
- Grid layouts
- Responsive breakpoints
- View states

**`components.css`**: UI components
- Buttons, inputs, badges
- Article boxes
- Comparison box
- Search suggestions
- Loading states
- Error messages

**`animations.css`**: Visual effects
- Keyframe animations
- Background effects (starry sky)
- Transitions
- Spinners

#### JavaScript Modules (`static/js/`)

**`api.js`**: API communication
- `searchArticles()` - Search endpoint
- `compareArticles()` - Comparison endpoint
- Error handling

**`ui.js`**: DOM manipulation
- Loading state management
- Error display
- Article content rendering
- Comparison display
- View state management

**`search.js`**: Search functionality
- Autocomplete initialization
- Debounced search
- Keyboard navigation (arrow keys, escape)
- Suggestion highlighting
- Click-outside handling

**`markdown.js`**: Markdown rendering
- Custom markdown parser
- Source badge rendering (W/G labels)
- Quote formatting
- List handling

**`utils.js`**: Utility functions
- HTML escaping (XSS prevention)
- Clipboard operations
- Article text formatting

**`main.js`**: Application initialization
- Event listener setup
- Module coordination
- State management
- Entry point

### Scripts (`scripts/`)

- **`map.py`**: Downloads sitemap data from Grokipedia
- **`link_index.py`**: Local slug index utilities
- **`test_grokipedia.py`**: Tests SDK functionality

## Architecture Principles

### Backend Architecture

The application follows a clean separation of concerns:

1. **Routes** handle HTTP requests and responses
2. **Services** contain business logic (article fetching, comparison)
3. **Utils** provide reusable helper functions
4. **Config** centralizes all configuration

This structure makes the codebase:
- **Modular**: Each component has a clear responsibility
- **Testable**: Components can be tested independently
- **Maintainable**: Easy to find and modify specific functionality
- **Scalable**: Easy to add new features or routes

### Frontend Architecture

The frontend uses ES6 modules for:

1. **Separation of Concerns**: Each module handles one aspect
   - API calls separate from UI
   - Search logic separate from rendering
   - Utilities reusable across modules

2. **Maintainability**: 
   - Easy to locate and fix bugs
   - Changes isolated to specific modules
   - Clear dependencies

3. **Performance**:
   - Smaller, focused files
   - Better caching
   - Lazy loading capabilities

4. **Developer Experience**:
   - Clear file organization
   - Easy to understand code flow
   - Simple to extend

## File Organization Benefits

### Easy Debugging
- CSS issues? Check `static/css/`
- Search not working? Check `static/js/search.js`
- API errors? Check `static/js/api.js`
- Backend routes? Check `app/routes/`

### Easy Maintenance
- Want to change styles? Edit CSS modules
- Need to add a feature? Create new module or extend existing
- Fix a bug? Go directly to the relevant module

### Easy Testing
- Test modules independently
- Mock dependencies easily
- Clear test boundaries

### Easy Collaboration
- Multiple developers can work on different modules
- Clear ownership of files
- Reduced merge conflicts

## Development Workflow

### Adding a New Feature

1. **Backend**: Add route in `app/routes/`, service in `app/services/`
2. **Frontend**: Add API call in `api.js`, UI in `ui.js`, wire up in `main.js`
3. **Styling**: Add styles to appropriate CSS module

### Fixing a Bug

1. Identify the area (frontend/backend, which module)
2. Navigate to the relevant file
3. Make focused changes
4. Test the specific functionality

### Extending Functionality

1. Identify which module handles similar functionality
2. Extend that module or create a new one
3. Update imports in dependent modules
4. Test integration

## Migrating from Old Structure

If you had the old `app.py` file, it has been renamed to `app.py.old`. The new structure maintains all functionality but is better organized.

**Changes:**
- Backend: Split into `app/` package structure
- Frontend: Split inline CSS/JS into modular files
- Entry point: Now `run.py` instead of `app.py`

**To use the new structure:**
- Run `python run.py` instead of `python app.py`
- All functionality remains the same
- Better organization for future development
