# Sistema de Administración de Tienda de Celulares

Este es un sistema completo de gestión para tiendas de celulares y accesorios que permite administrar:
- Inventario de celulares y accesorios
- Ventas y facturación
- Servicios técnicos
- Clientes
- Empleados y usuarios del sistema
- Reportes financieros y estadísticas

## Requisitos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Clonar el repositorio o descargar los archivos

2. Crear un entorno virtual:
```bash
python -m venv venv
```

3. Activar el entorno virtual:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Instalar dependencias:
```bash
pip install -r requirements.txt
```

5. Configurar variables de entorno:
   - Crear un archivo `.env` en la raíz del proyecto (ya incluido)
   - Configurar las variables necesarias (SECRET_KEY, DATABASE_URL, etc.)

6. Iniciar la aplicación:
```bash
python run.py
```

## Características

### Gestión de Inventario
- Control de stock de celulares por marca y modelo
- Gestión de accesorios por categorías
- Alertas de bajo stock
- Registro de IMEI para celulares

### Ventas
- Proceso de venta intuitivo
- Múltiples métodos de pago
- Historial de ventas
- Detalles de ventas por producto

### Servicios Técnicos
- Registro de servicios de reparación
- Seguimiento de estado
- Asignación a técnicos
- Notificaciones de servicios pendientes

### Administración
- Gestión de usuarios y permisos
- Configuración de marcas y categorías
- Reportes de ventas y servicios
- Dashboard con métricas importantes

### Seguridad
- Autenticación de usuarios
- Control de acceso basado en roles
- Protección de rutas sensibles

## Estructura del Proyecto

```
/app
  /instance         # Base de datos SQLite
  /routes           # Rutas de la aplicación (blueprints)
  /templates        # Plantillas HTML
  /utils            # Utilidades y funciones auxiliares
  __init__.py       # Inicialización de la aplicación
  config.py         # Configuración de la aplicación
  models.py         # Modelos de la base de datos
  seed.py           # Datos iniciales
/venv               # Entorno virtual
.env                # Variables de entorno
requirements.txt    # Dependencias
run.py              # Punto de entrada
```

## Usuarios por Defecto

- **Administrador**: 
  - Usuario: admin
  - Contraseña: admin123

## Despliegue

La aplicación está configurada para ser desplegada en servicios como Heroku, Render o PythonAnywhere. Consulta la documentación específica de cada plataforma para más detalles.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT.