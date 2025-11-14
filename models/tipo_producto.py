from conexionBD import Conexion

class TipoProducto:
    def __init__(self):
        pass
    
    # ============================================
    # MÉTODOS EXISTENTES (Para listar en front público)
    # ============================================
    
    def listar_tipos(self):
        """Listar tipos de producto activos para el frontend público"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    id_tipo_prod,
                    nombre
                FROM tipo_producto
                WHERE estado = TRUE
                ORDER BY nombre
            """
            
            cursor.execute(sql)
            resultados = cursor.fetchall()
            
            tipos = []
            for row in resultados:
                tipo = {
                    "id_tipo_prod": row['id_tipo_prod'],
                    "nombre": row['nombre']
                }
                tipos.append(tipo)
            
            cursor.close()
            con.close()
            
            return True, tipos
                
        except Exception as e:
            return False, f"Error al listar tipos: {str(e)}"
    
    # ============================================
    # MÉTODOS CRUD (Para dashboard/admin)
    # ============================================
    
    def listar(self):
        """Listar TODOS los tipos de producto (activos e inactivos) para el dashboard"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    id_tipo_prod,
                    nombre,
                    estado
                FROM tipo_producto
                ORDER BY id_tipo_prod DESC
            """
            
            cursor.execute(sql)
            resultado = cursor.fetchall()
            
            cursor.close()
            con.close()
            
            if resultado:
                tipos = []
                for row in resultado:
                    tipos.append({
                        'id_tipo_prod': row['id_tipo_prod'],
                        'nombre': row['nombre'],
                        'estado': row['estado']
                    })
                return True, tipos
            else:
                return True, []
                
        except Exception as e:
            return False, f"Error al listar tipos de producto: {str(e)}"
    
    def obtener_por_id(self, id_tipo_prod):
        """Obtener un tipo de producto por su ID"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    id_tipo_prod,
                    nombre,
                    estado
                FROM tipo_producto
                WHERE id_tipo_prod = %s
            """
            
            cursor.execute(sql, [id_tipo_prod])
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            if resultado:
                return True, {
                    'id_tipo_prod': resultado['id_tipo_prod'],
                    'nombre': resultado['nombre'],
                    'estado': resultado['estado']
                }
            else:
                return False, 'Tipo de producto no encontrado'
                
        except Exception as e:
            return False, f"Error al obtener tipo de producto: {str(e)}"
    
    def crear(self, nombre):
        """Crear un nuevo tipo de producto usando la función de PostgreSQL"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Llamar a la función fn_tipo_producto_crear
            sql = "SELECT fn_tipo_producto_crear(%s) as resultado"
            cursor.execute(sql, [nombre])
            
            resultado = cursor.fetchone()
            id_tipo_prod = resultado['resultado']
            
            con.commit()
            cursor.close()
            con.close()
            
            if id_tipo_prod and id_tipo_prod > 0:
                return True, id_tipo_prod
            else:
                return False, 'No se pudo crear el tipo de producto. Ya existe un tipo con ese nombre.'
                
        except Exception as e:
            return False, f"Error al crear tipo de producto: {str(e)}"
    
    def modificar(self, id_tipo_prod, nombre):
        """Modificar un tipo de producto usando la función de PostgreSQL"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Llamar a la función fn_tipo_producto_modificar
            sql = "SELECT fn_tipo_producto_modificar(%s, %s) as resultado"
            cursor.execute(sql, [id_tipo_prod, nombre])
            
            resultado = cursor.fetchone()
            codigo = resultado['resultado']
            
            con.commit()
            cursor.close()
            con.close()
            
            if codigo == 0:
                return True, 'Tipo de producto modificado correctamente'
            else:
                return False, 'No se pudo modificar el tipo de producto. Ya existe un tipo con ese nombre.'
                
        except Exception as e:
            return False, f"Error al modificar tipo de producto: {str(e)}"
    
    def cambiar_estado(self, id_tipo_prod):
        """Cambiar el estado de un tipo de producto (activar/desactivar)"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Obtener estado actual
            sql_get = "SELECT estado FROM tipo_producto WHERE id_tipo_prod = %s"
            cursor.execute(sql_get, [id_tipo_prod])
            resultado = cursor.fetchone()
            
            if not resultado:
                cursor.close()
                con.close()
                return False, 'Tipo de producto no encontrado'
            
            # Cambiar al estado contrario
            nuevo_estado = not resultado['estado']
            sql_update = "UPDATE tipo_producto SET estado = %s WHERE id_tipo_prod = %s"
            cursor.execute(sql_update, [nuevo_estado, id_tipo_prod])
            
            con.commit()
            cursor.close()
            con.close()
            
            return True, 'Estado cambiado correctamente'
                
        except Exception as e:
            return False, f"Error al cambiar estado: {str(e)}"
    
    def eliminar_fisico(self, id_tipo_prod):
        """Eliminar FÍSICAMENTE un tipo de producto (DELETE permanente)"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Verificar que existe
            sql_check_exists = "SELECT COUNT(*) as total FROM tipo_producto WHERE id_tipo_prod = %s"
            cursor.execute(sql_check_exists, [id_tipo_prod])
            existe = cursor.fetchone()
            
            if existe['total'] == 0:
                cursor.close()
                con.close()
                return False, 'Tipo de producto no encontrado'
            
            # Verificar que no tenga modelos asociados (ni activos ni inactivos)
            sql_check_modelos = """
                SELECT COUNT(*) as total
                FROM tipo_modelo_producto
                WHERE id_tipo_prod = %s
            """
            cursor.execute(sql_check_modelos, [id_tipo_prod])
            resultado = cursor.fetchone()
            
            if resultado['total'] > 0:
                cursor.close()
                con.close()
                return False, f'No se puede eliminar porque tiene {resultado["total"]} modelo(s) asociado(s)'
            
            # Eliminar físicamente (DELETE)
            sql_delete = "DELETE FROM tipo_producto WHERE id_tipo_prod = %s"
            cursor.execute(sql_delete, [id_tipo_prod])
            
            con.commit()
            cursor.close()
            con.close()
            
            return True, 'Tipo de producto eliminado permanentemente de la base de datos'
                
        except Exception as e:
            return False, f"Error al eliminar tipo de producto: {str(e)}"
    
    def contar_modelos(self, id_tipo_prod):
        """Contar TODOS los modelos asociados a un tipo de producto (activos e inactivos)"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT COUNT(*) as total
                FROM tipo_modelo_producto
                WHERE id_tipo_prod = %s
            """
            
            cursor.execute(sql, [id_tipo_prod])
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            return resultado['total'] if resultado else 0
                
        except Exception as e:
            return 0