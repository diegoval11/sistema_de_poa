from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from .models import Proyecto, MetaProyecto, Actividad, AvanceMensual, Evidencia
from .forms import FormularioProyecto, FormularioMeta, FormularioActividad, FormularioAvanceMensual, FormularioEvidencia
import json


@login_required
def lista_proyectos(request):
    """Vista para listar los proyectos de la unidad del usuario"""
    if request.user.rol == 'UNIDAD':
        proyectos = Proyecto.objects.filter(unidad__unidad=request.user.unidad).prefetch_related('metas__actividades')
        tiene_poa_aprobado = proyectos.filter(estado='APROBADO').exists()
    else:
        proyectos = Proyecto.objects.all().prefetch_related('metas__actividades')
        tiene_poa_aprobado = False
    
    for proyecto in proyectos:
        proyecto.total_actividades = sum(meta.actividades.count() for meta in proyecto.metas.all())
    
    return render(request, 'poa/lista_proyectos.html', {
        'proyectos': proyectos,
        'tiene_poa_aprobado': tiene_poa_aprobado,
    })


@login_required
def crear_proyecto_wizard(request):
    """Vista para crear un nuevo proyecto con wizard de pasos"""
    if request.user.rol != 'UNIDAD':
        messages.error(request, 'Solo los usuarios de unidad pueden crear proyectos.')
        return redirect('poa:lista_proyectos')
    
    poa_aprobado = Proyecto.objects.filter(
        unidad__unidad=request.user.unidad,
        estado='APROBADO'
    ).exists()
    
    if poa_aprobado:
        messages.error(request, 'Su unidad ya tiene un POA aprobado. No puede crear un nuevo POA mientras tenga uno aprobado.')
        return redirect('login:dashboard_unidad')
    
    # Obtener el paso actual del wizard desde la sesión
    paso_actual = int(request.session.get('wizard_paso', 1))
    proyecto_id = request.session.get('wizard_proyecto_id')
    
    # Recuperar el proyecto si existe
    proyecto = None
    if proyecto_id:
        proyecto = Proyecto.objects.filter(id=proyecto_id, unidad=request.user).first()
    
    context = {
        'paso_actual': paso_actual,
        'proyecto': proyecto,
    }
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        # Paso 1: Información del Proyecto
        if paso_actual == 1:
            if accion == 'siguiente':
                formulario = FormularioProyecto(request.POST, instance=proyecto)
                if formulario.is_valid():
                    proyecto = formulario.save(commit=False)
                    proyecto.unidad = request.user
                    proyecto.save()
                    request.session['wizard_proyecto_id'] = proyecto.id
                    request.session['wizard_paso'] = 2
                    messages.success(request, 'Información del proyecto guardada. Ahora agregue las metas.')
                    return redirect('poa:crear_proyecto_wizard')
                else:
                    context['formulario_proyecto'] = formulario
            
        # Paso 2: Agregar Metas
        elif paso_actual == 2:
            if accion == 'agregar_meta':
                formulario = FormularioMeta(request.POST)
                if formulario.is_valid():
                    meta = formulario.save(commit=False)
                    meta.proyecto = proyecto
                    meta.save()
                    messages.success(request, 'Meta agregada exitosamente.')
                    return redirect('poa:crear_proyecto_wizard')
            elif accion == 'siguiente':
                if proyecto.metas.count() > 0:
                    request.session['wizard_paso'] = 3
                    return redirect('poa:crear_proyecto_wizard')
                else:
                    messages.warning(request, 'Debe agregar al menos una meta antes de continuar.')
            elif accion == 'anterior':
                request.session['wizard_paso'] = 1
                return redirect('poa:crear_proyecto_wizard')
        
        # Paso 3: Agregar Actividades
        elif paso_actual == 3:
            if accion == 'agregar_actividad':
                meta_id = request.POST.get('meta_id')
                formulario = FormularioActividad(request.POST)
                if formulario.is_valid() and meta_id:
                    meta = get_object_or_404(MetaProyecto, id=meta_id, proyecto=proyecto)
                    actividad = formulario.save(commit=False)
                    actividad.meta = meta
                    actividad.save()
                    
                    # Crear avances mensuales automáticamente
                    for mes in range(1, 13):
                        AvanceMensual.objects.get_or_create(
                            actividad=actividad,
                            mes=mes,
                            anio=proyecto.anio,
                            defaults={'cantidad_programada_mes': 0, 'cantidad_realizada': 0}
                        )
                    
                    messages.success(request, 'Actividad agregada exitosamente.')
                    return redirect('poa:crear_proyecto_wizard')
                else:
                    if not formulario.is_valid():
                        for field, errors in formulario.errors.items():
                            for error in errors:
                                messages.error(request, f'{field}: {error}')
            elif accion == 'siguiente':
                metas_sin_actividades = []
                for meta in proyecto.metas.all():
                    if meta.actividades.count() == 0:
                        metas_sin_actividades.append(meta.descripcion)

                if metas_sin_actividades:
                    # Crear mensaje de error detallado
                    if len(metas_sin_actividades) == 1:
                        mensaje = f'La meta "{metas_sin_actividades[0]}" no tiene actividades. Debe agregar al menos una actividad para cada meta antes de continuar.'
                    else:
                        # Formatear la lista de metas sin usar backslash dentro del f-string
                        metas_formateadas = ', '.join([f'"{m}"' for m in metas_sin_actividades])
                        mensaje = f'Las siguientes metas no tienen actividades: {metas_formateadas}. Debe agregar al menos una actividad para cada meta antes de continuar.'
                    messages.warning(request, mensaje)
                else:
                    # Todo correcto, avanzar al siguiente paso
                    request.session['wizard_paso'] = 4
                    return redirect('poa:crear_proyecto_wizard')
            elif accion == 'anterior':
                request.session['wizard_paso'] = 2
                return redirect('poa:crear_proyecto_wizard')
        
        # Paso 4: Programación Mensual
        elif paso_actual == 4:
            if accion == 'guardar_programacion':
                actividad_id = request.POST.get('actividad_id')
                actividad = get_object_or_404(Actividad, id=actividad_id, meta__proyecto=proyecto)

                suma_programacion = 0
                for mes in range(1, 13):
                    cantidad = request.POST.get(f'mes_{mes}', 0)
                    try:
                        cantidad_int = int(cantidad) if cantidad else 0
                        
                        if cantidad_int > 999999:
                            messages.error(request, f'La cantidad del mes {mes} no puede exceder 999,999 unidades.')
                            return redirect('poa:crear_proyecto_wizard')
                        
                        suma_programacion += cantidad_int
                    except ValueError:
                        cantidad_int = 0
                    except OverflowError:
                        messages.error(request, f'El número ingresado para el mes {mes} es demasiado grande.')
                        return redirect('poa:crear_proyecto_wizard')

                if suma_programacion > actividad.cantidad_programada:
                    messages.error(
                        request,
                        f'La suma de programación mensual ({suma_programacion}) no puede exceder '
                        f'la cantidad programada total ({actividad.cantidad_programada}).'
                    )
                    return redirect('poa:crear_proyecto_wizard')

                # Guardar programación para cada mes
                for mes in range(1, 13):
                    cantidad = request.POST.get(f'mes_{mes}', 0)
                    try:
                        cantidad_int = int(cantidad) if cantidad else 0
                        
                        if cantidad_int > 999999:
                            cantidad_int = 999999
                    except (ValueError, OverflowError):
                        cantidad_int = 0

                    avance, created = AvanceMensual.objects.get_or_create(
                        actividad=actividad,
                        mes=mes,
                        anio=proyecto.anio,
                        defaults={'cantidad_programada_mes': cantidad_int}
                    )
                    if not created:
                        avance.cantidad_programada_mes = cantidad_int
                        avance.save()

                messages.success(request, f'Programación mensual guardada exitosamente ({suma_programacion}/{actividad.cantidad_programada}).')
                return redirect('poa:crear_proyecto_wizard')
            elif accion == 'finalizar':
                actividades_sin_programar = []
                for actividad in Actividad.objects.filter(meta__proyecto=proyecto).select_related('meta'):
                    # Calcular el total programado de la actividad
                    total_programado = sum(
                        avance.cantidad_programada_mes 
                        for avance in AvanceMensual.objects.filter(actividad=actividad, anio=proyecto.anio)
                    )
                    
                    # Verificar si el total programado coincide con la cantidad programada
                    if total_programado != actividad.cantidad_programada:
                        actividades_sin_programar.append({
                            'descripcion': actividad.descripcion,
                            'meta': actividad.meta.descripcion,
                            'total_programado': total_programado,
                            'cantidad_programada': actividad.cantidad_programada
                        })
                
                if actividades_sin_programar:
                    # Crear mensaje de error detallado
                    if len(actividades_sin_programar) == 1:
                        act = actividades_sin_programar[0]
                        mensaje = (
                            f'La actividad "{act["descripcion"]}" de la meta "{act["meta"]}" '
                            f'no está completamente programada. '
                            f'Total programado: {act["total_programado"]}/{act["cantidad_programada"]}. '
                            f'Debe programar todas las actividades completamente antes de continuar.'
                        )
                    else:
                        mensaje_lista = []
                        for act in actividades_sin_programar:
                            mensaje_lista.append(
                                f'"{act["descripcion"]}" ({act["total_programado"]}/{act["cantidad_programada"]})'
                            )
                        actividades_formateadas = ', '.join(mensaje_lista)
                        mensaje = (
                            f'Las siguientes actividades no están completamente programadas: '
                            f'{actividades_formateadas}. '
                            f'Debe programar todas las actividades completamente antes de continuar.'
                        )
                    messages.warning(request, mensaje)
                else:
                    # Todo correcto, avanzar al siguiente paso
                    request.session['wizard_paso'] = 5
                    return redirect('poa:crear_proyecto_wizard')
            elif accion == 'anterior':
                request.session['wizard_paso'] = 3
                return redirect('poa:crear_proyecto_wizard')
        
        # Paso 5: Revisión y Confirmación
        elif paso_actual == 5:
            if accion == 'confirmar':
                # Limpiar la sesión del wizard
                del request.session['wizard_paso']
                del request.session['wizard_proyecto_id']
                messages.success(request, 'Proyecto creado exitosamente.')
                return redirect('poa:lista_proyectos')
            elif accion == 'anterior':
                request.session['wizard_paso'] = 4
                return redirect('poa:crear_proyecto_wizard')
    
    # Preparar formularios según el paso
    if paso_actual == 1:
        context['formulario_proyecto'] = FormularioProyecto(instance=proyecto)
    elif paso_actual == 2:
        context['formulario_meta'] = FormularioMeta()
        context['metas'] = proyecto.metas.all() if proyecto else []
    elif paso_actual == 3:
        metas_con_actividades = proyecto.metas.prefetch_related('actividades').all() if proyecto else []
        
        # Verificar si todas las metas tienen al menos una actividad
        todas_metas_tienen_actividades = all(meta.actividades.count() > 0 for meta in metas_con_actividades)
        
        context['metas'] = metas_con_actividades
        context['formulario_actividad'] = FormularioActividad()
        context['todas_metas_tienen_actividades'] = todas_metas_tienen_actividades
    elif paso_actual == 4:
        context['actividades'] = Actividad.objects.filter(meta__proyecto=proyecto).prefetch_related('avances').select_related('meta') if proyecto else []
        context['meses'] = range(1, 13)

        programacion_mensual = {}
        actividades_programadas = {}
        for actividad in context['actividades']:
            programacion_mensual[actividad.id] = {}
            avances = AvanceMensual.objects.filter(actividad=actividad, anio=proyecto.anio)
            total_programado = 0
            for avance in avances:
                programacion_mensual[actividad.id][avance.mes] = avance.cantidad_programada_mes
                total_programado += avance.cantidad_programada_mes
            # Verificar si la actividad está completamente programada
            actividades_programadas[actividad.id] = (total_programado == actividad.cantidad_programada)
        
        context['programacion_mensual'] = programacion_mensual
        context['actividades_programadas'] = actividades_programadas
        # Verificar si todas las actividades están completamente programadas
        context['todas_actividades_programadas'] = all(actividades_programadas.values()) if actividades_programadas else False

    elif paso_actual == 5:
        context['metas'] = proyecto.metas.prefetch_related('actividades__avances').all() if proyecto else []

    return render(request, 'poa/crear_proyecto_wizard.html', context)


