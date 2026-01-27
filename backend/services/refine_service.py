"""
Refinement service handles the core data quality pipeline.
Implements deduplication, quality scoring, classification, and filtering.
"""
import os
import json
from typing import Dict, List, Tuple, Optional
from models import db, Dataset, RefinementRecord, PipelineStage
from pipeline.quality_scorer import QualityScorer
from pipeline.deduplicator import Deduplicator
from pipeline.classifier import Classifier


class RefinementService:
    """
    Manages the data refinement pipeline - the core product.
    
    Responsibilities:
    - Execute quality scoring on data
    - Detect and remove duplicates
    - Classify data properties (language, modality, domain, etc.)
    - Filter out low-quality or unusable content
    - Segment and structure data for training use
    - Track all refinement metrics
    """
    
    def __init__(self):
        """Initialize refinement service with pipeline components."""
        self.quality_scorer = QualityScorer()
        self.deduplicator = Deduplicator()
        self.classifier = Classifier()
    
    def refine_dataset(self, dataset_id: str, quality_threshold: float = 0.5) -> RefinementRecord:
        """
        Execute the full refinement pipeline on a dataset.
        
        Pipeline stages:
        1. Quality scoring - evaluate each item's quality
        2. Deduplication - identify and mark duplicates
        3. Classification - detect properties (language, type, domain)
        4. Filtering - reject low-quality items
        5. Segmentation - structure into training units
        
        Args:
            dataset_id: ID of dataset to refine
            quality_threshold: Minimum quality score (0-1) to keep items
            
        Returns:
            RefinementRecord with detailed processing metrics
        """
        dataset = Dataset.query.get(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")
        
        record = RefinementRecord(
            dataset_id=dataset_id,
            pipeline_stage='full_refinement'
        )
        
        # Stage 1: Quality Scoring
        quality_results = self._score_quality(dataset)
        record.quality_scores = quality_results['scores']
        record.overall_quality = quality_results['overall_score']
        
        # Stage 2: Deduplication
        dedup_results = self._deduplicate(dataset, quality_results)
        record.duplicates_found = dedup_results['duplicates_found']
        record.duplicate_removal_method = dedup_results['method']
        
        # Stage 3: Classification
        classification_results = self._classify_data(dataset)
        record.classifications = classification_results
        
        # Stage 4: Filtering and statistics
        passed_count = self._count_passing_items(
            dataset,
            quality_threshold,
            dedup_results['rejected_items']
        )
        record.items_processed = dataset.file_count
        record.items_passed = passed_count
        record.items_rejected = dataset.file_count - passed_count
        
        # Update dataset
        dataset.stage = PipelineStage.REFINED.value
        dataset.quality_score = record.overall_quality
        
        db.session.add(record)
        db.session.commit()
        
        return record
    
    def _score_quality(self, dataset: Dataset) -> Dict:
        """
        Score quality of all items in dataset.
        
        Returns:
            Dict with individual scores and overall quality metric
        """
        # Placeholder: In production, would analyze actual files
        scores = {
            'completeness': 0.85,
            'clarity': 0.90,
            'relevance': 0.75,
            'format_validity': 0.95,
            'metadata_quality': 0.65,
        }
        
        overall = sum(scores.values()) / len(scores)
        
        return {
            'scores': scores,
            'overall_score': overall
        }
    
    def _deduplicate(self, dataset: Dataset, quality_results: Dict) -> Dict:
        """
        Detect and mark duplicate items.
        
        Uses combination of hash-based and semantic deduplication.
        """
        # Placeholder: In production, would compare files
        return {
            'duplicates_found': 0,
            'method': 'hash_and_semantic',
            'rejected_items': [],
            'similarity_threshold': 0.95
        }
    
    def _classify_data(self, dataset: Dataset) -> Dict:
        """
        Classify data properties.
        
        Detects: language, modality, domain, content type, etc.
        """
        # Placeholder: In production, would use ML models
        classifications = {
            'languages': {
                'en': 0.92,
                'es': 0.08,
            },
            'modalities': {
                'text': 1.0,
            },
            'domains': {
                'general': 0.7,
                'technical': 0.3,
            },
            'content_types': {
                'conversation': 0.5,
                'instructions': 0.3,
                'creative': 0.2,
            }
        }
        
        return classifications
    
    def _count_passing_items(self, 
                            dataset: Dataset,
                            quality_threshold: float,
                            rejected_items: List) -> int:
        """
        Count items that pass quality threshold and deduplication.
        """
        # Placeholder calculation
        passed = int(dataset.file_count * 0.95)  # Assume 95% pass in prototype
        return passed
    
    def get_refinement_status(self, dataset_id: str) -> Dict:
        """Get current refinement status of a dataset."""
        records = RefinementRecord.query.filter_by(dataset_id=dataset_id).all()
        
        if not records:
            return {'status': 'not_refined', 'records': []}
        
        latest = records[-1]
        return {
            'status': 'refined',
            'overall_quality': latest.overall_quality,
            'items_processed': latest.items_processed,
            'items_passed': latest.items_passed,
            'items_rejected': latest.items_rejected,
            'duplicates_found': latest.duplicates_found,
            'classifications': latest.classifications,
            'last_refined_at': latest.created_at
        }
    
    def export_refinement_metrics(self, dataset_id: str) -> Dict:
        """Export detailed refinement metrics for a dataset."""
        record = RefinementRecord.query.filter_by(dataset_id=dataset_id).order_by(
            RefinementRecord.created_at.desc()
        ).first()
        
        if not record:
            return None
        
        return {
            'quality_scores': record.quality_scores,
            'classifications': record.classifications,
            'deduplication': {
                'duplicates_found': record.duplicates_found,
                'method': record.duplicate_removal_method,
            },
            'processing_summary': {
                'items_processed': record.items_processed,
                'items_passed': record.items_passed,
                'items_rejected': record.items_rejected,
                'pass_rate': (record.items_passed / record.items_processed * 100) 
                            if record.items_processed > 0 else 0,
            },
            'duration_seconds': record.processing_duration_seconds,
            'timestamp': record.created_at
        }
