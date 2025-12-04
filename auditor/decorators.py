from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def auditor_required(view_func):
    """
    Decorator para verificar que el usuario sea un auditor.
    Los auditores tienen acceso de solo lectura a todo el sistema.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debe iniciar sesión para acceder a esta página.')
            return redirect('login:login')
        
        if request.user.rol != 'AUDITOR':
            messages.error(request, 'No tiene permisos para acceder a esta sección.')
            return redirect('login:redirigir_dashboard')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
