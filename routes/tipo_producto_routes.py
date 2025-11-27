from flask import Blueprint, jsonify, request
from models.tipo_producto import TipoProducto

ws_tipo_producto = Blueprint('ws_tipo_producto', __name__)

# ============================================
# ENDPOINTS EXISTENTES (Frontend público)
# ============================================

@ws_tipo_producto.route('/tipos/listar', methods=['GET'])
def listar_tipos():
    """
    ---
    tags:
      - Tipos de Producto
    summary: Listar tipos de producto activos
    description: Obtiene la lista de todos los tipos de producto activos CON opción 'Todos' al inicio para filtros
    responses:
      200:
        description: Tipos listados correctamente
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
                    example: -1
                  idTipoProd:
                    type: integer
                    example: -1
                    description: Alias para Android
                  nombre:
                    type: string
                    example: "Todos"
                  descripcion:
                    type: string
      500:
        description: Error en el servidor
    """
    try:
        tipo_producto = TipoProducto()
        exito, resultado = tipo_producto.listar_tipos()
        
        if exito:
            # ✅ AGREGAR "TODOS" AL INICIO
            todos = {
                'id_tipo_prod': -1,
                'idTipoProd': -1,  # ✅ ALIAS PARA ANDROID
                'nombre': 'Todos',
                'descripcion': 'Mostrar todos los productos'
            }
            
            # ✅ AGREGAR ALIAS A CADA TIPO
            tipos_con_alias = []
            for tipo in resultado:
                tipo['idTipoProd'] = tipo['id_tipo_prod']  # ✅ AGREGAR ALIAS
                tipos_con_alias.append(tipo)
            
            # Insertar "Todos" al inicio
            tipos_con_alias.insert(0, todos)
            
            return jsonify({
                'status': True,
                'data': tipos_con_alias,
                'message': 'Tipos listados correctamente'
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

# ============================================
# ENDPOINTS CRUD (Dashboard/Admin)
# ============================================

@ws_tipo_producto.route('/tipos/listar-admin', methods=['GET'])
def listar_tipos_admin():
    """
    ---
    tags:
      - Tipos de Producto
    summary: Listar todos los tipos (admin)
    description: Listar TODOS los tipos de producto (activos e inactivos) para el dashboard de administración
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
                  estado:
                    type: boolean
      500:
        description: Error en el servidor
    """
    try:
        tipo_producto = TipoProducto()
        exito, resultado = tipo_producto.listar()
        
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


@ws_tipo_producto.route('/tipos/obtener/<int:id_tipo_prod>', methods=['GET'])
def obtener_tipo(id_tipo_prod):
    """
    ---
    tags:
      - Tipos de Producto
    summary: Obtener tipo de producto por ID
    description: Obtiene un tipo de producto específico por su ID
    parameters:
      - name: id_tipo_prod
        in: path
        type: integer
        required: true
        description: ID del tipo de producto
    responses:
      200:
        description: Tipo de producto obtenido correctamente
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
                id_tipo_prod:
                  type: integer
                nombre:
                  type: string
                estado:
                  type: boolean
      404:
        description: Tipo de producto no encontrado
      500:
        description: Error en el servidor
    """
    try:
        tipo_producto = TipoProducto()
        exito, resultado = tipo_producto.obtener_por_id(id_tipo_prod)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Tipo de producto obtenido correctamente',
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


@ws_tipo_producto.route('/tipos/crear', methods=['POST'])
def crear_tipo():
    """
    ---
    tags:
      - Tipos de Producto
    summary: Crear nuevo tipo de producto
    description: Crea un nuevo tipo de producto en el sistema
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - nombre
          properties:
            nombre:
              type: string
              description: Nombre del tipo de producto
              example: "Ropa"
    responses:
      201:
        description: Tipo de producto creado correctamente
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
                id_tipo_prod:
                  type: integer
      400:
        description: Datos inválidos o incompletos
      500:
        description: Error en el servidor
    """
    try:
        data = request.get_json()
        
        # Validaciones
        if not data or 'nombre' not in data:
            return jsonify({
                'status': False,
                'message': 'El nombre del tipo de producto es requerido'
            }), 400
        
        nombre = data.get('nombre', '').strip()
        
        if not nombre:
            return jsonify({
                'status': False,
                'message': 'El nombre del tipo de producto no puede estar vacío'
            }), 400
        
        # Crear tipo de producto
        tipo_producto = TipoProducto()
        exito, resultado = tipo_producto.crear(nombre)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Tipo de producto creado correctamente',
                'data': {'id_tipo_prod': resultado}
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


@ws_tipo_producto.route('/tipos/modificar/<int:id_tipo_prod>', methods=['PUT'])
def modificar_tipo(id_tipo_prod):
    """
    ---
    tags:
      - Tipos de Producto
    summary: Modificar tipo de producto existente
    description: Actualiza los datos de un tipo de producto existente
    parameters:
      - name: id_tipo_prod
        in: path
        type: integer
        required: true
        description: ID del tipo de producto
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - nombre
          properties:
            nombre:
              type: string
              description: Nombre actualizado del tipo de producto
              example: "Ropa Deportiva"
    responses:
      200:
        description: Tipo de producto modificado correctamente
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
        if not data or 'nombre' not in data:
            return jsonify({
                'status': False,
                'message': 'El nombre del tipo de producto es requerido'
            }), 400
        
        nombre = data.get('nombre', '').strip()
        
        if not nombre:
            return jsonify({
                'status': False,
                'message': 'El nombre del tipo de producto no puede estar vacío'
            }), 400
        
        # Modificar tipo de producto
        tipo_producto = TipoProducto()
        exito, mensaje = tipo_producto.modificar(id_tipo_prod, nombre)
        
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


@ws_tipo_producto.route('/tipos/cambiar-estado/<int:id_tipo_prod>', methods=['PATCH'])
def cambiar_estado_tipo(id_tipo_prod):
    """
    ---
    tags:
      - Tipos de Producto
    summary: Cambiar estado de tipo de producto
    description: Cambia el estado de un tipo de producto entre activo e inactivo
    parameters:
      - name: id_tipo_prod
        in: path
        type: integer
        required: true
        description: ID del tipo de producto
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
        tipo_producto = TipoProducto()
        exito, mensaje = tipo_producto.cambiar_estado(id_tipo_prod)
        
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


@ws_tipo_producto.route('/tipos/eliminar/<int:id_tipo_prod>', methods=['DELETE'])
def eliminar_tipo(id_tipo_prod):
    """
    ---
    tags:
      - Tipos de Producto
    summary: Eliminar tipo de producto permanentemente
    description: Elimina FÍSICAMENTE un tipo de producto de la base de datos (DELETE permanente). No se puede eliminar si tiene modelos asociados
    parameters:
      - name: id_tipo_prod
        in: path
        type: integer
        required: true
        description: ID del tipo de producto
    responses:
      200:
        description: Tipo de producto eliminado correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
      400:
        description: No se puede eliminar el tipo o error en los datos
      500:
        description: Error en el servidor
    """
    try:
        tipo_producto = TipoProducto()
        
        # Verificar si tiene modelos asociados (activos o inactivos)
        total_modelos = tipo_producto.contar_modelos(id_tipo_prod)
        
        if total_modelos > 0:
            return jsonify({
                'status': False,
                'message': f'No se puede eliminar el tipo de producto porque tiene {total_modelos} modelo(s) asociado(s). Primero debe eliminar o reasignar los modelos.'
            }), 400
        
        # Eliminar FÍSICAMENTE el tipo de producto (DELETE FROM)
        exito, mensaje = tipo_producto.eliminar_fisico(id_tipo_prod)
        
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


@ws_tipo_producto.route('/tipos/estadisticas', methods=['GET'])
def estadisticas_tipos():
    """
    ---
    tags:
      - Tipos de Producto
    summary: Obtener estadísticas de tipos de producto
    description: Obtiene estadísticas completas incluyendo cantidad de modelos por tipo de producto
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
                  id_tipo_prod:
                    type: integer
                  nombre:
                    type: string
                  estado:
                    type: boolean
                  total_modelos:
                    type: integer
      500:
        description: Error en el servidor
    """
    try:
        tipo_producto = TipoProducto()
        exito, tipos = tipo_producto.listar()
        
        if not exito:
            return jsonify({
                'status': False,
                'message': 'Error al obtener estadísticas'
            }), 500
        
        estadisticas = []
        for t in tipos:
            total_modelos = tipo_producto.contar_modelos(t['id_tipo_prod'])
            estadisticas.append({
                'id_tipo_prod': t['id_tipo_prod'],
                'nombre': t['nombre'],
                'estado': t['estado'],
                'total_modelos': total_modelos
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