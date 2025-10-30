/**
 * Main Application Module - Initializes and coordinates all modules
 */

import { compareArticles } from './api.js';
import { 
    showLoading, 
    hideLoading,
    updateLoadingMessage,
    showError, 
    clearError, 
    showResultsView,
    displayArticle,
    displayComparison,
    setButtonDisabled
} from './ui.js';
import { initSearch, handleEnterKey } from './search.js';
import { copyToClipboard, buildArticleCopy } from './utils.js';
import { saveComparison } from './storage.js';
import { initSidebar, updateSidebarBadge } from './sidebar.js';
import { getComparisonById } from './storage.js';

// Global state
let lastGrokCopyText = '';
let lastWikiCopyText = '';
let currentComparisonData = null;

/**
 * Initialize the application
 */
export function init() {
    const articleInput = document.getElementById('article-url');
    const compareBtn = document.getElementById('compareBtn');
    const newSearchBtn = document.getElementById('newSearchBtn');
    const suggestionsContainer = document.getElementById('suggestions');
    const copyBtn = document.getElementById('copyBtn');
    const rawToggle = document.getElementById('rawToggle');
    const copyGrokBtn = document.getElementById('copyGrokBtn');
    const copyWikiBtn = document.getElementById('copyWikiBtn');
    const comparisonRaw = document.getElementById('comparison-raw');
    const saveBtn = document.getElementById('saveBtn');
    const homeLink = document.getElementById('homeLink');
    const resultsHomeLink = document.getElementById('resultsHomeLink');

    if (!articleInput || !compareBtn) {
        console.error('Required elements not found');
        return;
    }

    // Initialize sidebar
    initSidebar();
    
    // Update sidebar badge on load
    updateSidebarBadge();

    // Home link click handlers
    if (homeLink) {
        homeLink.addEventListener('click', resetToSearchView);
    }
    if (resultsHomeLink) {
        resultsHomeLink.addEventListener('click', resetToSearchView);
    }

    // Initialize search/autocomplete
    initSearch(articleInput, suggestionsContainer, (result) => {
        compareArticlesHandler();
    });

    // Compare button click
    compareBtn.addEventListener('click', compareArticlesHandler);

    // New Search button
    if (newSearchBtn) {
        newSearchBtn.addEventListener('click', () => {
            resetToSearchView();
        });
    }

    // Enter key handler
    articleInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            if (!handleEnterKey(suggestionsContainer, () => compareArticlesHandler())) {
                compareArticlesHandler();
            }
        }
    });

    // Copy buttons
    if (copyBtn) {
        copyBtn.addEventListener('click', async () => {
            const text = window.lastComparisonMarkdown || 
                        (document.getElementById('comparison-content')?.innerText ?? '');
            await copyToClipboard(text, copyBtn);
        });
    }

    if (copyGrokBtn) {
        copyGrokBtn.addEventListener('click', async () => {
            await copyToClipboard(lastGrokCopyText, copyGrokBtn);
        });
    }

    if (copyWikiBtn) {
        copyWikiBtn.addEventListener('click', async () => {
            await copyToClipboard(lastWikiCopyText, copyWikiBtn);
        });
    }

    // Raw toggle
    if (rawToggle) {
        rawToggle.addEventListener('click', () => {
            const isOn = rawToggle.getAttribute('aria-pressed') === 'true';
            const next = !isOn;
            rawToggle.setAttribute('aria-pressed', String(next));
            const comparisonContent = document.getElementById('comparison-content');
            if (comparisonContent) {
                comparisonContent.classList.toggle('hidden', next);
            }
            if (comparisonRaw) {
                comparisonRaw.classList.toggle('hidden', !next);
            }
        });
    }

    // Save button
    if (saveBtn) {
        saveBtn.addEventListener('click', handleSaveComparison);
    }

    // Focus input on load
    articleInput.focus();
}

/**
 * Handle saving comparison
 */