@login_required
def editar_proyecto(request, proyecto_id):
    """Vista para editar un proyecto existente"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    if request.user.rol == 'UNIDAD' and proyecto.unidad.unidad != request.user.unidad:
        messages.error(request, 'No tiene permisos para editar este proyecto.')
        return redirect('poa:lista_proyectos')
    
    if request.method == 'POST':
        formulario = FormularioProyecto(request.POST, instance=proyecto)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Proyecto actualizado exitosamente.')
            return redirect('poa:detalle_proyecto', proyecto_id=proyecto.id)
    else:
        formulario = FormularioProyecto(instance=proyecto)
    
    return render(request, 'poa/editar_proyecto.html', {
        'proyecto': proyecto,
        'formulario': formulario,
    })


@login_required
def detalle_proyecto(request, proyecto_id):
    """Vista para ver el detalle de un proyecto"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    if request.user.rol == 'UNIDAD' and proyecto.unidad.unidad != request.user.unidad:
        messages.error(request, 'No tiene permisos para ver este proyecto.')
        return redirect('poa:lista_proyectos')
    
    metas = proyecto.metas.prefetch_related('actividades__avances').all()
    
    return render(request, 'poa/detalle_proyecto.html', {
        'proyecto': proyecto,
        'metas': metas,
    })


