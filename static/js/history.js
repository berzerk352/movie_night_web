// History page functionality

let allRolls = [];
let currentRollId = null;

// Load initial data
document.addEventListener('DOMContentLoaded', async () => {
    await loadSeasons();
    await loadHistory();
    setupEventListeners();
});

// Load seasons for filter
async function loadSeasons() {
    try {
        const seasons = await apiCall('/api/seasons');
        const seasonFilter = document.getElementById('seasonFilter');
        
        seasons.forEach(season => {
            const option = document.createElement('option');
            option.value = season.id;
            option.textContent = season.name;
            if (season.is_active) {
                option.textContent += ' (Active)';
            }
            seasonFilter.appendChild(option);
        });
        
    } catch (error) {
        showNotification('Error loading seasons: ' + error.message, 'error');
    }
}

// Load history
async function loadHistory(seasonId = null) {
    try {
        const endpoint = seasonId ? `/api/rolls?season_id=${seasonId}` : '/api/rolls';
        allRolls = await apiCall(endpoint);
        
        displayHistory(allRolls);
        
    } catch (error) {
        showNotification('Error loading history: ' + error.message, 'error');
    }
}

// Display history
function displayHistory(rolls) {
    const historyList = document.getElementById('historyList');
    
    if (rolls.length === 0) {
        historyList.innerHTML = '<p>No rolls found.</p>';
        return;
    }
    
    historyList.innerHTML = rolls.map(roll => `
        <div class="history-item" data-roll-id="${roll.id}">
            <h3>${roll.movie_title}</h3>
            <p><strong>Participant:</strong> ${roll.participant_name}</p>
            <p><strong>Date:</strong> ${formatDate(roll.roll_date)}</p>
            ${roll.tmdb_data ? '<p>✓ TMDB data available</p>' : ''}
        </div>
    `).join('');
    
    // Add click handlers
    document.querySelectorAll('.history-item').forEach(item => {
        item.addEventListener('click', () => {
            const rollId = parseInt(item.dataset.rollId);
            showRollDetails(rollId);
        });
    });
}

// Show roll details in modal
async function showRollDetails(rollId) {
    try {
        const roll = await apiCall(`/api/rolls/${rollId}`);
        currentRollId = rollId;
        
        const modal = document.getElementById('rollModal');
        const detailsDiv = document.getElementById('rollDetails');
        
        let detailsHtml = `
            <p><strong>Movie:</strong> ${roll.movie_title}</p>
            <p><strong>Participant:</strong> ${roll.participant_name}</p>
            <p><strong>Date:</strong> ${formatDate(roll.roll_date)}</p>
        `;
        
        if (roll.tmdb_data) {
            const data = roll.tmdb_data;
            detailsHtml += `
                <div class="movie-details">
                    ${data.poster_url ? `<img src="${data.poster_url}" alt="${data.title} poster">` : ''}
                    <h3>${data.title}</h3>
                    ${data.release_date ? `<p><strong>Release Date:</strong> ${data.release_date}</p>` : ''}
                    ${data.runtime ? `<p><strong>Runtime:</strong> ${data.runtime} minutes</p>` : ''}
                    ${data.genres && data.genres.length > 0 ? `<p><strong>Genres:</strong> ${data.genres.join(', ')}</p>` : ''}
                    ${data.vote_average ? `<p><strong>Rating:</strong> ${data.vote_average}/10</p>` : ''}
                    ${data.overview ? `<p><strong>Overview:</strong> ${data.overview}</p>` : ''}
                </div>
            `;
        } else {
            detailsHtml += '<p><em>No TMDB data available. Click "Fetch TMDB Data" to retrieve it.</em></p>';
        }
        
        if (roll.notes) {
            detailsHtml += `<p><strong>Notes:</strong> ${roll.notes}</p>`;
        }
        
        detailsDiv.innerHTML = detailsHtml;
        modal.style.display = 'flex';
        
    } catch (error) {
        showNotification('Error loading roll details: ' + error.message, 'error');
    }
}

// Setup event listeners
function setupEventListeners() {
    // Season filter
    document.getElementById('seasonFilter').addEventListener('change', (e) => {
        const seasonId = e.target.value ? parseInt(e.target.value) : null;
        loadHistory(seasonId);
    });
    
    // Modal close
    const modal = document.getElementById('rollModal');
    const closeBtn = modal.querySelector('.close');
    
    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    // Delete roll button
    document.getElementById('deleteRollButton').addEventListener('click', deleteRoll);
    
    // Enrich roll button
    document.getElementById('enrichRollButton').addEventListener('click', enrichRoll);
}

// Delete roll
async function deleteRoll() {
    if (!currentRollId) return;
    
    if (!confirm('Are you sure you want to delete this roll?')) {
        return;
    }
    
    try {
        await apiCall(`/api/rolls/${currentRollId}`, {
            method: 'DELETE'
        });
        
        document.getElementById('rollModal').style.display = 'none';
        
        // Reload history
        const seasonFilter = document.getElementById('seasonFilter');
        const seasonId = seasonFilter.value ? parseInt(seasonFilter.value) : null;
        await loadHistory(seasonId);
        
        showNotification('Roll deleted successfully!', 'success');
        
    } catch (error) {
        showNotification('Error deleting roll: ' + error.message, 'error');
    }
}

// Enrich roll with TMDB data
async function enrichRoll() {
    if (!currentRollId) return;
    
    const enrichButton = document.getElementById('enrichRollButton');
    enrichButton.disabled = true;
    enrichButton.textContent = 'Fetching...';
    
    try {
        await apiCall(`/api/rolls/${currentRollId}/enrich`, {
            method: 'POST'
        });
        
        // Reload roll details
        await showRollDetails(currentRollId);
        
        // Reload history to show updated indicator
        const seasonFilter = document.getElementById('seasonFilter');
        const seasonId = seasonFilter.value ? parseInt(seasonFilter.value) : null;
        await loadHistory(seasonId);
        
        showNotification('Movie details fetched successfully!', 'success');
        
    } catch (error) {
        showNotification('Error fetching movie details: ' + error.message, 'error');
    } finally {
        enrichButton.disabled = false;
        enrichButton.textContent = 'Fetch TMDB Data';
    }
}
