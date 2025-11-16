from flask import Blueprint, request, jsonify
import os
from models.venta import Venta
from models.carrito import Carrito

ws_venta = Blueprint('ws_venta', __name__)

@ws_venta.route('/ventas/crear-multiple', methods=['POST'])
def crear_venta_multiple():
    """Crear múltiples ventas (una por sucursal) desde el carrito"""
    try:
        data = request.get_json()
        id_usuario = data.get('id_usuario')
        id_tarjeta = data.get('id_tarjeta')
        sucursales = data.get('sucursales')  # Lista de IDs de sucursales
        
        if not all([id_usuario, id_tarjeta, sucursales]):
            return jsonify({
                'status': False,
                'message': 'Faltan datos requeridos'
            }), 400
        
        venta_model = Venta()
        ventas_creadas = []
        errores = []
        
        # Crear una venta por cada sucursal
        for id_sucursal in sucursales:
            exito, resultado = venta_model.crear_venta_completa(
                id_usuario, id_sucursal, id_tarjeta
            )
            
            if exito:
                ventas_creadas.append(resultado)
            else:
                errores.append({
                    'id_sucursal': id_sucursal,
                    'error': resultado
                })
        
        if ventas_creadas:
            return jsonify({
                'status': True,
                'data': {
                    'ventas': ventas_creadas,
                    'errores': errores if errores else None
                },
                'message': 'Compra realizada correctamente'
            }), 201
        else:
            return jsonify({
                'status': False,
                'data': {'errores': errores},
                'message': 'Error al crear las ventas'
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500

@ws_venta.route('/ventas/listar/<int:id_usuario>', methods=['GET'])
def listar_ventas(id_usuario):
    """Listar ventas del usuario"""
    try:
        venta = Venta()
        exito, resultado = venta.listar_por_usuario(id_usuario)
        
        if exito:
            return jsonify({
                'status': True,
                'data': resultado,
                'message': 'Ventas listadas correctamente'
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

@ws_venta.route('/ventas/detalle/<int:id_venta>', methods=['GET'])
def obtener_detalle_venta(id_venta):
    """Obtener detalle de una venta"""
    try:
        # ✅ DETECTAR ENTORNO Y CLIENTE
        user_agent = request.headers.get('User-Agent', '').lower()
        is_android = 'okhttp' in user_agent or 'android' in user_agent
        
        # ✅ DETERMINAR BASE_URL SEGÚN ENTORNO
        if os.environ.get('RENDER'):
            base_url = "https://usat-comercial-api.onrender.com" if is_android else ""
        else:
            base_url = "http://10.0.2.2:3007" if is_android else ""
        
        venta = Venta()
        exito, resultado = venta.obtener_detalle(id_venta)
        
        if exito:
            # ✅ PROCESAR URLs DE IMÁGENES
            for detalle in resultado:
                url_img = detalle.get('url_img', '')
                if url_img and is_android:
                    if not url_img.startswith('http'):
                        if not url_img.startswith('/'):
                            url_img = '/' + url_img
                        detalle['url_img'] = base_url + url_img
            
            return jsonify({
                'status': True,
                'data': resultado,
                'message': 'Detalle obtenido correctamente'
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

@ws_venta.route('/ventas/completa/<int:id_venta>', methods=['GET'])
def obtener_venta_completa(id_venta):
    """Obtener información completa de una venta"""
    try:
        venta = Venta()
        exito, resultado = venta.obtener_venta_completa(id_venta)
        
        if exito:
            return jsonify({
                'status': True,
                'data': resultado,
                'message': 'Venta obtenida correctamente'
            }), 200
        else:
            return jsonify({
                'status': False,
                'data': None,
                'message': resultado
            }), 404
    except Exception as e:
        return jsonify({
            'status': False,
            'data': None,
            'message': f'Error: {str(e)}'
        }), 500

@ws_venta.route('/ventas/cancelar/<int:id_venta>', methods=['POST'])
def cancelar_venta(id_venta):
    """Cancelar venta y devolver stock"""
    try:
        venta = Venta()
        exito, mensaje = venta.cancelar_venta(id_venta)
        
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
            'message': f'Error: {str(e)}'
        }), 500