"""
User and account models for authentication and user management.
"""
from .database import db, BaseModel
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum


class UserRole(str, Enum):
    """User roles in the platform."""
    SUPPLIER = "supplier"  # Data suppliers (crowd, universities, enterprises)
    BUYER = "buyer"  # Data buyers (AI labs, companies)
    ADMIN = "admin"  # Platform administrators
    MODERATOR = "moderator"  # Content moderators


class User(BaseModel):
    """
    User account model for authentication and profile management.
    """
    __tablename__ = 'users'
    
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile information
    full_name = db.Column(db.String(120))
    organization = db.Column(db.String(255))  # University, company, etc.
    profile_description = db.Column(db.Text)
    
    # Role and permissions
    role = db.Column(db.String(50), default=UserRole.SUPPLIER.value)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Supplier-specific fields
    is_supplier = db.Column(db.Boolean, default=False)
    supplier_tier = db.Column(db.String(50))  # "basic", "professional", "enterprise"
    
    # Buyer-specific fields
    is_buyer = db.Column(db.Boolean, default=False)
    buyer_tier = db.Column(db.String(50))  # "basic", "professional", "enterprise"
    
    # Contact and location
    contact_email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    country = db.Column(db.String(100))
    
    # Account settings
    preferences = db.Column(db.JSON, default=dict)  # User preferences
    
    # Relationships
    purchases = db.relationship('Purchase', backref='buyer')
    
    def set_password(self, password):
        """Hash and store password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Return dictionary representation (excluding password hash)."""
        data = super().to_dict()
        data.pop('password_hash', None)
        return data


class Purchase(BaseModel):
    """
    Purchase transaction tracking for data package sales.
    """
    __tablename__ = 'purchases'
    
    buyer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    package_id = db.Column(db.String(36), db.ForeignKey('data_packages.id'), nullable=False)
    
    # Transaction details
    amount_paid = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default="USD")
    payment_method = db.Column(db.String(50))  # "credit_card", "wire_transfer", "etc"
    
    # Download/access info
    access_token = db.Column(db.String(255), unique=True)  # Token for access
    download_count = db.Column(db.Integer, default=0)
    last_accessed = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)  # License expiration
    
    # Relationships
    package = db.relationship('DataPackage', backref='purchases')
