from conexionBD import Conexion

class Conversacion:
    def __init__(self):
        pass
    
    @staticmethod
    def buscar_o_crear(id_usuario, id_sucursal):
        """Busca una conversación existente o la crea"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Llamar función PostgreSQL
            cursor.execute("""
                SELECT fn_iniciar_conversacion(%s, %s)
            """, (id_usuario, id_sucursal))
            
            resultado = cursor.fetchone()[0]
            con.commit()
            
            cursor.close()
            con.close()
            
            return resultado
            
        except Exception as e:
            print(f"❌ Error al iniciar conversación: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    @staticmethod
    def listar_por_usuario(id_usuario):
        """Lista todas las conversaciones de un usuario"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            cursor.execute("""
                SELECT fn_listar_conversaciones_usuario(%s)
            """, (id_usuario,))
            
            resultado = cursor.fetchone()[0]
            
            cursor.close()
            con.close()
            
            return resultado
            
        except Exception as e:
            print(f"❌ Error al listar conversaciones: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    @staticmethod
    def obtener_por_id(id_conversacion):
        """Obtiene una conversación específica"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
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
            
            cursor.close()
            con.close()
            
            if row:
                return {
                    'id_conversacion': row['id_conversacion'],
                    'id_usuario': row['id_usuario'],
                    'id_sucursal': row['id_sucursal'],
                    'ultimo_mensaje': row['ultimo_mensaje'],
                    'fecha_ultimo_mensaje': row['fecha_ultimo_mensaje'].isoformat() if row['fecha_ultimo_mensaje'] else None,
                    'mensajes_no_leidos_usuario': row['mensajes_no_leidos_usuario'],
                    'mensajes_no_leidos_sucursal': row['mensajes_no_leidos_sucursal'],
                    'estado': row['estado'],
                    'nombre_sucursal': row['nombre_sucursal'],
                    'logo_sucursal': row['logo_sucursal']
                }
            return None
            
        except Exception as e:
            print(f"❌ Error al obtener conversación: {e}")
            return None
    
    @staticmethod
    def archivar(id_conversacion, id_usuario):
        """Archiva una conversación"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            cursor.execute("""
                SELECT fn_archivar_conversacion(%s, %s)
            """, (id_conversacion, id_usuario))
            
            resultado = cursor.fetchone()[0]
            con.commit()
            
            cursor.close()
            con.close()
            
            return resultado
            
        except Exception as e:
            print(f"❌ Error al archivar conversación: {e}")
            return {
                'success': False,
                'message': str(e)
            }