from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError


class FormularioLogin(forms.Form):
    """Formulario de inicio de sesión"""
    
    email = forms.EmailField(
        label='Correo electrónico',
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'correo@ejemplo.com',
            'autocomplete': 'email',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': '••••••••',
            'autocomplete': 'current-password'
        })
    )
    
    recordar = forms.BooleanField(
        label='Recordar sesión',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'checkbox checkbox-primary'
        })
    )
    
    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.usuario_cache = None
        super().__init__(*args, **kwargs)
    
    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        
        if email and password:
            self.usuario_cache = authenticate(
                self.request,
                username=email,
                password=password
            )
            
            if self.usuario_cache is None:
                raise ValidationError(
                    'Correo electrónico o contraseña incorrectos.',
                    code='invalid_login'
                )
            
            if not self.usuario_cache.is_active:
                raise ValidationError(
                    'Esta cuenta está inactiva.',
                    code='inactive'
                )
        
        return self.cleaned_data
    
    def get_usuario(self):
        return self.usuario_cache


class FormularioCambiarClave(forms.Form):
    """Formulario para cambiar contraseña"""
    
    clave_actual = forms.CharField(
        label='Contraseña actual',
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': '••••••••',
            'autocomplete': 'current-password'
        })
    )
    
    clave_nueva = forms.CharField(
        label='Nueva contraseña',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': '••••••••',
            'autocomplete': 'new-password'
        }),
        help_text='Mínimo 8 caracteres'
    )
    
    confirmar_clave = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': '••••••••',
            'autocomplete': 'new-password'
        })
    )
    
    def __init__(self, usuario, *args, **kwargs):
        self.usuario = usuario
        super().__init__(*args, **kwargs)
    
    def clean_clave_actual(self):
        clave_actual = self.cleaned_data.get('clave_actual')
        if not self.usuario.check_password(clave_actual):
            raise ValidationError('La contraseña actual es incorrecta.')
        return clave_actual
    
    def clean(self):
        cleaned_data = super().clean()
        clave_nueva = cleaned_data.get('clave_nueva')
        confirmar_clave = cleaned_data.get('confirmar_clave')
        clave_actual = cleaned_data.get('clave_actual')
        
        if clave_nueva and confirmar_clave:
            if clave_nueva != confirmar_clave:
                raise ValidationError('Las contraseñas no coinciden.')
        
        if clave_actual and clave_nueva:
            if self.usuario.check_password(clave_nueva):
                raise ValidationError(
                    'La nueva contraseña debe ser diferente a la contraseña actual.'
                )
        
        return cleaned_data
    
    def save(self):
        self.usuario.set_password(self.cleaned_data['clave_nueva'])
        self.usuario.debe_cambiar_clave = False
        self.usuario.save()
        return self.usuario
