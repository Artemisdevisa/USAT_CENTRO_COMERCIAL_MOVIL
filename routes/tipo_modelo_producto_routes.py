from flask import Blueprint, jsonify, request
from models.tipo_modelo_producto import TipoModeloProducto

ws_tipo_modelo = Blueprint('ws_tipo_modelo', __name__)

# ============================================
# ENDPOINTS CRUD
# ============================================

@ws_tipo_modelo.route('/modelos/listar', methods=['GET'])
def listar_modelos():
    """Listar TODOS los modelos de producto"""
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
    """Obtener un modelo específico por ID"""
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
    """Listar modelos de un tipo de producto específico (solo activos)"""
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
    """Crear un nuevo modelo de producto"""
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
    """Modificar un modelo de producto existente"""
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
    """Cambiar estado de un modelo de producto (activar/desactivar)"""
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
    """Eliminar FÍSICAMENTE un modelo de producto (DELETE permanente)"""
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
    """Obtener estadísticas de modelos y productos"""
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
    """Listar tipos de producto activos para el select"""
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