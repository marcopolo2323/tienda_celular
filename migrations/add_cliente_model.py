from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

# Configuración básica para la migración
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Importar los modelos para que Alembic los detecte
from app.models import Cliente, Venta

if __name__ == '__main__':
    # Este script se puede ejecutar directamente para aplicar las migraciones
    print("Ejecute 'flask db migrate' y luego 'flask db upgrade' para aplicar los cambios.")