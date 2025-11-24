from flask import Blueprint, request, jsonify
from models.mensaje import Mensaje
from conexionBD import Conexion
from config import Config
ws_mensaje = Blueprint('mensaje', __name__)

# =====================================================
# ENVIAR MENSAJE
# =====================================================
@ws_mensaje.route('/mensaje/enviar', methods=['POST'])
def enviar_mensaje():
    """
    Envía un mensaje en una conversación
    Body: {
        "id_conversacion": 1,
        "id_emisor": 5,
        "tipo_emisor": "USUARIO",
        "contenido": "Hola, ¿tienen stock?",
        "tipo_mensaje": "TEXTO"
    }
    """
    try:
        data = request.json
        id_conversacion = data.get('id_conversacion')
        id_emisor = data.get('id_emisor')
        tipo_emisor = data.get('tipo_emisor')
        contenido = data.get('contenido')
        tipo_mensaje = data.get('tipo_mensaje', 'TEXTO')
        url_archivo = data.get('url_archivo')
        
        print(f"📤 Enviando mensaje | Conversación: {id_conversacion} | Emisor: {id_emisor} ({tipo_emisor})")
        
        if not all([id_conversacion, id_emisor, tipo_emisor, contenido]):
            return jsonify({
                'status': False,
                'message': 'Faltan datos requeridos'
            }), 400
        
        resultado = Mensaje.enviar(
            id_conversacion,
            id_emisor,
            tipo_emisor,
            contenido,
            tipo_mensaje,
            url_archivo
        )
        
        if resultado.get('success'):
            print(f"✅ Mensaje enviado: ID {resultado.get('data', {}).get('id_mensaje')}")
            
            # TODO: Aquí se puede agregar lógica para enviar notificación FCM
            
            return jsonify({
                'status': True,
                'data': resultado.get('data'),
                'message': 'Mensaje enviado correctamente'
            }), 200
        else:
            print(f"❌ Error: {resultado.get('message')}")
            return jsonify({
                'status': False,
                'message': resultado.get('message')
            }), 400
            
    except Exception as e:
        print(f"❌ Error en enviar_mensaje: {e}")
        return jsonify({
            'status': False,
            'message': str(e)
        }), 500


# =====================================================
# LISTAR MENSAJES DE CONVERSACIÓN
# =====================================================
@ws_mensaje.route('/mensaje/listar/<int:id_conversacion>/<int:id_usuario>', methods=['GET'])
def listar_mensajes(id_conversacion, id_usuario):
    """
    Lista todos los mensajes de una conversación
    Automáticamente marca los mensajes como leídos
    """
    try:
        print(f"📨 Listando mensajes | Conversación: {id_conversacion} | Usuario: {id_usuario}")
        
        resultado = Mensaje.listar_por_conversacion(id_conversacion, id_usuario)
        
        if resultado.get('success'):
            mensajes = resultado.get('data', [])
            print(f"✅ {len(mensajes)} mensajes encontrados")
            
            return jsonify({
                'status': True,
                'data': mensajes
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': resultado.get('message')
            }), 400
            
    except Exception as e:
        print(f"❌ Error en listar_mensajes: {e}")
        return jsonify({
            'status': False,
            'message': str(e)
        }), 500


# =====================================================
# MARCAR MENSAJES COMO LEÍDOS
# =====================================================
@ws_mensaje.route('/mensaje/marcar-leidos', methods=['POST'])
def marcar_leidos():
    """
    Marca mensajes de una conversación como leídos
    Body: {
        "id_conversacion": 1,
        "tipo_lector": "USUARIO"
    }
    """
    try:
        data = request.json
        id_conversacion = data.get('id_conversacion')
        tipo_lector = data.get('tipo_lector')
        
        print(f"✔️ Marcando mensajes como leídos | Conversación: {id_conversacion} | Lector: {tipo_lector}")
        
        resultado = Mensaje.marcar_leidos(id_conversacion, tipo_lector)
        
        if resultado.get('success'):
            return jsonify({
                'status': True,
                'message': resultado.get('message')
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': resultado.get('message')
            }), 400
            
    except Exception as e:
        print(f"❌ Error en marcar_leidos: {e}")
        return jsonify({
            'status': False,
            'message': str(e)
        }), 500
    
# ✅ AGREGAR AL FINAL DEL ARCHIVO

# =====================================================
# LISTAR MENSAJES PARA WEB (MARCA COMO LEÍDOS PARA SUCURSAL)
# =====================================================
@ws_mensaje.route('/mensaje/listar-web/<int:id_conversacion>/<int:id_sucursal>', methods=['GET'])
def listar_mensajes_web(id_conversacion, id_sucursal):
    """
    Lista mensajes y marca como leídos para la sucursal
    """
    try:
        print(f"📨 Listando mensajes web | Conversación: {id_conversacion} | Sucursal: {id_sucursal}")
        
        con = Conexion().open
        cursor = con.cursor()
        
        # Obtener mensajes
        cursor.execute("""
            SELECT 
                m.id_mensaje,
                m.id_emisor,
                m.tipo_emisor,
                m.contenido,
                m.tipo_mensaje,
                m.url_archivo,
                m.leido,
                m.fecha_leido,
                m.created_at,
                u.nomusuario as nombre_emisor,
                u.img_logo as img_emisor
            FROM mensaje m
            INNER JOIN usuario u ON m.id_emisor = u.id_usuario
            WHERE m.id_conversacion = %s
            ORDER BY m.created_at ASC
        """, (id_conversacion,))
        
        mensajes = []
        for row in cursor.fetchall():
            mensajes.append({
                'id_mensaje': row['id_mensaje'],
                'id_emisor': row['id_emisor'],
                'tipo_emisor': row['tipo_emisor'],
                'contenido': row['contenido'],
                'tipo_mensaje': row['tipo_mensaje'],
                'url_archivo': row['url_archivo'],
                'leido': row['leido'],
                'fecha_leido': row['fecha_leido'].isoformat() if row['fecha_leido'] else None,
                'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                'nombre_emisor': row['nombre_emisor'],
                'img_emisor': row['img_emisor']
            })
        
        # Marcar mensajes de usuario como leídos
        cursor.execute("""
            UPDATE mensaje
            SET leido = TRUE,
                fecha_leido = DATE_TRUNC('minute', LOCALTIMESTAMP)
            WHERE id_conversacion = %s
              AND tipo_emisor = 'USUARIO'
              AND leido = FALSE
        """, (id_conversacion,))
        
        # Resetear contador
        cursor.execute("""
            UPDATE conversacion
            SET mensajes_no_leidos_sucursal = 0
            WHERE id_conversacion = %s
        """, (id_conversacion,))
        
        con.commit()
        cursor.close()
        con.close()
        
        print(f"✅ {len(mensajes)} mensajes encontrados")
        
        return jsonify({
            'status': True,
            'data': mensajes
        }), 200
        
    except Exception as e:
        print(f"❌ Error en listar_mensajes_web: {e}")
        return jsonify({
            'status': False,
            'message': str(e)
        }), 500