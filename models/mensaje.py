from config import get_db_connection
from datetime import datetime

class Mensaje:
    def __init__(self):
        pass
    
    @staticmethod
    def enviar(id_conversacion, id_emisor, tipo_emisor, contenido, tipo_mensaje='TEXTO', url_archivo=None):
        """Envía un mensaje"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT fn_enviar_mensaje(%s, %s, %s, %s, %s, %s)
            """, (id_conversacion, id_emisor, tipo_emisor, contenido, tipo_mensaje, url_archivo))
            
            resultado = cursor.fetchone()[0]
            conn.commit()
            
            return resultado
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error al enviar mensaje: {e}")
            return {
                'success': False,
                'message': str(e)
            }
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def listar_por_conversacion(id_conversacion, id_usuario):
        """Lista mensajes de una conversación"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT fn_listar_mensajes(%s, %s)
            """, (id_conversacion, id_usuario))
            
            resultado = cursor.fetchone()[0]
            return resultado
            
        except Exception as e:
            print(f"❌ Error al listar mensajes: {e}")
            return {
                'success': False,
                'message': str(e)
            }
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def marcar_leidos(id_conversacion, tipo_lector):
        """Marca mensajes como leídos"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT fn_marcar_mensajes_leidos(%s, %s)
            """, (id_conversacion, tipo_lector))
            
            resultado = cursor.fetchone()[0]
            conn.commit()
            
            return resultado
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error al marcar mensajes: {e}")
            return {
                'success': False,
                'message': str(e)
            }
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def contar_no_leidos(id_usuario):
        """Cuenta mensajes no leídos de un usuario"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT fn_contar_mensajes_no_leidos_usuario(%s)
            """, (id_usuario,))
            
            count = cursor.fetchone()[0]
            return count
            
        except Exception as e:
            print(f"❌ Error al contar mensajes: {e}")
            return 0
        finally:
            cursor.close()
            conn.close()