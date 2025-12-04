from django.urls import path
from . import views

app_name = 'administrador'

urlpatterns = [
    path('', views.dashboard_admin, name='dashboard'),
    path('estadisticas/', views.estadisticas_admin, name='estadisticas'),
    path('unidades/', views.lista_unidades, name='lista_unidades'),
    path('unidades/exportar/pdf/', views.exportar_unidades_pdf, name='exportar_unidades_pdf'),
    path('unidades/exportar/excel/', views.exportar_unidades_excel, name='exportar_unidades_excel'),
    path('unidades/<int:unidad_id>/proyectos/', views.proyectos_unidad, name='proyectos_unidad'),
    path('proyectos/<int:proyecto_id>/', views.detalle_proyecto_admin, name='detalle_proyecto_admin'),
    path('proyectos/<int:proyecto_id>/aprobar/', views.aprobar_proyecto, name='aprobar_proyecto'),
    path('proyectos/<int:proyecto_id>/rechazar/', views.rechazar_proyecto, name='rechazar_proyecto'),
    path('proyectos/<int:proyecto_id>/editar/', views.editar_proyecto_admin, name='editar_proyecto_admin'),
    path('proyectos/<int:proyecto_id>/exportar/pdf/', views.exportar_proyecto_detalle_pdf, name='exportar_proyecto_detalle_pdf'),
    path('proyectos/<int:proyecto_id>/exportar/excel/', views.exportar_proyecto_detalle_excel, name='exportar_proyecto_detalle_excel'),
    path('api/buscar-unidades/', views.buscar_unidades_ajax, name='buscar_unidades_ajax'),
    path('exportar/reporte-trimestral/pdf/', 
         views.exportar_reporte_trimestral_pdf, 
         name='exportar_reporte_trimestral_pdf'),
         
    path('exportar/reporte-trimestral/excel/', 
         views.exportar_reporte_trimestral_excel, 
         name='exportar_reporte_trimestral_excel'),
         
    # Metas predeterminadas
    path('metas-predeterminadas/', views.lista_metas_predeterminadas, name='lista_metas_predeterminadas'),
    path('metas-predeterminadas/crear/', views.crear_meta_predeterminada, name='crear_meta_predeterminada'),
    path('metas-predeterminadas/<int:meta_id>/editar/', views.editar_meta_predeterminada, name='editar_meta_predeterminada'),
    path('metas-predeterminadas/<int:meta_id>/eliminar/', views.eliminar_meta_predeterminada, name='eliminar_meta_predeterminada'),
    
    # URLs para Objetivos Estratégicos
    path('objetivos-estrategicos/', views.lista_objetivos_estrategicos, name='lista_objetivos_estrategicos'),
    path('objetivos-estrategicos/crear/', views.crear_objetivo_estrategico, name='crear_objetivo_estrategico'),
    path('objetivos-estrategicos/editar/<int:objetivo_id>/', views.editar_objetivo_estrategico, name='editar_objetivo_estrategico'),
    path('objetivos-estrategicos/eliminar/<int:objetivo_id>/', views.eliminar_objetivo_estrategico, name='eliminar_objetivo_estrategico'),
    
    # URL para exportar proyectos a Excel
    path('unidades/<int:unidad_id>/proyectos/exportar/', views.exportar_proyectos_unidad, name='exportar_proyectos_unidad'),
]
