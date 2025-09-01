#!/usr/bin/env python3
"""
Script para manejar migraciones de la base de datos
"""

from flask_migrate import Migrate, MigrateCommand
from app import create_app, db

app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    from flask.cli import FlaskGroup
    cli = FlaskGroup(create_app=lambda: app)
    
    @cli.command('db')
    def db_command():
        """Comandos de base de datos"""
        pass
    
    cli()