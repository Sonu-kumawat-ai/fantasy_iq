// Contest Details Page JavaScript

let currentContest = null;
let countdownInterval = null;

// Load contest details on page load
window.addEventListener('DOMContentLoaded', async () => {
    // Get contest ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    const contestId = urlParams.get('id');
    
    if (!contestId) {
        alert('No contest selected!');
        window.location.href = '/';
        return;
    }
    
    // Load contest details
    await loadContestDetails(contestId);
    
    // Check user session
    await checkUserSession();
});

// Load contest details from API
async function loadContestDetails(contestId) {
    try {
        const response = await fetch(`/get-contest-details?id=${contestId}`);
        const data = await response.json();
        
        if (data.success && data.contest) {
            currentContest = data.contest;
            displayContestDetails(data.contest);
        } else {
            alert('Contest not found!');
            window.location.href = '/';
        }
    } catch (error) {
        console.error('Error loading contest details:', error);
        alert('Failed to load contest details. Please try again.');
    }
}

// Display contest details on page
function displayContestDetails(contest) {
    // Contest title
    document.getElementById('contestTitle').textContent = contest.title || contest.match_name;
    
    // Determine sport type and set appropriate icon
    const sportType = contest.sport_type || 'cricket';
    const sportIcon = sportType === 'football' ? '⚽' : '🏏';
    
    // Teams display
    if (contest.teams && contest.teams.length >= 2) {
        document.getElementById('team1Name').textContent = contest.teams[0];
        document.getElementById('team2Name').textContent = contest.teams[1];
        
        // Update team flags based on sport type
        const teamFlags = document.querySelectorAll('.team-flag');
        teamFlags.forEach(flag => {
            flag.textContent = sportIcon;
        });
    } else {
        // Hide teams display if not available
        document.getElementById('teamsDisplay').style.display = 'none';
    }
    
    // Contest info
    document.getElementById('prizePool').textContent = `₹${formatNumber(contest.prize_pool)}`;
    document.getElementById('entryFee').textContent = contest.entry_fee === 0 ? 'Free' : `₹${contest.entry_fee}`;
    
    // Start countdown timer
    if (contest.match_start_time) {
        startCountdown(contest.match_start_time);
    } else {
        document.getElementById('timeRemaining').textContent = 'TBD';
    }
    
    // Match information
    document.getElementById('venueInfo').textContent = contest.venue || 'TBD';
    document.getElementById('matchStatus').textContent = contest.status || 'Upcoming';
    
    // Set sport type with icon
    const sportTypeLabel = document.getElementById('sportTypeLabel');
    const sportTypeValue = document.getElementById('sportType');
    if (sportType === 'football') {
        sportTypeLabel.innerHTML = '⚽ Sport Type:';
        sportTypeValue.textContent = 'Football';
    } else {
        sportTypeLabel.innerHTML = '🏏 Sport Type:';
        sportTypeValue.textContent = 'Cricket';
    }
    
    // Set league with sport-specific fallback (sportType already declared above)
    const defaultLeague = sportType === 'football' ? 'Football League' : 'Cricket League';
    document.getElementById('leagueInfo').textContent = contest.league || defaultLeague;
    
    // Update Points System description based on sport type
    const pointsDescription = document.querySelector('.points-content p');
    if (pointsDescription) {
        if (sportType === 'football') {
            pointsDescription.textContent = 'Standard football fantasy points rules apply - Goals, Assists, Clean Sheets, Saves, Passes & more';
        } else {
            pointsDescription.textContent = 'Standard cricket fantasy points rules apply - Runs, Wickets, Catches, Strike Rate, Economy Rate & more';
        }
    }
    
    // Match date
    if (contest.match_date) {
        const matchDate = new Date(contest.match_date);
        document.getElementById('matchDate').textContent = matchDate.toLocaleDateString('en-IN', {
            day: 'numeric',
            month: 'long',
            year: 'numeric'
        });
    } else {
        document.getElementById('matchDate').textContent = 'TBD';
    }
    
    // Match time
    if (contest.match_start_time) {
        const matchTime = new Date(contest.match_start_time);
        document.getElementById('matchTime').textContent = matchTime.toLocaleTimeString('en-IN', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        });
    } else {
        document.getElementById('matchTime').textContent = 'TBD';
    }
}

