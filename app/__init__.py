from flask import Flask, render_template
from flask_login import LoginManager, current_user
from app.models import db, Usuario
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Inicializar extensiones
    db.init_app(app)
    
    # Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Debes iniciar sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    
    # AGREGAR ESTA FUNCIÓN PARA LOS TEMPLATES
    @app.template_global()
    def has_permission(permission_name):
        """Verificar si el usuario actual tiene un permiso específico"""
        if not current_user.is_authenticated:
            return False
        
        # Lógica de permisos basada en el rol del usuario
        user_role = current_user.rol
        
        # Definir permisos por rol
        permissions = {
            'admin': [
                'manage_employees', 'manage_products', 'manage_sales', 
                'manage_services', 'view_reports', 'manage_users'
            ],
            'manager': [
                'manage_employees', 'manage_products', 'manage_sales', 
                'manage_services', 'view_reports'
            ],
            'employee': [
                'manage_products', 'manage_sales', 'manage_services'
            ],
            'viewer': [
                'view_reports'
            ]
        }
        
        # Verificar si el rol del usuario tiene el permiso solicitado
        user_permissions = permissions.get(user_role, [])
        return permission_name in user_permissions
    
    # Registrar Blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.productos import productos_bp
    from app.routes.ventas import ventas_bp
    from app.routes.servicios import servicios_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(productos_bp, url_prefix='/productos')
    app.register_blueprint(ventas_bp, url_prefix='/ventas')
    app.register_blueprint(servicios_bp, url_prefix='/servicios')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Registrar manejadores de errores
    register_error_handlers(app)
    
    # Crear tablas y datos iniciales
    with app.app_context():
        db.create_all()
        create_initial_data()
    
    return app

def register_error_handlers(app):
    """Registrar manejadores de errores personalizados"""
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

def create_initial_data():
    """Crear datos iniciales si no existen"""
    from werkzeug.security import generate_password_hash
    
    # Crear usuario admin si no existe
    admin = Usuario.query.filter_by(username='admin').first()
    if not admin:
        admin = Usuario(
            username='admin',
            password=generate_password_hash('admin123'),
            nombre='Administrador',
            rol='admin',
            telefono='',
            direccion=''
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Usuario admin creado: admin/admin123")