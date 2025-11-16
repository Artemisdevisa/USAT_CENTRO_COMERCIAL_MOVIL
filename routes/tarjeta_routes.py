from flask import Blueprint, request, jsonify
import os
from models.tarjeta import Tarjeta

ws_tarjeta = Blueprint('ws_tarjeta', __name__)

@ws_tarjeta.route('/tarjetas/listar/<int:id_usuario>', methods=['GET'])
def listar_tarjetas(id_usuario):
    """Listar tarjetas del usuario"""
    try:
        tarjeta = Tarjeta()
        exito, resultado = tarjeta.listar_por_usuario(id_usuario)
        
        if exito:
            # ✅ DETECTAR ENTORNO Y CLIENTE
            user_agent = request.headers.get('User-Agent', '').lower()
            is_android = 'okhttp' in user_agent or 'android' in user_agent
            
            # No hay imágenes en tarjetas, pero mantenemos la estructura
            return jsonify({
                'status': True,
                'data': resultado,
                'message': 'Tarjetas listadas correctamente'
            }), 200
        else:
            return jsonify({
                'status': False,
                'data': [],
                'message': resultado
            }), 500
    except Exception as e:
        return jsonify({
            'status': False,
            'data': [],
            'message': f'Error: {str(e)}'
        }), 500

@ws_tarjeta.route('/tarjetas/agregar', methods=['POST'])
def agregar_tarjeta():
    """Agregar nueva tarjeta"""
    try:
        data = request.get_json()
        
        id_usuario = data.get('id_usuario')
        numero = data.get('numero')
        titular = data.get('titular')
        fecha_vencimiento = data.get('fecha_vencimiento')
        cvv = data.get('cvv')
        tipo_tarjeta = data.get('tipo_tarjeta')
        es_principal = data.get('es_principal', False)
        
        if not all([id_usuario, numero, titular, fecha_vencimiento, cvv, tipo_tarjeta]):
            return jsonify({
                'status': False,
                'message': 'Faltan datos requeridos'
            }), 400
        
        tarjeta = Tarjeta()
        exito, resultado = tarjeta.agregar(
            id_usuario, numero, titular, fecha_vencimiento, 
            cvv, tipo_tarjeta, es_principal
        )
        
        if exito:
            return jsonify({
                'status': True,
                'data': {'id_tarjeta': resultado},
                'message': 'Tarjeta agregada correctamente'
            }), 201
        else:
            return jsonify({
                'status': False,
                'message': resultado
            }), 400
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500

@ws_tarjeta.route('/tarjetas/eliminar', methods=['POST'])
def eliminar_tarjeta():
    """Eliminar tarjeta"""
    try:
        data = request.get_json()
        
        id_usuario = data.get('id_usuario')
        id_tarjeta = data.get('id_tarjeta')
        
        if not all([id_usuario, id_tarjeta]):
            return jsonify({
                'status': False,
                'message': 'Faltan datos requeridos'
            }), 400
        
        tarjeta = Tarjeta()
        exito, mensaje = tarjeta.eliminar(id_usuario, id_tarjeta)
        
        if exito:
            return jsonify({
                'status': True,
                'message': mensaje
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': mensaje
            }), 400
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500

@ws_tarjeta.route('/tarjetas/establecer-principal', methods=['POST'])
def establecer_principal():
    """Establecer tarjeta como principal"""
    try:
        data = request.get_json()
        
        id_usuario = data.get('id_usuario')
        id_tarjeta = data.get('id_tarjeta')
        
        if not all([id_usuario, id_tarjeta]):
            return jsonify({
                'status': False,
                'message': 'Faltan datos requeridos'
            }), 400
        
        tarjeta = Tarjeta()
        exito, mensaje = tarjeta.establecer_principal(id_usuario, id_tarjeta)
        
        if exito:
            return jsonify({
                'status': True,
                'message': mensaje
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': mensaje
            }), 400
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500