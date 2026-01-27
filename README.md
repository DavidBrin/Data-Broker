# DataBroker - Data Refinement Platform for AI

End-to-end data refinery platform that turns massive amounts of raw, messy, unstructured data into high-quality, model-ready training assets.

## Vision

DataBroker operates as an end-to-end data refinery for AI, implementing the pipeline:

**[SOURCE] → [INGEST] → [STORE] → [REFINE] → [PACKAGE] → [SELL]**

Instead of just collecting or labeling new data, we ingest data that already exists (from universities, enterprises, crowd contributors) and use AI systems to sort, filter, score, classify, and extract the high-signal subset valuable for training models.

## Platform Features

### For Data Suppliers

- **Easy Ingestion**: Upload files directly, connect cloud buckets, or use APIs
- **Legal Compliance**: Comprehensive metadata and rights attestations
- **Automatic Refinement**: AI-powered quality scoring, deduplication, classification
- **Transparent Metrics**: Detailed quality reports and provenance tracking
- **Flexible Returns**: Receive cleaned data or broker sales on marketplace

### For Data Buyers

- **Curated Marketplace**: Browse thousands of high-quality training datasets
- **Quality Assurance**: Detailed metrics, classifications, and quality scores
- **Flexible Licensing**: Multiple license types and pricing options
- **Easy Integration**: One-click purchase with instant download access
- **Full Provenance**: Complete tracking of data processing pipeline

## Project Structure

```
data-broker/
├── backend/                 # Flask REST API
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   ├── models/             # Database models
│   ├── routes/             # API endpoints
│   ├── services/           # Business logic
│   ├── pipeline/           # Refinement pipeline
│   └── README.md
│
├── frontend/               # React + TypeScript
│   ├── src/
│   │   ├── pages/         # Page components
│   │   ├── components/    # Reusable components
│   │   ├── services/      # API client
│   │   ├── types/         # TypeScript interfaces
│   │   └── styles/        # CSS
│   ├── package.json
│   ├── vite.config.ts
│   ├── index.html
│   └── README.md
│
└── README.md             # This file
```

## Tech Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLAlchemy ORM (SQLite/PostgreSQL)
- **APIs**: RESTful with CORS support
- **Storage**: Local filesystem + cloud-ready (S3, GCS, Azure)

### Frontend
- **Framework**: React 18
- **Language**: TypeScript
- **Build Tool**: Vite
- **HTTP Client**: Axios
- **Styling**: CSS with design system

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- (Optional) PostgreSQL for production

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Backend runs on `http://localhost:5000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000` and proxies API calls to backend.

### Quick Demo Flow

1. **Register Account**: Go to `/register`, create account as "Supplier"
2. **Create Dataset**: Go to `/ingest`, create a new dataset
3. **Upload Files**: Upload test files (images, audio, text)
4. **Run Refinement**: Go to dataset refinement page, run pipeline
5. **Create Package**: Create curated package with quality metrics
6. **List for Sale**: Set price and list on marketplace
7. **Browse Marketplace**: As buyer, search and view datasets

## API Documentation

Complete API documentation in [backend/README.md](backend/README.md)

### Example Requests

**Create Dataset:**
```bash
curl -X POST http://localhost:5000/api/datasets/ \
  -H "Content-Type: application/json" \
  -d '{
    "owner_id": "user123",
    "name": "My Dataset",
    "source_type": "enterprise"
  }'
```

**Upload Files:**
```bash
curl -X POST http://localhost:5000/api/datasets/dataset-id/ingest \
  -F "files=@file1.mp3" \
  -F "legal_rights_confirmed=true"
```

**Run Refinement:**
```bash
curl -X POST http://localhost:5000/api/refinement/refine/dataset-id \
  -H "Content-Type: application/json" \
  -d '{"quality_threshold": 0.5}'
```

**Search Marketplace:**
```bash
curl "http://localhost:5000/api/marketplace/search?query=audio&category=audio&sort_by=rating"
```

## Architecture Overview

### Data Flow

1. **INGEST**: Suppliers upload raw data with metadata
2. **STORE**: Files stored in cold storage (local or cloud)
3. **REFINE**: AI pipeline evaluates quality, detects duplicates, classifies
4. **PACKAGE**: Curated datasets packaged with manifests and metrics
5. **SELL**: Listed on marketplace or returned to supplier
6. **PURCHASE**: Buyers search, review, and purchase with access tokens

### Database Schema

Key entities:
- **Users**: Accounts with supplier/buyer roles
- **Datasets**: Raw data tracking through pipeline
- **RefinementRecords**: Quality scoring results
- **DataPackages**: Curated, ready-for-sale packages
- **MarketplaceListings**: Marketplace listings with pricing
- **Sales**: Purchase transactions and access tracking
- **Reviews**: Customer ratings and feedback

### Refinement Pipeline

The core product: AI-powered data quality assessment

**Components:**
1. **Quality Scorer**: Evaluates completeness, clarity, relevance, validity
2. **Deduplicator**: Finds duplicates via hashing and semantic similarity
3. **Classifier**: Detects language, modality, domain, content type
4. **Filterer**: Removes low-quality items based on threshold

**Currently**: Placeholder implementations for prototype
**Production**: Integrate actual ML models for each stage

## Cloud Storage

The system is designed for cloud integration but uses local storage in prototype.

### To Enable Cloud Storage

Update `config.py`:
```python
USE_CLOUD_STORAGE = True
AWS_S3_BUCKET = "my-bucket"
AWS_ACCESS_KEY = "xxx"
AWS_SECRET_KEY = "xxx"
```

