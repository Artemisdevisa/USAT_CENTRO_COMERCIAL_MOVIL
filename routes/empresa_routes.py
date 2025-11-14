from flask import Blueprint, jsonify, request
from conexionBD import Conexion
from werkzeug.utils import secure_filename
import os
import time

ws_empresa = Blueprint('ws_empresa', __name__)

# Configuración de uploads con subcarpetas
UPLOAD_FOLDER_LOGOS = 'uploads/fotos/empresas/logos'
UPLOAD_FOLDER_BANNERS = 'uploads/fotos/empresas/banners'
os.makedirs(UPLOAD_FOLDER_LOGOS, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_BANNERS, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@ws_empresa.route('/empresas/listar-admin', methods=['GET'])
def listar_empresas_admin():
    """Listar TODAS las empresas (aprobadas y pendientes)"""
    try:
        con = Conexion().open
        cursor = con.cursor()
        
        sql = """
            SELECT 
                se.id_solicitud,
                se.id_usuario,
                se.ruc,
                se.razon_social,
                se.nombre_comercial,
                se.descripcion,
                se.telefono,
                se.email,
                se.direccion,
                se.estado,
                se.fecha_solicitud,
                se.fecha_respuesta,
                se.observaciones,
                u.nomusuario as usuario,
                CASE 
                    WHEN se.estado = 'APROBADA' THEN e.id_empresa
                    ELSE NULL
                END as id_empresa
            FROM solicitud_empresa se
            INNER JOIN usuario u ON se.id_usuario = u.id_usuario
            LEFT JOIN empresa e ON se.ruc = e.ruc
            ORDER BY se.fecha_solicitud DESC
        """
        
        cursor.execute(sql)
        resultados = cursor.fetchall()
        
        empresas = []
        for row in resultados:
            empresa = {
                'id_solicitud': row['id_solicitud'],
                'id_empresa': row.get('id_empresa'),
                'id_usuario': row['id_usuario'],
                'ruc': row['ruc'],
                'razon_social': row['razon_social'],
                'nombre_comercial': row['nombre_comercial'],
                'descripcion': row['descripcion'],
                'telefono': row['telefono'],
                'email': row['email'],
                'direccion': row['direccion'],
                'usuario': row['usuario'],
                'estado': row['estado'] == 'APROBADA',
                'fecha_solicitud': str(row['fecha_solicitud']),
                'observaciones': row.get('observaciones', '')
            }
            empresas.append(empresa)
        
        cursor.close()
        con.close()
        
        return jsonify({'status': True, 'data': empresas}), 200
            
    except Exception as e:
        print(f"Error al listar empresas: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': False, 'data': [], 'message': f'Error: {str(e)}'}), 500


@ws_empresa.route('/empresas/aprobar/<int:id_solicitud>', methods=['PATCH'])
def aprobar_empresa(id_solicitud):
    """Aprobar solicitud: crear empresa y asignar rol"""
    try:
        con = Conexion().open
        cursor = con.cursor()
        
        cursor.execute("""
            SELECT fn_solicitud_empresa_aprobar(%s, %s) as resultado
        """, [id_solicitud, 'Solicitud aprobada por administrador'])
        
        resultado_dict = cursor.fetchone()
        resultado = resultado_dict['resultado'] if resultado_dict else -1
        
        con.commit()
        cursor.close()
        con.close()
        
        if resultado == -1:
            return jsonify({'status': False, 'message': 'Error al aprobar la solicitud'}), 400
        
        return jsonify({
            'status': True,
            'message': '✅ Empresa aprobada correctamente',
            'id_empresa': resultado
        }), 200
            
    except Exception as e:
        print(f"Error al aprobar empresa: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': False, 'message': f'Error: {str(e)}'}), 500


@ws_empresa.route('/empresas/rechazar/<int:id_solicitud>', methods=['DELETE'])
def rechazar_empresa(id_solicitud):
    """Rechazar solicitud de empresa"""
    try:
        con = Conexion().open
        cursor = con.cursor()
        
        cursor.execute("""
            SELECT fn_solicitud_empresa_rechazar(%s, %s) as resultado
        """, [id_solicitud, 'Solicitud rechazada por administrador'])
        
        resultado_dict = cursor.fetchone()
        resultado = resultado_dict['resultado'] if resultado_dict else -1
        
        con.commit()
        cursor.close()
        con.close()
        
        if resultado == -1:
            return jsonify({'status': False, 'message': 'Error al rechazar la solicitud'}), 400
        
        return jsonify({'status': True, 'message': '✅ Solicitud rechazada correctamente'}), 200
            
    except Exception as e:
        print(f"Error al rechazar empresa: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': False, 'message': f'Error: {str(e)}'}), 500


@ws_empresa.route('/empresas/obtener/<int:id_solicitud>', methods=['GET'])
def obtener_detalle_empresa(id_solicitud):
    """Obtener detalle de una solicitud"""
    try:
        con = Conexion().open
        cursor = con.cursor()
        
        cursor.execute("""
            SELECT fn_solicitud_empresa_obtener(%s) as resultado
        """, [id_solicitud])
        
        resultado_dict = cursor.fetchone()
        resultado = resultado_dict['resultado'] if resultado_dict else None
        
        cursor.close()
        con.close()
        
        if not resultado:
            return jsonify({'status': False, 'data': None, 'message': 'Solicitud no encontrada'}), 404
        
        return jsonify({'status': True, 'data': resultado}), 200
            
    except Exception as e:
        print(f"Error al obtener detalle: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': False, 'data': None, 'message': f'Error: {str(e)}'}), 500


@ws_empresa.route('/empresas/obtener-por-usuario/<int:id_empresa>', methods=['GET'])
def obtener_empresa_por_usuario(id_empresa):
    """Obtener datos completos de empresa por ID"""
    try:
        con = Conexion().open
        cursor = con.cursor()
        
        cursor.execute("""
            SELECT 
                e.id_empresa, 
                e.ruc, 
                e.razon_social, 
                e.nombre_comercial,
                e.descripcion,
                e.sitio_web,
                e.telefono,
                e.email,
                e.direccion,
                e.img_logo,
                e.img_banner,
                e.id_dist,
                d.nombre as distrito,
                p.nombre as provincia,
                dep.nombre as departamento,
                p.id_prov,
                dep.id_dep
            FROM empresa e
            LEFT JOIN distrito d ON e.id_dist = d.id_dist
            LEFT JOIN provincia p ON d.id_prov = p.id_prov
            LEFT JOIN departamento dep ON p.id_dep = dep.id_dep
            WHERE e.id_empresa = %s AND e.estado = TRUE
        """, [id_empresa])
        
        empresa = cursor.fetchone()
        cursor.close()
        con.close()
        
        if not empresa:
            return jsonify({'status': False, 'data': None, 'message': 'Empresa no encontrada'}), 404
        
        return jsonify({'status': True, 'data': empresa}), 200
    except Exception as e:
        return jsonify({'status': False, 'message': f'Error: {str(e)}'}), 500


@ws_empresa.route('/empresas/modificar/<int:id_empresa>', methods=['PUT'])
def modificar_empresa(id_empresa):
    """Modificar datos de empresa con logo y banner"""
    try:
        print("=" * 60)
        print(f"🔄 MODIFICANDO EMPRESA ID: {id_empresa}")
        print("=" * 60)
        
        # Obtener datos del form-data
        ruc = request.form.get('ruc')
        razon_social = request.form.get('razon_social')
        nombre_comercial = request.form.get('nombre_comercial')
        descripcion = request.form.get('descripcion', '')
        sitio_web = request.form.get('sitio_web', '')
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        id_dist = request.form.get('id_dist')
        direccion = request.form.get('direccion')
        
        # Validar campos obligatorios
        if not all([ruc, razon_social, nombre_comercial, telefono, email, id_dist, direccion]):
            return jsonify({'status': False, 'message': 'Faltan campos obligatorios'}), 400
        
        # Procesar LOGO
        img_logo = None
        if 'img_logo' in request.files:
            file_logo = request.files['img_logo']
            if file_logo and file_logo.filename and allowed_file(file_logo.filename):
                # Generar nombre único con timestamp
                timestamp = int(time.time() * 1000)
                extension = file_logo.filename.rsplit('.', 1)[1].lower()
                filename_logo = f"{timestamp}_logo.{extension}"
                
                # Guardar en subcarpeta logos/
                filepath_logo = os.path.join(UPLOAD_FOLDER_LOGOS, filename_logo)
                file_logo.save(filepath_logo)
                img_logo = filename_logo
                
                print(f"✅ LOGO GUARDADO: {filepath_logo}")
        
        # Procesar BANNER
        img_banner = None
        if 'img_banner' in request.files:
            file_banner = request.files['img_banner']
            if file_banner and file_banner.filename and allowed_file(file_banner.filename):
                # Generar nombre único con timestamp
                timestamp = int(time.time() * 1000)
                extension = file_banner.filename.rsplit('.', 1)[1].lower()
                filename_banner = f"{timestamp}_banner.{extension}"
                
                # Guardar en subcarpeta banners/
                filepath_banner = os.path.join(UPLOAD_FOLDER_BANNERS, filename_banner)
                file_banner.save(filepath_banner)
                img_banner = filename_banner
                
                print(f"✅ BANNER GUARDADO: {filepath_banner}")
        
        # Actualizar empresa en BD
        con = Conexion().open
        cursor = con.cursor()
        
        # Construir SQL dinámicamente
        updates = [
            "ruc = %s",
            "razon_social = %s",
            "nombre_comercial = %s",
            "descripcion = %s",
            "sitio_web = %s",
            "telefono = %s",
            "email = %s",
            "id_dist = %s",
            "direccion = %s"
        ]
        params = [ruc, razon_social, nombre_comercial, descripcion, sitio_web, 
                  telefono, email, int(id_dist), direccion]
        
        # Agregar logo si existe
        if img_logo:
            updates.append("img_logo = %s")
            params.append(img_logo)
        
        # Agregar banner si existe
        if img_banner:
            updates.append("img_banner = %s")
            params.append(img_banner)
        
        params.append(id_empresa)
        
        sql = f"""
            UPDATE empresa 
            SET {', '.join(updates)}
            WHERE id_empresa = %s
        """
        
        print(f"📝 SQL: {sql}")
        print(f"📊 PARAMS: {params}")
        
        cursor.execute(sql, params)
        con.commit()
        cursor.close()
        con.close()
        
        print("=" * 60)
        print("✅ EMPRESA MODIFICADA EXITOSAMENTE")
        print("=" * 60)
        
        return jsonify({
            'status': True, 
            'message': '✅ Empresa modificada correctamente',
            'data': {
                'img_logo': img_logo,
                'img_banner': img_banner
            }
        }), 200
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': False, 'message': f'Error: {str(e)}'}), 500