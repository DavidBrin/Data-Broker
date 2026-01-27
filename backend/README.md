# Data Broker Backend

Flask-based REST API backend for the Data Broker platform - a comprehensive data refinement pipeline for AI training data.

## Overview

The backend implements the complete data refinement pipeline: SOURCE → INGEST → STORE → REFINE → PACKAGE → SELL.

It provides:
- User authentication and account management
- Dataset ingestion and validation
- Quality scoring and refinement pipeline
- Data packaging and marketplace management
- RESTful API for frontend integration

## Architecture

### Directory Structure

```
backend/
├── app.py                 # Flask application factory
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── models/              # Database models
│   ├── database.py      # SQLAlchemy setup
│   ├── user.py          # User and account models
│   ├── dataset.py       # Dataset, ingestion, refinement models
│   ├── marketplace.py   # Marketplace and sales models
│   └── __init__.py
├── routes/              # API route blueprints
│   ├── auth_routes.py
│   ├── dataset_routes.py
│   ├── refinement_routes.py
│   ├── package_routes.py
│   ├── marketplace_routes.py
│   └── __init__.py
├── services/            # Business logic
│   ├── ingest_service.py
│   ├── refine_service.py
│   ├── package_service.py
│   ├── marketplace_service.py
│   └── __init__.py
├── pipeline/            # Data refinement pipeline
│   ├── quality_scorer.py
│   ├── deduplicator.py
│   ├── classifier.py
│   └── __init__.py
└── utils/              # Utility functions
```

### Design Patterns

#### Service Layer

Business logic is separated into service classes:
- `IngestionService`: File upload, validation, storage
- `RefinementService`: Quality scoring, deduplication, classification
- `PackageService`: Package creation, manifest generation
- `MarketplaceService`: Marketplace operations, sales tracking

Each service encapsulates related functionality and is used by route handlers.

#### Database Models

Models use SQLAlchemy ORM with a base model providing:
- UUID primary keys
- Automatic timestamp tracking (created_at, updated_at)
- JSON field support for flexible metadata
- Relationship management

#### API Design

RESTful API endpoints organized by domain:
- `/api/auth/` - Authentication
- `/api/datasets/` - Dataset management
- `/api/refinement/` - Pipeline operations
- `/api/packages/` - Package management
- `/api/marketplace/` - Marketplace operations

### Database Schema

Key tables:
- **users**: User accounts and roles
- **datasets**: Raw datasets tracking
- **ingestion_records**: Ingestion event tracking
- **refinement_records**: Pipeline execution results
- **data_packages**: Curated packages ready for sale/return
- **marketplace_listings**: Marketplace listings
- **sales**: Sales transactions
- **reviews**: Customer reviews

### Data Flow

```
1. INGEST
   - User uploads files
   - IngestionService validates and stores
   - Creates IngestionRecord

2. STORE
   - Files stored in cold storage (local or cloud)
   - Dataset marked as "stored"

3. REFINE
   - RefinementService runs quality pipeline
   - Scores quality, detects duplicates, classifies data
   - Creates RefinementRecord with metrics

4. PACKAGE
   - PackageService creates curated packages
   - Generates manifests and quality metrics
   - Tracks provenance

5. SELL
   - Package listed on marketplace
   - Buyers can search, review, and purchase
   - Sales tracked with access tokens
```

## Getting Started

### Prerequisites

- Python 3.8+
- pip or conda
- PostgreSQL (or SQLite for dev)
- (Optional) AWS S3 credentials for cloud storage

### Installation

```bash
cd backend
pip install -r requirements.txt
```

### Configuration

Create a `.env` file:

```
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///data_broker.db
UPLOAD_FOLDER=uploads
USE_CLOUD_STORAGE=false

# Optional: AWS S3 credentials
# AWS_S3_BUCKET=your-bucket
# AWS_REGION=us-east-1
# AWS_ACCESS_KEY=xxx
# AWS_SECRET_KEY=xxx
```

### Running the Server

```bash
python app.py
```

Server will start at `http://localhost:5000`

API documentation is available at `http://localhost:5000/` (lists all endpoints)

## API Endpoints

### Authentication

```
POST   /api/auth/register           - Create account
POST   /api/auth/login              - Log in
POST   /api/auth/logout             - Log out
GET    /api/auth/profile/<user_id>  - Get profile
PUT    /api/auth/profile/<user_id>  - Update profile
```

### Datasets

