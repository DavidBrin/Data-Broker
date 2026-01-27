"""
Marketplace models for data package listings and transactions.
"""
from .database import db, BaseModel
from enum import Enum


class ListingStatus(str, Enum):
    """Status of a marketplace listing."""
    DRAFT = "draft"
    PUBLISHED = "published"
    DELISTED = "delisted"
    SOLD_OUT = "sold_out"


class MarketplaceListing(BaseModel):
    """
    Marketplace listing for data packages available for purchase.
    """
    __tablename__ = 'marketplace_listings'
    
    package_id = db.Column(db.String(36), db.ForeignKey('data_packages.id'), nullable=False)
    
    # Listing details
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))  # e.g., "text", "audio", "video", "images"
    subcategory = db.Column(db.String(100))  # e.g., "conversation", "language-specific", etc.
    
    # Tags and searchability
    tags = db.Column(db.JSON, default=list)  # ["audio", "english", "high-quality"]
    keywords = db.Column(db.JSON, default=list)  # For search indexing
    
    # Availability
    status = db.Column(db.String(50), default=ListingStatus.DRAFT.value)
    copies_available = db.Column(db.Integer, default=-1)  # -1 for unlimited
    copies_sold = db.Column(db.Integer, default=0)
    
    # Pricing and commercials
    price_usd = db.Column(db.Float, nullable=False)
    discount_percentage = db.Column(db.Float, default=0.0)  # 0-100
    bulk_discount_threshold = db.Column(db.Integer)  # Min quantity for discount
    bulk_discount_percentage = db.Column(db.Float, default=0.0)
    
    # Discovery and ratings
    view_count = db.Column(db.Integer, default=0)
    download_count = db.Column(db.Integer, default=0)
    average_rating = db.Column(db.Float, default=0.0)  # 0-5 stars
    review_count = db.Column(db.Integer, default=0)
    
    # Publishing
    is_featured = db.Column(db.Boolean, default=False)
    published_at = db.Column(db.DateTime)
    
    package = db.relationship('DataPackage')


class Sale(BaseModel):
    """
    Record of a sale transaction for audit and reporting.
    """
    __tablename__ = 'sales'
    
    package_id = db.Column(db.String(36), db.ForeignKey('data_packages.id'), nullable=False)
    listing_id = db.Column(db.String(36), db.ForeignKey('marketplace_listings.id'))
    buyer_user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # Transaction details
    amount_usd = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=1)  # For bulk purchases
    
    # Fulfillment
    download_link = db.Column(db.String(512))
    access_token = db.Column(db.String(255), unique=True)
    downloads_used = db.Column(db.Integer, default=0)
    max_downloads = db.Column(db.Integer, default=-1)  # -1 for unlimited
    
    # License terms
    license_expires_at = db.Column(db.DateTime)
    can_redistribute = db.Column(db.Boolean, default=False)
    
    # Status
    is_refunded = db.Column(db.Boolean, default=False)
    refund_reason = db.Column(db.Text)
    
    package = db.relationship('DataPackage')
    listing = db.relationship('MarketplaceListing')
    buyer = db.relationship('User')


class Review(BaseModel):
    """
    Customer review and rating for marketplace listings.
    """
    __tablename__ = 'reviews'
    
    listing_id = db.Column(db.String(36), db.ForeignKey('marketplace_listings.id'), nullable=False)
    reviewer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Rating and feedback
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    title = db.Column(db.String(255))
    comment = db.Column(db.Text)
    
    # Metadata
    verified_purchase = db.Column(db.Boolean, default=False)
    helpful_count = db.Column(db.Integer, default=0)
    
    listing = db.relationship('MarketplaceListing', backref='reviews')
    reviewer = db.relationship('User', backref='reviews')
