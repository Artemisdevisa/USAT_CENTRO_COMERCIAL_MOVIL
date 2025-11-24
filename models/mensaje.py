from conexionBD import Conexion
import json

class Mensaje:
    
    @staticmethod
    def enviar(id_conversacion, id_emisor, tipo_emisor, contenido, tipo_mensaje='TEXTO', url_archivo=None):
        """
        Envía un mensaje en una conversación
        """
        con = None
        cursor = None
        
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            print(f"📤 Enviando mensaje | Conversación: {id_conversacion} | Emisor: {id_emisor} ({tipo_emisor})")
            print(f"   Contenido: \"{contenido}\"")
            
            # Llamar a la función PostgreSQL
            cursor.execute(
                "SELECT fn_enviar_mensaje(%s, %s, %s, %s, %s, %s) as resultado",
                (id_conversacion, id_emisor, tipo_emisor, contenido, tipo_mensaje, url_archivo)
            )
            
            row = cursor.fetchone()
            
            print(f"📊 Row type: {type(row)}")
            
            if row is None:
                print("❌ fetchone() devolvió None")
                if con:
                    con.rollback()
                return {
                    'success': False,
                    'message': 'No se obtuvo respuesta de la base de datos'
                }
            
            # Obtener resultado según tipo
            if isinstance(row, dict):
                resultado_jsonb = row.get('resultado') or row.get('fn_enviar_mensaje')
                print(f"📦 Es DICT - Resultado: {resultado_jsonb}")
            else:
                resultado_jsonb = row[0] if len(row) > 0 else None
                print(f"📦 Es TUPLE - Resultado: {resultado_jsonb}")
            
            if resultado_jsonb is None:
                print("❌ resultado_jsonb es None")
                if con:
                    con.rollback()
                return {
                    'success': False,
                    'message': 'La función no devolvió datos'
                }
            
            # Convertir a dict si es string
            if isinstance(resultado_jsonb, str):
                mensaje_data = json.loads(resultado_jsonb)
            elif isinstance(resultado_jsonb, dict):
                mensaje_data = resultado_jsonb
            else:
                print(f"❌ Tipo inesperado: {type(resultado_jsonb)}")
                if con:
                    con.rollback()
                return {
                    'success': False,
                    'message': f'Formato de respuesta inválido: {type(resultado_jsonb)}'
                }
            
            # Verificar si la función devolvió success
            if mensaje_data.get('success'):
                con.commit()
                print(f"✅ Mensaje enviado: {mensaje_data.get('data', {}).get('id_mensaje')}")
                return mensaje_data
            else:
                con.rollback()
                print(f"❌ Error en función SQL: {mensaje_data.get('message')}")
                return mensaje_data
                
        except Exception as e:
            print(f"❌ ERROR COMPLETO en enviar():")
            print(f"   Tipo: {type(e).__name__}")
            print(f"   Mensaje: {str(e)}")
            
            import traceback
            print("📜 Traceback:")
            traceback.print_exc()
            
            if con:
                try:
                    con.rollback()
                except:
                    pass
            
            return {
                'success': False,
                'message': f"{type(e).__name__}: {str(e)}"
            }
        
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            if con:
                try:
                    con.close()
                except:
                    pass
    
    
    @staticmethod
    def listar_por_conversacion(id_conversacion, id_usuario):
        """
        Lista todos los mensajes de una conversación
        Marca automáticamente como leídos los mensajes de la sucursal
        """
        con = None
        cursor = None
        
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            print(f"📨 Listando mensajes | Conversación: {id_conversacion} | Usuario: {id_usuario}")
            
            # Llamar a la función PostgreSQL
            cursor.execute(
                "SELECT fn_listar_mensajes(%s, %s) as resultado",
                (id_conversacion, id_usuario)
            )
            
            row = cursor.fetchone()
            
            print(f"📊 Row type: {type(row)}")
            
            if row is None:
                print("❌ fetchone() devolvió None")
                return {
                    'success': False,
                    'message': 'No se obtuvo respuesta de la base de datos'
                }
            
            # Obtener resultado según tipo
            if isinstance(row, dict):
                resultado_jsonb = row.get('resultado') or row.get('fn_listar_mensajes')
                print(f"📦 Es DICT")
            else:
                resultado_jsonb = row[0] if len(row) > 0 else None
                print(f"📦 Es TUPLE")
            
            if resultado_jsonb is None:
                print("❌ resultado_jsonb es None")
                return {
                    'success': False,
                    'message': 'La función no devolvió datos'
                }
            
            # Convertir a dict si es string
            if isinstance(resultado_jsonb, str):
                mensajes_data = json.loads(resultado_jsonb)
            elif isinstance(resultado_jsonb, dict):
                mensajes_data = resultado_jsonb
            else:
                print(f"❌ Tipo inesperado: {type(resultado_jsonb)}")
                return {
                    'success': False,
                    'message': f'Formato de respuesta inválido: {type(resultado_jsonb)}'
                }
            
            # Verificar si la función devolvió success
            if mensajes_data.get('success'):
                con.commit()
                mensajes = mensajes_data.get('data', [])
                print(f"✅ {len(mensajes)} mensajes encontrados")
                return mensajes_data
            else:
                print(f"❌ Error en función SQL: {mensajes_data.get('message')}")
                return mensajes_data
                
        except Exception as e:
            print(f"❌ ERROR COMPLETO en listar_por_conversacion():")
            print(f"   Tipo: {type(e).__name__}")
            print(f"   Mensaje: {str(e)}")
            
            import traceback
            print("📜 Traceback:")
            traceback.print_exc()
            
            return {
                'success': False,
                'message': f"{type(e).__name__}: {str(e)}"
            }
        
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            if con:
                try:
                    con.close()
                except:
                    pass
    
    
    @staticmethod
    def marcar_leidos(id_conversacion, tipo_lector):
        """
        Marca mensajes de una conversación como leídos
        """
        con = None
        cursor = None
        
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            print(f"✔️ Marcando mensajes como leídos | Conversación: {id_conversacion} | Lector: {tipo_lector}")
            
            # Llamar a la función PostgreSQL
            cursor.execute(
                "SELECT fn_marcar_mensajes_leidos(%s, %s) as resultado",
                (id_conversacion, tipo_lector)
            )
            
            row = cursor.fetchone()
            
            if row is None:
                if con:
                    con.rollback()
                return {
                    'success': False,
                    'message': 'No se obtuvo respuesta de la base de datos'
                }
            
            # Obtener resultado según tipo
            if isinstance(row, dict):
                resultado_jsonb = row.get('resultado') or row.get('fn_marcar_mensajes_leidos')
            else:
                resultado_jsonb = row[0] if len(row) > 0 else None
            
            if resultado_jsonb is None:
                if con:
                    con.rollback()
                return {
                    'success': False,
                    'message': 'La función no devolvió datos'
                }
            
            # Convertir a dict si es string
            if isinstance(resultado_jsonb, str):
                result_data = json.loads(resultado_jsonb)
            elif isinstance(resultado_jsonb, dict):
                result_data = resultado_jsonb
            else:
                if con:
                    con.rollback()
                return {
                    'success': False,
                    'message': f'Formato de respuesta inválido: {type(resultado_jsonb)}'
                }
            
            if result_data.get('success'):
                con.commit()
                return result_data
            else:
                con.rollback()
                return result_data
                
        except Exception as e:
            print(f"❌ ERROR en marcar_leidos: {e}")
            import traceback
            traceback.print_exc()
            
            if con:
                try:
                    con.rollback()
                except:
                    pass
            
            return {
                'success': False,
                'message': str(e)
            }
        
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            if con:
                try:
                    con.close()
                except:
                    pass
    
    
    @staticmethod
    def contar_no_leidos(id_usuario):
        """
        Cuenta total de mensajes no leídos de un usuario
        """
        con = None
        cursor = None
        
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            cursor.execute(
                "SELECT fn_contar_mensajes_no_leidos_usuario(%s) as count",
                (id_usuario,)
            )
            
            row = cursor.fetchone()
            
            if row is None:
                return 0
            
            if isinstance(row, dict):
                count = row.get('count', 0)
            else:
                count = row[0] if len(row) > 0 else 0
            
            return count if count is not None else 0
            
        except Exception as e:
            print(f"❌ ERROR en contar_no_leidos: {e}")
            return 0
        
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            if con:
                try:
                    con.close()
                except:
                    pass