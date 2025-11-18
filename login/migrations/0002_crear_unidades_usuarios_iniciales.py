from django.db import migrations

UNIDADES_PARA_CREAR = [
    ("Sindicatura", "sindicatura"),
    ("Auditoría Interna", "auditoriainterna"),
    ("Secretaría Municipal", "secretariamunicipal"),
    ("UGDA", "ugda"),
    ("UAIP", "uaip"),
    ("DESPACHO MUNICIPAL", "despachomunicipal"),
    ("CAM.", "cam"),
    ("Unidad de Proteccion de Animales de Compañía", "proteccionanimales"),
    ("Desarrollo Comunal.", "desarrollocomunal"),
    ("Unidad de Turismo.", "turismo"),
    ("UCP", "ucp"),
    ("Comunicaciones.", "comunicaciones"),
    ("DIRECCION DE DISTRITO", "direcciondistrito"),
    ("Unidad de Cooperación y Relaciones Internacionales.", "cooperacion"),
    ("Departamento de Talento Humano.", "talentohumano"),
    ("Centro de Contacto de Denuncias y Quejas Ciudadanas.", "contactociudadano"),
    ("Unidad de Gestión de Riesgos.", "gestionriesgos"),
    ("Unidad de Eventos y Festejos Municipales", "eventos"),
    ("Gerencia de Innovación", "innovacion"),
    ("GERENCIA DE PLANIFICACIÓN Y OPERERACIONES", "planificacionoperaciones"),
    ("Transporte y Logística", "transportelogistica"),
    ("GERENCIA FINANCIERA Y TRIBUTARIA", "finanzastributaria"),
    ("Departamento de Presupuesto.", "presupuesto"),
    ("Departamento de Tesorería.", "tesoreria"),
    ("Departamento de Contabilidad.", "contabilidad"),
    ("Departamento de Inventario.", "inventario"),
    ("Unidad de Almacén y Proveeduría.", "almacenproveeduria"),
    ("Sub Gerencia Tributaria", "subgerenciatributaria"),
    ("Departamento de Cuentas Corrientes.", "cuentascorrientes"),
    ("Departamento de Recuperación de Mora.", "recuperacionmora"),
    ("Departamento de Fiscalización.", "fiscalizacion"),
    ("Departamento de Catastro de Inmuebles.", "catastroinmuebles"),
    ("Departamento de Catastro de Empresas", "catastroempresas"),
    ("Unidad de Desarrollo Empresarial.", "desarrolloempresarial"),
    ("GERENCIA TÉCNICA DE DESARROLLO TERRITORIAL", "desarrolloterritorial"),
    ("Departamento de Ingeniería", "ingenieria"),
    ("Unidad de Proyectos", "proyectos"),
    ("Unidad de topografía", "topografia"),
    ("Oficina de Centro Histórico", "centrohistorico"),
    ("Unidad de ornato publico, parques y jardines municipales", "ornatoparques"),
    ("Unidad de Medio Ambiente", "medioambiente"),
    ("GERENCIA DE DESECHOS SOLIDOS", "desechossolidos"),
    ("Aseo Urbano", "aseourbano"),
    ("Recoleccion de Desechos Solidos", "recolecciondesechos"),
    ("Unidad de Orden y Limpieza", "ordenlimpieza"),
    ("GERENCIA DE SERVICIOS DE MANTENIMIENTO.", "serviciosmantenimiento"),
    ("Mtto. de Alumbrado Público y Servicios Generales.", "alumbradopublico"),
    ("Red Vial.", "redvial"),
    ("Monitoreo y mantenimiento de flotas municipales", "monitoreoflotas"),
    ("GERENCIA LEGAL.", "gerencialegal"),
    ("Departamento de Legalización de Bienes Raíces Municipales.", "legalizacionbienes"),
    ("Delegación Contravencional Municipal.", "contravencional"),
    ("Centro de Mediación Municipal.", "mediacion"),
    ("Registro del Estado Familiar y OAT-REF 1 y 2.", "estadofamiliar"),
    ("GERENCIA DE DESARROLLO SOCIAL", "desarrollosocial"),
    ("Sub Gerencia de Desarrollo Social", "subdesarrollosocial"),
    ("Talleres Vocacionales.", "talleresvocacionales"),
    ("Cultura, Arte y Biblioteca Municipal", "culturaartebiblioteca"),
    ("Clínica Municipal.", "clinicamunicipal"),
    ("Recreación y Deportes.", "recreaciondeportes"),
    ("Unidad Municipal de la Mujer.", "mujer"),
    ("Departamento de Impresión Grafica", "impresiongrafica"),
    ("Unidad de la Niñez , Adolescencia y juventud", "ninezjuventud"),
    ("C.B.I Colon", "cbicolon"),
    ("C.B.I Río Zarco", "cbiriozarco"),
    ("GERENCIA DE SERVICIOS MUNICIPALES", "serviciosmunicipales"),
    ("Mercado Municipal 1", "mercado1"),
    ("Mercado Municipal 2 y Terminal de Buses.", "mercado2"),
    ("Mercado Municipal 3", "mercado3"),
    ("Cementerios y Funeraria Municipal.", "cementerios"),
    ("Unidad de prevencion en salud, saneamiento ambental y abastos de los mercados municipales", "prevencionsaludmercados"),
    ("Rastro Municipal.", "rastromunicipal"),
]


def crear_unidades_y_usuarios(apps, schema_editor):
    """
    Poblamos la base de datos con las unidades y usuarios iniciales.
    """
    # --- INICIO DE LA CORRECCIÓN ---
    # Importamos AMBOS modelos reales.
    # No podemos mezclar un modelo real (Usuario)
    # con un modelo histórico (Unidad)
    from login.models import Unidad, Usuario
    # --- FIN DE LA CORRECCIÓN ---

    print("\nCreando unidades y usuarios...")

    for nombre_unidad, alias in UNIDADES_PARA_CREAR:

        # 1. Crear la Unidad (usando el modelo real)
        unidad_obj, created = Unidad.objects.get_or_create(
            nombre=nombre_unidad,
            defaults={
                'activa': True,
                'sin_reporte': False
            }
        )

        if created:
            print(f"  - Creada Unidad: {nombre_unidad}")
        else:
            print(f"  - Ya existía Unidad: {nombre_unidad}")

        # 2. Definir datos del Usuario
        email = f"{alias}@alcaldia.com"
        password = f"{alias.capitalize()[0]}#{alias[:3]}!2025"

        # 3. Crear el Usuario (usando el modelo real)
        if not Usuario.objects.filter(email=email).exists():
            
            Usuario.objects.create_user(
                email=email,
                password=password,
                unidad=unidad_obj,  # Ahora SÍ es el tipo correcto
                rol='UNIDAD',
                debe_cambiar_clave=True
            )
            
            print(f"    - Creado Usuario: {email} (Pass: {password})")
        else:
            print(f"    - Ya existía Usuario: {email}")


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0001_initial'), 
    ]

    operations = [
        migrations.RunPython(crear_unidades_y_usuarios),
    ]