from flask import Blueprint, request, jsonify
from conexionBD import Conexion
import json  # ✅ AGREGAR ESTE IMPORT

ws_entrega = Blueprint('ws_entrega', __name__)

@ws_entrega.route('/entregas/sucursales/<int:id_empresa>', methods=['GET'])
def listar_sucursales_empresa(id_empresa):
    """
    Listar sucursales de una empresa con estadísticas de ventas
    ---
    tags:
      - Entregas
    parameters:
      - name: id_empresa
        in: path
        required: true
        type: integer
        description: ID de la empresa
    responses:
      200:
        description: Sucursales listadas correctamente
      500:
        description: Error interno del servidor
    """
    try:
        print(f"\n{'='*60}")
        print(f"📊 LISTAR SUCURSALES DE EMPRESA {id_empresa}")
        print(f"{'='*60}")
        
        con = Conexion().open
        cursor = con.cursor()
        
        cursor.execute("SELECT * FROM fn_listar_sucursales_empresa(%s)", [id_empresa])
        sucursales = cursor.fetchall()
        
        cursor.close()
        con.close()
        
        print(f"✅ Sucursales encontradas: {len(sucursales)}")
        
        return jsonify({
            'status': True,
            'data': sucursales,
            'message': 'Sucursales listadas correctamente'
        }), 200
        
    except Exception as e:
        print(f"💥 ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': False,
            'data': [],
            'message': f'Error: {str(e)}'
        }), 500


@ws_entrega.route('/entregas/ventas/<int:id_sucursal>', methods=['GET'])
def listar_ventas_sucursal(id_sucursal):
    """
    Listar ventas de una sucursal con filtro de entrega
    ---
    tags:
      - Entregas
    parameters:
      - name: id_sucursal
        in: path
        required: true
        type: integer
        description: ID de la sucursal
      - name: entregado
        in: query
        required: false
        type: string
        enum: [true, false]
        description: Filtrar por ventas entregadas (true) o no entregadas (false)
    responses:
      200:
        description: Ventas listadas correctamente
      500:
        description: Error interno del servidor
    """
    try:
        # Obtener parámetro opcional de filtro
        entregado_param = request.args.get('entregado')
        
        entregado = None
        if entregado_param == 'true':
            entregado = True
        elif entregado_param == 'false':
            entregado = False
        
        print(f"\n{'='*60}")
        print(f"📦 LISTAR VENTAS DE SUCURSAL {id_sucursal}")
        print(f"   Filtro entregado: {entregado}")
        print(f"{'='*60}")
        
        con = Conexion().open
        cursor = con.cursor()
        
        cursor.execute("""
            SELECT * FROM fn_listar_ventas_por_sucursal(%s, %s)
        """, [id_sucursal, entregado])
        
        ventas = cursor.fetchall()
        
        cursor.close()
        con.close()
        
        print(f"✅ Ventas encontradas: {len(ventas)}")
        
        ventas_formateadas = []
        for venta in ventas:
            ventas_formateadas.append({
                'id_venta': venta['id_venta'],
                'codigo_qr': venta['codigo_qr'],
                'fecha_venta': str(venta['fecha_venta']) if venta['fecha_venta'] else '',
                'subtotal': float(venta['subtotal']) if venta['subtotal'] else 0.0,
                'descuento': float(venta['descuento']) if venta['descuento'] else 0.0,
                'impuesto': float(venta['impuesto']) if venta['impuesto'] else 0.0,
                'total': float(venta['total']) if venta['total'] else 0.0,
                'entregado': venta['entregado'],
                'nombre_usuario': venta['nombre_usuario'],
                'email_usuario': venta['email_usuario'],
                'cantidad_productos': venta['cantidad_productos']
            })
        
        return jsonify({
            'status': True,
            'data': ventas_formateadas,
            'message': 'Ventas listadas correctamente'
        }), 200
        
    except Exception as e:
        print(f"💥 ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': False,
            'data': [],
            'message': f'Error: {str(e)}'
        }), 500


