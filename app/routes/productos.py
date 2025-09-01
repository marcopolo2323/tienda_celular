from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required,current_user
from app.models import db, Celular, Accesorio, Marca, Categoria, ServicioTV
from app.utils.validators import validate_product_data

productos_bp = Blueprint('productos', __name__)

@productos_bp.route('/celulares', methods=['GET', 'POST'])
@login_required
def celulares():
    if request.method == 'POST':
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
     # Lógica de permisos basada en el rol del usuario
    can_add = current_user.rol in ['admin', 'manager']
    can_edit = current_user.rol in ['admin', 'manager', 'employee'] 
    can_delete = current_user.rol == 'admin'
    
    return render_template('celulares.html',
                         celulares=celulares,
                         marcas=marcas,
                         can_add=can_add,
                         can_edit=can_edit,
                         can_delete=can_delete)

@productos_bp.route('/accesorios', methods=['GET', 'POST'])
@login_required
def accesorios():
    if request.method == 'POST':
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

@productos_bp.route('/celular/<int:id>', methods=['GET'])
@login_required
def obtener_celular(id):
    celular = Celular.query.get_or_404(id)
    return jsonify({
        'id': celular.id,
        'marca': celular.marca.nombre,
        'marca_id': celular.marca_id,
        'modelo': celular.modelo,
        'precio': celular.precio,
        'stock': celular.stock,
        'estado': celular.estado,
        'imei': celular.imei,
        'descripcion': celular.descripcion,
        'especificaciones': celular.especificaciones
    })

@productos_bp.route('/celular/<int:id>', methods=['PUT'])
@login_required
def actualizar_celular(id):
    celular = Celular.query.get_or_404(id)
    try:
        data = request.get_json()
        celular.modelo = data['modelo']
        celular.marca_id = data['marca_id']
        celular.precio = data['precio']
        celular.stock = data['stock']
        celular.estado = data['estado']
        celular.imei = data['imei']
        celular.descripcion = data['descripcion']
        celular.especificaciones = data['especificaciones']
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@productos_bp.route('/celular/<int:id>', methods=['DELETE'])
@login_required
def eliminar_celular_ajax(id):
    celular = Celular.query.get_or_404(id)
    try:
        db.session.delete(celular)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400