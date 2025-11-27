from flask import Blueprint, jsonify, request
from models.tipo_modelo_producto import TipoModeloProducto

ws_tipo_modelo = Blueprint('ws_tipo_modelo', __name__)

# ============================================
# ENDPOINTS CRUD
# ============================================

@ws_tipo_modelo.route('/modelos/listar', methods=['GET'])
def listar_modelos():
    """
    ---
    tags:
      - Modelos de Producto
    summary: Listar todos los modelos
    description: Obtiene la lista de TODOS los modelos de producto del sistema
    responses:
      200:
        description: Modelos obtenidos correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
            data:
              type: array
              items:
                type: object
                properties:
                  id_tipo_modelo:
                    type: integer
                  id_tipo_prod:
                    type: integer
                  nombre:
                    type: string
                  nombre_tipo:
                    type: string
                  estado:
                    type: boolean
      500:
        description: Error en el servidor
    """
    try:
        modelo = TipoModeloProducto()
        exito, resultado = modelo.listar()
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Modelos obtenidos correctamente',
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


@ws_tipo_modelo.route('/modelos/obtener/<int:id_tipo_modelo>', methods=['GET'])
def obtener_modelo(id_tipo_modelo):
    """
    ---
    tags:
      - Modelos de Producto
    summary: Obtener modelo por ID
    description: Obtiene un modelo específico por su ID
    parameters:
      - name: id_tipo_modelo
        in: path
        type: integer
        required: true
        description: ID del modelo de producto
    responses:
      200:
        description: Modelo obtenido correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
            data:
              type: object
              properties:
                id_tipo_modelo:
                  type: integer
                id_tipo_prod:
                  type: integer
                nombre:
                  type: string
                estado:
                  type: boolean
      404:
        description: Modelo no encontrado
      500:
        description: Error en el servidor
    """
    try:
        modelo = TipoModeloProducto()
        exito, resultado = modelo.obtener_por_id(id_tipo_modelo)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Modelo obtenido correctamente',
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


@ws_tipo_modelo.route('/modelos/listar-por-tipo/<int:id_tipo_prod>', methods=['GET'])
def listar_por_tipo(id_tipo_prod):
    """
    ---
    tags:
      - Modelos de Producto
    summary: Listar modelos por tipo
    description: Obtiene los modelos de un tipo de producto específico (solo activos)
    parameters:
      - name: id_tipo_prod
        in: path
        type: integer
        required: true
        description: ID del tipo de producto
    responses:
      200:
        description: Modelos obtenidos correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
            data:
              type: array
              items:
                type: object
      500:
        description: Error en el servidor
    """
    try:
        modelo = TipoModeloProducto()
        exito, resultado = modelo.listar_por_tipo(id_tipo_prod)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Modelos obtenidos correctamente',
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


@ws_tipo_modelo.route('/modelos/crear', methods=['POST'])
def crear_modelo():
    """
    ---
    tags:
      - Modelos de Producto
    summary: Crear nuevo modelo
    description: Crea un nuevo modelo de producto
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - id_tipo_prod
            - nombre
          properties:
            id_tipo_prod:
              type: integer
              description: ID del tipo de producto
            nombre:
              type: string
              description: Nombre del modelo
              example: "Modelo Clásico"
    responses:
      201:
        description: Modelo creado correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
            data:
              type: object
              properties:
                id_tipo_modelo:
                  type: integer
      400:
        description: Datos inválidos o incompletos
      500:
        description: Error en el servidor
    """
    try:
        data = request.get_json()
        
        # Validaciones
        if not data or 'id_tipo_prod' not in data or 'nombre' not in data:
            return jsonify({
                'status': False,
                'message': 'El tipo de producto y el nombre del modelo son requeridos'
            }), 400
        
        id_tipo_prod = data.get('id_tipo_prod')
        nombre = data.get('nombre', '').strip()
        
        if not nombre:
            return jsonify({
                'status': False,
                'message': 'El nombre del modelo no puede estar vacío'
            }), 400
        
        if not id_tipo_prod or id_tipo_prod <= 0:
            return jsonify({
                'status': False,
                'message': 'Debe seleccionar un tipo de producto válido'
            }), 400
        
        # Crear modelo
        modelo = TipoModeloProducto()
        exito, resultado = modelo.crear(id_tipo_prod, nombre)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Modelo de producto creado correctamente',
                'data': {'id_tipo_modelo': resultado}
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