@ws_entrega.route('/entregas/marcar-entregada', methods=['POST'])
def marcar_venta_entregada():
    """
    Marcar venta como entregada mediante código QR
    ---
    tags:
      - Entregas
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        description: Datos para marcar la venta como entregada
        schema:
          type: object
          properties:
            codigo_venta:
              type: string
              description: Código QR de la venta
          required:
            - codigo_venta
    responses:
      200:
        description: Venta marcada como entregada correctamente
      400:
        description: Error de validación o código inválido
      500:
        description: Error interno del servidor
    """
    try:
        data = request.get_json()
        codigo_venta = data.get('codigo_venta')
        
        if not codigo_venta:
            return jsonify({
                'status': False,
                'message': 'Código de venta requerido',
                'data': None
            }), 400
        
        print(f"\n{'='*60}")
        print(f"📦 MARCAR VENTA COMO ENTREGADA")
        print(f"   Código QR: {codigo_venta}")
        print(f"{'='*60}")
        
        con = Conexion().open
        cursor = con.cursor()
        
        # ✅ EJECUTAR FUNCIÓN DE POSTGRESQL
        cursor.execute("SELECT fn_marcar_venta_entregada(%s)", [codigo_venta])
        
        # ✅ FIX: Acceder al resultado correctamente
        resultado_raw = cursor.fetchone()
        
        # El resultado viene en el primer campo del diccionario
        # Puede ser 'fn_marcar_venta_entregada' o index 0 dependiendo del cursor
        if isinstance(resultado_raw, dict):
            # Si es diccionario, buscar la clave correcta
            resultado_json = resultado_raw.get('fn_marcar_venta_entregada') or list(resultado_raw.values())[0]
        else:
            # Si es tupla
            resultado_json = resultado_raw[0]
        
        print(f"\n📊 RESULTADO RAW:")
        print(f"   Tipo resultado_raw: {type(resultado_raw)}")
        print(f"   Contenido: {resultado_raw}")
        print(f"   Tipo resultado_json: {type(resultado_json)}")
        
        # ✅ CONVERTIR JSONB A DICCIONARIO PYTHON
        if isinstance(resultado_json, str):
            resultado = json.loads(resultado_json)
        else:
            resultado = resultado_json
        
        print(f"\n📊 RESULTADO PROCESADO:")
        print(f"   Success: {resultado.get('success')}")
        print(f"   Message: {resultado.get('message')}")
        print(f"   ID Venta: {resultado.get('id_venta')}")
        
        # Solo hacer commit si fue exitoso
        if resultado.get('success'):
            con.commit()
            print(f"✅ Commit realizado - Venta marcada como entregada")
        else:
            print(f"⚠️ No se hizo commit - Operación no exitosa")
        
        cursor.close()
        con.close()
        
        print(f"{'='*60}\n")
        
        # ✅ RETORNAR RESPUESTA
        if resultado.get('success'):
            return jsonify({
                'status': True,
                'data': {
                    'success': resultado.get('success'),
                    'message': resultado.get('message'),
                    'id_venta': resultado.get('id_venta'),
                    'sucursal': resultado.get('sucursal', ''),
                    'total': resultado.get('total', 0),
                    'codigo': resultado.get('codigo', codigo_venta)
                },
                'message': resultado.get('message', 'Venta entregada correctamente')
            }), 200
        else:
            return jsonify({
                'status': False,
                'data': {
                    'success': False,
                    'message': resultado.get('message'),
                    'id_venta': resultado.get('id_venta')
                },
                'message': resultado.get('message', 'Error al marcar venta')
            }), 400
        
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"💥 ERROR CRÍTICO:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensaje: {str(e)}")
        print(f"{'='*60}")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}\n")
        
        return jsonify({
            'status': False,
            'data': None,
            'message': f'Error interno: {str(e)}'
        }), 500


@ws_entrega.route('/entregas/verificar-codigo', methods=['POST'])
def verificar_codigo_venta():
    """
    Verificar si un código QR de venta es válido
    ---
    tags:
      - Entregas
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        description: Datos para verificar el código de venta
        schema:
          type: object
          properties:
            codigo_venta:
              type: string
              description: Código QR de la venta
          required:
            - codigo_venta
    responses:
      200:
        description: Código válido y venta encontrada
      400:
        description: Código de venta requerido
      404:
        description: Código de venta no encontrado
      500:
        description: Error interno del servidor
    """
    try:
        data = request.get_json()
        codigo_venta = data.get('codigo_venta')
        
        if not codigo_venta:
            return jsonify({
                'status': False,
                'message': 'Código de venta requerido'
            }), 400
        
        print(f"\n{'='*60}")
        print(f"🔍 VERIFICAR CÓDIGO DE VENTA")
        print(f"   Código QR: {codigo_venta}")
        print(f"{'='*60}")
        
        con = Conexion().open
        cursor = con.cursor()
        
        cursor.execute("""
            SELECT 
                v.id_venta,
                v.codigo_qr,
                v.total,
                v.entregado,
                s.nombre as nombre_sucursal
            FROM venta v
            INNER JOIN sucursal s ON v.id_sucursal = s.id_sucursal
            WHERE v.codigo_qr = %s AND v.estado = TRUE
        """, [codigo_venta])
        
        venta = cursor.fetchone()
        
        cursor.close()
        con.close()
        
        if venta:
            print(f"✅ Venta encontrada:")
            print(f"   ID: {venta['id_venta']}")
            print(f"   Sucursal: {venta['nombre_sucursal']}")
            print(f"   Total: {venta['total']}")
            print(f"   Entregado: {venta['entregado']}")
            print(f"{'='*60}\n")
            
            return jsonify({
                'status': True,
                'data': {
                    'id_venta': venta['id_venta'],
                    'codigo_qr': venta['codigo_qr'],
                    'total': float(venta['total']) if venta['total'] else 0.0,
                    'entregado': venta['entregado'],
                    'nombre_sucursal': venta['nombre_sucursal']
                },
                'message': 'Código válido'
            }), 200
        else:
            print(f"❌ Venta no encontrada")
            print(f"{'='*60}\n")
            
            return jsonify({
                'status': False,
                'data': None,
                'message': 'Código de venta no encontrado'
            }), 404
        
    except Exception as e:
        print(f"\n💥 ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}\n")
        
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500
