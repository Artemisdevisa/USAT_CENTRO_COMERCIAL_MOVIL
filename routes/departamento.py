from flask import Blueprint, request, jsonify, render_template
from models.departamento import Departamento

ws_departamento = Blueprint('ws_departamento', __name__)
departamento_model = Departamento()

# ==================== VISTAS HTML ====================

@ws_departamento.route('/departamentos', methods=['GET'])
def departamentos_page():
    """Página de lista de departamentos"""
    return render_template('departamento/lista.html')

# ==================== API ENDPOINTS ====================

@ws_departamento.route('/departamentos/listar', methods=['GET'])
def listar():
    """
    Listar departamentos
    ---
    tags:
      - Departamentos
    responses:
      200:
        description: Departamentos obtenidos correctamente
      500:
        description: Error del servidor
    """
    try:
        resultado, data = departamento_model.listar()
        
        if resultado:
            return jsonify({
                'status': True,
                'data': data,
                'message': 'Departamentos obtenidos correctamente'
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

@ws_departamento.route('/departamentos/crear', methods=['POST'])
def crear():
    """
    Crear departamento
    ---
    tags:
      - Departamentos
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            nombre:
              type: string
              example: Lima
    responses:
      201:
        description: Departamento creado correctamente
      400:
        description: Faltan datos requeridos
    """
    try:
        data = request.get_json()
        nombre = data.get('nombre')
        
        if not nombre:
            return jsonify({
                'status': False,
                'message': 'El nombre es requerido'
            }), 400
        
        resultado, data_result = departamento_model.crear(nombre)
        
        if resultado:
            return jsonify({
                'status': True,
                'data': {'id_dep': data_result},
                'message': 'Departamento creado correctamente'
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

@ws_departamento.route('/departamentos/modificar', methods=['PUT'])
def modificar():
    """
    Modificar departamento
    ---
    tags:
      - Departamentos
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
              example: Lima Actualizada
    responses:
      200:
        description: Departamento modificado correctamente
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
                'message': 'ID y nombre son requeridos'
            }), 400
        
        resultado, mensaje = departamento_model.modificar(id_dep, nombre)
        
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

@ws_departamento.route('/departamentos/eliminar/<int:id_dep>', methods=['DELETE'])
def eliminar(id_dep):
    """
    Eliminar departamento
    ---
    tags:
      - Departamentos
    parameters:
      - name: id_dep
        in: path
        type: integer
        required: true
        description: ID del departamento
    responses:
      200:
        description: Departamento eliminado correctamente
      400:
        description: Error al eliminar
    """
    try:
        resultado, mensaje = departamento_model.eliminar(id_dep)
        
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