from conexionBD import Conexion

class Distrito:
    def __init__(self):
        pass
    
    def listar_por_provincia(self, id_prov):
        """Listar distritos por provincia"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = "SELECT * FROM fn_distrito_listar_distritos_por_provincia(%s)"
            cursor.execute(sql, [id_prov])
            resultados = cursor.fetchall()
            
            cursor.close()
            con.close()
            
            if not resultados:
                return True, []
            
            # ✅ Usar nombres de columnas
            distritos = []
            for row in resultados:
                distritos.append({
                    'id_dist': row['id_dist'],
                    'nombre': row['nombre']
                })
            
            return True, distritos
                
        except Exception as e:
            print(f"Error en listar_por_provincia: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, []
    
    def crear(self, id_prov, nombre):
        """Crear distrito"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = "SELECT fn_distrito_crear(%s, %s)"
            cursor.execute(sql, [id_prov, nombre])
            resultado = cursor.fetchone()
            
            con.commit()
            cursor.close()
            con.close()
            
            if resultado and resultado[0] > 0:
                return True, resultado[0]
            else:
                return False, 'No se pudo crear el distrito'
                
        except Exception as e:
            print(f"Error en crear: {str(e)}")
            return False, f"Error al crear: {str(e)}"
    
    def modificar(self, id_dist, id_prov, nombre):
        """Modificar distrito"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = "SELECT fn_distrito_modificar(%s, %s, %s)"
            cursor.execute(sql, [id_dist, id_prov, nombre])
            resultado = cursor.fetchone()
            
            con.commit()
            cursor.close()
            con.close()
            
            if resultado and resultado[0] == 0:
                return True, 'Distrito actualizado correctamente'
            else:
                return False, 'No se pudo actualizar'
                
        except Exception as e:
            print(f"Error en modificar: {str(e)}")
            return False, f"Error al modificar: {str(e)}"
    
    def eliminar(self, id_dist):
        """Eliminar distrito (lógico)"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = "SELECT fn_distrito_eliminar(%s)"
            cursor.execute(sql, [id_dist])
            resultado = cursor.fetchone()
            
            con.commit()
            cursor.close()
            con.close()
            
            if resultado and resultado[0] == 0:
                return True, 'Distrito eliminado correctamente'
            else:
                return False, 'No se pudo eliminar (tiene registros asociados)'
                
        except Exception as e:
            print(f"Error en eliminar: {str(e)}")
            return False, f"Error al eliminar: {str(e)}"