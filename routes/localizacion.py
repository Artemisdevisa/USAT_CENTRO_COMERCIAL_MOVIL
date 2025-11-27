# routes/localizacion.py
from flask import Blueprint, jsonify, request
from models.localizacion import Localizacion

ws_localizacion = Blueprint("ws_localizacion", __name__)
localizacion = Localizacion()

@ws_localizacion.get("/localizacion/departamentos")
def listar_departamentos():
    """
    Listar departamentos
    ---
    tags:
      - Localización
    responses:
      200:
        description: Departamentos obtenidos correctamente
      500:
        description: Error interno del servidor
    """
    ok, data, msg = localizacion.listar_departamentos()
    code = 200 if ok else 500
    return jsonify({"status": ok, "data": data if ok else None, "message": msg}), code


@ws_localizacion.get("/localizacion/provincias")
def listar_provincias_por_departamento():
    """
    Listar provincias por departamento
    ---
    tags:
      - Localización
    parameters:
      - name: id_dep
        in: query
        required: true
        type: integer
        description: ID del departamento
    responses:
      200:
        description: Provincias obtenidas correctamente
      400:
        description: Parámetro id_dep es requerido o no es entero
      500:
        description: Error interno del servidor
    """
    # admite ?id_dep=#
    id_dep = request.args.get("id_dep", type=int)
    if not id_dep:
        return jsonify({"status": False, "data": None, "message": "Parámetro id_dep es requerido y debe ser entero."}), 400
    ok, data, msg = localizacion.listar_provincias_por_departamento(id_dep)
    code = 200 if ok else 500
    return jsonify({"status": ok, "data": data if ok else None, "message": msg}), code


@ws_localizacion.get("/localizacion/distritos")
def listar_distritos_por_provincia():
    """
    Listar distritos por provincia
    ---
    tags:
      - Localización
    parameters:
      - name: id_prov
        in: query
        required: true
        type: integer
        description: ID de la provincia
    responses:
      200:
        description: Distritos obtenidos correctamente
      400:
        description: Parámetro id_prov es requerido o no es entero
      500:
        description: Error interno del servidor
    """
    # admite ?id_prov=#
    id_prov = request.args.get("id_prov", type=int)
    if not id_prov:
        return jsonify({"status": False, "data": None, "message": "Parámetro id_prov es requerido y debe ser entero."}), 400
    ok, data, msg = localizacion.listar_distritos_por_provincia(id_prov)
    code = 200 if ok else 500
    return jsonify({"status": ok, "data": data if ok else None, "message": msg}), code
