"""Payment integration with Razorpay for Fantasy IQ application"""
import razorpay
from modules.config import Config

# Initialize Razorpay client
razorpay_client = None

def init_razorpay():
    """Initialize Razorpay client"""
    global razorpay_client
    try:
        if Config.RAZORPAY_KEY_ID and Config.RAZORPAY_KEY_SECRET:
            razorpay_client = razorpay.Client(auth=(Config.RAZORPAY_KEY_ID, Config.RAZORPAY_KEY_SECRET))
            print("Razorpay client initialized successfully")
            return razorpay_client
        else:
            print("Razorpay credentials not configured")
            return None
    except Exception as e:
        print(f"Error initializing Razorpay: {e}")
        return None

def get_razorpay_client():
    """Get the Razorpay client instance"""
    global razorpay_client
    if razorpay_client is None:
        razorpay_client = init_razorpay()
    return razorpay_client
