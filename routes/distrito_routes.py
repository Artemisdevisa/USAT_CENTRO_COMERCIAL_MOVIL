from flask import Blueprint, request, jsonify
from models.distrito import Distrito

ws_distrito = Blueprint('ws_distrito', __name__)
distrito_model = Distrito()

@ws_distrito.route('/distritos/listar/<int:id_prov>', methods=['GET'])
def listar_por_provincia(id_prov):
    """
    Listar distritos por provincia
    ---
    tags:
      - Distritos
    parameters:
      - name: id_prov
        in: path
        type: integer
        required: true
        description: ID de la provincia
    responses:
      200:
        description: Distritos obtenidos correctamente
      500:
        description: Error del servidor
    """
    try:
        resultado, data = distrito_model.listar_por_provincia(id_prov)
        
        if resultado:
            return jsonify({
                'status': True,
                'data': data,
                'message': 'Distritos obtenidos correctamente'
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

@ws_distrito.route('/distritos/crear', methods=['POST'])
def crear():
    """
    Crear distrito
    ---
    tags:
      - Distritos
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            id_prov:
              type: integer
              example: 1
            nombre:
              type: string
              example: San Isidro
    responses:
      201:
        description: Distrito creado correctamente
      400:
        description: Faltan datos requeridos
    """
    try:
        data = request.get_json()
        id_prov = data.get('id_prov')
        nombre = data.get('nombre')
        
        if not id_prov or not nombre:
            return jsonify({
                'status': False,
                'message': 'Provincia y nombre son requeridos'
            }), 400
        
        resultado, data_result = distrito_model.crear(id_prov, nombre)
        
        if resultado:
            return jsonify({
                'status': True,
                'data': {'id_dist': data_result},
                'message': 'Distrito creado correctamente'
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

@ws_distrito.route('/distritos/modificar', methods=['PUT'])
def modificar():
    """
    Modificar distrito
    ---
    tags:
      - Distritos
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            id_dist:
              type: integer
              example: 1
            id_prov:
              type: integer
              example: 1
            nombre:
              type: string
              example: San Isidro Actualizado
    responses:
      200:
        description: Distrito modificado correctamente
      400:
        description: Faltan datos requeridos
    """
    try:
        data = request.get_json()
        id_dist = data.get('id_dist')
        id_prov = data.get('id_prov')
        nombre = data.get('nombre')
        
        if not id_dist or not id_prov or not nombre:
            return jsonify({
                'status': False,
                'message': 'Todos los campos son requeridos'
            }), 400
        
        resultado, mensaje = distrito_model.modificar(id_dist, id_prov, nombre)
        
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

@ws_distrito.route('/distritos/eliminar/<int:id_dist>', methods=['DELETE'])
def eliminar(id_dist):
    """
    Eliminar distrito
    ---
    tags:
      - Distritos
    parameters:
      - name: id_dist
        in: path
        type: integer
        required: true
        description: ID del distrito
    responses:
      200:
        description: Distrito eliminado correctamente
      400:
        description: Error al eliminar
    """
    try:
        resultado, mensaje = distrito_model.eliminar(id_dist)
        
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