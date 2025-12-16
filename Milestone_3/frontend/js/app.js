// filepath: Milestone_3/frontend/js/app.js
import { SolrAPI } from './api.js';
import { SearchManager } from './search.js';
import { renderResultCard, renderDetailModal } from './utils.js';

class MovieSearchApp {
    constructor() {
        this.api = new SolrAPI();
        this.searchManager = new SearchManager(this.api);
        this.currentMode = 'basic'; // basic, intermediate, semantic
        this.currentResults = [];
        this.currentPage = 1;
        this.resultsPerPage = 12;
        
        this.initializeElements();
        this.attachEventListeners();
    }

    initializeElements() {
        // Search elements
        this.searchInput = document.getElementById('searchInput');
        this.searchBtn = document.getElementById('searchBtn');
        this.toggleFiltersBtn = document.getElementById('toggleFiltersBtn');
        this.filtersPanel = document.getElementById('filtersPanel');
        this.applyFiltersBtn = document.getElementById('applyFiltersBtn');
        
        // Mode buttons
        this.basicSearchBtn = document.getElementById('basicSearchBtn');
        this.intermediateSearchBtn = document.getElementById('intermediateSearchBtn');
        this.semanticSearchBtn = document.getElementById('semanticSearchBtn');
        this.semanticReviewsBtn = document.getElementById('semanticReviewsBtn');
        this.semanticCombinedBtn = document.getElementById('semanticCombinedBtn');
        this.currentModeSpan = document.getElementById('currentMode');
        
        // Results elements
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.errorMessage = document.getElementById('errorMessage');
        this.errorText = document.getElementById('errorText');
        this.resultsInfo = document.getElementById('resultsInfo');
        this.resultCount = document.getElementById('resultCount');
        this.queryTime = document.getElementById('queryTime');
        this.resultsGrid = document.getElementById('resultsGrid');
        
        // Pagination
        this.pagination = document.getElementById('pagination');
        this.prevPageBtn = document.getElementById('prevPage');
        this.nextPageBtn = document.getElementById('nextPage');
        this.pageInfo = document.getElementById('pageInfo');
        
        // Modal
        this.detailModal = document.getElementById('detailModal');
        this.modalBody = document.getElementById('modalBody');
        this.closeModal = this.detailModal.querySelector('.close');
    }