// Start countdown timer
function startCountdown(matchStartTime) {
    // Clear any existing interval
    if (countdownInterval) {
        clearInterval(countdownInterval);
    }
    
    const updateCountdown = () => {
        const now = new Date().getTime();
        const matchTime = new Date(matchStartTime).getTime();
        const distance = matchTime - now;
        
        if (distance < 0) {
            document.getElementById('timeRemaining').textContent = 'Match Started';
            document.getElementById('timeRemaining').style.color = '#dc3545';
            clearInterval(countdownInterval);
            
            // Disable create team button
            const createTeamBtn = document.querySelector('.btn-create-team');
            if (createTeamBtn) {
                createTeamBtn.disabled = true;
                createTeamBtn.textContent = 'Contest Closed - Match Started';
                createTeamBtn.style.backgroundColor = '#6c757d';
                createTeamBtn.style.cursor = 'not-allowed';
            }
            return;
        }
        
        // Calculate time components
        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);
        
        // Format countdown display
        let countdownText = '';
        if (days > 0) {
            countdownText = `${days}d ${hours}h ${minutes}m`;
        } else if (hours > 0) {
            countdownText = `${hours}h ${minutes}m ${seconds}s`;
        } else {
            countdownText = `${minutes}m ${seconds}s`;
        }
        
        document.getElementById('timeRemaining').textContent = countdownText;
    };
    
    // Update immediately
    updateCountdown();
    
    // Update every second
    countdownInterval = setInterval(updateCountdown, 1000);
}

// Format numbers with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Check user session
async function checkUserSession() {
    try {
        const response = await fetch('/check-session');
        const data = await response.json();
        
        const authButtons = document.getElementById('authButtons');
        const userInfo = document.getElementById('userInfo');
        
        if (data.logged_in) {
            // User is logged in
            if (authButtons) authButtons.style.display = 'none';
            if (userInfo) userInfo.style.display = 'flex';
            
            const welcomeText = document.getElementById('welcomeText');
            if (welcomeText) {
                welcomeText.textContent = `Welcome ${data.username}`;
            }
            
            const walletBadge = document.getElementById('walletBadge');
            if (walletBadge) {
                walletBadge.textContent = `₹${data.wallet}`;
            }
        } else {
            // User is not logged in
            if (authButtons) authButtons.style.display = 'flex';
            if (userInfo) userInfo.style.display = 'none';
        }
    } catch (error) {
        console.error('Error checking session:', error);
    }
}

