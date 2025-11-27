from flask import Blueprint, request, jsonify
import os
from models.venta import Venta
from models.carrito import Carrito
from conexionBD import Conexion

ws_venta = Blueprint('ws_venta', __name__)

@ws_venta.route('/ventas/crear-multiple', methods=['POST'])
def crear_venta_multiple():
    """
    ---
    tags:
      - Ventas
    summary: Crear múltiples ventas desde carrito
    description: Crea múltiples ventas (una por sucursal) desde el carrito del usuario. Soporta aplicación de cupones a sucursales específicas
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - id_usuario
            - id_tarjeta
            - sucursales
          properties:
            id_usuario:
              type: integer
              description: ID del usuario que realiza la compra
            id_tarjeta:
              type: integer
              description: ID de la tarjeta de pago
            sucursales:
              type: array
              items:
                type: integer
              description: Lista de IDs de sucursales para crear ventas
            id_cupon:
              type: integer
              description: Opcional. ID del cupón a aplicar (se aplica solo en la sucursal del cupón)
    responses:
      201:
        description: Compra realizada correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
            data:
              type: object
              properties:
                ventas:
                  type: array
                  items:
                    type: object
                    properties:
                      id_venta:
                        type: integer
                      codigo_venta:
                        type: string
                      total:
                        type: number
                      descuento:
                        type: number
                errores:
                  type: array
                  description: Errores al crear alguna venta
      400:
        description: Faltan datos requeridos
      500:
        description: Error en el servidor
    """
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
        id_sucursal_cupon = None  # ✅ NUEVA VARIABLE
        
        # ✅ SI HAY CUPÓN, OBTENER SU SUCURSAL
        if id_cupon:
            try:
                con = Conexion().open
                cursor = con.cursor()
                cursor.execute("SELECT id_sucursal FROM cupon WHERE id_cupon = %s", [id_cupon])
                cupon_info = cursor.fetchone()
                if cupon_info:
                    id_sucursal_cupon = cupon_info['id_sucursal']
                cursor.close()
                con.close()
                print(f"   ✅ Sucursal del cupón: {id_sucursal_cupon}")
            except Exception as e:
                print(f"   ⚠️ Error al obtener sucursal del cupón: {str(e)}")
        
        for id_sucursal in sucursales:
            print(f"\n🏪 Procesando sucursal ID: {id_sucursal}")
            
            # ✅ SOLO APLICAR CUPÓN EN LA SUCURSAL CORRECTA
            cupon_para_esta_venta = id_cupon if (id_sucursal == id_sucursal_cupon) else None
            
            if cupon_para_esta_venta:
                print(f"   🎫 Aplicando cupón {id_cupon} en esta sucursal")
            else:
                print(f"   ℹ️ Sin cupón para esta sucursal")
            
            exito, resultado = venta_model.crear_venta_completa(
                id_usuario, id_sucursal, id_tarjeta, cupon_para_esta_venta  # ✅ AQUÍ PASAMOS EL CUPÓN
            )
            
            if exito:
                print(f"✅ Venta creada exitosamente:")
                print(f"   - ID Venta: {resultado.get('id_venta')}")
                print(f"   - Código: {resultado.get('codigo_venta')}")
                print(f"   - Total: {resultado.get('total', 0)}")
                print(f"   - Descuento: {resultado.get('descuento', 0)}")
                
                ventas_creadas.append(resultado)
            else:
                print(f"❌ Error: {resultado}")
                errores.append({
                    'id_sucursal': id_sucursal,
                    'error': resultado
                })
        
        # ✅ REGISTRAR USO DEL CUPÓN
        if ventas_creadas and id_cupon:
            try:
                print(f"\n{'='*60}")
                print(f"🎫 REGISTRANDO USO DE CUPÓN")
                print(f"{'='*60}")
                
                # Buscar la venta que tiene el cupón aplicado (la que tiene descuento > 0)
                venta_con_cupon = None
                for venta in ventas_creadas:
                    if venta.get('descuento', 0) > 0:
                        venta_con_cupon = venta
                        break
                
                if venta_con_cupon:
                    con = Conexion().open
                    cursor = con.cursor()
                    
                    # Verificar si ya usó el cupón
                    cursor.execute("""
                        SELECT COUNT(*) as usado
                        FROM cupon_usuario
                        WHERE id_cupon = %s AND id_usuario = %s
                    """, [id_cupon, id_usuario])
                    
                    resultado_check = cursor.fetchone()
                    
                    if resultado_check['usado'] > 0:
                        print("⚠️ Usuario ya usó este cupón previamente (no debería llegar aquí)")
                    else:
                        # Insertar registro
                        cursor.execute("""
                            INSERT INTO cupon_usuario (id_cupon, id_usuario, id_venta, fecha_uso)
                            VALUES (%s, %s, %s, NOW())
                        """, [id_cupon, id_usuario, venta_con_cupon['id_venta']])
                        
                        # Incrementar contador
                        cursor.execute("""
                            UPDATE cupon
                            SET cantidad_usada = cantidad_usada + 1
                            WHERE id_cupon = %s
                        """, [id_cupon])
                        
                        con.commit()
                        print(f"✅ Cupón registrado en venta {venta_con_cupon['id_venta']}")
                    
                    cursor.close()
                    con.close()
                else:
                    print("⚠️ No se encontró venta con descuento aplicado")
                
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
    """
    ---
    tags:
      - Ventas
    summary: Listar productos comprados del usuario
    description: Obtiene una lista de todos los productos que el usuario ha comprado, con URLs de imágenes procesadas según el entorno
    parameters:
      - name: id_usuario
        in: path
        type: integer
        required: true
        description: ID del usuario
    responses:
      200:
        description: Productos listados correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
            data:
              type: array
              items:
                type: object
                properties:
                  id_venta:
                    type: integer
                  nombre_producto:
                    type: string
                  url_img_producto:
                    type: string
                    description: URL de la imagen del producto (procesada según entorno)
                  total:
                    type: number
                  fecha_venta:
                    type: string
                    format: date-time
      500:
        description: Error en el servidor
    """
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
    """
    ---
    tags:
      - Ventas
    summary: Obtener detalle de una venta
    description: Obtiene los detalles completos de una venta específica (items, precios, etc)
    parameters:
      - name: id_venta
        in: path
        type: integer
        required: true
        description: ID de la venta
    responses:
      200:
        description: Detalle obtenido correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
            data:
              type: array
              items:
                type: object
                properties:
                  id_detalle_venta:
                    type: integer
                  id_prod_color:
                    type: integer
                  talla:
                    type: string
                  cantidad:
                    type: integer
                  precio:
                    type: number
                  url_img:
                    type: string
      500:
        description: Error en el servidor
    """
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
    """
    ---
    tags:
      - Ventas
    summary: Obtener información completa de una venta
    description: Obtiene toda la información de una venta incluyendo datos del usuario, dirección y detalles
    parameters:
      - name: id_venta
        in: path
        type: integer
        required: true
        description: ID de la venta
    responses:
      200:
        description: Venta obtenida correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
            data:
              type: object
              properties:
                id_venta:
                  type: integer
                codigo_qr:
                  type: string
                usuario:
                  type: object
                subtotal:
                  type: number
                descuento:
                  type: number
                impuesto:
                  type: number
                total:
                  type: number
                detalles:
                  type: array
      404:
        description: Venta no encontrada
      500:
        description: Error en el servidor
    """
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
    

