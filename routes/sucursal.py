from flask import Blueprint, jsonify, request
from models.sucursal import Sucursal
from conexionBD import Conexion
from werkzeug.utils import secure_filename
import cloudinary.uploader
import os

ws_sucursal = Blueprint('ws_sucursal', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Verificar si el archivo tiene una extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def subir_a_cloudinary(file, folder):
    """
    Subir archivo a Cloudinary y retornar URL pública
    
    Args:
        file: Archivo de Flask (request.files)
        folder: Carpeta en Cloudinary (ej: 'sucursales/logos')
    
    Returns:
        str: URL pública de Cloudinary o None si falla
    """
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

@ws_sucursal.route('/sucursales/listar-por-empresa/<int:id_empresa>', methods=['GET'])
def listar_por_empresa(id_empresa):
    """
    ---
    tags:
      - Sucursales
    summary: Listar sucursales por empresa
    description: Obtiene todas las sucursales asociadas a una empresa específica
    parameters:
      - name: id_empresa
        in: path
        type: integer
        required: true
        description: ID de la empresa
    responses:
      200:
        description: Sucursales obtenidas correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            data:
              type: array
              items:
                type: object
                properties:
                  id_sucursal:
                    type: integer
                  nombre:
                    type: string
                  direccion:
                    type: string
                  telefono:
                    type: string
                  img_logo:
                    type: string
                  img_banner:
                    type: string
                  latitud:
                    type: number
                  longitud:
                    type: number
                  distrito:
                    type: string
                  estado:
                    type: string
      500:
        description: Error en el servidor
    """
    try:
        con = Conexion().open
        cursor = con.cursor()
        
        cursor.execute("""
            SELECT 
                s.id_sucursal, 
                s.nombre, 
                s.direccion, 
                s.telefono, 
                s.img_logo, 
                s.img_banner,
                s.latitud,
                s.longitud,
                d.nombre as distrito, 
                s.estado, 
                s.id_dist
            FROM sucursal s
            LEFT JOIN distrito d ON s.id_dist = d.id_dist
            WHERE s.id_empresa = %s
            ORDER BY s.nombre
        """, [id_empresa])
        
        sucursales_raw = cursor.fetchall()
        
        # ✅ CONVERTIR estado booleano a texto
        sucursales = []
        for row in sucursales_raw:
            sucursal = dict(row)
            sucursal['estado'] = "Abierto" if row['estado'] else "Cerrado"
            sucursales.append(sucursal)
        
        cursor.close()
        con.close()
        
        return jsonify({'status': True, 'data': sucursales}), 200
    except Exception as e:
        return jsonify({'status': False, 'message': f'Error: {str(e)}'}), 500

@ws_sucursal.route('/sucursales/crear', methods=['POST'])
def crear_sucursal():
    """
    ---
    tags:
      - Sucursales
    summary: Crear nueva sucursal
    description: Crea una nueva sucursal con imágenes cargadas a Cloudinary
    parameters:
      - name: id_empresa
        in: formData
        type: integer
        required: true
        description: ID de la empresa
      - name: nombre
        in: formData
        type: string
        required: true
        description: Nombre de la sucursal
      - name: id_dist
        in: formData
        type: integer
        required: true
        description: ID del distrito
      - name: direccion
        in: formData
        type: string
        required: true
        description: Dirección completa
      - name: telefono
        in: formData
        type: string
        required: true
        description: Número de teléfono
      - name: latitud
        in: formData
        type: number
        required: true
        description: Latitud geográfica
      - name: longitud
        in: formData
        type: number
        required: true
        description: Longitud geográfica
      - name: img_logo
        in: formData
        type: file
        description: Archivo de logo (PNG, JPG, GIF, WebP)
      - name: img_banner
        in: formData
        type: file
        description: Archivo de banner (PNG, JPG, GIF, WebP)
    responses:
      201:
        description: Sucursal creada correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
            id_sucursal:
              type: integer
            img_logo:
              type: string
            img_banner:
              type: string
      400:
        description: Faltan campos obligatorios
      500:
        description: Error en el servidor
    """
    try:
        # Obtener datos del formulario
        id_empresa = request.form.get('id_empresa')
        nombre = request.form.get('nombre')
        id_dist = request.form.get('id_dist')
        direccion = request.form.get('direccion')
        telefono = request.form.get('telefono')
        latitud = request.form.get('latitud')
        longitud = request.form.get('longitud')
        
        print("=" * 60)
        print("📝 CREAR SUCURSAL")
        print("=" * 60)
        print(f"   Nombre: {nombre}")
        print(f"   Dirección: {direccion}")
        print(f"   Coordenadas: {latitud}, {longitud}")
        
        if not all([id_empresa, nombre, id_dist, direccion, telefono, latitud, longitud]):
            return jsonify({'status': False, 'message': 'Faltan campos obligatorios'}), 400
        
        # ✅ SUBIR IMÁGENES A CLOUDINARY
        img_logo_url = None
        img_banner_url = None
        
        if 'img_logo' in request.files:
            file = request.files['img_logo']
            if file and file.filename and allowed_file(file.filename):
                print(f"📸 Logo detectado: {file.filename}")
                img_logo_url = subir_a_cloudinary(file, 'sucursales/logos')
        
        if 'img_banner' in request.files:
            file = request.files['img_banner']
            if file and file.filename and allowed_file(file.filename):
                print(f"🖼️ Banner detectado: {file.filename}")
                img_banner_url = subir_a_cloudinary(file, 'sucursales/banners')
        
        # Crear sucursal en BD
        con = Conexion().open
        cursor = con.cursor()
        
        cursor.execute("""
            SELECT fn_sucursal_crear(%s, %s, %s, %s, %s, %s, %s, %s, %s) as resultado
        """, [
            int(id_empresa), 
            nombre, 
            int(id_dist), 
            direccion, 
            telefono, 
            img_logo_url,      # URL de Cloudinary
            img_banner_url,    # URL de Cloudinary
            float(latitud), 
            float(longitud)
        ])
        
        resultado = cursor.fetchone()['resultado']
        con.commit()
        cursor.close()
        con.close()
        
        if resultado > 0:
            print(f"✅ Sucursal creada con ID: {resultado}")
            print("=" * 60)
            return jsonify({
                'status': True, 
                'message': 'Sucursal creada exitosamente', 
                'id_sucursal': resultado,
                'img_logo': img_logo_url,
                'img_banner': img_banner_url
            }), 201
        else:
            print(f"❌ Error al crear sucursal")
            print("=" * 60)
            return jsonify({'status': False, 'message': 'Error al crear sucursal'}), 400
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        return jsonify({'status': False, 'message': f'Error: {str(e)}'}), 500

@ws_sucursal.route('/sucursales/listar', methods=['GET'])
def listar_sucursales():
    """
    ---
    tags:
      - Sucursales
    summary: Listar sucursales activas
    description: Obtiene lista de sucursales activas con filtro opcional por empresa
    parameters:
      - name: id_empresa
        in: query
        type: integer
        description: ID de la empresa para filtrar (opcional)
    responses:
      200:
        description: Sucursales listadas correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
            data:
              type: array
              items:
                type: object
                properties:
                  id_sucursal:
                    type: integer
                  nombre:
                    type: string
                  direccion:
                    type: string
                  telefono:
                    type: string
                  img_logo:
                    type: string
                  img_banner:
                    type: string
                  latitud:
                    type: string
                  longitud:
                    type: string
                  empresa:
                    type: string
                  distrito:
                    type: string
                  estado:
                    type: string
      500:
        description: Error en el servidor
    """
    try:
        # ✅ OBTENER id_empresa DEL QUERY PARAM
        id_empresa = request.args.get('id_empresa', type=int)
        
        con = Conexion().open
        cursor = con.cursor()
        
        sql = """
            SELECT 
                s.id_sucursal,
                s.nombre,
                s.direccion,
                s.telefono,
                s.img_logo,
                s.img_banner,
                s.latitud,
                s.longitud,
                e.nombre_comercial as empresa,
                d.nombre as distrito,
                s.estado
            FROM sucursal s
            LEFT JOIN empresa e ON s.id_empresa = e.id_empresa
            LEFT JOIN distrito d ON s.id_dist = d.id_dist
            WHERE s.estado = TRUE
        """
        
        # ✅ FILTRAR POR EMPRESA SI SE PROPORCIONA
        if id_empresa:
            sql += " AND s.id_empresa = %s"
            cursor.execute(sql + " ORDER BY s.nombre", [id_empresa])
        else:
            cursor.execute(sql + " ORDER BY s.nombre")
        
        resultados = cursor.fetchall()
        
        sucursales = []
        for row in resultados:
            sucursal = {
                "id_sucursal": row['id_sucursal'],
                "nombre": row['nombre'],
                "direccion": row['direccion'],
                "telefono": row['telefono'],
                "img_logo": row['img_logo'] or '',
                "img_banner": row['img_banner'] or '',
                "latitud": str(row['latitud']) if row['latitud'] else None,
                "longitud": str(row['longitud']) if row['longitud'] else None,
                "empresa": row['empresa'] or '',
                "distrito": row['distrito'] or '',
                # ✅ CORRECCIÓN: Convertir booleano a texto legible
                "estado": "Abierto" if row['estado'] else "Cerrado"
            }
            sucursales.append(sucursal)
        
        cursor.close()
        con.close()
        
        return jsonify({
            'status': True,
            'data': sucursales,
            'message': 'Sucursales listadas correctamente'
        }), 200
            
    except Exception as e:
        return jsonify({
            'status': False,
            'data': None,
            'message': f'Error en el servidor: {str(e)}'
        }), 500

@ws_sucursal.route('/sucursales/detalle/<int:id_sucursal>', methods=['GET'])
def obtener_detalle_sucursal(id_sucursal):
    """
    ---
    tags:
      - Sucursales
    summary: Obtener detalle completo de sucursal
    description: Obtiene información completa de una sucursal incluyendo horarios de atención
    parameters:
      - name: id_sucursal
        in: path
        type: integer
        required: true
        description: ID de la sucursal
    responses:
      200:
        description: Detalle obtenido correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            data:
              type: object
      404:
        description: Sucursal no encontrada
      500:
        description: Error en el servidor
    """
    try:
        print("=" * 60)
        print(f"📥 DETALLE SUCURSAL - ID: {id_sucursal}")
        print("=" * 60)
        
        sucursal_model = Sucursal()
        exito, resultado = sucursal_model.obtener_detalle_sucursal(id_sucursal)
        
        if exito:
            print(f"✅ Detalle obtenido exitosamente")
            print(f"   Nombre: {resultado.get('nombre', 'N/A')}")
            print(f"   Horarios: {len(resultado.get('horarios', []))}")
            print("=" * 60)
            
            return jsonify({
                'status': True,
                'data': resultado
            }), 200
        else:
            print(f"❌ Error al obtener detalle: {resultado}")
            print("=" * 60)
            return jsonify({
                'status': False,
                'data': None,
                'message': resultado
            }), 404
            
    except Exception as e:
        print(f"❌ Excepción en detalle sucursal: {str(e)}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        return jsonify({
            'status': False,
            'data': None,
            'message': f'Error: {str(e)}'
        }), 500