@login_required
def eliminar_proyecto(request, proyecto_id):
    """Vista para eliminar un proyecto"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    if request.user.rol == 'UNIDAD' and proyecto.unidad.unidad != request.user.unidad:
        messages.error(request, 'No tiene permisos para eliminar este proyecto.')
        return redirect('poa:lista_proyectos')
    
    if proyecto.estado != 'BORRADOR':
        messages.error(request, 'Solo se pueden eliminar proyectos en estado BORRADOR.')
        return redirect('poa:lista_proyectos')
    
    proyecto.delete()
    messages.success(request, 'Proyecto eliminado exitosamente.')
    return redirect('poa:lista_proyectos')

@login_required
def eliminar_meta(request, meta_id):
    """Vista para eliminar una meta"""
    meta = get_object_or_404(MetaProyecto, id=meta_id)
    proyecto_id = meta.proyecto.id
    
    if request.method == 'POST':
        meta.delete()
        messages.success(request, 'Meta eliminada exitosamente.')
    
    # Redirigir según el contexto
    if 'wizard' in request.GET:
        return redirect('poa:crear_proyecto_wizard')
    else:
        return redirect('poa:detalle_proyecto', proyecto_id=proyecto_id)


@login_required
def eliminar_actividad(request, actividad_id):
    """Vista para eliminar una actividad"""
    actividad = get_object_or_404(Actividad, id=actividad_id)
    proyecto_id = actividad.meta.proyecto.id
    
    if request.method == 'POST':
        actividad.delete()
        messages.success(request, 'Actividad eliminada exitosamente.')
    
    # Redirigir según el contexto
    if 'wizard' in request.GET:
        return redirect('poa:crear_proyecto_wizard')
    else:
        return redirect('poa:detalle_proyecto', proyecto_id=proyecto_id)


@login_required
def cancelar_wizard(request):
    """Vista para cancelar el wizard y limpiar la sesión"""
    proyecto_id = request.session.get('wizard_proyecto_id')
    
    if proyecto_id:
        # Opcional: eliminar el proyecto en borrador
        proyecto = Proyecto.objects.filter(id=proyecto_id).first()
        if proyecto and request.GET.get('eliminar') == '1':
            proyecto.delete()
            messages.info(request, 'Creación de proyecto cancelada.')
    
    # Limpiar sesión
    if 'wizard_paso' in request.session:
        del request.session['wizard_paso']
    if 'wizard_proyecto_id' in request.session:
        del request.session['wizard_proyecto_id']
    
    return redirect('poa:lista_proyectos')

@login_required
def enviar_proyecto(request, proyecto_id):
    """Vista para enviar un proyecto (cambiar estado de BORRADOR a ENVIADO)"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    if request.user.rol != 'UNIDAD' or proyecto.unidad != request.user:
        messages.error(request, 'No tiene permisos para enviar este proyecto.')
        return redirect('poa:lista_proyectos')
    
    if proyecto.estado != 'BORRADOR':
        messages.error(request, 'Solo se pueden enviar proyectos en estado BORRADOR.')
        return redirect('poa:lista_proyectos')
    
    if request.method == 'POST':
        # Cambiar estado a ENVIADO
        proyecto.estado = 'ENVIADO'
        proyecto.save()
        
        messages.success(request, f'Proyecto "{proyecto.nombre}" enviado exitosamente. Está esperando revisión del administrador.')
        return redirect('poa:lista_proyectos')
    
    return redirect('poa:lista_proyectos')

