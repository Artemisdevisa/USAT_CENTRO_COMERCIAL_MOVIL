from flask import Blueprint, jsonify, request
from models.resenia import Resenia

ws_resenia = Blueprint('ws_resenia', __name__)

# ============================================
# LISTAR RESEÑAS POR PRODUCTO
# ============================================
@ws_resenia.route('/resenias/producto/<int:id_prod_color>', methods=['GET'])
def listar_resenias_producto(id_prod_color):
    """Listar todas las reseñas de un producto específico"""
    try:
        resenia = Resenia()
        exito, resultado = resenia.listar_por_producto(id_prod_color)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Reseñas obtenidas correctamente',
                'data': resultado
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': resultado,
                'data': []
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}',
            'data': []
        }), 500


# ============================================
# LISTAR RESEÑAS POR USUARIO
# ============================================
@ws_resenia.route('/resenias/usuario/<int:id_usuario>', methods=['GET'])
def listar_resenias_usuario(id_usuario):
    """Listar todas las reseñas de un usuario específico"""
    try:
        resenia = Resenia()
        exito, resultado = resenia.listar_por_usuario(id_usuario)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Reseñas obtenidas correctamente',
                'data': resultado
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': resultado,
                'data': []
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}',
            'data': []
        }), 500


# ============================================
# OBTENER RESEÑA POR ID
# ============================================
@ws_resenia.route('/resenias/obtener/<int:id_resenia>', methods=['GET'])
def obtener_resenia(id_resenia):
    """Obtener una reseña específica por ID"""
    try:
        resenia = Resenia()
        exito, resultado = resenia.obtener_por_id(id_resenia)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Reseña obtenida correctamente',
                'data': resultado
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': resultado,
                'data': None
            }), 404
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}',
            'data': None
        }), 500


# ============================================
# CREAR RESEÑA
# ============================================
@ws_resenia.route('/resenias/crear', methods=['POST'])
def crear_resenia():
    """Crear una nueva reseña"""
    try:
        data = request.get_json()
        
        # Validaciones
        if not data:
            return jsonify({
                'status': False,
                'message': 'No se recibieron datos'
            }), 400
        
        # Validar campos requeridos
        campos_requeridos = ['id_prod_color', 'id_det_vent', 'id_usuario', 'titulo', 'comentario', 'calificacion']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({
                    'status': False,
                    'message': f'El campo {campo} es requerido'
                }), 400
        
        id_prod_color = data.get('id_prod_color')
        id_det_vent = data.get('id_det_vent')
        id_usuario = data.get('id_usuario')
        titulo = data.get('titulo', '').strip()
        comentario = data.get('comentario', '').strip()
        calificacion = data.get('calificacion')
        
        # Validaciones adicionales
        if not titulo or not comentario:
            return jsonify({
                'status': False,
                'message': 'El título y el comentario no pueden estar vacíos'
            }), 400
        
        if not isinstance(calificacion, int) or calificacion < 1 or calificacion > 5:
            return jsonify({
                'status': False,
                'message': 'La calificación debe ser un número entre 1 y 5'
            }), 400
        
        # Crear reseña
        resenia = Resenia()
        exito, resultado = resenia.crear(id_prod_color, id_det_vent, id_usuario, titulo, comentario, calificacion)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Reseña creada correctamente',
                'data': {'id_resenia': resultado}
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


# ============================================
# MODIFICAR RESEÑA
# ============================================
@ws_resenia.route('/resenias/modificar/<int:id_resenia>', methods=['PUT'])
def modificar_resenia(id_resenia):
    """Modificar una reseña existente"""
    try:
        data = request.get_json()
        
        # Validaciones
        if not data:
            return jsonify({
                'status': False,
                'message': 'No se recibieron datos'
            }), 400
        
        # Validar campos requeridos
        campos_requeridos = ['titulo', 'comentario', 'calificacion']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({
                    'status': False,
                    'message': f'El campo {campo} es requerido'
                }), 400
        
        titulo = data.get('titulo', '').strip()
        comentario = data.get('comentario', '').strip()
        calificacion = data.get('calificacion')
        
        # Validaciones adicionales
        if not titulo or not comentario:
            return jsonify({
                'status': False,
                'message': 'El título y el comentario no pueden estar vacíos'
            }), 400
        
        if not isinstance(calificacion, int) or calificacion < 1 or calificacion > 5:
            return jsonify({
                'status': False,
                'message': 'La calificación debe ser un número entre 1 y 5'
            }), 400
        
        # Modificar reseña
        resenia = Resenia()
        exito, mensaje = resenia.modificar(id_resenia, titulo, comentario, calificacion)
        
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


