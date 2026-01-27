/**
 * SupplierDashboard - Main dashboard for data suppliers.
 * Shows datasets in progress through the pipeline.
 */
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Plus, TrendingUp, Package, Zap } from 'lucide-react';
import { User, Dataset } from '../types';
import apiService from '../services/api';
import Card from '../components/Card';
import LoadingSpinner from '../components/LoadingSpinner';
import './Dashboard.css';

interface SupplierDashboardProps {
  user: User;
}

const SupplierDashboard: React.FC<SupplierDashboardProps> = ({ user }) => {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDatasets = async () => {
      try {
        const data = await apiService.listUserDatasets(user.id);
        setDatasets(data);
      } catch (err: any) {
        setError('Failed to load datasets');
      } finally {
        setLoading(false);
      }
    };

    fetchDatasets();
  }, [user.id]);

  if (loading) return <LoadingSpinner />;

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Data Supplier Dashboard</h1>
        <Link to="/ingest" className="btn btn-primary">
          <Plus size={18} />
          New Dataset
        </Link>
      </div>

      {/* Quick Stats */}
      <div className="stats-grid">
        <Card title="Total Datasets" description={datasets.length.toString()} />
        <Card
          title="Refined Data"
          description={datasets.filter((d) => d.stage === 'refined').length.toString()}
        />
        <Card
          title="Listed for Sale"
          description={datasets.filter((d) => d.stage === 'listed').length.toString()}
        />
      </div>

      {error && <div className="error-message">{error}</div>}

      {/* Datasets Table */}
      <div className="datasets-section">
        <h2>Your Datasets</h2>
        {datasets.length === 0 ? (
          <Card>
            <p className="empty-state">
              No datasets yet.{' '}
              <Link to="/ingest">Create your first dataset</Link>
            </p>
          </Card>
        ) : (
          <div className="datasets-grid">
            {datasets.map((dataset) => (
              <Card key={dataset.id} className="dataset-card">
                <h3>{dataset.name}</h3>
                <p className="dataset-description">{dataset.description}</p>
                <div className="dataset-info">
                  <span className="badge">{dataset.source_type}</span>
                  <span className="badge stage">{dataset.stage}</span>
                  {dataset.quality_score > 0 && (
                    <span className="quality-score">
                      Quality: {(dataset.quality_score * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
                <div className="dataset-stats">
                  <small>Files: {dataset.file_count}</small>
                  <small>Size: {(dataset.total_size_bytes / 1024 / 1024).toFixed(2)}MB</small>
                </div>
                <div className="card-footer">
                  <Link
                    to={`/refinement/${dataset.id}`}
                    className="btn btn-outline btn-sm"
                  >
                    <Zap size={16} />
                    Refine
                  </Link>
                  {dataset.stage === 'refined' && (
                    <Link
                      to={`/package/${dataset.id}`}
                      className="btn btn-outline btn-sm"
                    >
                      <Package size={16} />
                      Package
                    </Link>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SupplierDashboard;
