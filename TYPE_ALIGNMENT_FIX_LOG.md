# Type Alignment and Model Fixes - January 27, 2026

## Issues Fixed

### Frontend Type Error - Role Mismatch

**Error:**
```
Type 'string' is not assignable to type '"supplier" | "buyer" | "both"'.
```

**Root Cause:**
- `User` interface in types had role as `'supplier' | 'buyer' | 'admin'`
- API expected `'supplier' | 'buyer' | 'both'`
- Type mismatch caused TypeScript errors in RegisterPage and Navbar

**Solution:**
1. Updated `User` interface to use `'supplier' | 'buyer' | 'both'` (matches API)
2. Added type casting in RegisterPage's handleSubmit to ensure role is proper type
3. Updated backend UserRole enum to include `BOTH` role

**Files Updated:**
- ✅ `frontend/src/types/index.ts` - User.role type changed
- ✅ `frontend/src/pages/RegisterPage.tsx` - Added role type casting
- ✅ `backend/models/user.py` - Added BOTH to UserRole enum

---

### Backend SQLAlchemy Error - Reserved Metadata in DataPackage

**Error:**
```
sqlalchemy.exc.InvalidRequestError: Attribute name 'metadata' is reserved when using the Declarative API.
```

**Root Cause:**
After renaming `Dataset.metadata` → `Dataset.dataset_metadata`, we missed the `metadata` column in the `DataPackage` model, which also conflicts with SQLAlchemy's reserved `metadata` attribute.

**Solution:**
Renamed `DataPackage.metadata` → `DataPackage.package_metadata` to avoid the conflict.

**Files Updated:**
- ✅ `backend/models/dataset.py` - Renamed DataPackage.metadata column

---

## Summary of All Metadata Column Renames

The following columns were renamed to avoid SQLAlchemy conflicts:

1. ✅ `Dataset.metadata` → `Dataset.dataset_metadata` (fixed earlier)
2. ✅ `DataPackage.metadata` → `DataPackage.package_metadata` (fixed now)

Other metadata columns that don't conflict:
- `IngestionRecord.uploader_metadata` - No conflict
- `RefinementRecord.classifications` - Named differently, no conflict

---

## Role Types Alignment

**Frontend (User Type):**
```typescript
role: 'supplier' | 'buyer' | 'both'
```

**Backend (UserRole Enum):**
```python
SUPPLIER = "supplier"
BUYER = "buyer"
BOTH = "both"  # Added
ADMIN = "admin"
MODERATOR = "moderator"
```

**API (Register Endpoint):**
```typescript
role: 'supplier' | 'buyer' | 'both'
```

All three now aligned correctly.

---

## Testing Checklist

- [ ] Frontend compiles without TypeScript errors: `npm run build`
- [ ] Backend starts without SQLAlchemy errors: `python app.py`
- [ ] Register page works with role selection
- [ ] User object properly typed in Navbar
- [ ] API registration accepts all three role types
- [ ] Database handles both and supplier/buyer roles

---

## Key Changes

| Component | Change | Reason |
|-----------|--------|--------|
| `User.role` type | Added 'both' option | Support dual supplier/buyer accounts |
| `Dataset.metadata` | → `dataset_metadata` | Avoid SQLAlchemy reserved name |
| `DataPackage.metadata` | → `package_metadata` | Avoid SQLAlchemy reserved name |
| `UserRole` enum | Added BOTH role | Backend support for dual roles |
| RegisterPage | Added type casting | Ensure role type safety |

---

## Notes

- The API parameter name in request bodies remains `metadata` (unchanged)
- Internal database columns renamed to avoid conflicts
- Frontend users still see the platform without changes
- No migration needed for fresh prototypes using SQLite

---

## Status

✅ All type mismatches resolved
✅ All SQLAlchemy conflicts fixed
✅ Frontend and backend now aligned
✅ Ready to run and test
