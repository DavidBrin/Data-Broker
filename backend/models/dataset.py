"""
Dataset models representing the data flow through the platform.
Tracks datasets from ingestion through refinement to sale.
"""
from .database import db, BaseModel
from enum import Enum
import json


class DataSourceType(str, Enum):
    """Types of data sources in the platform."""
    CROWD = "crowd"  # Crowd contributors
    UNIVERSITY = "university"  # Universities and research institutions
    ENTERPRISE = "enterprise"  # Enterprise data lakes
    MARKETPLACE = "marketplace"  # Previously sold datasets


class PipelineStage(str, Enum):
    """Stages in the data refinement pipeline."""
    INGESTED = "ingested"
    STORED = "stored"
    REFINING = "refining"
    REFINED = "refined"
    PACKAGED = "packaged"
    LISTED = "listed"
    SOLD = "sold"


class Dataset(BaseModel):
    """
    Core dataset model tracking data through the entire pipeline.
    
    Attributes:
        name: Human-readable dataset name
        description: Detailed description of dataset contents
        source_type: Type of data source (crowd, university, enterprise)
        owner_id: ID of the user who owns/supplied the data
        file_path: Local or cloud storage path to raw files
        file_count: Number of files in the dataset
        total_size_bytes: Total size of all files
        metadata: JSON field for flexible key-value data about dataset
        stage: Current pipeline stage
        quality_score: Overall quality metric (0-1)
        is_public: Whether dataset can be viewed by others in marketplace
    """
    __tablename__ = 'datasets'
    
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    source_type = db.Column(db.String(50), nullable=False)
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Storage information
    file_path = db.Column(db.String(512), nullable=False)
    file_count = db.Column(db.Integer, default=0)
    total_size_bytes = db.Column(db.BigInteger, default=0)
    
    # Flexible metadata storage
    metadata = db.Column(db.JSON, default=dict)
    
    # Pipeline tracking
    stage = db.Column(db.String(50), default=PipelineStage.INGESTED.value)
    quality_score = db.Column(db.Float, default=0.0)  # 0-1 scale
    is_public = db.Column(db.Boolean, default=False)
    
    # Legal and licensing
    legal_attestation = db.Column(db.Boolean, default=False)
    license_type = db.Column(db.String(100))  # e.g., "CC-BY", "proprietary"
    
    # Relationships
    owner = db.relationship('User', backref='datasets')
    ingestion_records = db.relationship('IngestionRecord', backref='dataset', cascade='all, delete-orphan')
    refinement_records = db.relationship('RefinementRecord', backref='dataset', cascade='all, delete-orphan')
    packages = db.relationship('DataPackage', backref='source_dataset', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Return dictionary representation of dataset."""
        base = super().to_dict()
        base['owner_name'] = self.owner.username if self.owner else None
        return base


class IngestionRecord(BaseModel):
    """
    Tracks metadata about data ingestion event.
    Records how data entered the system, what was provided, validation results.
    """
    __tablename__ = 'ingestion_records'
    
    dataset_id = db.Column(db.String(36), db.ForeignKey('datasets.id'), nullable=False)
    
    # Ingestion method
    ingestion_method = db.Column(db.String(50))  # "direct_upload", "cloud_bucket", "api"
    ingestion_source = db.Column(db.String(512))  # Cloud path, S3 bucket, etc.
    
    # Validation results
    files_validated = db.Column(db.Integer, default=0)
    files_passed = db.Column(db.Integer, default=0)
    files_failed = db.Column(db.Integer, default=0)
    validation_errors = db.Column(db.JSON, default=list)  # List of validation error objects
    
    # Metadata provided by uploader
    uploader_metadata = db.Column(db.JSON)  # Free-form metadata from source
    legal_rights_confirmed = db.Column(db.Boolean, default=False)
    
    # Actual storage info
    stored_location = db.Column(db.String(512))  # Where files were stored
    
    dataset = db.relationship('Dataset', backref='ingestion')


class RefinementRecord(BaseModel):
    """
    Tracks the refinement pipeline execution.
    Records quality scoring, deduplication, classification results.
    """
    __tablename__ = 'refinement_records'
    
    dataset_id = db.Column(db.String(36), db.ForeignKey('datasets.id'), nullable=False)
    
    # Pipeline stage
    pipeline_stage = db.Column(db.String(50))  # e.g., "quality_check", "deduplication", "classification"
    
    # Quality metrics
    quality_scores = db.Column(db.JSON)  # Dict of individual quality scores
    overall_quality = db.Column(db.Float, default=0.0)
    
    # Processing results
    items_processed = db.Column(db.Integer, default=0)
    items_passed = db.Column(db.Integer, default=0)
    items_rejected = db.Column(db.Integer, default=0)
    
    # Classification results
    classifications = db.Column(db.JSON)  # Dict of detected properties
    # e.g. {"languages": {"en": 45, "es": 12}, "modalities": {"text": 45, "audio": 0}}
    
    # Deduplication
    duplicates_found = db.Column(db.Integer, default=0)
    duplicate_removal_method = db.Column(db.String(100))  # "hash", "semantic", "hybrid"
    
    # Processing details
    processing_duration_seconds = db.Column(db.Float)
    error_log = db.Column(db.JSON, default=list)
    
    dataset = db.relationship('Dataset', backref='refinement')


class DataPackage(BaseModel):
    """
    Curated data packages ready for sale or return to owner.
    Contains refined datasets with manifests, statistics, and licensing.
    """
    __tablename__ = 'data_packages'
    
    source_dataset_id = db.Column(db.String(36), db.ForeignKey('datasets.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    version = db.Column(db.String(50), default="1.0")
    
    # Content information
    items_count = db.Column(db.Integer, default=0)
    package_size_bytes = db.Column(db.BigInteger, default=0)
    
    # Quality and statistics
    quality_score = db.Column(db.Float, default=0.0)
    quality_metrics = db.Column(db.JSON)  # Detailed quality breakdown
    
    # Manifest and documentation
    manifest = db.Column(db.JSON)  # File listing, format info, etc.
    metadata = db.Column(db.JSON)  # Extended metadata about package contents
    
    # Licensing and provenance
    license_type = db.Column(db.String(100))
    license_url = db.Column(db.String(512))
    provenance_log = db.Column(db.JSON)  # Chain of processing steps
    
    # Availability
    is_available = db.Column(db.Boolean, default=True)
    is_for_sale = db.Column(db.Boolean, default=False)
    
    # Pricing (if for sale)
    price_usd = db.Column(db.Float)
    currency = db.Column(db.String(3), default="USD")
    
    # Relationships
    marketplace_listings = db.relationship('MarketplaceListing', backref='package')
    sales = db.relationship('Sale', backref='package')
    
    def to_dict(self):
        """Return dictionary representation."""
        base = super().to_dict()
        base['source_dataset_name'] = self.source_dataset.name if self.source_dataset else None
        return base