# ============================================
# ELIMINAR RESEÑA
# ============================================
@ws_resenia.route('/resenias/eliminar/<int:id_resenia>', methods=['DELETE'])
def eliminar_resenia(id_resenia):
    """Eliminar lógicamente una reseña"""
    try:
        resenia = Resenia()
        exito, mensaje = resenia.eliminar(id_resenia)
        
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


# ============================================
# OBTENER PROMEDIO DE CALIFICACIÓN
# ============================================
@ws_resenia.route('/resenias/promedio/<int:id_prod_color>', methods=['GET'])
def obtener_promedio(id_prod_color):
    """Obtener el promedio de calificación de un producto"""
    try:
        resenia = Resenia()
        exito, promedio = resenia.obtener_promedio_calificacion(id_prod_color)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Promedio obtenido correctamente',
                'data': {'promedio': promedio}
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': promedio
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


# ============================================
# CONTAR RESEÑAS
# ============================================
@ws_resenia.route('/resenias/contar/<int:id_prod_color>', methods=['GET'])
def contar_resenias(id_prod_color):
    """Contar el total de reseñas de un producto"""
    try:
        resenia = Resenia()
        total = resenia.contar_por_producto(id_prod_color)
        
        return jsonify({
            'status': True,
            'message': 'Total obtenido correctamente',
            'data': {'total': total}
        }), 200
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


# ============================================
# VERIFICAR SI USUARIO YA RESEÑÓ
# ============================================
@ws_resenia.route('/resenias/verificar-existencia', methods=['POST'])
def verificar_existencia():
    """Verificar si un usuario ya reseñó un producto"""
    try:
        data = request.get_json()
        
        if not data or 'id_prod_color' not in data or 'id_usuario' not in data:
            return jsonify({
                'status': False,
                'message': 'Se requieren id_prod_color e id_usuario'
            }), 400
        
        id_prod_color = data.get('id_prod_color')
        id_usuario = data.get('id_usuario')
        
        resenia = Resenia()
        existe = resenia.verificar_existencia(id_prod_color, id_usuario)
        
        return jsonify({
            'status': True,
            'message': 'Verificación completada',
            'data': {'existe': existe}
        }), 200
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


# ============================================
# VERIFICAR SI USUARIO PUEDE RESEÑAR
# ============================================
@ws_resenia.route('/resenias/puede-reseniar', methods=['POST'])
def puede_reseniar():
    """Verificar si un usuario puede reseñar un producto (debe haberlo comprado)"""
    try:
        data = request.get_json()
        
        if not data or 'id_prod_color' not in data or 'id_usuario' not in data:
            return jsonify({
                'status': False,
                'message': 'Se requieren id_prod_color e id_usuario'
            }), 400
        
        id_prod_color = data.get('id_prod_color')
        id_usuario = data.get('id_usuario')
        
        resenia = Resenia()
        puede = resenia.puede_reseniar(id_prod_color, id_usuario)
        
        return jsonify({
            'status': True,
            'message': 'Verificación completada',
            'data': {'puede_reseniar': puede}
        }), 200
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


# ============================================
# OBTENER ESTADÍSTICAS DE CALIFICACIONES
# ============================================
@ws_resenia.route('/resenias/estadisticas/<int:id_prod_color>', methods=['GET'])
def obtener_estadisticas(id_prod_color):
    """Obtener estadísticas detalladas de calificaciones de un producto"""
    try:
        resenia = Resenia()
        exito, estadisticas = resenia.obtener_estadisticas(id_prod_color)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Estadísticas obtenidas correctamente',
                'data': estadisticas
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': estadisticas
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500