/**
 * RIK JavaScript/Node.js Client
 * ==============================
 *
 * Official JavaScript client library for the Recursive Intelligence Kernel (RIK).
 * Works in both Node.js and browser environments.
 *
 * Example (Node.js):
 *   const RIKClient = require('./rik-client');
 *   const client = new RIKClient('http://localhost:8000');
 *   const result = await client.processInvoice(pdfContent, 'INV-001');
 *   console.log(result.final_action);
 *
 * Example (Browser):
 *   <script src="rik-client.js"></script>
 *   <script>
 *     const client = new RIKClient('http://localhost:8000');
 *     client.processInvoice(pdfContent, 'INV-001')
 *       .then(result => console.log(result.final_action));
 *   </script>
 */

class RIKClient {
    /**
     * Create a new RIK client.
     *
     * @param {string} baseUrl - Base URL of RIK API (e.g., 'http://localhost:8000')
     * @param {Object} options - Client options
     * @param {string} options.apiKey - Optional API key for authentication
     * @param {number} options.timeout - Request timeout in milliseconds (default: 30000)
     * @param {number} options.maxRetries - Maximum number of retries (default: 3)
     */
    constructor(baseUrl = 'http://localhost:8000', options = {}) {
        this.baseUrl = baseUrl.replace(/\/$/, ''); // Remove trailing slash
        this.apiKey = options.apiKey || null;
        this.timeout = options.timeout || 30000;
        this.maxRetries = options.maxRetries || 3;

        // Detect environment
        this.isNode = typeof process !== 'undefined' && process.versions && process.versions.node;

        // Use node-fetch in Node.js environment
        if (this.isNode && typeof fetch === 'undefined') {
            try {
                this.fetch = require('node-fetch');
            } catch (e) {
                console.warn('node-fetch not found. Please install it: npm install node-fetch');
                this.fetch = null;
            }
        } else {
            this.fetch = fetch;
        }
    }

