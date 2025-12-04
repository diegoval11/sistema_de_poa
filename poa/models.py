from decimal import Decimal, InvalidOperation
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from login.models import Usuario


class Proyecto(models.Model):
    """Modelo para los proyectos de una unidad"""
    ESTADOS = [
        ('BORRADOR', 'Borrador'),
        ('ENVIADO', 'Enviado'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
    ]
    
    unidad = models.ForeignKey(
        Usuario, 
        on_delete=models.PROTECT, 
        verbose_name='Unidad',
        related_name='proyectos',
        limit_choices_to={'rol': 'UNIDAD'}
    )
    nombre = models.CharField(max_length=200, verbose_name='Nombre del Proyecto', blank=True, null=True)
    objetivo_unidad = models.CharField(max_length=1000, verbose_name='Objetivo de la Unidad', blank=True)
    anio = models.IntegerField(
        default=2025, 
        verbose_name='Año', 
        validators=[MinValueValidator(2000), MaxValueValidator(2100)]
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='BORRADOR',
        verbose_name='Estado'
    )
    aprobado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='proyectos_aprobados',
        limit_choices_to={'rol': 'ADMIN'},
        verbose_name='Aprobado por'
    )
    fecha_aprobacion = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Aprobación')
    motivo_rechazo = models.CharField(max_length=1000, blank=True, verbose_name='Motivo de Rechazo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Última Modificación')
    es_no_planificado = models.BooleanField(default=False, verbose_name='Es Proyecto No Planificado')
    
    class Meta:
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'
        ordering = ['-anio', 'unidad__unidad__nombre', 'id']
    
    def __str__(self):
        return f"{self.nombre} ({self.anio})"
    
    def es_editable_por_unidad(self):
        """Verifica si el proyecto puede ser editado por la unidad"""
        return self.estado in ['BORRADOR', 'RECHAZADO']
    
    def puede_ser_enviado(self):
        """Verifica si el proyecto puede ser enviado para revisión"""
        return self.estado == 'BORRADOR' and self.metas.exists()


class MetaProyecto(models.Model):
    """Modelo para las metas de un proyecto"""
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='metas', verbose_name='Proyecto')
    descripcion = models.CharField(max_length=200, verbose_name='Descripción de la Meta')
    
    class Meta:
        verbose_name = 'Meta'
        verbose_name_plural = 'Metas'
        ordering = ['proyecto', 'id']
    
    def __str__(self):
        return f"Meta {self.id} - {self.proyecto.nombre}"


class MetaPredeterminada(models.Model):
    """Modelo para metas predeterminadas configurables por el administrador"""
    nombre = models.CharField(max_length=200, verbose_name='Nombre de la Meta')
    activa = models.BooleanField(default=True, verbose_name='Activa')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Meta Predeterminada'
        verbose_name_plural = 'Metas Predeterminadas'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class ObjetivoEstrategico(models.Model):
    """Modelo para los objetivos estratégicos definidos por el administrador"""
    descripcion = models.TextField(verbose_name='Descripción del Objetivo')
    activa = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')

    class Meta:
        verbose_name = 'Objetivo Estratégico'
        verbose_name_plural = 'Objetivos Estratégicos'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.descripcion[:50]


class Actividad(models.Model):
    """Modelo para las actividades de una meta"""
    meta = models.ForeignKey(MetaProyecto, on_delete=models.CASCADE, related_name='actividades', verbose_name='Meta')
    descripcion = models.CharField(max_length=500, verbose_name='Descripción de la Actividad')
    unidad_medida = models.CharField(max_length=80, verbose_name='Unidad de Medida')
    cantidad_programada = models.IntegerField(
        default=0,
        verbose_name='Cantidad Programada',
        validators=[MinValueValidator(0), MaxValueValidator(999999)]
    )
    es_cuantificable = models.BooleanField(default=True, verbose_name='Es Cuantificable')
    medio_verificacion = models.CharField(max_length=500, verbose_name='Medio de Verificación')
    recursos = models.CharField(max_length=500, blank=True, verbose_name='Recursos')
    total_recursos = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Total Recursos (Bs.)',
        validators=[MinValueValidator(0), MaxValueValidator(99999999.99)]
    )
    observaciones = models.CharField(max_length=500, blank=True, verbose_name='Observaciones')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    
    class Meta:
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'
        ordering = ['meta', 'id']
    
    def __str__(self):
        return f"Actividad {self.id} - {self.meta.proyecto.nombre}"


