from datetime import datetime, date
from werkzeug.security import generate_password_hash
# Ajusta estos imports según tu estructura de archivos
from app import create_app, db  # O como tengas configurado tu app
from models import Usuario, Marca, Categoria, Celular, Accesorio, ServicioTV

# Crear la app
app = create_app('development')  # O el config que uses

def create_seed_data():
    """Crea datos iniciales para la base de datos"""
    
    with app.app_context():
        # Limpiar tablas existentes (opcional)
        db.drop_all()
        
        # Crear todas las tablas
        db.create_all()
        
        print("Creando datos iniciales...")
        
        # 1. Crear usuarios
        usuarios = [
            Usuario(
                username='admin',
                password=generate_password_hash('admin123'),
                nombre='Administrador Principal',
                rol='admin',
                telefono='987654321',
                direccion='Av. Principal 123',
                fecha_contratacion=date(2024, 1, 1)
            ),
            Usuario(
                username='vendedor1',
                password=generate_password_hash('vend123'),
                nombre='Juan Pérez',
                rol='vendedor',
                telefono='987654322',
                direccion='Jr. Comercio 456',
                fecha_contratacion=date(2024, 2, 15)
            ),
            Usuario(
                username='tecnico1',
                password=generate_password_hash('tech123'),
                nombre='María García',
                rol='tecnico',
                telefono='987654323',
                direccion='Av. Tecnológica 789',
                fecha_contratacion=date(2024, 3, 1)
            )
        ]
        
        for usuario in usuarios:
            db.session.add(usuario)
        
        # 2. Crear marcas
        marcas = [
            Marca(nombre='Samsung'),
            Marca(nombre='Apple'),
            Marca(nombre='Xiaomi'),
            Marca(nombre='Huawei'),
            Marca(nombre='Motorola'),
            Marca(nombre='Anker'),
            Marca(nombre='Belkin')
        ]
        
        for marca in marcas:
            db.session.add(marca)
        
        # 3. Crear categorías de accesorios
        categorias = [
            Categoria(nombre='Fundas', descripcion='Fundas y estuches protectores'),
            Categoria(nombre='Cargadores', descripcion='Cargadores y cables'),
            Categoria(nombre='Auriculares', descripcion='Auriculares y audífonos'),
            Categoria(nombre='Protectores', descripcion='Micas y protectores de pantalla'),
            Categoria(nombre='Soportes', descripcion='Soportes y bases para dispositivos')
        ]
        
        for categoria in categorias:
            db.session.add(categoria)
        
        # Hacer commit para obtener los IDs
        db.session.commit()
        
        # 4. Crear celulares
        celulares = [
            Celular(
                modelo='Galaxy S24',
                marca_id=1,  # Samsung
                precio=3500.00,
                stock=15,
                descripcion='Smartphone premium con cámara de alta calidad',
                especificaciones={
                    'ram': '8GB',
                    'almacenamiento': '256GB',
                    'pantalla': '6.2 pulgadas',
                    'color': 'Negro'
                },
                estado='nuevo',
                imei='123456789012345'
            ),
            Celular(
                modelo='iPhone 15',
                marca_id=2,  # Apple
                precio=4200.00,
                stock=10,
                descripcion='iPhone con chip A17 Pro',
                especificaciones={
                    'ram': '8GB',
                    'almacenamiento': '128GB',
                    'pantalla': '6.1 pulgadas',
                    'color': 'Azul'
                },
                estado='nuevo',
                imei='123456789012346'
            ),
            Celular(
                modelo='Redmi Note 13',
                marca_id=3,  # Xiaomi
                precio=800.00,
                stock=25,
                descripcion='Smartphone económico con gran batería',
                especificaciones={
                    'ram': '6GB',
                    'almacenamiento': '128GB',
                    'pantalla': '6.67 pulgadas',
                    'color': 'Verde'
                },
                estado='nuevo',
                imei='123456789012347'
            )
        ]
        
        for celular in celulares:
            db.session.add(celular)
        
        # 5. Crear accesorios
        accesorios = [
            Accesorio(
                nombre='Funda Samsung Galaxy S24',
                marca_id=1,
                categoria_id=1,
                precio=25.00,
                stock=50,
                descripcion='Funda protectora transparente',
                codigo_producto='FUND-SAM-S24-001'
            ),
            Accesorio(
                nombre='Cargador USB-C 25W',
                marca_id=6,  # Anker
                categoria_id=2,
                precio=45.00,
                stock=30,
                descripcion='Cargador rápido compatible con Samsung',
                codigo_producto='CARG-ANK-25W-001'
            ),
            Accesorio(
                nombre='Auriculares AirPods',
                marca_id=2,  # Apple
                categoria_id=3,
                precio=180.00,
                stock=20,
                descripcion='Auriculares inalámbricos con cancelación de ruido',
                codigo_producto='AUR-APP-PODS-001'
            ),
            Accesorio(
                nombre='Mica Protectora iPhone 15',
                marca_id=7,  # Belkin
                categoria_id=4,
                precio=15.00,
                stock=40,
                descripcion='Protector de pantalla de vidrio templado',
                codigo_producto='MICA-BEL-IP15-001'
            )
        ]
        
        for accesorio in accesorios:
            db.session.add(accesorio)
        
        # 6. Crear servicios de TV
        servicios_tv = [
            ServicioTV(
                nombre='Paquete Básico',
                proveedor='Movistar',
                descripcion='Paquete básico con canales nacionales',
                precio_mensual=65.00,
                canales=120,
                caracteristicas={
                    'hd': True,
                    'deco': 'incluido',
                    'internet': False
                }
            ),
            ServicioTV(
                nombre='Paquete Premium',
                proveedor='Claro',
                descripcion='Paquete completo con canales internacionales',
                precio_mensual=120.00,
                canales=300,
                caracteristicas={
                    'hd': True,
                    '4k': True,
                    'deco': 'incluido',
                    'internet': '100MB'
                }
            ),
            ServicioTV(
                nombre='Netflix + Prime',
                proveedor='Streaming Bundle',
                descripcion='Combo de servicios de streaming',
                precio_mensual=35.00,
                canales=0,
                caracteristicas={
                    'netflix': 'premium',
                    'prime_video': 'incluido',
                    'dispositivos': 4
                }
            )
        ]
        
        for servicio in servicios_tv:
            db.session.add(servicio)
        
        # Hacer commit final
        db.session.commit()
        
        print("✅ Datos iniciales creados exitosamente!")
        print(f"📱 Celulares: {len(celulares)}")
        print(f"🔌 Accesorios: {len(accesorios)}")
        print(f"👥 Usuarios: {len(usuarios)}")
        print(f"🏷️ Marcas: {len(marcas)}")
        print(f"📂 Categorías: {len(categorias)}")
        print(f"📺 Servicios TV: {len(servicios_tv)}")

def reset_database():
    """Elimina y recrea toda la base de datos"""
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("🔄 Base de datos reiniciada")

if __name__ == '__main__':
    create_seed_data()