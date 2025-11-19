from flask import Blueprint, jsonify, request
from models.cupon import Cupon

ws_cupon = Blueprint('ws_cupon', __name__)

@ws_cupon.route('/cupones/listar', methods=['GET'])
def listar_cupones():
    """Listar todos los cupones"""
    try:
        cupones = Cupon.listar()
        
        return jsonify({
            'status': True,
            'data': cupones
        }), 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': False,
            'data': [],
            'message': f'Error: {str(e)}'
        }), 500


@ws_cupon.route('/cupones/listar-por-sucursal/<int:id_sucursal>', methods=['GET'])
def listar_por_sucursal(id_sucursal):
    """Listar cupones activos de una sucursal"""
    try:
        print(f"📥 Listando cupones para sucursal: {id_sucursal}")
        cupones = Cupon.listar_por_sucursal(id_sucursal)
        
        print(f"✅ Cupones encontrados: {len(cupones) if cupones else 0}")
        
        return jsonify({
            'status': True,
            'data': cupones
        }), 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': False,
            'data': [],
            'message': f'Error: {str(e)}'
        }), 500


@ws_cupon.route('/cupones/crear', methods=['POST'])
def crear_cupon():
    """Crear un nuevo cupón"""
    try:
        data = request.get_json()
        
        print(f"📥 Datos recibidos para crear cupón: {data}")
        
        # Validaciones
        if not data.get('codigo'):
            return jsonify({'status': False, 'message': 'El código es requerido'}), 400
        
        if not data.get('descripcion'):
            return jsonify({'status': False, 'message': 'La descripción es requerida'}), 400
        
        if not data.get('id_sucursal'):
            return jsonify({'status': False, 'message': 'La sucursal es requerida'}), 400
        
        # Crear cupón
        resultado = Cupon.crear(
            codigo=data['codigo'],
            descripcion=data['descripcion'],
            porcentaje_descuento=float(data['porcentaje_descuento']),
            monto_minimo=float(data.get('monto_minimo', 0)),
            id_sucursal=int(data['id_sucursal']),
            id_categoria=int(data['id_categoria']) if data.get('id_categoria') else None,
            fecha_inicio=data['fecha_inicio'],
            fecha_fin=data['fecha_fin'],
            cantidad_total=int(data['cantidad_total'])
        )
        
        if resultado > 0:
            return jsonify({
                'status': True,
                'message': 'Cupón creado correctamente',
                'data': {'id_cupon': resultado}
            }), 201
        else:
            return jsonify({
                'status': False,
                'message': 'Error al crear el cupón. Verifique que el código no exista.'
            }), 400
        
    except Exception as e:
        print(f"❌ Error al crear cupón: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500


@ws_cupon.route('/cupones/modificar/<int:id_cupon>', methods=['PUT'])
def modificar_cupon(id_cupon):
    """Modificar un cupón existente"""
    try:
        data = request.get_json()
        
        print(f"📥 Modificando cupón {id_cupon}: {data}")
        
        resultado = Cupon.modificar(
            id_cupon=id_cupon,
            descripcion=data['descripcion'],
            porcentaje_descuento=float(data['porcentaje_descuento']),
            monto_minimo=float(data.get('monto_minimo', 0)),
            fecha_inicio=data['fecha_inicio'],
            fecha_fin=data['fecha_fin'],
            cantidad_total=int(data['cantidad_total'])
        )
        
        if resultado == 0:
            return jsonify({
                'status': True,
                'message': 'Cupón modificado correctamente'
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': 'Error al modificar el cupón'
            }), 400
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500


@ws_cupon.route('/cupones/eliminar/<int:id_cupon>', methods=['DELETE'])
def eliminar_cupon(id_cupon):
    """Eliminar un cupón (lógico)"""
    try:
        print(f"🗑️ Eliminando cupón {id_cupon}")
        
        resultado = Cupon.eliminar(id_cupon)
        
        if resultado == 0:
            return jsonify({
                'status': True,
                'message': 'Cupón eliminado correctamente'
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': 'Error al eliminar el cupón'
            }), 400
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500
    
@ws_cupon.route('/cupones/mejor-descuento', methods=['GET'])
def obtener_mejor_descuento():
    """Obtener el cupón con mayor descuento activo de todas las sucursales"""
    try:
        print("🔍 Buscando cupón con mayor descuento...")
        
        con = Conexion().open
        cursor = con.cursor()
        
        # Buscar el cupón con mayor descuento que esté activo y vigente
        cursor.execute("""
            SELECT 
                id_cupon,
                codigo,
                descripcion,
                porcentaje_descuento,
                monto_minimo,
                fecha_inicio,
                fecha_fin,
                cantidad_total,
                cantidad_usada,
                id_sucursal,
                id_categoria
            FROM cupon
            WHERE estado = TRUE
                AND fecha_inicio <= NOW()
                AND fecha_fin >= NOW()
                AND cantidad_usada < cantidad_total
            ORDER BY porcentaje_descuento DESC
            LIMIT 1
        """)
        
        resultado = cursor.fetchone()
        cursor.close()
        con.close()
        
        if resultado:
            cupon = {
                'id_cupon': resultado['id_cupon'],
                'codigo': resultado['codigo'],
                'descripcion': resultado['descripcion'],
                'porcentaje_descuento': float(resultado['porcentaje_descuento']),
                'monto_minimo': float(resultado['monto_minimo']),
                'fecha_inicio': resultado['fecha_inicio'].isoformat() if resultado['fecha_inicio'] else None,
                'fecha_fin': resultado['fecha_fin'].isoformat() if resultado['fecha_fin'] else None,
                'cantidad_disponible': resultado['cantidad_total'] - resultado['cantidad_usada']
            }
            
            print(f"✅ Mejor cupón encontrado: {cupon['codigo']} - {cupon['porcentaje_descuento']}%")
            
            return jsonify({
                'status': True,
                'data': cupon
            }), 200
        else:
            print("⚠️ No hay cupones disponibles")
            return jsonify({
                'status': False,
                'data': None,
                'message': 'No hay cupones disponibles'
            }), 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': False,
            'data': None,
            'message': f'Error: {str(e)}'
        }), 500