@ws_tipo_modelo.route('/modelos/modificar/<int:id_tipo_modelo>', methods=['PUT'])
def modificar_modelo(id_tipo_modelo):
    """
    ---
    tags:
      - Modelos de Producto
    summary: Modificar modelo existente
    description: Actualiza los datos de un modelo de producto existente
    parameters:
      - name: id_tipo_modelo
        in: path
        type: integer
        required: true
        description: ID del modelo de producto
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - id_tipo_prod
            - nombre
          properties:
            id_tipo_prod:
              type: integer
              description: ID del tipo de producto
            nombre:
              type: string
              description: Nombre actualizado del modelo
              example: "Modelo Premium"
    responses:
      200:
        description: Modelo modificado correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
      400:
        description: Datos inválidos o incompletos
      500:
        description: Error en el servidor
    """
    try:
        data = request.get_json()
        
        # Validaciones
        if not data or 'id_tipo_prod' not in data or 'nombre' not in data:
            return jsonify({
                'status': False,
                'message': 'El tipo de producto y el nombre del modelo son requeridos'
            }), 400
        
        id_tipo_prod = data.get('id_tipo_prod')
        nombre = data.get('nombre', '').strip()
        
        if not nombre:
            return jsonify({
                'status': False,
                'message': 'El nombre del modelo no puede estar vacío'
            }), 400
        
        if not id_tipo_prod or id_tipo_prod <= 0:
            return jsonify({
                'status': False,
                'message': 'Debe seleccionar un tipo de producto válido'
            }), 400
        
        # Modificar modelo
        modelo = TipoModeloProducto()
        exito, mensaje = modelo.modificar(id_tipo_modelo, id_tipo_prod, nombre)
        
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


@ws_tipo_modelo.route('/modelos/cambiar-estado/<int:id_tipo_modelo>', methods=['PATCH'])
def cambiar_estado_modelo(id_tipo_modelo):
    """
    ---
    tags:
      - Modelos de Producto
    summary: Cambiar estado de modelo
    description: Cambia el estado de un modelo entre activo e inactivo
    parameters:
      - name: id_tipo_modelo
        in: path
        type: integer
        required: true
        description: ID del modelo de producto
    responses:
      200:
        description: Estado cambiado correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
      400:
        description: Error al cambiar estado
      500:
        description: Error en el servidor
    """
    try:
        modelo = TipoModeloProducto()
        exito, mensaje = modelo.cambiar_estado(id_tipo_modelo)
        
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


@ws_tipo_modelo.route('/modelos/eliminar/<int:id_tipo_modelo>', methods=['DELETE'])
def eliminar_modelo(id_tipo_modelo):
    """
    ---
    tags:
      - Modelos de Producto
    summary: Eliminar modelo permanentemente
    description: Elimina FÍSICAMENTE un modelo de producto de la base de datos (DELETE permanente). No se puede eliminar si tiene productos asociados
    parameters:
      - name: id_tipo_modelo
        in: path
        type: integer
        required: true
        description: ID del modelo de producto
    responses:
      200:
        description: Modelo eliminado correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
      400:
        description: No se puede eliminar el modelo o error en los datos
      500:
        description: Error en el servidor
    """
    try:
        modelo = TipoModeloProducto()
        
        # Verificar si tiene productos asociados
        total_productos = modelo.contar_productos(id_tipo_modelo)
        
        if total_productos > 0:
            return jsonify({
                'status': False,
                'message': f'No se puede eliminar el modelo porque tiene {total_productos} producto(s) asociado(s). Primero debe eliminar o reasignar los productos.'
            }), 400
        
        # Eliminar FÍSICAMENTE (DELETE FROM)
        exito, mensaje = modelo.eliminar_fisico(id_tipo_modelo)
        
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


@ws_tipo_modelo.route('/modelos/estadisticas', methods=['GET'])
def estadisticas_modelos():
    """
    ---
    tags:
      - Modelos de Producto
    summary: Obtener estadísticas de modelos
    description: Obtiene estadísticas completas incluyendo cantidad de productos por modelo
    responses:
      200:
        description: Estadísticas obtenidas correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
            data:
              type: array
              items:
                type: object
                properties:
                  id_tipo_modelo:
                    type: integer
                  id_tipo_prod:
                    type: integer
                  nombre_tipo:
                    type: string
                  nombre:
                    type: string
                  estado:
                    type: boolean
                  total_productos:
                    type: integer
      500:
        description: Error en el servidor
    """
    try:
        modelo = TipoModeloProducto()
        exito, modelos = modelo.listar()
        
        if not exito:
            return jsonify({
                'status': False,
                'message': 'Error al obtener estadísticas'
            }), 500
        
        estadisticas = []
        for m in modelos:
            total_productos = modelo.contar_productos(m['id_tipo_modelo'])
            estadisticas.append({
                'id_tipo_modelo': m['id_tipo_modelo'],
                'id_tipo_prod': m['id_tipo_prod'],
                'nombre_tipo': m['nombre_tipo'],
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


@ws_tipo_modelo.route('/modelos/tipos-activos', methods=['GET'])
def listar_tipos_activos():
    """
    ---
    tags:
      - Modelos de Producto
    summary: Listar tipos de producto activos
    description: Obtiene la lista de tipos de producto activos para los selects
    responses:
      200:
        description: Tipos de producto obtenidos correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
            data:
              type: array
              items:
                type: object
                properties:
                  id_tipo_prod:
                    type: integer
                  nombre:
                    type: string
      500:
        description: Error en el servidor
    """
    try:
        modelo = TipoModeloProducto()
        exito, resultado = modelo.listar_tipos_activos()
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Tipos de producto obtenidos correctamente',
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