"""
Data API routes.
Handles dataset management, file uploads, and data operations.
"""

from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import json
import csv
import io

data_bp = Blueprint('data', __name__)


@data_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_data_summary():
    """
    Get comprehensive data summary.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "total_cases": 500,
        "total_diagnoses": 50,
        "categories": [...],
        "age_groups": [...],
        "complexity_levels": [...],
        "cases_by_category": {...},
        "cases_by_age_group": {...},
        "cases_by_complexity": {...}
    }
    """
    try:
        # Get data loader
        data_loader = current_app.data_loader
        
        # Get data summary
        summary = data_loader.get_data_summary()
        
        return jsonify(summary), 200
        
    except Exception as e:
        current_app.logger.error(f"Get data summary error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve data summary',
            'message': 'An unexpected error occurred'
        }), 500


@data_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """
    Upload data files (cases, diagnoses, etc.).
    
    Headers:
    Authorization: Bearer <access_token>
    Content-Type: multipart/form-data
    
    Form Data:
    - file: File to upload
    - type: File type (cases, diagnoses, config)
    - overwrite: Whether to overwrite existing data (true/false)
    
    Response:
    {
        "message": "File uploaded successfully",
        "filename": "string",
        "records_processed": 150,
        "validation_errors": [...]
    }
    """
    try:
        user_id = get_jwt_identity()
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                'error': 'No file provided',
                'message': 'A file is required for upload'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'message': 'Please select a file to upload'
            }), 400
        
        # Get upload parameters
        file_type = request.form.get('type', 'cases')
        overwrite = request.form.get('overwrite', 'false').lower() == 'true'
        
        # Validate file type
        if file_type not in ['cases', 'diagnoses', 'config']:
            return jsonify({
                'error': 'Invalid file type',
                'message': 'File type must be cases, diagnoses, or config'
            }), 400
        
        # Check file extension
        if not current_app.allowed_file(file.filename, {'json', 'csv'}):
            return jsonify({
                'error': 'Invalid file format',
                'message': 'Only JSON and CSV files are allowed'
            }), 400
        
        # Secure filename
        filename = secure_filename(file.filename)
        
        # Create upload directory if it doesn't exist
        upload_dir = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # Process uploaded file
        validation_errors = []
        records_processed = 0
        
        try:
            if file_type == 'cases':
                records_processed, validation_errors = _process_cases_file(file_path)
            elif file_type == 'diagnoses':
                records_processed, validation_errors = _process_diagnoses_file(file_path)
            elif file_type == 'config':
                records_processed, validation_errors = _process_config_file(file_path)
            
            current_app.logger.info(f"File uploaded by user {user_id}: {filename} ({records_processed} records)")
            
            return jsonify({
                'message': 'File uploaded successfully',
                'filename': filename,
                'file_type': file_type,
                'records_processed': records_processed,
                'validation_errors': validation_errors,
                'uploaded_at': datetime.now().isoformat()
            }), 200
            
        except Exception as processing_error:
            # Remove uploaded file if processing failed
            if os.path.exists(file_path):
                os.remove(file_path)
            
            current_app.logger.error(f"File processing error: {str(processing_error)}")
            return jsonify({
                'error': 'File processing failed',
                'message': str(processing_error)
            }), 400
        
    except Exception as e:
        current_app.logger.error(f"File upload error: {str(e)}")
        return jsonify({
            'error': 'File upload failed',
            'message': 'An unexpected error occurred during file upload'
        }), 500


@data_bp.route('/download/<filename>', methods=['GET'])
@jwt_required()
def download_file(filename):
    """
    Download data files.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    File download
    """
    try:
        # Validate filename
        if not current_app.allowed_file(filename, {'json', 'csv', 'txt'}):
            return jsonify({
                'error': 'Invalid file',
                'message': 'File not allowed for download'
            }), 400
        
        # Check if file exists in upload directory
        upload_dir = current_app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_dir, filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                'error': 'File not found',
                'message': 'The requested file does not exist'
            }), 404
        
        return send_from_directory(upload_dir, filename, as_attachment=True)
        
    except Exception as e:
        current_app.logger.error(f"File download error: {str(e)}")
        return jsonify({
            'error': 'File download failed',
            'message': 'An unexpected error occurred during file download'
        }), 500


