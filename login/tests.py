from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Unidad

Usuario = get_user_model()


class ModelosTestCase(TestCase):
    """Tests para los modelos de la app login"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.unidad = Unidad.objects.create(
            nombre='Unidad de Prueba',
            activa=True
        )
    
    def test_crear_usuario(self):
        """Test para crear un usuario"""
        usuario = Usuario.objects.create_user(
            email='test@ejemplo.com',
            password='password123',
            unidad=self.unidad,
            rol='UNIDAD'
        )
        self.assertEqual(usuario.email, 'test@ejemplo.com')
        self.assertTrue(usuario.check_password('password123'))
        self.assertEqual(usuario.rol, 'UNIDAD')
    
    def test_crear_superusuario(self):
        """Test para crear un superusuario"""
        admin = Usuario.objects.create_superuser(
            email='admin@ejemplo.com',
            password='admin123',
            unidad=self.unidad
        )
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)
        self.assertEqual(admin.rol, 'ADMIN')
    
    def test_unidad_str(self):
        """Test para el método __str__ de Unidad"""
        self.assertEqual(str(self.unidad), 'Unidad de Prueba')
