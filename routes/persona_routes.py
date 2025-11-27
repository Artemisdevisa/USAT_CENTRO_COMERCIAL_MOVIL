from flask import Blueprint, request, jsonify
from models.persona import Persona
from conexionBD import Conexion

ws_persona = Blueprint('ws_persona', __name__)
persona_model = Persona()

@ws_persona.route('/api/persona/<int:id_persona>', methods=['GET'])
def obtener_persona(id_persona):
    """
    Obtener datos de persona por ID
    ---
    tags:
      - Personas
    parameters:
      - name: id_persona
        in: path
        required: true
        type: integer
        description: ID de la persona
    responses:
      200:
        description: Datos de la persona obtenidos correctamente
      404:
        description: Persona no encontrada
      500:
        description: Error interno del servidor
    """
    try:
        exito, resultado = persona_model.obtener_por_id(id_persona)
        
        if exito:
            return jsonify({
                'status': True,
                'data': {
                    'id_persona': resultado['id_persona'],
                    'nombres': resultado['nombres'],
                    'apellidos': resultado['apellidos'],
                    'tipo_doc': resultado['tipo_doc'],
                    'documento': resultado['documento'],
                    'fecha_nacimiento': str(resultado['fecha_nacimiento']) if resultado['fecha_nacimiento'] else None,
                    'telefono': resultado['telefono'],
                    'id_dist': resultado['id_dist'],
                    'direccion': resultado['direccion'],
                    'distrito': resultado['distrito'],
                    'provincia': resultado['provincia'],
                    'departamento': resultado['departamento']
                }
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': resultado
            }), 404
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500


@ws_persona.route('/api/persona/<int:id_persona>', methods=['PUT'])
def actualizar_persona(id_persona):
    """
    Actualizar datos de persona
    ---
    tags:
      - Personas
    consumes:
      - application/json
    parameters:
      - name: id_persona
        in: path
        required: true
        type: integer
        description: ID de la persona a actualizar
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            nombres:
              type: string
              description: Nombres de la persona
            apellidos:
              type: string
              description: Apellidos de la persona
            telefono:
              type: string
              description: Teléfono de contacto
            direccion:
              type: string
              description: Dirección de la persona
            fecha_nacimiento:
              type: string
              format: date
              description: Fecha de nacimiento (YYYY-MM-DD)
          required:
            - nombres
            - apellidos
    responses:
      200:
        description: Persona actualizada correctamente
      400:
        description: Error de validación o datos incompletos
      404:
        description: Persona no encontrada
      500:
        description: Error interno del servidor
    """
    try:
        data = request.get_json()
        
        nombres = data.get('nombres', '').strip()
        apellidos = data.get('apellidos', '').strip()
        telefono = data.get('telefono', '').strip()
        direccion = data.get('direccion', '').strip()
        fecha_nacimiento = data.get('fecha_nacimiento')
        
        if not nombres or not apellidos:
            return jsonify({
                'status': False,
                'message': 'Nombres y apellidos son requeridos'
            }), 400
        
        print("\n" + "="*80)
        print("📝 ACTUALIZAR PERSONA")
        print("="*80)
        print(f"🆔 ID: {id_persona}")
        print(f"👤 Nombres: {nombres}")
        print(f"👤 Apellidos: {apellidos}")
        print(f"📞 Teléfono: {telefono}")
        print(f"📍 Dirección: {direccion}")
        print(f"📅 Fecha Nac: {fecha_nacimiento}")
        print("="*80)
        
        con = Conexion().open
        cursor = con.cursor()
        
        sql = """
            UPDATE persona 
            SET nombres = %s, 
                apellidos = %s,
                telefono = %s,
                direccion = %s,
                fecha_nacimiento = %s
            WHERE id_persona = %s AND estado = TRUE
        """
        
        cursor.execute(sql, [nombres, apellidos, telefono, direccion, fecha_nacimiento, id_persona])
        
        if cursor.rowcount == 0:
            cursor.close()
            con.close()
            return jsonify({
                'status': False,
                'message': 'No se pudo actualizar. Persona no encontrada.'
            }), 404
        
        con.commit()
        cursor.close()
        con.close()
        
        print("✅ Persona actualizada correctamente\n")
        
        return jsonify({
            'status': True,
            'message': 'Persona actualizada correctamente'
        }), 200
        
    except Exception as e:
        print(f"💥 ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500
