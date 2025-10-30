/**
 * Search Module - Handles autocomplete and search functionality
 */

let searchTimeout = null;
let currentSuggestions = [];
let selectedSuggestionIndex = -1;

// Import dependencies
import { escapeHtml } from './utils.js';

/**
 * Initialize search functionality
 * @param {HTMLElement} inputElement - Input element for search
 * @param {HTMLElement} suggestionsContainer - Container for suggestions
 * @param {Function} onSelect - Callback when suggestion is selected
 */
export function initSearch(inputElement, suggestionsContainer, onSelect) {
    if (!inputElement || !suggestionsContainer) return;

    // Handle input events with debouncing
    inputElement.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        
        if (searchTimeout) {
            clearTimeout(searchTimeout);
        }

        if (query.length < 2) {
            hideSuggestions(suggestionsContainer);
            return;
        }

        searchTimeout = setTimeout(async () => {
            try {
                const { searchArticles } = await import('./api.js');
                const results = await searchArticles(query, 8);
                showSuggestions(suggestionsContainer, results, inputElement, onSelect);
            } catch (error) {
                console.error('Search error:', error);
                hideSuggestions(suggestionsContainer);
            }
        }, 300);
    });

    // Handle keyboard navigation
    inputElement.addEventListener('keydown', (e) => {
        if (!suggestionsContainer.classList.contains('hidden')) {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                selectedSuggestionIndex = Math.min(selectedSuggestionIndex + 1, currentSuggestions.length - 1);
                updateSuggestionHighlight(suggestionsContainer);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                selectedSuggestionIndex = Math.max(selectedSuggestionIndex - 1, -1);
                updateSuggestionHighlight(suggestionsContainer);
            } else if (e.key === 'Escape') {
                hideSuggestions(suggestionsContainer);
            }
        }
    });

    // Handle clicking outside
    document.addEventListener('click', (e) => {
        if (!suggestionsContainer.contains(e.target) && e.target !== inputElement) {
            hideSuggestions(suggestionsContainer);
        }
    });
}

/**
 * Show search suggestions
 * @param {HTMLElement} container - Container element
 * @param {Array} results - Array of suggestion results
 * @param {HTMLElement} inputElement - Input element
 * @param {Function} onSelect - Callback when selected
 */
function showSuggestions(container, results, inputElement, onSelect) {
    currentSuggestions = results;
    selectedSuggestionIndex = -1;
    
    const emptyMessage = container.querySelector('.suggestions-empty');
    
    if (results.length === 0) {
        if (emptyMessage) {
            emptyMessage.classList.remove('hidden');
        }
        container.classList.remove('hidden');
        return;
    }
    
    if (emptyMessage) {
        emptyMessage.classList.add('hidden');
    }
    
    // Clear existing suggestions (except empty message)
    const existingItems = container.querySelectorAll('.suggestion-item');
    existingItems.forEach(item => item.remove());
    
    results.forEach((result, index) => {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        item.innerHTML = `
            <div class="title">${escapeHtml(result.title)}</div>
            <div class="url">${escapeHtml(result.url)}</div>
        `;
        item.addEventListener('click', () => {
            selectSuggestion(result, inputElement, container, onSelect);
        });
        item.addEventListener('mouseenter', () => {
            selectedSuggestionIndex = index;
            updateSuggestionHighlight(container);
        });
        container.appendChild(item);
    });

    container.classList.remove('hidden');
}

/**
 * Hide search suggestions
 * @param {HTMLElement} container - Container element
 */
function hideSuggestions(container) {
    container.classList.add('hidden');
    const emptyMessage = container.querySelector('.suggestions-empty');
    if (emptyMessage) {
        emptyMessage.classList.add('hidden');
    }
    currentSuggestions = [];
    selectedSuggestionIndex = -1;
}

/**
 * Update highlight on suggestions
 * @param {HTMLElement} container - Container element
 */
function updateSuggestionHighlight(container) {
    const items = container.querySelectorAll('.suggestion-item');
    items.forEach((item, index) => {
        if (index === selectedSuggestionIndex) {
            item.classList.add('selected');
        } else {
            item.classList.remove('selected');
        }
    });
}

/**
 * Select a suggestion
 * @param {Object} result - Selected result
 * @param {HTMLElement} inputElement - Input element
 * @param {HTMLElement} container - Container element
 * @param {Function} onSelect - Callback function
 */
function selectSuggestion(result, inputElement, container, onSelect) {
    inputElement.value = result.url;
    hideSuggestions(container);
    if (onSelect) {
        onSelect(result);
    }
}

/**
 * Handle Enter key press for suggestions
 * @param {HTMLElement} container - Container element
 * @param {Function} onSelect - Callback function
 * @returns {boolean} True if suggestion was selected
 */
export function handleEnterKey(container, onSelect) {
    if (selectedSuggestionIndex >= 0 && currentSuggestions[selectedSuggestionIndex]) {
        const result = currentSuggestions[selectedSuggestionIndex];
        const inputElement = document.getElementById('article-url');
        selectSuggestion(result, inputElement, container, onSelect);
        return true;
    }
    return false;
}

