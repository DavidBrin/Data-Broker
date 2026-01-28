/**
 * Navbar component - persistent navigation header.
 * Shows branding and user account info.
 */
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { LogOut, Home, BarChart3, ShoppingCart } from 'lucide-react';
import { User } from '../types';
import './Navbar.css';

interface NavbarProps {
  user: User | null;
  onLogout: () => void;
}

const Navbar: React.FC<NavbarProps> = ({ user, onLogout }) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    onLogout();
    navigate('/');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <span className="brand-icon">📊</span>
          <span className="brand-name">DataBroker</span>
        </Link>

        <div className="navbar-menu">
          <Link to="/" className="nav-link">
            <Home size={18} />
            Home
          </Link>
          <Link to="/marketplace" className="nav-link">
            <ShoppingCart size={18} />
            Marketplace
          </Link>
          {user && (
            <Link to="/dashboard" className="nav-link">
              <BarChart3 size={18} />
              Dashboard
            </Link>
          )}
        </div>

        <div className="navbar-right">
          {user ? (
            <div className="user-menu">
              <span className="user-name">{user.username}</span>
              <div className="role-badge">{user.role}</div>
              <button onClick={handleLogout} className="logout-btn" title="Logout">
                <LogOut size={18} />
              </button>
            </div>
          ) : (
            <div className="auth-links">
              <Link to="/login" className="nav-link">
                Login
              </Link>
              <Link to="/register" className="nav-link highlight">
                Sign Up
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