Then implement cloud methods in `services/ingest_service.py`

**Supported Providers:**
- AWS S3 (boto3)
- Google Cloud Storage (google-cloud-storage)
- Azure Blob Storage (azure-storage-blob)

## Key Design Decisions

### Modularity

- **Services Layer**: Business logic separated from routes
- **Pipeline Components**: Pluggable quality scoring, deduplication, classification
- **Flexible Models**: JSON fields for metadata and classifications
- **Component-Based UI**: Reusable React components

### Type Safety

- Backend: Python type hints (where applicable)
- Frontend: Full TypeScript with strict mode
- Shared types in `frontend/src/types/index.ts`

### Scalability

- Prepared for async jobs (Celery) for long-running pipeline
- Database indexes on frequently queried fields
- API caching support
- Cloud storage ready

### Security

- Password hashing with werkzeug
- File upload validation
- CORS enabled
- SQL injection protection (SQLAlchemy ORM)
- Session-based auth (JWT in production)

## Development Workflow

### Adding a New Feature

1. **Design**: Update data model if needed
2. **Backend**: Create/update model, service, routes
3. **Frontend**: Create page/component, update types, add API calls
4. **Test**: Use curl or Postman for backend, browser for frontend
5. **Document**: Update README files

### Running in Development

**Terminal 1 - Backend:**
```bash
cd backend
FLASK_ENV=development python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Visit `http://localhost:3000` and start developing

### Debugging

**Backend:**
- Add breakpoints and use pdb
- Check Flask debug mode in config.py
- Review logs in terminal

**Frontend:**
- Use browser DevTools (F12)
- Check React DevTools extension
- Use console.log for debugging

## File Upload Limits

Default limits in `config.py`:
- Max file size: 5GB
- Per request limit: ~5GB
- Text: 100MB per file
- Audio: 500MB per file
- Video: 2GB per file
- Images: 50MB per file

Adjust in `backend/config.py` as needed.

## Deployment

### Quick Deploy (Local Testing)

```bash
# Backend
cd backend
pip install -r requirements.txt
FLASK_ENV=production python app.py

# Frontend (new terminal)
cd frontend
npm install
npm run build
npm run preview
```

### Production Deployment

See detailed guides in:
- [backend/README.md](backend/README.md#deployment)
- [frontend/README.md](frontend/README.md#deployment)

## Testing

### Manual Testing

1. **Auth Flow**: Register, login, logout
2. **Supplier Flow**: Create dataset → ingest → refine → package → list
3. **Buyer Flow**: Search marketplace → view details → purchase
4. **Pipeline**: Upload files → run refinement → check metrics

### Automated Testing

Create test suites:
- Backend: pytest
- Frontend: React Testing Library
- E2E: Playwright

## Performance Tips

- Enable caching in production
- Use database indexes
- Implement async jobs for refinement
- Optimize images and assets
- Use CDN for static files
- Enable gzip compression

## Roadmap

**Phase 1 (Prototype):**
- [x] User authentication
- [x] Dataset ingestion
- [x] Refinement pipeline framework
- [x] Package creation
- [x] Basic marketplace

**Phase 2 (MVP):**
- [ ] Real ML models for quality scoring
- [ ] Payment processing
- [ ] Advanced search and filtering
- [ ] Analytics dashboard
- [ ] Cloud storage integration

**Phase 3 (Scale):**
- [ ] Batch processing with Celery
- [ ] Advanced access controls (RBAC)
- [ ] Data versioning
- [ ] APIs for programmatic access
- [ ] Mobile app
- [ ] Compliance features (GDPR, etc.)

## Environment Variables

Create `.env` files:

**Backend** (`backend/.env`):
```
FLASK_ENV=development
SECRET_KEY=dev-key-change-in-production
DATABASE_URL=sqlite:///data_broker.db
UPLOAD_FOLDER=uploads
USE_CLOUD_STORAGE=false
```

**Frontend** (`frontend/.env`):
```
VITE_API_URL=http://localhost:5000/api
```

## Troubleshooting

### Backend won't start
- Check Python version (3.8+)
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check port 5000 is not in use
- Review error in terminal

### Frontend won't run
- Check Node.js version (16+)
- Clear node_modules: `rm -rf node_modules && npm install`
- Check port 3000 is not in use
- Check backend is running (needed for API calls)

### CORS errors
- Backend CORS is enabled in app.py
- Frontend proxies /api to localhost:5000 in vite.config.ts
- Check both servers are running

### Database errors
- Check DATABASE_URL is correct
- For SQLite, check file permissions
- For PostgreSQL, check connection string
- Run `db.create_all()` in Python shell to create tables

## Contributing

Contributions welcome! Please:
1. Create feature branch
2. Make changes with clear commits
3. Update documentation
4. Test your changes
5. Submit pull request

## License

To be determined

## Contact

For questions or support, contact the development team.

## Key Files to Understand

- **Backend Entry**: [backend/app.py](backend/app.py) - Flask app factory
- **Frontend Entry**: [frontend/src/App.tsx](frontend/src/App.tsx) - React app structure
- **Backend Models**: [backend/models/dataset.py](backend/models/dataset.py) - Core data models
- **API Service**: [frontend/src/services/api.ts](frontend/src/services/api.ts) - API client
- **Pipeline**: [backend/pipeline/](backend/pipeline/) - Quality scoring and refinement

## Next Steps

1. Read [backend/README.md](backend/README.md) for API details
2. Read [frontend/README.md](frontend/README.md) for UI details
3. Try the demo flow above
4. Customize for your use case
5. Deploy to production
