from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.models import db, Usuario, Marca, Categoria
from app.utils.validators import validate_user_data
from functools import wraps
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorador para requerir permisos de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != 'admin':
            flash('No tienes permisos para acceder a esta sección', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def has_permission(permission):
    """Función helper para verificar permisos"""
    if not current_user.is_authenticated:
        return False
    
    permissions = {
        'manage_employees': ['admin'],
        'manage_products': ['admin', 'manager'],
        'view_reports': ['admin', 'manager'],
        'edit_products': ['admin', 'manager', 'employee'],
        'view_products': ['admin', 'manager', 'employee']
    }
    
    return current_user.rol in permissions.get(permission, [])

# Hacer disponible la función en templates
@admin_bp.context_processor
def inject_permissions():
    return dict(has_permission=has_permission)

@admin_bp.route('/empleados', methods=['GET', 'POST'])
@login_required
@admin_required
def empleados():
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            errors = validate_user_data(data)
            
            if errors:
                for error in errors:
                    flash(error, 'error')
                return redirect(url_for('admin.empleados'))
            
            # Verificar que el username no exista
            existing_user = Usuario.query.filter_by(username=data['username']).first()
            if existing_user:
                flash('El nombre de usuario ya existe', 'error')
                return redirect(url_for('admin.empleados'))
            
            hashed_password = generate_password_hash(data['password'])
            empleado = Usuario(
                username=data['username'],
                password=hashed_password,
                nombre=data['nombre'],
                rol=data['rol'],
                telefono=data.get('telefono', ''),
                direccion=data.get('direccion', '')
            )
            
            db.session.add(empleado)
            db.session.commit()
            flash('Empleado agregado exitosamente', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar empleado: {str(e)}', 'error')
        
        return redirect(url_for('admin.empleados'))
    
    empleados = Usuario.query.order_by(Usuario.nombre).all()
    return render_template('empleados.html', empleados=empleados)

@admin_bp.route('/empleado/<int:id>', methods=['GET'])
@login_required
def get_empleado(id):
    """Obtener datos de un empleado para mostrar detalles o editar"""
    try:
        empleado = Usuario.query.get_or_404(id)
        
        # Verificar que fecha_contratacion existe y es válida
        fecha_contratacion = empleado.fecha_contratacion
        if fecha_contratacion is None:
            # Si no existe fecha_contratacion, usar la fecha actual o una fecha por defecto
            fecha_contratacion = datetime.now()
        
        return jsonify({
            'id': empleado.id,
            'nombre': empleado.nombre or '',
            'username': empleado.username or '',
            'rol': empleado.rol or '',
            'telefono': empleado.telefono or '',
            'direccion': empleado.direccion or '',
            'fecha_contratacion': fecha_contratacion.isoformat()
        })
    
    except AttributeError as e:
        # Error específico por atributo faltante
        return jsonify({'error': f'Atributo faltante en el modelo Usuario: {str(e)}'}), 500
    
    except Exception as e:
        # Error general
        return jsonify({'error': f'Error al obtener empleado: {str(e)}'}), 500

@admin_bp.route('/empleado/<int:id>', methods=['PUT'])
@login_required
@admin_required
def update_empleado(id):
    """Actualizar datos de un empleado"""
    try:
        empleado = Usuario.query.get_or_404(id)
        data = request.json
        
        # Verificar username único (excluyendo el usuario actual)
        if data.get('username') and data.get('username') != empleado.username:
            existing_user = Usuario.query.filter(
                Usuario.username == data['username'], 
                Usuario.id != id
            ).first()
            
            if existing_user:
                return jsonify({'error': 'El nombre de usuario ya existe'}), 400
        
        # Actualizar campos de forma segura
        if data.get('username'):
            empleado.username = data['username']
        if data.get('nombre'):
            empleado.nombre = data['nombre']
        if data.get('rol'):
            empleado.rol = data['rol']
        if 'telefono' in data:
            empleado.telefono = data['telefono']
        if 'direccion' in data:
            empleado.direccion = data['direccion']
        
        # Actualizar contraseña solo si se proporciona
        if data.get('password') and data['password'].strip():
            empleado.password = generate_password_hash(data['password'])
        
        # Actualizar fecha de contratación si se proporciona
        if data.get('fecha_contratacion'):
            try:
                fecha_str = data['fecha_contratacion']
                if 'T' in fecha_str:
                    fecha_str = fecha_str.split('T')[0]  # Tomar solo la parte de la fecha
                empleado.fecha_contratacion = datetime.strptime(fecha_str, '%Y-%m-%d')
            except (ValueError, AttributeError) as e:
                return jsonify({'error': f'Formato de fecha inválido: {str(e)}'}), 400
        
        db.session.commit()
        return jsonify({'message': 'Empleado actualizado exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar empleado: {str(e)}'}), 500

@admin_bp.route('/empleado/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_empleado(id):
    """Eliminar un empleado"""
    try:
        if id == current_user.id:
            return jsonify({'error': 'No puedes eliminarte a ti mismo'}), 400
        
        empleado = Usuario.query.get_or_404(id)
        
        # Verificar si el empleado tiene relaciones asociadas
        # Nota: Ajustar según el modelo real de tu base de datos
        try:
            # Verificar ventas asociadas (si existe la relación)
            if hasattr(empleado, 'ventas') and empleado.ventas:
                return jsonify({'error': 'No se puede eliminar un empleado con ventas asociadas'}), 400
            
            # Verificar servicios asociados (si existe la relación)
            if hasattr(empleado, 'servicios_asignados') and empleado.servicios_asignados:
                return jsonify({'error': 'No se puede eliminar un empleado con servicios asociados'}), 400
        except AttributeError:
            # Si las relaciones no existen, continuar con la eliminación
            pass
        
        db.session.delete(empleado)
        db.session.commit()
        return jsonify({'message': 'Empleado eliminado exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al eliminar empleado: {str(e)}'}), 500

@admin_bp.route('/marcas', methods=['GET', 'POST'])
@login_required
@admin_required
def marcas():
    if request.method == 'POST':
        try:
            nombre = request.form['nombre'].strip()
            
            if not nombre:
                flash('El nombre de la marca es obligatorio', 'error')
                return redirect(url_for('admin.marcas'))
            
            # Verificar que no exista
            existing = Marca.query.filter_by(nombre=nombre).first()
            if existing:
                flash('Esta marca ya existe', 'error')
                return redirect(url_for('admin.marcas'))
            
            marca = Marca(nombre=nombre)
            db.session.add(marca)
            db.session.commit()
            flash('Marca agregada exitosamente', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar marca: {str(e)}', 'error')
        
        return redirect(url_for('admin.marcas'))
    
    marcas = Marca.query.order_by(Marca.nombre).all()
    return render_template('marcas.html', marcas=marcas)

@admin_bp.route('/marca/<int:id>', methods=['GET'])
@login_required
def obtener_marca(id):
    try:
        marca = Marca.query.get_or_404(id)
        return jsonify({
            'id': marca.id,
            'nombre': marca.nombre,
            'celulares': [{
                'modelo': celular.modelo,
                'stock': celular.stock
            } for celular in marca.celulares] if hasattr(marca, 'celulares') else [],
            'accesorios': [{
                'nombre': accesorio.nombre,
                'stock': accesorio.stock
            } for accesorio in marca.accesorios] if hasattr(marca, 'accesorios') else []
        })
    except Exception as e:
        return jsonify({'error': f'Error al obtener marca: {str(e)}'}), 500

@admin_bp.route('/marca/<int:id>', methods=['PUT'])
@login_required
@admin_required
def actualizar_marca_api(id):
    try:
        marca = Marca.query.get_or_404(id)
        data = request.get_json()
        
        if not data.get('nombre'):
            return jsonify({'error': 'El nombre de la marca es obligatorio'}), 400
        
        # Verificar unicidad
        existing = Marca.query.filter(
            Marca.nombre == data['nombre'], 
            Marca.id != id
        ).first()
        
        if existing:
            return jsonify({'error': 'Esta marca ya existe'}), 400
        
        marca.nombre = data['nombre']
        db.session.commit()
        return jsonify({'message': 'Marca actualizada exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/marca/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def eliminar_marca_api(id):
    try:
        marca = Marca.query.get_or_404(id)
        
        # Verificar si tiene productos asociados
        has_celulares = hasattr(marca, 'celulares') and marca.celulares
        has_accesorios = hasattr(marca, 'accesorios') and marca.accesorios
        
        if has_celulares or has_accesorios:
            return jsonify({'error': 'No se puede eliminar una marca con productos asociados'}), 400
        
        db.session.delete(marca)
        db.session.commit()
        return jsonify({'message': 'Marca eliminada exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/categorias', methods=['GET', 'POST'])
@login_required
@admin_required
def categorias():
    if request.method == 'POST':
        try:
            nombre = request.form['nombre'].strip()
            descripcion = request.form.get('descripcion', '').strip()
            
            if not nombre:
                flash('El nombre de la categoría es obligatorio', 'error')
                return redirect(url_for('admin.categorias'))
            
            # Verificar que no exista
            existing = Categoria.query.filter_by(nombre=nombre).first()
            if existing:
                flash('Esta categoría ya existe', 'error')
                return redirect(url_for('admin.categorias'))
            
            categoria = Categoria(
                nombre=nombre,
                descripcion=descripcion
            )
            db.session.add(categoria)
            db.session.commit()
            flash('Categoría agregada exitosamente', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar categoría: {str(e)}', 'error')
        
        return redirect(url_for('admin.categorias'))
    
    categorias = Categoria.query.order_by(Categoria.nombre).all()
    return render_template('categorias.html', categorias=categorias)

@admin_bp.route('/categoria/<int:id>', methods=['GET'])
@login_required
def obtener_categoria(id):
    try:
        categoria = Categoria.query.get_or_404(id)
        return jsonify({
            'id': categoria.id,
            'nombre': categoria.nombre,
            'descripcion': categoria.descripcion,
            'accesorios': [{
                'id': accesorio.id,
                'nombre': accesorio.nombre,
                'marca': accesorio.marca.nombre,
                'stock': accesorio.stock,
                'precio': float(accesorio.precio)
            } for accesorio in categoria.accesorios] if hasattr(categoria, 'accesorios') else []
        })
    except Exception as e:
        return jsonify({'error': f'Error al obtener categoría: {str(e)}'}), 500

@admin_bp.route('/categoria/<int:id>', methods=['PUT'])
@login_required
@admin_required
def actualizar_categoria_api(id):
    try:
        categoria = Categoria.query.get_or_404(id)
        data = request.get_json()
        
        if not data.get('nombre'):
            return jsonify({'error': 'El nombre de la categoría es obligatorio'}), 400
        
        # Verificar unicidad
        existing = Categoria.query.filter(
            Categoria.nombre == data['nombre'], 
            Categoria.id != id
        ).first()
        
        if existing:
            return jsonify({'error': 'Esta categoría ya existe'}), 400
        
        categoria.nombre = data['nombre']
        categoria.descripcion = data.get('descripcion', '')
        db.session.commit()
        return jsonify({'message': 'Categoría actualizada exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/categoria/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def eliminar_categoria_api(id):
    try:
        categoria = Categoria.query.get_or_404(id)
        
        # Verificar si tiene productos asociados
        if hasattr(categoria, 'accesorios') and categoria.accesorios:
            return jsonify({'error': 'No se puede eliminar una categoría con productos asociados'}), 400
        
        db.session.delete(categoria)
        db.session.commit()
        return jsonify({'message': 'Categoría eliminada exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/reportes')
@login_required
@admin_required
def reportes():
    """Panel de reportes administrativos"""
    return render_template('reportes.html')

@admin_bp.route('/configuracion')
@login_required
@admin_required
def configuracion():
    """Configuraciones del sistema"""
    return render_template('configuracion.html')