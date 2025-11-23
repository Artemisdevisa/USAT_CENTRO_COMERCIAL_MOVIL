from flask import Blueprint, jsonify, request
from models.resenia import Resenia
from conexionBD import Conexion

ws_resenia = Blueprint('ws_resenia', __name__)

# ============================================
# LISTAR RESEÑAS POR PRODUCTO_COLOR
# ============================================
@ws_resenia.route('/resenias/producto-color/<int:id_prod_color>', methods=['GET'])
def listar_resenias_producto(id_prod_color):
    """Listar todas las reseñas de un producto_color específico"""
    try:
        resenia = Resenia()
        exito, resultado = resenia.listar_por_producto(id_prod_color)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Reseñas obtenidas correctamente',
                'data': resultado
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': resultado,
                'data': []
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}',
            'data': []
        }), 500


# ============================================
# LISTAR RESEÑAS POR USUARIO
# ============================================
@ws_resenia.route('/resenias/usuario/<int:id_usuario>', methods=['GET'])
def listar_resenias_usuario(id_usuario):
    """Listar todas las reseñas de un usuario específico"""
    try:
        resenia = Resenia()
        exito, resultado = resenia.listar_por_usuario(id_usuario)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Reseñas obtenidas correctamente',
                'data': resultado
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': resultado,
                'data': []
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}',
            'data': []
        }), 500


# ============================================
# OBTENER RESEÑA POR ID
# ============================================
@ws_resenia.route('/resenias/obtener/<int:id_resenia>', methods=['GET'])
def obtener_resenia(id_resenia):
    """Obtener una reseña específica por ID"""
    try:
        resenia = Resenia()
        exito, resultado = resenia.obtener_por_id(id_resenia)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Reseña obtenida correctamente',
                'data': resultado
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': resultado,
                'data': None
            }), 404
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}',
            'data': None
        }), 500


# ============================================
# CREAR RESEÑA
# ============================================
@ws_resenia.route('/resenias/crear', methods=['POST'])
def crear_resenia():
    """Crear una nueva reseña"""
    try:
        data = request.get_json()
        
        # Validaciones
        if not data:
            return jsonify({
                'status': False,
                'message': 'No se recibieron datos'
            }), 400
        
        # Validar campos requeridos
        campos_requeridos = ['id_prod_color', 'id_det_vent', 'id_usuario', 'titulo', 'comentario', 'calificacion']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({
                    'status': False,
                    'message': f'El campo {campo} es requerido'
                }), 400
        
        id_prod_color = data.get('id_prod_color')
        id_det_vent = data.get('id_det_vent')
        id_usuario = data.get('id_usuario')
        titulo = data.get('titulo', '').strip()
        comentario = data.get('comentario', '').strip()
        calificacion = data.get('calificacion')
        
        # Validaciones adicionales
        if not titulo or not comentario:
            return jsonify({
                'status': False,
                'message': 'El título y el comentario no pueden estar vacíos'
            }), 400
        
        if not isinstance(calificacion, int) or calificacion < 1 or calificacion > 5:
            return jsonify({
                'status': False,
                'message': 'La calificación debe ser un número entre 1 y 5'
            }), 400
        
        # Crear reseña
        resenia = Resenia()
        exito, resultado = resenia.crear(id_prod_color, id_det_vent, id_usuario, titulo, comentario, calificacion)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Reseña creada correctamente',
                'data': {'id_resenia': resultado}
            }), 201
        else:
            return jsonify({
                'status': False,
                'message': resultado
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


# ============================================
# MODIFICAR RESEÑA
# ============================================
@ws_resenia.route('/resenias/modificar/<int:id_resenia>', methods=['PUT'])
def modificar_resenia(id_resenia):
    """Modificar una reseña existente"""
    try:
        data = request.get_json()
        
        # Validaciones
        if not data:
            return jsonify({
                'status': False,
                'message': 'No se recibieron datos'
            }), 400
        
        # Validar campos requeridos
        campos_requeridos = ['titulo', 'comentario', 'calificacion']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({
                    'status': False,
                    'message': f'El campo {campo} es requerido'
                }), 400
        
        titulo = data.get('titulo', '').strip()
        comentario = data.get('comentario', '').strip()
        calificacion = data.get('calificacion')
        
        # Validaciones adicionales
        if not titulo or not comentario:
            return jsonify({
                'status': False,
                'message': 'El título y el comentario no pueden estar vacíos'
            }), 400
        
        if not isinstance(calificacion, int) or calificacion < 1 or calificacion > 5:
            return jsonify({
                'status': False,
                'message': 'La calificación debe ser un número entre 1 y 5'
            }), 400
        
        # Modificar reseña
        resenia = Resenia()
        exito, mensaje = resenia.modificar(id_resenia, titulo, comentario, calificacion)
        
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
            'message': f'Error en el servidor: {str(e)}'
        }), 500


