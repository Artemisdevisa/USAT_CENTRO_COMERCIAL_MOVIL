from flask import Blueprint, request, jsonify
from models.mensaje import Mensaje

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