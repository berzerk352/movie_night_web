// Roll page functionality

let currentSeason = null;
let currentRollId = null;

// Load initial data
document.addEventListener('DOMContentLoaded', async () => {
    await loadActiveSeason();
    await loadEligibleParticipants();
    await loadSeasonRoster();
    setupEventListeners();
});

// Load active season
async function loadActiveSeason() {
    try {
        const seasons = await apiCall('/api/seasons');
        currentSeason = seasons.find(s => s.is_active);
        
        const seasonInfo = document.getElementById('seasonInfo');
        if (currentSeason) {
            seasonInfo.innerHTML = `
                <h3>Current Season: ${currentSeason.name}</h3>
                <p>Spreadsheet Tab: ${currentSeason.spreadsheet_tab}</p>
            `;
        } else {
            seasonInfo.innerHTML = `
                <p class="error">No active season found. Please create one in the <a href="/seasons">Seasons</a> page.</p>
            `;
        }
    } catch (error) {
        showNotification('Error loading season: ' + error.message, 'error');
    }
}

// Load eligible participants
async function loadEligibleParticipants() {
    try {
        const data = await apiCall('/api/eligible');
        const eligibleInfo = document.getElementById('eligibleInfo');
        
        if (data.eligible.length === 0) {
            eligibleInfo.innerHTML = `
                <h3>Eligible Participants</h3>
                <p>No eligible participants remaining this season!</p>
            `;
        } else {
            eligibleInfo.innerHTML = `
                <h3>Eligible Participants (${data.count})</h3>
                <p>${data.eligible.join(', ')}</p>
            `;
        }
        
        // Populate checkboxes for custom selection
        const checkboxContainer = document.getElementById('participantCheckboxes');
        checkboxContainer.innerHTML = data.eligible.map(name => `
            <label>
                <input type="checkbox" name="participant" value="${name}">
                ${name}
            </label>
        `).join('');
        
    } catch (error) {
        showNotification('Error loading participants: ' + error.message, 'error');
    }
}

// Load season roster
async function loadSeasonRoster() {
    try {
        if (!currentSeason) return;
        
        const data = await apiCall(`/api/seasons/${currentSeason.id}/roster`);
        const rosterList = document.getElementById('rosterList');
        
        if (data.roster.length === 0) {
            rosterList.innerHTML = '<li>No one selected yet</li>';
        } else {
            rosterList.innerHTML = data.roster.map(name => `<li>${name}</li>`).join('');
        }
    } catch (error) {
        showNotification('Error loading roster: ' + error.message, 'error');
    }
}

// Setup event listeners
function setupEventListeners() {
    // Roll type radio buttons
    const radioButtons = document.querySelectorAll('input[name="rollType"]');
    radioButtons.forEach(radio => {
        radio.addEventListener('change', (e) => {
            const customDiv = document.getElementById('customParticipants');
            customDiv.style.display = e.target.value === 'custom' ? 'block' : 'none';
        });
    });
    
    // Roll button
    document.getElementById('rollButton').addEventListener('click', performRoll);
    
    // Reset roster button
    document.getElementById('resetRosterButton').addEventListener('click', resetRoster);
    
    // Enrich button (will be shown after roll)
    document.getElementById('enrichButton').addEventListener('click', enrichMovie);
}

// Perform roll
async function performRoll() {
    const rollButton = document.getElementById('rollButton');
    rollButton.disabled = true;
    rollButton.textContent = '🎲 Rolling...';
    
    try {
        const rollType = document.querySelector('input[name="rollType"]:checked').value;
        let participants = null;
        
        if (rollType === 'custom') {
            const checkboxes = document.querySelectorAll('input[name="participant"]:checked');
            participants = Array.from(checkboxes).map(cb => cb.value);
            
            if (participants.length === 0) {
                showNotification('Please select at least one participant', 'error');
                rollButton.disabled = false;
                rollButton.textContent = '🎬 Roll the Dice!';
                return;
            }
        }
        
        const result = await apiCall('/api/rolls', {
            method: 'POST',
            body: JSON.stringify({
                season_id: currentSeason?.id,
                participants: participants
            })
        });
        
        if (result.success) {
            currentRollId = result.roll_id;
            displayRollResult(result);
            await loadEligibleParticipants();
            await loadSeasonRoster();
            showNotification('Roll successful!', 'success');
        }
        
    } catch (error) {
        showNotification('Error performing roll: ' + error.message, 'error');
    } finally {
        rollButton.disabled = false;
        rollButton.textContent = '🎬 Roll the Dice!';
    }
}

// Display roll result
function displayRollResult(result) {
    const resultDiv = document.getElementById('rollResult');
    const participantName = resultDiv.querySelector('.participant-name');
    const movieTitle = resultDiv.querySelector('.movie-title');
    
    participantName.textContent = `Selected: ${result.participant}`;
    movieTitle.textContent = `"${result.movie}"`;
    
    resultDiv.style.display = 'block';
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// Enrich movie with TMDB data
async function enrichMovie() {
    if (!currentRollId) return;
    
    const enrichButton = document.getElementById('enrichButton');
    enrichButton.disabled = true;
    enrichButton.textContent = 'Fetching...';
    
    try {
        const result = await apiCall(`/api/rolls/${currentRollId}/enrich`, {
            method: 'POST'
        });
        
        if (result.tmdb_data) {
            displayMovieDetails(result.tmdb_data);
            showNotification('Movie details fetched successfully!', 'success');
        }
        
    } catch (error) {
        showNotification('Error fetching movie details: ' + error.message, 'error');
    } finally {
        enrichButton.disabled = false;
        enrichButton.textContent = 'Fetch Movie Details from TMDB';
    }
}

// Display movie details
function displayMovieDetails(data) {
    const detailsDiv = document.getElementById('movieDetails');
    
    detailsDiv.innerHTML = `
        ${data.poster_url ? `<img src="${data.poster_url}" alt="${data.title} poster">` : ''}
        <h3>${data.title}</h3>
        ${data.release_date ? `<p><strong>Release Date:</strong> ${data.release_date}</p>` : ''}
        ${data.runtime ? `<p><strong>Runtime:</strong> ${data.runtime} minutes</p>` : ''}
        ${data.genres && data.genres.length > 0 ? `<p><strong>Genres:</strong> ${data.genres.join(', ')}</p>` : ''}
        ${data.vote_average ? `<p><strong>Rating:</strong> ${data.vote_average}/10</p>` : ''}
        ${data.overview ? `<p><strong>Overview:</strong> ${data.overview}</p>` : ''}
    `;
    
    detailsDiv.style.display = 'block';
}

// Reset roster
async function resetRoster() {
    if (!currentSeason) return;
    
    if (!confirm('Are you sure you want to reset the season roster? This will clear all rolls for this season.')) {
        return;
    }
    
    try {
        await apiCall(`/api/seasons/${currentSeason.id}/roster`, {
            method: 'DELETE'
        });
        
        await loadEligibleParticipants();
        await loadSeasonRoster();
        
        // Hide roll result
        document.getElementById('rollResult').style.display = 'none';
        
        showNotification('Season roster reset successfully!', 'success');
    } catch (error) {
        showNotification('Error resetting roster: ' + error.message, 'error');
    }
}
