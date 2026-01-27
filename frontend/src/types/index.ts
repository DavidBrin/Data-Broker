/**
 * Type definitions for the Data Broker application.
 * Provides TypeScript interfaces for all data structures.
 */

// User types
export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  organization?: string;
  role: 'supplier' | 'buyer' | 'admin';
  is_supplier: boolean;
  is_buyer: boolean;
  country?: string;
  created_at: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// Dataset types
export type DataSourceType = 'crowd' | 'university' | 'enterprise';
export type PipelineStage = 'ingested' | 'stored' | 'refining' | 'refined' | 'packaged' | 'listed' | 'sold';

export interface Dataset {
  id: string;
  name: string;
  description: string;
  source_type: DataSourceType;
  owner_id: string;
  file_count: number;
  total_size_bytes: number;
  stage: PipelineStage;
  quality_score: number;
  legal_attestation: boolean;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface IngestionRecord {
  id: string;
  dataset_id: string;
  files_validated: number;
  files_passed: number;
  files_failed: number;
  validation_errors: any[];
  stored_location: string;
  legal_rights_confirmed: boolean;
  created_at: string;
}

// Refinement types
export interface RefinementMetrics {
  quality_scores: Record<string, number>;
  overall_quality: number;
  items_processed: number;
  items_passed: number;
  items_rejected: number;
  duplicates_found: number;
  classifications: Record<string, any>;
  created_at: string;
}

export interface RefinementStatus {
  status: 'not_refined' | 'refined';
  overall_quality?: number;
  items_processed?: number;
  items_passed?: number;
  items_rejected?: number;
  duplicates_found?: number;
  classifications?: Record<string, any>;
  last_refined_at?: string;
}

// Package types
export interface DataPackage {
  id: string;
  name: string;
  description: string;
  version: string;
  quality_score: number;
  items_count: number;
  size_bytes: number;
  manifest: any;
  quality_metrics: any;
  provenance: any[];
  license_type: string;
  is_available: boolean;
  is_for_sale: boolean;
  price_usd?: number;
  created_at: string;
}

// Marketplace types
export interface MarketplaceListing {
  id: string;
  title: string;
  description: string;
  category: string;
  price_usd: number;
  average_rating: number;
  review_count: number;
  download_count: number;
  is_featured: boolean;
  package_name: string;
  quality_score: number;
}

export interface Sale {
  sale_id: string;
  package_id: string;
  amount_paid: number;
  access_token: string;
  downloads_remaining: number | string;
  license_expires: string | null;
  created_at: string;
}

export interface MarketplaceStats {
  total_listings: number;
  published_listings: number;
  total_sales: number;
  total_revenue_usd: number;
  average_listing_price: number;
  average_rating: number;
}

// API Response types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}
