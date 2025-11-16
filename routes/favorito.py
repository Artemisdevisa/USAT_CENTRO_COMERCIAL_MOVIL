from flask import Blueprint, jsonify, request
import os
from models.favorito import Favorito

ws_favorito = Blueprint('ws_favorito', __name__)

@ws_favorito.route('/favoritos/listar/<int:id_usuario>', methods=['GET'])
def listar_favoritos(id_usuario):
    """Endpoint para listar favoritos del usuario"""
    try:
        favorito = Favorito()
        exito, resultado = favorito.listar_favoritos(id_usuario)
        
        if exito:
            # ✅ DETECTAR ENTORNO Y CLIENTE
            user_agent = request.headers.get('User-Agent', '').lower()
            is_android = 'okhttp' in user_agent or 'android' in user_agent
            
            # ✅ DETERMINAR BASE_URL SEGÚN ENTORNO
            if os.environ.get('RENDER'):
                base_url = "https://usat-comercial-api.onrender.com" if is_android else ""
            else:
                base_url = "http://10.0.2.2:3007" if is_android else ""
            
            # ✅ PROCESAR URLs DE IMÁGENES
            for fav in resultado:
                url_img = fav.get('url_img', '')
                if url_img and is_android:
                    if not url_img.startswith('http'):
                        if not url_img.startswith('/'):
                            url_img = '/' + url_img
                        fav['url_img'] = base_url + url_img
            
            return jsonify({
                'status': True,
                'data': resultado,
                'message': 'Favoritos listados correctamente'
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


@ws_favorito.route('/favoritos/agregar', methods=['POST'])
def agregar_favorito():
    """Endpoint para agregar un producto a favoritos"""
    try:
        data = request.get_json()
        id_usuario = data.get('id_usuario')
        id_prod_color = data.get('id_prod_color')
        
        if not id_usuario or not id_prod_color:
            return jsonify({
                'status': False,
                'data': None,
                'message': 'Faltan datos requeridos'
            }), 400
        
        favorito = Favorito()
        exito, mensaje = favorito.agregar_favorito(id_usuario, id_prod_color)
        
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

@ws_favorito.route('/favoritos/eliminar', methods=['POST'])
def eliminar_favorito():
    """Endpoint para eliminar un favorito"""
    try:
        data = request.get_json()
        id_usuario = data.get('id_usuario')
        id_favorito = data.get('id_favorito')
        
        if not id_usuario or not id_favorito:
            return jsonify({
                'status': False,
                'data': None,
                'message': 'Faltan datos requeridos'
            }), 400
        
        favorito = Favorito()
        exito, mensaje = favorito.eliminar_favorito(id_usuario, id_favorito)
        
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

@ws_favorito.route('/favoritos/eliminar-producto', methods=['POST'])
def eliminar_favorito_por_producto():
    """Endpoint para eliminar un favorito por producto"""
    try:
        data = request.get_json()
        id_usuario = data.get('id_usuario')
        id_prod_color = data.get('id_prod_color')
        
        if not id_usuario or not id_prod_color:
            return jsonify({
                'status': False,
                'data': None,
                'message': 'Faltan datos requeridos'
            }), 400
        
        favorito = Favorito()
        exito, mensaje = favorito.eliminar_favorito_por_producto(id_usuario, id_prod_color)
        
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

@ws_favorito.route('/favoritos/verificar', methods=['POST'])
def verificar_favorito():
    """Endpoint para verificar si un producto está en favoritos"""
    try:
        data = request.get_json()
        id_usuario = data.get('id_usuario')
        id_prod_color = data.get('id_prod_color')
        
        if not id_usuario or not id_prod_color:
            return jsonify({
                'status': False,
                'data': None,
                'message': 'Faltan datos requeridos'
            }), 400
        
        favorito = Favorito()
        exito, resultado = favorito.verificar_favorito(id_usuario, id_prod_color)
        
        if exito:
            return jsonify({
                'status': True,
                'data': resultado,
                'message': 'Verificación exitosa'
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