@ws_sucursal.route('/sucursales/obtener/<int:id>', methods=['GET'])
def obtener_sucursal(id):
    """
    ---
    tags:
      - Sucursales
    summary: Obtener datos completos de sucursal
    description: Obtiene información completa de una sucursal incluyendo datos de ubicación geográfica y división territorial
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID de la sucursal
    responses:
      200:
        description: Sucursal obtenida correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            data:
              type: object
      404:
        description: Sucursal no encontrada
      500:
        description: Error en el servidor
    """
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
        
        sucursal_raw = cursor.fetchone()
        cursor.close()
        con.close()
        
        if sucursal_raw:
            # ✅ CONVERTIR estado booleano a texto
            sucursal = dict(sucursal_raw)
            sucursal['estado'] = "Abierto" if sucursal_raw['estado'] else "Cerrado"
            return jsonify({'status': True, 'data': sucursal}), 200
        else:
            return jsonify({'status': False, 'message': 'Sucursal no encontrada'}), 404
            
    except Exception as e:
        return jsonify({'status': False, 'message': str(e)}), 500

@ws_sucursal.route('/sucursales/modificar/<int:id>', methods=['PUT'])
def modificar_sucursal(id):
    """
    ---
    tags:
      - Sucursales
    summary: Modificar sucursal existente
    description: Actualiza los datos de una sucursal incluyendo imágenes a través de Cloudinary
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID de la sucursal
      - name: id_empresa
        in: formData
        type: integer
        required: true
        description: ID de la empresa
      - name: nombre
        in: formData
        type: string
        required: true
        description: Nombre de la sucursal
      - name: id_dist
        in: formData
        type: integer
        required: true
        description: ID del distrito
      - name: direccion
        in: formData
        type: string
        required: true
        description: Dirección completa
      - name: telefono
        in: formData
        type: string
        required: true
        description: Número de teléfono
      - name: latitud
        in: formData
        type: number
        required: true
        description: Latitud geográfica
      - name: longitud
        in: formData
        type: number
        required: true
        description: Longitud geográfica
      - name: img_logo
        in: formData
        type: file
        description: Nuevo archivo de logo (PNG, JPG, GIF, WebP)
      - name: img_banner
        in: formData
        type: file
        description: Nuevo archivo de banner (PNG, JPG, GIF, WebP)
    responses:
      200:
        description: Sucursal modificada correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
      400:
        description: Faltan campos obligatorios o error en los datos
      500:
        description: Error en el servidor
    """
    try:
        id_empresa = request.form.get('id_empresa')
        nombre = request.form.get('nombre')
        id_dist = request.form.get('id_dist')
        direccion = request.form.get('direccion')
        telefono = request.form.get('telefono')
        latitud = request.form.get('latitud')
        longitud = request.form.get('longitud')
        
        print("=" * 60)
        print(f"📝 MODIFICAR SUCURSAL - ID: {id}")
        print("=" * 60)
        print(f"   Nombre: {nombre}")
        print(f"   Dirección: {direccion}")
        
        if not all([id_empresa, nombre, id_dist, direccion, telefono, latitud, longitud]):
            return jsonify({'status': False, 'message': 'Faltan campos obligatorios'}), 400
        
        # Obtener URLs actuales
        con = Conexion().open
        cursor = con.cursor()
        cursor.execute("SELECT img_logo, img_banner FROM sucursal WHERE id_sucursal = %s", [id])
        current = cursor.fetchone()
        
        img_logo_url = current['img_logo'] if current else None
        img_banner_url = current['img_banner'] if current else None
        
        # ✅ SUBIR NUEVAS IMÁGENES SI EXISTEN
        if 'img_logo' in request.files:
            file = request.files['img_logo']
            if file and file.filename and allowed_file(file.filename):
                print(f"📸 Nuevo logo detectado: {file.filename}")
                nueva_url = subir_a_cloudinary(file, 'sucursales/logos')
                if nueva_url:
                    img_logo_url = nueva_url
        
        if 'img_banner' in request.files:
            file = request.files['img_banner']
            if file and file.filename and allowed_file(file.filename):
                print(f"🖼️ Nuevo banner detectado: {file.filename}")
                nueva_url = subir_a_cloudinary(file, 'sucursales/banners')
                if nueva_url:
                    img_banner_url = nueva_url
        
        cursor.execute("""
            SELECT fn_sucursal_modificar(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) as resultado
        """, [
            id, 
            int(id_empresa), 
            nombre, 
            int(id_dist), 
            direccion, 
            telefono, 
            img_logo_url, 
            img_banner_url, 
            float(latitud), 
            float(longitud)
        ])
        
        resultado = cursor.fetchone()['resultado']
        con.commit()
        cursor.close()
        con.close()
        
        if resultado == 0:
            print(f"✅ Sucursal modificada correctamente")
            print("=" * 60)
        else:
            print(f"❌ Error al modificar sucursal")
            print("=" * 60)
        
        return jsonify({
            'status': resultado == 0, 
            'message': 'Sucursal modificada correctamente' if resultado == 0 else 'Error al modificar'
        }), 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        return jsonify({'status': False, 'message': str(e)}), 500

