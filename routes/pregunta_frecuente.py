from flask import Blueprint, jsonify, request
from models.pregunta_frecuente import PreguntaFrecuente

ws_pregunta_frecuente = Blueprint('ws_pregunta_frecuente', __name__)

@ws_pregunta_frecuente.route('/preguntas-frecuentes/listar', methods=['GET'])
def listar_preguntas():
    """Endpoint para listar todas las preguntas frecuentes"""
    try:
        pregunta = PreguntaFrecuente()
        exito, resultado = pregunta.listar_preguntas_frecuentes()
        
        if exito:
            return jsonify({
                'status': True,
                'data': resultado,
                'message': 'Preguntas frecuentes listadas correctamente'
            }), 200
        else:
            return jsonify({
                'status': False,
                'data': None,
                'message': resultado
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'data': None,
            'message': f'Error en el servidor: {str(e)}'
        }), 500

@ws_pregunta_frecuente.route('/preguntas-frecuentes/obtener/<int:id_pregunta>', methods=['GET'])
def obtener_pregunta(id_pregunta):
    """Endpoint para obtener el detalle de una pregunta frecuente"""
    try:
        pregunta = PreguntaFrecuente()
        exito, resultado = pregunta.obtener_pregunta(id_pregunta)
        
        if exito:
            return jsonify({
                'status': True,
                'data': resultado,
                'message': 'Pregunta obtenida correctamente'
            }), 200
        else:
            return jsonify({
                'status': False,
                'data': None,
                'message': resultado
            }), 404
            
    except Exception as e:
        return jsonify({
            'status': False,
            'data': None,
            'message': f'Error en el servidor: {str(e)}'
        }), 500

@ws_pregunta_frecuente.route('/preguntas-frecuentes/crear', methods=['POST'])
def crear_pregunta():
    """Endpoint para crear una nueva pregunta frecuente"""
    try:
        data = request.get_json()
        nombre = data.get('nombre')
        descripcion = data.get('descripcion')
        respuesta = data.get('respuesta')
        
        if not nombre or not descripcion or not respuesta:
            return jsonify({
                'status': False,
                'data': None,
                'message': 'Todos los campos son requeridos'
            }), 400
        
        pregunta = PreguntaFrecuente()
        exito, resultado = pregunta.crear_pregunta(nombre, descripcion, respuesta, id_usuario=1)
        
        if exito:
            return jsonify({
                'status': True,
                'data': None,
                'message': resultado
            }), 201
        else:
            return jsonify({
                'status': False,
                'data': None,
                'message': resultado
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'data': None,
            'message': f'Error en el servidor: {str(e)}'
        }), 500

@ws_pregunta_frecuente.route('/preguntas-frecuentes/modificar/<int:id_pregunta>', methods=['PUT'])
def modificar_pregunta(id_pregunta):
    """Endpoint para modificar una pregunta frecuente"""
    try:
        data = request.get_json()
        nombre = data.get('nombre')
        descripcion = data.get('descripcion')
        respuesta = data.get('respuesta')
        
        if not nombre or not descripcion or not respuesta:
            return jsonify({
                'status': False,
                'data': None,
                'message': 'Todos los campos son requeridos'
            }), 400
        
        pregunta = PreguntaFrecuente()
        exito, resultado = pregunta.modificar_pregunta(id_pregunta, nombre, descripcion, respuesta)
        
        if exito:
            return jsonify({
                'status': True,
                'data': None,
                'message': resultado
            }), 200
        else:
            return jsonify({
                'status': False,
                'data': None,
                'message': resultado
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'data': None,
            'message': f'Error en el servidor: {str(e)}'
        }), 500

@ws_pregunta_frecuente.route('/preguntas-frecuentes/cambiar-estado/<int:id_pregunta>', methods=['PATCH'])
def cambiar_estado(id_pregunta):
    """Endpoint para cambiar el estado de una pregunta frecuente"""
    try:
        pregunta = PreguntaFrecuente()
        exito, resultado = pregunta.cambiar_estado(id_pregunta)
        
        if exito:
            return jsonify({
                'status': True,
                'data': None,
                'message': resultado
            }), 200
        else:
            return jsonify({
                'status': False,
                'data': None,
                'message': resultado
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'data': None,
            'message': f'Error en el servidor: {str(e)}'
        }), 500

@ws_pregunta_frecuente.route('/preguntas-frecuentes/eliminar/<int:id_pregunta>', methods=['DELETE'])
def eliminar_pregunta(id_pregunta):
    """Endpoint para eliminar permanentemente una pregunta frecuente"""
    try:
        pregunta = PreguntaFrecuente()
        exito, resultado = pregunta.eliminar_pregunta(id_pregunta)
        
        if exito:
            return jsonify({
                'status': True,
                'data': None,
                'message': resultado
            }), 200
        else:
            return jsonify({
                'status': False,
                'data': None,
                'message': resultado
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'data': None,
            'message': f'Error en el servidor: {str(e)}'
        }), 500