@login_required
def ver_poa_aprobado(request, proyecto_id):
    """Vista para ver el POA aprobado completo (solo lectura para unidades)"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    if request.user.rol == 'UNIDAD' and proyecto.unidad.unidad != request.user.unidad:
        messages.error(request, 'No tiene permisos para ver este proyecto.')
        return redirect('login:dashboard_unidad')
    
    # Verificar que el proyecto esté aprobado
    if proyecto.estado != 'APROBADO' and request.user.rol == 'UNIDAD':
        messages.error(request, 'Solo puede ver proyectos aprobados.')
        return redirect('login:dashboard_unidad')
    
    metas = proyecto.metas.prefetch_related('actividades__avances', 'actividades__evidencias').all()
    
    return render(request, 'poa/ver_poa_aprobado.html', {
        'proyecto': proyecto,
        'metas': metas,
    })


@login_required
def gestionar_avances(request, proyecto_id):
    """Vista para gestionar los avances mensuales de las actividades"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    if request.user.rol == 'UNIDAD' and proyecto.unidad.unidad != request.user.unidad:
        messages.error(request, 'No tiene permisos para gestionar este proyecto.')
        return redirect('login:dashboard_unidad')
    
    # Verificar que el proyecto esté aprobado
    if proyecto.estado != 'APROBADO':
        messages.error(request, 'Solo puede gestionar avances de proyectos aprobados.')
        return redirect('login:dashboard_unidad')
    
    if request.method == 'POST':
        actividad_id = request.POST.get('actividad_id')
        mes = request.POST.get('mes')
        cantidad_realizada = request.POST.get('cantidad_realizada')
        
        if actividad_id and mes and cantidad_realizada is not None:
            actividad = get_object_or_404(Actividad, id=actividad_id, meta__proyecto=proyecto)
            avance = get_object_or_404(AvanceMensual, actividad=actividad, mes=mes, anio=proyecto.anio)
            
            try:
                cantidad_int = int(cantidad_realizada)
                
                if cantidad_int > 999999:
                    messages.error(request, 'La cantidad realizada no puede exceder 999,999 unidades.')
                    return redirect('poa:gestionar_avances', proyecto_id=proyecto.id)
                
                if cantidad_int < 0:
                    messages.error(request, 'La cantidad realizada no puede ser negativa.')
                else:
                    if cantidad_int > avance.cantidad_programada_mes:
                        avance.es_no_planificada = True
                        messages.info(
                            request, 
                            f'Se registraron {cantidad_int - avance.cantidad_programada_mes} unidades adicionales no planificadas.'
                        )
                    else:
                        avance.es_no_planificada = False
                    
                    avance.cantidad_realizada = cantidad_int
                    avance.save()
                    
                    proyecto.fecha_modificacion = timezone.now()
                    proyecto.save(update_fields=['fecha_modificacion'])
                    
                    messages.success(request, 'Avance actualizado exitosamente.')
            except ValueError:
                messages.error(request, 'La cantidad debe ser un número válido.')
            except OverflowError:
                messages.error(request, 'El número ingresado es demasiado grande. Por favor, ingrese un valor menor a 999,999.')
            
            return redirect('poa:gestionar_avances', proyecto_id=proyecto.id)
    
    metas = proyecto.metas.prefetch_related('actividades__avances', 'actividades__evidencias').all()
    meses_nombres = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                     'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    
    for meta in metas:
        for actividad in meta.actividades.all():
            for avance in actividad.avances.all():
                # Contar evidencias para este mes específico
                avance.evidencias_count = actividad.evidencias.filter(mes=avance.mes).count()
    
    return render(request, 'poa/gestionar_avances.html', {
        'proyecto': proyecto,
        'metas': metas,
        'meses_nombres': meses_nombres,
    })


