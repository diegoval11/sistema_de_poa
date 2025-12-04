from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, Unidad


@admin.register(Unidad)
class UnidadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activa', 'sin_reporte')
    list_filter = ('activa', 'sin_reporte')
    search_fields = ('nombre',)


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = ('email', 'rol', 'unidad', 'is_active', 'debe_cambiar_clave', 'date_joined')
    list_filter = ('rol', 'is_active', 'debe_cambiar_clave', 'is_staff')
    search_fields = ('email', 'unidad__nombre')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información Personal', {'fields': ('unidad', 'rol')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Seguridad', {'fields': ('debe_cambiar_clave',)}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'unidad', 'rol', 'password1', 'password2', 'debe_cambiar_clave'),
        }),
    )
