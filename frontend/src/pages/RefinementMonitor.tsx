/**
 * RefinementMonitor - View and manage the refinement pipeline for a dataset.
 */
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { User } from '../types';
import apiService from '../services/api';
import Card from '../components/Card';
import LoadingSpinner from '../components/LoadingSpinner';
import './RefinementMonitor.css';

interface RefinementMonitorProps {
  user: User;
}

const RefinementMonitor: React.FC<RefinementMonitorProps> = ({ user }) => {
  const { datasetId } = useParams<{ datasetId: string }>();
  const [dataset, setDataset] = useState<any>(null);
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refining, setRefining] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!datasetId) return;

    const fetchData = async () => {
      try {
        const [dsData, metricsData] = await Promise.all([
          apiService.getDataset(datasetId),
          apiService.getRefinementMetrics(datasetId),
        ]);
        setDataset(dsData);
        setMetrics(metricsData);
      } catch (err: any) {
        setError('Failed to load dataset');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [datasetId]);

  const handleRefine = async () => {
    if (!datasetId) return;
    setRefining(true);
    setError('');

    try {
      const result = await apiService.refineDataset(datasetId);
      setMetrics(result);
    } catch (err: any) {
      setError('Refinement failed');
    } finally {
      setRefining(false);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="refinement-monitor">
      <h1>Refinement Pipeline: {dataset?.name}</h1>

      {error && <div className="error-message">{error}</div>}

      {/* Dataset Info */}
      <Card title="Dataset Information">
        <div className="dataset-info">
          <div className="info-row">
            <span>Status:</span>
            <strong>{dataset?.stage}</strong>
          </div>
          <div className="info-row">
            <span>Files:</span>
            <strong>{dataset?.file_count}</strong>
          </div>
          <div className="info-row">
            <span>Size:</span>
            <strong>{(dataset?.total_size_bytes / 1024 / 1024).toFixed(2)}MB</strong>
          </div>
        </div>
      </Card>

      {/* Refinement Controls */}
      <Card title="Refinement Pipeline">
        {!metrics || !metrics.overall_quality ? (
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <p>Run the refinement pipeline to analyze your data quality.</p>
            <button
              onClick={handleRefine}
              className="btn btn-primary"
              disabled={refining}
              style={{ marginTop: '1rem' }}
            >
              {refining ? 'Processing...' : 'Run Refinement Pipeline'}
            </button>
          </div>
        ) : (
          <div className="metrics-display">
            <div className="quality-score">
              <h3>Overall Quality Score</h3>
              <div className="score">{(metrics.overall_quality * 100).toFixed(1)}%</div>
            </div>

            {metrics.quality_scores && (
              <div className="quality-breakdown">
                <h4>Quality Breakdown</h4>
                {Object.entries(metrics.quality_scores).map(([key, value]: any) => (
                  <div key={key} className="quality-metric">
                    <span>{key}</span>
                    <div className="metric-bar">
                      <div
                        className="metric-fill"
                        style={{ width: `${value * 100}%` }}
                      ></div>
                    </div>
                    <span>{(value * 100).toFixed(0)}%</span>
                  </div>
                ))}
              </div>
            )}

            <div className="processing-stats">
              <div className="stat">
                <span>Items Processed</span>
                <strong>{metrics.items_processed}</strong>
              </div>
              <div className="stat">
                <span>Items Passed</span>
                <strong>{metrics.items_passed}</strong>
              </div>
              <div className="stat">
                <span>Items Rejected</span>
                <strong>{metrics.items_rejected}</strong>
              </div>
              <div className="stat">
                <span>Duplicates Found</span>
                <strong>{metrics.duplicates_found}</strong>
              </div>
            </div>

            {metrics.classifications && (
              <div className="classifications">
                <h4>Detected Classifications</h4>
                <div className="classification-grid">
                  {Object.entries(metrics.classifications).map(([category, data]: any) => (
                    <div key={category} className="classification-item">
                      <h5>{category}</h5>
                      {typeof data === 'object' && (
                        <ul>
                          {Object.entries(data).map(([key, val]: any) => (
                            <li key={key}>
                              {key}: {typeof val === 'number' ? val.toFixed(2) : val}
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {datasetId && (
              <Link
                to={`/package/${datasetId}`}
                className="btn btn-secondary"
                style={{ marginTop: '1.5rem' }}
              >
                Create Package
              </Link>
            )}
          </div>
        )}
      </Card>
    </div>
  );
};

export default RefinementMonitor;
