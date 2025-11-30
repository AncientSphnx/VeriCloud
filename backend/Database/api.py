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
    get_reports_dashboard_data, create_user_report_record, verify_password,
    create_new_analysis, get_analysis_by_id, get_user_analyses, update_analysis_files,
    update_analysis_results, update_analysis_status, get_user_analysis_stats,
    add_analysis_error, delete_analysis,
    create_simple_report, get_user_simple_reports, get_user_report_summary,
    delete_simple_report, delete_all_user_simple_reports
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

@app.route('/api/reports/user/<user_id>', methods=['GET'])
def get_user_reports_endpoint(user_id):
    """Get all reports for a user (backward compatibility - redirects to simple reports)"""
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
        limit = request.args.get('limit', 50, type=int)

        # Get simple reports (new auto-save system)
        reports = get_user_simple_reports(user_id, limit=limit)

        return jsonify({
            'success': True,
            'reports': reports,
            'total': len(reports)
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to get user reports: {str(e)}'}), 500

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

# ----------------------------
# Analysis endpoints
# ----------------------------

@app.route('/api/analysis/create', methods=['POST'])
def create_analysis_endpoint():
    """Create a new analysis record"""
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
        required_fields = ['user_id', 'session_id', 'analysis_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400

        # Create the analysis
        mongo_id = create_new_analysis(
            user_id=data['user_id'],
            session_id=data['session_id'],
            analysis_id=data['analysis_id']
        )

        return jsonify({
            'success': True,
            'message': 'Analysis created successfully',
            'mongo_id': mongo_id,
            'analysis_id': data['analysis_id']
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to create analysis: {str(e)}'}), 500

@app.route('/api/analysis/<analysis_id>', methods=['GET'])
def get_analysis_endpoint(analysis_id):
    """Get a specific analysis by ID"""
    try:
        # Verify token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'No token provided'}), 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return jsonify({'success': False, 'message': 'Invalid or expired token'}), 401

        # Get analysis
        analysis = get_analysis_by_id(analysis_id)

        if not analysis:
            return jsonify({'success': False, 'message': 'Analysis not found'}), 404

        # Convert ObjectIds to strings for JSON serialization
        analysis['_id'] = str(analysis['_id'])
        analysis['user_id'] = str(analysis['user_id'])
        analysis['session_id'] = str(analysis['session_id'])

        return jsonify({
            'success': True,
            'analysis': analysis
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to get analysis: {str(e)}'}), 500

@app.route('/api/analysis/user/<user_id>', methods=['GET'])
def get_user_analyses_endpoint(user_id):
    """Get all analyses for a specific user"""
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
        limit = request.args.get('limit', 50, type=int)
        skip = request.args.get('skip', 0, type=int)
        status = request.args.get('status', None, type=str)

        # Get analyses
        analyses = get_user_analyses(user_id, limit=limit, skip=skip, status=status)

        # Convert ObjectIds to strings for JSON serialization
        for analysis in analyses:
            analysis['_id'] = str(analysis['_id'])
            analysis['user_id'] = str(analysis['user_id'])
            analysis['session_id'] = str(analysis['session_id'])

        return jsonify({
            'success': True,
            'analyses': analyses,
            'total': len(analyses)
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to get user analyses: {str(e)}'}), 500

@app.route('/api/analysis/<analysis_id>/files', methods=['PATCH'])
def update_analysis_files_endpoint(analysis_id):
    """Update file information for an analysis"""
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
        required_fields = ['file_type', 'file_data']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400

        # Update files
        success = update_analysis_files(
            analysis_id=analysis_id,
            file_type=data['file_type'],
            file_data=data['file_data']
        )

        if success:
            return jsonify({
                'success': True,
                'message': 'Analysis files updated successfully'
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to update analysis files'}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to update analysis files: {str(e)}'}), 500

@app.route('/api/analysis/<analysis_id>/results', methods=['PATCH'])
def update_analysis_results_endpoint(analysis_id):
    """Update prediction results for an analysis"""
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
        required_fields = ['model_type', 'results_data']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400

        # Update results
        success = update_analysis_results(
            analysis_id=analysis_id,
            model_type=data['model_type'],
            results_data=data['results_data']
        )

        if success:
            return jsonify({
                'success': True,
                'message': 'Analysis results updated successfully'
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to update analysis results'}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to update analysis results: {str(e)}'}), 500

@app.route('/api/analysis/<analysis_id>/status', methods=['PATCH'])
def update_analysis_status_endpoint(analysis_id):
    """Update analysis status"""
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
        if 'status' not in data:
            return jsonify({'success': False, 'message': 'Missing required field: status'}), 400

        # Update status
        success = update_analysis_status(
            analysis_id=analysis_id,
            status=data['status'],
            metadata_updates=data.get('metadata_updates')
        )

        if success:
            return jsonify({
                'success': True,
                'message': 'Analysis status updated successfully'
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to update analysis status'}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to update analysis status: {str(e)}'}), 500

@app.route('/api/analysis/user/<user_id>/stats', methods=['GET'])
def get_user_analysis_stats_endpoint(user_id):
    """Get statistics about user's analyses"""
    try:
        # Verify token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'No token provided'}), 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return jsonify({'success': False, 'message': 'Invalid or expired token'}), 401

        # Get stats
        stats = get_user_analysis_stats(user_id)

        # Convert ObjectIds to strings for JSON serialization
        if stats['most_recent_analysis']:
            stats['most_recent_analysis']['_id'] = str(stats['most_recent_analysis']['_id'])
            stats['most_recent_analysis']['user_id'] = str(stats['most_recent_analysis']['user_id'])
            stats['most_recent_analysis']['session_id'] = str(stats['most_recent_analysis']['session_id'])

        return jsonify({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to get analysis stats: {str(e)}'}), 500

@app.route('/api/analysis/<analysis_id>', methods=['DELETE'])
def delete_analysis_endpoint(analysis_id):
    """Delete an analysis"""
    try:
        # Verify token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'No token provided'}), 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return jsonify({'success': False, 'message': 'Invalid or expired token'}), 401

        # Delete analysis
        success = delete_analysis(analysis_id)

        if success:
            return jsonify({
                'success': True,
                'message': 'Analysis deleted successfully'
            })
        else:
            return jsonify({'success': False, 'message': 'Analysis not found or already deleted'}), 404

    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to delete analysis: {str(e)}'}), 500

# ----------------------------
# Simple Report Endpoints (No AWS Required)
# ----------------------------

@app.route('/api/simple_reports/create_unauth', methods=['POST'])
def create_simple_report_unauth_endpoint():
    """Create a simple report without authentication (for module APIs)"""
    try:
        data = request.get_json()
        
        # Log the request for debugging
        print(f"🔍 Unauth report create request: {data}")

        # Validate required fields
        required_fields = ['user_id', 'module_type', 'prediction', 'confidence']
        for field in required_fields:
            if field not in data:
                print(f"❌ Missing required field: {field}")
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400

        # Validate module_type
        if data['module_type'] not in ['text', 'voice', 'face']:
            print(f"❌ Invalid module_type: {data['module_type']}")
            return jsonify({'success': False, 'message': 'module_type must be text, voice, or face'}), 400

        # Validate prediction
        if data['prediction'] not in ['Truthful', 'Deceptive']:
            print(f"❌ Invalid prediction: {data['prediction']}")
            return jsonify({'success': False, 'message': 'prediction must be Truthful or Deceptive'}), 400

        # Create the simple report
        report_id = create_simple_report(
            user_id=data['user_id'],
            module_type=data['module_type'],
            prediction=data['prediction'],
            confidence=float(data['confidence']),
            session_id=data.get('session_id')
        )
        
        print(f"✅ Unauth report created: {report_id}")

        return jsonify({
            'success': True,
            'message': 'Report created successfully',
            'report_id': report_id,
            'confidence_percentage': round(float(data['confidence']) * 100, 2)
        })

    except Exception as e:
        print(f"❌ Unauth report creation error: {e}")
        return jsonify({'success': False, 'message': f'Failed to create report: {str(e)}'}), 500

@app.route('/api/simple_reports/create', methods=['POST'])
def create_simple_report_endpoint():
    """Create a simple report without AWS dependency"""
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
        required_fields = ['user_id', 'module_type', 'prediction', 'confidence']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400

        # Validate module_type
        if data['module_type'] not in ['text', 'voice', 'face']:
            return jsonify({'success': False, 'message': 'module_type must be text, voice, or face'}), 400

        # Validate prediction
        if data['prediction'] not in ['Truthful', 'Deceptive']:
            return jsonify({'success': False, 'message': 'prediction must be Truthful or Deceptive'}), 400

        # Create the simple report
        report_id = create_simple_report(
            user_id=data['user_id'],
            module_type=data['module_type'],
            prediction=data['prediction'],
            confidence=float(data['confidence']),
            session_id=data.get('session_id')
        )

        return jsonify({
            'success': True,
            'message': 'Report created successfully',
            'report_id': report_id,
            'confidence_percentage': round(float(data['confidence']) * 100, 2)
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to create report: {str(e)}'}), 500

@app.route('/api/simple_reports/user/<user_id>', methods=['GET'])
def get_user_simple_reports_endpoint(user_id):
    """Get simple reports for a user"""
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
        limit = request.args.get('limit', 50, type=int)
        module_type = request.args.get('module_type', None, type=str)

        # Get reports
        reports = get_user_simple_reports(user_id, limit=limit, module_type=module_type)

        return jsonify({
            'success': True,
            'reports': reports,
            'total': len(reports)
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to get reports: {str(e)}'}), 500

@app.route('/api/simple_reports/user/<user_id>/summary', methods=['GET'])
def get_user_report_summary_endpoint(user_id):
    """Get summary statistics for user's reports"""
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

        # Get summary
        summary = get_user_report_summary(user_id, days=days)

        return jsonify({
            'success': True,
            'summary': summary
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to get report summary: {str(e)}'}), 500

@app.route('/api/simple_reports/<report_id>', methods=['DELETE'])
def delete_simple_report_endpoint(report_id):
    """Delete a single simple report by ID"""
    try:
        # Verify token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'No token provided'}), 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return jsonify({'success': False, 'message': 'Invalid token'}), 401

        # Delete the report
        success = delete_simple_report(report_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Report deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Report not found or could not be deleted'
            }), 404

    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to delete report: {str(e)}'}), 500

@app.route('/api/simple_reports/user/<user_id>', methods=['DELETE'])
def delete_all_user_simple_reports_endpoint(user_id):
    """Delete all simple reports for a user"""
    try:
        # Verify token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'No token provided'}), 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return jsonify({'success': False, 'message': 'Invalid token'}), 401

        # Verify user can only delete their own reports
        if payload.get('user_id') != user_id:
            return jsonify({'success': False, 'message': 'Unauthorized to delete reports for this user'}), 403

        # Delete all reports for this user
        deleted_count = delete_all_user_simple_reports(user_id)
        
        return jsonify({
            'success': True,
            'message': f'Successfully deleted {deleted_count} reports',
            'deleted_count': deleted_count
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to delete all reports: {str(e)}'}), 500

# Run the app
def run_auth_api(host='0.0.0.0', port=5001, debug=True):
    """Run the authentication API server"""
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_auth_api()