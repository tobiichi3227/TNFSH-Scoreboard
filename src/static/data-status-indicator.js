/**
 * Vue component for displaying data freshness and offline status
 */

const DataStatusIndicator = {
    template: `
        <div v-if="showIndicator" class="alert alert-dismissible fade show" :class="alertClass" role="alert">
            <div class="d-flex align-items-center">
                <svg v-if="isOffline" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="me-2">
                    <line x1="1" y1="1" x2="23" y2="23"></line>
                    <path d="M16.72 11.06A10.94 10.94 0 0 1 19 12.55"></path>
                    <path d="M5 12.55a10.94 10.94 0 0 1 5.17-2.39"></path>
                    <path d="M10.71 5.05A16 16 0 0 1 22.58 9"></path>
                    <path d="M1.42 9a15.91 15.91 0 0 1 4.7-2.88"></path>
                    <path d="M8.53 16.11a6 6 0 0 1 6.95 0"></path>
                    <line x1="12" y1="20" x2="12.01" y2="20"></line>
                </svg>
                <svg v-else-if="isFromCache && !isFresh" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="me-2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                <svg v-else-if="loading" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="me-2">
                    <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
                </svg>
                <div class="flex-grow-1">
                    <strong v-text="statusTitle"></strong>
                    <span v-if="statusMessage" class="ms-2" v-text="statusMessage"></span>
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        </div>
    `,
    props: {
        loading: {
            type: Boolean,
            default: false
        },
        isFromCache: {
            type: Boolean,
            default: false
        },
        isFresh: {
            type: Boolean,
            default: false
        },
        isOffline: {
            type: Boolean,
            default: false
        },
        formattedCacheTime: {
            type: String,
            default: null
        },
        error: {
            type: [Object, String, Error, null],
            default: null
        }
    },
    computed: {
        showIndicator() {
            return this.isOffline || (this.isFromCache && !this.isFresh) || (this.loading && this.isFromCache);
        },
        alertClass() {
            if (this.isOffline) {
                return 'alert-warning';
            } else if (this.loading && this.isFromCache) {
                return 'alert-info';
            } else if (this.isFromCache && !this.isFresh) {
                return 'alert-info';
            }
            return 'alert-info';
        },
        statusTitle() {
            if (this.isOffline) {
                return '離線模式';
            } else if (this.loading && this.isFromCache) {
                return '更新中...';
            } else if (this.isFromCache && !this.isFresh) {
                return '顯示快取資料';
            }
            return '';
        },
        statusMessage() {
            if (this.isOffline) {
                return this.formattedCacheTime ? `顯示 ${this.formattedCacheTime} 的資料` : '顯示離線資料';
            } else if (this.loading && this.isFromCache) {
                return this.formattedCacheTime ? `目前顯示 ${this.formattedCacheTime} 的資料，正在獲取最新資料` : '正在獲取最新資料';
            } else if (this.isFromCache && !this.isFresh) {
                return this.formattedCacheTime ? `更新於 ${this.formattedCacheTime}` : '';
            }
            return '';
        }
    }
};
