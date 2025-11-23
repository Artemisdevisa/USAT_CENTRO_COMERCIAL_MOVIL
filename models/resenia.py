from conexionBD import Conexion

class Resenia:
    def __init__(self):
        pass
    
    # ============================================
    # LISTAR RESEÑAS POR PRODUCTO_COLOR
    # ============================================
    def listar_por_producto(self, id_prod_color):
        """Listar todas las reseñas de un producto_color específico"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    r.id_resenia,
                    r.titulo,
                    r.comentario,
                    r.calificacion,
                    r.fecha_resenia,
                    u.nomusuario,
                    p.nombres,
                    p.apellidos,
                    u.img_logo as avatar_usuario
                FROM resenia_producto r
                INNER JOIN usuario u ON r.id_usuario = u.id_usuario
                INNER JOIN persona p ON u.id_persona = p.id_persona
                WHERE r.id_prod_color = %s 
                  AND r.estado = TRUE
                ORDER BY r.fecha_resenia DESC
            """
            
            cursor.execute(sql, [id_prod_color])
            resultado = cursor.fetchall()
            
            cursor.close()
            con.close()
            
            if resultado:
                resenias = []
                for row in resultado:
                    resenias.append({
                        'id_resenia': row['id_resenia'],
                        'titulo': row['titulo'],
                        'comentario': row['comentario'],
                        'calificacion': row['calificacion'],
                        'fecha_resenia': row['fecha_resenia'].strftime('%Y-%m-%d %H:%M') if row['fecha_resenia'] else None,
                        'usuario': row['nomusuario'],
                        'nombre_completo': f"{row['nombres']} {row['apellidos']}",
                        'avatar_usuario': row['avatar_usuario'] if row['avatar_usuario'] else None
                    })
                return True, resenias
            else:
                return True, []
                
        except Exception as e:
            return False, f"Error al listar reseñas: {str(e)}"
    
    # ============================================
    # OBTENER RESEÑA POR ID
    # ============================================
    def obtener_por_id(self, id_resenia):
        """Obtener una reseña específica por su ID"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    r.id_resenia,
                    r.id_prod_color,
                    r.id_det_vent,
                    r.id_usuario,
                    r.titulo,
                    r.comentario,
                    r.calificacion,
                    r.fecha_resenia,
                    r.estado
                FROM resenia_producto r
                WHERE r.id_resenia = %s
            """
            
            cursor.execute(sql, [id_resenia])
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            if resultado:
                return True, {
                    'id_resenia': resultado['id_resenia'],
                    'id_prod_color': resultado['id_prod_color'],
                    'id_det_vent': resultado['id_det_vent'],
                    'id_usuario': resultado['id_usuario'],
                    'titulo': resultado['titulo'],
                    'comentario': resultado['comentario'],
                    'calificacion': resultado['calificacion'],
                    'fecha_resenia': resultado['fecha_resenia'].strftime('%Y-%m-%d %H:%M') if resultado['fecha_resenia'] else None,
                    'estado': resultado['estado']
                }
            else:
                return False, 'Reseña no encontrada'
                
        except Exception as e:
            return False, f"Error al obtener reseña: {str(e)}"
    
    # ============================================
    # CREAR RESEÑA
    # ============================================
    def crear(self, id_prod_color, id_det_vent, id_usuario, titulo, comentario, calificacion):
        """Crear una nueva reseña usando la función de PostgreSQL"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Llamar a la función fn_resenia_crear
            sql = "SELECT fn_resenia_crear(%s, %s, %s, %s, %s, %s) as resultado"
            cursor.execute(sql, [id_prod_color, id_det_vent, id_usuario, titulo, comentario, calificacion])
            
            resultado = cursor.fetchone()
            id_resenia = resultado['resultado']
            
            con.commit()
            cursor.close()
            con.close()
            
            if id_resenia and id_resenia > 0:
                return True, id_resenia
            elif id_resenia == -2:
                return False, 'No puedes reseñar este producto porque no lo has comprado'
            elif id_resenia == -3:
                return False, 'Ya has reseñado este producto anteriormente'
            else:
                return False, 'No se pudo crear la reseña. Verifica que todos los datos sean válidos.'
                
        except Exception as e:
            return False, f"Error al crear reseña: {str(e)}"
    
    # ============================================
    # MODIFICAR RESEÑA
    # ============================================
    def modificar(self, id_resenia, titulo, comentario, calificacion):
        """Modificar una reseña existente usando la función de PostgreSQL"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Llamar a la función fn_resenia_modificar
            sql = "SELECT fn_resenia_modificar(%s, %s, %s, %s) as resultado"
            cursor.execute(sql, [id_resenia, titulo, comentario, calificacion])
            
            resultado = cursor.fetchone()
            codigo = resultado['resultado']
            
            con.commit()
            cursor.close()
            con.close()
            
            if codigo == 0:
                return True, 'Reseña modificada correctamente'
            else:
                return False, 'No se pudo modificar la reseña'
                
        except Exception as e:
            return False, f"Error al modificar reseña: {str(e)}"
    
    # ============================================
    # ELIMINAR RESEÑA (LÓGICO)
    # ============================================
    def eliminar(self, id_resenia):
        """Eliminar lógicamente una reseña (estado = FALSE)"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Llamar a la función fn_resenia_eliminar
            sql = "SELECT fn_resenia_eliminar(%s) as resultado"
            cursor.execute(sql, [id_resenia])
            
            resultado = cursor.fetchone()
            codigo = resultado['resultado']
            
            con.commit()
            cursor.close()
            con.close()
            
            if codigo == 0:
                return True, 'Reseña eliminada correctamente'
            else:
                return False, 'No se pudo eliminar la reseña'
                
        except Exception as e:
            return False, f"Error al eliminar reseña: {str(e)}"
    
    # ============================================
    # OBTENER PROMEDIO DE CALIFICACIÓN
    # ============================================
    def obtener_promedio_calificacion(self, id_prod_color):
        """Obtener el promedio de calificación de un producto"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = "SELECT fn_resenia_promedio_calificacion(%s) as promedio"
            cursor.execute(sql, [id_prod_color])
            
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            promedio = float(resultado['promedio']) if resultado and resultado['promedio'] else 0.0
            return True, promedio
                
        except Exception as e:
            return False, f"Error al obtener promedio: {str(e)}"
    
    # ============================================
    # CONTAR RESEÑAS
    # ============================================
    def contar_por_producto(self, id_prod_color):
        """Contar total de reseñas de un producto"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = "SELECT fn_resenia_contar_por_producto(%s) as total"
            cursor.execute(sql, [id_prod_color])
            
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            return resultado['total'] if resultado else 0
                
        except Exception as e:
            return 0
    
    # ============================================
    # VERIFICAR SI USUARIO YA RESEÑÓ
    # ============================================
    def verificar_existencia(self, id_prod_color, id_usuario):
        """Verificar si un usuario ya reseñó un producto"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = "SELECT fn_resenia_verificar_existencia(%s, %s) as existe"
            cursor.execute(sql, [id_prod_color, id_usuario])
            
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            return resultado['existe'] if resultado else False
                
        except Exception as e:
            return False
    
    # ============================================
    # VERIFICAR SI USUARIO PUEDE RESEÑAR
    # ============================================
    def puede_reseniar(self, id_prod_color, id_usuario):
        """Verificar si un usuario puede reseñar (debe haber comprado el producto)"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = "SELECT fn_resenia_puede_reseniar(%s, %s) as puede"
            cursor.execute(sql, [id_prod_color, id_usuario])
            
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            return resultado['puede'] if resultado else False
                
        except Exception as e:
            return False
    
    # ============================================
    # LISTAR RESEÑAS POR USUARIO
    # ============================================
    def listar_por_usuario(self, id_usuario):
        """Listar todas las reseñas de un usuario específico"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    r.id_resenia,
                    r.titulo,
                    r.comentario,
                    r.calificacion,
                    r.fecha_resenia,
                    ps.nombre as nombre_producto,
                    c.nombre as color,
                    pc.talla,
                    pc.url_img
                FROM resenia_producto r
                INNER JOIN producto_color pc ON r.id_prod_color = pc.id_prod_color
                INNER JOIN producto_sucursal ps ON pc.id_prod_sucursal = ps.id_prod_sucursal
                INNER JOIN color c ON pc.id_color = c.id_color
                WHERE r.id_usuario = %s 
                  AND r.estado = TRUE
                ORDER BY r.fecha_resenia DESC
            """
            
            cursor.execute(sql, [id_usuario])
            resultado = cursor.fetchall()
            
            cursor.close()
            con.close()
            
            if resultado:
                resenias = []
                for row in resultado:
                    resenias.append({
                        'id_resenia': row['id_resenia'],
                        'titulo': row['titulo'],
                        'comentario': row['comentario'],
                        'calificacion': row['calificacion'],
                        'fecha_resenia': row['fecha_resenia'].strftime('%Y-%m-%d %H:%M') if row['fecha_resenia'] else None,
                        'nombre_producto': row['nombre_producto'],
                        'color': row['color'],
                        'talla': row['talla'],
                        'url_img': row['url_img']
                    })
                return True, resenias
            else:
                return True, []
                
        except Exception as e:
            return False, f"Error al listar reseñas por usuario: {str(e)}"
    
    # ============================================
    # OBTENER ESTADÍSTICAS DE CALIFICACIONES
    # ============================================
    def obtener_estadisticas(self, id_prod_color):
        """Obtener estadísticas detalladas de calificaciones de un producto"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    COUNT(*) as total_resenias,
                    ROUND(AVG(calificacion), 1) as promedio,
                    COUNT(CASE WHEN calificacion = 5 THEN 1 END) as cinco_estrellas,
                    COUNT(CASE WHEN calificacion = 4 THEN 1 END) as cuatro_estrellas,
                    COUNT(CASE WHEN calificacion = 3 THEN 1 END) as tres_estrellas,
                    COUNT(CASE WHEN calificacion = 2 THEN 1 END) as dos_estrellas,
                    COUNT(CASE WHEN calificacion = 1 THEN 1 END) as una_estrella
                FROM resenia_producto
                WHERE id_prod_color = %s
                  AND estado = TRUE
            """
            
            cursor.execute(sql, [id_prod_color])
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            if resultado:
                return True, {
                    'total_resenias': resultado['total_resenias'],
                    'promedio': float(resultado['promedio']) if resultado['promedio'] else 0.0,
                    'cinco_estrellas': resultado['cinco_estrellas'],
                    'cuatro_estrellas': resultado['cuatro_estrellas'],
                    'tres_estrellas': resultado['tres_estrellas'],
                    'dos_estrellas': resultado['dos_estrellas'],
                    'una_estrella': resultado['una_estrella']
                }
            else:
                return True, {
                    'total_resenias': 0,
                    'promedio': 0.0,
                    'cinco_estrellas': 0,
                    'cuatro_estrellas': 0,
                    'tres_estrellas': 0,
                    'dos_estrellas': 0,
                    'una_estrella': 0
                }
                
        except Exception as e:
            return False, f"Error al obtener estadísticas: {str(e)}"