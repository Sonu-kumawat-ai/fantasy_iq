// Joined Contests Page JavaScript

// Mobile Menu Toggle
function toggleMobileMenu() {
    const navLinks = document.getElementById('navLinks');
    const hamburger = document.getElementById('hamburger');
    
    navLinks.classList.toggle('active');
    hamburger.classList.toggle('active');
}

// Check user session on page load
window.addEventListener('DOMContentLoaded', async () => {
    await checkUserSession();
});

// Check user session
async function checkUserSession() {
    try {
        const response = await fetch('/check-session');
        const data = await response.json();
        
        const authButtons = document.getElementById('authButtons');
        const userInfo = document.getElementById('userInfo');
        
        if (data.logged_in) {
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
            // User not logged in, redirect to login
            window.location.href = '/login-page';
        }
    } catch (error) {
        console.error('Error checking session:', error);
    }
}
