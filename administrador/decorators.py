from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def admin_required(view_func):
    """
    Decorator que verifica que el usuario sea administrador.
    Redirige al dashboard correspondiente si no tiene permisos.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para acceder a esta sección.')
            return redirect('login:login')
        
        if request.user.rol != 'ADMIN':
            messages.error(request, 'No tienes permisos para acceder a esta sección. Solo administradores.')
            return redirect('login:redirigir_dashboard')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