@login_required
def gestionar_evidencias(request, proyecto_id):
    """Vista para gestionar las evidencias de las actividades"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    if request.user.rol == 'UNIDAD' and proyecto.unidad.unidad != request.user.unidad:
        messages.error(request, 'No tiene permisos para gestionar este proyecto.')
        return redirect('login:dashboard_unidad')
    
    # Verificar que el proyecto esté aprobado
    if proyecto.estado != 'APROBADO':
        messages.error(request, 'Solo puede gestionar evidencias de proyectos aprobados.')
        return redirect('login:dashboard_unidad')
    
    if request.method == 'POST':
        actividad_id = request.POST.get('actividad_id')
        
        if actividad_id:
            actividad = get_object_or_404(Actividad, id=actividad_id, meta__proyecto=proyecto)
            formulario = FormularioEvidencia(request.POST, request.FILES)
            
            if formulario.is_valid():
                evidencia = formulario.save(commit=False)
                evidencia.actividad = actividad
                evidencia.save()
                messages.success(request, 'Evidencia agregada exitosamente.')
                return redirect('poa:gestionar_evidencias', proyecto_id=proyecto.id)
            else:
                messages.error(request, 'Error al agregar la evidencia. Verifique los datos.')
    
    metas = proyecto.metas.prefetch_related('actividades__evidencias').all()
    formulario_evidencia = FormularioEvidencia()
    
    return render(request, 'poa/gestionar_evidencias.html', {
        'proyecto': proyecto,
        'metas': metas,
        'formulario_evidencia': formulario_evidencia,
    })


@login_required
def ver_reportes(request, proyecto_id):
    """Vista para ver reportes del POA"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    if request.user.rol == 'UNIDAD' and proyecto.unidad.unidad != request.user.unidad:
        messages.error(request, 'No tiene permisos para ver este proyecto.')
        return redirect('login:dashboard_unidad')
    
    total_actividades = Actividad.objects.filter(meta__proyecto=proyecto).count()
    
    # Calcular total programado
    total_programado = Decimal(0)
    for avance in AvanceMensual.objects.filter(actividad__meta__proyecto=proyecto):
        total_programado += Decimal(avance.cantidad_programada_mes or 0)
    
    
    total_realizado = Decimal(0)
    for avance in AvanceMensual.objects.filter(actividad__meta__proyecto=proyecto):
        cantidad_realizada = Decimal(avance.cantidad_realizada or 0)
        cantidad_programada = Decimal(avance.cantidad_programada_mes or 0)
        total_realizado += min(cantidad_realizada, cantidad_programada)
    
    try:
        if total_programado > 0:
            porcentaje_cumplimiento = (total_realizado / total_programado * 100)
            porcentaje_cumplimiento = round(porcentaje_cumplimiento, 2)
            
            if porcentaje_cumplimiento > 100:
                porcentaje_cumplimiento = Decimal(100)
        else:
            porcentaje_cumplimiento = Decimal(0)
    except (InvalidOperation, ZeroDivisionError, Exception) as e:
        porcentaje_cumplimiento = Decimal(0)
        messages.warning(request, 'Error al calcular el porcentaje de cumplimiento.')
    
    return render(request, 'poa/ver_reportes.html', {
        'proyecto': proyecto,
        'total_actividades': total_actividades,
        'total_programado': total_programado,
        'total_realizado': total_realizado,
        'porcentaje_cumplimiento': porcentaje_cumplimiento,
    })

