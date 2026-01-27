/**
 * Reusable card component for displaying data.
 */
import React from 'react';
import './Card.css';

interface CardProps {
  title?: string;
  description?: string;
  children?: React.ReactNode;
  footer?: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

const Card: React.FC<CardProps> = ({ title, description, children, footer, className = '', onClick }) => {
  return (
    <div className={`card ${className}`} onClick={onClick}>
      {title && <h3 className="card-title">{title}</h3>}
      {description && <p className="card-description">{description}</p>}
      {children && <div className="card-content">{children}</div>}
      {footer && <div className="card-footer">{footer}</div>}
    </div>
  );
};

export default Card;