```
POST   /api/datasets/               - Create dataset
GET    /api/datasets/<dataset_id>   - Get dataset
GET    /api/datasets/user/<user_id> - List user datasets
PUT    /api/datasets/<dataset_id>   - Update dataset
DELETE /api/datasets/<dataset_id>   - Delete dataset
POST   /api/datasets/<id>/ingest    - Upload files
GET    /api/datasets/<id>/ingestion-status - Get ingestion status
```

### Refinement

```
POST   /api/refinement/refine/<dataset_id>       - Run full pipeline
GET    /api/refinement/status/<dataset_id>       - Get refinement status
GET    /api/refinement/metrics/<dataset_id>      - Get metrics
GET    /api/refinement/history/<dataset_id>      - Get history
POST   /api/refinement/quality-check/<id>        - Run quality scoring
POST   /api/refinement/deduplication/<id>        - Run deduplication
POST   /api/refinement/classification/<id>       - Run classification
```

### Packages

```
POST   /api/packages/                    - Create package
GET    /api/packages/<package_id>        - Get package
GET    /api/packages/dataset/<dataset_id> - List packages for dataset
GET    /api/packages/<id>/manifest       - Get manifest
GET    /api/packages/<id>/provenance     - Get provenance
PUT    /api/packages/<id>/sell           - Prepare for sale
GET    /api/packages/<id>/export-json    - Export as JSON
```

### Marketplace

```
POST   /api/marketplace/listings              - Create listing
PUT    /api/marketplace/listings/<id>/publish - Publish listing
GET    /api/marketplace/search                - Search listings
GET    /api/marketplace/listings/<id>         - Get listing
POST   /api/marketplace/purchase              - Purchase package
GET    /api/marketplace/purchases/<id>        - Get purchase details
POST   /api/marketplace/listings/<id>/review  - Add review
GET    /api/marketplace/stats                 - Get marketplace stats
GET    /api/marketplace/featured              - Get featured listings
```

## Request/Response Examples

### Create Dataset

**Request:**
```bash
curl -X POST http://localhost:5000/api/datasets/ \
  -H "Content-Type: application/json" \
  -d '{
    "owner_id": "user123",
    "name": "English Conversations",
    "description": "High-quality customer service calls",
    "source_type": "enterprise"
  }'
```

**Response:**
```json
{
  "id": "dataset-uuid",
  "name": "English Conversations",
  "source_type": "enterprise",
  "stage": "ingested",
  "created_at": "2024-01-27T12:00:00Z"
}
```

### Upload Files

**Request:**
```bash
curl -X POST http://localhost:5000/api/datasets/dataset-id/ingest \
  -F "files=@file1.mp3" \
  -F "files=@file2.mp3" \
  -F "legal_rights_confirmed=true"
```

**Response:**
```json
{
  "dataset_id": "dataset-id",
  "files_validated": 2,
  "files_passed": 2,
  "files_failed": 0,
  "stored_location": "uploads/dataset-id",
  "legal_attestation": true
}
```

### Run Refinement

**Request:**
```bash
curl -X POST http://localhost:5000/api/refinement/refine/dataset-id \
  -H "Content-Type: application/json" \
  -d '{"quality_threshold": 0.5}'
```

**Response:**
```json
{
  "dataset_id": "dataset-id",
  "overall_quality": 0.82,
  "quality_scores": {
    "completeness": 0.85,
    "clarity": 0.90,
    "relevance": 0.75
  },
  "items_processed": 1000,
  "items_passed": 950,
  "items_rejected": 50,
  "duplicates_found": 5,
  "classifications": {
    "languages": {"en": 0.92, "es": 0.08},
    "modalities": {"audio": 1.0}
  }
}
```

## Pipeline Implementation

### Quality Scoring

Evaluates data quality across dimensions:
- **Completeness**: Portion of expected data present
- **Clarity**: Freedom from noise, corruption, blur
- **Relevance**: Match to target domains
- **Format Validity**: Valid file formats
- **Metadata Quality**: Presence of metadata

Currently returns placeholder scores. To implement:
1. Add file-specific analyzers (ImageQualityAnalyzer, AudioQualityAnalyzer, etc.)
2. Integrate ML models for quality prediction
3. Implement format-specific validation

### Deduplication

Identifies duplicate and near-duplicate items using:
- **Hash-based**: Exact duplicates via SHA256
- **Semantic**: Similarity via embeddings
- **Hybrid**: Combined approach

