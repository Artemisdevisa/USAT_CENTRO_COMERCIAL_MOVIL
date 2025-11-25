from flask import Blueprint, jsonify, request
from models.tipo_producto import TipoProducto

ws_tipo_producto = Blueprint('ws_tipo_producto', __name__)

# ============================================
# ENDPOINTS EXISTENTES (Frontend público)
# ============================================

@ws_tipo_producto.route('/tipos/listar', methods=['GET'])
def listar_tipos():
    """Lista todos los tipos de producto activos CON 'TODOS' al inicio"""
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
    """Listar TODOS los tipos de producto (activos e inactivos) para el dashboard"""
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
    """Obtener un tipo de producto específico por ID"""
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
    """Crear un nuevo tipo de producto"""
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
    """Modificar un tipo de producto existente"""
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
    """Cambiar estado de un tipo de producto (activar/desactivar)"""
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
    """Eliminar FÍSICAMENTE un tipo de producto (DELETE permanente)"""
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
    """Obtener estadísticas de tipos de producto y modelos"""
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