@ws_sucursal.route('/sucursales/cambiar-estado/<int:id>', methods=['PATCH'])
def cambiar_estado(id):
    """
    ---
    tags:
      - Sucursales
    summary: Cambiar estado de sucursal
    description: Cambia el estado de una sucursal entre activo e inactivo
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID de la sucursal
    responses:
      200:
        description: Estado cambiado correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
      500:
        description: Error en el servidor
    """
    try:
        con = Conexion().open
        cursor = con.cursor()
        cursor.execute("UPDATE sucursal SET estado = NOT estado WHERE id_sucursal = %s", [id])
        con.commit()
        cursor.close()
        con.close()
        
        return jsonify({'status': True, 'message': 'Estado cambiado correctamente'}), 200
    except Exception as e:
        return jsonify({'status': False, 'message': str(e)}), 500

@ws_sucursal.route('/sucursales/eliminar/<int:id>', methods=['DELETE'])
def eliminar_sucursal(id):
    """
    ---
    tags:
      - Sucursales
    summary: Eliminar sucursal lógicamente
    description: Marca una sucursal como eliminada (elimina lógicamente) sin borrar de la BD
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID de la sucursal
    responses:
      200:
        description: Sucursal eliminada correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
      400:
        description: No se puede eliminar la sucursal
      500:
        description: Error en el servidor
    """
    try:
        con = Conexion().open
        cursor = con.cursor()
        
        cursor.execute("SELECT fn_sucursal_eliminar(%s) as resultado", [id])
        resultado = cursor.fetchone()['resultado']
        
        con.commit()
        cursor.close()
        con.close()
        
        if resultado == 0:
            return jsonify({'status': True, 'message': 'Sucursal eliminada correctamente'}), 200
        else:
            return jsonify({'status': False, 'message': 'No se puede eliminar la sucursal'}), 400
    except Exception as e:
        return jsonify({'status': False, 'message': f'Error: {str(e)}'}), 500

@ws_sucursal.route('/sucursales/eliminar-fisico/<int:id>', methods=['DELETE'])
def eliminar_fisico(id):
    """
    ---
    tags:
      - Sucursales
    summary: Eliminar sucursal permanentemente
    description: Elimina una sucursal de forma permanente de la base de datos (DELETE FÍSICO)
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID de la sucursal
    responses:
      200:
        description: Sucursal eliminada permanentemente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
      500:
        description: Error en el servidor
    """
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