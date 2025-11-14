from flask import Blueprint, request, jsonify
from models.provincia import Provincia

ws_provincia = Blueprint('ws_provincia', __name__)
provincia_model = Provincia()

@ws_provincia.route('/provincias/listar/<int:id_dep>', methods=['GET'])
def listar_por_departamento(id_dep):
    """Listar provincias por departamento"""
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
    """Crear provincia"""
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
    """Modificar provincia"""
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
    """Eliminar provincia"""
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