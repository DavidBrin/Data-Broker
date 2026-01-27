"""
Marketplace service handles data package sales and distribution.
Manages listings, pricing, purchases, and access control.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import uuid
from models import db, DataPackage, MarketplaceListing, Sale, Review, User, ListingStatus


class MarketplaceService:
    """
    Manages the data marketplace.
    
    Responsibilities:
    - Create and manage marketplace listings
    - Handle purchase transactions
    - Generate access tokens for downloads
    - Track ratings and reviews
    - Monitor sales and marketplace metrics
    - Support bulk purchases and licensing
    """
    
    def create_listing(self,
                      package_id: str,
                      title: str,
                      description: str,
                      price_usd: float,
                      category: str,
                      tags: List[str] = None,
                      is_featured: bool = False) -> MarketplaceListing:
        """
        Create a marketplace listing for a data package.
        
        Args:
            package_id: ID of data package to list
            title: Listing title
            description: Detailed description
            price_usd: Price in USD
            category: Category (text, audio, video, images)
            tags: List of searchable tags
            is_featured: Whether to feature on homepage
            
        Returns:
            Created MarketplaceListing
        """
        package = DataPackage.query.get(package_id)
        if not package:
            raise ValueError(f"Package {package_id} not found")
        
        listing = MarketplaceListing(
            package_id=package_id,
            title=title,
            description=description,
            price_usd=price_usd,
            category=category,
            tags=tags or [],
            status=ListingStatus.DRAFT.value,
            is_featured=is_featured,
        )
        
        db.session.add(listing)
        db.session.commit()
        
        return listing
    
    def publish_listing(self, listing_id: str) -> MarketplaceListing:
        """
        Publish a listing to the marketplace.
        
        Makes data package visible and purchasable.
        """
        listing = MarketplaceListing.query.get(listing_id)
        if not listing:
            raise ValueError(f"Listing {listing_id} not found")
        
        listing.status = ListingStatus.PUBLISHED.value
        listing.published_at = datetime.utcnow()
        
        db.session.commit()
        return listing
    
    def search_marketplace(self,
                         query: str = '',
                         category: str = None,
                         min_price: float = None,
                         max_price: float = None,
                         min_rating: float = None,
                         sort_by: str = 'relevance',
                         limit: int = 20) -> List[Dict]:
        """
        Search marketplace listings.
        
        Args:
            query: Search query
            category: Filter by category
            min_price: Minimum price filter
            max_price: Maximum price filter
            min_rating: Minimum average rating
            sort_by: Sort order (relevance, price, rating, recent)
            limit: Max results to return
            
        Returns:
            List of matching listing dicts
        """
        listing_query = MarketplaceListing.query.filter_by(
            status=ListingStatus.PUBLISHED.value
        )
        
        if category:
            listing_query = listing_query.filter_by(category=category)
        
        if min_price is not None:
            listing_query = listing_query.filter(MarketplaceListing.price_usd >= min_price)
        
        if max_price is not None:
            listing_query = listing_query.filter(MarketplaceListing.price_usd <= max_price)
        
        if min_rating is not None:
            listing_query = listing_query.filter(MarketplaceListing.average_rating >= min_rating)
        
        # TODO: Add full-text search for query field
        # For now, simple title/description search
        if query:
            listing_query = listing_query.filter(
                (MarketplaceListing.title.contains(query)) |
                (MarketplaceListing.description.contains(query))
            )
        
        # Sort
        if sort_by == 'price':
            listing_query = listing_query.order_by(MarketplaceListing.price_usd)
        elif sort_by == 'rating':
            listing_query = listing_query.order_by(MarketplaceListing.average_rating.desc())
        elif sort_by == 'recent':
            listing_query = listing_query.order_by(MarketplaceListing.published_at.desc())
        else:  # relevance
            pass  # Default order
        
        listings = listing_query.limit(limit).all()
        
        return [self._listing_to_dict(listing) for listing in listings]
    
    def purchase_package(self,
                        listing_id: str,
                        buyer_id: str,
                        quantity: int = 1) -> Sale:
        """
        Process purchase of a data package.
        
        Args:
            listing_id: ID of marketplace listing
            buyer_id: ID of purchasing user
            quantity: Number of copies (for bulk purchases)
            
        Returns:
            Created Sale record
        """
        listing = MarketplaceListing.query.get(listing_id)
        if not listing:
            raise ValueError(f"Listing {listing_id} not found")
        
        package = listing.package
        
        # Calculate price
        price = listing.price_usd * quantity
        
        # Apply bulk discount if applicable
        if (listing.bulk_discount_threshold and 
            quantity >= listing.bulk_discount_threshold and
            listing.bulk_discount_percentage > 0):
            discount = price * (listing.bulk_discount_percentage / 100)
            price -= discount
        
        # Create access token for download
        access_token = str(uuid.uuid4())
        
        # Create sale record
        sale = Sale(
            package_id=package.id,
            listing_id=listing_id,
            buyer_user_id=buyer_id,
            amount_usd=price,
            quantity=quantity,
            access_token=access_token,
            license_expires_at=datetime.utcnow() + timedelta(days=365),  # 1 year license
        )
        
        # Update listing stats
        listing.copies_sold += quantity
        listing.download_count += quantity  # Initial download count
        
        # Check if sold out
        if listing.copies_available > 0 and listing.copies_sold >= listing.copies_available:
            listing.status = ListingStatus.SOLD_OUT.value
        
        db.session.add(sale)
        db.session.commit()
        
        return sale
    
    def get_purchase_details(self, sale_id: str) -> Optional[Dict]:
        """Get details of a purchase for the buyer."""
        sale = Sale.query.get(sale_id)
        if not sale:
            return None
        
        return {
            'sale_id': sale.id,
            'package_name': sale.package.name,
            'amount_paid': sale.amount_usd,
            'purchase_date': sale.created_at.isoformat(),
            'access_token': sale.access_token,
            'downloads_remaining': (
                sale.max_downloads - sale.downloads_used 
                if sale.max_downloads > 0 else 'unlimited'
            ),
            'license_expires': sale.license_expires_at.isoformat() if sale.license_expires_at else None,
        }
    
    def add_review(self,
                   listing_id: str,
                   reviewer_id: str,
                   rating: int,
                   comment: str = '',
                   verified_purchase: bool = False) -> Review:
        """
        Add a review to a marketplace listing.
        
        Args:
            listing_id: ID of listing
            reviewer_id: ID of reviewer
            rating: Star rating (1-5)
            comment: Review comment
            verified_purchase: Whether review is from verified purchase
            
        Returns:
            Created Review
        """
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")
        
        review = Review(
            listing_id=listing_id,
            reviewer_id=reviewer_id,
            rating=rating,
            comment=comment,
            verified_purchase=verified_purchase,
        )
        
        db.session.add(review)
        
        # Update listing average rating
        listing = MarketplaceListing.query.get(listing_id)
        all_reviews = Review.query.filter_by(listing_id=listing_id).all()
        avg_rating = sum(r.rating for r in all_reviews) / len(all_reviews)
        listing.average_rating = avg_rating
        listing.review_count = len(all_reviews)
        
        db.session.commit()
        return review
    
    def get_marketplace_stats(self) -> Dict:
        """Get overall marketplace statistics."""
        total_listings = MarketplaceListing.query.count()
        published_listings = MarketplaceListing.query.filter_by(
            status=ListingStatus.PUBLISHED.value
        ).count()
        total_sales = Sale.query.count()
        total_revenue = db.session.query(db.func.sum(Sale.amount_usd)).scalar() or 0
        
        return {
            'total_listings': total_listings,
            'published_listings': published_listings,
            'total_sales': total_sales,
            'total_revenue_usd': float(total_revenue),
            'average_listing_price': (
                db.session.query(db.func.avg(MarketplaceListing.price_usd)).scalar() or 0
            ),
            'average_rating': (
                db.session.query(db.func.avg(MarketplaceListing.average_rating)).scalar() or 0
            ),
        }
    
    @staticmethod
    def _listing_to_dict(listing: MarketplaceListing) -> Dict:
        """Convert listing object to dictionary."""
        return {
            'id': listing.id,
            'title': listing.title,
            'description': listing.description,
            'category': listing.category,
            'price_usd': listing.price_usd,
            'average_rating': listing.average_rating,
            'review_count': listing.review_count,
            'view_count': listing.view_count,
            'download_count': listing.download_count,
            'is_featured': listing.is_featured,
            'package_name': listing.package.name,
            'quality_score': listing.package.quality_score,
        }
