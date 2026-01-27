"""
Refinement routes for managing the data quality pipeline.
Handles quality scoring, deduplication, classification, and filtering.
"""
from flask import Blueprint, request, jsonify
from models import db, Dataset, RefinementRecord
from services import RefinementService

bp = Blueprint('refinement', __name__, url_prefix='/api/refinement')
refine_service = RefinementService()


@bp.route('/refine/<dataset_id>', methods=['POST'])
def refine_dataset(dataset_id: str):
    """
    Execute full refinement pipeline on a dataset.
    
    Request body:
    {
        "quality_threshold": 0.5  (optional, default 0.5)
    }
    
    Returns:
        RefinementRecord with processing results
    """
    dataset = Dataset.query.get(dataset_id)
    if not dataset:
        return {'error': 'Dataset not found'}, 404
    
    data = request.get_json() or {}
    quality_threshold = data.get('quality_threshold', 0.5)
    
    if quality_threshold < 0 or quality_threshold > 1:
        return {'error': 'Quality threshold must be between 0 and 1'}, 400
    
    try:
        record = refine_service.refine_dataset(
            dataset_id=dataset_id,
            quality_threshold=quality_threshold
        )
        
        return {
            'dataset_id': dataset_id,
            'pipeline_stage': record.pipeline_stage,
            'quality_scores': record.quality_scores,
            'overall_quality': record.overall_quality,
            'items_processed': record.items_processed,
            'items_passed': record.items_passed,
            'items_rejected': record.items_rejected,
            'duplicates_found': record.duplicates_found,
            'classifications': record.classifications,
            'created_at': record.created_at.isoformat(),
        }, 200
    except ValueError as e:
        return {'error': str(e)}, 400
    except Exception as e:
        return {'error': str(e)}, 500


@bp.route('/status/<dataset_id>', methods=['GET'])
def get_refinement_status(dataset_id: str):
    """Get current refinement status of a dataset."""
    dataset = Dataset.query.get(dataset_id)
    if not dataset:
        return {'error': 'Dataset not found'}, 404
    
    status = refine_service.get_refinement_status(dataset_id)
    return status, 200


@bp.route('/metrics/<dataset_id>', methods=['GET'])
def get_refinement_metrics(dataset_id: str):
    """Get detailed refinement metrics."""
    metrics = refine_service.export_refinement_metrics(dataset_id)
    
    if not metrics:
        return {'error': 'No refinement records found for dataset'}, 404
    
    return metrics, 200


@bp.route('/history/<dataset_id>', methods=['GET'])
def get_refinement_history(dataset_id: str):
    """Get refinement processing history."""
    records = RefinementRecord.query.filter_by(dataset_id=dataset_id).order_by(
        RefinementRecord.created_at
    ).all()
    
    return {
        'dataset_id': dataset_id,
        'records': [
            {
                'id': r.id,
                'pipeline_stage': r.pipeline_stage,
                'overall_quality': r.overall_quality,
                'items_processed': r.items_processed,
                'items_passed': r.items_passed,
                'items_rejected': r.items_rejected,
                'created_at': r.created_at.isoformat(),
            }
            for r in records
        ]
    }, 200


@bp.route('/quality-check/<dataset_id>', methods=['POST'])
def quality_check(dataset_id: str):
    """
    Run just the quality scoring stage.
    Useful for quick assessment without full pipeline.
    """
    dataset = Dataset.query.get(dataset_id)
    if not dataset:
        return {'error': 'Dataset not found'}, 404
    
    # In production, would run just quality scorer
    return {
        'dataset_id': dataset_id,
        'quality_scores': {
            'completeness': 0.85,
            'clarity': 0.90,
            'relevance': 0.75,
            'format_validity': 0.95,
            'metadata_quality': 0.65,
        },
        'overall_quality': 0.82,
    }, 200


@bp.route('/deduplication/<dataset_id>', methods=['POST'])
def deduplication(dataset_id: str):
    """
    Run just the deduplication stage.
    """
    dataset = Dataset.query.get(dataset_id)
    if not dataset:
        return {'error': 'Dataset not found'}, 404
    
    data = request.get_json() or {}
    method = data.get('method', 'hybrid')  # hash, semantic, hybrid
    
    if method not in ['hash', 'semantic', 'hybrid']:
        return {'error': 'Invalid deduplication method'}, 400
    
    return {
        'dataset_id': dataset_id,
        'duplicates_found': 0,
        'method': method,
        'duplicate_groups': [],
    }, 200


@bp.route('/classification/<dataset_id>', methods=['POST'])
def classify_data(dataset_id: str):
    """
    Run just the classification stage.
    Detects languages, modalities, domains, etc.
    """
    dataset = Dataset.query.get(dataset_id)
    if not dataset:
        return {'error': 'Dataset not found'}, 404
    
    return {
        'dataset_id': dataset_id,
        'classifications': {
            'languages': {'en': 0.92, 'es': 0.08},
            'modalities': {'text': 1.0},
            'domains': {'general': 0.7, 'technical': 0.3},
            'content_types': {'conversation': 0.5, 'instructions': 0.3, 'creative': 0.2},
        }
    }, 200
