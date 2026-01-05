// Load user profile data
let currentUserData = {};

window.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('/check-session');
        const data = await response.json();
        
        const authButtons = document.getElementById('authButtons');
        const userInfo = document.getElementById('userInfo');
        
        if (data.logged_in) {
            currentUserData = data;
            
            // Update profile information
            document.getElementById('profileUsername').textContent = data.username;
            document.getElementById('profileEmail').textContent = data.email || 'N/A';
            document.getElementById('usernameDisplay').textContent = data.username;
            document.getElementById('emailDisplay').textContent = data.email || 'N/A';
            document.getElementById('walletAmount').textContent = `₹${data.wallet}`;
            
            // Format member since date
            if (data.created_at) {
                const date = new Date(data.created_at);
                document.getElementById('memberSince').textContent = date.toLocaleDateString('en-IN', {
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric'
                });
            } else {
                document.getElementById('memberSince').textContent = 'N/A';
            }
            
            // Update navbar
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
            // User not logged in, redirect to login page
            window.location.href = '/login-page';
        }
    } catch (error) {
        console.error('Error loading profile:', error);
        window.location.href = '/login-page';
    }
    
    // Load theme preference
    loadTheme();
});

// Edit profile functions
function toggleEdit() {
    const displayElements = document.querySelectorAll('.info-value');
    const inputElements = document.querySelectorAll('.info-input');
    const editButtons = document.getElementById('editButtons');
    const editBtn = document.getElementById('editBtn');
    
    // Populate inputs with current values
    document.getElementById('usernameInput').value = currentUserData.username;
    document.getElementById('emailInput').value = currentUserData.email || '';
    
    // Toggle display/input visibility
    document.getElementById('usernameDisplay').style.display = 'none';
    document.getElementById('emailDisplay').style.display = 'none';
    document.getElementById('usernameInput').style.display = 'inline-block';
    document.getElementById('emailInput').style.display = 'inline-block';
    
    editButtons.style.display = 'flex';
    editBtn.style.display = 'none';
}

function cancelEdit() {
    // Hide inputs, show display
    document.getElementById('usernameDisplay').style.display = 'inline';
    document.getElementById('emailDisplay').style.display = 'inline';
    document.getElementById('usernameInput').style.display = 'none';
    document.getElementById('emailInput').style.display = 'none';
    
    document.getElementById('editButtons').style.display = 'none';
    document.getElementById('editBtn').style.display = 'inline-block';
}

async function saveProfile() {
    const newUsername = document.getElementById('usernameInput').value.trim();
    const newEmail = document.getElementById('emailInput').value.trim();
    
    if (!newUsername || !newEmail) {
        alert('Username and Email cannot be empty!');
        return;
    }
    
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(newEmail)) {
        alert('Please enter a valid email address!');
        return;
    }
    
    try {
        // Send update to the server
        const response = await fetch('/update-profile', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: newUsername,
                email: newEmail
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            alert('Profile updated successfully!');
            
            // Update local data and display
            currentUserData.username = newUsername;
            currentUserData.email = newEmail;
            document.getElementById('usernameDisplay').textContent = newUsername;
            document.getElementById('emailDisplay').textContent = newEmail;
            document.getElementById('profileUsername').textContent = newUsername;
            document.getElementById('profileEmail').textContent = newEmail;
            
            // Update navbar welcome text if it exists
            const welcomeText = document.getElementById('welcomeText');
            if (welcomeText) {
                welcomeText.textContent = `Welcome ${newUsername}`;
            }
            
            cancelEdit();
        } else {
            alert(data.message || 'Failed to update profile. Please try again.');
        }
    } catch (error) {
        console.error('Error updating profile:', error);
        alert('An error occurred while updating profile: ' + error.message);
    }
}

// Theme functions
function setTheme(theme) {
    const lightBtn = document.getElementById('lightBtn');
    const darkBtn = document.getElementById('darkBtn');
    
    if (theme === 'dark') {
        document.body.classList.add('dark-theme');
        lightBtn.classList.remove('active');
        darkBtn.classList.add('active');
        localStorage.setItem('theme', 'dark');
    } else {
        document.body.classList.remove('dark-theme');
        darkBtn.classList.remove('active');
        lightBtn.classList.add('active');
        localStorage.setItem('theme', 'light');
    }
}

function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
}

// Notification toggle
document.addEventListener('DOMContentLoaded', () => {
    const notificationToggle = document.getElementById('notificationToggle');
    if (notificationToggle) {
        notificationToggle.addEventListener('change', function() {
            if (this.checked) {
                alert('Notifications enabled!');
            } else {
                alert('Notifications disabled!');
            }
        });
    }
});

