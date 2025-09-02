import os
import sys
from flask import Flask
from app import create_app
from app.models import db
from sqlalchemy import text

# Crear la aplicación Flask
app = create_app()

# Establecer el contexto de la aplicación
with app.app_context():
    print("Iniciando migración de la base de datos...")
    try:
        # Verificar si la tabla Cliente existe
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='cliente'"))
            if result.fetchone():
                print("Tabla Cliente ya existe.")
            else:
                print("Creando tabla Cliente...")
                conn.execute(text("""
                CREATE TABLE cliente (
                    id INTEGER NOT NULL, 
                    nombre VARCHAR(120) NOT NULL, 
                    telefono VARCHAR(20), 
                    email VARCHAR(120), 
                    direccion TEXT, 
                    fecha_registro DATETIME, 
                    PRIMARY KEY (id)
                )
                """))
                conn.commit()
                print("Tabla Cliente creada exitosamente.")
    except Exception as e:
        print(f"Error al verificar/crear tabla Cliente: {e}")
    
    # Verificar si la columna cliente_id existe en la tabla venta
    try:
        with db.engine.connect() as conn:
            try:
                conn.execute(text("SELECT cliente_id FROM venta LIMIT 1"))
                print("Columna cliente_id ya existe en la tabla venta.")
            except Exception:
                print("Agregando columna cliente_id a la tabla venta...")
                conn.execute(text("ALTER TABLE venta ADD COLUMN cliente_id INTEGER REFERENCES cliente(id)"))
                conn.commit()
                print("Columna cliente_id agregada exitosamente a la tabla venta.")
    except Exception as e:
        print(f"Error al verificar/agregar columna cliente_id: {e}")
    
    print("Migración completada.")
    
    # Crear tablas que faltan
    try:
        db.create_all()
        print("Todas las tablas han sido creadas/actualizadas.")
    except Exception as e:
        print(f"Error al crear tablas: {e}")