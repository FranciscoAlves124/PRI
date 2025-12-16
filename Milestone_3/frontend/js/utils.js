// filepath: Milestone_3/frontend/js/utils.js

/**
 * Render a result card for a movie/series document
 */
export function renderResultCard(doc, mode) {
    const card = document.createElement('div');
    card.className = 'result-card';
    
    const title = getFieldValue(doc.primaryTitle);
    const type = getFieldValue(doc.titleType);
    const year = getFieldValue(doc.startYear);
    const rating = getFieldValue(doc.averageRating);
    const description = getFieldValue(doc.description);
    const genres = parseGenres(doc.genres);
    const cast = getArrayField(doc.top_3_cast);
    const poster_url = getFieldValue(doc.poster_url);
    const score = doc.score;

    console.log("Poster_Url : " + doc.poster_url); // should log the URL

    const tconst = getFieldValue(doc.tconst);

    card.innerHTML = `
        <div class="result-card-image">
            ${
                poster_url && poster_url !== "N/A"
                    ? `<img 
                        src="${escapeHtml(poster_url)}"
                        alt="${escapeHtml(title)} poster"
                        loading="lazy"
                        onload="console.log('Poster loaded:', '${escapeHtml(title)}')"
                        onerror="console.warn('Poster failed to load:', '${escapeHtml(title)}', '${escapeHtml(poster_url)}')"
                    >`
                    : `<i class="fas fa-film"></i>`
            }
        </div>
        <div class="result-card-content">
            <h3 class="result-card-title">${escapeHtml(title)}</h3>
            <div class="result-card-meta">
                ${type ? `<span class="meta-badge type">${escapeHtml(type)}</span>` : ''}
                ${year ? `<span class="meta-badge year">${year}</span>` : ''}
                ${rating ? `<span class="meta-badge rating">★ ${Number(rating).toFixed(1)}</span>` : ''}
            </div>
            ${description ? `<p class="result-card-description">${escapeHtml(truncate(description, 150))}</p>` : ''}
            ${genres.length > 0 ? `
                <div class="result-card-genres">
                    ${genres.slice(0, 3).map(g => `<span class="genre-tag">${escapeHtml(g)}</span>`).join('')}
                </div>
            ` : ''}
        </div>
        <div class="result-card-footer">
            ${cast.length > 0 ? `
                <div class="result-card-cast">
                    <i class="fas fa-user"></i>
                    ${escapeHtml(cast[0].split(' - ')[0])}
                </div>
            ` : '<div></div>'}
            <div class="result-card-actions">
                ${mode === 'semantic' && score ? `
                    <div class="similarity-score">
                        <i class="fas fa-brain"></i>
                        ${(score * 100).toFixed(0)}%
                    </div>
                ` : ''}
                <button class="btn-similar" data-tconst="${escapeHtml(tconst)}" title="Find Similar">
                    <i class="fas fa-magic"></i> Similar
                </button>
            </div>
        </div>
    `;

    return card;
}

/**
 * Render detail modal content
 */
export function renderDetailModal(doc, mode) {
    const title = getFieldValue(doc.primaryTitle);
    const type = getFieldValue(doc.titleType);
    const year = getFieldValue(doc.startYear);
    const endYear = getFieldValue(doc.endYear);
    const rating = getFieldValue(doc.averageRating);
    const numVotes = getFieldValue(doc.numVotes);
    const description = getFieldValue(doc.description);
    const genres = parseGenres(doc.genres);
    const cast = getArrayField(doc.top_3_cast);
    const runtime = getFieldValue(doc.runtimeMinutes);
    const score = doc.score;

    return `
        <h2 class="modal-detail-title">${escapeHtml(title)}</h2>
        
        <div class="modal-detail-meta">
            ${type ? `<span class="meta-badge type">${escapeHtml(type)}</span>` : ''}
            ${year ? `<span class="meta-badge year">${year}${endYear && endYear !== year ? ` - ${endYear}` : ''}</span>` : ''}
            ${rating ? `<span class="meta-badge rating">★ ${Number(rating).toFixed(1)}/10</span>` : ''}
            ${numVotes ? `<span class="meta-badge">${formatNumber(numVotes)} votes</span>` : ''}
            ${runtime ? `<span class="meta-badge">${runtime} min</span>` : ''}
            ${mode === 'semantic' && score ? `
                <span class="similarity-score">
                    <i class="fas fa-brain"></i>
                    Similarity: ${(score * 100).toFixed(1)}%
                </span>
            ` : ''}
        </div>

        ${description ? `
            <div class="modal-section">
                <h3>Description</h3>
                <p>${escapeHtml(description)}</p>
            </div>
        ` : ''}

        ${genres.length > 0 ? `
            <div class="modal-section">
                <h3>Genres</h3>
                <div class="result-card-genres">
                    ${genres.map(g => `<span class="genre-tag">${escapeHtml(g)}</span>`).join('')}
                </div>
            </div>
        ` : ''}

        ${cast.length > 0 ? `
            <div class="modal-section">
                <h3>Top Cast</h3>
                <div class="cast-list">
                    ${cast.map(c => `
                        <div class="cast-item">
                            ${escapeHtml(c)}
                        </div>
                    `).join('')}
                </div>
            </div>
        ` : ''}
    `;
}

/**
 * Get field value (handles both arrays and scalars)
 */
function getFieldValue(field) {
    if (Array.isArray(field)) {
        return field[0] || '';
    }
    return field || '';
}

/**
 * Get array field (ensures always returns array)
 */
function getArrayField(field) {
    if (Array.isArray(field)) {
        return field;
    }
    if (field) {
        return [field];
    }
    return [];
}

/**
 * Parse genres (handles "Comedy,Drama" format)
 */
function parseGenres(genres) {
    const genreArray = getArrayField(genres);
    // Split comma-separated genres
    return genreArray.flatMap(g => g.split(',').map(x => x.trim())).filter(Boolean);
}

/**
 * Truncate text to specified length
 */
function truncate(text, maxLength) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength).trim() + '...';
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Format number with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}