/**
 * IngestionPage - Data upload and ingestion interface.
 * Allows suppliers to upload files and provide metadata.
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, Check } from 'lucide-react';
import { User } from '../types';
import apiService from '../services/api';
import './IngestionPage.css';

interface IngestionPageProps {
  user: User;
}

const IngestionPage: React.FC<IngestionPageProps> = ({ user }) => {
  const navigate = useNavigate();
  const [step, setStep] = useState<'create' | 'upload' | 'confirm'>('create');
  const [datasetId, setDatasetId] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    source_type: 'crowd' as 'crowd' | 'university' | 'enterprise',
  });
  const [files, setFiles] = useState<File[]>([]);
  const [legalConfirmed, setLegalConfirmed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Step 1: Create Dataset
  const handleCreateDataset = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await apiService.createDataset({
        owner_id: user.id,
        name: formData.name,
        description: formData.description,
        source_type: formData.source_type,
      });
      setDatasetId(response.id);
      setStep('upload');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to create dataset');
    } finally {
      setLoading(false);
    }
  };

  // Step 2: Upload Files
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const handleUploadFiles = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!files.length) {
      setError('Please select at least one file');
      return;
    }

    if (!legalConfirmed) {
      setError('Please confirm you have rights to this data');
      return;
    }

    setError('');
    setLoading(true);

    try {
      await apiService.uploadFiles(datasetId, files, legalConfirmed);
      setSuccess('Files uploaded successfully!');
      setStep('confirm');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to upload files');
    } finally {
      setLoading(false);
    }
  };

  // Step 3: Confirmation
  const handleComplete = () => {
    navigate(`/refinement/${datasetId}`);
  };

  return (
    <div className="ingestion-page">
      <div className="ingestion-container">
        <h1>Ingest New Dataset</h1>

        {/* Progress Indicator */}
        <div className="progress-indicator">
          <div className={`step ${step === 'create' ? 'active' : ''}`}>
            <span>1</span>
            <p>Create Dataset</p>
          </div>
          <div className="step-connector"></div>
          <div className={`step ${step === 'upload' ? 'active' : ''}`}>
            <span>2</span>
            <p>Upload Files</p>
          </div>
          <div className="step-connector"></div>
          <div className={`step ${step === 'confirm' ? 'active' : ''}`}>
            <span>3</span>
            <p>Confirm</p>
          </div>
        </div>

        {/* Step 1: Create Dataset */}
        {step === 'create' && (
          <form onSubmit={handleCreateDataset} className="ingestion-form">
            <h2>Step 1: Create Dataset</h2>

            <div className="form-group">
              <label>Dataset Name *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., English Customer Service Calls"
                required
              />
            </div>

            <div className="form-group">
              <label>Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Describe your dataset..."
                rows={4}
              />
            </div>

            <div className="form-group">
              <label>Data Source Type *</label>
              <select
                value={formData.source_type}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    source_type: e.target.value as 'crowd' | 'university' | 'enterprise',
                  })
                }
              >
                <option value="crowd">Crowd Contributors</option>
                <option value="university">University/Research</option>
                <option value="enterprise">Enterprise</option>
              </select>
            </div>

            {error && <div className="error-message">{error}</div>}

            <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
              {loading ? 'Creating...' : 'Continue to Upload'}
            </button>
          </form>
        )}

        {/* Step 2: Upload Files */}
        {step === 'upload' && (
          <form onSubmit={handleUploadFiles} className="ingestion-form">
            <h2>Step 2: Upload Files</h2>

            <div className="upload-area">
              <Upload size={48} />
              <h3>Drag and drop files here</h3>
              <p>or</p>
              <label className="file-input-label">
                Click to select files
                <input
                  type="file"
                  multiple
                  onChange={handleFileChange}
                  style={{ display: 'none' }}
                />
              </label>
              <p className="upload-info">Supported: images, videos, audio, documents</p>
            </div>

            {files.length > 0 && (
              <div className="file-list">
                <h4>Selected Files ({files.length})</h4>
                <ul>
                  {files.map((file, idx) => (
                    <li key={idx}>
                      {file.name} ({(file.size / 1024 / 1024).toFixed(2)}MB)
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="form-group">
              <label>
                <input
                  type="checkbox"
                  checked={legalConfirmed}
                  onChange={(e) => setLegalConfirmed(e.target.checked)}
                />
                I confirm that I have the rights to use and upload this data
              </label>
            </div>

            {error && <div className="error-message">{error}</div>}
            {success && <div className="success-message">{success}</div>}

            <div className="button-group">
              <button
                type="button"
                onClick={() => setStep('create')}
                className="btn btn-outline"
              >
                Back
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading || !files.length || !legalConfirmed}
              >
                {loading ? 'Uploading...' : 'Upload Files'}
              </button>
            </div>
          </form>
        )}

        {/* Step 3: Confirmation */}
        {step === 'confirm' && (
          <div className="confirmation">
            <div className="success-icon">
              <Check size={64} />
            </div>
            <h2>Dataset Created Successfully!</h2>
            <p>Your data has been uploaded and is ready for refinement.</p>
            <div className="next-steps">
              <h3>Next Steps:</h3>
              <ol>
                <li>Run the refinement pipeline to quality-score your data</li>
                <li>Review quality metrics and classifications</li>
                <li>Create curated packages for marketplace or return to you</li>
              </ol>
            </div>
            <button onClick={handleComplete} className="btn btn-primary btn-block">
              Start Refinement Pipeline
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default IngestionPage;
