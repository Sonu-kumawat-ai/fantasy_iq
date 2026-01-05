# Fantasy IQ - Fantasy Sports Website

A fantasy sports platform built with Flask, MongoDB, HTML, CSS, and JavaScript.

## Features

- User Registration & Login
- User Authentication with Session Management
- MongoDB Database Integration
- Wallet System (₹0 for new users)
- Responsive Design with Red & Yellow Theme
- Ad Carousel/Rotator
- Contest Cards Layout
- Dynamic Welcome Message

## Prerequisites

- Python 3.7+
- MongoDB (running on localhost:27017)
- Virtual Environment

## Installation

1. Create and activate virtual environment:
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # For Windows PowerShell
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Copy the example environment file
copy .env.example .env

# Edit .env file and add your configuration:
# - Generate a SECRET_KEY
# - Add your MongoDB URI (default: mongodb://localhost:27017/)
# - Add your Razorpay API keys from https://dashboard.razorpay.com/app/keys
```

4. Make sure MongoDB is running on your system

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Flask Configuration
SECRET_KEY=your_secret_key_here

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=fantasy_iq_db

# Razorpay Configuration
RAZORPAY_KEY_ID=rzp_test_YOUR_KEY_ID
RAZORPAY_KEY_SECRET=YOUR_KEY_SECRET

# Application Configuration
FLASK_ENV=development
DEBUG=True
PORT=5000
```

### Getting Razorpay Keys:
1. Sign up at https://razorpay.com/
2. Go to Dashboard → Settings → API Keys
3. Generate Test Keys for development
4. Copy Key ID and Key Secret to your `.env` file

**Important:** Never commit your `.env` file to version control!

## Running the Application

1. Activate virtual environment:
```bash
.\venv\Scripts\Activate.ps1  # For Windows PowerShell
```

2. Run the Flask application:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## Project Structure

```
fantasy IQ/
│
├── app.py                 # Flask backend
├── templates/
│   ├── index.html        # Home page
│   └── login.html        # Login/Register page
├── static/
│   ├── css/
│   │   └── style.css     # Styling with red-yellow theme
│   ├── js/
│   │   └── script.js     # Frontend JavaScript
│   └── images/           # Image assets
├── venv/                 # Virtual environment
└── README.md            # This file
```

## Database Schema

### Users Collection
```json
{
    "username": "string",
    "email": "string",
    "password": "string",
    "wallet": 0,
    "created_at": "datetime"
}
```

## Features Overview

### Home Page
- Welcome section with personalized greeting
- Navigation bar with Login/Register buttons
- Ad carousel with 3 rotating banners
- Contest cards with prize pool, entry fee, and spots information
- Footer with links

### Login/Register Page
- Toggle between login and register forms
- Form validation
- Success/Error messages
- Automatic redirect after login
- New users get ₹0 wallet balance

### User Session
- Session management using Flask sessions
- Logged-in users see their username in navbar
- Wallet balance displayed
- Logout functionality

## Technologies Used

- **Frontend**: HTML5, CSS3, JavaScript
- **Backend**: Flask (Python)
- **Database**: MongoDB
- **Theme**: Red (#DC143C) and Yellow (#FFD700)

## Security Note

⚠️ **Important**: This is a demonstration project. In production:
- Use password hashing (bcrypt, werkzeug.security)
- Implement CSRF protection
- Use environment variables for sensitive data
- Add input validation and sanitization
- Implement rate limiting
- Use HTTPS

## Future Enhancements

- Password hashing
- Email verification
- Forgot password functionality
- Contest joining functionality
- User profile page
- Wallet recharge system
- Admin dashboard
- Real-time contest updates

## License

This project is for educational purposes.
