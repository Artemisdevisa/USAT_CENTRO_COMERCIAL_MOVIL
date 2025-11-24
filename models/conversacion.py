from conexionBD import Conexion
import json

class Conversacion:
    
    @staticmethod
    def buscar_o_crear(id_usuario, id_sucursal):
        """
        Busca o crea conversación entre usuario y sucursal
        """
        con = None
        cursor = None
        
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            print(f"🔍 Buscando/creando conversación | Usuario: {id_usuario} | Sucursal: {id_sucursal}")
            
            # Llamar a la función PostgreSQL
            cursor.execute(
                "SELECT fn_iniciar_conversacion(%s, %s)", 
                (id_usuario, id_sucursal)
            )
            
            resultado = cursor.fetchone()
            
            # ✅ CORRECCIÓN: Verificar correctamente el resultado
            if resultado is None or resultado[0] is None:
                con.rollback()
                print("❌ La función no devolvió datos")
                return {
                    'success': False,
                    'message': 'No se pudo iniciar la conversación'
                }
            
            # Obtener el JSONB (puede ser dict o str)
            conversacion_data = resultado[0]
            
            # Si es string, convertir a dict
            if isinstance(conversacion_data, str):
                conversacion_data = json.loads(conversacion_data)
            
            con.commit()
            
            print(f"✅ Conversación obtenida: {conversacion_data.get('id_conversacion')}")
            
            return {
                'success': True,
                'data': conversacion_data
            }
                
        except Exception as e:
            print(f"❌ Error en buscar_o_crear: {type(e).__name__}: {str(e)}")
            
            if con:
                con.rollback()
            
            return {
                'success': False,
                'message': f"{type(e).__name__}: {str(e)}"
            }
        
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    
    @staticmethod
    def listar_por_usuario(id_usuario):
        """
        Lista todas las conversaciones activas de un usuario
        """
        con = None
        cursor = None
        
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
                    c.created_at,
                    s.nombre as sucursal_nombre,
                    s.img_logo as sucursal_logo
                FROM conversacion c
                INNER JOIN sucursal s ON c.id_sucursal = s.id_sucursal
                WHERE c.id_usuario = %s 
                  AND c.estado = TRUE
                ORDER BY c.fecha_ultimo_mensaje DESC NULLS LAST
            """, (id_usuario,))
            
            conversaciones = []
            for row in cursor.fetchall():
                conversaciones.append({
                    'id_conversacion': row['id_conversacion'],
                    'id_usuario': row['id_usuario'],
                    'id_sucursal': row['id_sucursal'],
                    'ultimo_mensaje': row['ultimo_mensaje'],
                    'fecha_ultimo_mensaje': row['fecha_ultimo_mensaje'].isoformat() if row['fecha_ultimo_mensaje'] else None,
                    'mensajes_no_leidos': row['mensajes_no_leidos_usuario'],
                    'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                    'sucursal': {
                        'nombre': row['sucursal_nombre'],
                        'logo': row['sucursal_logo']
                    }
                })
            
            return {
                'success': True,
                'data': conversaciones
            }
            
        except Exception as e:
            print(f"❌ Error en listar_por_usuario: {e}")
            return {
                'success': False,
                'message': str(e)
            }
        
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    
    @staticmethod
    def obtener_por_id(id_conversacion):
        """
        Obtiene detalles de una conversación específica
        """
        con = None
        cursor = None
        
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
                    c.created_at,
                    u.nomusuario,
                    u.img_logo as usuario_img,
                    s.nombre as sucursal_nombre,
                    s.img_logo as sucursal_logo
                FROM conversacion c
                INNER JOIN usuario u ON c.id_usuario = u.id_usuario
                INNER JOIN sucursal s ON c.id_sucursal = s.id_sucursal
                WHERE c.id_conversacion = %s
            """, (id_conversacion,))
            
            row = cursor.fetchone()
            
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
                    'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                    'usuario': {
                        'nombre': row['nomusuario'],
                        'img': row['usuario_img']
                    },
                    'sucursal': {
                        'nombre': row['sucursal_nombre'],
                        'logo': row['sucursal_logo']
                    }
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Error en obtener_por_id: {e}")
            return None
        
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    
    @staticmethod
    def archivar(id_conversacion, id_usuario):
        """
        Archiva una conversación (cambia estado a FALSE)
        """
        con = None
        cursor = None
        
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            cursor.execute("""
                UPDATE conversacion
                SET estado = FALSE
                WHERE id_conversacion = %s 
                  AND id_usuario = %s
                RETURNING id_conversacion
            """, (id_conversacion, id_usuario))
            
            resultado = cursor.fetchone()
            
            if resultado:
                con.commit()
                return {
                    'success': True,
                    'message': 'Conversación archivada correctamente'
                }
            else:
                con.rollback()
                return {
                    'success': False,
                    'message': 'No se pudo archivar la conversación'
                }
                
        except Exception as e:
            print(f"❌ Error en archivar: {e}")
            if con:
                con.rollback()
            
            return {
                'success': False,
                'message': str(e)
            }
        
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()