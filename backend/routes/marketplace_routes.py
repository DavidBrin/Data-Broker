"""
Marketplace routes for listing, searching, and purchasing data packages.
Handles the data brokerage marketplace functionality.
"""
from flask import Blueprint, request, jsonify
from models import db
from services import MarketplaceService

bp = Blueprint('marketplace', __name__, url_prefix='/api/marketplace')
marketplace_service = MarketplaceService()


@bp.route('/listings', methods=['POST'])
def create_listing():
    """
    Create a marketplace listing for a data package.
    
    Request body:
    {
        "package_id": "string",
        "title": "string",
        "description": "string",
        "price_usd": float,
        "category": "string",
        "tags": ["string"],
        "is_featured": boolean (optional)
    }
    
    Returns:
        Created MarketplaceListing object
    """
    data = request.get_json()
    
    required = ['package_id', 'title', 'description', 'price_usd', 'category']
    if not all(field in data for field in required):
        return {'error': f'Missing required fields: {", ".join(required)}'}, 400
    
    try:
        listing = marketplace_service.create_listing(
            package_id=data['package_id'],
            title=data['title'],
            description=data['description'],
            price_usd=data['price_usd'],
            category=data['category'],
            tags=data.get('tags', []),
            is_featured=data.get('is_featured', False)
        )
        
        return {
            'id': listing.id,
            'title': listing.title,
            'status': listing.status,
            'price_usd': listing.price_usd,
            'created_at': listing.created_at.isoformat(),
        }, 201
    except Exception as e:
        return {'error': str(e)}, 500


@bp.route('/listings/<listing_id>/publish', methods=['PUT'])
def publish_listing(listing_id: str):
    """Publish a listing to the marketplace."""
    try:
        listing = marketplace_service.publish_listing(listing_id)
        
        return {
            'message': 'Listing published successfully',
            'listing': {
                'id': listing.id,
                'title': listing.title,
                'status': listing.status,
                'published_at': listing.published_at.isoformat(),
            }
        }, 200
    except ValueError as e:
        return {'error': str(e)}, 404
    except Exception as e:
        return {'error': str(e)}, 500


@bp.route('/search', methods=['GET'])
def search_marketplace():
    """
    Search marketplace listings.
    
    Query parameters:
    - query: Search query string
    - category: Filter by category
    - min_price: Minimum price
    - max_price: Maximum price
    - min_rating: Minimum average rating
    - sort_by: Sort order (relevance, price, rating, recent)
    - limit: Max results (default 20)
    
    Returns:
        List of matching listings
    """
    query = request.args.get('query', '')
    category = request.args.get('category')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    min_rating = request.args.get('min_rating', type=float)
    sort_by = request.args.get('sort_by', 'relevance')
    limit = request.args.get('limit', 20, type=int)
    
    results = marketplace_service.search_marketplace(
        query=query,
        category=category,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        sort_by=sort_by,
        limit=limit
    )
    
    return {
        'query': query,
        'total_results': len(results),
        'results': results
    }, 200


@bp.route('/listings/<listing_id>', methods=['GET'])
def get_listing(listing_id: str):
    """Get detailed listing information."""
    # Placeholder implementation
    return {
        'id': listing_id,
        'title': 'Sample Data Package',
        'description': 'High-quality training data',
        'price_usd': 99.99,
        'average_rating': 4.5,
        'review_count': 12,
    }, 200


@bp.route('/purchase', methods=['POST'])
def purchase_package():
    """
    Purchase a data package from the marketplace.
    
    Request body:
    {
        "listing_id": "string",
        "buyer_id": "string",
        "quantity": int (optional, default 1)
    }
    
    Returns:
        Sale record with download access information
    """
    data = request.get_json()
    
    required = ['listing_id', 'buyer_id']
    if not all(field in data for field in required):
        return {'error': f'Missing required fields: {", ".join(required)}'}, 400
    
    try:
        sale = marketplace_service.purchase_package(
            listing_id=data['listing_id'],
            buyer_id=data['buyer_id'],
            quantity=data.get('quantity', 1)
        )
        
        return {
            'sale_id': sale.id,
            'package_id': sale.package_id,
            'amount_paid': sale.amount_usd,
            'access_token': sale.access_token,
            'license_expires': sale.license_expires_at.isoformat() if sale.license_expires_at else None,
            'created_at': sale.created_at.isoformat(),
        }, 201
    except ValueError as e:
        return {'error': str(e)}, 404
    except Exception as e:
        return {'error': str(e)}, 500


@bp.route('/purchases/<sale_id>', methods=['GET'])
def get_purchase_details(sale_id: str):
    """Get details of a purchase."""
    details = marketplace_service.get_purchase_details(sale_id)
    
    if not details:
        return {'error': 'Purchase not found'}, 404
    
    return details, 200


@bp.route('/listings/<listing_id>/review', methods=['POST'])
def add_review(listing_id: str):
    """
    Add a review/rating to a marketplace listing.
    
    Request body:
    {
        "reviewer_id": "string",
        "rating": int (1-5),
        "comment": "string" (optional),
        "verified_purchase": boolean (optional)
    }
    """
    data = request.get_json()
    
    required = ['reviewer_id', 'rating']
    if not all(field in data for field in required):
        return {'error': f'Missing required fields: {", ".join(required)}'}, 400
    
    try:
        review = marketplace_service.add_review(
            listing_id=listing_id,
            reviewer_id=data['reviewer_id'],
            rating=data['rating'],
            comment=data.get('comment', ''),
            verified_purchase=data.get('verified_purchase', False)
        )
        
        return {
            'id': review.id,
            'rating': review.rating,
            'comment': review.comment,
            'created_at': review.created_at.isoformat(),
        }, 201
    except ValueError as e:
        return {'error': str(e)}, 400
    except Exception as e:
        return {'error': str(e)}, 500


@bp.route('/stats', methods=['GET'])
def get_marketplace_stats():
    """Get marketplace statistics and metrics."""
    stats = marketplace_service.get_marketplace_stats()
    return stats, 200


@bp.route('/featured', methods=['GET'])
def get_featured_listings():
    """Get featured listings for homepage."""
    # Placeholder implementation
    return {
        'featured_listings': [
            {
                'id': '1',
                'title': 'High-Quality English Conversations',
                'price_usd': 199.99,
                'quality_score': 0.95,
                'items_count': 50000,
            },
            {
                'id': '2',
                'title': 'Multilingual Audio Dataset',
                'price_usd': 299.99,
                'quality_score': 0.92,
                'items_count': 100000,
            },
        ]
    }, 200
