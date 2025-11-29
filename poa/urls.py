from django.urls import path
from . import views

app_name = 'poa'

urlpatterns = [
    path('', views.lista_proyectos, name='lista_proyectos'),
    path('crear/', views.crear_proyecto_wizard, name='crear_proyecto_wizard'),
    path('cancelar/', views.cancelar_wizard, name='cancelar_wizard'),
    path('proyecto/<int:proyecto_id>/', views.detalle_proyecto, name='detalle_proyecto'),
    path('proyecto/<int:proyecto_id>/editar/', views.editar_proyecto, name='editar_proyecto'),
    path('proyecto/<int:proyecto_id>/eliminar/', views.eliminar_proyecto, name='eliminar_proyecto'),
    path('proyecto/<int:proyecto_id>/enviar/', views.enviar_proyecto, name='enviar_proyecto'),
    path('proyecto/<int:proyecto_id>/ver-aprobado/', views.ver_poa_aprobado, name='ver_poa_aprobado'),
    path('proyecto/<int:proyecto_id>/gestionar-avances/', views.gestionar_avances, name='gestionar_avances'),
    path('proyecto/<int:proyecto_id>/gestionar-evidencias/', views.gestionar_evidencias, name='gestionar_evidencias'),
    path('proyecto/<int:proyecto_id>/reportes/', views.ver_reportes, name='ver_reportes'),
    path('actividad/<int:actividad_id>/registrar-avance/', views.registrar_avance_actividad, name='registrar_avance_actividad'),
    path('actividad/<int:actividad_id>/subir-evidencia/', views.subir_evidencia_actividad, name='subir_evidencia_actividad'),
    path('meta/<int:meta_id>/eliminar/', views.eliminar_meta, name='eliminar_meta'),
    path('actividad/<int:actividad_id>/eliminar/', views.eliminar_actividad, name='eliminar_actividad'),
    path('subir-evidencia-mes/', views.subir_evidencia_mes, name='subir_evidencia_mes'),
    
    path('evidencias-mes/<int:actividad_id>/<int:mes>/', views.obtener_evidencias_mes, name='obtener_evidencias_mes'),
    path('crear-actividad-no-planificada/', views.crear_actividad_no_planificada, name='crear_actividad_no_planificada'),
]