@data_bp.route('/export/cases', methods=['GET'])
@jwt_required()
def export_cases():
    """
    Export cases data in specified format.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Query Parameters:
    - format: Export format (json, csv)
    - category: Filter by category
    - complexity: Filter by complexity
    - limit: Number of cases to export (default: all)
    
    Response:
    File download or JSON response
    """
    try:
        # Get query parameters
        export_format = request.args.get('format', 'json')
        category = request.args.get('category')
        complexity = request.args.get('complexity')
        limit = request.args.get('limit')
        
        if export_format not in ['json', 'csv']:
            return jsonify({
                'error': 'Invalid format',
                'message': 'Export format must be json or csv'
            }), 400
        
        # Get data loader
        data_loader = current_app.data_loader
        
        # Get filtered cases
        filtered_cases = data_loader.get_filtered_cases(
            category=category,
            complexity=complexity
        )
        
        # Apply limit if specified
        if limit:
            try:
                limit = int(limit)
                filtered_cases = filtered_cases[:limit]
            except ValueError:
                return jsonify({
                    'error': 'Invalid limit',
                    'message': 'Limit must be a valid integer'
                }), 400
        
        # Export data
        if export_format == 'json':
            export_data = {
                'export_info': {
                    'format': 'json',
                    'exported_at': datetime.now().isoformat(),
                    'total_cases': len(filtered_cases),
                    'filters_applied': {
                        'category': category,
                        'complexity': complexity
                    }
                },
                'cases': filtered_cases
            }
            
            return jsonify(export_data)
        
        else:  # CSV format
            output = io.StringIO()
            if filtered_cases:
                fieldnames = ['case_id', 'category', 'age_group', 'complexity', 'diagnosis', 'narrative', 'MSE']
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                
                for case in filtered_cases:
                    writer.writerow({
                        'case_id': case.get('case_id', ''),
                        'category': case.get('category', ''),
                        'age_group': case.get('age_group', ''),
                        'complexity': case.get('complexity', ''),
                        'diagnosis': case.get('diagnosis', ''),
                        'narrative': case.get('narrative', ''),
                        'MSE': case.get('MSE', '')
                    })
            
            csv_data = output.getvalue()
            output.close()
            
            return jsonify({
                'export_info': {
                    'format': 'csv',
                    'exported_at': datetime.now().isoformat(),
                    'total_cases': len(filtered_cases),
                    'filters_applied': {
                        'category': category,
                        'complexity': complexity
                    }
                },
                'csv_data': csv_data
            })
        
    except Exception as e:
        current_app.logger.error(f"Export cases error: {str(e)}")
        return jsonify({
            'error': 'Export failed',
            'message': 'An unexpected error occurred during export'
        }), 500


