from conexionBD import Conexion

class TipoModeloProducto:
    def __init__(self):
        pass
    
    # ============================================
    # MÉTODOS CRUD
    # ============================================
    
    def listar(self):
        """Listar TODOS los modelos de producto con su tipo padre"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    tm.id_tipo_modelo,
                    tm.id_tipo_prod,
                    tp.nombre as nombre_tipo,
                    tm.nombre,
                    tm.estado
                FROM tipo_modelo_producto tm
                INNER JOIN tipo_producto tp ON tm.id_tipo_prod = tp.id_tipo_prod
                ORDER BY tm.id_tipo_modelo DESC
            """
            
            cursor.execute(sql)
            resultado = cursor.fetchall()
            
            cursor.close()
            con.close()
            
            if resultado:
                modelos = []
                for row in resultado:
                    modelos.append({
                        'id_tipo_modelo': row['id_tipo_modelo'],
                        'id_tipo_prod': row['id_tipo_prod'],
                        'nombre_tipo': row['nombre_tipo'],
                        'nombre': row['nombre'],
                        'estado': row['estado']
                    })
                return True, modelos
            else:
                return True, []
                
        except Exception as e:
            return False, f"Error al listar modelos de producto: {str(e)}"
    
    def obtener_por_id(self, id_tipo_modelo):
        """Obtener un modelo de producto por su ID"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    tm.id_tipo_modelo,
                    tm.id_tipo_prod,
                    tp.nombre as nombre_tipo,
                    tm.nombre,
                    tm.estado
                FROM tipo_modelo_producto tm
                INNER JOIN tipo_producto tp ON tm.id_tipo_prod = tp.id_tipo_prod
                WHERE tm.id_tipo_modelo = %s
            """
            
            cursor.execute(sql, [id_tipo_modelo])
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            if resultado:
                return True, {
                    'id_tipo_modelo': resultado['id_tipo_modelo'],
                    'id_tipo_prod': resultado['id_tipo_prod'],
                    'nombre_tipo': resultado['nombre_tipo'],
                    'nombre': resultado['nombre'],
                    'estado': resultado['estado']
                }
            else:
                return False, 'Modelo de producto no encontrado'
                
        except Exception as e:
            return False, f"Error al obtener modelo de producto: {str(e)}"
    
    def listar_por_tipo(self, id_tipo_prod):
        """Listar modelos de un tipo de producto específico (solo activos)"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    id_tipo_modelo,
                    nombre
                FROM tipo_modelo_producto
                WHERE id_tipo_prod = %s AND estado = TRUE
                ORDER BY nombre
            """
            
            cursor.execute(sql, [id_tipo_prod])
            resultado = cursor.fetchall()
            
            cursor.close()
            con.close()
            
            if resultado:
                modelos = []
                for row in resultado:
                    modelos.append({
                        'id_tipo_modelo': row['id_tipo_modelo'],
                        'nombre': row['nombre']
                    })
                return True, modelos
            else:
                return True, []
                
        except Exception as e:
            return False, f"Error al listar modelos por tipo: {str(e)}"
    
    def crear(self, id_tipo_prod, nombre):
        """Crear un nuevo modelo de producto usando la función de PostgreSQL"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Llamar a la función fn_tipo_modelo_producto_crear
            sql = "SELECT fn_tipo_modelo_producto_crear(%s, %s) as resultado"
            cursor.execute(sql, [id_tipo_prod, nombre])
            
            resultado = cursor.fetchone()
            id_tipo_modelo = resultado['resultado']
            
            con.commit()
            cursor.close()
            con.close()
            
            if id_tipo_modelo and id_tipo_modelo > 0:
                return True, id_tipo_modelo
            else:
                return False, 'No se pudo crear el modelo de producto. Verifique que el tipo de producto exista y esté activo.'
                
        except Exception as e:
            return False, f"Error al crear modelo de producto: {str(e)}"
    
    def modificar(self, id_tipo_modelo, id_tipo_prod, nombre):
        """Modificar un modelo de producto usando la función de PostgreSQL"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Llamar a la función fn_tipo_modelo_producto_modificar
            sql = "SELECT fn_tipo_modelo_producto_modificar(%s, %s, %s) as resultado"
            cursor.execute(sql, [id_tipo_modelo, id_tipo_prod, nombre])
            
            resultado = cursor.fetchone()
            codigo = resultado['resultado']
            
            con.commit()
            cursor.close()
            con.close()
            
            if codigo == 0:
                return True, 'Modelo de producto modificado correctamente'
            else:
                return False, 'No se pudo modificar el modelo de producto. Verifique que el tipo de producto exista y esté activo.'
                
        except Exception as e:
            return False, f"Error al modificar modelo de producto: {str(e)}"
    
    def cambiar_estado(self, id_tipo_modelo):
        """Cambiar el estado de un modelo de producto (activar/desactivar)"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Obtener estado actual
            sql_get = "SELECT estado FROM tipo_modelo_producto WHERE id_tipo_modelo = %s"
            cursor.execute(sql_get, [id_tipo_modelo])
            resultado = cursor.fetchone()
            
            if not resultado:
                cursor.close()
                con.close()
                return False, 'Modelo de producto no encontrado'
            
            # Cambiar al estado contrario
            nuevo_estado = not resultado['estado']
            sql_update = "UPDATE tipo_modelo_producto SET estado = %s WHERE id_tipo_modelo = %s"
            cursor.execute(sql_update, [nuevo_estado, id_tipo_modelo])
            
            con.commit()
            cursor.close()
            con.close()
            
            return True, 'Estado cambiado correctamente'
                
        except Exception as e:
            return False, f"Error al cambiar estado: {str(e)}"
    
    def eliminar_fisico(self, id_tipo_modelo):
        """Eliminar FÍSICAMENTE un modelo de producto (DELETE permanente)"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Verificar que existe
            sql_check_exists = "SELECT COUNT(*) as total FROM tipo_modelo_producto WHERE id_tipo_modelo = %s"
            cursor.execute(sql_check_exists, [id_tipo_modelo])
            existe = cursor.fetchone()
            
            if existe['total'] == 0:
                cursor.close()
                con.close()
                return False, 'Modelo de producto no encontrado'
            
            # Verificar que no tenga productos asociados
            sql_check_productos = """
                SELECT COUNT(*) as total
                FROM producto_sucursal
                WHERE id_tipo_modelo = %s
            """
            cursor.execute(sql_check_productos, [id_tipo_modelo])
            resultado = cursor.fetchone()
            
            if resultado['total'] > 0:
                cursor.close()
                con.close()
                return False, f'No se puede eliminar porque tiene {resultado["total"]} producto(s) asociado(s)'
            
            # Eliminar físicamente (DELETE)
            sql_delete = "DELETE FROM tipo_modelo_producto WHERE id_tipo_modelo = %s"
            cursor.execute(sql_delete, [id_tipo_modelo])
            
            con.commit()
            cursor.close()
            con.close()
            
            return True, 'Modelo de producto eliminado permanentemente de la base de datos'
                
        except Exception as e:
            return False, f"Error al eliminar modelo de producto: {str(e)}"
    
    def contar_productos(self, id_tipo_modelo):
        """Contar TODOS los productos asociados a un modelo"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT COUNT(*) as total
                FROM producto_sucursal
                WHERE id_tipo_modelo = %s
            """
            
            cursor.execute(sql, [id_tipo_modelo])
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            return resultado['total'] if resultado else 0
                
        except Exception as e:
            return 0
    
    def listar_tipos_activos(self):
        """Listar tipos de producto activos para select"""
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
            resultado = cursor.fetchall()
            
            cursor.close()
            con.close()
            
            if resultado:
                tipos = []
                for row in resultado:
                    tipos.append({
                        'id_tipo_prod': row['id_tipo_prod'],
                        'nombre': row['nombre']
                    })
                return True, tipos
            else:
                return True, []
                
        except Exception as e:
            return False, f"Error al listar tipos de producto: {str(e)}"