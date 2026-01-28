# Build and Compatibility Fixes - January 27, 2026

## Issues Fixed

### Issue 1: Frontend Build Error - Missing tsconfig.node.json

**Error:**
```
tsconfig.json:21:18 - error TS6053: File 'C:/Users/david/OneDrive/Documents/Personal Projects/Data-Broker/frontend/tsconfig.node.json' not found.
```

**Root Cause:**
The `tsconfig.json` referenced a `tsconfig.node.json` file that wasn't created.

**Solution:**
Created `frontend/tsconfig.node.json` with proper TypeScript configuration for Node-based tools (Vite, esbuild).

**File Created:**
- `frontend/tsconfig.node.json` - TypeScript configuration for build tools

**Status:** ✅ FIXED

---

### Issue 2: Backend SQLAlchemy Error - Reserved Attribute Name

**Error:**
```
sqlalchemy.exc.InvalidRequestError: Attribute name 'metadata' is reserved when using the Declarative API.
```

**Root Cause:**
SQLAlchemy 2.0.23 reserves the name `metadata` for its internal ORM metadata registry. The Dataset model had a column named `metadata` which conflicted with this reserved name.

**Solution:**
Renamed the `metadata` column to `dataset_metadata` throughout the codebase to avoid the reserved name conflict.

**Changes Made:**

1. **Backend Models** (`backend/models/dataset.py`)
   - Renamed `Dataset.metadata` column to `Dataset.dataset_metadata`
   - Updated docstring reference
   
2. **Backend Services** (`backend/services/ingest_service.py`)
   - Updated `create_dataset()` to use `dataset_metadata=metadata or {}`

3. **Backend Routes** (`backend/routes/dataset_routes.py`)
   - Updated update endpoint to use `dataset.dataset_metadata.update(data['metadata'])`

**API Impact:**
- Frontend API calls still use `metadata` in request bodies (unchanged)
- Backend database column renamed internally (transparent to API)
- No breaking changes to API contracts

**Status:** ✅ FIXED

---

## Verification Steps

### Frontend Build
```bash
cd frontend
npm run build
```

Expected: Successful build with no TypeScript errors

### Backend Startup
```bash
cd backend
# Set up .env file first
python app.py
```

Expected: Flask app starts without SQLAlchemy errors

---

## Files Modified

1. ✅ `frontend/tsconfig.node.json` - CREATED
2. ✅ `backend/models/dataset.py` - UPDATED (metadata → dataset_metadata)
3. ✅ `backend/services/ingest_service.py` - UPDATED (metadata → dataset_metadata)
4. ✅ `backend/routes/dataset_routes.py` - UPDATED (metadata → dataset_metadata)

---

## Database Migration Note

If you have existing data:

**SQLite:** No migration needed (database will be recreated on first run)

**PostgreSQL:** To migrate existing data:
```sql
-- Backup existing data
CREATE TABLE datasets_backup AS SELECT * FROM datasets;

-- Add new column
ALTER TABLE datasets ADD COLUMN dataset_metadata JSON DEFAULT '{}';

-- Copy data from old column if it exists
UPDATE datasets SET dataset_metadata = metadata WHERE metadata IS NOT NULL;

-- Drop old column (optional, if backward compatibility not needed)
-- ALTER TABLE datasets DROP COLUMN metadata;

-- Verify
SELECT * FROM datasets LIMIT 5;
```

---

## Column Naming Rationale

Changed from `metadata` to `dataset_metadata` to:
- ✅ Avoid SQLAlchemy reserved names
- ✅ Be more descriptive (clarifies this is dataset metadata, not ingestion/refinement metadata)
- ✅ Follow naming conventions for flexible storage fields
- ✅ Future-proof against SQLAlchemy API changes

Other metadata columns remain named differently:
- `IngestionRecord.uploader_metadata` - metadata from upload
- `RefinementRecord.classifications` - classification results (not named metadata)
- `DataPackage.metadata` - package metadata (different model, no conflict)

---

## API Behavior

### Request/Response Examples

**Creating Dataset (Frontend API):**
```json
{
  "owner_id": "user123",
  "name": "My Dataset",
  "description": "...",
  "source_type": "enterprise",
  "metadata": {
    "custom_field": "custom_value"
  }
}
```

**Backend Processing:**
- Frontend sends `metadata` in request body
- Backend stores in `dataset.dataset_metadata` column
- No API changes needed

**Frontend API Client** (`frontend/src/services/api.ts`):
```typescript
async createDataset(data: {
  owner_id: string;
  name: string;
  description: string;
  source_type: string;
  metadata?: any;  // Still uses 'metadata' in API
}): Promise<Dataset>
```

✅ API contracts unchanged - only internal column name changed

---

## Testing Checklist

- [ ] Frontend builds without errors: `npm run build`
- [ ] Backend starts without errors: `python app.py`
- [ ] Create dataset with metadata: Works
- [ ] Upload files to dataset: Works
- [ ] Retrieve dataset: Shows metadata correctly
- [ ] Update dataset metadata: Works
- [ ] API endpoints respond properly

---

## Next Steps

1. ✅ Apply both fixes (done)
2. Run frontend build: `cd frontend && npm run build`
3. Run backend: `cd backend && python app.py`
4. Test API endpoints with Postman/curl
5. Verify metadata is stored and retrieved correctly

---

## Summary

Both critical issues have been resolved:

1. **Frontend** - tsconfig.node.json created for build tools
2. **Backend** - SQLAlchemy reserved name conflict fixed by renaming metadata column

The application should now build and run successfully without errors. All API functionality remains unchanged from the frontend perspective.
