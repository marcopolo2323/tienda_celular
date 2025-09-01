from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # admin, vendedor, tecnico
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.Text)
    fecha_contratacion = db.Column(db.Date, default=datetime.today().date)
    ventas = db.relationship('Venta', backref='vendedor', lazy=True)

class Marca(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    celulares = db.relationship('Celular', backref='marca', lazy=True)
    accesorios = db.relationship('Accesorio', backref='marca', lazy=True)

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    descripcion = db.Column(db.Text)
    accesorios = db.relationship('Accesorio', backref='categoria', lazy=True)

class Celular(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    modelo = db.Column(db.String(100), nullable=False)
    marca_id = db.Column(db.Integer, db.ForeignKey('marca.id'), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    descripcion = db.Column(db.Text)
    especificaciones = db.Column(db.JSON)  # Almacena RAM, almacenamiento, color, etc.
    estado = db.Column(db.String(20), default='nuevo')  # nuevo, reacondicionado
    imei = db.Column(db.String(50), unique=True)

class Accesorio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    marca_id = db.Column(db.Integer, db.ForeignKey('marca.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    descripcion = db.Column(db.Text)
    codigo_producto = db.Column(db.String(50), unique=True)

class ServicioTV(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    proveedor = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    precio_mensual = db.Column(db.Float, nullable=False)
    canales = db.Column(db.Integer)  # Número de canales incluidos
    caracteristicas = db.Column(db.JSON)  # Almacena detalles del paquete

class Venta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendedor_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    cliente_nombre = db.Column(db.String(120), nullable=False)
    cliente_telefono = db.Column(db.String(20))
    cliente_email = db.Column(db.String(120))
    fecha_venta = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Float, default=0.0)
    metodo_pago = db.Column(db.String(50))  # efectivo, tarjeta, transferencia
    estado = db.Column(db.String(20), default='completada')  # completada, cancelada
    detalles = db.relationship('DetalleVenta', backref='venta', lazy=True)

class DetalleVenta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('venta.id'), nullable=False)
    tipo_producto = db.Column(db.String(20))  # celular, accesorio, servicio
    producto_id = db.Column(db.Integer, nullable=False)  # ID del producto según tipo
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    garantia = db.Column(db.String(100))  # Información de garantía si aplica
    notas = db.Column(db.Text)

class Servicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)  # reparación, mantenimiento, instalación
    descripcion = db.Column(db.Text, nullable=False)
    cliente_nombre = db.Column(db.String(120), nullable=False)
    cliente_telefono = db.Column(db.String(20))
    fecha_recepcion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_entrega_estimada = db.Column(db.DateTime)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, en_proceso, completado
    costo = db.Column(db.Float)
    tecnico_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    notas_tecnicas = db.Column(db.Text)
    
    tecnico = db.relationship('Usuario', backref='servicios') 