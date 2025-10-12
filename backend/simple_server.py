"""
Simple authentication server for VeriCloud application.
This file provides a basic Flask API server for authentication.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import jwt
import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Secret key for JWT
SECRET_KEY = "vericloud_secret_key"

# In-memory user database (for demo purposes)
users = {}

# Authentication routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
    
    # Check if user already exists
    if data['email'] in users:
        return jsonify({'success': False, 'message': 'User already exists'}), 400
    
    # Create user ID
    user_id = str(uuid.uuid4())
    
    # Store user (in a real app, we would hash the password)
    users[data['email']] = {
        '_id': user_id,
        'name': data['name'],
        'email': data['email'],
        'password': data['password']  # In a real app, this would be hashed
    }
    
    # Generate token
    token = jwt.encode({
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }, SECRET_KEY, algorithm='HS256')
    
    # Return user data and token
    return jsonify({
        'success': True,
        'message': 'User registered successfully',
        'token': token,
        'user': {
            'id': user_id,
            'name': data['name'],
            'email': data['email']
        }
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login a user"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
    
    # Check if user exists
    if data['email'] not in users:
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
    
    # Check password
    user = users[data['email']]
    if user['password'] != data['password']:
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
    
    # Generate token
    token = jwt.encode({
        'user_id': user['_id'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }, SECRET_KEY, algorithm='HS256')
    
    # Return user data and token
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': user['_id'],
            'name': user['name'],
            'email': user['email']
        }
    })

@app.route('/api/auth/verify', methods=['GET'])
def verify():
    """Verify a user's token"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'success': False, 'message': 'No token provided'}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        # Verify token
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        
        # Find user
        user = None
        for u in users.values():
            if u['_id'] == user_id:
                user = u
                break
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Return user data
        return jsonify({
            'success': True,
            'message': 'Token verified',
            'user': {
                'id': user['_id'],
                'name': user['name'],
                'email': user['email']
            }
        })
    except jwt.ExpiredSignatureError:
        return jsonify({'success': False, 'message': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'success': False, 'message': 'Invalid token'}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)