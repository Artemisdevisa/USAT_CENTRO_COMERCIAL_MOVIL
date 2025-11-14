from conexionBD import Conexion

class HorarioSucursal:
    """Modelo para gestión de horarios de sucursales"""
    
    @staticmethod
    def crear(id_sucursal, dia, hora_inicio, hora_fin):
        """Crear un nuevo horario para una sucursal"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Llamar a la función de PostgreSQL
            cursor.execute("""
                SELECT fn_horario_sucursal_crear(%s, %s, %s, %s) as resultado
            """, [int(id_sucursal), int(dia), hora_inicio, hora_fin])
            
            resultado = cursor.fetchone()
            id_horario = resultado['resultado'] if resultado else -1
            
            con.commit()
            cursor.close()
            con.close()
            
            return id_horario
        except Exception as e:
            print(f"❌ Error en crear horario: {str(e)}")
            import traceback
            traceback.print_exc()
            return -1
    
    @staticmethod
    def modificar(id_horario, id_sucursal, dia, hora_inicio, hora_fin):
        """Modificar un horario existente"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            cursor.execute("""
                SELECT fn_horario_sucursal_modificar(%s, %s, %s, %s, %s) as resultado
            """, [int(id_horario), int(id_sucursal), int(dia), hora_inicio, hora_fin])
            
            resultado = cursor.fetchone()
            codigo = resultado['resultado'] if resultado else -1
            
            con.commit()
            cursor.close()
            con.close()
            
            return codigo
        except Exception as e:
            print(f"❌ Error en modificar horario: {str(e)}")
            import traceback
            traceback.print_exc()
            return -1
    
    @staticmethod
    def eliminar(id_horario):
        """Eliminar (lógico) un horario"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            cursor.execute("""
                SELECT fn_horario_sucursal_eliminar(%s) as resultado
            """, [int(id_horario)])
            
            resultado = cursor.fetchone()
            codigo = resultado['resultado'] if resultado else -1
            
            con.commit()
            cursor.close()
            con.close()
            
            return codigo
        except Exception as e:
            print(f"❌ Error en eliminar horario: {str(e)}")
            import traceback
            traceback.print_exc()
            return -1
    
    @staticmethod
    def listar_por_sucursal(id_sucursal):
        """Listar todos los horarios de una sucursal"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            cursor.execute("""
                SELECT 
                    h.id_horario,
                    h.id_sucursal,
                    h.dia,
                    h.hora_inicio::text as hora_inicio,
                    h.hora_fin::text as hora_fin,
                    h.estado,
                    s.nombre as sucursal
                FROM horario_sucursal h
                INNER JOIN sucursal s ON h.id_sucursal = s.id_sucursal
                WHERE h.id_sucursal = %s AND h.estado = TRUE
                ORDER BY h.dia
            """, [int(id_sucursal)])
            
            horarios = cursor.fetchall()
            cursor.close()
            con.close()
            
            return horarios if horarios else []
        except Exception as e:
            print(f"❌ Error en listar horarios: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def obtener(id_horario):
        """Obtener un horario específico"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            cursor.execute("""
                SELECT 
                    h.id_horario,
                    h.id_sucursal,
                    h.dia,
                    h.hora_inicio::text as hora_inicio,
                    h.hora_fin::text as hora_fin,
                    h.estado,
                    s.nombre as sucursal
                FROM horario_sucursal h
                INNER JOIN sucursal s ON h.id_sucursal = s.id_sucursal
                WHERE h.id_horario = %s
            """, [int(id_horario)])
            
            horario = cursor.fetchone()
            cursor.close()
            con.close()
            
            return horario
        except Exception as e:
            print(f"❌ Error en obtener horario: {str(e)}")
            import traceback
            traceback.print_exc()
            return None