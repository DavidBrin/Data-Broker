"""
Package service handles creation and management of curated data packages.
Prepares refined data for sale or return to supplier.
"""
import json
from datetime import datetime
from typing import Dict, List, Optional
from models import db, Dataset, DataPackage, RefinementRecord, PipelineStage


class PackageService:
    """
    Manages data package creation and curation.
    
    Responsibilities:
    - Create data packages from refined datasets
    - Generate manifests and documentation
    - Calculate and attach quality metrics
    - Track provenance and processing history
    - Manage licensing and legal terms
    - Prepare for marketplace or return to supplier
    """
    
    def create_package(self,
                      dataset_id: str,
                      name: str,
                      description: str,
                      version: str = "1.0",
                      license_type: str = "proprietary") -> DataPackage:
        """
        Create a data package from a refined dataset.
        
        Args:
            dataset_id: ID of the refined dataset
            name: Package name
            description: Package description
            version: Package version
            license_type: License type (e.g., CC-BY, proprietary)
            
        Returns:
            Created DataPackage object
        """
        dataset = Dataset.query.get(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")
        
        if dataset.stage != PipelineStage.REFINED.value:
            raise ValueError(f"Dataset must be refined before packaging. Current stage: {dataset.stage}")
        
        # Get refinement metrics for quality info
        latest_refinement = RefinementRecord.query.filter_by(
            dataset_id=dataset_id
        ).order_by(RefinementRecord.created_at.desc()).first()
        
        # Create manifest
        manifest = self._generate_manifest(dataset)
        
        # Create quality metrics
        quality_metrics = {
            'overall_score': latest_refinement.overall_quality if latest_refinement else dataset.quality_score,
            'items_included': latest_refinement.items_passed if latest_refinement else dataset.file_count,
            'quality_breakdown': latest_refinement.quality_scores if latest_refinement else {},
        }
        
        # Create provenance log
        provenance = self._generate_provenance_log(dataset)
        
        package = DataPackage(
            source_dataset_id=dataset_id,
            name=name,
            description=description,
            version=version,
            items_count=latest_refinement.items_passed if latest_refinement else dataset.file_count,
            package_size_bytes=dataset.total_size_bytes,
            quality_score=latest_refinement.overall_quality if latest_refinement else dataset.quality_score,
            quality_metrics=quality_metrics,
            manifest=manifest,
            license_type=license_type,
            provenance_log=provenance,
            metadata={
                'source_type': dataset.source_type,
                'classifications': latest_refinement.classifications if latest_refinement else {},
            }
        )
        
        db.session.add(package)
        db.session.commit()
        
        # Update dataset stage
        dataset.stage = PipelineStage.PACKAGED.value
        db.session.commit()
        
        return package
    
    def _generate_manifest(self, dataset: Dataset) -> Dict:
        """
        Generate a detailed manifest of package contents.
        
        Includes file listing, formats, sizes, checksums.
        """
        # Placeholder: In production, would walk the file system
        manifest = {
            'total_files': dataset.file_count,
            'total_size_bytes': dataset.total_size_bytes,
            'format_breakdown': {
                'text': int(dataset.file_count * 0.5),
                'images': int(dataset.file_count * 0.3),
                'other': int(dataset.file_count * 0.2),
            },
            'files': [
                {
                    'filename': f'file_{i}.dat',
                    'size_bytes': dataset.total_size_bytes // max(1, dataset.file_count),
                    'format': 'binary',
                    'checksum': f'sha256_{i}' * 8,
                }
                for i in range(min(5, dataset.file_count))  # Show first 5 as sample
            ]
        }
        return manifest
    
    def _generate_provenance_log(self, dataset: Dataset) -> List[Dict]:
        """
        Generate provenance chain showing all processing steps.
        
        Tracks dataset from source through refinement pipeline.
        """
        provenance = [
            {
                'timestamp': dataset.created_at.isoformat(),
                'stage': 'ingestion',
                'description': f'Data ingested from {dataset.source_type}',
                'files_count': dataset.file_count,
            }
        ]
        
        # Add refinement steps
        refinement_records = RefinementRecord.query.filter_by(
            dataset_id=dataset.id
        ).order_by(RefinementRecord.created_at).all()
        
        for record in refinement_records:
            provenance.append({
                'timestamp': record.created_at.isoformat(),
                'stage': 'refinement',
                'pipeline_stage': record.pipeline_stage,
                'items_passed': record.items_passed,
                'items_rejected': record.items_rejected,
            })
        
        provenance.append({
            'timestamp': datetime.utcnow().isoformat(),
            'stage': 'packaging',
            'description': 'Data packaged for delivery',
        })
        
        return provenance
    
    def get_package_details(self, package_id: str) -> Optional[Dict]:
        """Get detailed information about a data package."""
        package = DataPackage.query.get(package_id)
        if not package:
            return None
        
        return {
            'id': package.id,
            'name': package.name,
            'description': package.description,
            'version': package.version,
            'quality_score': package.quality_score,
            'items_count': package.items_count,
            'size_bytes': package.package_size_bytes,
            'manifest': package.manifest,
            'quality_metrics': package.quality_metrics,
            'provenance': package.provenance_log,
            'license_type': package.license_type,
            'is_available': package.is_available,
            'created_at': package.created_at.isoformat(),
        }
    
    def list_packages_by_dataset(self, dataset_id: str) -> List[Dict]:
        """Get all packages created from a dataset."""
        packages = DataPackage.query.filter_by(source_dataset_id=dataset_id).all()
        return [self.get_package_details(p.id) for p in packages]
    
    def update_package_for_sale(self,
                               package_id: str,
                               price_usd: float,
                               is_for_sale: bool = True) -> DataPackage:
        """
        Update package as available for marketplace sale.
        
        Args:
            package_id: Package ID
            price_usd: Price in USD
            is_for_sale: Whether to list for sale
            
        Returns:
            Updated DataPackage
        """
        package = DataPackage.query.get(package_id)
        if not package:
            raise ValueError(f"Package {package_id} not found")
        
        package.is_for_sale = is_for_sale
        package.price_usd = price_usd
        
        if is_for_sale:
            # Get the dataset to update stage
            dataset = package.source_dataset
            dataset.stage = PipelineStage.LISTED.value
        
        db.session.commit()
        return package
    
    def export_package_as_json(self, package_id: str) -> str:
        """Export package metadata as JSON for external use."""
        package = self.get_package_details(package_id)
        if not package:
            raise ValueError(f"Package {package_id} not found")
        
        return json.dumps(package, indent=2, default=str)