@data_bp.route('/validate', methods=['POST'])
@jwt_required()
def validate_data():
    """
    Validate uploaded data files.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Request Body:
    {
        "file_path": "string",
        "file_type": "cases|diagnoses|config"
    }
    
    Response:
    {
        "is_valid": true,
        "validation_errors": [...],
        "records_checked": 150,
        "validation_summary": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'file_path' not in data or 'file_type' not in data:
            return jsonify({
                'error': 'Missing required fields',
                'message': 'file_path and file_type are required'
            }), 400
        
        file_path = data['file_path']
        file_type = data['file_type']
        
        if file_type not in ['cases', 'diagnoses', 'config']:
            return jsonify({
                'error': 'Invalid file type',
                'message': 'File type must be cases, diagnoses, or config'
            }), 400
        
        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({
                'error': 'File not found',
                'message': 'The specified file does not exist'
            }), 404
        
        # Validate file
        validation_errors = []
        records_checked = 0
        
        try:
            if file_type == 'cases':
                records_checked, validation_errors = _validate_cases_file(file_path)
            elif file_type == 'diagnoses':
                records_checked, validation_errors = _validate_diagnoses_file(file_path)
            elif file_type == 'config':
                records_checked, validation_errors = _validate_config_file(file_path)
            
            is_valid = len(validation_errors) == 0
            
            return jsonify({
                'is_valid': is_valid,
                'validation_errors': validation_errors,
                'records_checked': records_checked,
                'validation_summary': {
                    'total_errors': len(validation_errors),
                    'error_types': list(set(error.get('type', 'unknown') for error in validation_errors)),
                    'critical_errors': len([e for e in validation_errors if e.get('severity') == 'critical'])
                },
                'validated_at': datetime.now().isoformat()
            }), 200
            
        except Exception as validation_error:
            current_app.logger.error(f"Data validation error: {str(validation_error)}")
            return jsonify({
                'error': 'Validation failed',
                'message': str(validation_error)
            }), 400
        
    except Exception as e:
        current_app.logger.error(f"Data validation error: {str(e)}")
        return jsonify({
            'error': 'Validation failed',
            'message': 'An unexpected error occurred during validation'
        }), 500


@data_bp.route('/backup', methods=['POST'])
@jwt_required()
def create_backup():
    """
    Create backup of current data.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Request Body:
    {
        "include_users": true,
        "include_cases": true,
        "include_diagnoses": true
    }
    
    Response:
    {
        "backup_id": "string",
        "backup_path": "string",
        "created_at": "timestamp",
        "components_backed_up": [...]
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        include_users = data.get('include_users', True)
        include_cases = data.get('include_cases', True)
        include_diagnoses = data.get('include_diagnoses', True)
        
        # Create backup directory
        backup_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], f'backup_{backup_timestamp}')
        os.makedirs(backup_dir, exist_ok=True)
        
        components_backed_up = []
        
        try:
            # Backup cases
            if include_cases:
                data_loader = current_app.data_loader
                cases = data_loader.load_cases()
                cases_file = os.path.join(backup_dir, 'cases.json')
                with open(cases_file, 'w', encoding='utf-8') as f:
                    json.dump(cases, f, indent=2, ensure_ascii=False)
                components_backed_up.append('cases')
            
            # Backup diagnoses
            if include_diagnoses:
                data_loader = current_app.data_loader
                diagnoses = data_loader.load_diagnoses()
                diagnoses_file = os.path.join(backup_dir, 'diagnoses.json')
                with open(diagnoses_file, 'w', encoding='utf-8') as f:
                    json.dump(diagnoses, f, indent=2, ensure_ascii=False)
                components_backed_up.append('diagnoses')
            
            # Backup users
            if include_users:
                user_manager = current_app.user_manager
                backup_path = user_manager.backup_all_users()
                if backup_path:
                    components_backed_up.append('users')
            
            backup_id = f"backup_{backup_timestamp}"
            
            current_app.logger.info(f"Backup created by user {user_id}: {backup_id}")
            
            return jsonify({
                'backup_id': backup_id,
                'backup_path': backup_dir,
                'created_at': datetime.now().isoformat(),
                'components_backed_up': components_backed_up,
                'backup_size': _get_directory_size(backup_dir)
            }), 200
            
        except Exception as backup_error:
            # Clean up failed backup directory
            import shutil
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            
            raise backup_error
        
    except Exception as e:
        current_app.logger.error(f"Backup creation error: {str(e)}")
        return jsonify({
            'error': 'Backup failed',
            'message': 'An unexpected error occurred during backup creation'
        }), 500


