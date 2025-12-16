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
     * Semantic search - using vector embeddings (description only)
     */
    async semanticSearch(query, filters = {}) {
        // Get embedding for the query
        const embedding = await this.api.getEmbedding(query);
        
        const params = {
            q: `{!knn f=vector topK=100}${JSON.stringify(embedding)}`,
            rows: 100,
            fl: 'tconst,primaryTitle,description,genres,titleType,startYear,averageRating,score,poster_url',
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
     * Semantic search using reviews embeddings only
     */
    async semanticSearchReviews(query, filters = {}) {
        const embedding = await this.api.getEmbedding(query);
        
        const params = {
            q: `{!knn f=reviews_vector topK=100}${JSON.stringify(embedding)}`,
            rows: 100,
            fl: 'tconst,primaryTitle,description,genres,titleType,startYear,averageRating,score',
            wt: 'json'
        };

        const fq = this.buildFilterQuery(filters);
        if (fq.length > 0) {
            params.fq = fq;
        }

        return await this.api.querySemantic(params);
    }

    /**
     * Hybrid semantic search - combines description and reviews vectors
     * Uses reranking to merge results from both vector searches
     */
    async semanticSearchHybrid(query, filters = {}, descWeight = 0.6, reviewsWeight = 0.4) {
        const embedding = await this.api.getEmbedding(query);
        const embeddingStr = JSON.stringify(embedding);
        
        // Use Solr's query-time boosting with multiple KNN queries
        // This performs both searches and combines scores
        const params = {
            q: '*:*',
            rq: `{!rerank reRankQuery=$rqq reRankDocs=200 reRankWeight=1}`,
            rqq: `(_query_:"{!knn f=vector topK=100}${embeddingStr}")^${descWeight} OR (_query_:"{!knn f=reviews_vector topK=100}${embeddingStr}")^${reviewsWeight}`,
            rows: 100,
            fl: 'tconst,primaryTitle,description,genres,titleType,startYear,averageRating,score',
            wt: 'json'
        };

        const fq = this.buildFilterQuery(filters);
        if (fq.length > 0) {
            params.fq = fq;
        }

        return await this.api.querySemantic(params);
    }

    /**
     * Merge results from two semantic searches with weighted scoring
     */
    mergeSemanticResults(descResults, reviewResults, descWeight, reviewsWeight) {
        const scoreMap = new Map();
        const docMap = new Map();

        // Process description results
        const descDocs = descResults?.response?.docs || [];
        const maxDescScore = descDocs.length > 0 ? descDocs[0].score : 1;
        
        descDocs.forEach((doc, idx) => {
            const normalizedScore = doc.score / maxDescScore;
            scoreMap.set(doc.tconst, (scoreMap.get(doc.tconst) || 0) + normalizedScore * descWeight);
            docMap.set(doc.tconst, doc);
        });

        // Process review results
        const reviewDocs = reviewResults?.response?.docs || [];
        const maxReviewScore = reviewDocs.length > 0 ? reviewDocs[0].score : 1;
        
        reviewDocs.forEach((doc, idx) => {
            const normalizedScore = doc.score / maxReviewScore;
            scoreMap.set(doc.tconst, (scoreMap.get(doc.tconst) || 0) + normalizedScore * reviewsWeight);
            if (!docMap.has(doc.tconst)) {
                docMap.set(doc.tconst, doc);
            }
        });

        // Sort by combined score and rebuild response
        const sortedDocs = Array.from(scoreMap.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, 100)
            .map(([tconst, score]) => {
                const doc = docMap.get(tconst);
                return { ...doc, score: score };
            });

        return {
            response: {
                numFound: sortedDocs.length,
                docs: sortedDocs
            }
        };
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

    /**
     * More Like This - find similar documents based on content
     */
    async moreLikeThis(tconst, core = 'media_intermediate') {
        const params = {
            q: `tconst:${tconst}`,
            mlt: 'true',
            'mlt.fl': 'description,genres,top_3_cast',
            'mlt.mindf': 1,
            'mlt.mintf': 1,
            'mlt.count': 12,
            fl: 'tconst,primaryTitle,description,genres,titleType,startYear,averageRating,score,poster_url,top_3_cast',
            rows: 12,
            wt: 'json'
        };

        return await this.api.moreLikeThis(core, params);
    }
}