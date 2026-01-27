/**
 * Main App component - entry point for the Data Broker frontend.
 * Handles routing and global state management.
 */
import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import './styles/globals.css';
import { AuthState } from './types';

// Pages
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import SupplierDashboard from './pages/SupplierDashboard';
import BuyerDashboard from './pages/BuyerDashboard';
import IngestionPage from './pages/IngestionPage';
import RefinementMonitor from './pages/RefinementMonitor';
import PackageCreation from './pages/PackageCreation';
import MarketplaceBrowse from './pages/MarketplaceBrowse';

// Components
import Navbar from './components/Navbar';
import LoadingSpinner from './components/LoadingSpinner';

function App() {
  const [auth, setAuth] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
  });

  useEffect(() => {
    // Check if user is logged in (from localStorage or session)
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        setAuth({
          user: JSON.parse(storedUser),
          isAuthenticated: true,
          isLoading: false,
        });
      } catch {
        setAuth({ user: null, isAuthenticated: false, isLoading: false });
      }
    } else {
      setAuth({ user: null, isAuthenticated: false, isLoading: false });
    }
  }, []);

  const handleLogin = (user: any) => {
    localStorage.setItem('user', JSON.stringify(user));
    setAuth({
      user,
      isAuthenticated: true,
      isLoading: false,
    });
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    setAuth({
      user: null,
      isAuthenticated: false,
      isLoading: false,
    });
  };

  if (auth.isLoading) {
    return <LoadingSpinner />;
  }

  return (
    <BrowserRouter>
      <div className="app">
        <Navbar user={auth.user} onLogout={handleLogout} />
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<HomePage user={auth.user} />} />
          <Route
            path="/login"
            element={
              auth.isAuthenticated ? (
                <Navigate to="/dashboard" replace />
              ) : (
                <LoginPage onLogin={handleLogin} />
              )
            }
          />
          <Route
            path="/register"
            element={
              auth.isAuthenticated ? (
                <Navigate to="/dashboard" replace />
              ) : (
                <RegisterPage onRegister={handleLogin} />
              )
            }
          />

          {/* Protected routes */}
          {auth.isAuthenticated && auth.user ? (
            <>
              <Route
                path="/dashboard"
                element={
                  auth.user.is_supplier ? (
                    <SupplierDashboard user={auth.user} />
                  ) : (
                    <BuyerDashboard user={auth.user} />
                  )
                }
              />
              <Route path="/ingest" element={<IngestionPage user={auth.user} />} />
              <Route path="/refinement/:datasetId" element={<RefinementMonitor user={auth.user} />} />
              <Route path="/package/:datasetId" element={<PackageCreation user={auth.user} />} />
              <Route path="/marketplace" element={<MarketplaceBrowse user={auth.user} />} />
            </>
          ) : null}

          {/* Catch all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
