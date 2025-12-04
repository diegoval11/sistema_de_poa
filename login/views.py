from decimal import Decimal
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse

from poa.models import AvanceMensual, Proyecto
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
    if request.user.rol != 'UNIDAD':
        return redirect('login:login')
    
    # Obtener todos los proyectos de la unidad
    proyectos = Proyecto.objects.filter(unidad__unidad=request.user.unidad).order_by('-anio', '-fecha_modificacion')
    
    # Estadísticas
    total_proyectos = proyectos.count()
    proyectos_aprobados = proyectos.filter(estado='APROBADO').count()
    proyectos_revision = proyectos.filter(estado='ENVIADO').count()
    proyectos_borrador = proyectos.filter(estado__in=['BORRADOR', 'RECHAZADO']).count()
    
    # Cálculo de cumplimiento global (solo de proyectos aprobados)
    cumplimiento_global = Decimal(0)
    proyectos_aprobados_qs = proyectos.filter(estado='APROBADO')
    
    total_programado_global = 0
    total_realizado_global = 0
    
    if proyectos_aprobados_qs.exists():
        # Obtener todos los avances de los proyectos aprobados
        avances = AvanceMensual.objects.filter(actividad__meta__proyecto__in=proyectos_aprobados_qs)
        
        for avance in avances:
            prog = avance.cantidad_programada_mes or 0
            real = avance.cantidad_realizada or 0
            # Solo sumamos lo realizado hasta el tope de lo programado para el % de cumplimiento
            # (aunque el dato real se guarde completo)
            total_programado_global += prog
            total_realizado_global += min(real, prog)
            
        if total_programado_global > 0:
            cumplimiento_global = (Decimal(total_realizado_global) / Decimal(total_programado_global)) * 100
            cumplimiento_global = round(cumplimiento_global, 1)

    # Proyectos recientes (para la lista rápida)
    proyectos_recientes = proyectos[:5]
    
    context = {
        'unidad': request.user.unidad,
        'titulo': 'Panel de Control',
        'total_proyectos': total_proyectos,
        'proyectos_aprobados': proyectos_aprobados,
        'proyectos_revision': proyectos_revision,
        'proyectos_borrador': proyectos_borrador,
        'cumplimiento_global': cumplimiento_global,
        'proyectos_recientes': proyectos_recientes,
        'tiene_proyectos': total_proyectos > 0
    }
    
    return render(request, 'poa/dashboard_unidad.html', context)

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
