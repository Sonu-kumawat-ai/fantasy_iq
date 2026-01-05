// Carousel functionality
let currentSlide = 0;
const slides = document.querySelectorAll('.carousel-slide');
const dots = document.querySelectorAll('.dot');

// Mobile Menu Toggle
function toggleMobileMenu() {
    const navLinks = document.getElementById('navLinks');
    const hamburger = document.getElementById('hamburger');
    
    navLinks.classList.toggle('active');
    hamburger.classList.toggle('active');
}

// Close mobile menu when clicking on a link
document.addEventListener('DOMContentLoaded', () => {
    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            const navLinksContainer = document.getElementById('navLinks');
            const hamburger = document.getElementById('hamburger');
            if (navLinksContainer && navLinksContainer.classList.contains('active')) {
                navLinksContainer.classList.remove('active');
                hamburger.classList.remove('active');
            }
        });
    });
});

function showSlide(n) {
    if (slides.length === 0) return;
    
    if (n >= slides.length) {
        currentSlide = 0;
    }
    if (n < 0) {
        currentSlide = slides.length - 1;
    }
    
    slides.forEach(slide => slide.classList.remove('active'));
    dots.forEach(dot => dot.classList.remove('active'));
    
    slides[currentSlide].classList.add('active');
    if (dots[currentSlide]) {
        dots[currentSlide].classList.add('active');
    }
}

function changeSlide(n) {
    currentSlide += n;
    showSlide(currentSlide);
}

function currentSlideFunc(n) {
    currentSlide = n;
    showSlide(currentSlide);
}

// Auto-advance carousel
if (slides.length > 0) {
    setInterval(() => {
        currentSlide++;
        showSlide(currentSlide);
    }, 5000);
}

// Sports Selection functionality
let selectedSport = 'all';

function selectSport(sport) {
    selectedSport = sport;
    
    // Update active tab
    document.querySelectorAll('.sport-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    const selectedTab = document.querySelector(`.sport-tab[data-sport="${sport}"]`);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    
    // Update section title
    const sportTitle = document.getElementById('selectedSportTitle');
    if (sportTitle) {
        if (sport === 'all') {
            sportTitle.textContent = 'All Sports';
        } else {
            sportTitle.textContent = sport.charAt(0).toUpperCase() + sport.slice(1);
        }
    }
    
    // Load contests for selected sport
    loadContests(sport);
}

// Load contests from API
let allContests = []; // Store all contests
let displayedContestsCount = 0; // Track how many contests are displayed
const INITIAL_DISPLAY = 3; // Show 3 contests initially
const LOAD_MORE_COUNT = 6; // Load 6 more contests on each click

async function loadContests(sport = 'all') {
    try {
        const contestsContainer = document.getElementById('contestsContainer');
        if (!contestsContainer) return;
        
        // Show loading state
        contestsContainer.innerHTML = '<div class="loading-contests"><p>Loading contests...</p></div>';
        
        const response = await fetch(`/get-contests?sport=${sport}`);
        const data = await response.json();
        
        if (data.success && data.contests && data.contests.length > 0) {
            // Store all contests
            allContests = data.contests;
            displayedContestsCount = 0;
            
            // Clear container
            contestsContainer.innerHTML = '';
            
            // Display initial contests
            displayContests(INITIAL_DISPLAY);
            
            // Show or hide "Load More" button
            updateLoadMoreButton();
        } else {
            // No contests available
            contestsContainer.innerHTML = `
                <div class="no-contests">
                    <p>No contests available for ${sport} at the moment.</p>
                    <p>Check back soon for exciting contests!</p>
                </div>
            `;
            hideLoadMoreButton();
        }
    } catch (error) {
        console.error('Error loading contests:', error);
        const contestsContainer = document.getElementById('contestsContainer');
        if (contestsContainer) {
            contestsContainer.innerHTML = `
                <div class="error-contests">
                    <p>Failed to load contests. Please try again later.</p>
                </div>
            `;
        }
        hideLoadMoreButton();
    }
}

// Display contests
function displayContests(count) {
    const contestsContainer = document.getElementById('contestsContainer');
    if (!contestsContainer) return;
    
    const endIndex = Math.min(displayedContestsCount + count, allContests.length);
    
    for (let i = displayedContestsCount; i < endIndex; i++) {
        const contestCard = createContestCard(allContests[i]);
        contestsContainer.appendChild(contestCard);
    }
    
    displayedContestsCount = endIndex;
    
    // Re-attach event listeners to new join buttons
    attachJoinButtonListeners();
}

// Load more contests
function loadMoreContests() {
    displayContests(LOAD_MORE_COUNT);
    updateLoadMoreButton();
}

// Update Load More button visibility
function updateLoadMoreButton() {
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    if (!loadMoreBtn) return;
    
    // Always show the button if there are any contests (it redirects to contests page)
    if (allContests.length > 0) {
        loadMoreBtn.style.display = 'block';
        loadMoreBtn.textContent = 'More Contests';
    } else {
        loadMoreBtn.style.display = 'none';
    }
}

// Hide Load More button
function hideLoadMoreButton() {
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    if (loadMoreBtn) {
        loadMoreBtn.style.display = 'none';
    }
}

// Create contest card HTML element
function createContestCard(contest) {
    const card = document.createElement('div');
    card.className = 'contest-card';
    
    card.innerHTML = `
        <div class="contest-header">
            <h3>${contest.title || contest.match_name}</h3>
        </div>
        <div class="contest-body">
            <div class="contest-info">
                <div class="info-item">
                    <span class="label">Winning Prize</span>
                    <span class="value">₹${formatCurrency(contest.prize_pool)}</span>
                </div>
                <div class="info-item">
                    <span class="label">Entry Fee</span>
                    <span class="value">${contest.entry_fee === 0 ? 'Free' : '₹' + contest.entry_fee}</span>
                </div>
            </div>
        </div>
        <div class="contest-footer">
            <button class="btn-join" data-contest-id="${contest.match_id}">Join Contest</button>
        </div>
    `;
    
    return card;
}

// Format large numbers in readable format (Cr, L, K)
function formatCurrency(amount) {
    if (amount >= 10000000) {
        return (amount / 10000000).toFixed(1) + ' Cr';
    } else if (amount >= 100000) {
        return (amount / 100000).toFixed(1) + ' L';
    } else if (amount >= 1000) {
        return (amount / 1000).toFixed(1) + ' K';
    }
    return amount.toString();
}

// Format large numbers with commas (legacy, kept for compatibility)
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Attach event listeners to join buttons
function attachJoinButtonListeners() {
    const joinButtons = document.querySelectorAll('.btn-join');
    joinButtons.forEach(button => {
        button.addEventListener('click', handleJoinContest);
    });
}

// Handle join contest button click
async function handleJoinContest(event) {
    const button = event.target;
    const contestId = button.getAttribute('data-contest-id');
    
    // Redirect to contest details page
    window.location.href = `/contest-details?id=${contestId}`;
}

// Initialize with all sports selected and load contests
document.addEventListener('DOMContentLoaded', () => {
    selectSport('all');
});

// Check user session on page load
window.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('/check-session');
        const data = await response.json();
        
        const authButtons = document.getElementById('authButtons');
        const userInfo = document.getElementById('userInfo');
        
        if (data.logged_in) {
            // User is logged in
            if (authButtons) authButtons.style.display = 'none';
            if (userInfo) userInfo.style.display = 'flex';
            
            // Update welcome text in navbar
            const welcomeText = document.getElementById('welcomeText');
            if (welcomeText) {
                welcomeText.textContent = `Welcome ${data.username}`;
            }
            
            // Update wallet badge in dropdown
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
        // On error, show login button as fallback
        const authButtons = document.getElementById('authButtons');
        if (authButtons) authButtons.style.display = 'flex';
    }
    
    // Handle sport selection from landing page
    const selectedSport = localStorage.getItem('selectedSport');
    if (selectedSport) {
        // Find and click the corresponding sport tab
        const sportTabs = document.querySelectorAll('.tab-btn');
        sportTabs.forEach(tab => {
            const tabText = tab.textContent.toLowerCase();
            if (tabText.includes(selectedSport)) {
                tab.click();
                // Scroll to contests section
                const contestsSection = document.querySelector('.contests-section');
                if (contestsSection) {
                    contestsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
        });
        // Clear the stored sport after using it
        localStorage.removeItem('selectedSport');
    }
});

// Toggle between login and register forms
function toggleForms() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    if (loginForm && registerForm) {
        if (loginForm.style.display === 'none') {
            loginForm.style.display = 'block';
            registerForm.style.display = 'none';
        } else {
            loginForm.style.display = 'none';
            registerForm.style.display = 'block';
        }
        
        // Clear messages
        const loginMessage = document.getElementById('loginMessage');
        const registerMessage = document.getElementById('registerMessage');
        if (loginMessage) loginMessage.style.display = 'none';
        if (registerMessage) registerMessage.style.display = 'none';
    }
}

