from django.shortcuts import redirect
from django.urls import reverse


class CambiarClaveMiddleware:
    """Middleware que fuerza al usuario a cambiar su contraseña si es necesario"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            urls_permitidas = [
                reverse('login:cambiar_clave'),
                reverse('login:logout'),
                reverse('login:login'),
            ]
            
            if (request.user.debe_cambiar_clave and 
                request.path not in urls_permitidas and
                not request.path.startswith('/admin/')):
                return redirect('login:cambiar_clave')
        
        response = self.get_response(request)
        return response
