from conexionBD import Conexion

class Conversacion:
    
    @staticmethod
    def buscar_o_crear(id_usuario, id_sucursal):
        """
        Busca o crea conversación entre usuario y sucursal
        """
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
            
            if resultado and resultado[0]:
                conversacion_data = resultado[0]
                
                con.commit()
                cursor.close()
                con.close()
                
                print(f"✅ Conversación obtenida: {conversacion_data.get('id_conversacion')}")
                
                return {
                    'success': True,
                    'data': conversacion_data
                }
            else:
                con.rollback()
                cursor.close()
                con.close()
                
                print("❌ La función no devolvió datos")
                return {
                    'success': False,
                    'message': 'No se pudo iniciar la conversación'
                }
                
        except Exception as e:
            print(f"❌ Error en buscar_o_crear: {e}")
            if 'con' in locals():
                con.rollback()
                cursor.close()
                con.close()
            
            return {
                'success': False,
                'message': str(e)
            }
    
    
    @staticmethod
    def listar_por_usuario(id_usuario):
        """
        Lista todas las conversaciones activas de un usuario
        """
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
            
            cursor.close()
            con.close()
            
            return {
                'success': True,
                'data': conversaciones
            }
            
        except Exception as e:
            print(f"❌ Error en listar_por_usuario: {e}")
            if 'con' in locals():
                cursor.close()
                con.close()
            
            return {
                'success': False,
                'message': str(e)
            }
    
    
    @staticmethod
    def obtener_por_id(id_conversacion):
        """
        Obtiene detalles de una conversación específica
        """
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
            if 'con' in locals():
                cursor.close()
                con.close()
            return None
    
    
    @staticmethod
    def archivar(id_conversacion, id_usuario):
        """
        Archiva una conversación (cambia estado a FALSE)
        """
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
                cursor.close()
                con.close()
                
                return {
                    'success': True,
                    'message': 'Conversación archivada correctamente'
                }
            else:
                con.rollback()
                cursor.close()
                con.close()
                
                return {
                    'success': False,
                    'message': 'No se pudo archivar la conversación'
                }
                
        except Exception as e:
            print(f"❌ Error en archivar: {e}")
            if 'con' in locals():
                con.rollback()
                cursor.close()
                con.close()
            
            return {
                'success': False,
                'message': str(e)
            }