class AvanceMensual(models.Model):
    """Modelo para el avance mensual de una actividad"""
    MESES = [
        (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
        (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
        (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre'),
    ]
    
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, related_name='avances', verbose_name='Actividad')
    mes = models.IntegerField(choices=MESES, verbose_name='Mes')
    anio = models.IntegerField(
        default=2025, 
        verbose_name='Año',
        validators=[MinValueValidator(2000), MaxValueValidator(2100)]
    )
    cantidad_programada_mes = models.IntegerField(
        default=0, 
        verbose_name='Cantidad Programada', 
        validators=[MinValueValidator(0), MaxValueValidator(999999)]
    )
    cantidad_realizada = models.IntegerField(
        default=0, 
        verbose_name='Cantidad Realizada', 
        validators=[MinValueValidator(0), MaxValueValidator(999999)]
    )

    cumplimiento = models.DecimalField(
    max_digits=5,
    decimal_places=2,
    null=True,     
    blank=True,    
    verbose_name='Cumplimiento %',
    editable=False
)



    causal_incumplimiento = models.CharField(max_length=500, blank=True, verbose_name='Causal de Incumplimiento')
    es_no_planificada = models.BooleanField(default=False, verbose_name='Es No Planificada')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    
    class Meta:
        verbose_name = 'Avance Mensual'
        verbose_name_plural = 'Avances Mensuales'
        unique_together = ['actividad', 'mes', 'anio']
        ordering = ['actividad', 'anio', 'mes']
    

    def calcular_cumplimiento(self):
        """
        Calcula el porcentaje de cumplimiento
        - Si no hay programación, el cumplimiento NO SE CALCULA -> se marca como None
        """
        try:
            if self.cantidad_programada_mes > 0:
                cantidad_para_calculo = min(self.cantidad_realizada, self.cantidad_programada_mes)
                porcentaje = (Decimal(cantidad_para_calculo) / Decimal(self.cantidad_programada_mes)) * 100
                self.cumplimiento = min(round(porcentaje, 2), Decimal('100.00'))
            else:
                # NO SE CALCULA → "No aplica"
                self.cumplimiento = None
        except (InvalidOperation, Exception):
            self.cumplimiento = None

    
    def save(self, *args, **kwargs):
        self.calcular_cumplimiento()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.actividad} - {self.get_mes_display()} {self.anio}"


class Evidencia(models.Model):
    """Modelo para evidencias de actividades"""
    TIPOS = [
        ('PDF', 'PDF'),
        ('FOTO', 'Foto'),
        ('VIDEO', 'Video'),
        ('URL', 'URL'),
        ('MP3', 'Audio MP3'),
    ]
    
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, related_name='evidencias', verbose_name='Actividad')
    tipo = models.CharField(max_length=10, choices=TIPOS, verbose_name='Tipo')
    archivo = models.FileField(upload_to='evidencias/%Y/%m/', null=True, blank=True, verbose_name='Archivo')
    url = models.URLField(max_length=500, null=True, blank=True, verbose_name='URL')
    descripcion = models.CharField(max_length=200, blank=True, verbose_name='Descripción')
    mes = models.IntegerField(
        null=True, 
        blank=True, 
        choices=AvanceMensual.MESES,
        verbose_name='Mes'
    )
    fecha_subida = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Subida')
    
    class Meta:
        verbose_name = 'Evidencia'
        verbose_name_plural = 'Evidencias'
        ordering = ['-fecha_subida']
    
    def __str__(self):
        return f"{self.tipo} - {self.actividad}"


class AuditoriaLog(models.Model):
    """Modelo para auditoría de cambios"""
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, verbose_name='Usuario')
    accion = models.CharField(max_length=50, verbose_name='Acción')
    tabla = models.CharField(max_length=50, verbose_name='Tabla')
    registro_id = models.IntegerField(verbose_name='ID del Registro')
    datos_anteriores = models.JSONField(null=True, blank=True, verbose_name='Datos Anteriores')
    datos_nuevos = models.JSONField(null=True, blank=True, verbose_name='Datos Nuevos')
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')
    ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='Dirección IP')
    
    class Meta:
        verbose_name = 'Log de Auditoría'
        verbose_name_plural = 'Logs de Auditoría'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.accion} - {self.tabla} - {self.fecha}"











