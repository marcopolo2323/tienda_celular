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
    
    # FUNCIÓN PARA LOS TEMPLATES - Mejorada
    @app.template_global()
    def has_permission(permission_name):
        """Verificar si el usuario actual tiene un permiso específico"""
        if not current_user.is_authenticated:
            return False
        
        # Lógica de permisos basada en el rol del usuario
        user_role = current_user.rol
        
        # Definir permisos por rol - ACTUALIZADO para coincidir con templates
        permissions = {
            'admin': [
                'manage_employees', 'manage_products', 'manage_sales', 
                'manage_services', 'view_reports', 'manage_users',
                'edit_products', 'view_products', 'delete_products'
            ],
            'manager': [
                'manage_employees', 'manage_products', 'manage_sales', 
                'manage_services', 'view_reports', 'edit_products', 'view_products'
            ],
            'employee': [
                'manage_products', 'manage_sales', 'manage_services',
                'edit_products', 'view_products'
            ],
            'viewer': [
                'view_reports', 'view_products'
            ]
        }
        
        # Verificar si el rol del usuario tiene el permiso solicitado
        user_permissions = permissions.get(user_role, [])
        return permission_name in user_permissions
    
    # AGREGAR función auxiliar para debugging
    @app.template_global()
    def debug_user_role():
        """Para debugging - mostrar rol actual del usuario"""
        if current_user.is_authenticated:
            return current_user.rol
        return 'not_authenticated'
    
    # Registrar Blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.productos import productos_bp
    from app.routes.ventas import ventas_bp
    from app.routes.servicios import servicios_bp
    from app.routes.admin import admin_bp
    from app.routes.clientes import clientes_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(productos_bp, url_prefix='/productos')
    app.register_blueprint(ventas_bp, url_prefix='/ventas')
    app.register_blueprint(servicios_bp, url_prefix='/servicios')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(clientes_bp, url_prefix='/clientes')
    
    # Registrar manejadores de errores
    register_error_handlers(app)
    
    # Crear tablas y datos iniciales
    with app.app_context():
        # Imprimir la ruta de la base de datos para depuración
        import os
        print(f"Usando base de datos: {app.config['SQLALCHEMY_DATABASE_URI']}")
        # Solo crear directorio si no es una base de datos en memoria
        if ':memory:' not in app.config['SQLALCHEMY_DATABASE_URI']:
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            db_dir = os.path.dirname(db_path)
            if db_dir:  # Solo si hay un directorio para crear
                print(f"Directorio de la base de datos: {db_dir}")
                if not os.path.exists(db_dir):
                    print(f"Creando directorio: {db_dir}")
                    os.makedirs(db_dir, exist_ok=True)
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
        
        # AGREGAR: Crear un manager y empleado de prueba
        manager = Usuario(
            username='manager',
            password=generate_password_hash('manager123'),
            nombre='Manager de Prueba',
            rol='manager',
            telefono='123456789',
            direccion='Dirección del Manager'
        )
        db.session.add(manager)
        
        employee = Usuario(
            username='employee',
            password=generate_password_hash('employee123'),
            nombre='Empleado de Prueba',
            rol='employee',
            telefono='987654321',
            direccion='Dirección del Empleado'
        )
        db.session.add(employee)
        
        db.session.commit()
        print("✅ Usuarios creados:")
        print("   - Admin: admin/admin123")
        print("   - Manager: manager/manager123") 
        print("   - Employee: employee/employee123")