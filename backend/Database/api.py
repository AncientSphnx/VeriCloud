"""
API endpoints for authentication and user management.
This module provides Flask routes for user registration, login, and profile management.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from bson import ObjectId
import os

from .operations import (
    create_new_user, get_user_by_email, update_user, get_user_by_id,
    get_user_reports, get_session_reports, get_reports_by_type, get_user_report_stats,
    get_reports_dashboard_data, create_user_report_record, verify_password
)
from .auth import authenticate_user, generate_token, verify_token

# Initialize Flask app
app = Flask(__name__)
# Enable CORS with explicit configuration
CORS(app, 
     origins="*",
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     supports_credentials=True)

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
    
    try:
        # Create new user
        user_id = create_new_user(
            name=data['name'],
            email=data['email'],
            password=data['password']
        )
        
        # Generate token
        token = generate_token(user_id)
        
        # Get user data (without password)
        user = get_user_by_email(data['email'])
        user_data = {
            'id': str(user['_id']),
            'name': user['name'],
            'email': user['email']
        }
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'token': token,
            'user': user_data
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Registration failed: {str(e)}'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login a user"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
    
    try:
        # Authenticate user
        user = authenticate_user(data['email'], data['password'])
        
        if not user:
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
        
        # Generate token
        token = generate_token(str(user['_id']))
        
        # Prepare user data
        user_data = {
            'id': str(user['_id']),
            'name': user['name'],
            'email': user['email']
        }
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': user_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Login failed: {str(e)}'}), 500

@app.route('/api/auth/change-password', methods=['POST'])
def change_password():
    """Change user password"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['currentPassword', 'newPassword']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400

        # Verify token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'No token provided'}), 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return jsonify({'success': False, 'message': 'Invalid or expired token'}), 401

        # Get user data
        user_id_str = payload['user_id']
        try:
            user_id_obj = ObjectId(user_id_str)
            user = get_user_by_id(user_id_obj)
        except:
            return jsonify({'success': False, 'message': 'Invalid user ID'}), 400

        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        # Verify current password
        if not verify_password(user['password'], data['currentPassword']):
            return jsonify({'success': False, 'message': 'Current password is incorrect'}), 401

        # Update password
        success = update_user(user_id_obj, {'password': data['newPassword']})

        if success:
            return jsonify({
                'success': True,
                'message': 'Password changed successfully'
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to update password'}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': f'Password change failed: {str(e)}'}), 500

@app.route('/api/auth/verify', methods=['GET'])
def verify():
    """Verify a user's token"""
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'success': False, 'message': 'No token provided'}), 401

    token = auth_header.split(' ')[1]

    try:
        # Verify token
        payload = verify_token(token)

        if not payload:
            return jsonify({'success': False, 'message': 'Invalid or expired token'}), 401

        # Get user data
        user_id_str = payload['user_id']
        try:
            user_id_obj = ObjectId(user_id_str)
            user = get_user_by_id(user_id_obj)
        except:
            return jsonify({'success': False, 'message': 'Invalid user ID'}), 400

        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        # Prepare user data
        user_data = {
            'id': str(user['_id']),
            'name': user['name'],
            'email': user['email']
        }

        return jsonify({
            'success': True,
            'message': 'Token verified',
            'user': user_data
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Token verification failed: {str(e)}'}), 500

@app.route('/api/reports/session/<session_id>', methods=['GET'])
def get_session_reports_endpoint(session_id):
    """Get all reports for a specific session"""
    try:
        # Verify token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'No token provided'}), 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return jsonify({'success': False, 'message': 'Invalid or expired token'}), 401

        # Get session reports
        reports = get_session_reports(session_id)

        # Convert ObjectId to string for JSON serialization
        for report in reports:
            report['_id'] = str(report['_id'])
            report['user_id'] = str(report['user_id'])
            report['session_id'] = str(report['session_id'])

        return jsonify({
            'success': True,
            'reports': reports,
            'total': len(reports)
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to get session reports: {str(e)}'}), 500

@app.route('/api/reports/user/<user_id>/stats', methods=['GET'])
def get_user_report_stats_endpoint(user_id):
    """Get statistics about user's reports"""
    try:
        # Verify token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'No token provided'}), 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return jsonify({'success': False, 'message': 'Invalid or expired token'}), 401

        # Get user report statistics
        stats = get_user_report_stats(user_id)

        # Convert ObjectId to string for JSON serialization
        if stats['most_recent_report']:
            stats['most_recent_report']['_id'] = str(stats['most_recent_report']['_id'])
            stats['most_recent_report']['user_id'] = str(stats['most_recent_report']['user_id'])
            if 'session_id' in stats['most_recent_report']:
                stats['most_recent_report']['session_id'] = str(stats['most_recent_report']['session_id'])

        # Convert type breakdown ObjectIds
        for stat in stats['type_breakdown']:
            if 'latest_report' in stat and stat['latest_report']:
                stat['latest_report'] = str(stat['latest_report'])

        return jsonify({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to get report stats: {str(e)}'}), 500

@app.route('/api/reports/user/<user_id>/dashboard', methods=['GET'])
def get_reports_dashboard_endpoint(user_id):
    """Get dashboard data for user's recent reports"""
    try:
        # Verify token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'No token provided'}), 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return jsonify({'success': False, 'message': 'Invalid or expired token'}), 401

        # Get query parameters
        days = request.args.get('days', 30, type=int)

        # Get dashboard data
        dashboard_data = get_reports_dashboard_data(user_id, days=days)

        # Convert ObjectIds to strings for JSON serialization
        for report in dashboard_data['recent_reports']:
            report['_id'] = str(report['_id'])
            report['user_id'] = str(report['user_id'])
            if 'session_id' in report:
                report['session_id'] = str(report['session_id'])

        return jsonify({
            'success': True,
            'dashboard': dashboard_data
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to get dashboard data: {str(e)}'}), 500

@app.route('/api/reports/create', methods=['POST'])
def create_report_endpoint():
    """Create a new report"""
    try:
        # Verify token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'No token provided'}), 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return jsonify({'success': False, 'message': 'Invalid or expired token'}), 401

        data = request.get_json()

        # Validate required fields
        required_fields = ['user_id', 'session_id', 'report_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400

        # Create the report
        report_id = create_user_report_record(
            user_id=data['user_id'],
            session_id=data['session_id'],
            report_type=data['report_type'],
            data=data.get('data'),
            s3_file_path=data.get('s3_file_path')
        )

        return jsonify({
            'success': True,
            'message': 'Report created successfully',
            'report_id': report_id
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to create report: {str(e)}'}), 500

# Run the app
def run_auth_api(host='0.0.0.0', port=5001, debug=True):
    """Run the authentication API server"""
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_auth_api()