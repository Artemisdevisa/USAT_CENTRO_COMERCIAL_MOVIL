from flask import Blueprint, request, jsonify
import os
from models.tarjeta import Tarjeta

ws_tarjeta = Blueprint('ws_tarjeta', __name__)

@ws_tarjeta.route('/tarjetas/listar/<int:id_usuario>', methods=['GET'])
def listar_tarjetas(id_usuario):
    """
    ---
    tags:
      - Tarjetas
    summary: Listar tarjetas del usuario
    description: Obtiene la lista de tarjetas de crédito/débito registradas por el usuario
    parameters:
      - name: id_usuario
        in: path
        type: integer
        required: true
        description: ID del usuario
    responses:
      200:
        description: Tarjetas listadas correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
            data:
              type: array
              items:
                type: object
                properties:
                  id_tarjeta:
                    type: integer
                  numero:
                    type: string
                  titular:
                    type: string
                  fecha_vencimiento:
                    type: string
                  tipo_tarjeta:
                    type: string
                  es_principal:
                    type: boolean
      500:
        description: Error interno del servidor
    """
    try:
        tarjeta = Tarjeta()
        exito, resultado = tarjeta.listar_por_usuario(id_usuario)
        
        if exito:
            # ✅ DETECTAR ENTORNO Y CLIENTE
            user_agent = request.headers.get('User-Agent', '').lower()
            is_android = 'okhttp' in user_agent or 'android' in user_agent
            
            # No hay imágenes en tarjetas, pero mantenemos la estructura
            return jsonify({
                'status': True,
                'data': resultado,
                'message': 'Tarjetas listadas correctamente'
            }), 200
        else:
            return jsonify({
                'status': False,
                'data': [],
                'message': resultado
            }), 500
    except Exception as e:
        return jsonify({
            'status': False,
            'data': [],
            'message': f'Error: {str(e)}'
        }), 500

@ws_tarjeta.route('/tarjetas/agregar', methods=['POST'])
def agregar_tarjeta():
    """
    ---
    tags:
      - Tarjetas
    summary: Agregar nueva tarjeta
    description: Registra una nueva tarjeta de crédito o débito para el usuario
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - id_usuario
            - numero
            - titular
            - fecha_vencimiento
            - cvv
            - tipo_tarjeta
          properties:
            id_usuario:
              type: integer
              description: ID del usuario propietario de la tarjeta
            numero:
              type: string
              description: Número de la tarjeta (sin espacios)
              example: "4532123456789010"
            titular:
              type: string
              description: Nombre del titular de la tarjeta
              example: "FERNANDO GUERRERO"
            fecha_vencimiento:
              type: string
              description: Fecha de vencimiento en formato MM/YY
              example: "12/26"
            cvv:
              type: string
              description: Código de seguridad CVV de la tarjeta
              example: "123"
            tipo_tarjeta:
              type: string
              description: Tipo de tarjeta (Visa, MasterCard, Amex, etc)
              example: "Visa"
            es_principal:
              type: boolean
              description: Indica si es la tarjeta principal del usuario
              default: false
    responses:
      201:
        description: Tarjeta agregada correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
            data:
              type: object
              properties:
                id_tarjeta:
                  type: integer
      400:
        description: Datos incompletos o inválidos
      500:
        description: Error en el servidor
    """
    try:
        data = request.get_json()
        
        print("════════════════════════════════════════")
        print("📥 PETICIÓN AGREGAR TARJETA")
        print("════════════════════════════════════════")
        print(f"Data recibida: {data}")
        
        id_usuario = data.get('id_usuario')
        numero = data.get('numero')
        titular = data.get('titular')
        fecha_vencimiento = data.get('fecha_vencimiento')
        cvv = data.get('cvv')
        tipo_tarjeta = data.get('tipo_tarjeta')
        es_principal = data.get('es_principal', False)
        
        print(f"ID Usuario: {id_usuario}")
        print(f"Número: {numero}")
        print(f"Titular: {titular}")
        print(f"Fecha: {fecha_vencimiento}")
        print(f"Tipo: {tipo_tarjeta}")
        print(f"Principal: {es_principal}")
        
        if not all([id_usuario, numero, titular, fecha_vencimiento, cvv, tipo_tarjeta]):
            print("❌ Faltan datos requeridos")
            return jsonify({
                'status': False,
                'message': 'Faltan datos requeridos'
            }), 400
        
        tarjeta = Tarjeta()
        exito, resultado = tarjeta.agregar(
            id_usuario, numero, titular, fecha_vencimiento, 
            cvv, tipo_tarjeta, es_principal
        )
        
        if exito:
            print(f"✅ Tarjeta agregada con ID: {resultado}")
            return jsonify({
                'status': True,
                'data': {'id_tarjeta': resultado},
                'message': 'Tarjeta agregada correctamente'
            }), 201
        else:
            print(f"❌ Error: {resultado}")
            return jsonify({
                'status': False,
                'message': resultado
            }), 400
            
    except Exception as e:
        print(f"💥 ERROR CRÍTICO: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500


@ws_tarjeta.route('/tarjetas/eliminar', methods=['POST'])
def eliminar_tarjeta():
    """
    ---
    tags:
      - Tarjetas
    summary: Eliminar tarjeta
    description: Elimina una tarjeta del registro del usuario
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - id_usuario
            - id_tarjeta
          properties:
            id_usuario:
              type: integer
              description: ID del usuario propietario de la tarjeta
            id_tarjeta:
              type: integer
              description: ID de la tarjeta a eliminar
    responses:
      200:
        description: Tarjeta eliminada correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
      400:
        description: Datos incompletos o tarjeta no encontrada
      500:
        description: Error en el servidor
    """
    try:
        data = request.get_json()
        
        id_usuario = data.get('id_usuario')
        id_tarjeta = data.get('id_tarjeta')
        
        if not all([id_usuario, id_tarjeta]):
            return jsonify({
                'status': False,
                'message': 'Faltan datos requeridos'
            }), 400
        
        tarjeta = Tarjeta()
        exito, mensaje = tarjeta.eliminar(id_usuario, id_tarjeta)
        
        if exito:
            return jsonify({
                'status': True,
                'message': mensaje
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': mensaje
            }), 400
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500

@ws_tarjeta.route('/tarjetas/establecer-principal', methods=['POST'])
def establecer_principal():
    """
    ---
    tags:
      - Tarjetas
    summary: Establecer tarjeta como principal
    description: Marca una tarjeta como principal para transacciones del usuario
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - id_usuario
            - id_tarjeta
          properties:
            id_usuario:
              type: integer
              description: ID del usuario propietario de la tarjeta
            id_tarjeta:
              type: integer
              description: ID de la tarjeta a establecer como principal
    responses:
      200:
        description: Tarjeta establecida como principal correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
      400:
        description: Datos incompletos o tarjeta no encontrada
      500:
        description: Error en el servidor
    """
    try:
        data = request.get_json()
        
        id_usuario = data.get('id_usuario')
        id_tarjeta = data.get('id_tarjeta')
        
        if not all([id_usuario, id_tarjeta]):
            return jsonify({
                'status': False,
                'message': 'Faltan datos requeridos'
            }), 400
        
        tarjeta = Tarjeta()
        exito, mensaje = tarjeta.establecer_principal(id_usuario, id_tarjeta)
        
        if exito:
            return jsonify({
                'status': True,
                'message': mensaje
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': mensaje
            }), 400
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500