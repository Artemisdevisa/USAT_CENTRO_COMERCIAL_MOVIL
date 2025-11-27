from flask import Blueprint, jsonify, request
from models.tipo_documento import TipoDocumento

ws_tipo_documento = Blueprint("ws_tipo_documento", __name__)
tipo_documento = TipoDocumento()

@ws_tipo_documento.get("/api/tipos-documento/listar")
def listar_tipos_documento():
    """
    ---
    tags:
      - Tipos de Documento
    summary: Listar tipos de documento
    description: Obtiene la lista de todos los tipos de documento disponibles en el sistema
    responses:
      200:
        description: Tipos de documento obtenidos correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
              example: true
            data:
              type: array
              items:
                type: object
                properties:
                  id_tipo_documento:
                    type: integer
                  nombre:
                    type: string
                    example: "Cédula de Identidad"
            message:
              type: string
              example: "Tipos de documento obtenidos"
      500:
        description: Error interno del servidor
        schema:
          type: object
          properties:
            status:
              type: boolean
              example: false
            data:
              type: array
              example: []
            message:
              type: string
    """
    try:
        print("\n" + "="*60)
        print("📋 ENDPOINT: /api/tipos-documento/listar")
        print("="*60)
        
        ok, data, msg = tipo_documento.listar_tipo_documento()
        
        print(f"✅ Status: {ok}")
        print(f"📊 Total datos: {len(data) if data else 0}")
        print(f"📝 Mensaje: {msg}")
        
        if data:
            for item in data:
                print(f"   - {item}")
        
        if ok:
            response = {
                "status": True,
                "data": data,
                "message": "Tipos de documento obtenidos"
            }
            print(f"📤 Respuesta: {response}")
            print("="*60 + "\n")
            return jsonify(response), 200
        else:
            response = {
                "status": False,
                "data": [],
                "message": msg
            }
            print(f"❌ Error respuesta: {response}")
            print("="*60 + "\n")
            return jsonify(response), 500
            
    except Exception as e:
        print(f"💥 EXCEPCIÓN: {str(e)}")
        import traceback
        traceback.print_exc()
        print("="*60 + "\n")
        return jsonify({
            "status": False,
            "data": [],
            "message": f"Error: {str(e)}"
        }), 500