async function handleSaveComparison() {
    if (!currentComparisonData) {
        showError('No comparison data to save');
        return;
    }
    
    try {
        // Get article title for the saved item
        const title = currentComparisonData.grokipedia?.title || 
                     currentComparisonData.wikipedia?.title || 
                     'Untitled Comparison';
        
        const dataToSave = {
            ...currentComparisonData,
            title
        };
        
        saveComparison(dataToSave);
        
        // Update sidebar badge
        updateSidebarBadge();
        
        // Show feedback
        const saveBtn = document.getElementById('saveBtn');
        if (saveBtn) {
            const originalHTML = saveBtn.innerHTML;
            saveBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3.5 7L6 9.5L10.5 4.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg> Saved';
            saveBtn.style.background = 'rgba(87, 200, 255, 0.2)';
            saveBtn.style.borderColor = 'rgba(95, 200, 255, 0.4)';
            
            setTimeout(() => {
                saveBtn.innerHTML = originalHTML;
                saveBtn.style.background = '';
                saveBtn.style.borderColor = '';
            }, 2000);
        }
    } catch (error) {
        console.error('Error saving comparison:', error);
        showError('Failed to save comparison');
    }
}

/**
 * Load a saved comparison
 * @param {string} id - ID of the saved comparison
 */
export function loadSavedComparison(id) {
    const saved = getComparisonById(id);
    if (!saved) {
        showError('Saved comparison not found');
        return;
    }
    
    // Set current comparison data
    currentComparisonData = {
        grokipedia: saved.grokipedia,
        wikipedia: saved.wikipedia,
        comparison: saved.comparison,
        comparison_error: saved.comparison_error,
        grokipedia_url: saved.grokipedia_url,
        wikipedia_url: saved.wikipedia_url
    };
    
    // Display the saved comparison
    displayResults(currentComparisonData);
}

// Listen for load comparison events (from sidebar)
window.addEventListener('loadComparison', (e) => {
    loadSavedComparison(e.detail.id);
});

/**
 * Reset to search view
 */
export function resetToSearchView() {
    currentComparisonData = null;
    const body = document.body;
    const mainContainer = document.getElementById('mainContainer');
    const initialView = document.getElementById('initialView');
    const resultsContainer = document.getElementById('results-container');
    const articleInput = document.getElementById('article-url');
    
    if (body) body.classList.remove('has-results');
    if (mainContainer) mainContainer.classList.remove('has-results');
    if (initialView) initialView.style.minHeight = '60vh';
    if (resultsContainer) resultsContainer.classList.add('hidden');
    if (articleInput) {
        articleInput.value = '';
        articleInput.focus();
    }
    
    clearError();
    hideLoading();
}

/**
 * Handle article comparison
 */
async function compareArticlesHandler() {
    const articleInput = document.getElementById('article-url');
    const articleUrl = articleInput?.value.trim();

    if (!articleUrl) {
        showError('Please provide an article URL');
        return;
    }

    // Show loading with progressive messages
    showLoading('Fetching articles...');
    const resultsContainer = document.getElementById('results-container');
    if (resultsContainer) {
        resultsContainer.classList.add('hidden');
    }
    clearError();
    setButtonDisabled('compareBtn', true);

    try {
        // Simulate progressive loading states
        setTimeout(() => {
            updateLoadingMessage('Fetching articles...');
        }, 500);
        
        setTimeout(() => {
            updateLoadingMessage('Analyzing content...');
        }, 1500);
        
        setTimeout(() => {
            updateLoadingMessage('Comparing articles...');
        }, 2500);

        const data = await compareArticles(articleUrl);
        displayResults(data);
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
        setButtonDisabled('compareBtn', false);
    }
}

/**
 * Display comparison results
 * @param {Object} data - Comparison data
 */
function displayResults(data) {
    // Store current comparison data
    currentComparisonData = data;
    
    // Display Grokipedia content
    displayArticle('grokipedia-content', data.grokipedia, 'summary');
    lastGrokCopyText = buildArticleCopy('Grokipedia', data.grokipedia);

    // Display Wikipedia content
    displayArticle('wikipedia-content', data.wikipedia, 'intro');
    lastWikiCopyText = buildArticleCopy('Wikipedia', data.wikipedia);

    // Display comparison
    displayComparison(data.comparison, data.comparison_error);

    // Update layout for results view
    showResultsView();
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