# ============================================
# ELIMINAR RESEÑA
# ============================================
@ws_resenia.route('/resenias/eliminar/<int:id_resenia>', methods=['DELETE'])
def eliminar_resenia(id_resenia):
    """Eliminar lógicamente una reseña"""
    try:
        resenia = Resenia()
        exito, mensaje = resenia.eliminar(id_resenia)
        
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
            'message': f'Error en el servidor: {str(e)}'
        }), 500


# ============================================
# OBTENER PROMEDIO DE CALIFICACIÓN
# ============================================
@ws_resenia.route('/resenias/promedio/<int:id_prod_color>', methods=['GET'])
def obtener_promedio(id_prod_color):
    """Obtener el promedio de calificación de un producto"""
    try:
        resenia = Resenia()
        exito, promedio = resenia.obtener_promedio_calificacion(id_prod_color)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Promedio obtenido correctamente',
                'data': {'promedio': promedio}
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': promedio
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


# ============================================
# CONTAR RESEÑAS
# ============================================
@ws_resenia.route('/resenias/contar/<int:id_prod_color>', methods=['GET'])
def contar_resenias(id_prod_color):
    """Contar el total de reseñas de un producto"""
    try:
        resenia = Resenia()
        total = resenia.contar_por_producto(id_prod_color)
        
        return jsonify({
            'status': True,
            'message': 'Total obtenido correctamente',
            'data': {'total': total}
        }), 200
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


# ============================================
# VERIFICAR SI USUARIO YA RESEÑÓ
# ============================================
@ws_resenia.route('/resenias/verificar-existencia', methods=['POST'])
def verificar_existencia():
    """Verificar si un usuario ya reseñó un producto"""
    try:
        data = request.get_json()
        
        if not data or 'id_prod_color' not in data or 'id_usuario' not in data:
            return jsonify({
                'status': False,
                'message': 'Se requieren id_prod_color e id_usuario'
            }), 400
        
        id_prod_color = data.get('id_prod_color')
        id_usuario = data.get('id_usuario')
        
        resenia = Resenia()
        existe = resenia.verificar_existencia(id_prod_color, id_usuario)
        
        return jsonify({
            'status': True,
            'message': 'Verificación completada',
            'data': {'existe': existe}
        }), 200
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


# ============================================
# VERIFICAR SI USUARIO PUEDE RESEÑAR
# ============================================
@ws_resenia.route('/resenias/puede-reseniar', methods=['POST'])
def puede_reseniar():
    """Verificar si un usuario puede reseñar un producto (debe haberlo comprado)"""
    try:
        data = request.get_json()
        
        if not data or 'id_prod_color' not in data or 'id_usuario' not in data:
            return jsonify({
                'status': False,
                'message': 'Se requieren id_prod_color e id_usuario'
            }), 400
        
        id_prod_color = data.get('id_prod_color')
        id_usuario = data.get('id_usuario')
        
        resenia = Resenia()
        puede = resenia.puede_reseniar(id_prod_color, id_usuario)
        
        return jsonify({
            'status': True,
            'message': 'Verificación completada',
            'data': {'puede_reseniar': puede}
        }), 200
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


# ============================================
# OBTENER ESTADÍSTICAS DE CALIFICACIONES
# ============================================
@ws_resenia.route('/resenias/estadisticas/<int:id_prod_color>', methods=['GET'])
def obtener_estadisticas(id_prod_color):
    """Obtener estadísticas detalladas de calificaciones de un producto"""
    try:
        resenia = Resenia()
        exito, estadisticas = resenia.obtener_estadisticas(id_prod_color)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Estadísticas obtenidas correctamente',
                'data': estadisticas
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': estadisticas
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


