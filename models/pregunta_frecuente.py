from conexionBD import Conexion

class PreguntaFrecuente:
    def __init__(self):
        pass
    
    def listar_preguntas_frecuentes(self):
        """Lista todas las preguntas frecuentes (activas e inactivas para el dashboard)"""
        try:
            con = Conexion()
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    id_pregunta_frecuente,
                    nombre,
                    descripcion,
                    respuesta,
                    estado,
                    fecha_creacion,
                    fecha_actualizacion
                FROM preguntas_frecuentes
                ORDER BY fecha_creacion DESC
            """
            
            cursor.execute(sql)
            resultados = cursor.fetchall()
            
            preguntas = []
            for row in resultados:
                pregunta = {
                    "id_pregunta_frecuente": row['id_pregunta_frecuente'],
                    "nombre": row['nombre'],
                    "descripcion": row['descripcion'],
                    "respuesta": row['respuesta'],
                    "estado": row['estado'] == '1',
                    "fecha_creacion": str(row['fecha_creacion']),
                    "fecha_actualizacion": str(row['fecha_actualizacion']) if row['fecha_actualizacion'] else None
                }
                preguntas.append(pregunta)
            
            con.close()
            return True, preguntas
                
        except Exception as e:
            return False, f"Error al listar preguntas: {str(e)}"
    
    def obtener_pregunta(self, id_pregunta):
        """Obtiene una pregunta frecuente por ID"""
        try:
            con = Conexion()
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    id_pregunta_frecuente,
                    nombre,
                    descripcion,
                    respuesta,
                    estado,
                    fecha_creacion,
                    fecha_actualizacion
                FROM preguntas_frecuentes
                WHERE id_pregunta_frecuente = %s
            """
            
            cursor.execute(sql, (id_pregunta,))
            row = cursor.fetchone()
            
            if not row:
                con.close()
                return False, "Pregunta no encontrada"
            
            pregunta = {
                "id_pregunta_frecuente": row['id_pregunta_frecuente'],
                "nombre": row['nombre'],
                "descripcion": row['descripcion'],
                "respuesta": row['respuesta'],
                "estado": row['estado'] == '1',
                "fecha_creacion": str(row['fecha_creacion']),
                "fecha_actualizacion": str(row['fecha_actualizacion']) if row['fecha_actualizacion'] else None
            }
            
            con.close()
            return True, pregunta
                
        except Exception as e:
            return False, f"Error al obtener pregunta: {str(e)}"
    
    def crear_pregunta(self, nombre, descripcion, respuesta, id_usuario=1):
        """Crea una nueva pregunta frecuente"""
        try:
            con = Conexion()
            cursor = con.cursor()
            
            sql = """
                INSERT INTO preguntas_frecuentes 
                (id_usuario, nombre, descripcion, respuesta, estado, fecha_creacion)
                VALUES (%s, %s, %s, %s, '1', NOW())
            """
            
            cursor.execute(sql, (id_usuario, nombre, descripcion, respuesta))
            con.commit()
            con.close()
            
            return True, "Pregunta frecuente creada correctamente"
                
        except Exception as e:
            return False, f"Error al crear pregunta: {str(e)}"
    
    def modificar_pregunta(self, id_pregunta, nombre, descripcion, respuesta):
        """Modifica una pregunta frecuente existente"""
        try:
            con = Conexion()
            cursor = con.cursor()
            
            sql = """
                UPDATE preguntas_frecuentes 
                SET nombre = %s, 
                    descripcion = %s, 
                    respuesta = %s,
                    fecha_actualizacion = NOW()
                WHERE id_pregunta_frecuente = %s
            """
            
            cursor.execute(sql, (nombre, descripcion, respuesta, id_pregunta))
            
            if cursor.rowcount == 0:
                con.close()
                return False, "Pregunta no encontrada"
            
            con.commit()
            con.close()
            
            return True, "Pregunta frecuente modificada correctamente"
                
        except Exception as e:
            return False, f"Error al modificar pregunta: {str(e)}"
    
    def cambiar_estado(self, id_pregunta):
        """Cambia el estado de una pregunta frecuente (activa/inactiva)"""
        try:
            con = Conexion()
            cursor = con.cursor()
            
            cursor.execute("SELECT estado FROM preguntas_frecuentes WHERE id_pregunta_frecuente = %s", (id_pregunta,))
            row = cursor.fetchone()
            
            if not row:
                con.close()
                return False, "Pregunta no encontrada"
            
            nuevo_estado = '0' if row['estado'] == '1' else '1'
            
            sql = """
                UPDATE preguntas_frecuentes 
                SET estado = %s, fecha_actualizacion = NOW()
                WHERE id_pregunta_frecuente = %s
            """
            
            cursor.execute(sql, (nuevo_estado, id_pregunta))
            con.commit()
            con.close()
            
            return True, "Estado cambiado correctamente"
                
        except Exception as e:
            return False, f"Error al cambiar estado: {str(e)}"
    
    def eliminar_pregunta(self, id_pregunta):
        """Elimina permanentemente una pregunta frecuente"""
        try:
            con = Conexion()
            cursor = con.cursor()
            
            sql = "DELETE FROM preguntas_frecuentes WHERE id_pregunta_frecuente = %s"
            cursor.execute(sql, (id_pregunta,))
            
            if cursor.rowcount == 0:
                con.close()
                return False, "Pregunta no encontrada"
            
            con.commit()
            con.close()
            
            return True, "Pregunta eliminada permanentemente"
                
        except Exception as e:
            return False, f"Error al eliminar pregunta: {str(e)}"