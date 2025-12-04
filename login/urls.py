from django.urls import path
from . import views

app_name = 'login'

urlpatterns = [
    path('', views.vista_login, name='login'),
    path('logout/', views.vista_logout, name='logout'),
    path('cambiar-clave/', views.cambiar_clave, name='cambiar_clave'),
    path('dashboard/', views.redirigir_dashboard, name='redirigir_dashboard'),
    path('dashboard/auditor/', views.dashboard_auditor, name='dashboard_auditor'),
    path('dashboard/unidad/', views.dashboard_unidad, name='dashboard_unidad'),
]
