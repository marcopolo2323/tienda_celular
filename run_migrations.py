import os
import subprocess
import sys

def run_migrations():
    try:
        # Establecer la variable de entorno FLASK_APP
        os.environ['FLASK_APP'] = 'run.py'
        
        # Ejecutar las migraciones
        print("Generando migración...")
        subprocess.run([sys.executable, '-m', 'flask', 'db', 'migrate', '-m', 'Agregar modelo Cliente'], check=True)
        
        print("Aplicando migración...")
        subprocess.run([sys.executable, '-m', 'flask', 'db', 'upgrade'], check=True)
        
        print("Migración completada exitosamente.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar las migraciones: {e}")
        return False
    except Exception as e:
        print(f"Error inesperado: {e}")
        return False

if __name__ == '__main__':
    run_migrations()