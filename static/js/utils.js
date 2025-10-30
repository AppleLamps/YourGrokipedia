/**
 * Utils Module - Utility functions
 */

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped HTML
 */
export function escapeHtml(text) {
    if (typeof text !== 'string') return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @param {HTMLElement} button - Button element for feedback
 * @returns {Promise<boolean>} Success status
 */
export async function copyToClipboard(text, button = null) {
    try {
        await navigator.clipboard.writeText(text);
        if (button) {
            showCopyFeedback(button);
        }
        return true;
    } catch {
        // Fallback for older browsers
        const ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        try {
            document.execCommand('copy');
            if (button) {
                showCopyFeedback(button);
            }
            document.body.removeChild(ta);
            return true;
        } catch {
            if (button) {
                button.textContent = 'Failed';
                button.classList.add('copy-failed');
            }
            document.body.removeChild(ta);
            return false;
        }
    }
}

/**
 * Show copy feedback animation
 * @param {HTMLElement} button - Button element
 */
function showCopyFeedback(button) {
    const originalText = button.innerHTML;
    button.classList.add('copied');
    
    setTimeout(() => {
        button.classList.remove('copied');
        // Restore original text if it was changed
        if (button.textContent !== originalText && !originalText.includes('<svg')) {
            button.textContent = originalText;
        }
    }, 600);
}

/**
 * Build article copy text
 * @param {string} label - Article label (e.g., "Grokipedia")
 * @param {Object} data - Article data
 * @returns {string} Formatted text
 */
export function buildArticleCopy(label, data) {
    if (!data) return `${label}: not found`;
    const title = data.title || '';
    const url = data.url || '';
    const intro = data.summary || data.intro || '';
    const sections = (data.sections || []).map(s => `- ${s}`).join('\n');
    return [
        `${label}`,
        title,
        url,
        '',
        intro,
        '',
        'Sections:',
        sections
    ].filter(Boolean).join('\n');
}

