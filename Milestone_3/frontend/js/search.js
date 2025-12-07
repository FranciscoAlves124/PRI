// filepath: Milestone_3/frontend/js/search.js
export class SearchManager {
    constructor(api) {
        this.api = api;
    }

    /**
     * Basic search - simple query
     */
    async basicSearch(query, filters = {}) {
        const params = {
            q: query,
            defType: 'edismax',
            qf: 'primaryTitle^2 description^3 genres^2 top_3_cast',
            rows: 100,
            wt: 'json'
        };

        // Add filters
        const fq = this.buildFilterQuery(filters);
        if (fq.length > 0) {
            params.fq = fq;
        }

        // Add sorting
        if (filters.sortBy && filters.sortBy !== 'relevance') {
            params.sort = this.getSortString(filters.sortBy);
        }

        return await this.api.queryBasic(params);
    }

    /**
     * Intermediate search - with synonyms, stopwords, custom analyzers
     */
    async intermediateSearch(query, filters = {}) {
        const params = {
            q: query,
            defType: 'edismax',
            qf: 'primaryTitle^2 description^3 genres^2 top_3_cast',
            rows: 100,
            wt: 'json'
        };

        // Add filters
        const fq = this.buildFilterQuery(filters);
        if (fq.length > 0) {
            params.fq = fq;
        }

        // Add sorting
        if (filters.sortBy && filters.sortBy !== 'relevance') {
            params.sort = this.getSortString(filters.sortBy);
        }

        return await this.api.queryIntermediate(params);
    }

    /**
     * Semantic search - using vector embeddings
     */
    async semanticSearch(query, filters = {}) {
        // Get embedding for the query
        const embedding = await this.api.getEmbedding(query);
        
        const params = {
            q: `{!knn f=vector topK=100}${JSON.stringify(embedding)}`,
            rows: 100,
            fl: 'tconst,primaryTitle,description,genres,titleType,startYear,averageRating,score',
            wt: 'json'
        };

        // Add filters
        const fq = this.buildFilterQuery(filters);
        if (fq.length > 0) {
            params.fq = fq;
        }

        return await this.api.querySemantic(params);
    }

    /**
     * Build filter query array from filters object
     */
    buildFilterQuery(filters) {
        const fq = [];

        if (filters.type) {
            fq.push(`titleType:${filters.type}`);
        }

        if (filters.genres && filters.genres.length > 0) {
            const genreQuery = filters.genres.map(g => `genres:*${g}*`).join(' OR ');
            fq.push(`(${genreQuery})`);
        }

        if (filters.yearFrom || filters.yearTo) {
            const from = filters.yearFrom || '*';
            const to = filters.yearTo || '*';
            fq.push(`startYear:[${from} TO ${to}]`);
        }

        if (filters.minRating) {
            fq.push(`averageRating:[${filters.minRating} TO *]`);
        }

        return fq;
    }

    /**
     * Get sort string from sort option
     */
    getSortString(sortBy) {
        switch(sortBy) {
            case 'rating_desc':
                return 'averageRating desc';
            case 'rating_asc':
                return 'averageRating asc';
            case 'year_desc':
                return 'startYear desc';
            case 'year_asc':
                return 'startYear asc';
            default:
                return 'score desc';
        }
    }
}