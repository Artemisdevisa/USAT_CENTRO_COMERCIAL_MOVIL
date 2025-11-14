from conexionBD import Conexion

class Provincia:
    def __init__(self):
        pass
    
    def listar_por_departamento(self, id_dep):
        """Listar provincias por departamento"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = "SELECT * FROM fn_provincia_listar_provincia_por_departamento(%s)"
            cursor.execute(sql, [id_dep])
            resultados = cursor.fetchall()
            
            cursor.close()
            con.close()
            
            if not resultados:
                return True, []
            
            # ✅ Usar nombres de columnas
            provincias = []
            for row in resultados:
                provincias.append({
                    'id_prov': row['id_prov'],
                    'nombre': row['nombre']
                })
            
            return True, provincias
                
        except Exception as e:
            print(f"Error en listar_por_departamento: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, []
    
    def crear(self, id_dep, nombre):
        """Crear provincia"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = "SELECT fn_provincia_crear(%s, %s)"
            cursor.execute(sql, [id_dep, nombre])
            resultado = cursor.fetchone()
            
            con.commit()
            cursor.close()
            con.close()
            
            if resultado and resultado[0] > 0:
                return True, resultado[0]
            else:
                return False, 'No se pudo crear la provincia'
                
        except Exception as e:
            print(f"Error en crear: {str(e)}")
            return False, f"Error al crear: {str(e)}"
    
    def modificar(self, id_prov, id_dep, nombre):
        """Modificar provincia"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = "SELECT fn_provincia_modificar(%s, %s, %s)"
            cursor.execute(sql, [id_prov, id_dep, nombre])
            resultado = cursor.fetchone()
            
            con.commit()
            cursor.close()
            con.close()
            
            if resultado and resultado[0] == 0:
                return True, 'Provincia actualizada correctamente'
            else:
                return False, 'No se pudo actualizar'
                
        except Exception as e:
            print(f"Error en modificar: {str(e)}")
            return False, f"Error al modificar: {str(e)}"
    
    def eliminar(self, id_prov):
        """Eliminar provincia (lógico)"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = "SELECT fn_provincia_eliminar(%s)"
            cursor.execute(sql, [id_prov])
            resultado = cursor.fetchone()
            
            con.commit()
            cursor.close()
            con.close()
            
            if resultado and resultado[0] == 0:
                return True, 'Provincia eliminada correctamente'
            else:
                return False, 'No se pudo eliminar (tiene distritos asociados)'
                
        except Exception as e:
            print(f"Error en eliminar: {str(e)}")
            return False, f"Error al eliminar: {str(e)}"