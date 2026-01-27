"""
Routes package.
Exports all route blueprints for easy importing in main app.
"""
from . import auth_routes, dataset_routes, refinement_routes, package_routes, marketplace_routes

__all__ = [
    'auth_routes',
    'dataset_routes',
    'refinement_routes',
    'package_routes',
    'marketplace_routes',
]
