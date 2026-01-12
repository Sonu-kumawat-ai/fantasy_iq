// Admin Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    loadUsers();
    loadMatches();
    loadContests();
});

// Load dashboard stats
async function loadStats() {
    try {
        const response = await fetch('/api/admin/stats');
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('totalUsers').textContent = data.stats.total_users || 0;
            document.getElementById('totalContests').textContent = data.stats.total_contests || 0;
            document.getElementById('totalMatches').textContent = data.stats.total_matches || 0;
            document.getElementById('totalRevenue').textContent = '₹' + (data.stats.total_revenue || 0).toLocaleString();
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load users
async function loadUsers() {
    const tbody = document.getElementById('usersTable');
    tbody.innerHTML = '<tr><td colspan="5" class="loading">Loading users...</td></tr>';
    
    try {
        const response = await fetch('/api/admin/users');
        const data = await response.json();
        
        if (data.success && data.users.length > 0) {
            tbody.innerHTML = data.users.map(user => `
                <tr>
                    <td>${user.username || 'N/A'}</td>
                    <td>${user.email || 'N/A'}</td>
                    <td>₹${(user.balance || 0).toLocaleString()}</td>
                    <td>${formatDate(user.created_at)}</td>
                    <td>
                        <div class="action-btns">
                            <button class="btn-action btn-view" onclick="viewUser('${user.username}')">View</button>
                            <button class="btn-action btn-delete" onclick="deleteUser('${user.username}')">Delete</button>
                        </div>
                    </td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="5" class="loading">No users found</td></tr>';
        }
    } catch (error) {
        console.error('Error loading users:', error);
        tbody.innerHTML = '<tr><td colspan="5" class="loading">Error loading users</td></tr>';
    }
}

// Load matches
async function loadMatches() {
    const tbody = document.getElementById('matchesTable');
    tbody.innerHTML = '<tr><td colspan="5" class="loading">Loading matches...</td></tr>';
    
    try {
        const response = await fetch('/api/admin/matches');
        const data = await response.json();
        
        if (data.success && data.matches.length > 0) {
            tbody.innerHTML = data.matches.map(match => `
                <tr>
                    <td>${match.name || 'N/A'}</td>
                    <td>${(match.sport_type || 'cricket').toUpperCase()}</td>
                    <td>${formatDate(match.date)}</td>
                    <td><span class="status-badge status-${match.status}">${match.status || 'upcoming'}</span></td>
                    <td>
                        <div class="action-btns">
                            <button class="btn-action btn-view" onclick="viewMatch('${match.match_id}')">View</button>
                            <button class="btn-action btn-delete" onclick="deleteMatch('${match.match_id}')">Delete</button>
                        </div>
                    </td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="5" class="loading">No matches found</td></tr>';
        }
    } catch (error) {
        console.error('Error loading matches:', error);
        tbody.innerHTML = '<tr><td colspan="5" class="loading">Error loading matches</td></tr>';
    }
}

// Load contests
async function loadContests() {
    const tbody = document.getElementById('contestsTable');
    tbody.innerHTML = '<tr><td colspan="6" class="loading">Loading contests...</td></tr>';
    
    try {
        const response = await fetch('/api/admin/contests');
        const data = await response.json();
        
        if (data.success && data.contests.length > 0) {
            tbody.innerHTML = data.contests.map(contest => `
                <tr>
                    <td>${contest.title || 'N/A'}</td>
                    <td>${contest.match_name || 'N/A'}</td>
                    <td>₹${(contest.entry_fee || 0).toLocaleString()}</td>
                    <td>₹${(contest.prize_pool || 0).toLocaleString()}</td>
                    <td>${contest.filled_spots || 0} / ${contest.total_spots || 0}</td>
                    <td>
                        <div class="action-btns">
                            <button class="btn-action btn-view" onclick="viewContest('${contest.match_id}')">View</button>
                            <button class="btn-action btn-delete" onclick="deleteContest('${contest.match_id}')">Delete</button>
                        </div>
                    </td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="6" class="loading">No contests found</td></tr>';
        }
    } catch (error) {
        console.error('Error loading contests:', error);
        tbody.innerHTML = '<tr><td colspan="6" class="loading">Error loading contests</td></tr>';
    }
}

// Utility function to format date
function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    try {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-IN', { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric' 
        });
    } catch {
        return dateStr;
    }
}

// Action functions
function viewUser(username) {
    window.location.href = `/admin/user/${username}`;
}

async function deleteUser(username) {
    if (!confirm(`Are you sure you want to delete user: ${username}?`)) return;
    
    try {
        const response = await fetch(`/api/admin/user/${username}`, {
            method: 'DELETE'
        });
        const data = await response.json();
        
        if (data.success) {
            alert('User deleted successfully');
            loadUsers();
            loadStats();
        } else {
            alert(data.message || 'Failed to delete user');
        }
    } catch (error) {
        console.error('Error deleting user:', error);
        alert('Error deleting user');
    }
}

function viewMatch(matchId) {
    window.location.href = `/contest-details?match_id=${matchId}`;
}

async function deleteMatch(matchId) {
    if (!confirm('Are you sure you want to delete this match?')) return;
    
    try {
        const response = await fetch(`/api/admin/match/${matchId}`, {
            method: 'DELETE'
        });
        const data = await response.json();
        
        if (data.success) {
            alert('Match deleted successfully');
            loadMatches();
            loadStats();
        } else {
            alert(data.message || 'Failed to delete match');
        }
    } catch (error) {
        console.error('Error deleting match:', error);
        alert('Error deleting match');
    }
}

function viewContest(contestId) {
    window.location.href = `/contest-details?match_id=${contestId}`;
}

async function deleteContest(contestId) {
    if (!confirm('Are you sure you want to delete this contest?')) return;
    
    try {
        const response = await fetch(`/api/admin/contest/${contestId}`, {
            method: 'DELETE'
        });
        const data = await response.json();
        
        if (data.success) {
            alert('Contest deleted successfully');
            loadContests();
            loadStats();
        } else {
            alert(data.message || 'Failed to delete contest');
        }
    } catch (error) {
        console.error('Error deleting contest:', error);
        alert('Error deleting contest');
    }
}
