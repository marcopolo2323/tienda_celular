from app.models import db, Celular, Accesorio, Venta, Servicio
from datetime import datetime, date
from sqlalchemy import func

def get_dashboard_stats():
    """Obtiene estadísticas para el dashboard"""
    
    # Contadores básicos
    celulares_count = Celular.query.count()
    accesorios_count = Accesorio.query.count()
    
    # Ventas de hoy
    today = date.today()
    try:
        ventas_hoy = Venta.query.filter(
            Venta.fecha_venta >= today,
            Venta.estado == 'completada'
        ).count()
    except Exception as e:
        # Solución temporal si la migración no se ha aplicado
        ventas_hoy = 0
    
    # Total de ventas de hoy
    try:
        total_ventas_hoy = db.session.query(func.sum(Venta.total)).filter(
            Venta.fecha_venta >= today,
            Venta.estado == 'completada'
        ).scalar() or 0
    except Exception as e:
        # Solución temporal si la migración no se ha aplicado
        total_ventas_hoy = 0
    
    # Productos con bajo stock
    celulares_bajo_stock = Celular.query.filter(Celular.stock < 5).all()
    accesorios_bajo_stock = Accesorio.query.filter(Accesorio.stock < 10).all()
    
    # Servicios pendientes
    servicios_pendientes = Servicio.query.filter_by(estado='pendiente').all()
    
    # Estadísticas adicionales
    ventas_mes = get_monthly_sales()
    productos_mas_vendidos = get_top_selling_products()
    
    return {
        'celulares_count': celulares_count,
        'accesorios_count': accesorios_count,
        'ventas_hoy': ventas_hoy,
        'total_ventas_hoy': float(total_ventas_hoy),
        'celulares_bajo_stock': celulares_bajo_stock,
        'accesorios_bajo_stock': accesorios_bajo_stock,
        'servicios_pendientes': servicios_pendientes,
        'ventas_mes': ventas_mes,
        'productos_mas_vendidos': productos_mas_vendidos,
        'now': datetime.now()
    }

def get_monthly_sales():
    """Obtiene ventas del mes actual"""
    today = date.today()
    first_day = today.replace(day=1)
    
    try:
        ventas_mes = db.session.query(func.sum(Venta.total)).filter(
            Venta.fecha_venta >= first_day,
            Venta.estado == 'completada'
        ).scalar() or 0
    except Exception as e:
        # Solución temporal si la migración no se ha aplicado
        ventas_mes = 0
    
    return float(ventas_mes)

def get_top_selling_products(limit=5):
    """Obtiene los productos más vendidos"""
    # Esta consulta necesitaría ser más compleja para obtener productos específicos
    # Por ahora retornamos una estructura básica
    return []

def get_low_stock_alert():
    """Obtiene alertas de stock bajo"""
    alerts = []
    
    celulares_bajo_stock = Celular.query.filter(Celular.stock < 5).all()
    for celular in celulares_bajo_stock:
        alerts.append({
            'tipo': 'celular',
            'producto': f"{celular.marca.nombre} {celular.modelo}",
            'stock': celular.stock,
            'nivel': 'critico' if celular.stock < 2 else 'bajo'
        })
    
    accesorios_bajo_stock = Accesorio.query.filter(Accesorio.stock < 10).all()
    for accesorio in accesorios_bajo_stock:
        alerts.append({
            'tipo': 'accesorio',
            'producto': accesorio.nombre,
            'stock': accesorio.stock,
            'nivel': 'critico' if accesorio.stock < 5 else 'bajo'
        })
    
    return alerts