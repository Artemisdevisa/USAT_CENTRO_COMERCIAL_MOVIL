# routes/usuario2.py
from flask import Blueprint, request, jsonify
from models.usuario2 import Usuario2

ws_usuario2 = Blueprint("ws_usuario2", __name__)
usuario2 = Usuario2()

@ws_usuario2.post("/usuario2/registro")
def usuario2_registro():
    data = request.get_json(silent=True) or {}

    # Campos requeridos por la función
    required = [
        "nombres", "apellidos", "tipo_doc", "documento", "fecha_nacimiento",
        "telefono", "id_dist", "direccion", "nomusuario", "email", "password"
    ]
    missing = [k for k in required if data.get(k) in (None, "")]
    if missing:
        return jsonify({
            "status": False,
            "data": None,
            "message": f"Faltan datos obligatorios: {', '.join(missing)}"
        }), 400

    try:
        ok, payload, code = usuario2.registrar_cliente(
            nombres           = data.get("nombres"),
            apellidos         = data.get("apellidos"),
            tipo_doc          = int(data.get("tipo_doc")),
            documento         = data.get("documento"),
            fecha_nacimiento  = data.get("fecha_nacimiento"),  # 'YYYY-MM-DD'
            telefono          = data.get("telefono"),
            id_dist           = int(data.get("id_dist")),
            direccion         = data.get("direccion"),
            nomusuario        = data.get("nomusuario"),
            email             = data.get("email"),
            password          = data.get("password"),
            img_logo          = data.get("img_logo")  # opcional
        )
        return jsonify(payload), code
    except ValueError:
        # Por si tipo_doc o id_dist no son enteros
        return jsonify({
            "status": False,
            "data": None,
            "message": "Parámetros inválidos: 'tipo_doc' e 'id_dist' deben ser enteros"
        }), 400
    except Exception as e:
        return jsonify({"status": False, "data": None, "message": str(e)}), 500
