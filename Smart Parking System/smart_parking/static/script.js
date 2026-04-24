/**
 * Smart Parking System - Frontend JavaScript
 * ==========================================
 * Handles:
 * - Live video stream display
 * - Real-time status updates via API polling
 * - UI interactions and animations
 * - Alert notifications
 */

(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        API_STATUS_INTERVAL: 2000,  // Poll every 2 seconds
        VIDEO_RETRY_INTERVAL: 5000, // Retry video every 5 seconds
        MAX_RETRIES: 3
    };

    // State
    let state = {
        totalSlots: 0,
        emptySlots: 0,
        occupiedSlots: 0,
        isAvailable: false,
        videoRetries: 0,
        statusInterval: null
    };

    // DOM Elements
    const elements = {
        videoFeed: null,
        totalSlots: null,
        emptySlots: null,
        occupiedSlots: null,
        statusBadge: null,
        alertBanner: null,
        slotsList: null,
        liveIndicator: null
    };

    /**
     * Initialize the application
     */
    function init() {
        cacheElements();
        setupEventListeners();
        startStatusPolling();
        checkVideoStream();
    }

    /**
     * Cache DOM element references
     */
    function cacheElements() {
        elements.videoFeed = document.getElementById('videoFeed');
        elements.totalSlots = document.getElementById('totalSlots');
        elements.emptySlots = document.getElementById('emptySlots');
        elements.occupiedSlots = document.getElementById('occupiedSlots');
        elements.statusBadge = document.getElementById('statusBadge');
        elements.alertBanner = document.getElementById('alertBanner');
        elements.slotsList = document.getElementById('slotsList');
        elements.liveIndicator = document.getElementById('liveIndicator');
    }

    /**
     * Setup event listeners
     */
    function setupEventListeners() {
        // Handle video stream errors
        if (elements.videoFeed) {
            elements.videoFeed.onerror = handleVideoError;
        }

        // Handle page visibility changes
        document.addEventListener('visibilitychange', handleVisibilityChange);

        // Handle window focus
        window.addEventListener('focus', handleWindowFocus);
    }

    /**
     * Start polling for status updates
     */
    function startStatusPolling() {
        // Initial fetch
        fetchStatus();

        // Set up interval
        state.statusInterval = setInterval(fetchStatus, CONFIG.API_STATUS_INTERVAL);
    }

    /**
     * Fetch parking status from API
     */
    async function fetchStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();

            if (data.success) {
                updateUI(data.data);
            }
        } catch (error) {
            console.error('Error fetching status:', error);
        }
    }

    /**
     * Update UI with new status data
     * @param {Object} data - Status data from API
     */
    function updateUI(data) {
        // Update statistics
        if (elements.totalSlots) {
            elements.totalSlots.textContent = data.total_slots;
        }
        if (elements.emptySlots) {
            elements.emptySlots.textContent = data.empty_slots;
        }
        if (elements.occupiedSlots) {
            elements.occupiedSlots.textContent = data.occupied_slots;
        }

        // Update state
        state.totalSlots = data.total_slots;
        state.emptySlots = data.empty_slots;
        state.occupiedSlots = data.occupied_slots;
        state.isAvailable = data.available;

        // Update status badge
        updateStatusBadge(data.status, data.available);

        // Update alert banner
        updateAlertBanner(data.status, data.available);

        // Update slots list
        updateSlotsList();
    }

    /**
     * Update status badge
     * @param {string} status - Status text
     * @param {boolean} available - Whether parking is available
     */
    function updateStatusBadge(status, available) {
        if (!elements.statusBadge) return;

        elements.statusBadge.className = 'status-badge ' + (available ? 'available' : 'full');
        elements.statusBadge.innerHTML = `
            <span class="status-dot"></span>
            ${status}
        `;
    }

    /**
     * Update alert banner
     * @param {string} status - Status text
     * @param {boolean} available - Whether parking is available
     */
    function updateAlertBanner(status, available) {
        if (!elements.alertBanner) return;

        const icon = available ? '✓' : '✕';
        const message = available 
            ? `Great news! ${state.emptySlots} parking ${state.emptySlots === 1 ? 'slot' : 'slots'} available`
            : 'Sorry, parking lot is currently full';

        elements.alertBanner.className = 'alert-banner ' + (available ? 'available' : 'full');
        elements.alertBanner.innerHTML = `
            <span style="font-size: 1.5rem;">${icon}</span>
            <span>${message}</span>
        `;
    }

    /**
     * Update slots list display
     */
    function updateSlotsList() {
        if (!elements.slotsList) return;

        // Generate slot items based on current state
        let html = '';
        
        for (let i = 1; i <= state.totalSlots; i++) {
            const isEmpty = i <= state.emptySlots;
            html += `
                <div class="slot-item">
                    <span class="slot-number">#${i}</span>
                    <span class="slot-status ${isEmpty ? 'empty' : 'occupied'}">
                        ${isEmpty ? 'Empty' : 'Occupied'}
                    </span>
                </div>
            `;
        }

        elements.slotsList.innerHTML = html;
    }

    /**
     * Check video stream status
     */
    function checkVideoStream() {
        if (elements.videoFeed) {
            // Video is loading
            elements.videoFeed.style.display = 'block';
        }
    }

    /**
     * Handle video stream errors
     */
    function handleVideoError() {
        console.error('Video stream error');
        state.videoRetries++;

        if (state.videoRetries < CONFIG.MAX_RETRIES) {
            setTimeout(() => {
                if (elements.videoFeed) {
                    elements.videoFeed.src = '/video_feed?' + new Date().getTime();
                }
            }, CONFIG.VIDEO_RETRY_INTERVAL);
        }
    }

    /**
     * Handle page visibility changes
     */
    function handleVisibilityChange() {
        if (document.hidden) {
            // Pause polling when page is hidden
            if (state.statusInterval) {
                clearInterval(state.statusInterval);
                state.statusInterval = null;
            }
        } else {
            // Resume polling when page is visible
            if (!state.statusInterval) {
                startStatusPolling();
            }
        }
    }

    /**
     * Handle window focus
     */
    function handleWindowFocus() {
        // Refresh status when window gains focus
        fetchStatus();
    }

    /**
     * Format number with leading zero
     * @param {number} num - Number to format
     * @returns {string} Formatted number
     */
    function formatNumber(num) {
        return num.toString().padStart(2, '0');
    }

    /**
     * Show notification (optional feature)
     * @param {string} message - Notification message
     * @param {string} type - Notification type ('success', 'error', 'warning')
     */
    function showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: ${type === 'success' ? '#34a853' : type === 'error' ? '#ea4335' : '#fbbc04'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    // Add slideOut animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideOut {
            from {
                opacity: 1;
                transform: translateX(0);
            }
            to {
                opacity: 0;
                transform: translateX(100px);
            }
        }
    `;
    document.head.appendChild(style);

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose functions for debugging
    window.ParkingSystem = {
        fetchStatus: fetchStatus,
        getState: () => state,
        showNotification: showNotification
    };

})();