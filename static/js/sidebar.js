/**
 * Sidebar Module - Handles sidebar UI interactions
 */

import { getSavedComparisons, deleteComparison, formatDate, getSavedCount } from './storage.js';
import { escapeHtml } from './utils.js';

/**
 * Initialize the sidebar
 */
export function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
    const sidebarCloseBtn = document.getElementById('sidebarCloseBtn');
    
    if (!sidebar || !sidebarToggleBtn || !sidebarCloseBtn) {
        console.error('Sidebar elements not found');
        return;
    }
    
    // Toggle sidebar open
    sidebarToggleBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        openSidebar();
    });
    
    // Close sidebar
    sidebarCloseBtn.addEventListener('click', () => {
        closeSidebar();
    });
    
    // Close sidebar when clicking outside
    document.addEventListener('click', (e) => {
        if (sidebar.classList.contains('open') && 
            !sidebar.contains(e.target) && 
            !sidebarToggleBtn.contains(e.target)) {
            closeSidebar();
        }
    });
    
    // Prevent sidebar click from closing
    sidebar.addEventListener('click', (e) => {
        e.stopPropagation();
    });
    
    // Load saved comparisons and update badge
    loadSavedComparisons();
    updateSidebarBadge();
}

/**
 * Open the sidebar
 */
export function openSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        sidebar.classList.add('open');
        loadSavedComparisons();
    }
}

/**
 * Close the sidebar
 */
export function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        sidebar.classList.remove('open');
    }
}

/**
 * Load and display saved comparisons
 */
export function loadSavedComparisons() {
    const container = document.getElementById('savedComparisons');
    const emptyState = document.getElementById('sidebarEmpty');
    const badge = document.getElementById('sidebarBadge');
    
    if (!container) return;
    
    const saved = getSavedComparisons();
    
    // Update badge
    if (badge) {
        if (saved.length > 0) {
            badge.textContent = saved.length;
            badge.style.display = 'block';
        } else {
            badge.style.display = 'none';
        }
    }
    
    if (saved.length === 0) {
        container.innerHTML = '';
        if (emptyState) {
            emptyState.style.display = 'block';
            container.appendChild(emptyState);
        }
        return;
    }
    
    // Hide empty state
    if (emptyState) {
        emptyState.style.display = 'none';
    }
    
    // Render saved comparisons
    container.innerHTML = saved.map(item => {
        const title = escapeHtml(item.title);
        const date = formatDate(item.date);
        return `
            <div class="saved-comparison-item" data-id="${item.id}">
                <button class="saved-comparison-delete" aria-label="Delete comparison" title="Delete comparison">
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M9 3L3 9M3 3L9 9" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </button>
                <h3>${title}</h3>
                <div class="saved-comparison-meta">
                    <span class="saved-comparison-date">${date}</span>
                </div>
            </div>
        `;
    }).join('');
    
    // Add event listeners
    container.querySelectorAll('.saved-comparison-item').forEach(item => {
        const id = item.dataset.id;
        
        // Click to load
        item.addEventListener('click', (e) => {
            if (!e.target.closest('.saved-comparison-delete')) {
                loadComparison(id);
            }
        });
        
        // Delete button
        const deleteBtn = item.querySelector('.saved-comparison-delete');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                deleteComparisonHandler(id);
            });
        }
    });
}

/**
 * Handle loading a saved comparison
 * @param {string} id - ID of the comparison to load
 */
function loadComparison(id) {
    // Dispatch event for main.js to handle
    window.dispatchEvent(new CustomEvent('loadComparison', { detail: { id } }));
    closeSidebar();
}

/**
 * Handle deleting a saved comparison
 * @param {string} id - ID of the comparison to delete
 */
function deleteComparisonHandler(id) {
    if (confirm('Are you sure you want to delete this saved comparison?')) {
        deleteComparison(id);
        loadSavedComparisons();
        updateSidebarBadge();
    }
}

/**
 * Update sidebar badge count
 */
export function updateSidebarBadge() {
    const badge = document.getElementById('sidebarBadge');
    if (badge) {
        const count = getSavedCount();
        if (count > 0) {
            badge.textContent = count;
            badge.style.display = 'block';
        } else {
            badge.style.display = 'none';
        }
    }
}

