/**
 * Storage Module - Manages saved comparisons in localStorage
 */

const STORAGE_KEY = 'saved_comparisons';

/**
 * Get all saved comparisons
 * @returns {Array} Array of saved comparisons
 */
export function getSavedComparisons() {
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (!stored) return [];
        return JSON.parse(stored);
    } catch (error) {
        console.error('Error loading saved comparisons:', error);
        return [];
    }
}

/**
 * Save a comparison
 * @param {Object} comparisonData - The comparison data to save
 * @returns {string} ID of the saved comparison
 */
export function saveComparison(comparisonData) {
    try {
        const saved = getSavedComparisons();
        const id = Date.now().toString();
        const savedItem = {
            id,
            title: comparisonData.title || 'Untitled Comparison',
            date: new Date().toISOString(),
            grokipedia: comparisonData.grokipedia,
            wikipedia: comparisonData.wikipedia,
            comparison: comparisonData.comparison,
            comparison_error: comparisonData.comparison_error,
            grokipedia_url: comparisonData.grokipedia_url,
            wikipedia_url: comparisonData.wikipedia_url
        };
        
        saved.unshift(savedItem); // Add to beginning
        
        // Limit to 50 saved comparisons
        const trimmed = saved.slice(0, 50);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
        
        return id;
    } catch (error) {
        console.error('Error saving comparison:', error);
        throw error;
    }
}

/**
 * Delete a saved comparison
 * @param {string} id - ID of the comparison to delete
 */
export function deleteComparison(id) {
    try {
        const saved = getSavedComparisons();
        const filtered = saved.filter(item => item.id !== id);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
    } catch (error) {
        console.error('Error deleting comparison:', error);
        throw error;
    }
}

/**
 * Get a saved comparison by ID
 * @param {string} id - ID of the comparison
 * @returns {Object|null} The comparison data or null
 */
export function getComparisonById(id) {
    try {
        const saved = getSavedComparisons();
        return saved.find(item => item.id === id) || null;
    } catch (error) {
        console.error('Error getting comparison:', error);
        return null;
    }
}

/**
 * Get count of saved comparisons
 * @returns {number} Number of saved comparisons
 */
export function getSavedCount() {
    return getSavedComparisons().length;
}

/**
 * Format date for display
 * @param {string} isoDate - ISO date string
 * @returns {string} Formatted date string
 */
export function formatDate(isoDate) {
    try {
        const date = new Date(isoDate);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        
        return date.toLocaleDateString();
    } catch {
        return 'Unknown';
    }
}

