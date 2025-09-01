from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import db, Venta, DetalleVenta, Celular, Accesorio, ServicioTV
from app.utils.sales import process_sale, get_sale_details, cancel_sale

ventas_bp = Blueprint('ventas', __name__)

@ventas_bp.route('/')
@login_required
def lista_ventas():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    ventas = Venta.query.order_by(Venta.fecha_venta.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('ventas.html', ventas=ventas)

@ventas_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva_venta():
    if request.method == 'POST':
        try:
            result = process_sale(request.form, current_user.id)
            if result['success']:
                flash('Venta registrada exitosamente', 'success')
                return redirect(url_for('ventas.lista_ventas'))
            else:
                flash(result['message'], 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al procesar venta: {str(e)}', 'error')
    
    # Obtener productos disponibles
    celulares = Celular.query.filter(Celular.stock > 0).order_by(Celular.modelo).all()
    accesorios = Accesorio.query.filter(Accesorio.stock > 0).order_by(Accesorio.nombre).all()
    servicios_tv = ServicioTV.query.order_by(ServicioTV.nombre).all()
    
    return render_template('nueva_venta.html',
                         celulares=celulares,
                         accesorios=accesorios,
                         servicios_tv=servicios_tv)

@ventas_bp.route('/<int:id>/detalles')
@login_required
def detalles_venta(id):
    venta = Venta.query.get_or_404(id)
    detalles = get_sale_details(venta)
    
    return jsonify({
        'cliente_nombre': venta.cliente_nombre,
        'cliente_telefono': venta.cliente_telefono,
        'cliente_email': venta.cliente_email,
        'fecha_venta': venta.fecha_venta.isoformat(),
        'vendedor_nombre': venta.vendedor.nombre,
        'metodo_pago': venta.metodo_pago,
        'estado': venta.estado,
        'total': float(venta.total),
        'detalles': detalles
    })

@ventas_bp.route('/<int:id>/cancelar', methods=['POST'])
@login_required
def cancelar_venta(id):
    try:
        result = cancel_sale(id)
        if result['success']:
            flash('Venta cancelada exitosamente', 'success')
            return '', 204
        else:
            return result['message'], 400
    except Exception as e:
        return f'Error al cancelar venta: {str(e)}', 500

@ventas_bp.route('/api/producto/<tipo>/<int:id>')
@login_required
def get_producto_info(tipo, id):
    """API endpoint para obtener información de productos"""
    try:
        if tipo == 'celular':
            producto = Celular.query.get_or_404(id)
            data = {
                'id': producto.id,
                'nombre': f"{producto.marca.nombre} {producto.modelo}",
                'precio': float(producto.precio),
                'stock': producto.stock,
                'tipo': 'celular'
            }
        elif tipo == 'accesorio':
            producto = Accesorio.query.get_or_404(id)
            data = {
                'id': producto.id,
                'nombre': producto.nombre,
                'precio': float(producto.precio),
                'stock': producto.stock,
                'tipo': 'accesorio'
            }
        elif tipo == 'servicio_tv':
            producto = ServicioTV.query.get_or_404(id)
            data = {
                'id': producto.id,
                'nombre': producto.nombre,
                'precio': float(producto.precio_mensual),
                'stock': 999,  # Servicios no tienen límite de stock
                'tipo': 'servicio_tv'
            }
        else:
            return jsonify({'error': 'Tipo de producto no válido'}), 400
        
        return jsonify(data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500