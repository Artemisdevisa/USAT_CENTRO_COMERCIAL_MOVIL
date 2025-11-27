from flask import Blueprint, jsonify, request
from models.marca import Marca

ws_marca = Blueprint('ws_marca', __name__)

@ws_marca.route('/marcas/listar', methods=['GET'])
def listar_marcas():
    """
    Listar todas las marcas
    ---
    tags:
      - Marcas
    responses:
      200:
        description: Marcas obtenidas correctamente
      500:
        description: Error del servidor
    """
    try:
        marca = Marca()
        exito, resultado = marca.listar()
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Marcas obtenidas correctamente',
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


@ws_marca.route('/marcas/obtener/<int:id_marca>', methods=['GET'])
def obtener_marca(id_marca):
    """
    Obtener una marca por ID
    ---
    tags:
      - Marcas
    parameters:
      - name: id_marca
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Marca obtenida correctamente
      404:
        description: Marca no encontrada
    """
    try:
        marca = Marca()
        exito, resultado = marca.obtener_por_id(id_marca)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Marca obtenida correctamente',
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


@ws_marca.route('/marcas/crear', methods=['POST'])
def crear_marca():
    """
    Crear una nueva marca
    ---
    tags:
      - Marcas
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            nombre:
              type: string
              example: Nike
    responses:
      201:
        description: Marca creada correctamente
      400:
        description: Datos inválidos
    """
    try:
        data = request.get_json()
        
        if not data or 'nombre' not in data:
            return jsonify({
                'status': False,
                'message': 'El nombre de la marca es requerido'
            }), 400
        
        nombre = data.get('nombre', '').strip()
        
        if not nombre:
            return jsonify({
                'status': False,
                'message': 'El nombre de la marca no puede estar vacío'
            }), 400
        
        marca = Marca()
        exito, resultado = marca.crear(nombre)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Marca creada correctamente',
                'data': {'id_marca': resultado}
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


@ws_marca.route('/marcas/modificar/<int:id_marca>', methods=['PUT'])
def modificar_marca(id_marca):
    """
    Modificar una marca existente
    ---
    tags:
      - Marcas
    parameters:
      - name: id_marca
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          properties:
            nombre:
              type: string
              example: Nike Updated
    responses:
      200:
        description: Marca modificada correctamente
      400:
        description: Error en los datos
    """
    try:
        data = request.get_json()
        
        if not data or 'nombre' not in data:
            return jsonify({
                'status': False,
                'message': 'El nombre de la marca es requerido'
            }), 400
        
        nombre = data.get('nombre', '').strip()
        
        if not nombre:
            return jsonify({
                'status': False,
                'message': 'El nombre de la marca no puede estar vacío'
            }), 400
        
        marca = Marca()
        exito, mensaje = marca.modificar(id_marca, nombre)
        
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


@ws_marca.route('/marcas/cambiar-estado/<int:id_marca>', methods=['PATCH'])
def cambiar_estado_marca(id_marca):
    """
    Cambiar estado de una marca
    ---
    tags:
      - Marcas
    parameters:
      - name: id_marca
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Estado cambiado correctamente
      400:
        description: Error al cambiar estado
    """
    try:
        marca = Marca()
        exito, mensaje = marca.cambiar_estado(id_marca)
        
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


@ws_marca.route('/marcas/eliminar/<int:id_marca>', methods=['DELETE'])
def eliminar_marca(id_marca):
    """
    Eliminar una marca
    ---
    tags:
      - Marcas
    parameters:
      - name: id_marca
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Marca eliminada correctamente
      400:
        description: No se puede eliminar la marca
    """
    try:
        marca = Marca()
        
        total_productos = marca.contar_productos(id_marca)
        
        if total_productos > 0:
            return jsonify({
                'status': False,
                'message': f'No se puede desactivar la marca porque tiene {total_productos} producto(s) activo(s) asociado(s)'
            }), 400
        
        exito, mensaje = marca.eliminar_logico(id_marca)
        
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


@ws_marca.route('/marcas/estadisticas', methods=['GET'])
def estadisticas_marcas():
    """
    Obtener estadísticas de marcas
    ---
    tags:
      - Marcas
    responses:
      200:
        description: Estadísticas obtenidas correctamente
      500:
        description: Error del servidor
    """
    try:
        marca = Marca()
        exito, marcas = marca.listar()
        
        if not exito:
            return jsonify({
                'status': False,
                'message': 'Error al obtener estadísticas'
            }), 500
        
        estadisticas = []
        for m in marcas:
            total_productos = marca.contar_productos(m['id_marca'])
            estadisticas.append({
                'id_marca': m['id_marca'],
                'nombre': m['nombre'],
                'estado': m['estado'],
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