// Modal functions for Add Money
function openAddMoneyModal() {
    document.getElementById('addMoneyModal').style.display = 'block';
}

function closeAddMoneyModal() {
    document.getElementById('addMoneyModal').style.display = 'none';
    document.getElementById('addAmount').value = '';
}

function openWithdrawModal() {
    const availableBalanceWithdraw = document.getElementById('availableBalanceWithdraw');
    if (availableBalanceWithdraw) {
        availableBalanceWithdraw.textContent = `₹${currentUserData.wallet || 0}`;
    }
    document.getElementById('withdrawModal').style.display = 'block';
}

function closeWithdrawModal() {
    document.getElementById('withdrawModal').style.display = 'none';
    document.getElementById('withdrawAmount').value = '';
    document.getElementById('withdrawMethod').value = '';
}

// Set quick amount
function setAmount(amount) {
    document.getElementById('addAmount').value = amount;
}

// Handle Add Money with Razorpay
async function handleAddMoney(event) {
    event.preventDefault();
    
    const amount = parseFloat(document.getElementById('addAmount').value);
    
    if (!amount || amount < 1) {
        alert('Please enter a valid amount (minimum ₹1)');
        return;
    }
    
    try {
        // Create order on backend
        const response = await fetch('/create-order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ amount: amount })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        console.log('Create order response:', data);
        
        if (data.success) {
            // Initialize Razorpay
            const options = {
                key: data.razorpay_key_id,
                amount: data.order.amount,
                currency: data.order.currency,
                name: 'Fantasy IQ',
                description: 'Add Money to Wallet',
                order_id: data.order.id,
                handler: async function(response) {
                    // Payment successful, verify on backend
                    await verifyPayment(response, amount);
                },
                prefill: {
                    name: currentUserData.username,
                    email: currentUserData.email || ''
                },
                theme: {
                    color: '#DC143C'
                },
                modal: {
                    ondismiss: function() {
                        console.log('Payment cancelled by user');
                    }
                }
            };
            
            const rzp = new Razorpay(options);
            rzp.open();
            
            closeAddMoneyModal();
        } else {
            alert(data.message || 'Failed to create order. Please try again.');
        }
    } catch (error) {
        console.error('Error creating order:', error);
        alert('An error occurred while creating order: ' + error.message + '\n\nPlease check:\n1. Flask server is running\n2. MongoDB is connected\n3. Razorpay keys are set in .env file');
    }
}

// Verify payment
async function verifyPayment(paymentResponse, amount) {
    try {
        const response = await fetch('/verify-payment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                razorpay_order_id: paymentResponse.razorpay_order_id,
                razorpay_payment_id: paymentResponse.razorpay_payment_id,
                razorpay_signature: paymentResponse.razorpay_signature,
                amount: amount
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        console.log('Verify payment response:', data);
        
        if (data.success) {
            alert('Payment successful! Your wallet has been updated.');
            
            // Update wallet display
            currentUserData.wallet = data.new_wallet_balance;
            document.getElementById('walletAmount').textContent = `₹${data.new_wallet_balance}`;
            
            // Update navbar wallet badge
            const walletBadge = document.getElementById('walletBadge');
            if (walletBadge) {
                walletBadge.textContent = `₹${data.new_wallet_balance}`;
            }
        } else {
            alert('Payment verification failed: ' + (data.message || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error verifying payment:', error);
        alert('Payment verification failed: ' + error.message + '\n\nPlease contact support if amount was deducted.');
    }
}

// Handle Withdraw (placeholder)
function handleWithdraw(event) {
    event.preventDefault();
    
    const amount = parseFloat(document.getElementById('withdrawAmount').value);
    const method = document.getElementById('withdrawMethod').value;
    const currentBalance = parseFloat(currentUserData.wallet) || 0;
    
    if (!amount || amount < 1) {
        alert('Please enter a valid amount (minimum ₹1)');
        return;
    }
    
    if (amount > currentBalance) {
        alert('Insufficient balance! You cannot withdraw more than your current balance.');
        return;
    }
    
    if (!method) {
        alert('Please select a withdrawal method');
        return;
    }
    
    // TODO: Implement withdrawal backend
    alert(`Withdrawal feature coming soon!\nAmount: ₹${amount}\nMethod: ${method}`);
    closeWithdrawModal();
}

// Close modal on outside click
window.onclick = function(event) {
    const addMoneyModal = document.getElementById('addMoneyModal');
    const withdrawModal = document.getElementById('withdrawModal');
    
    if (event.target === addMoneyModal) {
        closeAddMoneyModal();
    }
    if (event.target === withdrawModal) {
        closeWithdrawModal();
    }
}
