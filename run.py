#!/usr/bin/env python3
"""
Aplicación de Gestión de Tienda de Celulares
Archivo principal para ejecutar la aplicación
"""

from app import create_app
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Crear la aplicación
app = create_app()

if __name__ == '__main__':
    # Configuración para desarrollo
    print("🚀 Iniciando aplicación de Gestión de Tienda de Celulares...")
    print("📍 Accede a: http://localhost:5000")
    print("👤 Usuario: admin | Contraseña: admin123")
    print("-" * 50)
    
    app.run(
        host='0.0.0.0',  # Permite acceso desde otras IPs en la red local
        port=int(os.environ.get('PORT', 5000)),
        debug=(os.environ.get('FLASK_ENV') == 'development'),
        threaded=True
    )