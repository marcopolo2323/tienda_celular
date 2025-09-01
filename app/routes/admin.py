from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.models import db, Usuario, Marca, Categoria
from app.utils.validators import validate_user_data
from functools import wraps

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
                direccion=data.get('direccion', ''),
                email=data.get('email', '')
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

@admin_bp.route('/empleados/<int:id>/editar', methods=['POST'])
@login_required
@admin_required
def editar_empleado(id):
    empleado = Usuario.query.get_or_404(id)
    
    try:
        data = request.form.to_dict()
        errors = validate_user_data(data, is_edit=True, user_id=id)
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('admin.empleados'))
        
        # Verificar username único (excluyendo el usuario actual)
        existing_user = Usuario.query.filter(
            Usuario.username == data['username'], 
            Usuario.id != id
        ).first()
        
        if existing_user:
            flash('El nombre de usuario ya existe', 'error')
            return redirect(url_for('admin.empleados'))
        
        empleado.username = data['username']
        empleado.nombre = data['nombre']
        empleado.rol = data['rol']
        empleado.telefono = data.get('telefono', '')
        empleado.direccion = data.get('direccion', '')
        empleado.email = data.get('email', '')
        
        # Actualizar contraseña solo si se proporciona
        if data.get('password'):
            empleado.password = generate_password_hash(data['password'])
        
        db.session.commit()
        flash('Empleado actualizado exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar empleado: {str(e)}', 'error')
    
    return redirect(url_for('admin.empleados'))

@admin_bp.route('/empleados/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_empleado(id):
    if id == current_user.id:
        flash('No puedes eliminarte a ti mismo', 'error')
        return redirect(url_for('admin.empleados'))
    
    empleado = Usuario.query.get_or_404(id)
    
    try:
        # Verificar si el empleado tiene ventas o servicios asociados
        if empleado.ventas or empleado.servicios_asignados:
            flash('No se puede eliminar un empleado con ventas o servicios asociados', 'error')
            return redirect(url_for('admin.empleados'))
        
        db.session.delete(empleado)
        db.session.commit()
        flash('Empleado eliminado exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar empleado: {str(e)}', 'error')
    
    return redirect(url_for('admin.empleados'))

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

@admin_bp.route('/marcas/<int:id>/editar', methods=['POST'])
@login_required
@admin_required
def editar_marca(id):
    marca = Marca.query.get_or_404(id)
    
    try:
        nombre = request.form['nombre'].strip()
        
        if not nombre:
            flash('El nombre de la marca es obligatorio', 'error')
            return redirect(url_for('admin.marcas'))
        
        # Verificar unicidad (excluyendo la marca actual)
        existing = Marca.query.filter(
            Marca.nombre == nombre, 
            Marca.id != id
        ).first()
        
        if existing:
            flash('Esta marca ya existe', 'error')
            return redirect(url_for('admin.marcas'))
        
        marca.nombre = nombre
        db.session.commit()
        flash('Marca actualizada exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar marca: {str(e)}', 'error')
    
    return redirect(url_for('admin.marcas'))

@admin_bp.route('/marcas/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_marca(id):
    marca = Marca.query.get_or_404(id)
    
    try:
        # Verificar si tiene productos asociados
        if marca.celulares or marca.accesorios:
            flash('No se puede eliminar una marca con productos asociados', 'error')
            return redirect(url_for('admin.marcas'))
        
        db.session.delete(marca)
        db.session.commit()
        flash('Marca eliminada exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar marca: {str(e)}', 'error')
    
    return redirect(url_for('admin.marcas'))

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

@admin_bp.route('/categorias/<int:id>/editar', methods=['POST'])
@login_required
@admin_required
def editar_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    
    try:
        nombre = request.form['nombre'].strip()
        descripcion = request.form.get('descripcion', '').strip()
        
        if not nombre:
            flash('El nombre de la categoría es obligatorio', 'error')
            return redirect(url_for('admin.categorias'))
        
        # Verificar unicidad
        existing = Categoria.query.filter(
            Categoria.nombre == nombre, 
            Categoria.id != id
        ).first()
        
        if existing:
            flash('Esta categoría ya existe', 'error')
            return redirect(url_for('admin.categorias'))
        
        categoria.nombre = nombre
        categoria.descripcion = descripcion
        db.session.commit()
        flash('Categoría actualizada exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar categoría: {str(e)}', 'error')
    
    return redirect(url_for('admin.categorias'))

@admin_bp.route('/categorias/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    
    try:
        # Verificar si tiene productos asociados
        if categoria.accesorios:
            flash('No se puede eliminar una categoría con productos asociados', 'error')
            return redirect(url_for('admin.categorias'))
        
        db.session.delete(categoria)
        db.session.commit()
        flash('Categoría eliminada exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar categoría: {str(e)}', 'error')
    
    return redirect(url_for('admin.categorias'))

@admin_bp.route('/reportes')
@login_required
@admin_required
def reportes():
    """Panel de reportes administrativos"""
    # Aquí puedes agregar lógica para generar reportes
    return render_template('reportes.html')

@admin_bp.route('/configuracion')
@login_required
@admin_required
def configuracion():
    """Configuraciones del sistema"""
    return render_template('configuracion.html')