@ws_venta.route('/ventas/reporte-por-sucursal/<int:id_sucursal>', methods=['GET'])
def obtener_reporte_por_sucursal(id_sucursal):
    """
    ---
    tags:
      - Reportes
    summary: Obtener reporte de ventas por sucursal
    description: Genera un reporte completo de ventas para una sucursal específica incluyendo totales, descuentos e impuestos
    parameters:
      - name: id_sucursal
        in: path
        type: integer
        required: true
        description: ID de la sucursal
    responses:
      200:
        description: Reporte generado correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
            data:
              type: array
              items:
                type: object
                properties:
                  id_venta:
                    type: integer
                  codigo_venta:
                    type: string
                  fecha_venta:
                    type: string
                    format: date-time
                  subtotal:
                    type: number
                  descuento:
                    type: number
                  impuesto:
                    type: number
                  total:
                    type: number
                  nombre_usuario:
                    type: string
                  cantidad_productos:
                    type: integer
                  estado:
                    type: boolean
      500:
        description: Error en el servidor
    """
    try:
        print(f"\n{'='*60}")
        print(f"📊 GENERANDO REPORTE DE VENTAS")
        print(f"{'='*60}")
        print(f"ID Sucursal: {id_sucursal}")
        
        con = Conexion().open
        cursor = con.cursor()
        
        # ✅ CORREGIDO: Calcular subtotal, impuesto y descuento si son NULL
        cursor.execute("""
            SELECT 
                v.id_venta,
                v.codigo_qr as codigo_venta,
                v.created_at as fecha_venta,
                -- ✅ Si subtotal es NULL, calcular desde detalles
                COALESCE(
                    v.subtotal,
                    (SELECT COALESCE(SUM(dv.sub_total), 0) 
                     FROM detalle_venta dv 
                     WHERE dv.id_venta = v.id_venta AND dv.estado = TRUE)
                ) as subtotal,
                -- ✅ Descuento (si es NULL, es 0)
                COALESCE(v.descuento, 0) as descuento,
                -- ✅ Si impuesto es NULL, calcular como (subtotal - descuento) * 0.18
                COALESCE(
                    v.impuesto,
                    (COALESCE(v.subtotal, (SELECT COALESCE(SUM(dv.sub_total), 0) 
                                            FROM detalle_venta dv 
                                            WHERE dv.id_venta = v.id_venta AND dv.estado = TRUE)) 
                     - COALESCE(v.descuento, 0)) * 0.18
                ) as impuesto,
                v.total,
                v.estado,
                u.nomusuario as nombre_usuario,
                (SELECT COUNT(*) FROM detalle_venta dv WHERE dv.id_venta = v.id_venta AND dv.estado = TRUE) as cantidad_productos
            FROM venta v
            INNER JOIN usuario u ON v.id_usuario = u.id_usuario
            WHERE v.id_sucursal = %s
            ORDER BY v.created_at DESC
        """, [id_sucursal])
        
        resultados = cursor.fetchall()
        
        cursor.close()
        con.close()
        
        print(f"✅ Ventas encontradas: {len(resultados)}")
        
        if resultados:
            ventas = []
            for row in resultados:
                subtotal = float(row['subtotal']) if row['subtotal'] else 0.0
                descuento = float(row['descuento']) if row['descuento'] else 0.0
                impuesto = float(row['impuesto']) if row['impuesto'] else 0.0
                total = float(row['total']) if row['total'] else 0.0
                
                # ✅ DEBUG: Imprimir valores calculados
                print(f"\n📦 Venta {row['codigo_venta']}:")
                print(f"   Subtotal: {subtotal}")
                print(f"   Descuento: {descuento}")
                print(f"   Impuesto: {impuesto}")
                print(f"   Total: {total}")
                
                venta = {
                    'id_venta': row['id_venta'],
                    'codigo_venta': row['codigo_venta'],
                    'fecha_venta': str(row['fecha_venta']) if row['fecha_venta'] else '',
                    'subtotal': subtotal,
                    'descuento': descuento,
                    'impuesto': impuesto,
                    'total': total,
                    'estado': row['estado'],
                    'nombre_usuario': row['nombre_usuario'],
                    'cantidad_productos': row['cantidad_productos']
                }
                ventas.append(venta)
            
            print(f"{'='*60}\n")
            
            return jsonify({
                'status': True,
                'data': ventas,
                'message': 'Reporte generado correctamente'
            }), 200
        else:
            return jsonify({
                'status': True,
                'data': [],
                'message': 'No hay ventas para esta sucursal'
            }), 200
            
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': False,
            'data': [],
            'message': f'Error: {str(e)}'
        }), 500