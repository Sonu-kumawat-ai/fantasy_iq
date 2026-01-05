// Create Team Page JavaScript

let allPlayers = [];
let selectedPlayers = [];
let captain = null;
let viceCaptain = null;
let currentFilter = 'all';
let contestData = null;

// Load players on page load
window.addEventListener('DOMContentLoaded', async () => {
    await loadPlayers();
    await loadExistingTeam();
});

// Load existing team if editing
async function loadExistingTeam() {
    try {
        const response = await fetch(`/get-user-team?contest_id=${contestId}`);
        const data = await response.json();
        
        if (data.success && data.team) {
            const team = data.team;
            
            // Pre-select players
            team.selected_players.forEach(playerId => {
                const player = allPlayers.find(p => p.player_id === playerId);
                if (player && selectedPlayers.length < 11) {
                    selectedPlayers.push(player);
                }
            });
            
            // Set captain
            const captainPlayer = allPlayers.find(p => p.player_id === team.captain_id);
            if (captainPlayer) {
                captain = captainPlayer;
            }
            
            // Set vice-captain
            const viceCaptainPlayer = allPlayers.find(p => p.player_id === team.vice_captain_id);
            if (viceCaptainPlayer) {
                viceCaptain = viceCaptainPlayer;
            }
            
            updateUI();
        }
    } catch (error) {
        console.error('Error loading existing team:', error);
        // No existing team, continue with empty selection
    }
}

// Load players from API
async function loadPlayers() {
    try {
        const response = await fetch(`/get-players?contest_id=${contestId}`);
        const data = await response.json();
        
        if (data.success) {
            allPlayers = data.players;
            contestData = data.contest;
            
            // Create filter tabs based on sport type
            createFilterTabs();
            
            displayPlayers(allPlayers);
            
            // Update contest title
            if (data.contest) {
                document.getElementById('contestTitle').textContent = `Create Team - ${data.contest.title}`;
            }
        } else {
            alert('Failed to load players: ' + data.message);
        }
    } catch (error) {
        console.error('Error loading players:', error);
        alert('Failed to load players. Please try again.');
    }
}

// Create filter tabs based on sport type
function createFilterTabs() {
    const filterTabsContainer = document.querySelector('.filter-tabs');
    if (!filterTabsContainer) return;
    
    const sportType = contestData?.sport_type || 'cricket';
    
    let tabs = [];
    if (sportType === 'football') {
        tabs = [
            { role: 'all', label: 'All' },
            { role: 'Goalkeeper', label: 'Goalkeepers' },
            { role: 'Defender', label: 'Defenders' },
            { role: 'Midfielder', label: 'Midfielders' },
            { role: 'Forward', label: 'Forwards' }
        ];
    } else {
        tabs = [
            { role: 'all', label: 'All' },
            { role: 'Batsman', label: 'Batsmen' },
            { role: 'Bowler', label: 'Bowlers' },
            { role: 'All-Rounder', label: 'All-Rounders' },
            { role: 'Wicket-Keeper', label: 'Wicket-Keepers' }
        ];
    }
    
    filterTabsContainer.innerHTML = tabs.map(tab => 
        `<button class="tab-btn ${tab.role === 'all' ? 'active' : ''}" data-role="${tab.role}" onclick="filterPlayers('${tab.role}')">${tab.label}</button>`
    ).join('');
}

// Display players
function displayPlayers(players) {
    const grid = document.getElementById('playersGrid');
    
    if (!players || players.length === 0) {
        grid.innerHTML = '<div class="loading">No players available</div>';
        return;
    }
    
    grid.innerHTML = '';
    
    const teamFull = selectedPlayers.length >= 11;
    
    players.forEach(player => {
        const isSelected = selectedPlayers.some(p => p.player_id === player.player_id);
        
        const card = document.createElement('div');
        card.className = `player-card ${isSelected ? 'selected' : ''} ${teamFull && !isSelected ? 'disabled' : ''}`;
        
        card.innerHTML = `
            <div class="player-header">
                <div class="player-name">${player.name}</div>
            </div>
            <div class="player-team">${player.team}</div>
            <div class="player-info">
                <span class="player-role">${player.role}</span>
            </div>
            <div class="player-actions">
                ${!isSelected ? `
                    <button class="btn-add-player" onclick="addPlayer('${player.player_id}')" ${teamFull ? 'disabled' : ''}>
                        Add
                    </button>
                ` : `
                    <button class="btn-add-player" onclick="removePlayer('${player.player_id}')" style="background: #dc3545;">
                        Remove
                    </button>
                `}
            </div>
        `;
        
        grid.appendChild(card);
    });
}

// Add player to team
function addPlayer(playerId) {
    const player = allPlayers.find(p => p.player_id === playerId);
    
    if (!player) return;
    
    // Check if already selected
    if (selectedPlayers.some(p => p.player_id === playerId)) {
        alert('Player already selected!');
        return;
    }
    
    // Check team limit
    if (selectedPlayers.length >= 11) {
        alert('You can only select 11 players!');
        return;
    }
    
    // Add player
    selectedPlayers.push(player);
    
    updateUI();
}

