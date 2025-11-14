from flask import Blueprint, jsonify, request
from models.sucursal import Sucursal
from conexionBD import Conexion
from werkzeug.utils import secure_filename
import os

ws_sucursal = Blueprint('ws_sucursal', __name__)

# Configuración de uploads
UPLOAD_FOLDER_LOGO = 'uploads/fotos/sucursales/logos'
UPLOAD_FOLDER_BANNER = 'uploads/fotos/sucursales/banners'
os.makedirs(UPLOAD_FOLDER_LOGO, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_BANNER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@ws_sucursal.route('/sucursales/listar-por-empresa/<int:id_empresa>', methods=['GET'])
def listar_por_empresa(id_empresa):
    """Listar sucursales de una empresa"""
    try:
        con = Conexion().open
        cursor = con.cursor()
        
        cursor.execute("""
            SELECT s.id_sucursal, s.nombre, s.direccion, s.telefono, 
                   s.img_logo, s.img_banner,
                   d.nombre as distrito, s.estado, s.id_dist
            FROM sucursal s
            LEFT JOIN distrito d ON s.id_dist = d.id_dist
            WHERE s.id_empresa = %s
            ORDER BY s.nombre
        """, [id_empresa])
        
        sucursales = cursor.fetchall()
        cursor.close()
        con.close()
        
        return jsonify({'status': True, 'data': sucursales}), 200
    except Exception as e:
        return jsonify({'status': False, 'message': f'Error: {str(e)}'}), 500

@ws_sucursal.route('/sucursales/crear', methods=['POST'])
def crear_sucursal():
    """Crear nueva sucursal con imágenes"""
    try:
        # Obtener datos del form-data
        id_empresa = request.form.get('id_empresa')
        nombre = request.form.get('nombre')
        id_dist = request.form.get('id_dist')
        direccion = request.form.get('direccion')
        telefono = request.form.get('telefono')
        
        if not all([id_empresa, nombre, id_dist, direccion, telefono]):
            return jsonify({'status': False, 'message': 'Faltan campos obligatorios'}), 400
        
        # Procesar imágenes
        img_logo = None
        img_banner = None
        
        if 'img_logo' in request.files:
            file = request.files['img_logo']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"logo_{id_empresa}_{nombre}_{file.filename}")
                filepath = os.path.join(UPLOAD_FOLDER_LOGO, filename)
                file.save(filepath)
                img_logo = filename
        
        if 'img_banner' in request.files:
            file = request.files['img_banner']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"banner_{id_empresa}_{nombre}_{file.filename}")
                filepath = os.path.join(UPLOAD_FOLDER_BANNER, filename)
                file.save(filepath)
                img_banner = filename
        
        # Crear sucursal
        con = Conexion().open
        cursor = con.cursor()
        
        cursor.execute("""
            SELECT fn_sucursal_crear(%s, %s, %s, %s, %s, %s, %s) as resultado
        """, [id_empresa, nombre, int(id_dist), direccion, telefono, img_logo, img_banner])
        
        resultado = cursor.fetchone()['resultado']
        con.commit()
        cursor.close()
        con.close()
        
        if resultado > 0:
            return jsonify({'status': True, 'message': 'Sucursal creada', 'id_sucursal': resultado}), 201
        else:
            return jsonify({'status': False, 'message': 'Error al crear'}), 400
    except Exception as e:
        print(f"Error al crear sucursal: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': False, 'message': f'Error: {str(e)}'}), 500

@ws_sucursal.route('/sucursales/obtener/<int:id>', methods=['GET'])
def obtener_sucursal(id):
    """Obtener datos completos de sucursal incluyendo ubicación"""
    try:
        con = Conexion().open
        cursor = con.cursor()
        
        cursor.execute("""
            SELECT 
                s.*,
                d.nombre as distrito,
                p.nombre as provincia,
                dep.nombre as departamento,
                p.id_prov,
                dep.id_dep
            FROM sucursal s
            LEFT JOIN distrito d ON s.id_dist = d.id_dist
            LEFT JOIN provincia p ON d.id_prov = p.id_prov
            LEFT JOIN departamento dep ON p.id_dep = dep.id_dep
            WHERE s.id_sucursal = %s
        """, [id])
        
        sucursal = cursor.fetchone()
        cursor.close()
        con.close()
        
        return jsonify({'status': True, 'data': sucursal}), 200
    except Exception as e:
        return jsonify({'status': False, 'message': str(e)}), 500

@ws_sucursal.route('/sucursales/modificar/<int:id>', methods=['PUT'])
def modificar_sucursal(id):
    """Modificar sucursal con opción de actualizar imágenes"""
    try:
        # Obtener datos del form-data
        id_empresa = request.form.get('id_empresa')
        nombre = request.form.get('nombre')
        id_dist = request.form.get('id_dist')
        direccion = request.form.get('direccion')
        telefono = request.form.get('telefono')
        
        if not all([id_empresa, nombre, id_dist, direccion, telefono]):
            return jsonify({'status': False, 'message': 'Faltan campos obligatorios'}), 400
        
        # Obtener imágenes actuales
        con = Conexion().open
        cursor = con.cursor()
        cursor.execute("SELECT img_logo, img_banner FROM sucursal WHERE id_sucursal = %s", [id])
        current = cursor.fetchone()
        
        img_logo = current['img_logo'] if current else None
        img_banner = current['img_banner'] if current else None
        
        # Procesar nueva imagen logo si existe
        if 'img_logo' in request.files:
            file = request.files['img_logo']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"logo_{id_empresa}_{nombre}_{file.filename}")
                filepath = os.path.join(UPLOAD_FOLDER_LOGO, filename)
                file.save(filepath)
                img_logo = filename
        
        # Procesar nueva imagen banner si existe
        if 'img_banner' in request.files:
            file = request.files['img_banner']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"banner_{id_empresa}_{nombre}_{file.filename}")
                filepath = os.path.join(UPLOAD_FOLDER_BANNER, filename)
                file.save(filepath)
                img_banner = filename
        
        # Modificar sucursal
        cursor.execute("""
            SELECT fn_sucursal_modificar(%s, %s, %s, %s, %s, %s, %s, %s) as resultado
        """, [id, id_empresa, nombre, int(id_dist), direccion, telefono, img_logo, img_banner])
        
        resultado = cursor.fetchone()['resultado']
        con.commit()
        cursor.close()
        con.close()
        
        return jsonify({
            'status': resultado == 0, 
            'message': 'Sucursal modificada' if resultado == 0 else 'Error'
        }), 200
    except Exception as e:
        print(f"Error al modificar sucursal: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': False, 'message': str(e)}), 500

@ws_sucursal.route('/sucursales/cambiar-estado/<int:id>', methods=['PATCH'])
def cambiar_estado(id):
    try:
        con = Conexion().open
        cursor = con.cursor()
        cursor.execute("UPDATE sucursal SET estado = NOT estado WHERE id_sucursal = %s", [id])
        con.commit()
        cursor.close()
        con.close()
        return jsonify({'status': True, 'message': 'Estado cambiado'}), 200
    except Exception as e:
        return jsonify({'status': False, 'message': str(e)}), 500

@ws_sucursal.route('/sucursales/eliminar/<int:id>', methods=['DELETE'])
def eliminar_sucursal(id):
    """Eliminar lógicamente (cambiar estado a false)"""
    try:
        con = Conexion().open
        cursor = con.cursor()
        
        cursor.execute("SELECT fn_sucursal_eliminar(%s) as resultado", [id])
        resultado = cursor.fetchone()['resultado']
        
        con.commit()
        cursor.close()
        con.close()
        
        if resultado == 0:
            return jsonify({'status': True, 'message': 'Sucursal eliminada'}), 200
        else:
            return jsonify({'status': False, 'message': 'No se puede eliminar'}), 400
    except Exception as e:
        return jsonify({'status': False, 'message': f'Error: {str(e)}'}), 500

@ws_sucursal.route('/sucursales/eliminar-fisico/<int:id>', methods=['DELETE'])
def eliminar_fisico(id):
    """Eliminación física permanente"""
    try:
        con = Conexion().open
        cursor = con.cursor()
        cursor.execute("DELETE FROM sucursal WHERE id_sucursal = %s", [id])
        con.commit()
        cursor.close()
        con.close()
        return jsonify({'status': True, 'message': 'Sucursal eliminada permanentemente'}), 200
    except Exception as e:
        return jsonify({'status': False, 'message': str(e)}), 500