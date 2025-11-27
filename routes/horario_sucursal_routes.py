from flask import Blueprint, jsonify, request
from models.horario_sucursal import HorarioSucursal

ws_horario_sucursal = Blueprint('ws_horario_sucursal', __name__)

DIAS_SEMANA = {
    0: 'Domingo',
    1: 'Lunes',
    2: 'Martes',
    3: 'Miércoles',
    4: 'Jueves',
    5: 'Viernes',
    6: 'Sábado'
}

@ws_horario_sucursal.route('/horarios-sucursal/crear', methods=['POST'])
def crear_horario():
    """
    Crear un nuevo horario para una sucursal
    ---
    tags:
      - Horarios Sucursal
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        description: Datos del horario a registrar
        schema:
          type: object
          properties:
            id_sucursal:
              type: integer
              description: ID de la sucursal
            dia:
              type: integer
              description: Día de la semana (0=Domingo, 6=Sábado)
            hora_inicio:
              type: string
              description: Hora de apertura en formato HH:MM
              example: "09:00"
            hora_fin:
              type: string
              description: Hora de cierre en formato HH:MM
              example: "18:00"
          required:
            - id_sucursal
            - dia
            - hora_inicio
            - hora_fin
    responses:
      201:
        description: Horario creado correctamente
      400:
        description: Error de validación o datos incompletos
      500:
        description: Error del servidor
    """
    try:
        data = request.get_json()
        
        print("=" * 60)
        print("📥 CREAR HORARIO - DATA RECIBIDA:")
        print(f"   Data completa: {data}")
        print("=" * 60)
        
        id_sucursal = data.get('id_sucursal')
        dia = data.get('dia')
        hora_inicio = data.get('hora_inicio')
        hora_fin = data.get('hora_fin')
        
        print(f"📊 VALORES PARSEADOS:")
        print(f"   id_sucursal: {id_sucursal} (type: {type(id_sucursal)})")
        print(f"   dia: {dia} (type: {type(dia)})")
        print(f"   hora_inicio: {hora_inicio} (type: {type(hora_inicio)})")
        print(f"   hora_fin: {hora_fin} (type: {type(hora_fin)})")
        
        # Validaciones
        if not all([id_sucursal, str(dia) != '', hora_inicio, hora_fin]):
            print("❌ VALIDACIÓN FALLIDA: Campos faltantes")
            return jsonify({
                'status': False,
                'message': 'Todos los campos son obligatorios'
            }), 400
        
        # Validar día
        try:
            dia_int = int(dia)
            if not (0 <= dia_int <= 6):
                print(f"❌ VALIDACIÓN FALLIDA: Día fuera de rango: {dia_int}")
                return jsonify({
                    'status': False,
                    'message': 'El día debe estar entre 0 (Domingo) y 6 (Sábado)'
                }), 400
        except ValueError:
            print(f"❌ VALIDACIÓN FALLIDA: Día no es número: {dia}")
            return jsonify({
                'status': False,
                'message': 'El día debe ser un número'
            }), 400
        
        print(f"🔄 LLAMANDO A HorarioSucursal.crear({id_sucursal}, {dia_int}, {hora_inicio}, {hora_fin})")
        resultado = HorarioSucursal.crear(id_sucursal, dia_int, hora_inicio, hora_fin)
        print(f"📤 RESULTADO: {resultado}")
        
        if resultado == -1:
            print("❌ ERROR: La función retornó -1")
            return jsonify({
                'status': False,
                'message': 'Error al crear el horario. Verifique que no exista un horario para este día en esta sucursal'
            }), 400
        
        print(f"✅ HORARIO CREADO EXITOSAMENTE - ID: {resultado}")
        print("=" * 60)
        
        return jsonify({
            'status': True,
            'message': '✅ Horario creado correctamente',
            'id_horario': resultado
        }), 201
        
    except Exception as e:
        print(f"❌ EXCEPCIÓN EN CREAR HORARIO: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': False,
            'message': f'Error del servidor: {str(e)}'
        }), 500


