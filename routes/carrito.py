from flask import Blueprint, jsonify, request
import os
from models.carrito import Carrito

ws_carrito = Blueprint('ws_carrito', __name__)

@ws_carrito.route('/carrito/listar/<int:id_usuario>', methods=['GET'])
def listar_carrito(id_usuario):
    """Listar carrito agrupado por sucursal"""
    try:
        carrito = Carrito()
        exito, resultado = carrito.listar_carrito(id_usuario)
        
        if exito:
            # ✅ DETECTAR ENTORNO Y CLIENTE
            user_agent = request.headers.get('User-Agent', '').lower()
            is_android = 'okhttp' in user_agent or 'android' in user_agent
            
            # ✅ DETERMINAR BASE_URL SEGÚN ENTORNO
            if os.environ.get('RENDER'):
                base_url = "https://usat-comercial-api.onrender.com" if is_android else ""
            else:
                base_url = "http://10.0.2.2:3007" if is_android else ""
            
            # ✅ PROCESAR URLs EN CADA SUCURSAL
            for sucursal in resultado:
                # ✅ PROCESAR LOGO DE SUCURSAL
                logo_url = sucursal.get('logo_sucursal', '')
                if logo_url and is_android:
                    if not logo_url.startswith('http'):
                        if not logo_url.startswith('/'):
                            logo_url = '/' + logo_url
                        sucursal['logo_sucursal'] = base_url + logo_url
                
                # ✅ PROCESAR IMÁGENES DE PRODUCTOS
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
    """Agregar producto al carrito"""
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
    """Actualizar cantidad de producto"""
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
    """Eliminar producto del carrito"""
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
    """Vaciar todo el carrito"""
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