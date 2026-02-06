/**
 * API Client - Wrapper for all backend API calls
 */

const API_BASE = '/api';

class ApiClient {
    /**
     * Generic fetch wrapper with error handling
     */
    async request(url, options = {}) {
        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            // Handle 204 No Content
            if (response.status === 204) {
                return null;
            }

            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    /**
     * Get paginated list of papers
     */
    async getPapers(limit = 20, offset = 0, bookmarked = false) {
        const params = new URLSearchParams({
            limit: limit.toString(),
            offset: offset.toString(),
            bookmarked: bookmarked.toString()
        });

        return await this.request(`${API_BASE}/papers?${params}`);
    }

    /**
     * Get single paper by ID with Grok analysis
     */
    async getPaper(paperId) {
        return await this.request(`${API_BASE}/papers/${paperId}`);
    }

    /**
     * Search papers by keyword (full-text search)
     */
    async searchPapers(query, limit = 20) {
        const params = new URLSearchParams({
            q: query,
            limit: limit.toString()
        });

        return await this.request(`${API_BASE}/papers/search?${params}`);
    }

    /**
     * Add bookmark for a paper
     */
    async addBookmark(paperId, notes = null) {
        return await this.request(`${API_BASE}/bookmarks/`, {
            method: 'POST',
            body: JSON.stringify({
                paper_id: paperId,
                notes: notes
            })
        });
    }

    /**
     * Remove bookmark for a paper
     */
    async removeBookmark(paperId) {
        return await this.request(`${API_BASE}/bookmarks/${paperId}`, {
            method: 'DELETE'
        });
    }

    /**
     * Get all bookmarked papers
     */
    async getBookmarks() {
        return await this.request(`${API_BASE}/bookmarks/`);
    }
}

// Export singleton instance
const api = new ApiClient();
