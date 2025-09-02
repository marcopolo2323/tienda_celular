from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import db, Servicio, Usuario
from app.utils.validators import validate_service_data
from datetime import datetime, date

servicios_bp = Blueprint('servicios', __name__)

@servicios_bp.route('/tecnicos', methods=['GET', 'POST'])
@login_required
def servicios_tecnicos():
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            errors = validate_service_data(data)
            
            if errors:
                for error in errors:
                    flash(error, 'error')
                return redirect(url_for('servicios.servicios_tecnicos'))
            
            # Parsear fecha de entrega estimada
            fecha_entrega = None
            if data.get('fecha_entrega'):
                try:
                    fecha_entrega = datetime.strptime(data['fecha_entrega'], '%Y-%m-%d').date()
                except ValueError:
                    flash('Formato de fecha inválido', 'error')
                    return redirect(url_for('servicios.servicios_tecnicos'))
            
            servicio = Servicio(
                tipo=data['tipo'],
                descripcion=data['descripcion'],
                cliente_nombre=data['cliente_nombre'],
                cliente_telefono=data['cliente_telefono'],
                fecha_entrega_estimada=fecha_entrega,
                costo=float(data['costo']),
                tecnico_id=int(data['tecnico_id']) if data.get('tecnico_id') else None,
                notas_tecnicas=data.get('notas_tecnicas', ''),
                estado='pendiente'
            )
            
            db.session.add(servicio)
            db.session.commit()
            flash('Servicio técnico registrado exitosamente', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar servicio: {str(e)}', 'error')
        
        return redirect(url_for('servicios.servicios_tecnicos'))
    
    # Obtener servicios con paginación
    page = request.args.get('page', 1, type=int)
    per_page = 15
    
    query = Servicio.query
    
    # Filtros
    estado_filter = request.args.get('estado')
    if estado_filter:
        query = query.filter_by(estado=estado_filter)
    
    tecnico_filter = request.args.get('tecnico_id', type=int)
    if tecnico_filter:
        query = query.filter_by(tecnico_id=tecnico_filter)
    
    servicios = query.order_by(Servicio.fecha_recepcion.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    tecnicos = Usuario.query.filter_by(rol='tecnico').order_by(Usuario.nombre).all()
    estados = ['pendiente', 'en_progreso', 'completado', 'entregado', 'cancelado']
    
    return render_template('servicios_tecnicos.html',
                         servicios=servicios,
                         tecnicos=tecnicos,
                         estados=estados,
                         estado_filter=estado_filter,
                         tecnico_filter=tecnico_filter)

@servicios_bp.route('/tecnicos/<int:id>/actualizar', methods=['POST'])
@login_required
def actualizar_servicio(id):
    servicio = Servicio.query.get_or_404(id)
    
    try:
        data = request.form.to_dict()
        
        # Actualizar campos básicos
        if 'estado' in data:
            servicio.estado = data['estado']
        
        if 'tecnico_id' in data and data['tecnico_id']:
            servicio.tecnico_id = int(data['tecnico_id'])
        
        if 'notas_tecnicas' in data:
            servicio.notas_tecnicas = data['notas_tecnicas']
        
        if 'costo' in data and data['costo']:
            servicio.costo = float(data['costo'])
        
        # Actualizar fecha de entrega si se proporciona
        if 'fecha_entrega_estimada' in data and data['fecha_entrega_estimada']:
            try:
                servicio.fecha_entrega_estimada = datetime.strptime(
                    data['fecha_entrega_estimada'], '%Y-%m-%d'
                ).date()
            except ValueError:
                flash('Formato de fecha inválido', 'error')
                return redirect(url_for('servicios.servicios_tecnicos'))
        
        # Actualizar fecha de finalización si se marca como completado
        if servicio.estado == 'completado' and not servicio.fecha_finalizacion:
            servicio.fecha_finalizacion = datetime.utcnow()
        
        db.session.commit()
        flash('Servicio actualizado exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar servicio: {str(e)}', 'error')
    
    return redirect(url_for('servicios.servicios_tecnicos'))

@servicios_bp.route('/tecnicos/<int:id>/detalles')
@login_required
def detalles_servicio(id):
    servicio = Servicio.query.get_or_404(id)
    
    return jsonify({
        'id': servicio.id,
        'tipo': servicio.tipo,
        'descripcion': servicio.descripcion,
        'cliente_nombre': servicio.cliente_nombre,
        'cliente_telefono': servicio.cliente_telefono,
        'estado': servicio.estado,
        'costo': float(servicio.costo),
        'fecha_recepcion': servicio.fecha_recepcion.isoformat(),
        'fecha_entrega_estimada': servicio.fecha_entrega_estimada.isoformat() if servicio.fecha_entrega_estimada else None,
        'fecha_finalizacion': servicio.fecha_finalizacion.isoformat() if servicio.fecha_finalizacion else None,
        'tecnico_nombre': servicio.tecnico.nombre if servicio.tecnico else None,
        'notas_tecnicas': servicio.notas_tecnicas or '',
        'diagnostico': getattr(servicio, 'diagnostico', '') or '',
        'solucion': getattr(servicio, 'solucion', '') or ''
    })

@servicios_bp.route('/tecnicos/<int:id>/diagnostico', methods=['POST'])
@login_required
def actualizar_diagnostico(id):
    servicio = Servicio.query.get_or_404(id)
    
    # Verificar permisos: solo el técnico asignado o admin pueden actualizar
    if (current_user.rol != 'admin' and 
        (not servicio.tecnico or servicio.tecnico.id != current_user.id)):
        flash('No tienes permisos para actualizar este servicio', 'error')
        return redirect(url_for('servicios.servicios_tecnicos'))
    
    try:
        # Solo actualizar campos que existen en el modelo
        if hasattr(servicio, 'diagnostico'):
            servicio.diagnostico = request.form.get('diagnostico', '')
        if hasattr(servicio, 'solucion'):
            servicio.solucion = request.form.get('solucion', '')
        
        servicio.notas_tecnicas = request.form.get('notas_tecnicas', '')
        
        # Si se proporciona una solución, cambiar estado a en_progreso
        if (hasattr(servicio, 'solucion') and servicio.solucion and 
            servicio.estado == 'pendiente'):
            servicio.estado = 'en_progreso'
        
        db.session.commit()
        flash('Diagnóstico actualizado exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar diagnóstico: {str(e)}', 'error')
    
    return redirect(url_for('servicios.servicios_tecnicos'))

@servicios_bp.route('/tecnicos/<int:id>/cancelar', methods=['POST'])
@login_required
def cancelar_servicio(id):
    servicio = Servicio.query.get_or_404(id)
    
    if servicio.estado in ['entregado', 'cancelado']:
        flash('Este servicio ya está finalizado', 'error')
        return redirect(url_for('servicios.servicios_tecnicos'))
    
    try:
        servicio.estado = 'cancelado'
        servicio.notas_tecnicas += f"\n[CANCELADO] {datetime.now().strftime('%Y-%m-%d %H:%M')} - Servicio cancelado"
        
        if request.form.get('motivo_cancelacion'):
            servicio.notas_tecnicas += f" - Motivo: {request.form.get('motivo_cancelacion')}"
        
        db.session.commit()
        flash('Servicio cancelado exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cancelar servicio: {str(e)}', 'error')
    
    return redirect(url_for('servicios.servicios_tecnicos'))

@servicios_bp.route('/tecnicos/mis-servicios')
@login_required
def mis_servicios():
    """Vista para técnicos - sus servicios asignados"""
    if current_user.rol != 'tecnico':
        flash('Acceso denegado', 'error')
        return redirect(url_for('main.index'))
    
    servicios = Servicio.query.filter_by(
        tecnico_id=current_user.id
    ).order_by(Servicio.fecha_recepcion.desc()).all()
    
    return render_template('servicios_tecnicos.html', servicios=servicios)

@servicios_bp.route('/reportes')
@login_required
def reportes_servicios():
    """Reportes de servicios técnicos"""
    if current_user.rol not in ['admin', 'gerente']:
        flash('No tienes permisos para ver reportes', 'error')
        return redirect(url_for('servicios.servicios_tecnicos'))
    
    # Estadísticas básicas
    total_servicios = Servicio.query.count()
    servicios_pendientes = Servicio.query.filter_by(estado='pendiente').count()
    servicios_en_progreso = Servicio.query.filter_by(estado='en_progreso').count()
    servicios_completados = Servicio.query.filter_by(estado='completado').count()
    
    # Servicios por técnico
    tecnicos_stats = db.session.query(
        Usuario.nombre,
        db.func.count(Servicio.id).label('total_servicios'),
        db.func.avg(Servicio.costo).label('costo_promedio')
    ).join(Servicio, Usuario.id == Servicio.tecnico_id)\
     .filter(Usuario.rol == 'tecnico')\
     .group_by(Usuario.id, Usuario.nombre).all()
    
    return render_template('reportes.html',
                         total_servicios=total_servicios,
                         servicios_pendientes=servicios_pendientes,
                         servicios_en_progreso=servicios_en_progreso,
                         servicios_completados=servicios_completados,
                         tecnicos_stats=tecnicos_stats)

@servicios_bp.route('/servicio_tecnico/<int:id>', methods=['GET'])
@login_required
def obtener_servicio_tecnico(id):
    """Obtener datos de un servicio técnico para edición"""
    try:
        servicio = Servicio.query.get_or_404(id)
        return jsonify({
            'id': servicio.id,
            'tipo': servicio.tipo,
            'descripcion': servicio.descripcion,
            'cliente_nombre': servicio.cliente_nombre,
            'cliente_telefono': servicio.cliente_telefono,
            'fecha_recepcion': servicio.fecha_recepcion.isoformat(),
            'fecha_entrega_estimada': servicio.fecha_entrega_estimada.isoformat() if servicio.fecha_entrega_estimada else None,
            'estado': servicio.estado,
            'costo': float(servicio.costo),
            'tecnico_id': servicio.tecnico_id,
            'tecnico_nombre': servicio.tecnico.nombre if servicio.tecnico else None,
            'notas_tecnicas': servicio.notas_tecnicas or '',
            'diagnostico': getattr(servicio, 'diagnostico', '') or '',
            'solucion': getattr(servicio, 'solucion', '') or ''
        })
    except Exception as e:
        return jsonify({'error': f'Error al obtener servicio: {str(e)}'}), 500

@servicios_bp.route('/servicio_tecnico/<int:id>', methods=['PUT'])
@login_required
def actualizar_servicio_api(id):
    """Actualizar servicio técnico via API"""
    try:
        servicio = Servicio.query.get_or_404(id)
        data = request.get_json()
        
        # Actualizar campos básicos
        if 'cliente_nombre' in data:
            servicio.cliente_nombre = data['cliente_nombre']
        if 'cliente_telefono' in data:
            servicio.cliente_telefono = data['cliente_telefono']
        if 'tipo' in data:
            servicio.tipo = data['tipo']
        if 'descripcion' in data:
            servicio.descripcion = data['descripcion']
        if 'estado' in data:
            servicio.estado = data['estado']
        if 'costo' in data and data['costo']:
            servicio.costo = float(data['costo'])
        if 'tecnico_id' in data:
            servicio.tecnico_id = int(data['tecnico_id']) if data['tecnico_id'] else None
        if 'notas_tecnicas' in data:
            servicio.notas_tecnicas = data['notas_tecnicas']
        
        # Actualizar fecha de entrega si se proporciona
        if 'fecha_entrega_estimada' in data and data['fecha_entrega_estimada']:
            try:
                # Manejar diferentes formatos de fecha
                fecha_str = data['fecha_entrega_estimada']
                if 'T' in fecha_str:
                    # Formato datetime-local
                    fecha_dt = datetime.fromisoformat(fecha_str.replace('Z', ''))
                    servicio.fecha_entrega_estimada = fecha_dt.date()
                else:
                    # Formato date
                    servicio.fecha_entrega_estimada = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError as e:
                return jsonify({'error': f'Formato de fecha inválido: {str(e)}'}), 400
        
        # Si se marca como completado, actualizar fecha de finalización
        if servicio.estado == 'completado' and not servicio.fecha_finalizacion:
            servicio.fecha_finalizacion = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'message': 'Servicio técnico actualizado exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@servicios_bp.route('/servicio_tecnico/<int:id>', methods=['DELETE'])
@login_required
def eliminar_servicio_api(id):
    """Eliminar servicio técnico"""
    if current_user.rol not in ['admin', 'gerente']:
        return jsonify({'error': 'No tienes permisos para eliminar servicios'}), 403
    
    try:
        servicio = Servicio.query.get_or_404(id)
        db.session.delete(servicio)
        db.session.commit()
        return jsonify({'message': 'Servicio técnico eliminado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500