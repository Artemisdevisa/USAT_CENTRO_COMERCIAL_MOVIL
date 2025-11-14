from conexionBD import Conexion

class Rol:
    def __init__(self):
        pass
    
    def listar(self):
        """Listar todos los roles activos"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    id_rol,
                    nombre,
                    estado
                FROM rol
                WHERE estado = TRUE
                ORDER BY nombre
            """
            
            cursor.execute(sql)
            resultado = cursor.fetchall()
            
            cursor.close()
            con.close()
            
            if resultado:
                roles = []
                for row in resultado:
                    roles.append({
                        'id_rol': row['id_rol'],
                        'nombre': row['nombre'],
                        'estado': row['estado']
                    })
                return True, roles
            else:
                return True, []
                
        except Exception as e:
            return False, f"Error al listar roles: {str(e)}"
    
    def obtener_por_id(self, id_rol):
        """Obtener un rol por su ID"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    id_rol,
                    nombre,
                    estado
                FROM rol
                WHERE id_rol = %s
            """
            
            cursor.execute(sql, [id_rol])
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            if resultado:
                return True, {
                    'id_rol': resultado['id_rol'],
                    'nombre': resultado['nombre'],
                    'estado': resultado['estado']
                }
            else:
                return False, 'Rol no encontrado'
                
        except Exception as e:
            return False, f"Error al obtener rol: {str(e)}"
    
    def crear(self, nombre):
        """Crear un nuevo rol usando la función de PostgreSQL"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Llamar a la función fn_rol_crear
            sql = "SELECT fn_rol_crear(%s) as resultado"
            cursor.execute(sql, [nombre])
            
            resultado = cursor.fetchone()
            id_rol = resultado['resultado']
            
            con.commit()
            cursor.close()
            con.close()
            
            if id_rol and id_rol > 0:
                return True, id_rol
            else:
                return False, 'No se pudo crear el rol. Puede que ya exista un rol con ese nombre.'
                
        except Exception as e:
            return False, f"Error al crear rol: {str(e)}"
    
    def modificar(self, id_rol, nombre):
        """Modificar un rol usando la función de PostgreSQL"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Llamar a la función fn_rol_modificar
            sql = "SELECT fn_rol_modificar(%s, %s) as resultado"
            cursor.execute(sql, [id_rol, nombre])
            
            resultado = cursor.fetchone()
            codigo = resultado['resultado']
            
            con.commit()
            cursor.close()
            con.close()
            
            if codigo == 0:
                return True, 'Rol modificado correctamente'
            else:
                return False, 'No se pudo modificar el rol. Puede que ya exista un rol con ese nombre.'
                
        except Exception as e:
            return False, f"Error al modificar rol: {str(e)}"
    
    def eliminar(self, id_rol):
        """Eliminar lógicamente un rol usando la función de PostgreSQL"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Llamar a la función fn_rol_eliminar
            sql = "SELECT fn_rol_eliminar(%s) as resultado"
            cursor.execute(sql, [id_rol])
            
            resultado = cursor.fetchone()
            codigo = resultado['resultado']
            
            con.commit()
            cursor.close()
            con.close()
            
            if codigo == 0:
                return True, 'Rol eliminado correctamente'
            else:
                return False, 'No se puede eliminar el rol. Puede que tenga usuarios asociados.'
                
        except Exception as e:
            return False, f"Error al eliminar rol: {str(e)}"
    
    def contar_usuarios(self, id_rol):
        """Contar usuarios asociados a un rol"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT COUNT(*) as total
                FROM usuario
                WHERE id_rol = %s AND estado = TRUE
            """
            
            cursor.execute(sql, [id_rol])
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            return resultado['total'] if resultado else 0
                
        except Exception as e:
            return 0