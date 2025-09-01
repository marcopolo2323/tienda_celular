# Este archivo hace que 'routes' sea un paquete Python
# Aquí puedes agregar imports comunes para todos los módulos de rutas

from flask import flash

# Funciones auxiliares compartidas por todas las rutas
def flash_errors(errors):
    """Helper para mostrar múltiples errores"""
    for error in errors:
        flash(error, 'error')

def flash_success(message):
    """Helper para mensajes de éxito"""
    flash(message, 'success')

def flash_info(message):
    """Helper para mensajes informativos"""
    flash(message, 'info')

def flash_warning(message):
    """Helper para mensajes de advertencia"""
    flash(message, 'warning')