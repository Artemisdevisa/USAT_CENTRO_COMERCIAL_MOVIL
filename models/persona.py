from conexionBD import Conexion

class Persona:
    def __init__(self):
        pass
    
    def crear(self, nombres, apellidos, tipo_doc, documento, fecha_nacimiento, telefono, id_dist, direccion):
        """Crear persona usando función PostgreSQL"""
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