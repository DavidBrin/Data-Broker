"""
Dataset routes for managing data ingestion and dataset lifecycle.
Handles uploading files, creating datasets, and tracking ingestion status.
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from models import db, Dataset, IngestionRecord
from services import IngestionService
import os

bp = Blueprint('datasets', __name__, url_prefix='/api/datasets')
ingest_service = IngestionService(upload_folder='uploads')


@bp.route('/', methods=['POST'])
def create_dataset():
    """
    Create a new dataset.
    
    Request body:
    {
        "owner_id": "string",
        "name": "string",
        "description": "string",
        "source_type": "crowd" | "university" | "enterprise",
        "metadata": {optional dict}
    }
    
    Returns:
        Created Dataset object
    """
    data = request.get_json()
    
    # Validation
    required = ['owner_id', 'name', 'source_type']
    if not all(field in data for field in required):
        return {'error': f'Missing required fields: {", ".join(required)}'}, 400
    
    try:
        dataset = ingest_service.create_dataset(
            owner_id=data['owner_id'],
            name=data['name'],
            description=data.get('description', ''),
            source_type=data['source_type'],
            metadata=data.get('metadata')
        )
        
        return {
            'id': dataset.id,
            'name': dataset.name,
            'source_type': dataset.source_type,
            'stage': dataset.stage,
            'created_at': dataset.created_at.isoformat(),
        }, 201
    except Exception as e:
        return {'error': str(e)}, 500


@bp.route('/<dataset_id>/ingest', methods=['POST'])
def ingest_files(dataset_id: str):
    """
    Ingest files into a dataset.
    
    Multipart form data:
    - files: Multiple files to upload
    - metadata: Optional JSON metadata
    - legal_rights_confirmed: Boolean (required)
    
    Returns:
        IngestionRecord with validation results
    """
    # Check if dataset exists
    dataset = Dataset.query.get(dataset_id)
    if not dataset:
        return {'error': 'Dataset not found'}, 404
    
    # Get files
    if 'files' not in request.files:
        return {'error': 'No files provided'}, 400
    
    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        return {'error': 'No files selected'}, 400
    
    # Get metadata
    uploader_metadata = {}
    if 'metadata' in request.form:
        try:
            import json
            uploader_metadata = json.loads(request.form['metadata'])
        except:
            pass
    
    legal_confirmed = request.form.get('legal_rights_confirmed', 'false').lower() == 'true'
    
    try:
        record = ingest_service.ingest_files(
            dataset_id=dataset_id,
            files=files,
            uploader_metadata=uploader_metadata,
            legal_rights_confirmed=legal_confirmed
        )
        
        return {
            'dataset_id': dataset_id,
            'files_validated': record.files_validated,
            'files_passed': record.files_passed,
            'files_failed': record.files_failed,
            'validation_errors': record.validation_errors,
            'stored_location': record.stored_location,
            'legal_attestation': record.legal_rights_confirmed,
        }, 200
    except Exception as e:
        return {'error': str(e)}, 500


@bp.route('/<dataset_id>', methods=['GET'])
def get_dataset(dataset_id: str):
    """Get dataset information."""
    dataset = Dataset.query.get(dataset_id)
    
    if not dataset:
        return {'error': 'Dataset not found'}, 404
    
    return {
        'id': dataset.id,
        'name': dataset.name,
        'description': dataset.description,
        'source_type': dataset.source_type,
        'owner_id': dataset.owner_id,
        'file_count': dataset.file_count,
        'total_size_bytes': dataset.total_size_bytes,
        'stage': dataset.stage,
        'quality_score': dataset.quality_score,
        'legal_attestation': dataset.legal_attestation,
        'is_public': dataset.is_public,
        'created_at': dataset.created_at.isoformat(),
        'updated_at': dataset.updated_at.isoformat(),
    }, 200


@bp.route('/user/<user_id>', methods=['GET'])
def list_user_datasets(user_id: str):
    """List all datasets for a user."""
    datasets = Dataset.query.filter_by(owner_id=user_id).all()
    
    return {
        'user_id': user_id,
        'datasets': [
            {
                'id': d.id,
                'name': d.name,
                'source_type': d.source_type,
                'stage': d.stage,
                'quality_score': d.quality_score,
                'file_count': d.file_count,
                'created_at': d.created_at.isoformat(),
            }
            for d in datasets
        ]
    }, 200


@bp.route('/<dataset_id>', methods=['PUT'])
def update_dataset(dataset_id: str):
    """Update dataset information."""
    dataset = Dataset.query.get(dataset_id)
    
    if not dataset:
        return {'error': 'Dataset not found'}, 404
    
    data = request.get_json()
    
    if 'name' in data:
        dataset.name = data['name']
    if 'description' in data:
        dataset.description = data['description']
    if 'is_public' in data:
        dataset.is_public = data['is_public']
    if 'metadata' in data:
        dataset.metadata.update(data['metadata'])
    
    db.session.commit()
    
    return {
        'message': 'Dataset updated successfully',
        'dataset': {
            'id': dataset.id,
            'name': dataset.name,
            'stage': dataset.stage,
        }
    }, 200


@bp.route('/<dataset_id>', methods=['DELETE'])
def delete_dataset(dataset_id: str):
    """Delete a dataset and associated files."""
    dataset = Dataset.query.get(dataset_id)
    
    if not dataset:
        return {'error': 'Dataset not found'}, 404
    
    # In production, would clean up files from storage
    
    db.session.delete(dataset)
    db.session.commit()
    
    return {'message': 'Dataset deleted successfully'}, 200


@bp.route('/<dataset_id>/ingestion-status', methods=['GET'])
def get_ingestion_status(dataset_id: str):
    """Get ingestion status and history."""
    records = IngestionRecord.query.filter_by(dataset_id=dataset_id).all()
    
    return {
        'dataset_id': dataset_id,
        'ingestion_records': [
            {
                'id': r.id,
                'method': r.ingestion_method,
                'files_validated': r.files_validated,
                'files_passed': r.files_passed,
                'files_failed': r.files_failed,
                'legal_confirmed': r.legal_rights_confirmed,
                'created_at': r.created_at.isoformat(),
            }
            for r in records
        ]
    }, 200
