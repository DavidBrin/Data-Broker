/**
 * API Service module for communicating with the backend.
 * Handles all HTTP requests to the Data Broker API.
 */
import axios, { AxiosInstance } from 'axios';
import { User, Dataset, DataPackage, MarketplaceListing, Sale } from '../types';

class ApiService {
  private api: AxiosInstance;
  private baseURL: string;

  constructor(baseURL: string = 'http://localhost:5000/api') {
    this.baseURL = baseURL;
    this.api = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // ============ Authentication ============
  
  async register(credentials: {
    username: string;
    email: string;
    password: string;
    full_name?: string;
    organization?: string;
    role: 'supplier' | 'buyer' | 'both';
    country?: string;
  }): Promise<User> {
    const response = await this.api.post('/auth/register', credentials);
    return response.data;
  }

  async login(email: string, password: string): Promise<User> {
    const response = await this.api.post('/auth/login', { email, password });
    return response.data;
  }

  async logout(): Promise<void> {
    await this.api.post('/auth/logout');
  }

  async getProfile(userId: string): Promise<User> {
    const response = await this.api.get(`/auth/profile/${userId}`);
    return response.data;
  }

  // ============ Datasets ============

  async createDataset(data: {
    owner_id: string;
    name: string;
    description: string;
    source_type: 'crowd' | 'university' | 'enterprise';
    metadata?: any;
  }): Promise<Dataset> {
    const response = await this.api.post('/datasets', data);
    return response.data;
  }

  async getDataset(datasetId: string): Promise<Dataset> {
    const response = await this.api.get(`/datasets/${datasetId}`);
    return response.data;
  }

  async listUserDatasets(userId: string): Promise<Dataset[]> {
    const response = await this.api.get(`/datasets/user/${userId}`);
    return response.data.datasets;
  }

  async uploadFiles(
    datasetId: string,
    files: File[],
    legalConfirmed: boolean,
    metadata?: any
  ): Promise<any> {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    formData.append('legal_rights_confirmed', legalConfirmed.toString());
    if (metadata) {
      formData.append('metadata', JSON.stringify(metadata));
    }

    const response = await this.api.post(`/datasets/${datasetId}/ingest`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  async getIngestionStatus(datasetId: string): Promise<any> {
    const response = await this.api.get(`/datasets/${datasetId}/ingestion-status`);
    return response.data;
  }

  // ============ Refinement ============

  async refineDataset(datasetId: string, qualityThreshold: number = 0.5): Promise<any> {
    const response = await this.api.post(`/refinement/refine/${datasetId}`, {
      quality_threshold: qualityThreshold,
    });
    return response.data;
  }

  async getRefinementStatus(datasetId: string): Promise<any> {
    const response = await this.api.get(`/refinement/status/${datasetId}`);
    return response.data;
  }

  async getRefinementMetrics(datasetId: string): Promise<any> {
    const response = await this.api.get(`/refinement/metrics/${datasetId}`);
    return response.data;
  }

  // ============ Packages ============

  async createPackage(data: {
    dataset_id: string;
    name: string;
    description: string;
    version?: string;
    license_type?: string;
  }): Promise<DataPackage> {
    const response = await this.api.post('/packages', data);
    return response.data;
  }

  async getPackage(packageId: string): Promise<DataPackage> {
    const response = await this.api.get(`/packages/${packageId}`);
    return response.data;
  }

  async getPackageManifest(packageId: string): Promise<any> {
    const response = await this.api.get(`/packages/${packageId}/manifest`);
    return response.data;
  }

  async getPackageProvenance(packageId: string): Promise<any> {
    const response = await this.api.get(`/packages/${packageId}/provenance`);
    return response.data;
  }

  async updatePackageForSale(packageId: string, priceUsd: number): Promise<any> {
    const response = await this.api.put(`/packages/${packageId}/sell`, {
      price_usd: priceUsd,
      is_for_sale: true,
    });
    return response.data;
  }

  // ============ Marketplace ============

  async searchMarketplace(params: {
    query?: string;
    category?: string;
    min_price?: number;
    max_price?: number;
    min_rating?: number;
    sort_by?: string;
    limit?: number;
  }): Promise<any> {
    const response = await this.api.get('/marketplace/search', { params });
    return response.data;
  }

  async getMarketplaceStats(): Promise<any> {
    const response = await this.api.get('/marketplace/stats');
    return response.data;
  }

  async getFeaturedListings(): Promise<any> {
    const response = await this.api.get('/marketplace/featured');
    return response.data;
  }

  async createListing(data: {
    package_id: string;
    title: string;
    description: string;
    price_usd: number;
    category: string;
    tags?: string[];
    is_featured?: boolean;
  }): Promise<any> {
    const response = await this.api.post('/marketplace/listings', data);
    return response.data;
  }

  async publishListing(listingId: string): Promise<any> {
    const response = await this.api.put(`/marketplace/listings/${listingId}/publish`);
    return response.data;
  }

  async purchasePackage(listingId: string, buyerId: string): Promise<Sale> {
    const response = await this.api.post('/marketplace/purchase', {
      listing_id: listingId,
      buyer_id: buyerId,
    });
    return response.data;
  }

  async getPurchaseDetails(saleId: string): Promise<Sale> {
    const response = await this.api.get(`/marketplace/purchases/${saleId}`);
    return response.data;
  }

  async addReview(listingId: string, data: {
    reviewer_id: string;
    rating: number;
    comment?: string;
  }): Promise<any> {
    const response = await this.api.post(`/marketplace/listings/${listingId}/review`, data);
    return response.data;
  }
}

// Export singleton instance
export default new ApiService();
