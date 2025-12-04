from django.db import migrations
from django.contrib.auth.hashers import make_password

def crear_superuser(apps, schema_editor):
    Usuario = apps.get_model('login', 'Usuario')
    Unidad = apps.get_model('login', 'Unidad')

    # Intentamos obtener una unidad para asignar al admin
    # Usamos 'DESPACHO MUNICIPAL' como default, o la primera que encontremos
    unidad = Unidad.objects.filter(nombre="DESPACHO MUNICIPAL").first()
    if not unidad:
        unidad = Unidad.objects.first()
    
    if not unidad:
        # Si no hay unidades, creamos una dummy (aunque la migracion 0002 deberia haberlas creado)
        unidad = Unidad.objects.create(nombre="ADMINISTRACION", activa=True, sin_reporte=True)

    email = "admin@alcaldia.com"
    password = "123"

    if not Usuario.objects.filter(email=email).exists():
        Usuario.objects.create(
            email=email,
            password=make_password(password),
            unidad=unidad,
            rol='ADMIN',
            is_staff=True,
            is_superuser=True,
            is_active=True,
            debe_cambiar_clave=False
        )
        print(f"\nSuperusuario creado: {email} / {password}")
    else:
        print(f"\nEl usuario {email} ya existe")

class Migration(migrations.Migration):

    dependencies = [
        ('login', '0002_crear_unidades_usuarios_iniciales'),
    ]

    operations = [
        migrations.RunPython(crear_superuser),
    ]
