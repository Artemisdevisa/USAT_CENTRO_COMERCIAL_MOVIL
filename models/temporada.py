from conexionBD import Conexion

class Temporada:
    def __init__(self):
        pass
    
    def listar(self):
        """Listar TODAS las temporadas (activas e inactivas) para el dashboard"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    id_temporada,
                    nombre,
                    fecha_inicio,
                    fecha_fin,
                    estado
                FROM temporada
                ORDER BY id_temporada DESC
            """
            
            cursor.execute(sql)
            resultado = cursor.fetchall()
            
            cursor.close()
            con.close()
            
            if resultado:
                temporadas = []
                for row in resultado:
                    temporadas.append({
                        'id_temporada': row['id_temporada'],
                        'nombre': row['nombre'],
                        'fecha_inicio': row['fecha_inicio'].strftime('%Y-%m-%d') if row['fecha_inicio'] else None,
                        'fecha_fin': row['fecha_fin'].strftime('%Y-%m-%d') if row['fecha_fin'] else None,
                        'estado': row['estado']
                    })
                return True, temporadas
            else:
                return True, []
                
        except Exception as e:
            return False, f"Error al listar temporadas: {str(e)}"
    
    def obtener_por_id(self, id_temporada):
        """Obtener una temporada por su ID"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    id_temporada,
                    nombre,
                    fecha_inicio,
                    fecha_fin,
                    estado
                FROM temporada
                WHERE id_temporada = %s
            """
            
            cursor.execute(sql, [id_temporada])
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            if resultado:
                return True, {
                    'id_temporada': resultado['id_temporada'],
                    'nombre': resultado['nombre'],
                    'fecha_inicio': resultado['fecha_inicio'].strftime('%Y-%m-%d') if resultado['fecha_inicio'] else None,
                    'fecha_fin': resultado['fecha_fin'].strftime('%Y-%m-%d') if resultado['fecha_fin'] else None,
                    'estado': resultado['estado']
                }
            else:
                return False, 'Temporada no encontrada'
                
        except Exception as e:
            return False, f"Error al obtener temporada: {str(e)}"
    
    def crear(self, nombre, fecha_inicio, fecha_fin):
        """Crear una nueva temporada usando la función de PostgreSQL"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Llamar a la función fn_temporada_crear
            sql = "SELECT fn_temporada_crear(%s, %s, %s) as resultado"
            cursor.execute(sql, [nombre, fecha_inicio, fecha_fin])
            
            resultado = cursor.fetchone()
            id_temporada = resultado['resultado']
            
            con.commit()
            cursor.close()
            con.close()
            
            if id_temporada and id_temporada > 0:
                return True, id_temporada
            else:
                return False, 'No se pudo crear la temporada. Verifica que el nombre no exista y las fechas sean correctas.'
                
        except Exception as e:
            return False, f"Error al crear temporada: {str(e)}"
    
    def modificar(self, id_temporada, nombre, fecha_inicio, fecha_fin):
        """Modificar una temporada usando la función de PostgreSQL"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Llamar a la función fn_temporada_modificar
            sql = "SELECT fn_temporada_modificar(%s, %s, %s, %s) as resultado"
            cursor.execute(sql, [id_temporada, nombre, fecha_inicio, fecha_fin])
            
            resultado = cursor.fetchone()
            codigo = resultado['resultado']
            
            con.commit()
            cursor.close()
            con.close()
            
            if codigo == 0:
                return True, 'Temporada modificada correctamente'
            else:
                return False, 'No se pudo modificar la temporada. Verifica que el nombre no exista y las fechas sean correctas.'
                
        except Exception as e:
            return False, f"Error al modificar temporada: {str(e)}"
    
    def cambiar_estado(self, id_temporada):
        """Cambiar el estado de una temporada (activar/desactivar)"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Obtener estado actual
            sql_get = "SELECT estado FROM temporada WHERE id_temporada = %s"
            cursor.execute(sql_get, [id_temporada])
            resultado = cursor.fetchone()
            
            if not resultado:
                cursor.close()
                con.close()
                return False, 'Temporada no encontrada'
            
            # Cambiar al estado contrario
            nuevo_estado = not resultado['estado']
            sql_update = "UPDATE temporada SET estado = %s WHERE id_temporada = %s"
            cursor.execute(sql_update, [nuevo_estado, id_temporada])
            
            con.commit()
            cursor.close()
            con.close()
            
            return True, 'Estado cambiado correctamente'
                
        except Exception as e:
            return False, f"Error al cambiar estado: {str(e)}"
    
    def eliminar_logico(self, id_temporada):
        """Eliminar lógicamente una temporada (cambiar estado a FALSE)"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Llamar a la función fn_temporada_eliminar (que hace eliminación lógica)
            sql = "SELECT fn_temporada_eliminar(%s) as resultado"
            cursor.execute(sql, [id_temporada])
            
            resultado = cursor.fetchone()
            codigo = resultado['resultado']
            
            con.commit()
            cursor.close()
            con.close()
            
            if codigo == 0:
                return True, 'Temporada desactivada correctamente'
            else:
                return False, 'No se puede desactivar la temporada porque tiene productos activos asociados'
                
        except Exception as e:
            return False, f"Error al eliminar temporada: {str(e)}"
    
    def contar_productos(self, id_temporada):
        """Contar productos activos asociados a una temporada"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT COUNT(*) as total
                FROM producto_sucursal
                WHERE id_temporada = %s AND estado = TRUE
            """
            
            cursor.execute(sql, [id_temporada])
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            return resultado['total'] if resultado else 0
                
        except Exception as e:
            return 0