from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class Unidad(models.Model):
    """Modelo para las unidades organizacionales"""
    nombre = models.CharField(max_length=200)
    activa = models.BooleanField(default=True)
    sin_reporte = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Unidad'
        verbose_name_plural = 'Unidades'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class UsuarioManager(BaseUserManager):
    """Manager personalizado para el modelo Usuario"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Crea y guarda un usuario regular"""
        if not email:
            raise ValueError('El usuario debe tener un correo electrónico')
        
        email = self.normalize_email(email)
        usuario = self.model(email=email, **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Crea y guarda un superusuario"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('rol', 'ADMIN')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """Modelo personalizado de usuario basado en el esquema proporcionado"""
    
    ROLES = [
        ('UNIDAD', 'Unidad'),
        ('ADMIN', 'Administrador'),
        ('AUDITOR', 'Auditor'),
    ]
    
    email = models.EmailField(max_length=254, unique=True, verbose_name='Correo electrónico')
    is_staff = models.BooleanField(default=False, verbose_name='Es staff')
    is_active = models.BooleanField(default=True, verbose_name='Está activo')
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='Fecha de registro')
    rol = models.CharField(max_length=10, choices=ROLES, default='UNIDAD', verbose_name='Rol')
    unidad = models.ForeignKey(Unidad, on_delete=models.PROTECT, verbose_name='Unidad')
    debe_cambiar_clave = models.BooleanField(default=True, verbose_name='Debe cambiar contraseña')
    
    objects = UsuarioManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['unidad_id']
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.email
    
    def get_nombre_completo(self):
        """Retorna el email como nombre completo"""
        return self.email
    
    def get_nombre_corto(self):
        """Retorna el email como nombre corto"""
        return self.email
