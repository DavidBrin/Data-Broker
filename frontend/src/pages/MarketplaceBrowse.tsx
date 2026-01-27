/**
 * MarketplaceBrowse - Browse and purchase data packages from marketplace.
 */
import React, { useState, useEffect } from 'react';
import { User, MarketplaceListing } from '../types';
import apiService from '../services/api';
import Card from '../components/Card';
import LoadingSpinner from '../components/LoadingSpinner';
import { Search, Star, Download, ShoppingCart } from 'lucide-react';
import './MarketplaceBrowse.css';

interface MarketplaceBrowseProps {
  user: User;
}

const MarketplaceBrowse: React.FC<MarketplaceBrowseProps> = ({ user }) => {
  const [listings, setListings] = useState<MarketplaceListing[]>([]);
  const [featured, setFeatured] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState('');
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');
  const [sortBy, setSortBy] = useState('relevance');

  useEffect(() => {
    const fetchListings = async () => {
      try {
        const [listingsData, featuredData] = await Promise.all([
          apiService.searchMarketplace({ sort_by: sortBy, limit: 20 }),
          apiService.getFeaturedListings(),
        ]);
        setListings(listingsData.results || []);
        setFeatured(featuredData.featured_listings || []);
      } catch (err: any) {
        setError('Failed to load marketplace');
      } finally {
        setLoading(false);
      }
    };

    fetchListings();
  }, [sortBy]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setSearching(true);
    setError('');

    try {
      const results = await apiService.searchMarketplace({
        query,
        category: category || undefined,
        sort_by: sortBy,
        limit: 50,
      });
      setListings(results.results || []);
    } catch (err: any) {
      setError('Search failed');
    } finally {
      setSearching(false);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="marketplace-browse">
      <h1>Data Marketplace</h1>
      <p>Browse thousands of high-quality training datasets</p>

      {/* Search Bar */}
      <form onSubmit={handleSearch} className="search-form">
        <div className="search-input-group">
          <Search size={20} />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search datasets..."
          />
        </div>
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="category-filter"
        >
          <option value="">All Categories</option>
          <option value="text">Text</option>
          <option value="audio">Audio</option>
          <option value="video">Video</option>
          <option value="images">Images</option>
        </select>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="sort-filter"
        >
          <option value="relevance">Relevance</option>
          <option value="price">Price: Low to High</option>
          <option value="rating">Rating</option>
          <option value="recent">Recent</option>
        </select>
        <button type="submit" className="btn btn-primary" disabled={searching}>
          {searching ? 'Searching...' : 'Search'}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}

      {/* Featured Section */}
      {featured.length > 0 && (
        <section className="featured-section">
          <h2>Featured Datasets</h2>
          <div className="listings-grid">
            {featured.map((listing) => (
              <Card key={listing.id} className="listing-card">
                <div className="listing-header">
                  <h3>{listing.title}</h3>
                  <span className="badge featured">Featured</span>
                </div>
                <p className="listing-description">{listing.description?.substring(0, 100)}</p>

                <div className="listing-meta">
                  <div className="meta-item">
                    <span className="label">Category</span>
                    <span className="value">{listing.category || 'General'}</span>
                  </div>
                  <div className="meta-item">
                    <span className="label">Quality</span>
                    <span className="value">{(listing.quality_score * 100).toFixed(0)}%</span>
                  </div>
                  <div className="meta-item">
                    <span className="label">Items</span>
                    <span className="value">
                      {listing.items_count
                        ? listing.items_count.toLocaleString()
                        : 'N/A'}
                    </span>
                  </div>
                </div>

                <div className="listing-footer">
                  <div className="price">${listing.price_usd?.toFixed(2)}</div>
                  <button className="btn btn-primary btn-sm">
                    <ShoppingCart size={16} />
                    Buy
                  </button>
                </div>
              </Card>
            ))}
          </div>
        </section>
      )}

      {/* All Listings */}
      <section className="listings-section">
        <h2>All Datasets ({listings.length})</h2>
        {listings.length === 0 ? (
          <Card>
            <p style={{ textAlign: 'center', padding: '2rem' }}>
              No datasets found. Try adjusting your search.
            </p>
          </Card>
        ) : (
          <div className="listings-grid">
            {listings.map((listing) => (
              <Card key={listing.id} className="listing-card">
                <div className="listing-header">
                  <h3>{listing.title}</h3>
                  <span className="badge">{listing.category}</span>
                </div>

                <p className="listing-description">{listing.description?.substring(0, 100)}</p>

                <div className="rating">
                  {Array(5)
                    .fill(0)
                    .map((_, i) => (
                      <Star
                        key={i}
                        size={16}
                        fill={i < Math.round(listing.average_rating) ? '#f59e0b' : 'none'}
                        color={i < Math.round(listing.average_rating) ? '#f59e0b' : '#d1d5db'}
                      />
                    ))}
                  <span className="rating-text">
                    {listing.average_rating.toFixed(1)} ({listing.review_count} reviews)
                  </span>
                </div>

                <div className="listing-meta">
                  <div className="meta-item">
                    <Download size={16} />
                    {listing.download_count} downloads
                  </div>
                  <div className="meta-item">Quality: {(listing.quality_score * 100).toFixed(0)}%</div>
                </div>

                <div className="listing-footer">
                  <div className="price">${listing.price_usd?.toFixed(2)}</div>
                  <button className="btn btn-primary btn-sm">
                    <ShoppingCart size={16} />
                    Purchase
                  </button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};

export default MarketplaceBrowse;
