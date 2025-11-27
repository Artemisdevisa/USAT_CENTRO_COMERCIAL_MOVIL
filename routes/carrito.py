from flask import Blueprint, jsonify, request
import os
from models.carrito import Carrito

ws_carrito = Blueprint('ws_carrito', __name__)

@ws_carrito.route('/carrito/listar/<int:id_usuario>', methods=['GET'])
def listar_carrito(id_usuario):
    """
    Listar carrito del usuario
    ---
    tags:
      - Carrito
    parameters:
      - name: id_usuario
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Carrito listado correctamente
      500:
        description: Error del servidor
    """
    try:
        carrito = Carrito()
        exito, resultado = carrito.listar_carrito(id_usuario)
        
        if exito:
            user_agent = request.headers.get('User-Agent', '').lower()
            is_android = 'okhttp' in user_agent or 'android' in user_agent
            
            if os.environ.get('RENDER'):
                base_url = "https://usat-comercial-api.onrender.com" if is_android else ""
            else:
                base_url = "http://10.0.2.2:3007" if is_android else ""
            
            for sucursal in resultado:
                logo_url = sucursal.get('logo_sucursal', '')
                if logo_url and is_android:
                    if not logo_url.startswith('http'):
                        if not logo_url.startswith('/'):
                            logo_url = '/' + logo_url
                        sucursal['logo_sucursal'] = base_url + logo_url
                
                for producto in sucursal['productos']:
                    url_img = producto.get('url_img', '')
                    if url_img and is_android:
                        if not url_img.startswith('http'):
                            if not url_img.startswith('/'):
                                url_img = '/' + url_img
                            producto['url_img'] = base_url + url_img
            
            return jsonify({
                'status': True,
                'data': resultado,
                'message': 'Carrito listado correctamente'
            }), 200
        else:
            return jsonify({
                'status': False,
                'data': None,
                'message': resultado
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'data': None,
            'message': f'Error en el servidor: {str(e)}'
        }), 500

@ws_carrito.route('/carrito/agregar', methods=['POST'])
def agregar_al_carrito():
    """
    Agregar producto al carrito
    ---
    tags:
      - Carrito
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            id_usuario:
              type: integer
              example: 5
            id_prod_color:
              type: integer
              example: 10
            cantidad:
              type: integer
              example: 2
    responses:
      200:
        description: Producto agregado correctamente
      400:
        description: Faltan datos requeridos
    """
    try:
        data = request.get_json()
        id_usuario = data.get('id_usuario')
        id_prod_color = data.get('id_prod_color')
        cantidad = data.get('cantidad', 1)
        
        if not id_usuario or not id_prod_color:
            return jsonify({
                'status': False,
                'data': None,
                'message': 'Faltan datos requeridos'
            }), 400
        
        carrito = Carrito()
        exito, mensaje = carrito.agregar_al_carrito(id_usuario, id_prod_color, cantidad)
        
        if exito:
            return jsonify({
                'status': True,
                'data': None,
                'message': mensaje
            }), 200
        else:
            return jsonify({
                'status': False,
                'data': None,
                'message': mensaje
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': False,
            'data': None,
            'message': f'Error en el servidor: {str(e)}'
        }), 500

@ws_carrito.route('/carrito/actualizar', methods=['POST'])
def actualizar_cantidad():
    """
    Actualizar cantidad de producto
    ---
    tags:
      - Carrito
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            id_usuario:
              type: integer
            id_carrito:
              type: integer
            cantidad:
              type: integer
    responses:
      200:
        description: Cantidad actualizada correctamente
      400:
        description: Faltan datos requeridos
    """
    try:
        data = request.get_json()
        id_usuario = data.get('id_usuario')
        id_carrito = data.get('id_carrito')
        cantidad = data.get('cantidad')
        
        if not id_usuario or not id_carrito or cantidad is None:
            return jsonify({
                'status': False,
                'data': None,
                'message': 'Faltan datos requeridos'
            }), 400
        
        carrito = Carrito()
        exito, mensaje = carrito.actualizar_cantidad(id_usuario, id_carrito, cantidad)
        
        if exito:
            return jsonify({
                'status': True,
                'data': None,
                'message': mensaje
            }), 200
        else:
            return jsonify({
                'status': False,
                'data': None,
                'message': mensaje
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': False,
            'data': None,
            'message': f'Error en el servidor: {str(e)}'
        }), 500

@ws_carrito.route('/carrito/eliminar', methods=['POST'])
def eliminar_del_carrito():
    """
    Eliminar producto del carrito
    ---
    tags:
      - Carrito
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            id_usuario:
              type: integer
            id_carrito:
              type: integer
    responses:
      200:
        description: Producto eliminado correctamente
      404:
        description: Producto no encontrado
    """
    try:
        data = request.get_json()
        id_usuario = data.get('id_usuario')
        id_carrito = data.get('id_carrito')
        
        if not id_usuario or not id_carrito:
            return jsonify({
                'status': False,
                'data': None,
                'message': 'Faltan datos requeridos'
            }), 400
        
        carrito = Carrito()
        exito, mensaje = carrito.eliminar_del_carrito(id_usuario, id_carrito)
        
        if exito:
            return jsonify({
                'status': True,
                'data': None,
                'message': mensaje
            }), 200
        else:
            return jsonify({
                'status': False,
                'data': None,
                'message': mensaje
            }), 404
            
    except Exception as e:
        return jsonify({
            'status': False,
            'data': None,
            'message': f'Error en el servidor: {str(e)}'
        }), 500

@ws_carrito.route('/carrito/vaciar/<int:id_usuario>', methods=['POST'])
def vaciar_carrito(id_usuario):
    """
    Vaciar todo el carrito
    ---
    tags:
      - Carrito
    parameters:
      - name: id_usuario
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Carrito vaciado correctamente
      500:
        description: Error del servidor
    """
    try:
        carrito = Carrito()
        exito, mensaje = carrito.vaciar_carrito(id_usuario)
        
        if exito:
            return jsonify({
                'status': True,
                'data': None,
                'message': mensaje
            }), 200
        else:
            return jsonify({
                'status': False,
                'data': None,
                'message': mensaje
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'data': None,
            'message': f'Error en el servidor: {str(e)}'
        }), 500