// Remove player from team
function removePlayer(playerId) {
    const index = selectedPlayers.findIndex(p => p.player_id === playerId);
    
    if (index === -1) return;
    
    const player = selectedPlayers[index];
    
    // Remove from selection
    selectedPlayers.splice(index, 1);
    
    // Remove captain/vice-captain if needed
    if (captain && captain.player_id === playerId) {
        captain = null;
    }
    if (viceCaptain && viceCaptain.player_id === playerId) {
        viceCaptain = null;
    }
    
    updateUI();
}

// Set captain
function setCaptain(playerId) {
    const player = selectedPlayers.find(p => p.player_id === playerId);
    
    if (!player) return;
    
    // Check if player is already vice-captain
    if (viceCaptain && viceCaptain.player_id === playerId) {
        alert('This player is already selected as Vice-Captain! Please choose a different player.');
        return;
    }
    
    captain = player;
    updateUI();
}

// Set vice-captain
function setViceCaptain(playerId) {
    const player = selectedPlayers.find(p => p.player_id === playerId);
    
    if (!player) return;
    
    // Check if player is already captain
    if (captain && captain.player_id === playerId) {
        alert('This player is already selected as Captain! Please choose a different player.');
        return;
    }
    
    viceCaptain = player;
    updateUI();
}

// Update UI
function updateUI() {
    // Update players count
    document.getElementById('playersSelected').innerHTML = `Players: <strong>${selectedPlayers.length}/11</strong>`;
    
    // Update team count in preview section
    const teamCountElement = document.getElementById('teamCount');
    if (teamCountElement) {
        teamCountElement.textContent = selectedPlayers.length;
    }
    
    // Update selected players display
    const selectedContainer = document.getElementById('selectedPlayers');
    
    if (selectedPlayers.length === 0) {
        selectedContainer.innerHTML = '<p class="empty-state">Select 11 players to create your team</p>';
    } else {
        selectedContainer.innerHTML = selectedPlayers.map(player => {
            const isCaptain = captain && captain.player_id === player.player_id;
            const isViceCaptain = viceCaptain && viceCaptain.player_id === player.player_id;
            
            return `
                <div class="selected-player-card ${isCaptain ? 'captain' : ''} ${isViceCaptain ? 'vice-captain' : ''}">
                    <div class="player-name-team">
                        <span class="name">${player.name}</span>
                        <span class="team">${player.team}</span>
                    </div>
                    <span class="role">${player.role}</span>
                    <div class="captain-buttons">
                        ${!isCaptain && !isViceCaptain ? `
                            <button class="btn-captain" onclick="setCaptain('${player.player_id}')" title="Set as Captain">C</button>
                            <button class="btn-vice-captain" onclick="setViceCaptain('${player.player_id}')" title="Set as Vice-Captain">VC</button>
                        ` : isCaptain ? `
                            <span style="color: #28a745; font-weight: bold; font-size: 0.85rem;">Captain</span>
                        ` : `
                            <span style="color: #17a2b8; font-weight: bold; font-size: 0.85rem;">Vice-Cap</span>
                        `}
                    </div>
                    <button class="remove-btn" onclick="removePlayer('${player.player_id}')">×</button>
                </div>
            `;
        }).join('');
    }
    
    // Update captain/vice-captain display
    document.getElementById('captainName').textContent = captain ? captain.name : 'Not selected';
    document.getElementById('viceCaptainName').textContent = viceCaptain ? viceCaptain.name : 'Not selected';
    
    // Enable/disable submit button
    const submitBtn = document.getElementById('submitTeamBtn');
    submitBtn.disabled = !(selectedPlayers.length === 11 && captain && viceCaptain);
    
    // Refresh players display
    filterPlayers(currentFilter);
}

// Filter players
function filterPlayers(role) {
    currentFilter = role;
    
    // Update active tab
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.role === role) {
            btn.classList.add('active');
        }
    });
    
    // Filter and display
    if (role === 'all') {
        displayPlayers(allPlayers);
    } else {
        const filtered = allPlayers.filter(p => p.role === role);
        displayPlayers(filtered);
    }
}

// Submit team
async function submitTeam() {
    if (selectedPlayers.length !== 11) {
        alert('Please select exactly 11 players!');
        return;
    }
    
    if (!captain || !viceCaptain) {
        alert('Please select Captain and Vice-Captain!');
        return;
    }
    
    if (captain.player_id === viceCaptain.player_id) {
        alert('Captain and Vice-Captain must be different players!');
        return;
    }
    
    // Disable submit button to prevent double submission
    const submitBtn = document.getElementById('submitTeamBtn');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting...';
    
    try {
        const response = await fetch('/save-team', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                contest_id: contestId,
                selected_players: selectedPlayers.map(p => p.player_id),
                captain_id: captain.player_id,
                vice_captain_id: viceCaptain.player_id
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(data.message);
            // Redirect to joined contests page
            window.location.href = '/joined-contests';
        } else {
            alert('Error: ' + data.message);
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Team';
        }
    } catch (error) {
        console.error('Error submitting team:', error);
        alert('Failed to submit team. Please try again.');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Team';
    }
}
