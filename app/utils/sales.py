from app.models import db, Venta, DetalleVenta, Celular, Accesorio, ServicioTV
from datetime import datetime

def process_sale(form_data, vendedor_id):
    """Procesa una nueva venta"""
    try:
        # Crear venta principal
        venta = Venta(
            vendedor_id=vendedor_id,
            cliente_nombre=form_data['cliente_nombre'],
            cliente_telefono=form_data['cliente_telefono'],
            metodo_pago=form_data['metodo_pago']
        )
        db.session.add(venta)
        db.session.flush()  # Para obtener el ID de la venta
        
        # Procesar productos
        productos = form_data.getlist('productos[]')
        tipos = form_data.getlist('tipos[]')
        cantidades = form_data.getlist('cantidades[]')
        
        if not productos or not tipos or not cantidades:
            return {'success': False, 'message': 'Debe seleccionar al menos un producto'}
        
        total = 0
        detalles_procesados = []
        
        for producto_id, tipo, cantidad in zip(productos, tipos, cantidades):
            if not producto_id or not cantidad:
                continue
                
            cantidad = int(cantidad)
            if cantidad <= 0:
                continue
                
            # Obtener producto
            producto = get_product_by_type(tipo, producto_id)
            if not producto:
                return {'success': False, 'message': f'Producto no encontrado: {producto_id}'}
            
            # Verificar stock para productos físicos
            if tipo in ['celular', 'accesorio'] and producto.stock < cantidad:
                return {
                    'success': False, 
                    'message': f'Stock insuficiente para {get_product_name(producto, tipo)}'
                }
            
            # Crear detalle de venta
            precio_unitario = producto.precio if tipo != 'servicio_tv' else producto.precio_mensual
            detalle = DetalleVenta(
                venta_id=venta.id,
                tipo_producto=tipo,
                producto_id=int(producto_id),
                cantidad=cantidad,
                precio_unitario=precio_unitario
            )
            db.session.add(detalle)
            
            # Actualizar stock para productos físicos
            if tipo in ['celular', 'accesorio']:
                producto.stock -= cantidad
            
            total += precio_unitario * cantidad
            detalles_procesados.append({
                'producto': get_product_name(producto, tipo),
                'cantidad': cantidad,
                'precio': precio_unitario
            })
        
        if not detalles_procesados:
            return {'success': False, 'message': 'Debe agregar productos válidos a la venta'}
        
        # Actualizar total de la venta
        venta.total = total
        db.session.commit()
        
        return {
            'success': True, 
            'message': 'Venta procesada exitosamente',
            'venta_id': venta.id,
            'total': total,
            'detalles': detalles_procesados
        }
        
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Error al procesar venta: {str(e)}'}

def get_product_by_type(tipo, producto_id):
    """Obtiene un producto por su tipo e ID"""
    if tipo == 'celular':
        return Celular.query.get(int(producto_id))
    elif tipo == 'accesorio':
        return Accesorio.query.get(int(producto_id))
    elif tipo == 'servicio_tv':
        return ServicioTV.query.get(int(producto_id))
    return None

def get_product_name(producto, tipo):
    """Obtiene el nombre formateado de un producto"""
    if tipo == 'celular':
        return f"{producto.marca.nombre} {producto.modelo}"
    elif tipo == 'accesorio':
        return producto.nombre
    elif tipo == 'servicio_tv':
        return producto.nombre
    return "Producto desconocido"

def get_sale_details(venta):
    """Obtiene los detalles formateados de una venta"""
    detalles = []
    
    for detalle in venta.detalles:
        producto = get_product_by_type(detalle.tipo_producto, detalle.producto_id)
        if producto:
            nombre = get_product_name(producto, detalle.tipo_producto)
            detalles.append({
                'producto_nombre': nombre,
                'tipo_producto': detalle.tipo_producto,
                'cantidad': detalle.cantidad,
                'precio_unitario': float(detalle.precio_unitario),
                'subtotal': float(detalle.precio_unitario * detalle.cantidad)
            })
    
    return detalles

def cancel_sale(venta_id):
    """Cancela una venta y devuelve productos al inventario"""
    try:
        venta = Venta.query.get_or_404(venta_id)
        
        if venta.estado == 'cancelada':
            return {'success': False, 'message': 'La venta ya está cancelada'}
        
        if venta.estado == 'completada':
            # Devolver productos al inventario
            for detalle in venta.detalles:
                if detalle.tipo_producto in ['celular', 'accesorio']:
                    producto = get_product_by_type(detalle.tipo_producto, detalle.producto_id)
                    if producto:
                        producto.stock += detalle.cantidad
            
            venta.estado = 'cancelada'
            # El campo fecha_cancelacion no existe en el modelo, no lo usamos
            db.session.commit()
            
            return {'success': True, 'message': 'Venta cancelada exitosamente'}
        
        return {'success': False, 'message': 'No se puede cancelar esta venta'}
        
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Error al cancelar venta: {str(e)}'}

def get_sales_summary(start_date=None, end_date=None):
    """Obtiene resumen de ventas en un período"""
    query = Venta.query.filter_by(estado='completada')
    
    if start_date:
        query = query.filter(Venta.fecha_venta >= start_date)
    if end_date:
        query = query.filter(Venta.fecha_venta <= end_date)
    
    ventas = query.all()
    
    total_ventas = len(ventas)
    total_ingresos = sum(venta.total for venta in ventas)
    
    # Agrupar por método de pago
    metodos_pago = {}
    for venta in ventas:
        metodo = venta.metodo_pago
        if metodo not in metodos_pago:
            metodos_pago[metodo] = {'count': 0, 'total': 0}
        metodos_pago[metodo]['count'] += 1
        metodos_pago[metodo]['total'] += venta.total
    
    return {
        'total_ventas': total_ventas,
        'total_ingresos': float(total_ingresos),
        'promedio_venta': float(total_ingresos / total_ventas) if total_ventas > 0 else 0,
        'metodos_pago': metodos_pago,
        'periodo': {
            'inicio': start_date,
            'fin': end_date
        }
    }