# ============================================
# ✅ LISTAR RESEÑAS POR PRODUCTO_SUCURSAL (CAMBIO DE RUTA)
# ============================================
@ws_resenia.route('/resenias/producto-sucursal/<int:id_prod_sucursal>', methods=['GET'])
def listar_resenias_por_producto_sucursal(id_prod_sucursal):
    """Listar TODAS las reseñas de TODOS los colores de un producto_sucursal"""
    try:
        print(f"=== LISTAR RESEÑAS POR PRODUCTO_SUCURSAL ===")
        print(f"id_prod_sucursal recibido: {id_prod_sucursal}")
        
        con = Conexion().open
        cursor = con.cursor()
        
        # ✅ QUERY CORRECTA: JOIN con producto_color
        sql = """
            SELECT 
                r.id_resenia,
                r.titulo,
                r.comentario,
                r.calificacion,
                TO_CHAR(r.fecha_resenia, 'YYYY-MM-DD HH24:MI') as fecha_resenia,
                u.nomusuario as usuario,
                p.nombres || ' ' || p.apellidos as nombre_completo,
                u.img_logo as avatar_usuario
            FROM resenia_producto r
            INNER JOIN producto_color pc ON r.id_prod_color = pc.id_prod_color
            INNER JOIN usuario u ON r.id_usuario = u.id_usuario
            INNER JOIN persona p ON u.id_persona = p.id_persona
            WHERE pc.id_prod_sucursal = %s 
              AND r.estado = TRUE
            ORDER BY r.fecha_resenia DESC
        """
        
        print(f"Ejecutando SQL con id_prod_sucursal = {id_prod_sucursal}")
        cursor.execute(sql, [id_prod_sucursal])
        resultado = cursor.fetchall()
        
        print(f"Filas obtenidas: {len(resultado) if resultado else 0}")
        
        cursor.close()
        con.close()
        
        if resultado:
            resenias = []
            for row in resultado:
                print(f"  ✅ Reseña: {row['titulo']} por {row['nombre_completo']}")
                resenias.append({
                    'id_resenia': row['id_resenia'],
                    'titulo': row['titulo'],
                    'comentario': row['comentario'],
                    'calificacion': row['calificacion'],
                    'fecha_resenia': row['fecha_resenia'],
                    'usuario': row['usuario'],
                    'nombre_completo': row['nombre_completo'],
                    'avatar_usuario': row['avatar_usuario'] if row['avatar_usuario'] else None
                })
            
            print(f"Total reseñas devueltas: {len(resenias)}")
            return jsonify({
                'status': True,
                'message': 'Reseñas obtenidas correctamente',
                'data': resenias
            }), 200
        else:
            print("❌ No hay reseñas para este producto_sucursal")
            return jsonify({
                'status': True,
                'message': 'No hay reseñas para este producto',
                'data': []
            }), 200
            
    except Exception as e:
        print(f"💥 ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}',
            'data': []
        }), 500


# ============================================
# OBTENER ID_DETALLE_VENTA
# ============================================
@ws_resenia.route('/resenias/obtener-id-det-vent', methods=['POST'])
def obtener_id_det_vent():
    """Obtener el id_detalle_venta de la última compra del usuario con un producto_color"""
    try:
        data = request.get_json()
        id_usuario = data.get('id_usuario')
        id_prod_color = data.get('id_prod_color')
        
        print(f"=== OBTENER ID_DET_VENT ===")
        print(f"id_usuario: {id_usuario}")
        print(f"id_prod_color: {id_prod_color}")
        
        if not id_usuario or not id_prod_color:
            return jsonify({
                'status': False,
                'message': 'Faltan parámetros: id_usuario o id_prod_color'
            }), 400
        
        con = Conexion().open
        cursor = con.cursor()
        
        # ✅ SQL CORRECTO: Usar nombres reales de columnas
        sql = """
            SELECT dv.id_detalle_venta
            FROM detalle_venta dv
            INNER JOIN venta v ON dv.id_venta = v.id_venta
            WHERE v.id_usuario = %s 
              AND dv.id_prod_color = %s
              AND v.estado = TRUE
            ORDER BY v.created_at DESC
            LIMIT 1
        """
        
        print(f"Ejecutando SQL...")
        cursor.execute(sql, [id_usuario, id_prod_color])
        resultado = cursor.fetchone()
        
        print(f"Resultado: {resultado}")
        
        cursor.close()
        con.close()
        
        if resultado:
            id_det_vent = resultado['id_detalle_venta']
            print(f"✅ id_detalle_venta encontrado: {id_det_vent}")
            
            return jsonify({
                'status': True,
                'message': 'Detalle de venta encontrado',
                'data': {
                    'id_det_vent': id_det_vent
                }
            }), 200
        else:
            print(f"❌ No se encontró compra del usuario {id_usuario} con producto_color {id_prod_color}")
            return jsonify({
                'status': False,
                'message': 'No has comprado este producto aún'
            }), 400
            
    except Exception as e:
        print(f"💥 ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500