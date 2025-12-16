// filepath: Milestone_3/frontend/js/api.js
export class SolrAPI {
    constructor() {
        // Use proxy server to avoid CORS issues
        this.proxyURL = 'http://localhost:5000/api/solr';
        this.basicCore = 'media_basic';
        this.intermediateCore = 'media_intermediate';
        this.semanticCore = 'semantic_core';
    }

    /**
     * Query basic Solr core (schemaless)
     */
    async queryBasic(params) {
        const core = this.basicCore;
        return this.query(core, params);
    }

    /**
     * Query intermediate Solr core (with custom schema, synonyms, stopwords)
     */
    async queryIntermediate(params) {
        const core = this.intermediateCore;
        return this.query(core, params);
    }

    /**
     * Query semantic Solr core (with vector embeddings)
     */
    async querySemantic(params) {
        const core = this.semanticCore;
        return this.query(core, params);
    }

    /**
     * Generic query method
     */
    async query(core, params) {
        const url = `${this.proxyURL}/${core}/select`;
        
        try {
            console.log('Querying Solr:', { core, params });
            
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(params)
            });

            if (!response.ok) {
                let errorMsg = `HTTP error! status: ${response.status}`;
                try {
                    const errorData = await response.json();
                    console.error('Solr error response:', errorData);
                    errorMsg = errorData.error || errorMsg;
                } catch (e) {
                    const errorText = await response.text();
                    console.error('Solr error text:', errorText);
                    errorMsg = errorText || errorMsg;
                }
                throw new Error(errorMsg);
            }

            const data = await response.json();
            console.log('Solr response:', data);
            return data.response;
            
        } catch (error) {
            console.error('Solr query error:', error);
            throw new Error(error.message || 'Failed to fetch results from Solr');
        }
    }

    /**
     * More Like This query
     */
    async moreLikeThis(core, params) {
        const url = `${this.proxyURL}/${core}/mlt`;
        
        try {
            console.log('MLT Query:', { core, params });
            
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(params)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('MLT response:', data);

            if (data.moreLikeThis) {
                // moreLikeThis is an object with document IDs as keys
                // Each key contains {numFound, docs} for similar documents
                const mltKeys = Object.keys(data.moreLikeThis);
                if (mltKeys.length > 0) {
                    const firstKey = mltKeys[0];
                    const mltData = data.moreLikeThis[firstKey];
                    return {
                        numFound: mltData.numFound || mltData.docs?.length || 0,
                        docs: mltData.docs || []
                    };
                }
            }

            return data.response;
            
        } catch (error) {
            console.error('MLT query error:', error);
            throw new Error(error.message || 'Failed to fetch similar results');
        }
    }

    /**
     * Get semantic embedding for a query
     */
    async getEmbedding(text) {
        try {
            // Call your Python backend to get embeddings
            const response = await fetch('http://localhost:5000/api/embed', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text })
            });

            if (!response.ok) {
                throw new Error('Failed to get embedding');
            }

            const data = await response.json();
            return data.embedding;
            
        } catch (error) {
            console.error('Embedding error:', error);
            throw error;
        }
    }
}