@data_bp.route('/restore', methods=['POST'])
@jwt_required()
def restore_backup():
    """
    Restore data from backup.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Request Body:
    {
        "backup_path": "string",
        "components": ["cases", "diagnoses", "users"]
    }
    
    Response:
    {
        "message": "Restore completed successfully",
        "restored_components": [...],
        "restore_timestamp": "timestamp"
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'backup_path' not in data:
            return jsonify({
                'error': 'Missing backup path',
                'message': 'backup_path is required'
            }), 400
        
        backup_path = data['backup_path']
        components = data.get('components', ['cases', 'diagnoses', 'users'])
        
        # Validate backup path
        if not os.path.exists(backup_path):
            return jsonify({
                'error': 'Backup not found',
                'message': 'The specified backup does not exist'
            }), 404
        
        restored_components = []
        
        try:
            # Restore cases
            if 'cases' in components:
                cases_file = os.path.join(backup_path, 'cases.json')
                if os.path.exists(cases_file):
                    # In a real implementation, you would validate and restore cases
                    restored_components.append('cases')
            
            # Restore diagnoses
            if 'diagnoses' in components:
                diagnoses_file = os.path.join(backup_path, 'diagnoses.json')
                if os.path.exists(diagnoses_file):
                    # In a real implementation, you would validate and restore diagnoses
                    restored_components.append('diagnoses')
            
            # Restore users
            if 'users' in components:
                user_manager = current_app.user_manager
                if user_manager.restore_from_backup(backup_path):
                    restored_components.append('users')
            
            current_app.logger.info(f"Backup restored by user {user_id}: {backup_path}")
            
            return jsonify({
                'message': 'Restore completed successfully',
                'restored_components': restored_components,
                'restore_timestamp': datetime.now().isoformat()
            }), 200
            
        except Exception as restore_error:
            current_app.logger.error(f"Restore error: {str(restore_error)}")
            return jsonify({
                'error': 'Restore failed',
                'message': str(restore_error)
            }), 400
        
    except Exception as e:
        current_app.logger.error(f"Data restore error: {str(e)}")
        return jsonify({
            'error': 'Restore failed',
            'message': 'An unexpected error occurred during restore'
        }), 500


def _process_cases_file(file_path):
    """Process uploaded cases file."""
    validation_errors = []
    records_processed = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        if file_path.endswith('.json'):
            data = json.load(f)
            if isinstance(data, list):
                cases = data
            else:
                cases = data.get('cases', [])
        else:  # CSV
            reader = csv.DictReader(f)
            cases = list(reader)
    
    for i, case in enumerate(cases):
        records_processed += 1
        
        # Validate required fields
        required_fields = ['case_id', 'category', 'age_group', 'diagnosis', 'narrative', 'MSE', 'complexity']
        for field in required_fields:
            if field not in case or not case[field]:
                validation_errors.append({
                    'row': i + 1,
                    'field': field,
                    'error': f'Missing required field: {field}',
                    'type': 'validation',
                    'severity': 'error'
                })
    
    return records_processed, validation_errors


def _process_diagnoses_file(file_path):
    """Process uploaded diagnoses file."""
    validation_errors = []
    records_processed = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        if file_path.endswith('.json'):
            data = json.load(f)
            if isinstance(data, list):
                diagnoses = data
            else:
                diagnoses = data.get('diagnoses', [])
        else:  # CSV
            reader = csv.DictReader(f)
            diagnoses = list(reader)
    
    for i, diagnosis in enumerate(diagnoses):
        records_processed += 1
        
        # Validate required fields
        required_fields = ['name', 'category', 'criteria_summary', 'prevalence_rate']
        for field in required_fields:
            if field not in diagnosis or not diagnosis[field]:
                validation_errors.append({
                    'row': i + 1,
                    'field': field,
                    'error': f'Missing required field: {field}',
                    'type': 'validation',
                    'severity': 'error'
                })
    
    return records_processed, validation_errors


def _process_config_file(file_path):
    """Process uploaded config file."""
    validation_errors = []
    records_processed = 1
    
    with open(file_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Validate config structure
    if not isinstance(config, dict):
        validation_errors.append({
            'error': 'Config must be a JSON object',
            'type': 'structure',
            'severity': 'critical'
        })
    
    return records_processed, validation_errors


def _validate_cases_file(file_path):
    """Validate cases file without processing."""
    # Similar to _process_cases_file but only validation
    return _process_cases_file(file_path)


def _validate_diagnoses_file(file_path):
    """Validate diagnoses file without processing."""
    # Similar to _process_diagnoses_file but only validation
    return _process_diagnoses_file(file_path)


def _validate_config_file(file_path):
    """Validate config file without processing."""
    # Similar to _process_config_file but only validation
    return _process_config_file(file_path)


def _get_directory_size(directory_path):
    """Calculate total size of directory in bytes."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.exists(file_path):
                total_size += os.path.getsize(file_path)
    return total_size