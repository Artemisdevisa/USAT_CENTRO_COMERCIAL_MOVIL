from flask import Blueprint, request, jsonify
from conexionBD import Conexion

ws_entrega = Blueprint('ws_entrega', __name__)

@ws_entrega.route('/entregas/sucursales/<int:id_empresa>', methods=['GET'])
def listar_sucursales_empresa(id_empresa):
    """Listar sucursales de una empresa con estadísticas de ventas"""
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
    """Listar ventas de una sucursal con filtro de entrega"""
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
    """Marcar venta como entregada mediante código QR"""
    try:
        data = request.get_json()
        codigo_venta = data.get('codigo_venta')
        
        if not codigo_venta:
            return jsonify({
                'status': False,
                'message': 'Código de venta requerido'
            }), 400
        
        print(f"\n{'='*60}")
        print(f"📦 MARCAR VENTA COMO ENTREGADA")
        print(f"   Código QR: {codigo_venta}")
        print(f"{'='*60}")
        
        con = Conexion().open
        cursor = con.cursor()
        
        cursor.execute("SELECT fn_marcar_venta_entregada(%s)", [codigo_venta])
        resultado = cursor.fetchone()[0]
        
        con.commit()
        cursor.close()
        con.close()
        
        if resultado['success']:
            print(f"✅ Venta marcada como entregada")
            return jsonify({
                'status': True,
                'data': resultado,
                'message': resultado['message']
            }), 200
        else:
            print(f"❌ Error: {resultado['message']}")
            return jsonify({
                'status': False,
                'data': resultado,
                'message': resultado['message']
            }), 400
        
    except Exception as e:
        print(f"💥 ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500


@ws_entrega.route('/entregas/verificar-codigo', methods=['POST'])
def verificar_codigo_venta():
    """Verificar si un código QR es válido"""
    try:
        data = request.get_json()
        codigo_venta = data.get('codigo_venta')
        
        if not codigo_venta:
            return jsonify({
                'status': False,
                'message': 'Código de venta requerido'
            }), 400
        
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
            return jsonify({
                'status': False,
                'data': None,
                'message': 'Código de venta no encontrado'
            }), 404
        
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500