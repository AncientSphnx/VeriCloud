"""
Authentication functionality for the lie detection project.
This module provides functions for user authentication and JWT token management.
"""
import jwt
import datetime
import os
from dotenv import load_dotenv

from .operations import get_user_by_email, verify_password

load_dotenv()

# JWT Configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-here')  # Change in production
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION = 24  # hours

def authenticate_user(email, password):
    """
    Authenticate a user with email and password
    
    Args:
        email (str): User email
        password (str): User password
        
    Returns:
        dict: User document if authentication successful, None otherwise
    """
    user = get_user_by_email(email)
    
    if not user:
        return None
    
    if verify_password(user['password'], password):
        # Remove password from user object before returning
        user_without_password = {k: v for k, v in user.items() if k != 'password'}
        return user_without_password
    
    return None

def generate_token(user_id):
    """
    Generate a JWT token for a user
    
    Args:
        user_id (str): User ID
        
    Returns:
        str: JWT token
    """
    payload = {
        'user_id': str(user_id),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRATION)
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def verify_token(token):
    """
    Verify a JWT token
    
    Args:
        token (str): JWT token
        
    Returns:
        dict: Token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.InvalidTokenError:
        # Invalid token
        return None