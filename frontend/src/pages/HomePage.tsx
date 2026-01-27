/**
 * HomePage - Landing page for the Data Broker platform.
 * Shows overview, features, and calls-to-action for suppliers and buyers.
 */
import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, TrendingUp, Shield, Zap, BarChart3 } from 'lucide-react';
import { User } from '../types';
import './HomePage.css';
import Card from '../components/Card';

interface HomePageProps {
  user: User | null;
}

const HomePage: React.FC<HomePageProps> = ({ user }) => {
  return (
    <div className="homepage">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <h1>Turn Raw Data into AI Training Assets</h1>
          <p>
            The end-to-end data refinement platform. Ingest messy data, refine it with AI,
            and sell or return high-quality training datasets.
          </p>
          <div className="hero-cta">
            {!user ? (
              <>
                <Link to="/register" className="btn btn-primary">
                  Get Started
                  <ArrowRight size={18} />
                </Link>
                <Link to="/login" className="btn btn-outline">
                  Sign In
                </Link>
              </>
            ) : (
              <Link to="/dashboard" className="btn btn-primary">
                Go to Dashboard
                <ArrowRight size={18} />
              </Link>
            )}
          </div>
        </div>
      </section>

      {/* Pipeline Overview */}
      <section className="pipeline-overview">
        <h2>The Data Refinement Pipeline</h2>
        <div className="pipeline-stages">
          <div className="stage">
            <div className="stage-icon">📥</div>
            <h3>Ingest</h3>
            <p>Upload data from any source: files, APIs, cloud buckets</p>
          </div>
          <div className="arrow">→</div>
          <div className="stage">
            <div className="stage-icon">🔍</div>
            <h3>Refine</h3>
            <p>Quality scoring, deduplication, classification with AI</p>
          </div>
          <div className="arrow">→</div>
          <div className="stage">
            <div className="stage-icon">📦</div>
            <h3>Package</h3>
            <p>Create curated datasets with manifests and metadata</p>
          </div>
          <div className="arrow">→</div>
          <div className="stage">
            <div className="stage-icon">💰</div>
            <h3>Sell</h3>
            <p>List on marketplace or return to supplier</p>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="features">
        <h2>Why DataBroker?</h2>
        <div className="features-grid">
          <Card>
            <div className="feature">
              <Shield size={32} className="feature-icon" />
              <h3>Data Privacy & Legal</h3>
              <p>Comprehensive legal attestations and licensing for every dataset</p>
            </div>
          </Card>
          <Card>
            <div className="feature">
              <Zap size={32} className="feature-icon" />
              <h3>AI-Powered Quality Scoring</h3>
              <p>Advanced ML models evaluate quality, detect duplicates, classify data</p>
            </div>
          </Card>
          <Card>
            <div className="feature">
              <TrendingUp size={32} className="feature-icon" />
              <h3>Transparent Pricing</h3>
              <p>Market-driven pricing with detailed quality metrics for every package</p>
            </div>
          </Card>
          <Card>
            <div className="feature">
              <BarChart3 size={32} className="feature-icon" />
              <h3>Complete Analytics</h3>
              <p>Track your dataset through every stage of the pipeline with detailed metrics</p>
            </div>
          </Card>
        </div>
      </section>

      {/* Supplier Section */}
      <section className="role-section suppliers">
        <div className="role-content">
          <h2>For Data Suppliers</h2>
          <p>
            Have massive amounts of raw data? Universities, enterprises, or crowd contributors
            can submit datasets and earn from high-quality refined outputs.
          </p>
          <ul className="benefits-list">
            <li>✓ Upload data from any source</li>
            <li>✓ Free quality refinement with our AI pipeline</li>
            <li>✓ Return cleaned data or broker sales on marketplace</li>
            <li>✓ Transparent provenance tracking</li>
            <li>✓ License your data with full legal protection</li>
          </ul>
          {!user && (
            <Link to="/register" className="btn btn-secondary">
              Join as Data Supplier
              <ArrowRight size={18} />
            </Link>
          )}
        </div>
      </section>

      {/* Buyer Section */}
      <section className="role-section buyers">
        <div className="role-content">
          <h2>For Data Buyers</h2>
          <p>
            Need high-quality training data for AI models? Browse our marketplace of curated,
            scored datasets ready for immediate use.
          </p>
          <ul className="benefits-list">
            <li>✓ Browse thousands of curated datasets</li>
            <li>✓ Detailed quality metrics and provenance</li>
            <li>✓ Multiple data modalities (text, audio, video, images)</li>
            <li>✓ Flexible licensing terms</li>
            <li>✓ Instant access with download tokens</li>
          </ul>
          {!user && (
            <Link to="/register" className="btn btn-primary">
              Browse Marketplace
              <ArrowRight size={18} />
            </Link>
          )}
        </div>
      </section>

      {/* Stats Section */}
      <section className="stats">
        <div className="stat">
          <h3>10M+</h3>
          <p>Data items refined</p>
        </div>
        <div className="stat">
          <h3>500+</h3>
          <p>Datasets published</p>
        </div>
        <div className="stat">
          <h3>$10M+</h3>
          <p>Value transacted</p>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
