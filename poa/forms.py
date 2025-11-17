from django import forms
from django.core.validators import MaxValueValidator
from .models import Proyecto, MetaProyecto, Actividad, AvanceMensual, Evidencia


class FormularioProyecto(forms.ModelForm):
    """Formulario para crear/editar proyectos"""
    
    class Meta:
        model = Proyecto
        fields = ['nombre', 'objetivo_unidad', 'anio']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Nombre del proyecto...',
                'required': True,
            }),
            'objetivo_unidad': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3,
                'placeholder': 'Describa el objetivo de la unidad...',
            }),
            'anio': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': '2025',
                'min': '2000',
                'max': '2100',
                'required': True,
            }),
        }
        labels = {
            'nombre': 'Nombre del Proyecto',
            'objetivo_unidad': 'Objetivo de la Unidad',
            'anio': 'Año',
        }


class FormularioMeta(forms.ModelForm):
    """Formulario para crear/editar metas"""
    
    class Meta:
        model = MetaProyecto
        fields = ['descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 2,
                'placeholder': 'Descripción de la meta...',
                'required': True,
            }),
        }
        labels = {
            'descripcion': 'Descripción de la Meta',
        }


class FormularioActividad(forms.ModelForm):
    """Formulario para crear/editar actividades"""
    
    UNIDADES_MEDIDA = [
        ('', 'Seleccione una unidad de medida'),
        ('Unidad', 'Unidad'),
        ('Porcentaje', 'Porcentaje'),
        ('Documento', 'Documento'),
        ('Informe', 'Informe'),
        ('Evento', 'Evento'),
        ('Persona', 'Persona'),
        ('Reunión', 'Reunión'),
        ('Capacitación', 'Capacitación'),
        ('Taller', 'Taller'),
        ('Proyecto', 'Proyecto'),
        ('Actividad', 'Actividad'),
        ('Servicio', 'Servicio'),
        ('Producto', 'Producto'),
        ('Otro', 'Otro (especificar)'),
    ]
    
    unidad_medida_select = forms.ChoiceField(
        choices=UNIDADES_MEDIDA,
        required=False,
        widget=forms.Select(attrs={
            'class': 'select select-bordered w-full',
            'id': 'id_unidad_medida_select',
        }),
        label='Unidad de Medida'
    )
    
    unidad_medida_otro = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Especifique la unidad de medida...',
            'id': 'id_unidad_medida_otro',
        }),
        label='Especificar Unidad de Medida'
    )
    
    class Meta:
        model = Actividad
        fields = [
            'descripcion', 
            'cantidad_programada',
            'es_cuantificable', 
            'medio_verificacion',
            'recursos',
            'total_recursos',
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 2,
                'placeholder': 'Descripción de la actividad...',
                'required': True,
            }),
            'cantidad_programada': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': '0',
                'min': '0',
                'max': '999999',
                'id': 'id_cantidad_programada',
            }),
            'es_cuantificable': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary',
                'id': 'id_es_cuantificable',
            }),
            'medio_verificacion': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 2,
                'placeholder': 'Medio de verificación...',
            }),
            'recursos': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 2,
                'placeholder': 'Recursos necesarios...',
            }),
            'total_recursos': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'max': '99999999.99',
            }),
        }
        labels = {
            'descripcion': 'Descripción de la Actividad',
            'cantidad_programada': 'Cantidad Programada Total',
            'es_cuantificable': '¿Es Cuantificable?',
            'medio_verificacion': 'Medio de Verificación',
            'recursos': 'Recursos',
            'total_recursos': 'Total de Recursos ($)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cantidad_programada'].required = False
        
        if self.instance and self.instance.pk:
            unidad = self.instance.unidad_medida
            if unidad in dict(self.UNIDADES_MEDIDA):
                self.fields['unidad_medida_select'].initial = unidad
            else:
                self.fields['unidad_medida_select'].initial = 'Otro'
                self.fields['unidad_medida_otro'].initial = unidad
    
    def clean(self):
        cleaned_data = super().clean()
        unidad_select = cleaned_data.get('unidad_medida_select')
        unidad_otro = cleaned_data.get('unidad_medida_otro')
        cantidad_programada = cleaned_data.get('cantidad_programada')
        es_cuantificable = cleaned_data.get('es_cuantificable')
        
        # Validar unidad de medida
        if unidad_select == 'Otro':
            if not unidad_otro:
                self.add_error('unidad_medida_otro', 'Debe especificar la unidad de medida cuando selecciona "Otro".')
            else:
                cleaned_data['unidad_medida'] = unidad_otro
        elif unidad_select:
            cleaned_data['unidad_medida'] = unidad_select
        else:
            self.add_error('unidad_medida_select', 'Debe seleccionar una unidad de medida.')
        
        if es_cuantificable:
            # Cuando es cuantificable, cantidad_programada es obligatoria
            if cantidad_programada is None or cantidad_programada <= 0:
                self.add_error('cantidad_programada', 'La cantidad programada debe ser mayor a 0 cuando la actividad es cuantificable.')
            elif cantidad_programada > 999999:
                self.add_error('cantidad_programada', 'La cantidad programada no puede ser mayor a 999,999.')
        else:
            # Si no es cuantificable, establecer cantidad en 0
            cleaned_data['cantidad_programada'] = 0
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.unidad_medida = self.cleaned_data.get('unidad_medida')
        if commit:
            instance.save()
        return instance