    attachEventListeners() {
        // Search
        this.searchBtn.addEventListener('click', () => this.performSearch());
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.performSearch();
        });
        
        // Filters
        this.toggleFiltersBtn.addEventListener('click', () => this.toggleFilters());
        this.applyFiltersBtn.addEventListener('click', () => this.performSearch());
        
        // Mode switching
        this.basicSearchBtn.addEventListener('click', () => this.switchMode('basic'));
        this.intermediateSearchBtn.addEventListener('click', () => this.switchMode('intermediate'));
        this.semanticSearchBtn.addEventListener('click', () => this.switchMode('semantic'));
        this.semanticReviewsBtn.addEventListener('click', () => this.switchMode('semantic-reviews'));
        this.semanticCombinedBtn.addEventListener('click', () => this.switchMode('semantic-combined'));
        
        // Pagination
        this.prevPageBtn.addEventListener('click', () => this.changePage(-1));
        this.nextPageBtn.addEventListener('click', () => this.changePage(1));
        
        // Modal
        this.closeModal.addEventListener('click', () => this.hideModal());
        window.addEventListener('click', (e) => {
            if (e.target === this.detailModal) this.hideModal();
        });
    }

    toggleFilters() {
        this.filtersPanel.classList.toggle('hidden');
    }

    switchMode(mode) {
        this.currentMode = mode;
        
        // Update UI
        [this.basicSearchBtn, this.intermediateSearchBtn, this.semanticSearchBtn, 
         this.semanticReviewsBtn, this.semanticCombinedBtn].forEach(btn => {
            btn.classList.remove('active');
        });
        
        if (mode === 'basic') {
            this.basicSearchBtn.classList.add('active');
            this.currentModeSpan.textContent = 'Basic Search';
            this.searchInput.placeholder = 'Search for movies and series...';
        } else if (mode === 'intermediate') {
            this.intermediateSearchBtn.classList.add('active');
            this.currentModeSpan.textContent = 'Intermediate Search';
            this.searchInput.placeholder = 'Advanced search with synonyms and filters...';
        } else if (mode === 'semantic') {
            this.semanticSearchBtn.classList.add('active');
            this.currentModeSpan.textContent = 'Semantic Search (Description)';
            this.searchInput.placeholder = 'Natural language search using descriptions...';
        } else if (mode === 'semantic-reviews') {
            this.semanticReviewsBtn.classList.add('active');
            this.currentModeSpan.textContent = 'Semantic Search (Reviews)';
            this.searchInput.placeholder = 'Natural language search using reviews...';
        } else if (mode === 'semantic-combined') {
            this.semanticCombinedBtn.classList.add('active');
            this.currentModeSpan.textContent = 'Semantic Search (Combined)';
            this.searchInput.placeholder = 'Natural language search using descriptions + reviews...';
        }
    }

    getFilters() {
        const typeFilter = document.getElementById('typeFilter').value;
        const genreFilter = Array.from(document.getElementById('genreFilter').selectedOptions).map(opt => opt.value);
        const yearFrom = document.getElementById('yearFrom').value;
        const yearTo = document.getElementById('yearTo').value;
        const minRating = document.getElementById('minRating').value;
        const sortBy = document.getElementById('sortBy').value;

        return {
            type: typeFilter,
            genres: genreFilter,
            yearFrom: yearFrom ? parseInt(yearFrom) : null,
            yearTo: yearTo ? parseInt(yearTo) : null,
            minRating: minRating ? parseFloat(minRating) : null,
            sortBy: sortBy
        };
    }

    async performSearch() {
        const query = this.searchInput.value.trim();
        
        if (!query) {
            this.showError('Please enter a search query');
            return;
        }

        this.showLoading();
        this.hideError();
        this.hideResults();

        try {
            const filters = this.getFilters();
            const startTime = performance.now();
            
            let results;
            if (this.currentMode === 'basic') {
                results = await this.searchManager.basicSearch(query, filters);
            } else if (this.currentMode === 'intermediate') {
                results = await this.searchManager.intermediateSearch(query, filters);
            } else if (this.currentMode === 'semantic') {
                results = await this.searchManager.semanticSearch(query, filters);
            } else if (this.currentMode === 'semantic-reviews') {
                results = await this.searchManager.semanticSearchReviews(query, filters);
            } else if (this.currentMode === 'semantic-combined') {
                results = await this.searchManager.semanticSearchCombined(query, filters);
            }
            
            const endTime = performance.now();
            const queryTime = Math.round(endTime - startTime);
            
            this.currentResults = results.docs || [];
            this.currentPage = 1;
            
            this.hideLoading();
            this.displayResults(queryTime);
            
        } catch (error) {
            console.error('Search error:', error);
            this.hideLoading();
            this.showError(error.message || 'An error occurred while searching');
        }
    }

    showLoading() {
        this.loadingIndicator.classList.remove('hidden');
    }

    hideLoading() {
        this.loadingIndicator.classList.add('hidden');
    }

    showError(message) {
        this.errorText.textContent = message;
        this.errorMessage.classList.remove('hidden');
    }

    hideError() {
        this.errorMessage.classList.add('hidden');
    }

    hideResults() {
        this.resultsInfo.classList.add('hidden');
        this.resultsGrid.innerHTML = '';
        this.pagination.classList.add('hidden');
    }

    displayResults(queryTime) {
        if (this.currentResults.length === 0) {
            this.showError('No results found. Try a different search query.');
            return;
        }

        // Show results info
        this.resultCount.textContent = this.currentResults.length;
        this.queryTime.textContent = queryTime;
        this.resultsInfo.classList.remove('hidden');

        // Display paginated results
        this.displayPage();
    }

    displayPage() {
        const startIndex = (this.currentPage - 1) * this.resultsPerPage;
        const endIndex = startIndex + this.resultsPerPage;
        const pageResults = this.currentResults.slice(startIndex, endIndex);

        // Clear grid
        this.resultsGrid.innerHTML = '';

        // Render result cards
        pageResults.forEach(doc => {
            const card = renderResultCard(doc, this.currentMode);
            card.addEventListener('click', () => this.showDetail(doc));
            this.resultsGrid.appendChild(card);
        });

        // Update pagination
        const totalPages = Math.ceil(this.currentResults.length / this.resultsPerPage);
        this.pageInfo.textContent = `Page ${this.currentPage} of ${totalPages}`;
        this.prevPageBtn.disabled = this.currentPage === 1;
        this.nextPageBtn.disabled = this.currentPage === totalPages;
        this.pagination.classList.remove('hidden');
    }

    changePage(delta) {
        this.currentPage += delta;
        this.displayPage();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    showDetail(doc) {
        const content = renderDetailModal(doc, this.currentMode);
        this.modalBody.innerHTML = content;
        this.detailModal.classList.remove('hidden');
    }

    hideModal() {
        this.detailModal.classList.add('hidden');
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new MovieSearchApp();
});