@login_required
def registrar_avance_actividad(request, actividad_id):
    """Vista para registrar avances mensuales de una actividad específica"""
    actividad = get_object_or_404(Actividad, id=actividad_id)
    proyecto = actividad.meta.proyecto
    
    if request.user.rol == 'UNIDAD' and proyecto.unidad.unidad != request.user.unidad:
        messages.error(request, 'No tiene permisos para gestionar esta actividad.')
        return redirect('login:dashboard_unidad')
    
    # Verificar que el proyecto esté aprobado
    if proyecto.estado != 'APROBADO':
        messages.error(request, 'Solo puede registrar avances de proyectos aprobados.')
        return redirect('login:dashboard_unidad')
    
    if request.method == 'POST':
        mes = request.POST.get('mes')
        cantidad_realizada = request.POST.get('cantidad_realizada')
        
        if mes and cantidad_realizada is not None:
            avance = get_object_or_404(AvanceMensual, actividad=actividad, mes=mes, anio=proyecto.anio)
            
            try:
                cantidad_int = int(cantidad_realizada)
                
                if cantidad_int > 999999:
                    messages.error(request, 'La cantidad realizada no puede exceder 999,999 unidades.')
                    return redirect('poa:registrar_avance_actividad', actividad_id=actividad.id)
                
                if cantidad_int < 0:
                    messages.error(request, 'La cantidad realizada no puede ser negativa.')
                else:
                    if cantidad_int > avance.cantidad_programada_mes:
                        avance.es_no_planificada = True
                        messages.info(
                            request,
                            f'Se registraron {cantidad_int - avance.cantidad_programada_mes} unidades adicionales no planificadas.'
                        )
                    else:
                        avance.es_no_planificada = False
                    
                    avance.cantidad_realizada = cantidad_int
                    avance.save()
                    
                    proyecto.fecha_modificacion = timezone.now()
                    proyecto.save(update_fields=['fecha_modificacion'])
                    
                    messages.success(request, 'Avance actualizado exitosamente.')
            except ValueError:
                messages.error(request, 'La cantidad debe ser un número válido.')
            except OverflowError:
                messages.error(request, 'El número ingresado es demasiado grande. Por favor, ingrese un valor menor a 999,999.')
            
            return redirect('poa:registrar_avance_actividad', actividad_id=actividad.id)
    
    avances = AvanceMensual.objects.filter(actividad=actividad, anio=proyecto.anio).order_by('mes')
    meses_nombres = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                     'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    
    return render(request, 'poa/registrar_avance_actividad.html', {
        'actividad': actividad,
        'proyecto': proyecto,
        'avances': avances,
        'meses_nombres': meses_nombres,
    })


