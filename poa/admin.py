from django.contrib import admin
from .models import Proyecto, MetaProyecto, Actividad, AvanceMensual, Evidencia, AuditoriaLog


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'unidad', 'anio', 'fecha_creacion']
    list_filter = ['anio', 'unidad']
    search_fields = ['nombre', 'objetivo_unidad']
    readonly_fields = ['fecha_creacion']


@admin.register(MetaProyecto)
class MetaProyectoAdmin(admin.ModelAdmin):
    list_display = ['id', 'proyecto', 'descripcion_corta']
    list_filter = ['proyecto__anio']
    search_fields = ['descripcion', 'proyecto__nombre']
    
    def descripcion_corta(self, obj):
        return obj.descripcion[:50] + '...' if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = 'Descripción'


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ['id', 'meta', 'unidad_medida', 'cantidad_programada', 'es_cuantificable', 'total_recursos']
    list_filter = ['es_cuantificable', 'meta__proyecto__anio']
    search_fields = ['descripcion', 'meta__proyecto__nombre']
    readonly_fields = ['fecha_creacion']


@admin.register(AvanceMensual)
class AvanceMensualAdmin(admin.ModelAdmin):
    list_display = ['actividad', 'mes', 'anio', 'cantidad_programada_mes', 'cantidad_realizada', 'cumplimiento']
    list_filter = ['mes', 'anio', 'es_no_planificada']
    search_fields = ['actividad__descripcion']
    readonly_fields = ['cumplimiento', 'fecha_actualizacion']


@admin.register(Evidencia)
class EvidenciaAdmin(admin.ModelAdmin):
    list_display = ['actividad', 'tipo', 'mes', 'descripcion', 'fecha_subida']
    list_filter = ['tipo', 'mes', 'fecha_subida']
    search_fields = ['descripcion', 'actividad__descripcion']
    readonly_fields = ['fecha_subida']


@admin.register(AuditoriaLog)
class AuditoriaLogAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'accion', 'tabla', 'fecha', 'ip']
    list_filter = ['accion', 'tabla', 'fecha']
    readonly_fields = ['usuario', 'accion', 'tabla', 'registro_id', 'datos_anteriores', 'datos_nuevos', 'fecha', 'ip']
    search_fields = ['usuario__email', 'tabla', 'accion']
