// Seasons page functionality

let editingSeasonId = null;

// Load initial data
document.addEventListener('DOMContentLoaded', async () => {
    await loadSeasons();
    setupEventListeners();
});

// Load seasons
async function loadSeasons() {
    try {
        const seasons = await apiCall('/api/seasons');
        displaySeasons(seasons);
    } catch (error) {
        showNotification('Error loading seasons: ' + error.message, 'error');
    }
}

// Display seasons
function displaySeasons(seasons) {
    const seasonsList = document.getElementById('seasonsList');
    
    if (seasons.length === 0) {
        seasonsList.innerHTML = '<p>No seasons found. Create your first season!</p>';
        return;
    }
    
    seasonsList.innerHTML = seasons.map(season => `
        <div class="season-card ${season.is_active ? 'active' : ''}">
            <h3>
                ${season.name}
                ${season.is_active ? '<span class="badge badge-active">Active</span>' : ''}
            </h3>
            <p><strong>Spreadsheet Tab:</strong> ${season.spreadsheet_tab}</p>
            <p><strong>Created:</strong> ${formatDate(season.created_at)}</p>
            ${season.start_date ? `<p><strong>Started:</strong> ${formatDate(season.start_date)}</p>` : ''}
            ${season.end_date ? `<p><strong>Ended:</strong> ${formatDate(season.end_date)}</p>` : ''}
            
            <div class="season-card-actions">
                <button class="btn btn-secondary btn-small edit-season" data-season-id="${season.id}">
                    Edit
                </button>
                ${!season.is_active ? `
                    <button class="btn btn-primary btn-small activate-season" data-season-id="${season.id}">
                        Set Active
                    </button>
                ` : ''}
            </div>
        </div>
    `).join('');
    
    // Add event listeners to buttons
    document.querySelectorAll('.edit-season').forEach(btn => {
        btn.addEventListener('click', () => {
            const seasonId = parseInt(btn.dataset.seasonId);
            editSeason(seasonId);
        });
    });
    
    document.querySelectorAll('.activate-season').forEach(btn => {
        btn.addEventListener('click', () => {
            const seasonId = parseInt(btn.dataset.seasonId);
            activateSeason(seasonId);
        });
    });
}

// Setup event listeners
function setupEventListeners() {
    // New season button
    document.getElementById('newSeasonButton').addEventListener('click', () => {
        editingSeasonId = null;
        showSeasonModal();
    });
    
    // Modal close
    const modal = document.getElementById('seasonModal');
    const closeBtn = modal.querySelector('.close');
    const cancelBtn = document.getElementById('cancelButton');
    
    closeBtn.addEventListener('click', hideSeasonModal);
    cancelBtn.addEventListener('click', hideSeasonModal);
    
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            hideSeasonModal();
        }
    });
    
    // Form submit
    document.getElementById('seasonForm').addEventListener('submit', handleFormSubmit);
}

// Show season modal
function showSeasonModal(season = null) {
    const modal = document.getElementById('seasonModal');
    const modalTitle = document.getElementById('modalTitle');
    const form = document.getElementById('seasonForm');
    
    if (season) {
        modalTitle.textContent = 'Edit Season';
        document.getElementById('seasonName').value = season.name;
        document.getElementById('spreadsheetTab').value = season.spreadsheet_tab;
        document.getElementById('isActive').checked = season.is_active;
    } else {
        modalTitle.textContent = 'Create New Season';
        form.reset();
    }
    
    modal.style.display = 'flex';
}

// Hide season modal
function hideSeasonModal() {
    const modal = document.getElementById('seasonModal');
    modal.style.display = 'none';
    editingSeasonId = null;
}

// Handle form submit
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('seasonName').value,
        spreadsheet_tab: document.getElementById('spreadsheetTab').value,
        is_active: document.getElementById('isActive').checked
    };
    
    try {
        if (editingSeasonId) {
            // Update existing season
            await apiCall(`/api/seasons/${editingSeasonId}`, {
                method: 'PUT',
                body: JSON.stringify(formData)
            });
            showNotification('Season updated successfully!', 'success');
        } else {
            // Create new season
            await apiCall('/api/seasons', {
                method: 'POST',
                body: JSON.stringify(formData)
            });
            showNotification('Season created successfully!', 'success');
        }
        
        hideSeasonModal();
        await loadSeasons();
        
    } catch (error) {
        showNotification('Error saving season: ' + error.message, 'error');
    }
}

// Edit season
async function editSeason(seasonId) {
    try {
        const season = await apiCall(`/api/seasons/${seasonId}`);
        editingSeasonId = seasonId;
        showSeasonModal(season);
    } catch (error) {
        showNotification('Error loading season: ' + error.message, 'error');
    }
}

// Activate season
async function activateSeason(seasonId) {
    try {
        await apiCall(`/api/seasons/${seasonId}`, {
            method: 'PUT',
            body: JSON.stringify({ is_active: true })
        });
        
        showNotification('Season activated successfully!', 'success');
        await loadSeasons();
        
    } catch (error) {
        showNotification('Error activating season: ' + error.message, 'error');
    }
}
