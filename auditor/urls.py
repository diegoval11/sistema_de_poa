from django.urls import path
from . import views

app_name = 'auditor'

urlpatterns = [
    path('', views.dashboard_auditor, name='dashboard'),
    path('estadisticas/', views.estadisticas_auditor, name='estadisticas'),
    path('usuarios/', views.ver_usuarios, name='ver_usuarios'),
    path('logs/', views.ver_logs, name='ver_logs'),
    path('proyectos/', views.ver_proyectos, name='ver_proyectos'),
    path('proyectos/<int:proyecto_id>/', views.detalle_proyecto_auditor, name='detalle_proyecto'),
    path('unidades/', views.ver_unidades, name='ver_unidades'),
    
    # Exportación de estadísticas
    path('exportar/estadisticas/pdf/', views.exportar_estadisticas_pdf, name='exportar_estadisticas_pdf'),
    path('exportar/estadisticas/excel/', views.exportar_estadisticas_excel, name='exportar_estadisticas_excel'),
    
    # Exportación de unidades
    path('exportar/unidades/pdf/', views.exportar_unidades_pdf, name='exportar_unidades_pdf'),
    path('exportar/unidades/excel/', views.exportar_unidades_excel, name='exportar_unidades_excel'),
    
    # Exportación de proyectos
    path('exportar/proyectos/pdf/', views.exportar_proyectos_pdf, name='exportar_proyectos_pdf'),
    path('exportar/proyectos/excel/', views.exportar_proyectos_excel, name='exportar_proyectos_excel'),
    
    # Exportación de usuarios
    path('exportar/usuarios/pdf/', views.exportar_usuarios_pdf, name='exportar_usuarios_pdf'),
    path('exportar/usuarios/excel/', views.exportar_usuarios_excel, name='exportar_usuarios_excel'),
    
    path('exportar/logs/pdf/', views.exportar_logs_pdf, name='exportar_logs_pdf'),
    path('exportar/logs/excel/', views.exportar_logs_excel, name='exportar_logs_excel'),
    
    path('exportar/proyecto/<int:proyecto_id>/pdf/', views.exportar_proyecto_detalle_pdf, name='exportar_proyecto_detalle_pdf'),
    path('exportar/proyecto/<int:proyecto_id>/excel/', views.exportar_proyecto_detalle_excel, name='exportar_proyecto_detalle_excel'),
    path('exportar/reporte-trimestral/pdf/', 
         views.exportar_reporte_trimestral_pdf, 
         name='exportar_reporte_trimestral_pdf'),
         
    path('exportar/reporte-trimestral/excel/', 
         views.exportar_reporte_trimestral_excel, 
         name='exportar_reporte_trimestral_excel'),
]
