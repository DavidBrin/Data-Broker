/**
 * Main layout component for the application.
 * Provides consistent header, navigation, and layout structure.
 */
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { LogOut, Menu, Home, BarChart3, ShoppingCart } from 'lucide-react';
import { User } from '../types';
import './Layout.css';

interface LayoutProps {
  user: User | null;
  onLogout: () => void;
}

export const Layout: React.FC<{ children: React.ReactNode } & LayoutProps> = ({
  user,
  onLogout,
  children,
}) => {
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  const handleLogout = () => {
    onLogout();
    navigate('/');
  };

  return (
    <div className="layout">
      <header className="header">
        <div className="container flex justify-between items-center">
          <Link to="/" className="logo">
            <span className="logo-icon">📊</span>
            <span className="logo-text">DataBroker</span>
          </Link>

          <nav className="nav">
            <Link to="/">Home</Link>
            <Link to="/marketplace">Marketplace</Link>
            {user && (
              <>
                <Link to="/dashboard">Dashboard</Link>
                {user.is_supplier && <Link to="/ingest">New Dataset</Link>}
              </>
            )}
          </nav>

          <div className="auth-section">
            {user ? (
              <>
                <span className="user-info">{user.username}</span>
                <button onClick={handleLogout} className="btn btn-outline">
                  <LogOut size={16} />
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="btn btn-outline">
                  Login
                </Link>
                <Link to="/register" className="btn btn-primary">
                  Sign Up
                </Link>
              </>
            )}
          </div>

          <button
            className="mobile-menu-toggle"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            <Menu size={24} />
          </button>
        </div>

        {mobileMenuOpen && (
          <div className="mobile-menu">
            <Link to="/">Home</Link>
            <Link to="/marketplace">Marketplace</Link>
            {user && <Link to="/dashboard">Dashboard</Link>}
            {user && user.is_supplier && <Link to="/ingest">New Dataset</Link>}
          </div>
        )}
      </header>

      <main className="main-content">
        <div className="container">{children}</div>
      </main>

      <footer className="footer">
        <div className="container">
          <p>&copy; 2024 DataBroker. All rights reserved.</p>
          <p>End-to-end data refinement for AI training</p>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
