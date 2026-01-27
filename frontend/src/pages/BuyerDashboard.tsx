/**
 * BuyerDashboard - Main dashboard for data buyers.
 * Shows purchased packages and marketplace recommendations.
 */
import React, { useState, useEffect } from 'react';
import { User } from '../types';
import apiService from '../services/api';
import Card from '../components/Card';
import LoadingSpinner from '../components/LoadingSpinner';
import { ShoppingCart } from 'lucide-react';
import './Dashboard.css';

interface BuyerDashboardProps {
  user: User;
}

const BuyerDashboard: React.FC<BuyerDashboardProps> = ({ user }) => {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await apiService.getMarketplaceStats();
        setStats(data);
      } catch (err: any) {
        setError('Failed to load marketplace stats');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) return <LoadingSpinner />;

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Data Buyer Dashboard</h1>
        <p>Welcome, {user.username}!</p>
      </div>

      {/* Quick Stats */}
      <div className="stats-grid">
        <Card title="Available Datasets" description={stats?.published_listings?.toString()} />
        <Card title="Total Purchases" description={stats?.total_sales?.toString()} />
        <Card
          title="Total Spent"
          description={`$${(stats?.total_revenue_usd || 0).toFixed(2)}`}
        />
      </div>

      {error && <div className="error-message">{error}</div>}

      {/* Browse Marketplace */}
      <div className="marketplace-section">
        <Card>
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <ShoppingCart size={48} style={{ margin: '0 auto 1rem', color: '#2563eb' }} />
            <h3>Browse the Marketplace</h3>
            <p>Explore thousands of high-quality training datasets</p>
            <a href="/marketplace" className="btn btn-primary" style={{ marginTop: '1rem' }}>
              Go to Marketplace
            </a>
          </div>
        </Card>
      </div>

      {/* Marketplace Info */}
      <div className="info-section">
        <h2>Marketplace Stats</h2>
        <div className="stats-grid">
          <Card
            title="Average Rating"
            description={stats?.average_rating?.toFixed(1) || '0'}
          />
          <Card
            title="Avg Price"
            description={`$${(stats?.average_listing_price || 0).toFixed(2)}`}
          />
        </div>
      </div>
    </div>
  );
};

export default BuyerDashboard;
