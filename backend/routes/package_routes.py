"""
Package routes for creating and managing curated data packages.
Handles packaging refined data with manifests and metadata.
"""
from flask import Blueprint, request, jsonify
from models import db, DataPackage
from services import PackageService

bp = Blueprint('packages', __name__, url_prefix='/api/packages')
package_service = PackageService()


@bp.route('/', methods=['POST'])
def create_package():
    """
    Create a data package from a refined dataset.
    
    Request body:
    {
        "dataset_id": "string",
        "name": "string",
        "description": "string",
        "version": "string" (optional),
        "license_type": "string" (optional)
    }
    
    Returns:
        Created DataPackage object
    """
    data = request.get_json()
    
    required = ['dataset_id', 'name', 'description']
    if not all(field in data for field in required):
        return {'error': f'Missing required fields: {", ".join(required)}'}, 400
    
    try:
        package = package_service.create_package(
            dataset_id=data['dataset_id'],
            name=data['name'],
            description=data['description'],
            version=data.get('version', '1.0'),
            license_type=data.get('license_type', 'proprietary')
        )
        
        return {
            'id': package.id,
            'name': package.name,
            'version': package.version,
            'quality_score': package.quality_score,
            'items_count': package.items_count,
            'is_available': package.is_available,
            'created_at': package.created_at.isoformat(),
        }, 201
    except ValueError as e:
        return {'error': str(e)}, 400
    except Exception as e:
        return {'error': str(e)}, 500


@bp.route('/<package_id>', methods=['GET'])
def get_package(package_id: str):
    """Get detailed package information."""
    package_details = package_service.get_package_details(package_id)
    
    if not package_details:
        return {'error': 'Package not found'}, 404
    
    return package_details, 200


@bp.route('/dataset/<dataset_id>', methods=['GET'])
def list_dataset_packages(dataset_id: str):
    """List all packages created from a dataset."""
    packages = package_service.list_packages_by_dataset(dataset_id)
    
    return {
        'dataset_id': dataset_id,
        'packages': packages
    }, 200


@bp.route('/<package_id>/manifest', methods=['GET'])
def get_manifest(package_id: str):
    """Get package manifest (file listing and metadata)."""
    package = DataPackage.query.get(package_id)
    
    if not package:
        return {'error': 'Package not found'}, 404
    
    return {
        'package_id': package_id,
        'manifest': package.manifest,
        'quality_metrics': package.quality_metrics,
    }, 200


@bp.route('/<package_id>/provenance', methods=['GET'])
def get_provenance(package_id: str):
    """Get provenance chain showing all processing steps."""
    package = DataPackage.query.get(package_id)
    
    if not package:
        return {'error': 'Package not found'}, 404
    
    return {
        'package_id': package_id,
        'name': package.name,
        'provenance_log': package.provenance_log,
    }, 200


@bp.route('/<package_id>/export-json', methods=['GET'])
def export_package_json(package_id: str):
    """Export package metadata as JSON."""
    try:
        json_str = package_service.export_package_as_json(package_id)
        return {
            'package_id': package_id,
            'metadata': json.loads(json_str),
        }, 200
    except ValueError as e:
        return {'error': str(e)}, 404
    except Exception as e:
        return {'error': str(e)}, 500


@bp.route('/<package_id>/sell', methods=['PUT'])
def update_for_sale(package_id: str):
    """
    Prepare package for marketplace sale.
    
    Request body:
    {
        "price_usd": float,
        "is_for_sale": boolean (optional, default true)
    }
    """
    data = request.get_json()
    
    if 'price_usd' not in data:
        return {'error': 'Missing required field: price_usd'}, 400
    
    try:
        package = package_service.update_package_for_sale(
            package_id=package_id,
            price_usd=data['price_usd'],
            is_for_sale=data.get('is_for_sale', True)
        )
        
        return {
            'message': 'Package updated for sale',
            'package': {
                'id': package.id,
                'name': package.name,
                'price_usd': package.price_usd,
                'is_for_sale': package.is_for_sale,
            }
        }, 200
    except ValueError as e:
        return {'error': str(e)}, 404
    except Exception as e:
        return {'error': str(e)}, 500


import json
