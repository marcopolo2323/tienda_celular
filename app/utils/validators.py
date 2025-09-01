import re
from app.models import Celular, Accesorio

def validate_product_data(data, product_type):
    """Valida datos de productos"""
    errors = []
    
    # Validaciones comunes
    if not data.get('precio'):
        errors.append('El precio es obligatorio')
    else:
        try:
            precio = float(data['precio'])
            if precio <= 0:
                errors.append('El precio debe ser mayor a 0')
        except ValueError:
            errors.append('El precio debe ser un número válido')
    
    if not data.get('stock'):
        errors.append('El stock es obligatorio')
    else:
        try:
            stock = int(data['stock'])
            if stock < 0:
                errors.append('El stock no puede ser negativo')
        except ValueError:
            errors.append('El stock debe ser un número entero')
    
    if not data.get('marca_id'):
        errors.append('La marca es obligatoria')
    
    # Validaciones específicas por tipo
    if product_type == 'celular':
        errors.extend(validate_celular_data(data))
    elif product_type == 'accesorio':
        errors.extend(validate_accesorio_data(data))
    
    return errors

def validate_celular_data(data):
    """Validaciones específicas para celulares"""
    errors = []
    
    if not data.get('modelo'):
        errors.append('El modelo es obligatorio')
    
    if not data.get('imei'):
        errors.append('El IMEI es obligatorio')
    else:
        # Validar formato IMEI (15 dígitos)
        imei = data['imei'].replace(' ', '').replace('-', '')
        if not re.match(r'^\d{15}$', imei):
            errors.append('El IMEI debe tener exactamente 15 dígitos')
        else:
            # Verificar que el IMEI no exista ya en la BD
            existing = Celular.query.filter_by(imei=imei).first()
            if existing:
                errors.append('Este IMEI ya está registrado')
    
    # Validar especificaciones
    if not data.get('ram'):
        errors.append('La memoria RAM es obligatoria')
    
    if not data.get('almacenamiento'):
        errors.append('El almacenamiento es obligatorio')
    
    if not data.get('color'):
        errors.append('El color es obligatorio')
    
    return errors

def validate_accesorio_data(data):
    """Validaciones específicas para accesorios"""
    errors = []
    
    if not data.get('nombre'):
        errors.append('El nombre es obligatorio')
    
    if not data.get('categoria_id'):
        errors.append('La categoría es obligatoria')
    
    if not data.get('codigo_producto'):
        errors.append('El código de producto es obligatorio')
    else:
        # Verificar que el código no exista ya
        existing = Accesorio.query.filter_by(codigo_producto=data['codigo_producto']).first()
        if existing:
            errors.append('Este código de producto ya está registrado')
    
    return errors

def validate_user_data(data, is_edit=False, user_id=None):
    """Valida datos de usuarios"""
    errors = []
    
    if not data.get('username'):
        errors.append('El nombre de usuario es obligatorio')
    elif len(data['username']) < 3:
        errors.append('El nombre de usuario debe tener al menos 3 caracteres')
    
    if not data.get('nombre'):
        errors.append('El nombre completo es obligatorio')
    
    if not data.get('rol'):
        errors.append('El rol es obligatorio')
    elif data['rol'] not in ['admin', 'vendedor', 'tecnico']:
        errors.append('Rol no válido')
    
    # Validar contraseña solo para usuarios nuevos
    if not is_edit and not data.get('password'):
        errors.append('La contraseña es obligatoria')
    elif not is_edit and len(data['password']) < 6:
        errors.append('La contraseña debe tener al menos 6 caracteres')
    
    # Validar email si se proporciona
    email = data.get('email', '').strip()
    if email and not validate_email(email):
        errors.append('El formato del email no es válido')
    
    # Validar teléfono si se proporciona
    telefono = data.get('telefono', '').strip()
    if telefono and not validate_phone(telefono):
        errors.append('El formato del teléfono no es válido')
    
    return errors

def validate_email(email):
    """Valida formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Valida formato de teléfono"""
    # Acepta números con o sin espacios, guiones o paréntesis
    phone_clean = re.sub(r'[\s\-\(\)]', '', phone)
    return re.match(r'^\+?[\d]{7,15}$', phone_clean) is not None

def validate_sale_data(data):
    """Valida datos de venta"""
    errors = []
    
    if not data.get('cliente_nombre'):
        errors.append('El nombre del cliente es obligatorio')
    
    if not data.get('cliente_telefono'):
        errors.append('El teléfono del cliente es obligatorio')
    elif not validate_phone(data['cliente_telefono']):
        errors.append('El formato del teléfono no es válido')
    
    if not data.get('metodo_pago'):
        errors.append('El método de pago es obligatorio')
    elif data['metodo_pago'] not in ['efectivo', 'tarjeta', 'transferencia', 'credito']:
        errors.append('Método de pago no válido')
    
    # Validar email si se proporciona
    email = data.get('cliente_email', '').strip()
    if email and not validate_email(email):
        errors.append('El formato del email no es válido')
    
    return errors

def validate_service_data(data):
    """Valida datos de servicios técnicos"""
    errors = []
    
    if not data.get('tipo'):
        errors.append('El tipo de servicio es obligatorio')
    
    if not data.get('descripcion'):
        errors.append('La descripción es obligatoria')
    elif len(data['descripcion']) < 10:
        errors.append('La descripción debe tener al menos 10 caracteres')
    
    if not data.get('cliente_nombre'):
        errors.append('El nombre del cliente es obligatorio')
    
    if not data.get('cliente_telefono'):
        errors.append('El teléfono del cliente es obligatorio')
    elif not validate_phone(data['cliente_telefono']):
        errors.append('El formato del teléfono no es válido')
    
    if not data.get('costo'):
        errors.append('El costo es obligatorio')
    else:
        try:
            costo = float(data['costo'])
            if costo < 0:
                errors.append('El costo no puede ser negativo')
        except ValueError:
            errors.append('El costo debe ser un número válido')
    
    return errors