class FormularioAvanceMensual(forms.ModelForm):
    """Formulario para avance mensual"""
    
    class Meta:
        model = AvanceMensual
        fields = ['mes', 'anio', 'cantidad_programada_mes', 'cantidad_realizada', 'causal_incumplimiento', 'es_no_planificada']
        widgets = {
            'mes': forms.Select(attrs={
                'class': 'select select-bordered select-sm w-full',
            }),
            'anio': forms.NumberInput(attrs={
                'class': 'input input-bordered input-sm w-full',
                'min': '2000',
                'max': '2100',
            }),
            'cantidad_programada_mes': forms.NumberInput(attrs={
                'class': 'input input-bordered input-sm w-full',
                'min': '0',
                'max': '999999',
            }),
            'cantidad_realizada': forms.NumberInput(attrs={
                'class': 'input input-bordered input-sm w-full',
                'min': '0',
                'max': '999999',
            }),
            'causal_incumplimiento': forms.TextInput(attrs={
                'class': 'input input-bordered input-sm w-full',
                'placeholder': 'Causa de incumplimiento...',
            }),
            'es_no_planificada': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-sm checkbox-primary',
            }),
        }


class FormularioEvidencia(forms.ModelForm):
    """Formulario para evidencias"""
    
    class Meta:
        model = Evidencia
        fields = ['tipo', 'archivo', 'url', 'descripcion', 'mes']
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'select select-bordered w-full',
            }),
            'archivo': forms.FileInput(attrs={
                'class': 'file-input file-input-bordered w-full',
            }),
            'url': forms.URLInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'https://...',
            }),
            'descripcion': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Descripción de la evidencia...',
            }),
            'mes': forms.Select(attrs={
                'class': 'select select-bordered w-full',
            }),
        }
        labels = {
            'tipo': 'Tipo de Evidencia',
            'archivo': 'Archivo',
            'url': 'URL',
            'descripcion': 'Descripción',
            'mes': 'Mes (opcional)',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        archivo = cleaned_data.get('archivo')
        url = cleaned_data.get('url')
        
        if tipo == 'URL':
            if not url:
                raise forms.ValidationError('Debe proporcionar una URL para este tipo de evidencia.')
        else:
            if not archivo:
                raise forms.ValidationError('Debe proporcionar un archivo para este tipo de evidencia.')
        
        return cleaned_data
