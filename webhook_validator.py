# File: webhook_validator.py
# Purpose: Implement webhook signature validation for secure callbacks

from flask import Flask, request, jsonify
import hmac
import hashlib
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get webhook secret from environment variables
# You should set this in your .env file
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'your_webhook_secret')

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """
    Handle and validate Alchemy webhook requests
    
    This endpoint validates the signature of incoming webhook requests
    and processes the webhook data if the signature is valid.
    """
    # Get signature from request headers
    signature = request.headers.get('x-alchemy-signature', '')
    
    # Get request body
    payload = request.data
    
    # Calculate signature using your webhook secret
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Verify signature
    if signature != expected_signature:
        print(f"Invalid signature: {signature}")
        print(f"Expected: {expected_signature}")
        return jsonify({"error": "Invalid signature"}), 403
    
    # Process webhook data
    webhook_data = request.json
    print(f"Received webhook: {webhook_data}")
    
    # Process different webhook types
    if webhook_data.get('type') == 'MINED_TRANSACTION':
        handle_mined_transaction(webhook_data)
    elif webhook_data.get('type') == 'ADDRESS_ACTIVITY':
        handle_address_activity(webhook_data)
    
    return jsonify({"status": "success"}), 200

def handle_mined_transaction(data):
    """Handle mined transaction webhook data"""
    print(f"Transaction mined: {data.get('event', {}).get('transaction', {}).get('hash')}")
    # Add your transaction processing logic here

def handle_address_activity(data):
    """Handle address activity webhook data"""
    print(f"Activity for address: {data.get('event', {}).get('address')}")
    # Add your address activity processing logic here

if __name__ == '__main__':
    print(f"Starting webhook server on port 3000...")
    print(f"To test locally with ngrok, run: ngrok http 3000")
    app.run(host='0.0.0.0', port=3000)
