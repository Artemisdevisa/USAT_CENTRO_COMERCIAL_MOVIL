from flask import Blueprint, jsonify, request
from conexionBD import Conexion
from werkzeug.utils import secure_filename
import cloudinary.uploader

ws_empresa = Blueprint('ws_empresa', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Verificar extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def subir_a_cloudinary(file, folder):
    """Subir archivo a Cloudinary"""
    try:
        if not file:
            return None
        
        print(f"📤 Subiendo a Cloudinary: {file.filename} → {folder}")
        
        resultado = cloudinary.uploader.upload(
            file,
            folder=f"centro_comercial/{folder}",
            resource_type="auto",
            overwrite=True,
            invalidate=True
        )
        
        url = resultado['secure_url']
        print(f"✅ URL Cloudinary: {url}")
        return url
        
    except Exception as e:
        print(f"❌ Error Cloudinary: {str(e)}")
        return None

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
    """Modificar datos de empresa con logo y banner en Cloudinary"""
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
        
        # Obtener URLs actuales
        con = Conexion().open
        cursor = con.cursor()
        cursor.execute("SELECT img_logo, img_banner FROM empresa WHERE id_empresa = %s", [id_empresa])
        current = cursor.fetchone()
        
        img_logo_url = current['img_logo'] if current else None
        img_banner_url = current['img_banner'] if current else None
        
        # ✅ SUBIR NUEVO LOGO SI EXISTE
        if 'img_logo' in request.files:
            file = request.files['img_logo']
            if file and file.filename and allowed_file(file.filename):
                print(f"📸 Nuevo logo detectado: {file.filename}")
                nueva_url = subir_a_cloudinary(file, 'empresas/logos')
                if nueva_url:
                    img_logo_url = nueva_url
        
        # ✅ SUBIR NUEVO BANNER SI EXISTE
        if 'img_banner' in request.files:
            file = request.files['img_banner']
            if file and file.filename and allowed_file(file.filename):
                print(f"🖼️ Nuevo banner detectado: {file.filename}")
                nueva_url = subir_a_cloudinary(file, 'empresas/banners')
                if nueva_url:
                    img_banner_url = nueva_url
        
        # Actualizar empresa en BD
        sql = """
            UPDATE empresa 
            SET ruc = %s,
                razon_social = %s,
                nombre_comercial = %s,
                descripcion = %s,
                sitio_web = %s,
                telefono = %s,
                email = %s,
                id_dist = %s,
                direccion = %s,
                img_logo = %s,
                img_banner = %s
            WHERE id_empresa = %s
        """
        
        params = [ruc, razon_social, nombre_comercial, descripcion, sitio_web, 
                  telefono, email, int(id_dist), direccion, img_logo_url, img_banner_url, id_empresa]
        
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
                'img_logo': img_logo_url,
                'img_banner': img_banner_url
            }
        }), 200
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': False, 'message': f'Error: {str(e)}'}), 500