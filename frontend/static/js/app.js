/**
 * Main Application Logic
 * Handles state management, event listeners, and navigation
 */

class App {
    constructor() {
        // State
        this.papers = [];
        this.currentIndex = 0;
        this.isSearchMode = false;
        this.isBookmarkMode = false;

        // Initialize
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadPapers();
    }

    /**
     * Setup all event listeners
     */
    setupEventListeners() {
        // Search
        document.getElementById('searchBtn').addEventListener('click', () => this.handleSearch());
        document.getElementById('searchInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleSearch();
        });

        // Clear search
        document.getElementById('clearSearchBtn').addEventListener('click', () => this.handleClearSearch());

        // Bookmarks view
        document.getElementById('bookmarksBtn').addEventListener('click', () => this.handleBookmarksToggle());

        // Navigation
        document.getElementById('prevBtn').addEventListener('click', () => this.navigatePrev());
        document.getElementById('nextBtn').addEventListener('click', () => this.navigateNext());

        // Bookmark toggle
        document.getElementById('bookmarkBtn').addEventListener('click', () => this.handleBookmarkToggle());

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.target.tagName === 'INPUT') return; // Don't interfere with input

            switch(e.key) {
                case 'ArrowLeft':
                    this.navigatePrev();
                    break;
                case 'ArrowRight':
                    this.navigateNext();
                    break;
            }
        });
    }

    /**
     * Load papers from API
     */
    async loadPapers(bookmarked = false) {
        try {
            ui.showLoading();

            const response = await api.getPapers(100, 0, bookmarked); // Load first 100 papers
            this.papers = response.papers;

            if (this.papers.length === 0) {
                ui.showNoResults();
                return;
            }

            this.currentIndex = 0;
            this.isBookmarkMode = bookmarked;
            await this.displayCurrentPaper();

        } catch (error) {
            console.error('Failed to load papers:', error);
            ui.showError('Failed to load papers');
        }
    }

    /**
     * Search papers by keyword
     */
    async handleSearch() {
        const query = document.getElementById('searchInput').value.trim();

        if (!query || query.length < 2) {
            alert('Please enter at least 2 characters to search');
            return;
        }

        try {
            ui.showLoading();

            this.papers = await api.searchPapers(query, 100);

            if (this.papers.length === 0) {
                ui.showNoResults();
                return;
            }

            this.currentIndex = 0;
            this.isSearchMode = true;
            this.isBookmarkMode = false;
            await this.displayCurrentPaper();

        } catch (error) {
            console.error('Search failed:', error);
            ui.showError('Search failed');
        }
    }

    /**
     * Clear search and reload all papers
     */
    async handleClearSearch() {
        document.getElementById('searchInput').value = '';
        this.isSearchMode = false;
        this.isBookmarkMode = false;
        await this.loadPapers();
    }

    /**
     * Toggle bookmarks view
     */
    async handleBookmarksToggle() {
        if (this.isBookmarkMode) {
            // Already in bookmark mode, go back to all papers
            await this.handleClearSearch();
        } else {
            // Switch to bookmark mode
            try {
                ui.showLoading();

                this.papers = await api.getBookmarks();

                if (this.papers.length === 0) {
                    ui.showNoResults();
                    return;
                }

                this.currentIndex = 0;
                this.isSearchMode = false;
                this.isBookmarkMode = true;
                await this.displayCurrentPaper();

            } catch (error) {
                console.error('Failed to load bookmarks:', error);
                ui.showError('Failed to load bookmarks');
            }
        }
    }

    /**
     * Display current paper with full details
     */
    async displayCurrentPaper() {
        if (this.papers.length === 0) {
            ui.showNoResults();
            return;
        }

        try {
            const paperSummary = this.papers[this.currentIndex];

            // Fetch full paper details including Grok analysis
            const paper = await api.getPaper(paperSummary.id);

            ui.renderPaper(paper);
            ui.updatePageIndicator(this.currentIndex + 1, this.papers.length);
            ui.showPaper();

        } catch (error) {
            console.error('Failed to display paper:', error);
            ui.showError('Failed to load paper details');
        }
    }

    /**
     * Navigate to previous paper
     */
    navigatePrev() {
        if (this.currentIndex > 0) {
            this.currentIndex--;
            this.displayCurrentPaper();
        }
    }

    /**
     * Navigate to next paper
     */
    navigateNext() {
        if (this.currentIndex < this.papers.length - 1) {
            this.currentIndex++;
            this.displayCurrentPaper();
        }
    }

    /**
     * Toggle bookmark for current paper
     */
    async handleBookmarkToggle() {
        if (this.papers.length === 0) return;

        const paper = this.papers[this.currentIndex];

        try {
            if (paper.is_bookmarked) {
                // Remove bookmark
                await api.removeBookmark(paper.id);
                paper.is_bookmarked = false;
                console.log('Bookmark removed');
            } else {
                // Add bookmark
                await api.addBookmark(paper.id);
                paper.is_bookmarked = true;
                console.log('Bookmark added');
            }

            // Update UI
            await this.displayCurrentPaper();

        } catch (error) {
            console.error('Bookmark toggle failed:', error);
            alert('Failed to update bookmark');
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});