@ws_horario_sucursal.route('/horarios-sucursal/modificar/<int:id_horario>', methods=['PUT'])
def modificar_horario(id_horario):
    """
    Modificar un horario existente
    ---
    tags:
      - Horarios Sucursal
    consumes:
      - application/json
    parameters:
      - name: id_horario
        in: path
        required: true
        type: integer
        description: ID del horario a modificar
      - in: body
        name: body
        required: true
        description: Datos actualizados del horario
        schema:
          type: object
          properties:
            id_sucursal:
              type: integer
              description: ID de la sucursal
            dia:
              type: integer
              description: Día de la semana (0=Domingo, 6=Sábado)
            hora_inicio:
              type: string
              description: Hora de apertura en formato HH:MM
              example: "09:00"
            hora_fin:
              type: string
              description: Hora de cierre en formato HH:MM
              example: "18:00"
          required:
            - id_sucursal
            - dia
            - hora_inicio
            - hora_fin
    responses:
      200:
        description: Horario modificado correctamente
      400:
        description: Error de validación o actualización
      500:
        description: Error interno del servidor
    """
    try:
        data = request.get_json()
        
        id_sucursal = data.get('id_sucursal')
        dia = data.get('dia')
        hora_inicio = data.get('hora_inicio')
        hora_fin = data.get('hora_fin')
        
        if not all([id_sucursal, str(dia), hora_inicio, hora_fin]):
            return jsonify({
                'status': False,
                'message': 'Todos los campos son obligatorios'
            }), 400
        
        if not (0 <= int(dia) <= 6):
            return jsonify({
                'status': False,
                'message': 'El día debe estar entre 0 (Domingo) y 6 (Sábado)'
            }), 400
        
        resultado = HorarioSucursal.modificar(id_horario, id_sucursal, dia, hora_inicio, hora_fin)
        
        if resultado == -1:
            return jsonify({
                'status': False,
                'message': 'Error al modificar el horario'
            }), 400
        
        return jsonify({
            'status': True,
            'message': '✅ Horario modificado correctamente'
        }), 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500


@ws_horario_sucursal.route('/horarios-sucursal/eliminar/<int:id_horario>', methods=['DELETE'])
def eliminar_horario(id_horario):
    """
    Eliminar (lógico) un horario
    ---
    tags:
      - Horarios Sucursal
    parameters:
      - name: id_horario
        in: path
        required: true
        type: integer
        description: ID del horario a eliminar
    responses:
      200:
        description: Horario eliminado correctamente
      400:
        description: Error al eliminar el horario
      500:
        description: Error interno del servidor
    """
    try:
        resultado = HorarioSucursal.eliminar(id_horario)
        
        if resultado == -1:
            return jsonify({
                'status': False,
                'message': 'Error al eliminar el horario'
            }), 400
        
        return jsonify({
            'status': True,
            'message': '✅ Horario eliminado correctamente'
        }), 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500


@ws_horario_sucursal.route('/horarios-sucursal/listar/<int:id_sucursal>', methods=['GET'])
def listar_horarios(id_sucursal):
    """
    Listar todos los horarios de una sucursal
    ---
    tags:
      - Horarios Sucursal
    parameters:
      - name: id_sucursal
        in: path
        required: true
        type: integer
        description: ID de la sucursal
    responses:
      200:
        description: Lista de horarios obtenida correctamente
      500:
        description: Error interno del servidor
    """
    try:
        horarios = HorarioSucursal.listar_por_sucursal(id_sucursal)
        
        # Agregar nombre del día
        for horario in horarios:
            horario['dia_nombre'] = DIAS_SEMANA.get(horario['dia'], 'Desconocido')
        
        return jsonify({
            'status': True,
            'data': horarios
        }), 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'status': False,
            'data': [],
            'message': f'Error: {str(e)}'
        }), 500


@ws_horario_sucursal.route('/horarios-sucursal/obtener/<int:id_horario>', methods=['GET'])
def obtener_horario(id_horario):
    """
    Obtener un horario específico
    ---
    tags:
      - Horarios Sucursal
    parameters:
      - name: id_horario
        in: path
        required: true
        type: integer
        description: ID del horario
    responses:
      200:
        description: Horario obtenido correctamente
      404:
        description: Horario no encontrado
      500:
        description: Error interno del servidor
    """
    try:
        horario = HorarioSucursal.obtener(id_horario)
        
        if not horario:
            return jsonify({
                'status': False,
                'data': None,
                'message': 'Horario no encontrado'
            }), 404
        
        horario['dia_nombre'] = DIAS_SEMANA.get(horario['dia'], 'Desconocido')
        
        return jsonify({
            'status': True,
            'data': horario
        }), 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'status': False,
            'data': None,
            'message': f'Error: {str(e)}'
        }), 500
