// Load wallet data
let currentUserData = {};
let walletStats = { total_added: 0, total_withdrawn: 0 };

window.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('/check-session');
        const data = await response.json();
        
        const authButtons = document.getElementById('authButtons');
        const userInfo = document.getElementById('userInfo');
        
        if (data.logged_in) {
            currentUserData = data;
            
            // Update wallet balance
            document.getElementById('totalBalance').textContent = `₹${data.wallet}`;
            document.getElementById('availableBalance').textContent = `₹${data.wallet}`;
            
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
            
            // Load transaction history
            await loadTransactionHistory();
        } else {
            // User not logged in, redirect to login page
            window.location.href = '/login-page';
        }
    } catch (error) {
        console.error('Error loading wallet:', error);
        window.location.href = '/login-page';
    }
});

// Modal functions
function openAddMoneyModal() {
    document.getElementById('addMoneyModal').style.display = 'block';
}

function closeAddMoneyModal() {
    document.getElementById('addMoneyModal').style.display = 'none';
    document.getElementById('addAmount').value = '';
}

function openWithdrawModal() {
    const balance = parseFloat(currentUserData.wallet) || 0;
    if (balance <= 0) {
        alert('Insufficient balance! Please add money first.');
        return;
    }
    document.getElementById('withdrawModal').style.display = 'block';
}

function closeWithdrawModal() {
    document.getElementById('withdrawModal').style.display = 'none';
    document.getElementById('withdrawAmount').value = '';
    document.getElementById('withdrawMethod').value = '';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const addModal = document.getElementById('addMoneyModal');
    const withdrawModal = document.getElementById('withdrawModal');
    if (event.target == addModal) {
        closeAddMoneyModal();
    }
    if (event.target == withdrawModal) {
        closeWithdrawModal();
    }
}

// Set quick amount
function setAmount(amount) {
    document.getElementById('addAmount').value = amount;
}

// Handle add money
async function handleAddMoney(event) {
    event.preventDefault();
    const amount = document.getElementById('addAmount').value;
    
    if (!amount || parseFloat(amount) <= 0) {
        alert('Please enter a valid amount!');
        return;
    }
    
    try {
        // Create order on server
        const response = await fetch('/create-order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ amount: parseFloat(amount) })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        console.log('Create order response:', data);
        
        if (data.success) {
            // Initialize Razorpay payment
            const options = {
                key: data.key_id,
                amount: data.amount * 100, // Amount in paise
                currency: 'INR',
                name: 'Fantasy IQ',
                description: 'Add Money to Wallet',
                order_id: data.order_id,
                handler: async function(response) {
                    // Payment successful, verify on server
                    await verifyPayment(response);
                },
                prefill: {
                    name: currentUserData.username,
                    email: currentUserData.email
                },
                theme: {
                    color: '#DC143C'
                },
                modal: {
                    ondismiss: function() {
                        alert('Payment cancelled!');
                    }
                }
            };
            
            const rzp = new Razorpay(options);
            rzp.open();
            closeAddMoneyModal();
        } else {
            alert(data.message || 'Failed to create order!');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while creating order: ' + error.message + '\n\nPlease check:\n1. Flask server is running\n2. MongoDB is connected\n3. Razorpay keys are set in .env file');
    }
}

// Verify payment
async function verifyPayment(paymentResponse) {
    try {
        const response = await fetch('/verify-payment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(paymentResponse)
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(data.message);
            // Update wallet balance
            currentUserData.wallet = data.new_balance;
            document.getElementById('totalBalance').textContent = `₹${data.new_balance}`;
            document.getElementById('availableBalance').textContent = `₹${data.new_balance}`;
            
            const walletBadge = document.getElementById('walletBadge');
            if (walletBadge) {
                walletBadge.textContent = `₹${data.new_balance}`;
            }
            
            // Reload transactions
            await loadTransactionHistory();
        } else {
            alert(data.message || 'Payment verification failed!');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Payment verification failed: ' + error.message + '\n\nPlease contact support if amount was deducted.');
    }
}

// Handle withdraw
function handleWithdraw(event) {
    event.preventDefault();
    const amount = document.getElementById('withdrawAmount').value;
    const method = document.getElementById('withdrawMethod').value;
    const balance = parseFloat(currentUserData.wallet) || 0;
    
    if (!method) {
        alert('Please select a withdrawal method!');
        return;
    }
    
    if (amount && parseFloat(amount) > 0) {
        if (parseFloat(amount) > balance) {
            alert('Insufficient balance! You cannot withdraw more than your current balance.');
        } else {
            alert(`Withdraw Money feature coming soon!\nAmount: ₹${amount}\nMethod: ${method}\n\nThis will be processed within 24-48 hours.`);
            closeWithdrawModal();
            // Here you would send request to backend
        }
    }
}

// Filter transactions
function filterTransactions(type) {
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    // Filter logic would go here
    console.log('Filtering transactions:', type);
}

// Load transaction history
async function loadTransactionHistory() {
    try {
        const response = await fetch('/get-transactions');
        const data = await response.json();
        
        if (data.success) {
            const transactionList = document.getElementById('transactionList');
            const transactions = data.transactions;
            walletStats = data.stats;
            
            // Update stats
            document.querySelectorAll('.stat-value.green')[0].textContent = `₹${walletStats.total_added}`;
            document.querySelectorAll('.stat-value.red')[0].textContent = `₹${walletStats.total_withdrawn}`;
            
            if (transactions.length === 0) {
                // Show no transactions message (already in HTML)
                return;
            }
            
            // Clear no transactions message
            transactionList.innerHTML = '';
            
            // Add transactions
            transactions.forEach(transaction => {
                const transactionItem = document.createElement('div');
                transactionItem.className = `transaction-item ${transaction.type}`;
                
                transactionItem.innerHTML = `
                    <div class="transaction-icon ${transaction.type}">
                        ${transaction.type === 'credit' ? 
                            '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="19" x2="12" y2="5"></line><polyline points="5 12 12 5 19 12"></polyline></svg>' :
                            '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><polyline points="19 12 12 19 5 12"></polyline></svg>'
                        }
                    </div>
                    <div class="transaction-details">
                        <span class="transaction-description">${transaction.description}</span>
                        <span class="transaction-date">${transaction.created_at}</span>
                        ${transaction.method ? `<span class="transaction-method">${transaction.method}</span>` : ''}
                        ${transaction.contest ? `<span class="transaction-contest">${transaction.contest}</span>` : ''}
                    </div>
                    <div class="transaction-amount ${transaction.type}">
                        ${transaction.type === 'credit' ? '+' : '-'}₹${transaction.amount}
                    </div>
                `;
                
                transactionList.appendChild(transactionItem);
            });
        }
    } catch (error) {
        console.error('Error loading transactions:', error);
    }
}
