/**
 * Cache management utility for offline mode support
 * Stores API responses in LocalStorage with timestamps
 */

const CacheManager = (function() {
    const CACHE_PREFIX = 'tnfsh_cache_';
    const CACHE_TIMESTAMP_PREFIX = 'tnfsh_cache_ts_';
    const CACHE_MAX_AGE = 24 * 60 * 60 * 1000; // 24 hours in milliseconds

    /**
     * Generate a cache key from URL
     * @param {string} url - The URL to generate key from
     * @return {string} Cache key
     */
    function getCacheKey(url) {
        // Remove cache-busting parameter and base URL to create stable key
        const urlObj = new URL(url, window.location.origin);
        urlObj.searchParams.delete('cache');
        return CACHE_PREFIX + urlObj.pathname + urlObj.search;
    }

    /**
     * Get timestamp key for a cache key
     * @param {string} cacheKey - The cache key
     * @return {string} Timestamp key
     */
    function getTimestampKey(cacheKey) {
        return cacheKey.replace(CACHE_PREFIX, CACHE_TIMESTAMP_PREFIX);
    }

    /**
     * Save data to cache
     * @param {string} url - The URL to cache data for
     * @param {Object} data - The data to cache
     */
    function set(url, data) {
        try {
            const cacheKey = getCacheKey(url);
            const timestampKey = getTimestampKey(cacheKey);
            
            localStorage.setItem(cacheKey, JSON.stringify(data));
            localStorage.setItem(timestampKey, Date.now().toString());
        } catch (e) {
            console.warn('Failed to save to cache:', e);
            // If localStorage is full, try to clear old entries
            if (e.name === 'QuotaExceededError') {
                clearOldEntries();
                try {
                    const cacheKey = getCacheKey(url);
                    const timestampKey = getTimestampKey(cacheKey);
                    localStorage.setItem(cacheKey, JSON.stringify(data));
                    localStorage.setItem(timestampKey, Date.now().toString());
                } catch (retryError) {
                    console.error('Failed to save to cache after cleanup:', retryError);
                }
            }
        }
    }

    /**
     * Get data from cache
     * @param {string} url - The URL to retrieve cached data for
     * @return {Object|null} Cached data with metadata or null if not found/expired
     */
    function get(url) {
        try {
            const cacheKey = getCacheKey(url);
            const timestampKey = getTimestampKey(cacheKey);
            
            const cachedData = localStorage.getItem(cacheKey);
            const cachedTimestamp = localStorage.getItem(timestampKey);
            
            if (!cachedData || !cachedTimestamp) {
                return null;
            }

            const timestamp = parseInt(cachedTimestamp, 10);
            const age = Date.now() - timestamp;
            
            return {
                data: JSON.parse(cachedData),
                timestamp: timestamp,
                age: age,
                isExpired: age > CACHE_MAX_AGE
            };
        } catch (e) {
            console.warn('Failed to read from cache:', e);
            return null;
        }
    }

    /**
     * Clear old cache entries to free up space
     */
    function clearOldEntries() {
        try {
            const now = Date.now();
            const keysToRemove = [];

            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key && key.startsWith(CACHE_TIMESTAMP_PREFIX)) {
                    const timestamp = parseInt(localStorage.getItem(key), 10);
                    if (now - timestamp > CACHE_MAX_AGE) {
                        const cacheKey = key.replace(CACHE_TIMESTAMP_PREFIX, CACHE_PREFIX);
                        keysToRemove.push(key);
                        keysToRemove.push(cacheKey);
                    }
                }
            }

            keysToRemove.forEach(key => localStorage.removeItem(key));
            console.log('Cleared', keysToRemove.length / 2, 'old cache entries');
        } catch (e) {
            console.warn('Failed to clear old entries:', e);
        }
    }

    /**
     * Clear all cache entries
     */
    function clearAll() {
        try {
            const keysToRemove = [];
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key && (key.startsWith(CACHE_PREFIX) || key.startsWith(CACHE_TIMESTAMP_PREFIX))) {
                    keysToRemove.push(key);
                }
            }
            keysToRemove.forEach(key => localStorage.removeItem(key));
            console.log('Cleared all cache entries');
        } catch (e) {
            console.warn('Failed to clear cache:', e);
        }
    }

    /**
     * Check if we're currently online
     * @return {boolean} True if online, false otherwise
     */
    function isOnline() {
        return navigator.onLine;
    }

    /**
     * Format timestamp for display
     * @param {number} timestamp - Timestamp in milliseconds
     * @return {string} Formatted timestamp
     */
    function formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) {
            return '剛剛';
        } else if (diffMins < 60) {
            return `${diffMins} 分鐘前`;
        } else if (diffHours < 24) {
            return `${diffHours} 小時前`;
        } else {
            return `${diffDays} 天前`;
        }
    }

    // Public API
    return {
        set: set,
        get: get,
        clearOldEntries: clearOldEntries,
        clearAll: clearAll,
        isOnline: isOnline,
        formatTimestamp: formatTimestamp
    };
})();
