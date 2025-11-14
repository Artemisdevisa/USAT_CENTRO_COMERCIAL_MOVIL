from conexionBD import Conexion

class Marca:
    def __init__(self):
        pass
    
    def listar(self):
        """Listar TODAS las marcas (activas e inactivas) para el dashboard"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    id_marca,
                    nombre,
                    estado
                FROM marca
                ORDER BY id_marca DESC
            """
            
            cursor.execute(sql)
            resultado = cursor.fetchall()
            
            cursor.close()
            con.close()
            
            if resultado:
                marcas = []
                for row in resultado:
                    marcas.append({
                        'id_marca': row['id_marca'],
                        'nombre': row['nombre'],
                        'estado': row['estado']
                    })
                return True, marcas
            else:
                return True, []
                
        except Exception as e:
            return False, f"Error al listar marcas: {str(e)}"
    
    def obtener_por_id(self, id_marca):
        """Obtener una marca por su ID"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    id_marca,
                    nombre,
                    estado
                FROM marca
                WHERE id_marca = %s
            """
            
            cursor.execute(sql, [id_marca])
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            if resultado:
                return True, {
                    'id_marca': resultado['id_marca'],
                    'nombre': resultado['nombre'],
                    'estado': resultado['estado']
                }
            else:
                return False, 'Marca no encontrada'
                
        except Exception as e:
            return False, f"Error al obtener marca: {str(e)}"
    
    def crear(self, nombre):
        """Crear una nueva marca usando la función de PostgreSQL"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Llamar a la función fn_marca_crear
            sql = "SELECT fn_marca_crear(%s) as resultado"
            cursor.execute(sql, [nombre])
            
            resultado = cursor.fetchone()
            id_marca = resultado['resultado']
            
            con.commit()
            cursor.close()
            con.close()
            
            if id_marca and id_marca > 0:
                return True, id_marca
            else:
                return False, 'No se pudo crear la marca. Ya existe una marca con ese nombre.'
                
        except Exception as e:
            return False, f"Error al crear marca: {str(e)}"
    
    def modificar(self, id_marca, nombre):
        """Modificar una marca usando la función de PostgreSQL"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Llamar a la función fn_marca_modificar
            sql = "SELECT fn_marca_modificar(%s, %s) as resultado"
            cursor.execute(sql, [id_marca, nombre])
            
            resultado = cursor.fetchone()
            codigo = resultado['resultado']
            
            con.commit()
            cursor.close()
            con.close()
            
            if codigo == 0:
                return True, 'Marca modificada correctamente'
            else:
                return False, 'No se pudo modificar la marca. Ya existe una marca con ese nombre.'
                
        except Exception as e:
            return False, f"Error al modificar marca: {str(e)}"
    
    def cambiar_estado(self, id_marca):
        """Cambiar el estado de una marca (activar/desactivar)"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Obtener estado actual
            sql_get = "SELECT estado FROM marca WHERE id_marca = %s"
            cursor.execute(sql_get, [id_marca])
            resultado = cursor.fetchone()
            
            if not resultado:
                cursor.close()
                con.close()
                return False, 'Marca no encontrada'
            
            # Cambiar al estado contrario
            nuevo_estado = not resultado['estado']
            sql_update = "UPDATE marca SET estado = %s WHERE id_marca = %s"
            cursor.execute(sql_update, [nuevo_estado, id_marca])
            
            con.commit()
            cursor.close()
            con.close()
            
            return True, 'Estado cambiado correctamente'
                
        except Exception as e:
            return False, f"Error al cambiar estado: {str(e)}"
    
    def eliminar_logico(self, id_marca):
        """Eliminar lógicamente una marca (cambiar estado a FALSE)"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Llamar a la función fn_marca_eliminar (que hace eliminación lógica)
            sql = "SELECT fn_marca_eliminar(%s) as resultado"
            cursor.execute(sql, [id_marca])
            
            resultado = cursor.fetchone()
            codigo = resultado['resultado']
            
            con.commit()
            cursor.close()
            con.close()
            
            if codigo == 0:
                return True, 'Marca desactivada correctamente'
            else:
                return False, 'No se puede desactivar la marca porque tiene productos activos asociados'
                
        except Exception as e:
            return False, f"Error al eliminar marca: {str(e)}"
    
    def contar_productos(self, id_marca):
        """Contar productos activos asociados a una marca"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT COUNT(*) as total
                FROM producto_sucursal
                WHERE id_marca = %s AND estado = TRUE
            """
            
            cursor.execute(sql, [id_marca])
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            return resultado['total'] if resultado else 0
                
        except Exception as e:
            return 0