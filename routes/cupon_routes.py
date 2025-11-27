from flask import Blueprint, jsonify, request
from models.cupon import Cupon
from conexionBD import Conexion
import firebase.fcm as fcm

ws_cupon = Blueprint('ws_cupon', __name__)

@ws_cupon.route('/cupones/listar', methods=['GET'])
def listar_cupones():
    """
    Listar cupones con filtro opcional por empresa
    ---
    tags:
      - Cupones
    parameters:
      - name: id_empresa
        in: query
        required: false
        type: integer
        description: ID de la empresa para filtrar cupones
    responses:
      200:
        description: Lista de cupones obtenida correctamente
      500:
        description: Error interno del servidor
    """
    try:
        # ✅ OBTENER id_empresa DEL QUERY PARAM
        id_empresa = request.args.get('id_empresa', type=int)
        
        print(f"\n{'='*60}")
        print(f"📋 LISTANDO CUPONES")
        if id_empresa:
            print(f"🏢 Filtrando por empresa: {id_empresa}")
        else:
            print(f"📊 Sin filtro de empresa (todos)")
        print(f"{'='*60}")
        
        cupones = Cupon.listar(id_empresa)
        
        print(f"✅ Cupones encontrados: {len(cupones)}")
        print(f"{'='*60}\n")
        
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
    """
    Listar cupones activos de una sucursal
    ---
    tags:
      - Cupones
    parameters:
      - name: id_sucursal
        in: path
        required: true
        type: integer
        description: ID de la sucursal
    responses:
      200:
        description: Lista de cupones de la sucursal obtenida correctamente
      500:
        description: Error interno del servidor
    """
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
    """
    Crear un nuevo cupón y notificar a todos los usuarios
    ---
    tags:
      - Cupones
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - codigo
            - descripcion
            - porcentaje_descuento
            - id_sucursal
            - fecha_inicio
            - fecha_fin
            - cantidad_total
          properties:
            codigo:
              type: string
              description: Código único del cupón
            descripcion:
              type: string
              description: Descripción del cupón
            porcentaje_descuento:
              type: number
              format: float
              description: Porcentaje de descuento
            monto_minimo:
              type: number
              format: float
              description: Monto mínimo de compra para aplicar el cupón
            id_sucursal:
              type: integer
              description: ID de la sucursal asociada al cupón
            id_categoria:
              type: integer
              description: ID de la categoría asociada (opcional)
            fecha_inicio:
              type: string
              description: Fecha de inicio de vigencia del cupón (YYYY-MM-DD)
            fecha_fin:
              type: string
              description: Fecha de fin de vigencia del cupón (YYYY-MM-DD)
            cantidad_total:
              type: integer
              description: Cantidad total disponible del cupón
    responses:
      201:
        description: Cupón creado correctamente
      400:
        description: Error de validación o negocio al crear cupón
      500:
        description: Error interno del servidor
    """
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
            # ✅ ENVIAR NOTIFICACIÓN PUSH A TODOS LOS USUARIOS
            try:
                print("\n" + "="*60)
                print("🔔 ENVIANDO NOTIFICACIONES PUSH")
                print("="*60)
                
                # Obtener nombre de la sucursal
                con = Conexion().open
                cursor = con.cursor()
                cursor.execute("SELECT nombre FROM sucursal WHERE id_sucursal = %s", [data['id_sucursal']])
                sucursal = cursor.fetchone()
                nombre_sucursal = sucursal['nombre'] if sucursal else "Centro Comercial"
                cursor.close()
                con.close()
                
                # Obtener todos los tokens FCM activos
                tokens_enviados = enviar_notificacion_nuevo_cupon(
                    codigo=data['codigo'],
                    descripcion=data['descripcion'],
                    porcentaje=float(data['porcentaje_descuento']),
                    nombre_sucursal=nombre_sucursal
                )
                
                print(f"✅ Notificaciones enviadas: {tokens_enviados}")
                print("="*60 + "\n")
                
            except Exception as e:
                print(f"⚠️ Error al enviar notificaciones: {str(e)}")
                import traceback
                traceback.print_exc()
                # No fallar la creación del cupón si falla el envío de notificaciones
            
            return jsonify({
                'status': True,
                'message': 'Cupón creado correctamente',
                'data': {
                    'id_cupon': resultado,
                    'notificaciones_enviadas': tokens_enviados if 'tokens_enviados' in locals() else 0
                }
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


def enviar_notificacion_nuevo_cupon(codigo, descripcion, porcentaje, nombre_sucursal):
    """
    Envía notificación push a todos los usuarios activos sobre un nuevo cupón
    
    Args:
        codigo (str): Código del cupón
        descripcion (str): Descripción del cupón
        porcentaje (float): Porcentaje de descuento
        nombre_sucursal (str): Nombre de la sucursal
    
    Returns:
        int: Cantidad de notificaciones enviadas exitosamente
    """
    try:
        con = Conexion().open
        cursor = con.cursor()
        
        # Obtener todos los tokens FCM activos
        cursor.execute("""
            SELECT DISTINCT uf.token, uf.id_usuario
            FROM usuario_fcm uf
            INNER JOIN usuario u ON uf.id_usuario = u.id_usuario
            WHERE uf.estado = TRUE AND u.estado = TRUE
        """)
        
        tokens = cursor.fetchall()
        cursor.close()
        con.close()
        
        if not tokens:
            print("⚠️ No hay usuarios con tokens FCM activos")
            return 0
        
        print(f"📱 Usuarios con FCM activos: {len(tokens)}")
        
        # Preparar mensaje de notificación
        titulo = f"🎉 ¡Nuevo Cupón {porcentaje}% OFF!"
        cuerpo = f"Usa el código {codigo} en {nombre_sucursal}. {descripcion}"
        
        # Enviar notificaciones
        exitosas = 0
        for row in tokens:
            token = row['token']
            id_usuario = row['id_usuario']
            
            try:
                resultado = fcm.notificar(
                    device_token=token,
                    title=titulo,
                    body=cuerpo
                )
                
                if resultado:
                    exitosas += 1
                    print(f"   ✅ Notificación enviada al usuario {id_usuario}")
                else:
                    print(f"   ❌ Error al enviar a usuario {id_usuario}")
                    
            except Exception as e:
                print(f"   ❌ Error al notificar usuario {id_usuario}: {str(e)}")
                continue
        
        print(f"\n📊 Resultado: {exitosas}/{len(tokens)} notificaciones exitosas")
        return exitosas
        
    except Exception as e:
        print(f"❌ Error en enviar_notificacion_nuevo_cupon: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0


@ws_cupon.route('/cupones/modificar/<int:id_cupon>', methods=['PUT'])
def modificar_cupon(id_cupon):
    """
    Modificar un cupón existente
    ---
    tags:
      - Cupones
    parameters:
      - name: id_cupon
        in: path
        required: true
        type: integer
        description: ID del cupón a modificar
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - descripcion
            - porcentaje_descuento
            - fecha_inicio
            - fecha_fin
            - cantidad_total
          properties:
            descripcion:
              type: string
              description: Nueva descripción del cupón
            porcentaje_descuento:
              type: number
              format: float
              description: Nuevo porcentaje de descuento
            monto_minimo:
              type: number
              format: float
              description: Nuevo monto mínimo de compra
            fecha_inicio:
              type: string
              description: Nueva fecha de inicio (YYYY-MM-DD)
            fecha_fin:
              type: string
              description: Nueva fecha de fin (YYYY-MM-DD)
            cantidad_total:
              type: integer
              description: Nueva cantidad total disponible
    responses:
      200:
        description: Cupón modificado correctamente
      400:
        description: Error al modificar el cupón
      500:
        description: Error interno del servidor
    """
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
    """
    Eliminar un cupón (lógico)
    ---
    tags:
      - Cupones
    parameters:
      - name: id_cupon
        in: path
        required: true
        type: integer
        description: ID del cupón a eliminar
    responses:
      200:
        description: Cupón eliminado correctamente
      400:
        description: Error al eliminar el cupón
      500:
        description: Error interno del servidor
    """
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
    """
    Obtener el cupón con mayor descuento activo de todas las sucursales
    ---
    tags:
      - Cupones
    responses:
      200:
        description: Cupón con mayor descuento obtenido o mensaje indicando que no hay cupones
      500:
        description: Error interno del servidor
    """
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
    

@ws_cupon.route('/cupones/usar', methods=['POST'])
def usar_cupon():
    """
    Registra el uso de un cupón por un usuario
    ---
    tags:
      - Cupones
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - id_cupon
            - id_usuario
            - id_venta
          properties:
            id_cupon:
              type: integer
              description: ID del cupón a usar
            id_usuario:
              type: integer
              description: ID del usuario que usa el cupón
            id_venta:
              type: integer
              description: ID de la venta asociada al uso del cupón
    responses:
      200:
        description: Cupón aplicado correctamente
      400:
        description: Faltan datos requeridos, cupón inválido o agotado
      500:
        description: Error interno del servidor
    """
    try:
        data = request.get_json()
        
        id_cupon = data.get('id_cupon')
        id_usuario = data.get('id_usuario')
        id_venta = data.get('id_venta')
        
        print(f"\n{'='*60}")
        print(f"🎫 REGISTRANDO USO DE CUPÓN")
        print(f"   ID Cupón: {id_cupon}")
        print(f"   ID Usuario: {id_usuario}")
        print(f"   ID Venta: {id_venta}")
        print(f"{'='*60}")
        
        if not id_cupon or not id_usuario or not id_venta:
            return jsonify({
                'status': False,
                'message': 'Faltan datos requeridos'
            }), 400
        
        con = Conexion().open
        cursor = con.cursor()
        
        # Verificar si el usuario ya usó este cupón
        cursor.execute("""
            SELECT COUNT(*) as usado
            FROM cupon_usuario
            WHERE id_cupon = %s AND id_usuario = %s
        """, [id_cupon, id_usuario])
        
        resultado = cursor.fetchone()
        
        if resultado['usado'] > 0:
            cursor.close()
            con.close()
            print("❌ Usuario ya usó este cupón")
            return jsonify({
                'status': False,
                'message': 'Ya has usado este cupón anteriormente'
            }), 400
        
        # Verificar que el cupón esté disponible
        cursor.execute("""
            SELECT cantidad_total, cantidad_usada
            FROM cupon
            WHERE id_cupon = %s AND estado = TRUE
        """, [id_cupon])
        
        cupon = cursor.fetchone()
        
        if not cupon:
            cursor.close()
            con.close()
            print("❌ Cupón no encontrado")
            return jsonify({
                'status': False,
                'message': 'Cupón no válido'
            }), 400
        
        if cupon['cantidad_usada'] >= cupon['cantidad_total']:
            cursor.close()
            con.close()
            print("❌ Cupón agotado")
            return jsonify({
                'status': False,
                'message': 'Este cupón ya no está disponible'
            }), 400
        
        # Registrar uso del cupón
        cursor.execute("""
            INSERT INTO cupon_usuario (id_cupon, id_usuario, id_venta, fecha_uso)
            VALUES (%s, %s, %s, NOW())
        """, [id_cupon, id_usuario, id_venta])
        
        # Incrementar cantidad_usada
        cursor.execute("""
            UPDATE cupon
            SET cantidad_usada = cantidad_usada + 1
            WHERE id_cupon = %s
        """, [id_cupon])
        
        con.commit()
        cursor.close()
        con.close()
        
        print("✅ Cupón registrado exitosamente")
        print(f"{'='*60}\n")
        
        return jsonify({
            'status': True,
            'message': 'Cupón aplicado correctamente'
        }), 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500
    
@ws_cupon.route('/cupones/verificar-uso/<int:id_cupon>/<int:id_usuario>', methods=['GET'])
def verificar_uso_cupon(id_cupon, id_usuario):
    """
    Verifica si un usuario ya usó un cupón específico
    ---
    tags:
      - Cupones
    parameters:
      - name: id_cupon
        in: path
        required: true
        type: integer
        description: ID del cupón
      - name: id_usuario
        in: path
        required: true
        type: integer
        description: ID del usuario
    responses:
      200:
        description: Verificación de uso del cupón realizada correctamente
      404:
        description: Cupón no encontrado
      500:
        description: Error interno del servidor
    """
    try:
        print(f"\n{'='*60}")
        print(f"🔍 VERIFICANDO USO DE CUPÓN")
        print(f"   ID Cupón: {id_cupon}")
        print(f"   ID Usuario: {id_usuario}")
        print(f"{'='*60}")
        
        con = Conexion().open
        cursor = con.cursor()
        
        # ✅ VERIFICAR SI YA LO USÓ
        cursor.execute("""
            SELECT COUNT(*) as usado
            FROM cupon_usuario
            WHERE id_cupon = %s AND id_usuario = %s
        """, [id_cupon, id_usuario])
        
        resultado = cursor.fetchone()
        ya_usado = resultado['usado'] > 0
        
        # ✅ VERIFICAR DISPONIBILIDAD
        cursor.execute("""
            SELECT 
                cantidad_total,
                cantidad_usada,
                (cantidad_total - cantidad_usada) as disponibles
            FROM cupon
            WHERE id_cupon = %s AND estado = TRUE
        """, [id_cupon])
        
        cupon_data = cursor.fetchone()
        
        cursor.close()
        con.close()
        
        if not cupon_data:
            print("❌ Cupón no encontrado")
            return jsonify({
                'status': False,
                'ya_usado': False,
                'disponible': False,
                'message': 'Cupón no encontrado'
            }), 404
        
        disponibles = cupon_data['disponibles']
        disponible = disponibles > 0
        
        print(f"✅ Resultado:")
        print(f"   Ya usado: {ya_usado}")
        print(f"   Disponibles: {disponibles}")
        print(f"   Está disponible: {disponible}")
        print(f"{'='*60}\n")
        
        return jsonify({
            'status': True,
            'ya_usado': ya_usado,
            'disponible': disponible,
            'cantidad_disponible': disponibles,
            'message': 'Verificación exitosa'
        }), 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500
