from config import get_db_connection
from datetime import datetime

class Conversacion:
    def __init__(self):
        pass
    
    @staticmethod
    def buscar_o_crear(id_usuario, id_sucursal):
        """Busca una conversación existente o la crea"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Llamar función PostgreSQL
            cursor.execute("""
                SELECT fn_iniciar_conversacion(%s, %s)
            """, (id_usuario, id_sucursal))
            
            resultado = cursor.fetchone()[0]
            conn.commit()
            
            return resultado
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error al iniciar conversación: {e}")
            return {
                'success': False,
                'message': str(e)
            }
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def listar_por_usuario(id_usuario):
        """Lista todas las conversaciones de un usuario"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT fn_listar_conversaciones_usuario(%s)
            """, (id_usuario,))
            
            resultado = cursor.fetchone()[0]
            return resultado
            
        except Exception as e:
            print(f"❌ Error al listar conversaciones: {e}")
            return {
                'success': False,
                'message': str(e)
            }
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def obtener_por_id(id_conversacion):
        """Obtiene una conversación específica"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    c.id_conversacion,
                    c.id_usuario,
                    c.id_sucursal,
                    c.ultimo_mensaje,
                    c.fecha_ultimo_mensaje,
                    c.mensajes_no_leidos_usuario,
                    c.mensajes_no_leidos_sucursal,
                    c.estado,
                    s.nombre as nombre_sucursal,
                    s.img_logo as logo_sucursal
                FROM conversacion c
                INNER JOIN sucursal s ON c.id_sucursal = s.id_sucursal
                WHERE c.id_conversacion = %s
            """, (id_conversacion,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id_conversacion': row[0],
                    'id_usuario': row[1],
                    'id_sucursal': row[2],
                    'ultimo_mensaje': row[3],
                    'fecha_ultimo_mensaje': row[4].isoformat() if row[4] else None,
                    'mensajes_no_leidos_usuario': row[5],
                    'mensajes_no_leidos_sucursal': row[6],
                    'estado': row[7],
                    'nombre_sucursal': row[8],
                    'logo_sucursal': row[9]
                }
            return None
            
        except Exception as e:
            print(f"❌ Error al obtener conversación: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def archivar(id_conversacion, id_usuario):
        """Archiva una conversación"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT fn_archivar_conversacion(%s, %s)
            """, (id_conversacion, id_usuario))
            
            resultado = cursor.fetchone()[0]
            conn.commit()
            
            return resultado
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error al archivar conversación: {e}")
            return {
                'success': False,
                'message': str(e)
            }
        finally:
            cursor.close()
            conn.close()