# Data Broker Frontend

React + TypeScript frontend application for the Data Broker platform.

## Overview

This is a modern, accessible web interface for the Data Broker data refinement platform. It provides interfaces for both data suppliers (to ingest and refine data) and data buyers (to browse and purchase datasets).

## Architecture

### Directory Structure

```
src/
├── components/        # Reusable UI components
│   ├── Navbar.tsx
│   ├── Card.tsx
│   └── LoadingSpinner.tsx
├── pages/            # Page components for routing
│   ├── HomePage.tsx
│   ├── LoginPage.tsx
│   ├── RegisterPage.tsx
│   ├── SupplierDashboard.tsx
│   ├── BuyerDashboard.tsx
│   ├── IngestionPage.tsx
│   ├── RefinementMonitor.tsx
│   ├── PackageCreation.tsx
│   └── MarketplaceBrowse.tsx
├── services/         # API client
│   └── api.ts
├── types/           # TypeScript interfaces
│   └── index.ts
├── styles/          # Global CSS
│   └── globals.css
├── App.tsx          # Main app component
└── index.tsx        # Entry point
```

### Component Structure

Each page represents a major workflow:

1. **HomePage** - Marketing landing page
2. **LoginPage / RegisterPage** - Authentication
3. **SupplierDashboard** - Dashboard for data suppliers
4. **BuyerDashboard** - Dashboard for data buyers
5. **IngestionPage** - Upload and create datasets (Supplier)
6. **RefinementMonitor** - View refinement pipeline results (Supplier)
7. **PackageCreation** - Create marketplaces packages (Supplier)
8. **MarketplaceBrowse** - Browse and purchase datasets (Buyer)

### API Service

The `ApiService` class in `src/services/api.ts` provides a type-safe interface to the backend API. All methods return typed responses.

### Styling Approach

- **CSS Variables**: Global color and spacing variables defined in `globals.css`
- **Utility Classes**: Common utilities like `.btn`, `.flex`, `.gap-md`
- **Component Styles**: Each component has its own CSS file for scoped styling
- **Responsive Design**: Mobile-first approach with media queries

## Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:3000` and will automatically proxy API calls to `http://localhost:5000/api`.

### Building for Production

```bash
npm run build
npm run preview
```

## Key Features

### For Data Suppliers

- **Dataset Management**: Create, upload, and manage datasets
- **Refinement Pipeline**: Run quality scoring, deduplication, classification
- **Package Creation**: Curate refined data into marketable packages
- **Marketplace Listing**: List packages for sale or return to supplier

### For Data Buyers

- **Marketplace Search**: Browse datasets by category, price, rating
- **Advanced Filtering**: Filter by quality, price range, rating
- **Purchase Flow**: One-click purchase with instant access
- **Download Management**: Track downloads and license expiration

## Design Decisions

### Technology Choices

- **React 18**: Modern component-based UI
- **TypeScript**: Type safety across the entire frontend
- **Vite**: Fast build tool and dev server
- **Axios**: Type-safe HTTP client
- **CSS**: Vanilla CSS with design system variables (no CSS framework needed for prototype)

### Styling System

Uses CSS custom properties (variables) for:
- **Colors**: Primary, secondary, danger, text, backgrounds
- **Spacing**: Consistent spacing scale (xs, sm, md, lg, xl, 2xl)
- **Typography**: Font families, sizes, weights
- **Shadows & Borders**: Elevation and emphasis

This approach provides:
- Easy dark mode support (future)
- Consistent design across all components
- Easy to extend and customize
- Small CSS bundle size

### State Management

Currently uses React hooks for local state. For more complex state needs, consider:
- Redux Toolkit
- Zustand
- Recoil

### API Integration

The `ApiService` class provides:
- Centralized API calls
- Type-safe request/response handling
- Error handling
- Session token management (placeholder)

## Customization Guide

### Adding New Pages

1. Create a new file in `src/pages/YourPage.tsx`
2. Add route in `src/App.tsx`
3. Create corresponding CSS file

Example:

```typescript
import React from 'react';
import { User } from '../types';
import './YourPage.css';

interface YourPageProps {
  user: User;
}

const YourPage: React.FC<YourPageProps> = ({ user }) => {
  return (
    <div className="your-page">
      <h1>Your Page</h1>
      {/* Content */}
    </div>
  );
};

export default YourPage;
```

### Adding New Components

1. Create file in `src/components/YourComponent.tsx`
2. Create corresponding CSS file
3. Export from component and import where needed

### Styling New Elements

Use CSS variable classes:

```css
.my-element {
  color: var(--color-text);
  padding: var(--spacing-lg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
}
```

## Cloud Storage Integration

The frontend is prepared for cloud storage integration. API calls reference cloud buckets, but actual implementation is in the backend.

Update the API service for:
- Direct cloud bucket uploads (Dropbox, Google Drive)
- S3 presigned URLs for large files
- Progress tracking for uploads

## Performance Considerations

- Lazy load pages with React.lazy()
- Implement virtual scrolling for large lists
- Cache API responses
- Optimize images and assets
- Use production build for deployment

## Accessibility

- Semantic HTML
- ARIA labels where needed
- Keyboard navigation support
- Color contrast compliance
- Form labels and descriptions

## Testing

Consider adding:
- Unit tests with Jest
- Component tests with React Testing Library
- E2E tests with Playwright or Cypress

## Environment Variables

Create a `.env` file:

```
VITE_API_URL=http://localhost:5000/api
```

Access in code:
```typescript
const API_URL = import.meta.env.VITE_API_URL;
```

## Troubleshooting

### CORS Errors

The Vite dev server proxies `/api` calls to the backend. Make sure:
- Backend is running on port 5000
- Backend has CORS enabled
- API URL is correct in environment

### TypeScript Errors

- Run `npm run lint` to check for issues
- Ensure all types are properly defined
- Check that async functions are properly typed

### Styling Issues

- Check CSS variable names
- Ensure specificity isn't causing conflicts
- Use browser DevTools to debug

## Future Enhancements

- [ ] Dark mode support
- [ ] Advanced search filters
- [ ] Real-time notifications
- [ ] File upload progress
- [ ] Dataset preview/sample viewer
- [ ] Advanced analytics dashboard
- [ ] Batch operations
- [ ] API documentation viewer

## Contributing

When adding features:
1. Follow the existing component structure
2. Use TypeScript for all new code
3. Add types in `src/types/index.ts`
4. Create corresponding CSS file
5. Update this README
