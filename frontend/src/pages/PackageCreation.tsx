/**
 * PackageCreation - Create and list curated data packages.
 */
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { User } from '../types';
import apiService from '../services/api';
import Card from '../components/Card';
import LoadingSpinner from '../components/LoadingSpinner';
import './PackageCreation.css';

interface PackageCreationProps {
  user: User;
}

const PackageCreation: React.FC<PackageCreationProps> = ({ user }) => {
  const { datasetId } = useParams<{ datasetId: string }>();
  const navigate = useNavigate();
  const [dataset, setDataset] = useState<any>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    version: '1.0',
    license_type: 'proprietary',
  });
  const [listing, setListing] = useState({
    for_sale: false,
    price_usd: 0,
  });
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (!datasetId) return;

    const fetchDataset = async () => {
      try {
        const data = await apiService.getDataset(datasetId);
        setDataset(data);
        setFormData({ ...formData, name: `${data.name} Package` });
      } catch (err: any) {
        setError('Failed to load dataset');
      } finally {
        setLoading(false);
      }
    };

    fetchDataset();
  }, [datasetId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!datasetId) return;

    setCreating(true);
    setError('');

    try {
      const packageData = await apiService.createPackage({
        dataset_id: datasetId,
        name: formData.name,
        description: formData.description,
        version: formData.version,
        license_type: formData.license_type,
      });

      if (listing.for_sale) {
        await apiService.updatePackageForSale(packageData.id, listing.price_usd);
      }

      setSuccess('Package created successfully!');
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to create package');
    } finally {
      setCreating(false);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="package-creation">
      <h1>Create Data Package</h1>
      {dataset && <p>From dataset: <strong>{dataset.name}</strong></p>}

      <div className="package-form-container">
        <form onSubmit={handleSubmit} className="package-form">
          <Card title="Package Details">
            <div className="form-group">
              <label>Package Name *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label>Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={4}
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Version</label>
                <input
                  type="text"
                  value={formData.version}
                  onChange={(e) => setFormData({ ...formData, version: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label>License Type</label>
                <select
                  value={formData.license_type}
                  onChange={(e) => setFormData({ ...formData, license_type: e.target.value })}
                >
                  <option value="proprietary">Proprietary</option>
                  <option value="cc-by">CC-BY</option>
                  <option value="cc-by-sa">CC-BY-SA</option>
                  <option value="cc-by-nc">CC-BY-NC</option>
                </select>
              </div>
            </div>
          </Card>

          <Card title="Marketplace Listing">
            <div className="form-group">
              <label>
                <input
                  type="checkbox"
                  checked={listing.for_sale}
                  onChange={(e) => setListing({ ...listing, for_sale: e.target.checked })}
                />
                List for sale on marketplace
              </label>
            </div>

            {listing.for_sale && (
              <div className="form-group">
                <label>Price (USD) *</label>
                <input
                  type="number"
                  value={listing.price_usd}
                  onChange={(e) =>
                    setListing({ ...listing, price_usd: parseFloat(e.target.value) })
                  }
                  min="0"
                  step="0.01"
                  required={listing.for_sale}
                />
              </div>
            )}
          </Card>

          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}

          <button type="submit" className="btn btn-primary btn-block" disabled={creating}>
            {creating ? 'Creating Package...' : 'Create Package'}
          </button>
        </form>

        {dataset && (
          <Card title="Dataset Summary">
            <div className="summary">
              <div className="summary-row">
                <span>Files:</span>
                <strong>{dataset.file_count}</strong>
              </div>
              <div className="summary-row">
                <span>Size:</span>
                <strong>{(dataset.total_size_bytes / 1024 / 1024).toFixed(2)}MB</strong>
              </div>
              <div className="summary-row">
                <span>Quality Score:</span>
                <strong>{(dataset.quality_score * 100).toFixed(1)}%</strong>
              </div>
              <div className="summary-row">
                <span>Status:</span>
                <strong>{dataset.stage}</strong>
              </div>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};

export default PackageCreation;