// Create team function
async function createTeam() {
    // Check if match has already started
    if (currentContest && currentContest.match_start_time) {
        const matchTime = new Date(currentContest.match_start_time).getTime();
        const now = new Date().getTime();
        
        if (now >= matchTime) {
            alert('Contest closed! The match has already started. You cannot join now.');
            return;
        }
    }
    
    // Check if user is logged in
    try {
        const response = await fetch('/check-session');
        const data = await response.json();
        
        if (data.logged_in) {
            // Show payment popup if contest has entry fee
            if (currentContest && currentContest.entry_fee > 0) {
                showPaymentPopup(data.wallet);
            } else {
                // Free contest - proceed directly
                proceedToTeamCreation();
            }
        } else {
            alert('Please login to create a team and join contests!');
            window.location.href = '/login-page';
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Please login to create a team!');
        window.location.href = '/login-page';
    }
}

// Show payment popup
function showPaymentPopup(walletBalance) {
    const entryFee = currentContest.entry_fee;
    const prizePool = formatNumber(currentContest.prize_pool);
    const contestTitle = currentContest.title;
    
    // Create popup HTML
    const popupHTML = `
        <div class="payment-popup-overlay" id="paymentPopup">
            <div class="payment-popup">
                <div class="popup-header">
                    <h3>Confirm Entry</h3>
                    <button class="close-popup" onclick="closePaymentPopup()">&times;</button>
                </div>
                <div class="popup-body">
                    <div class="contest-summary">
                        <h4>${contestTitle}</h4>
                        <div class="prize-info">
                            <span>Prize Pool: ₹${prizePool}</span>
                        </div>
                    </div>
                    
                    <div class="payment-details">
                        <div class="payment-row">
                            <span>Entry Fee</span>
                            <span class="amount">₹${entryFee}</span>
                        </div>
                        <div class="payment-row">
                            <span>Wallet Balance</span>
                            <span class="amount ${walletBalance >= entryFee ? 'sufficient' : 'insufficient'}">₹${walletBalance}</span>
                        </div>
                        <div class="payment-row total">
                            <span>To Pay</span>
                            <span class="amount">₹${entryFee}</span>
                        </div>
                    </div>
                    
                    ${walletBalance < entryFee ? `
                        <div class="insufficient-balance">
                            <p>⚠️ Insufficient balance! You need ₹${entryFee - walletBalance} more.</p>
                        </div>
                    ` : ''}
                </div>
                <div class="popup-footer">
                    ${walletBalance >= entryFee ? `
                        <button class="btn-cancel" onclick="closePaymentPopup()">Cancel</button>
                        <button class="btn-pay" onclick="confirmPayment()">Pay & Join Contest</button>
                    ` : `
                        <button class="btn-cancel" onclick="closePaymentPopup()">Cancel</button>
                        <button class="btn-add-money" onclick="goToWallet()">Add Money</button>
                    `}
                </div>
            </div>
        </div>
    `;
    
    // Add popup to body
    document.body.insertAdjacentHTML('beforeend', popupHTML);
}

// Close payment popup
function closePaymentPopup() {
    const popup = document.getElementById('paymentPopup');
    if (popup) {
        popup.remove();
    }
}

// Confirm payment and proceed
async function confirmPayment() {
    try {
        // Show loading state
        const payButton = document.querySelector('.btn-pay');
        if (payButton) {
            payButton.disabled = true;
            payButton.textContent = 'Processing...';
        }
        
        // Process payment
        const response = await fetch('/pay-entry-fee', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                contest_id: currentContest.match_id,
                entry_fee: currentContest.entry_fee
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Close popup
            closePaymentPopup();
            
            // Update wallet balance in UI
            const walletBadge = document.getElementById('walletBadge');
            if (walletBadge) {
                walletBadge.textContent = `₹${data.new_balance}`;
            }
            
            // Redirect to team creation page directly without showing message
            if (data.redirect_url) {
                window.location.href = data.redirect_url;
            } else {
                proceedToTeamCreation();
            }
        } else {
            // Close popup if match started
            if (data.match_started) {
                closePaymentPopup();
            }
            
            // Show error message
            alert(data.message || 'Payment failed. Please try again.');
            
            // Re-enable button only if match hasn't started
            if (payButton && !data.match_started) {
                payButton.disabled = false;
                payButton.textContent = 'Pay & Join Contest';
            }
        }
    } catch (error) {
        console.error('Payment error:', error);
        alert('An error occurred while processing payment. Please try again.');
        
        // Re-enable button
        const payButton = document.querySelector('.btn-pay');
        if (payButton) {
            payButton.disabled = false;
            payButton.textContent = 'Pay & Join Contest';
        }
    }
}

// Go to wallet page
function goToWallet() {
    window.location.href = '/wallet';
}

// Proceed to team creation
function proceedToTeamCreation() {
    // TODO: Implement team creation page
    alert('Team creation feature coming soon! You will be able to select 11 players and join the contest.');
    // window.location.href = `/create-team?contest=${currentContest.match_id}`;
}