@login_required
def subir_evidencia_actividad(request, actividad_id):
    """Vista para subir evidencias de una actividad específica"""
    actividad = get_object_or_404(Actividad, id=actividad_id)
    proyecto = actividad.meta.proyecto
    
    if request.user.rol == 'UNIDAD' and proyecto.unidad.unidad != request.user.unidad:
        messages.error(request, 'No tiene permisos para gestionar esta actividad.')
        return redirect('login:dashboard_unidad')
    
    # Verificar que el proyecto esté aprobado
    if proyecto.estado != 'APROBADO':
        messages.error(request, 'Solo puede subir evidencias de proyectos aprobados.')
        return redirect('login:dashboard_unidad')
    
    if request.method == 'POST':
        formulario = FormularioEvidencia(request.POST, request.FILES)
        
        if formulario.is_valid():
            evidencia = formulario.save(commit=False)
            evidencia.actividad = actividad
            evidencia.save()
            messages.success(request, 'Evidencia agregada exitosamente.')
            return redirect('poa:subir_evidencia_actividad', actividad_id=actividad.id)
        else:
            messages.error(request, 'Error al agregar la evidencia. Verifique los datos.')
    
    formulario_evidencia = FormularioEvidencia()
    evidencias = Evidencia.objects.filter(actividad=actividad).order_by('-fecha_subida')
    
    return render(request, 'poa/subir_evidencia_actividad.html', {
        'actividad': actividad,
        'proyecto': proyecto,
        'formulario_evidencia': formulario_evidencia,
        'evidencias': evidencias,
    })

