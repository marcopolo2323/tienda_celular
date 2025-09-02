from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import db, Cliente

clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route('/')
@login_required
def lista_clientes():
    clientes = Cliente.query.order_by(Cliente.nombre).all()
    return render_template('clientes.html', clientes=clientes)

@clientes_bp.route('/', methods=['POST'])
@login_required
def crear_cliente():
    try:
        data = request.form.to_dict()
        cliente = Cliente(
            nombre=data['nombre'],
            email=data.get('email', ''),
            telefono=data.get('telefono', ''),
            direccion=data.get('direccion', '')
        )
        db.session.add(cliente)
        db.session.commit()
        flash('Cliente agregado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al agregar cliente: {str(e)}', 'error')
    
    return redirect(url_for('clientes.lista_clientes'))

@clientes_bp.route('/<int:id>', methods=['GET'])
@login_required
def obtener_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    return jsonify({
        'id': cliente.id,
        'nombre': cliente.nombre,
        'email': cliente.email,
        'telefono': cliente.telefono,
        'direccion': cliente.direccion
    })

@clientes_bp.route('/<int:id>', methods=['PUT'])
@login_required
def actualizar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    try:
        data = request.form.to_dict()
        cliente.nombre = data['nombre']
        cliente.email = data.get('email', '')
        cliente.telefono = data.get('telefono', '')
        cliente.direccion = data.get('direccion', '')
        
        db.session.commit()
        flash('Cliente actualizado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar cliente: {str(e)}', 'error')
    
    return redirect(url_for('clientes.lista_clientes'))

@clientes_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def eliminar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    try:
        db.session.delete(cliente)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400