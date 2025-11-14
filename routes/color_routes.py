from flask import Blueprint, jsonify, request
from models.color import Color

ws_color = Blueprint('ws_color', __name__)
color_model = Color()

@ws_color.route('/colores/listar', methods=['GET'])
def listar_colores():
    """Listar TODOS los colores para administración"""
    try:
        exito, resultado = color_model.listar_todos()
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Colores obtenidos correctamente',
                'data': resultado
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': resultado
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


@ws_color.route('/colores/obtener/<int:id_color>', methods=['GET'])
def obtener_color(id_color):
    """Obtener un color específico por ID"""
    try:
        exito, resultado = color_model.obtener_por_id(id_color)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Color obtenido correctamente',
                'data': resultado
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': resultado
            }), 404
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


@ws_color.route('/colores/crear', methods=['POST'])
def crear_color():
    """Crear un nuevo color"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': False,
                'message': 'No se recibieron datos'
            }), 400
        
        nombre = data.get('nombre', '').strip()
        
        if not nombre:
            return jsonify({
                'status': False,
                'message': 'El nombre del color es requerido'
            }), 400
        
        # Crear color
        exito, resultado = color_model.crear(nombre)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Color creado correctamente',
                'data': {'id_color': resultado}
            }), 201
        else:
            return jsonify({
                'status': False,
                'message': resultado
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


@ws_color.route('/colores/modificar/<int:id_color>', methods=['PUT'])
def modificar_color(id_color):
    """Modificar un color existente"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': False,
                'message': 'No se recibieron datos'
            }), 400
        
        nombre = data.get('nombre', '').strip()
        
        if not nombre:
            return jsonify({
                'status': False,
                'message': 'El nombre del color es requerido'
            }), 400
        
        # Modificar color
        exito, mensaje = color_model.modificar(id_color, nombre)
        
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
            'message': f'Error en el servidor: {str(e)}'
        }), 500


@ws_color.route('/colores/cambiar-estado/<int:id_color>', methods=['PATCH'])
def cambiar_estado_color(id_color):
    """Cambiar estado de un color (activar/desactivar)"""
    try:
        exito, mensaje = color_model.cambiar_estado(id_color)
        
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
            'message': f'Error en el servidor: {str(e)}'
        }), 500


@ws_color.route('/colores/eliminar/<int:id_color>', methods=['DELETE'])
def eliminar_color(id_color):
    """Eliminar un color (lógico)"""
    try:
        # Verificar si tiene productos asociados
        total_productos = color_model.contar_productos(id_color)
        
        if total_productos > 0:
            return jsonify({
                'status': False,
                'message': f'No se puede eliminar el color porque tiene {total_productos} producto(s) asociado(s).'
            }), 400
        
        # Eliminar lógicamente
        exito, mensaje = color_model.eliminar_logico(id_color)
        
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
            'message': f'Error en el servidor: {str(e)}'
        }), 500


@ws_color.route('/colores/estadisticas', methods=['GET'])
def estadisticas_colores():
    """Obtener estadísticas de colores"""
    try:
        exito, colores = color_model.listar_todos()
        
        if not exito:
            return jsonify({
                'status': False,
                'message': 'Error al obtener estadísticas'
            }), 500
        
        estadisticas = []
        for c in colores:
            total_productos = color_model.contar_productos(c['id_color'])
            estadisticas.append({
                'id_color': c['id_color'],
                'nombre': c['nombre'],
                'estado': c['estado'],
                'total_productos': total_productos
            })
        
        return jsonify({
            'status': True,
            'message': 'Estadísticas obtenidas correctamente',
            'data': estadisticas
        }), 200
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500