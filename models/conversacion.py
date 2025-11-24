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
            
            print(f"🔍 Ejecutando fn_iniciar_conversacion({id_usuario}, {id_sucursal})")
            
            # ✅ SOLUCIÓN: Llamar función y obtener resultado como tupla
            cursor.execute(
                "SELECT fn_iniciar_conversacion(%s, %s)", 
                (id_usuario, id_sucursal)
            )
            
            row = cursor.fetchone()
            
            if row is None or row[0] is None:
                print("❌ fetchone() devolvió None o sin datos")
                if con:
                    con.rollback()
                return {
                    'success': False,
                    'message': 'No se obtuvo respuesta de la base de datos'
                }
            
            # ✅ Obtener el JSONB de la tupla (índice 0)
            resultado_jsonb = row[0]
            
            print(f"📦 Resultado type: {type(resultado_jsonb)}")
            print(f"📦 Resultado value: {resultado_jsonb}")
            
            # Si es string, convertir a dict
            if isinstance(resultado_jsonb, str):
                conversacion_data = json.loads(resultado_jsonb)
            elif isinstance(resultado_jsonb, dict):
                conversacion_data = resultado_jsonb
            else:
                print(f"❌ Tipo inesperado: {type(resultado_jsonb)}")
                if con:
                    con.rollback()
                return {
                    'success': False,
                    'message': 'Formato de respuesta inválido'
                }
            
            con.commit()
            
            print(f"✅ Conversación obtenida: {conversacion_data.get('id_conversacion')}")
            
            return {
                'success': True,
                'data': conversacion_data
            }
                
        except Exception as e:
            print(f"❌ Error en buscar_o_crear: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            
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
            
            rows = cursor.fetchall()
            conversaciones = []
            
            for row in rows:
                # Manejar tanto dict como tuple
                if isinstance(row, dict):
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
                else:
                    # Si es tupla
                    conversaciones.append({
                        'id_conversacion': row[0],
                        'id_usuario': row[1],
                        'id_sucursal': row[2],
                        'ultimo_mensaje': row[3],
                        'fecha_ultimo_mensaje': row[4].isoformat() if row[4] else None,
                        'mensajes_no_leidos': row[5],
                        'created_at': row[6].isoformat() if row[6] else None,
                        'sucursal': {
                            'nombre': row[7],
                            'logo': row[8]
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
                if isinstance(row, dict):
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
                else:
                    return {
                        'id_conversacion': row[0],
                        'id_usuario': row[1],
                        'id_sucursal': row[2],
                        'ultimo_mensaje': row[3],
                        'fecha_ultimo_mensaje': row[4].isoformat() if row[4] else None,
                        'mensajes_no_leidos_usuario': row[5],
                        'mensajes_no_leidos_sucursal': row[6],
                        'estado': row[7],
                        'created_at': row[8].isoformat() if row[8] else None,
                        'usuario': {
                            'nombre': row[9],
                            'img': row[10]
                        },
                        'sucursal': {
                            'nombre': row[11],
                            'logo': row[12]
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