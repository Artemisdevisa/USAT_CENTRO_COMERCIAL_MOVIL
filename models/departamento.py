from conexionBD import Conexion

class Departamento:
    def __init__(self):
        pass
    
    def listar(self):
        """Listar departamentos activos"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = "SELECT * FROM fn_departamento_listar_departamentos()"
            cursor.execute(sql)
            resultados = cursor.fetchall()
            
            cursor.close()
            con.close()
            
            if not resultados:
                return True, []
            
            # ✅ CAMBIO: Usar nombres de columnas en lugar de índices
            departamentos = []
            for row in resultados:
                departamentos.append({
                    'id_dep': row['id_dep'],  # ✅ Usar nombre, no índice
                    'nombre': row['nombre']    # ✅ Usar nombre, no índice
                })
            
            return True, departamentos
                
        except Exception as e:
            print(f"❌ Error en listar: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, []
    
    def crear(self, nombre):
        """Crear departamento"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = "SELECT fn_departamento_crear(%s)"
            cursor.execute(sql, [nombre])
            resultado = cursor.fetchone()
            
            con.commit()
            cursor.close()
            con.close()
            
            if resultado and resultado[0] > 0:
                return True, resultado[0]
            else:
                return False, 'No se pudo crear el departamento'
                
        except Exception as e:
            print(f"Error en crear: {str(e)}")
            return False, f"Error al crear: {str(e)}"
    
    def modificar(self, id_dep, nombre):
        """Modificar departamento"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = "SELECT fn_departamento_modificar(%s, %s)"
            cursor.execute(sql, [id_dep, nombre])
            resultado = cursor.fetchone()
            
            con.commit()
            cursor.close()
            con.close()
            
            if resultado and resultado[0] == 0:
                return True, 'Departamento actualizado correctamente'
            else:
                return False, 'No se pudo actualizar'
                
        except Exception as e:
            print(f"Error en modificar: {str(e)}")
            return False, f"Error al modificar: {str(e)}"
    
    def eliminar(self, id_dep):
        """Eliminar departamento (lógico)"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = "SELECT fn_departamento_eliminar(%s)"
            cursor.execute(sql, [id_dep])
            resultado = cursor.fetchone()
            
            con.commit()
            cursor.close()
            con.close()
            
            if resultado and resultado[0] == 0:
                return True, 'Departamento eliminado correctamente'
            else:
                return False, 'No se pudo eliminar'
                
        except Exception as e:
            print(f"Error en eliminar: {str(e)}")
            return False, f"Error al eliminar: {str(e)}"