// Handle login form submission
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const messageDiv = document.getElementById('loginMessage');
    
    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            messageDiv.className = 'message success';
            messageDiv.textContent = data.message;
            messageDiv.style.display = 'block';
            
            // Redirect to home page after 1 second
            setTimeout(() => {
                window.location.href = '/';
            }, 1000);
        } else {
            messageDiv.className = 'message error';
            messageDiv.textContent = data.message;
            messageDiv.style.display = 'block';
        }
    } catch (error) {
        messageDiv.className = 'message error';
        messageDiv.textContent = 'An error occurred. Please try again.';
        messageDiv.style.display = 'block';
        console.error('Login error:', error);
    }
}

// Handle register form submission
async function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('registerUsername').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const confirmPassword = document.getElementById('registerConfirmPassword').value;
    const messageDiv = document.getElementById('registerMessage');
    
    // Validate password match
    if (password !== confirmPassword) {
        messageDiv.className = 'message error';
        messageDiv.textContent = 'Passwords do not match!';
        messageDiv.style.display = 'block';
        return;
    }
    
    // Validate password length
    if (password.length < 6) {
        messageDiv.className = 'message error';
        messageDiv.textContent = 'Password must be at least 6 characters long!';
        messageDiv.style.display = 'block';
        return;
    }
    
    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            messageDiv.className = 'message success';
            messageDiv.textContent = data.message;
            messageDiv.style.display = 'block';
            
            // Clear form
            document.getElementById('registerUsername').value = '';
            document.getElementById('registerEmail').value = '';
            document.getElementById('registerPassword').value = '';
            document.getElementById('registerConfirmPassword').value = '';
            
            // Redirect to login page after 2 seconds
            setTimeout(() => {
                window.location.href = '/login-page';
            }, 2000);
        } else {
            messageDiv.className = 'message error';
            messageDiv.textContent = data.message;
            messageDiv.style.display = 'block';
        }
    } catch (error) {
        messageDiv.className = 'message error';
        messageDiv.textContent = 'An error occurred. Please try again.';
        messageDiv.style.display = 'block';
        console.error('Register error:', error);
    }
}
