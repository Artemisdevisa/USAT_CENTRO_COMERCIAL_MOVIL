from flask import Blueprint, jsonify, request
from models.temporada import Temporada

ws_temporada = Blueprint('ws_temporada', __name__)

@ws_temporada.route('/temporadas/listar', methods=['GET'])
def listar_temporadas():
    """Listar TODAS las temporadas (activas e inactivas) para el dashboard"""
    try:
        temporada = Temporada()
        exito, resultado = temporada.listar()
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Temporadas obtenidas correctamente',
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


@ws_temporada.route('/temporadas/obtener/<int:id_temporada>', methods=['GET'])
def obtener_temporada(id_temporada):
    """Obtener una temporada específica por ID"""
    try:
        temporada = Temporada()
        exito, resultado = temporada.obtener_por_id(id_temporada)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Temporada obtenida correctamente',
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


@ws_temporada.route('/temporadas/crear', methods=['POST'])
def crear_temporada():
    """Crear una nueva temporada"""
    try:
        data = request.get_json()
        
        # Validaciones
        if not data:
            return jsonify({
                'status': False,
                'message': 'No se recibieron datos'
            }), 400
        
        nombre = data.get('nombre', '').strip()
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        if not nombre:
            return jsonify({
                'status': False,
                'message': 'El nombre de la temporada es requerido'
            }), 400
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({
                'status': False,
                'message': 'Las fechas de inicio y fin son requeridas'
            }), 400
        
        # Crear temporada
        temporada = Temporada()
        exito, resultado = temporada.crear(nombre, fecha_inicio, fecha_fin)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Temporada creada correctamente',
                'data': {'id_temporada': resultado}
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


@ws_temporada.route('/temporadas/modificar/<int:id_temporada>', methods=['PUT'])
def modificar_temporada(id_temporada):
    """Modificar una temporada existente"""
    try:
        data = request.get_json()
        
        # Validaciones
        if not data:
            return jsonify({
                'status': False,
                'message': 'No se recibieron datos'
            }), 400
        
        nombre = data.get('nombre', '').strip()
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        if not nombre:
            return jsonify({
                'status': False,
                'message': 'El nombre de la temporada es requerido'
            }), 400
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({
                'status': False,
                'message': 'Las fechas de inicio y fin son requeridas'
            }), 400
        
        # Modificar temporada
        temporada = Temporada()
        exito, mensaje = temporada.modificar(id_temporada, nombre, fecha_inicio, fecha_fin)
        
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


@ws_temporada.route('/temporadas/cambiar-estado/<int:id_temporada>', methods=['PATCH'])
def cambiar_estado_temporada(id_temporada):
    """Cambiar estado de una temporada (activar/desactivar)"""
    try:
        temporada = Temporada()
        exito, mensaje = temporada.cambiar_estado(id_temporada)
        
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


@ws_temporada.route('/temporadas/eliminar/<int:id_temporada>', methods=['DELETE'])
def eliminar_temporada(id_temporada):
    """Eliminar lógicamente una temporada (desactivar)"""
    try:
        temporada = Temporada()
        
        # Verificar si tiene productos activos asociados
        total_productos = temporada.contar_productos(id_temporada)
        
        if total_productos > 0:
            return jsonify({
                'status': False,
                'message': f'No se puede desactivar la temporada porque tiene {total_productos} producto(s) activo(s) asociado(s)'
            }), 400
        
        # Eliminar (desactivar) temporada
        exito, mensaje = temporada.eliminar_logico(id_temporada)
        
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


@ws_temporada.route('/temporadas/estadisticas', methods=['GET'])
def estadisticas_temporadas():
    """Obtener estadísticas de temporadas y productos"""
    try:
        temporada = Temporada()
        exito, temporadas = temporada.listar()
        
        if not exito:
            return jsonify({
                'status': False,
                'message': 'Error al obtener estadísticas'
            }), 500
        
        estadisticas = []
        for t in temporadas:
            total_productos = temporada.contar_productos(t['id_temporada'])
            estadisticas.append({
                'id_temporada': t['id_temporada'],
                'nombre': t['nombre'],
                'fecha_inicio': t['fecha_inicio'],
                'fecha_fin': t['fecha_fin'],
                'estado': t['estado'],
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