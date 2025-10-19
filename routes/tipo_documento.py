from flask import Blueprint, jsonify, request
from models.tipo_documento import TipoDocumento

ws_tipo_documento = Blueprint("ws_tipo_documento", __name__)
tipo_documento = TipoDocumento()

@ws_tipo_documento.get("/documento/tipos")

def listar_tipo_documento():
    ok, data, msg = tipo_documento.listar_tipo_documento()
    code = 200 if ok else 500
    return jsonify({"status": ok, "data": data if ok else None, "message": msg}), code