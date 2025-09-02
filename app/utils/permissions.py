# app/utils/permissions.py
from flask_login import current_user
from functools import wraps
from flask import flash, redirect, url_for, jsonify, request

def has_permission(permission):
    """Función helper para verificar permisos"""
    if not current_user.is_authenticated:
        return False
    
    permissions = {
        'manage_employees': ['admin'],
        'manage_products': ['admin', 'manager'],
        'view_reports': ['admin', 'manager'],
        'edit_products': ['admin', 'manager', 'employee'],
        'view_products': ['admin', 'manager', 'employee'],
        'delete_products': ['admin'],
        'manage_sales': ['admin', 'manager', 'employee'],
        'view_sales': ['admin', 'manager', 'employee']
    }
    
    return current_user.rol in permissions.get(permission, [])

def admin_required(f):
    """Decorador para requerir permisos de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != 'admin':
            if request.is_json:
                return jsonify({'error': 'No tienes permisos para acceder a esta sección'}), 403
            flash('No tienes permisos para acceder a esta sección', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    """Decorador para requerir permisos de manager o superior"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol not in ['admin', 'manager']:
            if request.is_json:
                return jsonify({'error': 'No tienes permisos para realizar esta acción'}), 403
            flash('No tienes permisos para realizar esta acción', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def employee_required(f):
    """Decorador para requerir permisos de empleado o superior"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol not in ['admin', 'manager', 'employee']:
            if request.is_json:
                return jsonify({'error': 'No tienes permisos para realizar esta acción'}), 403
            flash('No tienes permisos para realizar esta acción', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def permission_required(permission):
    """Decorador para verificar un permiso específico"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not has_permission(permission):
                if request.is_json:
                    return jsonify({'error': f'No tienes permisos para: {permission}'}), 403
                flash(f'No tienes permisos para realizar esta acción', 'error')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator