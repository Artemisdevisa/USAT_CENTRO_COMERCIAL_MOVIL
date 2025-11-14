from conexionBD import Conexion

class Color:
    def __init__(self):
        pass
    
    def listar_todos(self):
        """Lista TODOS los colores (activos e inactivos)"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    id_color,
                    nombre,
                    estado
                FROM color
                ORDER BY nombre
            """
            
            cursor.execute(sql)
            resultado = cursor.fetchall()
            
            cursor.close()
            con.close()
            
            if resultado:
                colores = []
                for row in resultado:
                    colores.append({
                        'id_color': row['id_color'],
                        'nombre': row['nombre'],
                        'estado': row['estado']
                    })
                return True, colores
            else:
                return True, []
                
        except Exception as e:
            return False, f"Error al listar colores: {str(e)}"
    
    def obtener_por_id(self, id_color):
        """Obtener un color por su ID"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    id_color,
                    nombre,
                    estado
                FROM color
                WHERE id_color = %s
            """
            
            cursor.execute(sql, [id_color])
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            if resultado:
                return True, {
                    'id_color': resultado['id_color'],
                    'nombre': resultado['nombre'],
                    'estado': resultado['estado']
                }
            else:
                return False, 'Color no encontrado'
                
        except Exception as e:
            return False, f"Error al obtener color: {str(e)}"
    
    def crear(self, nombre):
        """Crear un nuevo color usando la función de PostgreSQL"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Llamar a la función fn_color_crear
            sql = "SELECT fn_color_crear(%s) as resultado"
            cursor.execute(sql, [nombre])
            
            resultado = cursor.fetchone()
            id_color = resultado['resultado']
            
            con.commit()
            cursor.close()
            con.close()
            
            if id_color and id_color > 0:
                return True, id_color
            else:
                return False, 'No se pudo crear el color. Verifique que el nombre no exista.'
                
        except Exception as e:
            return False, f"Error al crear color: {str(e)}"
    
    def modificar(self, id_color, nombre):
        """Modificar un color usando la función de PostgreSQL"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Llamar a la función fn_color_modificar
            sql = "SELECT fn_color_modificar(%s, %s) as resultado"
            cursor.execute(sql, [id_color, nombre])
            
            resultado = cursor.fetchone()
            code = resultado['resultado']
            
            con.commit()
            cursor.close()
            con.close()
            
            if code == 0:
                return True, 'Color modificado correctamente'
            else:
                return False, 'No se pudo modificar el color. Verifique que el nombre no exista.'
                
        except Exception as e:
            return False, f"Error al modificar color: {str(e)}"
    
    def cambiar_estado(self, id_color):
        """Cambiar el estado de un color (activar/desactivar)"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Obtener estado actual
            sql_get = "SELECT estado FROM color WHERE id_color = %s"
            cursor.execute(sql_get, [id_color])
            resultado = cursor.fetchone()
            
            if not resultado:
                cursor.close()
                con.close()
                return False, 'Color no encontrado'
            
            # Cambiar al estado contrario
            nuevo_estado = not resultado['estado']
            sql_update = "UPDATE color SET estado = %s WHERE id_color = %s"
            cursor.execute(sql_update, [nuevo_estado, id_color])
            
            con.commit()
            cursor.close()
            con.close()
            
            return True, 'Estado cambiado correctamente'
                
        except Exception as e:
            return False, f"Error al cambiar estado: {str(e)}"
    
    def eliminar_logico(self, id_color):
        """Eliminar lógicamente un color usando la función de PostgreSQL"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Llamar a la función fn_color_eliminar (lógico)
            sql = "SELECT fn_color_eliminar(%s) as resultado"
            cursor.execute(sql, [id_color])
            
            resultado = cursor.fetchone()
            code = resultado['resultado']
            
            con.commit()
            cursor.close()
            con.close()
            
            if code == 0:
                return True, 'Color eliminado correctamente'
            elif code == -1:
                return False, 'No se puede eliminar porque tiene productos asociados'
            else:
                return False, 'Error al eliminar color'
                
        except Exception as e:
            return False, f"Error al eliminar color: {str(e)}"
    
    def contar_productos(self, id_color):
        """Contar productos asociados a un color"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT COUNT(*) as total
                FROM producto_color
                WHERE id_color = %s
            """
            
            cursor.execute(sql, [id_color])
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            return resultado['total'] if resultado else 0
                
        except Exception as e:
            return 0