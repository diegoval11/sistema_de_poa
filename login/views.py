from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from .forms import FormularioLogin, FormularioCambiarClave


def vista_login(request):
    """Vista para el inicio de sesión"""
    
    # Si el usuario ya está autenticado, redirigir al dashboard correspondiente
    if request.user.is_authenticated:
        return redirect('login:redirigir_dashboard')
    
    if request.method == 'POST':
        formulario = FormularioLogin(request, data=request.POST)
        
        if formulario.is_valid():
            usuario = formulario.get_usuario()
            recordar = formulario.cleaned_data.get('recordar')
            
            # Configurar duración de sesión
            if not recordar:
                request.session.set_expiry(0)  # Expira al cerrar navegador
            
            login(request, usuario)
            
            # Verificar si debe cambiar contraseña
            if usuario.debe_cambiar_clave:
                messages.warning(request, 'Debe cambiar su contraseña antes de continuar.')
                return redirect('login:cambiar_clave')
            
            messages.success(request, f'Bienvenido, {usuario.email}')
            
            # Redirigir al dashboard correspondiente
            siguiente = request.GET.get('next')
            if siguiente:
                return redirect(siguiente)
            return redirect('login:redirigir_dashboard')
    else:
        formulario = FormularioLogin()
    
    contexto = {
        'formulario': formulario,
        'titulo': 'Iniciar Sesión'
    }
    
    return render(request, 'login/login.html', contexto)


@login_required
def vista_logout(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.info(request, 'Ha cerrado sesión correctamente.')
    return redirect('login:login')


@login_required
def redirigir_dashboard(request):
    """Redirige al dashboard correspondiente según el rol del usuario"""
    usuario = request.user
    
    if usuario.rol == 'ADMIN':
        return redirect('administrador:dashboard')
    elif usuario.rol == 'AUDITOR':
        return redirect('auditor:dashboard')
    else:  # UNIDAD
        return redirect('login:dashboard_unidad')


@login_required
def dashboard_auditor(request):
    """Dashboard para auditores"""
    contexto = {
        'titulo': 'Panel de Auditoría',
        'rol': 'Auditor'
    }
    return render(request, 'login/dashboard_auditor.html', contexto)


@login_required
def dashboard_unidad(request):
    """Dashboard para unidades"""
    from poa.models import Proyecto
    
    poa_aprobado = Proyecto.objects.filter(
        unidad__unidad=request.user.unidad,
        estado='APROBADO'
    ).first()
    
    contexto = {
        'titulo': 'Panel de Unidad',
        'rol': 'Unidad',
        'unidad': request.user.unidad,
        'poa_aprobado': poa_aprobado
    }
    
    # Si tiene POA aprobado, agregar estadísticas
    if poa_aprobado:
        from django.db.models import Count, Sum, Avg
        
        # Contar actividades
        total_actividades = poa_aprobado.metas.aggregate(
            total=Count('actividades')
        )['total'] or 0
        
        # Calcular cumplimiento promedio
        from poa.models import AvanceMensual
        cumplimiento_promedio = AvanceMensual.objects.filter(
            actividad__meta__proyecto=poa_aprobado
        ).aggregate(
            promedio=Avg('cumplimiento')
        )['promedio'] or 0
        
        # Contar evidencias
        from poa.models import Evidencia
        total_evidencias = Evidencia.objects.filter(
            actividad__meta__proyecto=poa_aprobado
        ).count()
        
        contexto.update({
            'total_actividades': total_actividades,
            'cumplimiento_promedio': round(cumplimiento_promedio, 2),
            'total_evidencias': total_evidencias
        })
    
    return render(request, 'poa/dashboard_unidad.html', contexto)


@login_required
def cambiar_clave(request):
    """Vista para cambiar contraseña"""
    
    if request.method == 'POST':
        formulario = FormularioCambiarClave(request.user, data=request.POST)
        
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Contraseña cambiada exitosamente.')
            
            # Volver a autenticar al usuario con la nueva contraseña
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
            
            return redirect('login:redirigir_dashboard')
    else:
        formulario = FormularioCambiarClave(request.user)
    
    contexto = {
        'formulario': formulario,
        'titulo': 'Cambiar Contraseña',
        'obligatorio': request.user.debe_cambiar_clave
    }
    
    return render(request, 'login/cambiar_clave.html', contexto)
