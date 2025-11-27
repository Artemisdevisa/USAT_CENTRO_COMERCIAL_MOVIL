from flask import Blueprint, request, jsonify
from models.rol import Rol

ws_rol = Blueprint('ws_rol', __name__)

@ws_rol.route('/roles/listar', methods=['GET'])
def listar_roles():
    """
    ---
    tags:
      - Roles
    summary: Listar todos los roles
    description: Obtiene una lista de todos los roles activos del sistema
    responses:
      200:
        description: Roles obtenidos correctamente
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
                  id_rol:
                    type: integer
                  nombre:
                    type: string
      500:
        description: Error interno del servidor
    """
    try:
        rol = Rol()
        exito, resultado = rol.listar()
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Roles obtenidos correctamente',
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

@ws_rol.route('/roles/obtener/<int:id_rol>', methods=['GET'])
def obtener_rol(id_rol):
    """
    ---
    tags:
      - Roles
    summary: Obtener rol por ID
    description: Obtiene un rol específico por su ID
    parameters:
      - name: id_rol
        in: path
        type: integer
        required: true
        description: ID del rol
    responses:
      200:
        description: Rol obtenido correctamente
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
                id_rol:
                  type: integer
                nombre:
                  type: string
      404:
        description: Rol no encontrado
      500:
        description: Error interno del servidor
    """
    try:
        rol = Rol()
        exito, resultado = rol.obtener_por_id(id_rol)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Rol obtenido correctamente',
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

@ws_rol.route('/roles/crear', methods=['POST'])
def crear_rol():
    """
    ---
    tags:
      - Roles
    summary: Crear un nuevo rol
    description: Crea un nuevo rol en el sistema
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
              description: Nombre del rol
              example: "Administrador"
    responses:
      201:
        description: Rol creado correctamente
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
                id_rol:
                  type: integer
      400:
        description: Datos inválidos
      500:
        description: Error en el servidor
    """
    try:
        data = request.get_json()
        
        # Validaciones
        if not data or 'nombre' not in data:
            return jsonify({
                'status': False,
                'message': 'El nombre del rol es requerido'
            }), 400
        
        nombre = data.get('nombre', '').strip()
        
        if not nombre:
            return jsonify({
                'status': False,
                'message': 'El nombre del rol no puede estar vacío'
            }), 400
        
        # Crear rol
        rol = Rol()
        exito, resultado = rol.crear(nombre)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Rol creado correctamente',
                'data': {'id_rol': resultado}
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

@ws_rol.route('/roles/modificar/<int:id_rol>', methods=['PUT'])
def modificar_rol(id_rol):
    """
    ---
    tags:
      - Roles
    summary: Modificar un rol existente
    description: Actualiza los datos de un rol existente
    parameters:
      - name: id_rol
        in: path
        type: integer
        required: true
        description: ID del rol
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
              description: Nombre actualizado del rol
              example: "Super Administrador"
    responses:
      200:
        description: Rol modificado correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
      400:
        description: Datos inválidos
      500:
        description: Error en el servidor
    """
    try:
        data = request.get_json()
        
        # Validaciones
        if not data or 'nombre' not in data:
            return jsonify({
                'status': False,
                'message': 'El nombre del rol es requerido'
            }), 400
        
        nombre = data.get('nombre', '').strip()
        
        if not nombre:
            return jsonify({
                'status': False,
                'message': 'El nombre del rol no puede estar vacío'
            }), 400
        
        # Modificar rol
        rol = Rol()
        exito, mensaje = rol.modificar(id_rol, nombre)
        
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

@ws_rol.route('/roles/eliminar/<int:id_rol>', methods=['DELETE'])
def eliminar_rol(id_rol):
    """
    ---
    tags:
      - Roles
    summary: Eliminar un rol
    description: Elimina lógicamente un rol del sistema. No se puede eliminar si tiene usuarios asociados
    parameters:
      - name: id_rol
        in: path
        type: integer
        required: true
        description: ID del rol
    responses:
      200:
        description: Rol eliminado correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
      400:
        description: No se puede eliminar el rol o error en los datos
      500:
        description: Error en el servidor
    """
    try:
        rol = Rol()
        
        # Verificar si tiene usuarios asociados
        total_usuarios = rol.contar_usuarios(id_rol)
        
        if total_usuarios > 0:
            return jsonify({
                'status': False,
                'message': f'No se puede eliminar el rol porque tiene {total_usuarios} usuario(s) asociado(s)'
            }), 400
        
        # Eliminar rol
        exito, mensaje = rol.eliminar(id_rol)
        
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

@ws_rol.route('/roles/estadisticas', methods=['GET'])
def estadisticas_roles():
    """
    ---
    tags:
      - Roles
    summary: Obtener estadísticas de roles
    description: Obtiene estadísticas completas de roles incluyendo cantidad de usuarios por rol
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
                  id_rol:
                    type: integer
                  nombre:
                    type: string
                  total_usuarios:
                    type: integer
      500:
        description: Error en el servidor
    """
    try:
        rol = Rol()
        exito, roles = rol.listar()
        
        if not exito:
            return jsonify({
                'status': False,
                'message': 'Error al obtener estadísticas'
            }), 500
        
        estadisticas = []
        for r in roles:
            total_usuarios = rol.contar_usuarios(r['id_rol'])
            estadisticas.append({
                'id_rol': r['id_rol'],
                'nombre': r['nombre'],
                'total_usuarios': total_usuarios
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