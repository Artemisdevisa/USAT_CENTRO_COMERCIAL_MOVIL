from conexionBD import Conexion

class Persona:
    def __init__(self):
        pass
    
    def crear(self, nombres, apellidos, tipo_doc, documento, fecha_nacimiento, telefono, id_dist, direccion):
        """Crear persona"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                INSERT INTO persona (nombres, apellidos, tipo_doc, documento, fecha_nacimiento, telefono, id_dist, direccion, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                RETURNING id_persona
            """
            
            cursor.execute(sql, [nombres, apellidos, tipo_doc, documento, fecha_nacimiento, telefono, id_dist, direccion])
            resultado = cursor.fetchone()
            
            con.commit()
            cursor.close()
            con.close()
            
            return True, resultado['id_persona']
                
        except Exception as e:
            return False, f"Error al crear persona: {str(e)}"
    
    def actualizar(self, id_persona, nombres, apellidos, telefono, direccion, fecha_nacimiento):
        """Actualizar datos de persona"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                UPDATE persona 
                SET nombres = %s, 
                    apellidos = %s, 
                    telefono = COALESCE(%s, telefono),
                    direccion = COALESCE(%s, direccion),
                    fecha_nacimiento = COALESCE(%s::DATE, fecha_nacimiento)
                WHERE id_persona = %s AND estado = TRUE
            """
            
            cursor.execute(sql, [nombres, apellidos, telefono, direccion, fecha_nacimiento, id_persona])
            
            con.commit()
            cursor.close()
            con.close()
            
            return True, 'Persona actualizada correctamente'
                
        except Exception as e:
            return False, f"Error al actualizar persona: {str(e)}"
    
    def obtener_por_id(self, id_persona):
        """Obtener datos de persona"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    p.id_persona,
                    p.nombres,
                    p.apellidos,
                    p.tipo_doc,
                    p.documento,
                    p.fecha_nacimiento,
                    p.telefono,
                    p.id_dist,
                    p.direccion,
                    d.nombre as distrito,
                    pr.nombre as provincia,
                    dep.nombre as departamento
                FROM persona p
                LEFT JOIN distrito d ON p.id_dist = d.id_dist
                LEFT JOIN provincia pr ON d.id_prov = pr.id_prov
                LEFT JOIN departamento dep ON pr.id_dep = dep.id_dep
                WHERE p.id_persona = %s AND p.estado = TRUE
            """
            
            cursor.execute(sql, [id_persona])
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            if resultado:
                return True, resultado
            else:
                return False, 'Persona no encontrada'
                
        except Exception as e:
            return False, f"Error: {str(e)}"