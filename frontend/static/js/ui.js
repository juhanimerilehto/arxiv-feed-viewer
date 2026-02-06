/**
 * UI Rendering Functions
 */

const ui = {
    /**
     * Format date to readable string
     */
    formatDate(dateString) {
        const date = new Date(dateString);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    },

    /**
     * Render a paper in the three-column layout
     */
    renderPaper(paper) {
        // Left column: Metadata
        document.getElementById('paperTitle').textContent = paper.title;
        document.getElementById('paperArxivId').textContent = paper.arxiv_id;
        document.getElementById('paperDate').textContent = this.formatDate(paper.published_date);
        document.getElementById('paperCategory').textContent = paper.primary_category;

        // Authors
        const authorsContainer = document.getElementById('paperAuthors');
        authorsContainer.innerHTML = paper.authors
            .map(author => `<div class="author">${author}</div>`)
            .join('');

        // PDF link
        const pdfLink = document.getElementById('pdfLink');
        pdfLink.href = paper.pdf_url;

        // Bookmark button
        const bookmarkBtn = document.getElementById('bookmarkBtn');
        if (paper.is_bookmarked) {
            bookmarkBtn.textContent = '★ BOOKMARKED';
            bookmarkBtn.classList.add('bookmarked');
        } else {
            bookmarkBtn.textContent = '☆ BOOKMARK';
            bookmarkBtn.classList.remove('bookmarked');
        }

        // Center column: Abstract
        document.getElementById('paperAbstract').textContent = paper.abstract;

        // Right column: Grok insights
        const grokContainer = document.getElementById('grokAnalysis');
        if (paper.grok_analysis && paper.grok_analysis.key_points) {
            const insights = paper.grok_analysis.key_points
                .map(point => `<div class="insight">${point}</div>`)
                .join('');
            grokContainer.innerHTML = insights;
        } else {
            grokContainer.innerHTML = '<div class="no-analysis">[ NO ANALYSIS AVAILABLE ]</div>';
        }
    },

    /**
     * Update page indicator in footer
     */
    updatePageIndicator(current, total) {
        document.getElementById('currentPage').textContent = current;
        document.getElementById('totalPages').textContent = total;

        // Update button states
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');

        prevBtn.disabled = current <= 1;
        nextBtn.disabled = current >= total;
    },

    /**
     * Show loading spinner
     */
    showLoading() {
        document.getElementById('loadingSpinner').classList.remove('hidden');
        document.getElementById('paperView').classList.add('hidden');
        document.getElementById('noResults').classList.add('hidden');
    },

    /**
     * Show paper view
     */
    showPaper() {
        document.getElementById('loadingSpinner').classList.add('hidden');
        document.getElementById('paperView').classList.remove('hidden');
        document.getElementById('noResults').classList.add('hidden');
    },

    /**
     * Show no results message
     */
    showNoResults() {
        document.getElementById('loadingSpinner').classList.add('hidden');
        document.getElementById('paperView').classList.add('hidden');
        document.getElementById('noResults').classList.remove('hidden');
    },

    /**
     * Show error message (using no results area)
     */
    showError(message) {
        const noResultsEl = document.getElementById('noResults');
        noResultsEl.innerHTML = `
            <pre>
╔═══════════════════════════════════╗
║                                   ║
║     ERROR                         ║
║                                   ║
║     ${message.padEnd(30)}║
║                                   ║
╚═══════════════════════════════════╝
            </pre>
        `;
        this.showNoResults();
    }
};
