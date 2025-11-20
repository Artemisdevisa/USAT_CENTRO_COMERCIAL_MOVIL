from flask import Blueprint, request, jsonify
from models.persona import Persona
from conexionBD import Conexion

ws_persona = Blueprint('ws_persona', __name__)
persona_model = Persona()

@ws_persona.route('/api/persona/<int:id_persona>', methods=['GET'])
def obtener_persona(id_persona):
    """Obtener datos de persona por ID"""
    try:
        print("\n" + "="*80)
        print("📥 GET PERSONA")
        print("="*80)
        print(f"🆔 ID Persona: {id_persona}")
        
        exito, resultado = persona_model.obtener_por_id(id_persona)
        
        if exito:
            print("✅ Persona encontrada")
            print("="*80 + "\n")
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
            print(f"❌ Error: {resultado}")
            print("="*80 + "\n")
            return jsonify({
                'status': False,
                'message': resultado
            }), 404
            
    except Exception as e:
        print(f"💥 ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        print("="*80 + "\n")
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500


@ws_persona.route('/api/persona/<int:id_persona>', methods=['PUT'])
def actualizar_persona(id_persona):
    """Actualizar datos de persona"""
    try:
        data = request.get_json()
        
        print("\n" + "="*80)
        print("📝 ACTUALIZAR PERSONA - INICIO")
        print("="*80)
        print(f"🆔 ID Persona recibido: {id_persona}")
        print(f"📦 Body completo: {data}")
        print("="*80)
        
        nombres = data.get('nombres')
        apellidos = data.get('apellidos')
        telefono = data.get('telefono')
        direccion = data.get('direccion')
        fecha_nacimiento = data.get('fecha_nacimiento')
        
        print(f"👤 Nombres: '{nombres}'")
        print(f"👤 Apellidos: '{apellidos}'")
        print(f"📞 Teléfono: '{telefono}'")
        print(f"📍 Dirección: '{direccion}'")
        print(f"📅 Fecha Nacimiento: '{fecha_nacimiento}'")
        print("="*80)
        
        # Validaciones
        if not nombres or nombres.strip() == '':
            return jsonify({
                'status': False,
                'message': 'Nombres es requerido'
            }), 400
        
        if not apellidos or apellidos.strip() == '':
            return jsonify({
                'status': False,
                'message': 'Apellidos es requerido'
            }), 400
        
        # Llamar al modelo
        exito, mensaje = persona_model.actualizar(
            id_persona, nombres, apellidos, telefono, direccion, fecha_nacimiento
        )
        
        if exito:
            print("✅ ACTUALIZACIÓN EXITOSA")
            print("="*80 + "\n")
            return jsonify({
                'status': True,
                'message': mensaje
            }), 200
        else:
            print(f"❌ Error: {mensaje}")
            print("="*80 + "\n")
            return jsonify({
                'status': False,
                'message': mensaje
            }), 400
            
    except Exception as e:
        print(f"💥 ERROR CRÍTICO: {str(e)}")
        import traceback
        traceback.print_exc()
        print("="*80 + "\n")
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500