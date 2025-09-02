from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import db, Celular, Accesorio, Marca, Categoria, ServicioTV
from app.utils.validators import validate_product_data
from functools import wraps

productos_bp = Blueprint('productos', __name__)

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
@productos_bp.context_processor
def inject_permissions():
    return dict(has_permission=has_permission)

def manage_products_required(f):
    """Decorador para requerir permisos de gestión de productos"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not has_permission('manage_products'):
            if request.is_json:
                return jsonify({'error': 'No tienes permisos para realizar esta acción'}), 403
            flash('No tienes permisos para realizar esta acción', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@productos_bp.route('/celulares', methods=['GET', 'POST'])
@login_required
def celulares():
    if request.method == 'POST':
        # Verificar permisos para agregar
        if not has_permission('manage_products'):
            flash('No tienes permisos para agregar productos', 'error')
            return redirect(url_for('productos.celulares'))
        
        try:
            # Validar datos
            data = request.form.to_dict()
            errors = validate_product_data(data, 'celular')
            
            if errors:
                for error in errors:
                    flash(error, 'error')
                return redirect(url_for('productos.celulares'))
            
            celular = Celular(
                modelo=data['modelo'],
                marca_id=int(data['marca_id']),
                precio=float(data['precio']),
                stock=int(data['stock']),
                descripcion=data['descripcion'],
                especificaciones={
                    'ram': data['ram'],
                    'almacenamiento': data['almacenamiento'],
                    'color': data['color'],
                    'pantalla': data['pantalla']
                },
                estado=data['estado'],
                imei=data['imei']
            )
            
            db.session.add(celular)
            db.session.commit()
            flash('Celular agregado exitosamente', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar celular: {str(e)}', 'error')
        
        return redirect(url_for('productos.celulares'))
    
    celulares = Celular.query.join(Marca).order_by(Marca.nombre, Celular.modelo).all()
    marcas = Marca.query.order_by(Marca.nombre).all()
    
    return render_template('celulares.html',
                         celulares=celulares,
                         marcas=marcas)

@productos_bp.route('/accesorios', methods=['GET', 'POST'])
@login_required
def accesorios():
    if request.method == 'POST':
        # Verificar permisos para agregar
        if not has_permission('manage_products'):
            flash('No tienes permisos para agregar productos', 'error')
            return redirect(url_for('productos.accesorios'))
        
        try:
            data = request.form.to_dict()
            errors = validate_product_data(data, 'accesorio')
            
            if errors:
                for error in errors:
                    flash(error, 'error')
                return redirect(url_for('productos.accesorios'))
            
            accesorio = Accesorio(
                nombre=data['nombre'],
                marca_id=int(data['marca_id']),
                categoria_id=int(data['categoria_id']),
                precio=float(data['precio']),
                stock=int(data['stock']),
                descripcion=data['descripcion'],
                codigo_producto=data['codigo_producto']
            )
            
            db.session.add(accesorio)
            db.session.commit()
            flash('Accesorio agregado exitosamente', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar accesorio: {str(e)}', 'error')
        
        return redirect(url_for('productos.accesorios'))
    
    accesorios = Accesorio.query.join(Marca).join(Categoria).order_by(Categoria.nombre, Accesorio.nombre).all()
    marcas = Marca.query.order_by(Marca.nombre).all()
    categorias = Categoria.query.order_by(Categoria.nombre).all()
    
    return render_template('accesorios.html', 
                         accesorios=accesorios, 
                         marcas=marcas,
                         categorias=categorias)

@productos_bp.route('/servicios-tv', methods=['GET', 'POST'])
@login_required
def servicios_tv():
    if request.method == 'POST':
        # Verificar permisos para agregar
        if not has_permission('manage_products'):
            flash('No tienes permisos para agregar productos', 'error')
            return redirect(url_for('productos.servicios_tv'))
        
        try:
            data = request.form.to_dict()
            
            servicio = ServicioTV(
                nombre=data['nombre'],
                proveedor=data['proveedor'],
                descripcion=data['descripcion'],
                precio_mensual=float(data['precio_mensual']),
                canales=int(data['canales']),
                caracteristicas={
                    'hd': 'hd' in request.form,
                    'internet': 'internet' in request.form,
                    'deportes': 'deportes' in request.form,
                    'peliculas': 'peliculas' in request.form
                }
            )
            
            db.session.add(servicio)
            db.session.commit()
            flash('Plan de TV agregado exitosamente', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar plan de TV: {str(e)}', 'error')
        
        return redirect(url_for('productos.servicios_tv'))
    
    servicios = ServicioTV.query.order_by(ServicioTV.nombre).all()
    return render_template('servicios_tv.html', servicios=servicios)

# API Endpoints para Celulares
@productos_bp.route('/celular/<int:id>', methods=['GET'])
@login_required
def obtener_celular(id):
    """Obtener datos de un celular para mostrar detalles o editar"""
    celular = Celular.query.get_or_404(id)
    return jsonify({
        'id': celular.id,
        'marca': celular.marca.nombre,
        'marca_id': celular.marca_id,
        'modelo': celular.modelo,
        'precio': float(celular.precio),
        'stock': celular.stock,
        'estado': celular.estado,
        'imei': celular.imei,
        'descripcion': celular.descripcion,
        'especificaciones': celular.especificaciones
    })

@productos_bp.route('/celular/<int:id>', methods=['PUT'])
@login_required
def actualizar_celular(id):
    """Actualizar datos de un celular"""
    # Verificar permisos
    if not has_permission('edit_products'):
        return jsonify({'error': 'No tienes permisos para editar productos'}), 403
    
    celular = Celular.query.get_or_404(id)
    try:
        data = request.get_json()
        celular.modelo = data['modelo']
        celular.marca_id = data['marca_id']
        celular.precio = float(data['precio'])
        celular.stock = int(data['stock'])
        celular.estado = data['estado']
        celular.imei = data['imei']
        celular.descripcion = data['descripcion']
        celular.especificaciones = data['especificaciones']
        
        db.session.commit()
        return jsonify({'message': 'Celular actualizado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@productos_bp.route('/celular/<int:id>', methods=['DELETE'])
@login_required
def eliminar_celular_ajax(id):
    """Eliminar un celular"""
    # Solo administradores pueden eliminar
    if current_user.rol != 'admin':
        return jsonify({'error': 'Solo los administradores pueden eliminar productos'}), 403
    
    celular = Celular.query.get_or_404(id)
    try:
        # Verificar si tiene ventas asociadas
        # if celular.ventas_detalle:  # Si tienes esta relación
        #     return jsonify({'error': 'No se puede eliminar un producto con ventas asociadas'}), 400
        
        db.session.delete(celular)
        db.session.commit()
        return jsonify({'message': 'Celular eliminado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API Endpoints para Accesorios
@productos_bp.route('/accesorio/<int:id>', methods=['GET'])
@login_required
def obtener_accesorio(id):
    """Obtener datos de un accesorio para mostrar detalles o editar"""
    accesorio = Accesorio.query.get_or_404(id)
    return jsonify({
        'id': accesorio.id,
        'nombre': accesorio.nombre,
        'marca_id': accesorio.marca_id,
        'marca': accesorio.marca.nombre,
        'categoria_id': accesorio.categoria_id,
        'categoria': accesorio.categoria.nombre,
        'precio': float(accesorio.precio),
        'stock': accesorio.stock,
        'descripcion': accesorio.descripcion,
        'codigo_producto': accesorio.codigo_producto
    })

@productos_bp.route('/accesorio/<int:id>', methods=['PUT'])
@login_required
def actualizar_accesorio(id):
    """Actualizar datos de un accesorio"""
    # Verificar permisos
    if not has_permission('edit_products'):
        return jsonify({'error': 'No tienes permisos para editar productos'}), 403
    
    accesorio = Accesorio.query.get_or_404(id)
    try:
        data = request.get_json()
        accesorio.nombre = data['nombre']
        accesorio.marca_id = data['marca_id']
        accesorio.categoria_id = data['categoria_id']
        accesorio.precio = float(data['precio'])
        accesorio.stock = int(data['stock'])
        accesorio.descripcion = data['descripcion']
        accesorio.codigo_producto = data['codigo_producto']
        
        db.session.commit()
        return jsonify({'message': 'Accesorio actualizado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@productos_bp.route('/accesorio/<int:id>', methods=['DELETE'])
@login_required
def eliminar_accesorio(id):
    """Eliminar un accesorio"""
    # Solo administradores pueden eliminar
    if current_user.rol != 'admin':
        return jsonify({'error': 'Solo los administradores pueden eliminar productos'}), 403
    
    accesorio = Accesorio.query.get_or_404(id)
    try:
        # Verificar si tiene ventas asociadas
        # if accesorio.ventas_detalle:  # Si tienes esta relación
        #     return jsonify({'error': 'No se puede eliminar un producto con ventas asociadas'}), 400
        
        db.session.delete(accesorio)
        db.session.commit()
        return jsonify({'message': 'Accesorio eliminado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API Endpoints para Servicios TV
@productos_bp.route('/servicio_tv/<int:id>', methods=['GET'])
@login_required
def obtener_servicio_tv(id):
    """Obtener datos de un servicio TV para mostrar detalles o editar"""
    servicio = ServicioTV.query.get_or_404(id)
    return jsonify({
        'id': servicio.id,
        'nombre': servicio.nombre,
        'proveedor': servicio.proveedor,
        'descripcion': servicio.descripcion,
        'precio_mensual': float(servicio.precio_mensual),
        'canales': servicio.canales,
        'caracteristicas': servicio.caracteristicas
    })

@productos_bp.route('/servicio_tv/<int:id>', methods=['PUT'])
@login_required
def actualizar_servicio_tv(id):
    """Actualizar datos de un servicio TV"""
    # Verificar permisos
    if not has_permission('edit_products'):
        return jsonify({'error': 'No tienes permisos para editar productos'}), 403
    
    servicio = ServicioTV.query.get_or_404(id)
    try:
        data = request.get_json()
        servicio.nombre = data['nombre']
        servicio.proveedor = data['proveedor']
        servicio.descripcion = data['descripcion']
        servicio.precio_mensual = float(data['precio_mensual'])
        servicio.canales = int(data['canales'])
        servicio.caracteristicas = {
            'hd': data.get('hd', False),
            'internet': data.get('internet', False),
            'deportes': data.get('deportes', False),
            'peliculas': data.get('peliculas', False)
        }
        
        db.session.commit()
        return jsonify({'message': 'Servicio TV actualizado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@productos_bp.route('/servicio_tv/<int:id>', methods=['DELETE'])
@login_required
def eliminar_servicio_tv(id):
    """Eliminar un servicio TV"""
    # Solo administradores pueden eliminar
    if current_user.rol != 'admin':
        return jsonify({'error': 'Solo los administradores pueden eliminar productos'}), 403
    
    servicio = ServicioTV.query.get_or_404(id)
    try:
        # Verificar si tiene contratos asociados
        # if servicio.contratos:  # Si tienes esta relación
        #     return jsonify({'error': 'No se puede eliminar un servicio con contratos asociados'}), 400
        
        db.session.delete(servicio)
        db.session.commit()
        return jsonify({'message': 'Servicio TV eliminado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500