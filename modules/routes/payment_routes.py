"""Payment and wallet routes for Fantasy IQ application"""
from flask import request, jsonify, session
from datetime import datetime
from modules.config import Config

def register_payment_routes(app, db, razorpay_client):
    """Register all payment and wallet related routes"""
    
    # Get collections from db
    users_collection = db['users']
    transactions_collection = db['transactions']
    
    @app.route('/create-order', methods=['POST'])
    def create_order():
        try:
            if 'username' not in session:
                print("User not logged in - session missing username")
                return jsonify({'success': False, 'message': 'Please login first'}), 401
            
            data = request.get_json()
            print(f"Create order request data: {data}")
            
            amount = int(data.get('amount'))  # Amount in rupees
            
            if amount <= 0:
                print(f"Invalid amount: {amount}")
                return jsonify({'success': False, 'message': 'Invalid amount'}), 400
            
            print(f"Creating Razorpay order for amount: ₹{amount}")
            
            # Create Razorpay order
            order_data = {
                'amount': amount * 100,  # Convert to paise (Razorpay uses paise)
                'currency': 'INR',
                'payment_capture': 1
            }
            
            razorpay_order = razorpay_client.order.create(data=order_data)
            print(f"Razorpay order created: {razorpay_order['id']}")
            
            # Store pending transaction in database
            transaction = {
                'username': session['username'],
                'email': session['email'],
                'type': 'credit',
                'amount': amount,
                'status': 'pending',
                'order_id': razorpay_order['id'],
                'description': 'Add Money to Wallet',
                'method': 'Razorpay',
                'created_at': datetime.now()
            }
            
            transactions_collection.insert_one(transaction)
            print(f"Transaction stored in database for user: {session['username']}")
            
            return jsonify({
                'success': True,
                'order_id': razorpay_order['id'],
                'razorpay_key_id': Config.RAZORPAY_KEY_ID,
                'key_id': Config.RAZORPAY_KEY_ID,  # For wallet.js compatibility
                'amount': amount,
                'order': {
                    'id': razorpay_order['id'],
                    'amount': amount * 100,  # For profile.js compatibility
                    'currency': 'INR'
                }
            }), 200
            
        except Exception as e:
            print(f"Error in create_order: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

    @app.route('/verify-payment', methods=['POST'])
    def verify_payment():
        try:
            if 'username' not in session:
                return jsonify({'success': False, 'message': 'Please login first'}), 401
            
            data = request.get_json()
            razorpay_order_id = data.get('razorpay_order_id')
            razorpay_payment_id = data.get('razorpay_payment_id')
            razorpay_signature = data.get('razorpay_signature')
            
            # Verify payment signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            try:
                razorpay_client.utility.verify_payment_signature(params_dict)
                
                # Payment verified successfully
                # Update transaction status
                transaction = transactions_collection.find_one({'order_id': razorpay_order_id})
                
                if transaction:
                    transactions_collection.update_one(
                        {'order_id': razorpay_order_id},
                        {
                            '$set': {
                                'status': 'success',
                                'payment_id': razorpay_payment_id,
                                'updated_at': datetime.now()
                            }
                        }
                    )
                    
                    # Update user wallet
                    users_collection.update_one(
                        {'username': session['username']},
                        {'$inc': {'wallet': transaction['amount']}}
                    )
                    
                    # Update session
                    user = users_collection.find_one({'username': session['username']})
                    session['wallet'] = user['wallet']
                    
                    return jsonify({
                        'success': True,
                        'message': 'Payment successful! Money added to wallet.',
                        'new_balance': user['wallet'],
                        'new_wallet_balance': user['wallet']  # For profile.js compatibility
                    }), 200
                else:
                    return jsonify({'success': False, 'message': 'Transaction not found'}), 404
                    
            except Exception as e:
                # Payment verification failed
                print(f"Signature verification failed: {str(e)}")
                transactions_collection.update_one(
                    {'order_id': razorpay_order_id},
                    {
                        '$set': {
                            'status': 'failed',
                            'updated_at': datetime.now()
                        }
                    }
                )
                return jsonify({'success': False, 'message': 'Payment verification failed'}), 400
                
        except Exception as e:
            print(f"Error in verify_payment: {str(e)}")
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

    @app.route('/get-transactions', methods=['GET'])
    def get_transactions():
        try:
            if 'username' not in session:
                return jsonify({'success': False, 'message': 'Please login first'}), 401
            
            # Get all successful transactions for the user
            transactions = list(transactions_collection.find(
                {
                    'username': session['username'], 
                    'status': 'success'
                },
                {'_id': 0}
            ).sort('created_at', -1))
            
            # Convert datetime to string
            for trans in transactions:
                if 'created_at' in trans:
                    trans['created_at'] = trans['created_at'].strftime('%Y-%m-%d')
            
            # Calculate stats (only credit transactions for total_added, exclude contest entries from withdrawn)
            total_added = sum(t['amount'] for t in transactions if t['type'] == 'credit')
            # Don't count contest entry fees as withdrawals
            total_withdrawn = 0
            
            return jsonify({
                'success': True,
                'transactions': transactions,
                'stats': {
                    'total_added': total_added,
                    'total_withdrawn': total_withdrawn
                }
            }), 200
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