@login_required
def subir_evidencia_mes(request):
    """Vista para subir evidencias asociadas a un mes específico"""
    if request.method == 'POST':
        actividad_id = request.POST.get('actividad_id')
        mes = request.POST.get('mes')
        tipo = request.POST.get('tipo')
        archivo = request.FILES.get('archivo')
        url = request.POST.get('url')
        descripcion = request.POST.get('descripcion', '')
        
        if actividad_id and mes and tipo:
            actividad = get_object_or_404(Actividad, id=actividad_id)
            proyecto = actividad.meta.proyecto
            
            if request.user.rol == 'UNIDAD' and proyecto.unidad.unidad != request.user.unidad:
                messages.error(request, 'No tiene permisos para subir evidencias.')
                return redirect('login:dashboard_unidad')
            
            # Verificar que el proyecto esté aprobado
            if proyecto.estado != 'APROBADO':
                messages.error(request, 'Solo puede subir evidencias de proyectos aprobados.')
                return redirect('login:dashboard_unidad')
            
            if archivo:
                # Validar tamaño del archivo (máximo 30MB)
                max_size = 30 * 1024 * 1024  # 30MB en bytes
                if archivo.size > max_size:
                    messages.error(request, f'El archivo es demasiado grande. Tamaño máximo permitido: 30MB. Tamaño del archivo: {archivo.size / (1024 * 1024):.2f}MB')
                    return redirect('poa:gestionar_avances', proyecto_id=proyecto.id)
                
                extensiones_permitidas = [
                    # Imágenes
                    '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp',
                    # Videos
                    '.mp4', '.avi', '.mov', '.wmv', '.mkv', '.flv',
                    # Documentos
                    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                    # Audio
                    '.mp3', '.wav', '.ogg', '.m4a'
                ]
                
                nombre_archivo = archivo.name.lower()
                extension_valida = any(nombre_archivo.endswith(ext) for ext in extensiones_permitidas)
                
                if not extension_valida:
                    extensiones_str = ', '.join(extensiones_permitidas)
                    messages.error(request, f'Formato de archivo no permitido. Formatos permitidos: {extensiones_str}')
                    return redirect('poa:gestionar_avances', proyecto_id=proyecto.id)
            
            # Crear la evidencia
            evidencia = Evidencia(
                actividad=actividad,
                tipo=tipo,
                archivo=archivo,
                url=url if url else None,
                descripcion=descripcion,
                mes=int(mes)
            )
            evidencia.save()
            
            proyecto.fecha_modificacion = timezone.now()
            proyecto.save(update_fields=['fecha_modificacion'])
            
            messages.success(request, f'Evidencia subida exitosamente para {evidencia.get_mes_display()}.')
            return redirect('poa:gestionar_avances', proyecto_id=proyecto.id)
        else:
            messages.error(request, 'Faltan datos requeridos para subir la evidencia.')
    
    return redirect('login:dashboard_unidad')

@login_required
def obtener_evidencias_mes(request, actividad_id, mes):
    """Vista AJAX para obtener las evidencias de un mes específico"""
    actividad = get_object_or_404(Actividad, id=actividad_id)
    proyecto = actividad.meta.proyecto
    
    if request.user.rol == 'UNIDAD' and proyecto.unidad.unidad != request.user.unidad:
        return JsonResponse({'error': 'No tiene permisos'}, status=403)
    
    # Si es ADMIN, permitir acceso sin restricciones adicionales
    
    evidencias = Evidencia.objects.filter(actividad=actividad, mes=mes).order_by('-fecha_subida')
    
    evidencias_data = []
    for ev in evidencias:
        evidencias_data.append({
            'id': ev.id,
            'tipo': ev.tipo,
            'descripcion': ev.descripcion,
            'archivo': ev.archivo.url if ev.archivo else None,
            'url': ev.url,
            'fecha_subida': ev.fecha_subida.strftime('%d/%m/%Y %H:%M')
        })
    
    return JsonResponse({'evidencias': evidencias_data})