Currently placeholder. To implement:
1. Add file hashing (compute & compare SHA256)
2. Add embedding generation (using pre-trained models)
3. Add similarity comparison (cosine similarity)

### Classification

Detects data properties:
- **Language**: Language identification (if text/audio)
- **Modality**: Type of content (text, audio, video, image)
- **Domain**: Subject matter (general, technical, medical, legal)
- **Content Type**: Conversation, instruction, creative, etc.

Currently placeholder. To implement:
1. Integrate language detection library (langdetect, textblob)
2. Add modality detection (file type + content analysis)
3. Add domain classification (fine-tuned BERT model)
4. Add content type classification

## Cloud Storage Integration

The system is designed for cloud storage but currently uses local filesystem.

### To Add AWS S3 Support

1. Install boto3:
```bash
pip install boto3
```

2. Update `services/ingest_service.py`:
```python
import boto3

def ingest_from_cloud_bucket(self, dataset_id, bucket_path):
    s3_client = boto3.client('s3')
    # Download from S3
    # Validate files
    # Store locally or re-upload to different bucket
```

3. Add S3 configuration to `config.py`

4. Update routes to accept cloud bucket paths

### Supported Cloud Services

- **AWS S3**: Use boto3
- **Google Cloud Storage**: Use google-cloud-storage
- **Azure Blob Storage**: Use azure-storage-blob

The pattern is:
1. User provides cloud bucket path
2. Service authenticates with cloud provider
3. Download/stream files
4. Process and store

## Database Migrations

For production, use Alembic:

```bash
pip install alembic
alembic init migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Testing

Create test files and run:

```bash
pip install pytest pytest-flask
pytest
```

Example test structure:
```
tests/
├── conftest.py
├── test_auth.py
├── test_datasets.py
├── test_refinement.py
└── test_marketplace.py
```

## Performance Considerations

### Indexing

Add database indexes for frequently queried fields:
```python
class Dataset(BaseModel):
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'), index=True)
    stage = db.Column(db.String(50), index=True)
    created_at = db.Column(db.DateTime, index=True)
```

### Caching

Cache expensive operations:
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/marketplace/stats')
@cache.cached(timeout=3600)
def get_stats():
    ...
```

### Async Tasks

Use Celery for long-running refinement:
```python
from celery import Celery

celery = Celery(app.name)

@celery.task
def refine_dataset_async(dataset_id):
    refine_service.refine_dataset(dataset_id)
```

## Security Considerations

### Production Checklist

- [ ] Change SECRET_KEY
- [ ] Use HTTPS only
- [ ] Enable CORS properly (not `*`)
- [ ] Implement rate limiting
- [ ] Add request validation
- [ ] Sanitize file uploads
- [ ] Hash passwords (done)
- [ ] Use environment variables for secrets
- [ ] Add logging
- [ ] Regular security audits
- [ ] Database backups
- [ ] API key authentication

### File Upload Security

Currently validates:
- File extensions
- File size

To improve:
- Scan files for malware (ClamAV)
- Verify file magic bytes
- Store files outside web root
- Implement access control

## Monitoring & Logging

Add structured logging:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info(f"Dataset {dataset_id} refined successfully")
```

## Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
```

### Using Docker

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]
```

### Environment Setup

- Set `FLASK_ENV=production`
- Use strong `SECRET_KEY`
- Use PostgreSQL (not SQLite)
- Enable SSL/HTTPS
- Set up monitoring and alerts
- Regular backups

## Troubleshooting

### Database Errors

- Check DATABASE_URL is correct
- Ensure database exists and is accessible
- Run `db.create_all()` in Python shell

### File Upload Issues

- Check UPLOAD_FOLDER exists
- Check file permissions
- Check max upload size in config
- Check disk space

### API Errors

- Check CORS is enabled
- Check Flask is running
- Check API requests use correct content-type
- Check backend logs for errors

## Contributing Guidelines

When adding features:
1. Create model in appropriate file
2. Create service for business logic
3. Create routes to expose API
4. Add error handling
5. Document in this README
6. Test with example requests

## Future Enhancements

- [ ] Batch processing with Celery
- [ ] Advanced filtering and search
- [ ] Payment processing integration
- [ ] Advanced analytics
- [ ] Multi-language support
- [ ] GraphQL API
- [ ] WebSocket for real-time updates
- [ ] Advanced access controls (RBAC)
- [ ] Data versioning
- [ ] Automated compliance checks
