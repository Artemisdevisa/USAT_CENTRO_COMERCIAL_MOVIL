from flask import Blueprint, request, jsonify
from models.provincia import Provincia

ws_provincia = Blueprint('ws_provincia', __name__)
provincia_model = Provincia()

@ws_provincia.route('/provincias/listar/<int:id_dep>', methods=['GET'])
def listar_por_departamento(id_dep):
    """
    Listar provincias por departamento
    ---
    tags:
      - Provincias
    parameters:
      - name: id_dep
        in: path
        type: integer
        required: true
        description: ID del departamento
    responses:
      200:
        description: Provincias obtenidas correctamente
      500:
        description: Error del servidor
    """
    try:
        resultado, data = provincia_model.listar_por_departamento(id_dep)
        
        if resultado:
            return jsonify({
                'status': True,
                'data': data,
                'message': 'Provincias obtenidas correctamente'
            }), 200
        else:
            return jsonify({
                'status': False,
                'data': [],
                'message': data
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'data': [],
            'message': f'Error: {str(e)}'
        }), 500

@ws_provincia.route('/provincias/crear', methods=['POST'])
def crear():
    """
    Crear provincia
    ---
    tags:
      - Provincias
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            id_dep:
              type: integer
              example: 1
            nombre:
              type: string
              example: Lima
    responses:
      201:
        description: Provincia creada correctamente
      400:
        description: Faltan datos requeridos
    """
    try:
        data = request.get_json()
        id_dep = data.get('id_dep')
        nombre = data.get('nombre')
        
        if not id_dep or not nombre:
            return jsonify({
                'status': False,
                'message': 'Departamento y nombre son requeridos'
            }), 400
        
        resultado, data_result = provincia_model.crear(id_dep, nombre)
        
        if resultado:
            return jsonify({
                'status': True,
                'data': {'id_prov': data_result},
                'message': 'Provincia creada correctamente'
            }), 201
        else:
            return jsonify({
                'status': False,
                'message': data_result
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500

@ws_provincia.route('/provincias/modificar', methods=['PUT'])
def modificar():
    """
    Modificar provincia
    ---
    tags:
      - Provincias
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            id_prov:
              type: integer
              example: 1
            id_dep:
              type: integer
              example: 1
            nombre:
              type: string
              example: Lima Actualizada
    responses:
      200:
        description: Provincia modificada correctamente
      400:
        description: Faltan datos requeridos
    """
    try:
        data = request.get_json()
        id_prov = data.get('id_prov')
        id_dep = data.get('id_dep')
        nombre = data.get('nombre')
        
        if not id_prov or not id_dep or not nombre:
            return jsonify({
                'status': False,
                'message': 'Todos los campos son requeridos'
            }), 400
        
        resultado, mensaje = provincia_model.modificar(id_prov, id_dep, nombre)
        
        if resultado:
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

@ws_provincia.route('/provincias/eliminar/<int:id_prov>', methods=['DELETE'])
def eliminar(id_prov):
    """
    Eliminar provincia
    ---
    tags:
      - Provincias
    parameters:
      - name: id_prov
        in: path
        type: integer
        required: true
        description: ID de la provincia
    responses:
      200:
        description: Provincia eliminada correctamente
      400:
        description: Error al eliminar
    """
    try:
        resultado, mensaje = provincia_model.eliminar(id_prov)
        
        if resultado:
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