from flask import Blueprint, jsonify, request
from models.tipo_documento import TipoDocumento

ws_tipo_documento = Blueprint("ws_tipo_documento", __name__)
tipo_documento = TipoDocumento()

# ✅ USAR SOLO ESTE ENDPOINT
@ws_tipo_documento.get("/api/tipos-documento/listar")
def listar_tipos_documento():
    """Listar tipos de documento para Android"""
    try:
        ok, data, msg = tipo_documento.listar_tipo_documento()
        
        print(f"📋 Tipos de documento: {data}")  # Debug
        
        if ok:
            return jsonify({
                "status": True,
                "data": data,
                "message": "Tipos de documento obtenidos"
            }), 200
        else:
            return jsonify({
                "status": False,
                "data": [],
                "message": msg
            }), 500
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({
            "status": False,
            "data": [],
            "message": f"Error: {str(e)}"
        }), 500