    /**
     * Make HTTP request with retry logic and error handling.
     *
     * @private
     */
    async _request(method, endpoint, data = null, params = null, retryCount = 0) {
        const url = new URL(`${this.baseUrl}${endpoint}`);

        // Add query parameters
        if (params) {
            Object.keys(params).forEach(key =>
                url.searchParams.append(key, params[key])
            );
        }

        // Build headers
        const headers = {
            'Content-Type': 'application/json',
        };

        if (this.apiKey) {
            headers['X-API-Key'] = this.apiKey;
        }

        // Build request options
        const options = {
            method: method,
            headers: headers,
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        try {
            // Create timeout promise
            const timeoutPromise = new Promise((_, reject) =>
                setTimeout(() => reject(new Error('Request timeout')), this.timeout)
            );

            // Make request with timeout
            const response = await Promise.race([
                this.fetch(url.toString(), options),
                timeoutPromise
            ]);

            // Handle HTTP errors
            if (response.status === 401 || response.status === 403) {
                throw new RIKAuthenticationError('Authentication failed. Check your API key.');
            }

            if (response.status === 422) {
                const errorData = await response.json();
                throw new RIKValidationError(errorData.detail || 'Validation error', errorData.errors);
            }

            if (response.status === 429) {
                const retryAfter = response.headers.get('Retry-After');
                throw new RIKRateLimitError(retryAfter);
            }

            if (response.status >= 400) {
                let errorMessage = `API request failed with status ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorMessage;
                } catch (e) {
                    // Ignore JSON parse error
                }
                throw new RIKAPIError(errorMessage, response.status, endpoint);
            }

            // Parse successful response
            const responseData = await response.json();
            return responseData;

        } catch (error) {
            // Retry on network errors
            if (retryCount < this.maxRetries &&
                (error.message === 'Request timeout' || error.name === 'FetchError')) {

                const delay = Math.pow(2, retryCount) * 1000; // Exponential backoff
                await new Promise(resolve => setTimeout(resolve, delay));
                return this._request(method, endpoint, data, params, retryCount + 1);
            }

            // Re-throw RIK errors
            if (error instanceof RIKError) {
                throw error;
            }

            // Wrap other errors
            if (error.message === 'Request timeout') {
                throw new RIKTimeoutError(this.timeout / 1000, endpoint);
            }

            if (error.message.includes('fetch')) {
                throw new RIKConnectionError(url.toString(), error);
            }

            throw new RIKAPIError(error.message, 0, endpoint);
        }
    }

    // ========================================================================
    // CORE ENDPOINTS
    // ========================================================================

    /**
     * Execute a reasoning task.
     *
     * @param {string} task - Task description to process
     * @returns {Promise<Object>} Task result with reasoning output
     */
    async runTask(task) {
        return await this._request('POST', '/run_task', { task });
    }

    /**
     * Process invoice with intelligent exception handling.
     *
     * @param {string} pdfContent - PDF content as string or JSON
     * @param {string} invoiceId - Optional invoice identifier
     * @param {Object} context - Optional additional context
     * @returns {Promise<Object>} Invoice processing result with decision and reasoning
     */
    async processInvoice(pdfContent, invoiceId = null, context = null) {
        const payload = {
            pdf_content: pdfContent,
            invoice_id: invoiceId,
            context: context
        };
        return await this._request('POST', '/process_invoice', payload);
    }

    /**
     * Recover broken web scraper selector.
     *
     * @param {string} failedSelector - The selector that stopped working
     * @param {string} html - Current HTML content
     * @param {string} url - URL being scraped
     * @param {Object} context - Optional context about what should be selected
     * @returns {Promise<Object>} Selector recovery result with new selector and reasoning
     */
    async recoverSelector(failedSelector, html, url, context = null) {
        const payload = {
            failed_selector: failedSelector,
            html: html,
            url: url,
            context: context
        };
        return await this._request('POST', '/recover_selector', payload);
    }

    /**
     * Test if a selector works on given HTML.
     *
     * @param {string} selector - CSS or XPath selector to test
     * @param {string} html - HTML content to test against
     * @param {string} selectorType - 'css' or 'xpath' (default: 'css')
     * @returns {Promise<Object>} Test result with success status and matched elements
     */
    async testSelector(selector, html, selectorType = 'css') {
        const payload = {
            selector: selector,
            html: html,
            selector_type: selectorType
        };
        return await this._request('POST', '/test_selector', payload);
    }

    // ========================================================================
    // MONITORING & ANALYTICS
    // ========================================================================

    /**
     * Get API health status.
     *
     * @returns {Promise<Object>} Health status with subsystem checks
     */
    async getHealth() {
        return await this._request('GET', '/health');
    }

    /**
     * Check if API is alive (simple liveness check).
     *
     * @returns {Promise<boolean>} True if API is responding
     */
    async isAlive() {
        try {
            const result = await this._request('GET', '/health/live');
            return result.status === 'alive';
        } catch (error) {
            return false;
        }
    }

    /**
     * Check if API is ready to handle requests.
     *
     * @returns {Promise<boolean>} True if API is ready
     */
    async isReady() {
        try {
            const result = await this._request('GET', '/health/ready');
            return result.status === 'ready';
        } catch (error) {
            return false;
        }
    }

    /**
     * Get performance and efficiency metrics.
     *
     * @returns {Promise<Object>} Metrics with efficiency stats
     */
    async getMetrics() {
        return await this._request('GET', '/metrics');
    }

    /**
     * Get invoice processing statistics and ROI data.
     *
     * @returns {Promise<Object>} Invoice stats with automation rates and savings
     */
    async getInvoiceStats() {
        return await this._request('GET', '/invoice_stats');
    }

    /**
     * Get API version information.
     *
     * @returns {Promise<Object>} Version and environment info
     */
    async getVersion() {
        return await this._request('GET', '/version');
    }

    /**
     * Retrieve episodic memory entries.
     *
     * @param {number} limit - Maximum number of entries to return (default: 10)
     * @returns {Promise<Array>} List of memory episodes
     */
    async getMemory(limit = 10) {
        const result = await this._request('GET', '/memory', null, { limit });
        return result.episodes || [];
    }
}

// ============================================================================
// EXCEPTION CLASSES
// ============================================================================

class RIKError extends Error {
    constructor(message, details = {}) {
        super(message);
        this.name = 'RIKError';
        this.details = details;
    }
}

class RIKConnectionError extends RIKError {
    constructor(url, originalError = null) {
        super(`Failed to connect to RIK API at ${url}`);
        this.name = 'RIKConnectionError';
        this.url = url;
        this.originalError = originalError;
    }
}

class RIKAPIError extends RIKError {
    constructor(message, statusCode, endpoint = null) {
        super(message);
        this.name = 'RIKAPIError';
        this.statusCode = statusCode;
        this.endpoint = endpoint;
    }
}

class RIKAuthenticationError extends RIKAPIError {
    constructor(message = 'Authentication failed. Check your API key.') {
        super(message, 401);
        this.name = 'RIKAuthenticationError';
    }
}

class RIKValidationError extends RIKAPIError {
    constructor(message, validationErrors = null) {
        super(`Validation error: ${message}`, 422);
        this.name = 'RIKValidationError';
        this.validationErrors = validationErrors;
    }
}

class RIKTimeoutError extends RIKError {
    constructor(timeoutSeconds, endpoint = null) {
        super(`Request timed out after ${timeoutSeconds}s`);
        this.name = 'RIKTimeoutError';
        this.timeoutSeconds = timeoutSeconds;
        this.endpoint = endpoint;
    }
}

class RIKRateLimitError extends RIKAPIError {
    constructor(retryAfter = null) {
        let message = 'Rate limit exceeded';
        if (retryAfter) {
            message += `. Retry after ${retryAfter} seconds`;
        }
        super(message, 429);
        this.name = 'RIKRateLimitError';
        this.retryAfter = retryAfter;
    }
}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RIKClient;
    module.exports.RIKError = RIKError;
    module.exports.RIKConnectionError = RIKConnectionError;
    module.exports.RIKAPIError = RIKAPIError;
    module.exports.RIKAuthenticationError = RIKAuthenticationError;
    module.exports.RIKValidationError = RIKValidationError;
    module.exports.RIKTimeoutError = RIKTimeoutError;
    module.exports.RIKRateLimitError = RIKRateLimitError;
}
