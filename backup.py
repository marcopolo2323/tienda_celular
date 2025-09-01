#!/usr/bin/env python3
"""
Script para realizar copias de seguridad de la base de datos
"""

import os
import shutil
import datetime
import sqlite3
import argparse

def backup_database(db_path, backup_dir='backups'):
    """Realiza una copia de seguridad de la base de datos"""
    # Crear directorio de backups si no existe
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Generar nombre de archivo con fecha y hora
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    db_name = os.path.basename(db_path)
    backup_filename = f"{os.path.splitext(db_name)[0]}_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    # Verificar si la base de datos existe
    if not os.path.exists(db_path):
        print(f"Error: La base de datos {db_path} no existe.")
        return False
    
    try:
        # Verificar que la base de datos es válida
        conn = sqlite3.connect(db_path)
        conn.close()
        
        # Realizar la copia de seguridad
        shutil.copy2(db_path, backup_path)
        print(f"✅ Copia de seguridad creada: {backup_path}")
        return True
    except sqlite3.Error as e:
        print(f"Error de SQLite: {e}")
        return False
    except Exception as e:
        print(f"Error al realizar la copia de seguridad: {e}")
        return False

def list_backups(backup_dir='backups'):
    """Lista todas las copias de seguridad disponibles"""
    if not os.path.exists(backup_dir):
        print("No hay copias de seguridad disponibles.")
        return
    
    backups = [f for f in os.listdir(backup_dir) if f.endswith('.db')]
    
    if not backups:
        print("No hay copias de seguridad disponibles.")
        return
    
    print("\nCopias de seguridad disponibles:")
    for i, backup in enumerate(sorted(backups, reverse=True)):
        backup_path = os.path.join(backup_dir, backup)
        size_mb = os.path.getsize(backup_path) / (1024 * 1024)
        print(f"{i+1}. {backup} ({size_mb:.2f} MB)")

def restore_database(backup_path, db_path):
    """Restaura una copia de seguridad"""
    try:
        # Verificar que el archivo de backup existe
        if not os.path.exists(backup_path):
            print(f"Error: El archivo de backup {backup_path} no existe.")
            return False
        
        # Verificar que es una base de datos SQLite válida
        conn = sqlite3.connect(backup_path)
        conn.close()
        
        # Crear una copia de seguridad de la base de datos actual antes de restaurar
        if os.path.exists(db_path):
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            db_name = os.path.basename(db_path)
            pre_restore_backup = f"{os.path.splitext(db_name)[0]}_pre_restore_{timestamp}.db"
            pre_restore_path = os.path.join('backups', pre_restore_backup)
            
            if not os.path.exists('backups'):
                os.makedirs('backups')
                
            shutil.copy2(db_path, pre_restore_path)
            print(f"✅ Copia de seguridad previa a la restauración: {pre_restore_path}")
        
        # Restaurar la base de datos
        shutil.copy2(backup_path, db_path)
        print(f"✅ Base de datos restaurada desde: {backup_path}")
        return True
    except sqlite3.Error as e:
        print(f"Error de SQLite: {e}")
        return False
    except Exception as e:
        print(f"Error al restaurar la base de datos: {e}")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Herramienta de backup para la base de datos')
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando backup
    backup_parser = subparsers.add_parser('backup', help='Crear una copia de seguridad')
    backup_parser.add_argument('--db', default='app/tienda_celulares.db', help='Ruta a la base de datos')
    backup_parser.add_argument('--dir', default='backups', help='Directorio para guardar backups')
    
    # Comando list
    list_parser = subparsers.add_parser('list', help='Listar copias de seguridad')
    list_parser.add_argument('--dir', default='backups', help='Directorio de backups')
    
    # Comando restore
    restore_parser = subparsers.add_parser('restore', help='Restaurar una copia de seguridad')
    restore_parser.add_argument('backup', help='Ruta al archivo de backup')
    restore_parser.add_argument('--db', default='app/tienda_celulares.db', help='Ruta a la base de datos')
    
    args = parser.parse_args()
    
    if args.command == 'backup':
        backup_database(args.db, args.dir)
    elif args.command == 'list':
        list_backups(args.dir)
    elif args.command == 'restore':
        restore_database(args.backup, args.db)
    else:
        parser.print_help()