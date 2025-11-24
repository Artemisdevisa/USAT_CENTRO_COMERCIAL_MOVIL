from flask import Blueprint, request, jsonify
from models.conversacion import Conversacion
from models.mensaje import Mensaje

ws_conversacion = Blueprint('conversacion', __name__)

# =====================================================
# INICIAR O RECUPERAR CONVERSACIÓN
# =====================================================
@ws_conversacion.route('/conversacion/iniciar', methods=['POST'])
def iniciar_conversacion():
    """
    Iniciar o recuperar conversación entre usuario y sucursal
    Body: {
        "id_usuario": 1,
        "id_sucursal": 3
    }
    """
    try:
        data = request.json
        id_usuario = data.get('id_usuario')
        id_sucursal = data.get('id_sucursal')
        
        print(f"📩 Iniciando conversación | Usuario: {id_usuario} | Sucursal: {id_sucursal}")
        
        if not id_usuario or not id_sucursal:
            return jsonify({
                'status': False,
                'message': 'Faltan datos requeridos'
            }), 400
        
        resultado = Conversacion.buscar_o_crear(id_usuario, id_sucursal)
        
        if resultado.get('success'):
            print(f"✅ Conversación iniciada: {resultado.get('data', {}).get('id_conversacion')}")
            return jsonify({
                'status': True,
                'data': resultado.get('data')
            }), 200
        else:
            print(f"❌ Error: {resultado.get('message')}")
            return jsonify({
                'status': False,
                'message': resultado.get('message')
            }), 400
            
    except Exception as e:
        print(f"❌ Error en iniciar_conversacion: {e}")
        return jsonify({
            'status': False,
            'message': str(e)
        }), 500


# =====================================================
# LISTAR CONVERSACIONES DE UN USUARIO
# =====================================================
@ws_conversacion.route('/conversacion/listar/<int:id_usuario>', methods=['GET'])
def listar_conversaciones(id_usuario):
    """
    Lista todas las conversaciones de un usuario
    """
    try:
        print(f"📋 Listando conversaciones del usuario: {id_usuario}")
        
        resultado = Conversacion.listar_por_usuario(id_usuario)
        
        if resultado.get('success'):
            conversaciones = resultado.get('data', [])
            print(f"✅ {len(conversaciones)} conversaciones encontradas")
            
            return jsonify({
                'status': True,
                'data': conversaciones
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': resultado.get('message')
            }), 400
            
    except Exception as e:
        print(f"❌ Error en listar_conversaciones: {e}")
        return jsonify({
            'status': False,
            'message': str(e)
        }), 500


# =====================================================
# OBTENER DETALLE DE CONVERSACIÓN
# =====================================================
@ws_conversacion.route('/conversacion/<int:id_conversacion>', methods=['GET'])
def obtener_conversacion(id_conversacion):
    """
    Obtiene detalles de una conversación específica
    """
    try:
        print(f"🔍 Obteniendo conversación: {id_conversacion}")
        
        conversacion = Conversacion.obtener_por_id(id_conversacion)
        
        if conversacion:
            return jsonify({
                'status': True,
                'data': conversacion
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': 'Conversación no encontrada'
            }), 404
            
    except Exception as e:
        print(f"❌ Error en obtener_conversacion: {e}")
        return jsonify({
            'status': False,
            'message': str(e)
        }), 500


# =====================================================
# ARCHIVAR CONVERSACIÓN
# =====================================================
@ws_conversacion.route('/conversacion/archivar', methods=['POST'])
def archivar_conversacion():
    """
    Archiva una conversación
    Body: {
        "id_conversacion": 1,
        "id_usuario": 5
    }
    """
    try:
        data = request.json
        id_conversacion = data.get('id_conversacion')
        id_usuario = data.get('id_usuario')
        
        print(f"🗄️ Archivando conversación: {id_conversacion}")
        
        resultado = Conversacion.archivar(id_conversacion, id_usuario)
        
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
        print(f"❌ Error en archivar_conversacion: {e}")
        return jsonify({
            'status': False,
            'message': str(e)
        }), 500


# =====================================================
# CONTAR MENSAJES NO LEÍDOS
# =====================================================
@ws_conversacion.route('/conversacion/no-leidos/<int:id_usuario>', methods=['GET'])
def contar_no_leidos(id_usuario):
    """
    Cuenta total de mensajes no leídos de un usuario
    """
    try:
        count = Mensaje.contar_no_leidos(id_usuario)
        
        return jsonify({
            'status': True,
            'count': count
        }), 200
        
    except Exception as e:
        print(f"❌ Error en contar_no_leidos: {e}")
        return jsonify({
            'status': False,
            'message': str(e)
        }), 500