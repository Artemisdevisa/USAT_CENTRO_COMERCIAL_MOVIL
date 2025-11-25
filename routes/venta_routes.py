from flask import Blueprint, request, jsonify
import os
from models.venta import Venta
from models.carrito import Carrito
from conexionBD import Conexion

ws_venta = Blueprint('ws_venta', __name__)

@ws_venta.route('/ventas/crear-multiple', methods=['POST'])
def crear_venta_multiple():
    """Crear múltiples ventas (una por sucursal) desde el carrito"""
    try:
        data = request.get_json()
        id_usuario = data.get('id_usuario')
        id_tarjeta = data.get('id_tarjeta')
        sucursales = data.get('sucursales')
        id_cupon = data.get('id_cupon')
        
        print(f"\n{'='*60}")
        print(f"📥 PETICIÓN RECIBIDA - CREAR VENTA MÚLTIPLE")
        print(f"{'='*60}")
        print(f"ID Usuario: {id_usuario}")
        print(f"ID Tarjeta: {id_tarjeta}")
        print(f"Sucursales: {sucursales}")
        print(f"ID Cupón: {id_cupon if id_cupon else 'Sin cupón'}")
        
        if not all([id_usuario, id_tarjeta, sucursales]):
            return jsonify({
                'status': False,
                'message': 'Faltan datos requeridos'
            }), 400
        
        venta_model = Venta()
        ventas_creadas = []
        errores = []
        
        for id_sucursal in sucursales:
            print(f"\n🏪 Procesando sucursal ID: {id_sucursal}")
            
            exito, resultado = venta_model.crear_venta_completa(
                id_usuario, id_sucursal, id_tarjeta
            )
            
            if exito:
                print(f"✅ Venta creada exitosamente:")
                print(f"   - ID Venta: {resultado.get('id_venta')}")
                print(f"   - Código: {resultado.get('codigo_venta')}")
                print(f"   - Total: {resultado.get('total', 0)}")
                
                ventas_creadas.append(resultado)
            else:
                print(f"❌ Error: {resultado}")
                errores.append({
                    'id_sucursal': id_sucursal,
                    'error': resultado
                })
        
        if ventas_creadas and id_cupon:
            try:
                print(f"\n{'='*60}")
                print(f"🎫 REGISTRANDO USO DE CUPÓN")
                print(f"{'='*60}")
                print(f"ID Cupón: {id_cupon}")
                print(f"ID Usuario: {id_usuario}")
                
                primera_venta = ventas_creadas[0]['id_venta']
                print(f"ID Venta (primera): {primera_venta}")
                
                con = Conexion().open
                cursor = con.cursor()
                
                cursor.execute("""
                    SELECT COUNT(*) as usado
                    FROM cupon_usuario
                    WHERE id_cupon = %s AND id_usuario = %s
                """, [id_cupon, id_usuario])
                
                resultado_check = cursor.fetchone()
                
                if resultado_check['usado'] > 0:
                    print("⚠️ Usuario ya usó este cupón previamente")
                    cursor.close()
                    con.close()
                else:
                    cursor.execute("""
                        SELECT cantidad_total, cantidad_usada
                        FROM cupon
                        WHERE id_cupon = %s AND estado = TRUE
                    """, [id_cupon])
                    
                    cupon = cursor.fetchone()
                    
                    if cupon and cupon['cantidad_usada'] < cupon['cantidad_total']:
                        cursor.execute("""
                            INSERT INTO cupon_usuario (id_cupon, id_usuario, id_venta, fecha_uso)
                            VALUES (%s, %s, %s, NOW())
                        """, [id_cupon, id_usuario, primera_venta])
                        
                        cursor.execute("""
                            UPDATE cupon
                            SET cantidad_usada = cantidad_usada + 1
                            WHERE id_cupon = %s
                        """, [id_cupon])
                        
                        con.commit()
                        print(f"✅ Cupón registrado exitosamente")
                        print(f"   - Cantidad usada incrementada")
                    else:
                        print("⚠️ Cupón no disponible o agotado")
                    
                    cursor.close()
                    con.close()
                
                print(f"{'='*60}\n")
                
            except Exception as e:
                print(f"⚠️ Error al registrar cupón: {str(e)}")
                import traceback
                traceback.print_exc()
        
        print(f"\n{'='*60}")
        print(f"📊 RESUMEN:")
        print(f"   Ventas creadas: {len(ventas_creadas)}")
        print(f"   Errores: {len(errores)}")
        print(f"{'='*60}\n")
        
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
        print(f"\n💥 ERROR CRÍTICO: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500

@ws_venta.route('/ventas/listar/<int:id_usuario>', methods=['GET'])
def listar_ventas(id_usuario):
    """Listar productos comprados del usuario"""
    try:
        print(f"\n{'='*60}")
        print(f"📥 PETICIÓN: Listar ventas usuario {id_usuario}")
        print(f"{'='*60}")
        
        user_agent = request.headers.get('User-Agent', '').lower()
        is_android = 'okhttp' in user_agent or 'android' in user_agent
        
        print(f"User-Agent: {user_agent}")
        print(f"Es Android: {is_android}")
        
        if os.environ.get('RENDER'):
            base_url = "https://usat-comercial-api.onrender.com"
            print(f"🌍 Entorno: RENDER (Producción)")
        else:
            base_url = "http://10.0.2.2:3007" if is_android else "http://localhost:3007"
            print(f"💻 Entorno: LOCAL (Desarrollo)")
        
        print(f"Base URL: {base_url}")
        
        venta = Venta()
        exito, resultado = venta.listar_por_usuario(id_usuario)
        
        if exito:
            print(f"\n✅ Productos obtenidos: {len(resultado)}")
            
            for i, producto in enumerate(resultado):
                url_img = producto.get('url_img_producto', '')
                print(f"\n📦 Producto {i+1}:")
                print(f"   - Nombre: {producto.get('nombre_producto')}")
                print(f"   - URL Original: {url_img}")
                
                if url_img:
                    if not url_img.startswith('http'):
                        if not url_img.startswith('/'):
                            url_img = '/' + url_img
                        producto['url_img_producto'] = base_url + url_img
                        print(f"   - URL Procesada: {producto['url_img_producto']}")
                else:
                    print(f"   - ⚠️ Sin imagen")
            
            print(f"\n{'='*60}")
            print(f"📤 RESPUESTA ENVIADA")
            print(f"{'='*60}\n")
            
            return jsonify({
                'status': True,
                'data': resultado,
                'message': 'Productos listados correctamente'
            }), 200
        else:
            print(f"\n❌ Error al listar productos: {resultado}")
            return jsonify({
                'status': False,
                'data': [],
                'message': resultado
            }), 500
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': False,
            'data': [],
            'message': f'Error: {str(e)}'
        }), 500

@ws_venta.route('/ventas/detalle/<int:id_venta>', methods=['GET'])
def obtener_detalle_venta(id_venta):
    """Obtener detalle de una venta"""
    try:
        user_agent = request.headers.get('User-Agent', '').lower()
        is_android = 'okhttp' in user_agent or 'android' in user_agent
        
        if os.environ.get('RENDER'):
            base_url = "https://usat-comercial-api.onrender.com" if is_android else ""
        else:
            base_url = "http://10.0.2.2:3007" if is_android else ""
        
        venta = Venta()
        exito, resultado = venta.obtener_detalle(id_venta)
        
        if exito:
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