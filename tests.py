#!/usr/bin/env python3
"""
Pruebas unitarias para la aplicación
"""

import unittest
from app import create_app, db
from app.models import Usuario, Marca, Categoria, Celular, Accesorio
from werkzeug.security import generate_password_hash

class TestApp(unittest.TestCase):
    
    def setUp(self):
        """Configuración antes de cada prueba"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Crear datos de prueba
        admin = Usuario(
            username='testadmin',
            password=generate_password_hash('test123'),
            nombre='Admin Test',
            rol='admin',
            telefono='123456789'
        )
        db.session.add(admin)
        
        marca = Marca(nombre='Marca Test')
        db.session.add(marca)
        
        categoria = Categoria(nombre='Categoria Test', descripcion='Descripción de prueba')
        db.session.add(categoria)
        
        db.session.commit()
    
    def tearDown(self):
        """Limpieza después de cada prueba"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_login_page(self):
        """Prueba que la página de login se carga correctamente"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Iniciar Sesi', response.data)  # 'Iniciar Sesión' en español
    
    def test_login_success(self):
        """Prueba que el login funciona correctamente"""
        response = self.client.post('/login', data={
            'username': 'testadmin',
            'password': 'test123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)
    
    def test_login_failure(self):
        """Prueba que el login falla con credenciales incorrectas"""
        response = self.client.post('/login', data={
            'username': 'testadmin',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Usuario o contrase', response.data)  # 'Usuario o contraseña incorrectos'
    
    def test_protected_route(self):
        """Prueba que las rutas protegidas redirigen a login"""
        response = self.client.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Iniciar Sesi', response.data)  # Redirigido a login

if __name__ == '__main__':
    unittest.main()