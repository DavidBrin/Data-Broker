"""
Ingestion service handles data source ingestion and validation.
Manages the initial data upload, metadata collection, and legal attestations.
"""
import os
from datetime import datetime
from pathlib import Path
import hashlib
import json
from typing import Dict, List, Tuple, Optional
from models import db, Dataset, IngestionRecord, DataSourceType


class IngestionService:
    """
    Manages data ingestion pipeline.
    
    Responsibilities:
    - Handle file uploads from various sources
    - Validate file formats and content
    - Store metadata and legal information
    - Track ingestion process
    - Interface with cloud storage systems
    """
    
    ALLOWED_EXTENSIONS = {
        'txt', 'pdf', 'csv', 'json', 'xml',  # Text
        'mp3', 'wav', 'm4a', 'flac',  # Audio
        'mp4', 'avi', 'mov', 'mkv', 'webm',  # Video
        'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'  # Images
    }
    
    # Maximum file sizes by type (in bytes)
    MAX_FILE_SIZES = {
        'text': 100 * 1024 * 1024,  # 100MB
        'audio': 500 * 1024 * 1024,  # 500MB
        'video': 2 * 1024 * 1024 * 1024,  # 2GB
        'image': 50 * 1024 * 1024,  # 50MB
    }
    
    def __init__(self, upload_folder: str = 'uploads'):
        """Initialize ingestion service with upload folder."""
        self.upload_folder = upload_folder
        os.makedirs(upload_folder, exist_ok=True)
    
    def create_dataset(self, 
                      owner_id: str,
                      name: str,
                      description: str,
                      source_type: str,
                      metadata: Dict = None) -> Dataset:
        """
        Create a new dataset record to track throughout pipeline.
        
        Args:
            owner_id: ID of the user supplying data
            name: Human-readable dataset name
            description: Detailed description
            source_type: Type of source (crowd, university, enterprise)
            metadata: Optional flexible metadata
            
        Returns:
            Created Dataset object
        """
        dataset = Dataset(
            owner_id=owner_id,
            name=name,
            description=description,
            source_type=source_type,
            file_path='',  # Will be set during ingestion
            dataset_metadata=metadata or {},
        )
        db.session.add(dataset)
        db.session.commit()
        return dataset
    
    def validate_file(self, filename: str, file_size: int) -> Tuple[bool, Optional[str]]:
        """
        Validate if a file is acceptable for ingestion.
        
        Args:
            filename: Name of the file to validate
            file_size: Size of file in bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check extension
        if '.' not in filename:
            return False, f"File '{filename}' has no extension"
        
        ext = filename.rsplit('.', 1)[1].lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            return False, f"File type '.{ext}' not allowed"
        
        # Check file size
        file_type = self._get_file_type(ext)
        max_size = self.MAX_FILE_SIZES.get(file_type, 100 * 1024 * 1024)
        if file_size > max_size:
            return False, f"File exceeds maximum size of {max_size / 1024 / 1024}MB"
        
        return True, None
    
    def ingest_files(self,
                    dataset_id: str,
                    files: List,
                    uploader_metadata: Dict = None,
                    legal_rights_confirmed: bool = False) -> IngestionRecord:
        """
        Ingest multiple files for a dataset.
        
        Args:
            dataset_id: ID of the dataset
            files: List of file objects to ingest
            uploader_metadata: Metadata provided by uploader
            legal_rights_confirmed: Whether legal rights were attested
            
        Returns:
            IngestionRecord tracking the process
        """
        dataset = Dataset.query.get(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")
        
        # Create ingestion record
        record = IngestionRecord(
            dataset_id=dataset_id,
            ingestion_method='direct_upload',
            uploader_metadata=uploader_metadata or {},
            legal_rights_confirmed=legal_rights_confirmed,
        )
        
        # Create dataset folder
        dataset_folder = os.path.join(self.upload_folder, dataset_id)
        os.makedirs(dataset_folder, exist_ok=True)
        
        validation_errors = []
        files_stored = 0
        total_size = 0
        
        for file in files:
            if not file or file.filename == '':
                continue
            
            # Validate
            is_valid, error = self.validate_file(file.filename, 0)  # Size check done by Flask
            if not is_valid:
                validation_errors.append({
                    'filename': file.filename,
                    'error': error
                })
                record.files_failed += 1
                continue
            
            # Save file
            try:
                filename = self._sanitize_filename(file.filename)
                filepath = os.path.join(dataset_folder, filename)
                file.save(filepath)
                
                file_size = os.path.getsize(filepath)
                total_size += file_size
                files_stored += 1
                record.files_passed += 1
                
            except Exception as e:
                validation_errors.append({
                    'filename': file.filename,
                    'error': str(e)
                })
                record.files_failed += 1
        
        # Update dataset and ingestion record
        record.files_validated = record.files_passed + record.files_failed
        record.validation_errors = validation_errors
        record.stored_location = dataset_folder
        
        dataset.file_path = dataset_folder
        dataset.file_count = files_stored
        dataset.total_size_bytes = total_size
        dataset.legal_attestation = legal_rights_confirmed
        
        db.session.add(record)
        db.session.commit()
        
        return record
    
    def ingest_from_cloud_bucket(self,
                                dataset_id: str,
                                bucket_path: str,
                                uploader_metadata: Dict = None) -> IngestionRecord:
        """
        Ingest data from cloud storage (S3, GCS, etc).
        
        NOTE: This is a placeholder for cloud integration.
        In production, integrate with AWS S3, Google Cloud Storage, or Azure Blob Storage.
        
        Args:
            dataset_id: ID of the dataset
            bucket_path: Path to cloud bucket (e.g., s3://bucket/path)
            uploader_metadata: Metadata provided by uploader
            
        Returns:
            IngestionRecord tracking the process
        """
        # Placeholder implementation
        # In production, would connect to cloud provider and download files
        record = IngestionRecord(
            dataset_id=dataset_id,
            ingestion_method='cloud_bucket',
            ingestion_source=bucket_path,
            uploader_metadata=uploader_metadata or {},
        )
        
        # TODO: Implement actual cloud integration
        # This would involve:
        # 1. Authenticate with cloud provider
        # 2. List objects in bucket
        # 3. Download and validate files
        # 4. Update metadata
        
        db.session.add(record)
        db.session.commit()
        
        return record
    
    @staticmethod
    def _get_file_type(extension: str) -> str:
        """Determine file type from extension."""
        text_exts = {'txt', 'pdf', 'csv', 'json', 'xml'}
        audio_exts = {'mp3', 'wav', 'm4a', 'flac'}
        video_exts = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
        image_exts = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}
        
        if extension in text_exts:
            return 'text'
        elif extension in audio_exts:
            return 'audio'
        elif extension in video_exts:
            return 'video'
        elif extension in image_exts:
            return 'image'
        else:
            return 'unknown'
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent directory traversal attacks.
        Keeps only alphanumeric, dash, underscore, and extension.
        """
        import re
        # Remove path components
        filename = os.path.basename(filename)
        # Keep only safe characters
        filename = re.sub(r'[^\w\s.-]', '', filename)
        return filename
    
    @staticmethod
    def calculate_file_hash(filepath: str, algorithm: str = 'sha256') -> str:
        """
        Calculate hash of file for deduplication and integrity checking.
        
        Args:
            filepath: Path to file
            algorithm: Hash algorithm (sha256, md5, etc.)
            
        Returns:
            Hex hash string
        """
        hasher = hashlib.new(algorithm)
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
