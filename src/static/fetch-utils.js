/**
 * Enhanced fetch utilities with cache support for offline mode
 */

/**
 * Fetch data with cache support
 * Returns cached data immediately if available, then fetches fresh data
 * @param {string} url - The URL to fetch
 * @param {Function} onCachedData - Callback when cached data is available (data, metadata)
 * @param {Function} onFreshData - Callback when fresh data is fetched (data)
 * @param {Function} onError - Callback when fetch fails (error, hasCachedData)
 * @return {Promise} Promise that resolves when fetch completes
 */
async function fetchWithCache(url, onCachedData, onFreshData, onError) {
    // Check cache first
    const cached = CacheManager.get(url);
    let hasCachedData = false;

    if (cached) {
        hasCachedData = true;
        // Return cached data immediately
        if (onCachedData) {
            onCachedData(cached.data, {
                timestamp: cached.timestamp,
                age: cached.age,
                isExpired: cached.isExpired,
                isOnline: CacheManager.isOnline(),
                formattedTime: CacheManager.formatTimestamp(cached.timestamp)
            });
        }
    }

    // Try to fetch fresh data
    try {
        const response = await get(url);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // Save to cache
        CacheManager.set(url, data);
        
        // Return fresh data
        if (onFreshData) {
            onFreshData(data);
        }

        return { success: true, data: data };
    } catch (error) {
        console.error('Fetch failed:', error);
        
        // Call error callback
        if (onError) {
            onError(error, hasCachedData);
        }

        return { success: false, error: error, hasCachedData: hasCachedData };
    }
}

/**
 * Create a data state object for Vue components
 * @return {Object} Reactive data state
 */
function createDataState() {
    return {
        data: null,
        loading: true,
        error: null,
        isFromCache: false,
        isFresh: false,
        isOffline: false,
        cacheTimestamp: null,
        cacheAge: null,
        formattedCacheTime: null
    };
}

/**
 * Load data with cache support for Vue components
 * @param {Object} state - Vue reactive state object
 * @param {string} url - The URL to fetch
 * @param {Function} dataExtractor - Function to extract data from response (optional)
 * @return {Promise} Promise that resolves when fetch completes
 */
async function loadDataWithCache(state, url, dataExtractor) {
    state.loading = true;
    state.error = null;
    state.isOffline = !CacheManager.isOnline();

    const result = await fetchWithCache(
        url,
        // onCachedData
        (data, metadata) => {
            if (dataExtractor) {
                Object.assign(state, dataExtractor(data));
            } else {
                state.data = data;
            }
            state.isFromCache = true;
            state.isFresh = false;
            state.cacheTimestamp = metadata.timestamp;
            state.cacheAge = metadata.age;
            state.formattedCacheTime = metadata.formattedTime;
            state.isOffline = !metadata.isOnline;
            state.loading = !metadata.isOnline; // Keep loading if we're online and waiting for fresh data
        },
        // onFreshData
        (data) => {
            if (dataExtractor) {
                Object.assign(state, dataExtractor(data));
            } else {
                state.data = data;
            }
            state.isFromCache = false;
            state.isFresh = true;
            state.loading = false;
            state.error = null;
            state.cacheTimestamp = Date.now();
            state.formattedCacheTime = CacheManager.formatTimestamp(Date.now());
            state.isOffline = false;
        },
        // onError
        (error, hasCachedData) => {
            state.error = error;
            state.loading = false;
            state.isOffline = !CacheManager.isOnline();
            
            // If we don't have cached data, show error
            if (!hasCachedData) {
                state.data = null;
            }
        }
    );

    // If we had no cached data and fetch failed, stop loading
    if (!result.success && !result.hasCachedData) {
        state.loading = false;
    }

    return result;
}
