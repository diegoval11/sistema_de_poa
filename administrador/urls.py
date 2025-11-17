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
]
