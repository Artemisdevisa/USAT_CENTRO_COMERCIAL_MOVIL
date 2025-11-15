from flask import Blueprint, jsonify, request
import os
from werkzeug.utils import secure_filename
from models.producto_color import ProductoColor
from conexionBD import Conexion

ws_producto_color = Blueprint('ws_producto_color', __name__)
producto_color = ProductoColor()

# Configuración de uploads
UPLOAD_FOLDER = 'uploads/fotos/productos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@ws_producto_color.route('/productos-color/listar', methods=['GET'])
def listar_productos_color():
    """Listar TODOS los productos_color para administración"""
    try:
        exito, resultado = producto_color.listar_todos()
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Productos color obtenidos correctamente',
                'data': resultado
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': resultado
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


@ws_producto_color.route('/productos-color/obtener/<int:id_prod_color>', methods=['GET'])
def obtener_producto_color(id_prod_color):
    """Obtener un producto_color específico por ID para edición"""
    try:
        exito, resultado = producto_color.obtener_por_id(id_prod_color)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Producto color obtenido correctamente',
                'data': resultado
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': resultado
            }), 404
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


@ws_producto_color.route('/productos-color/crear', methods=['POST'])
def crear_producto_color():
    """Crear un nuevo producto_color con imagen"""
    try:
        # Obtener datos del formulario
        id_prod_sucursal = request.form.get('id_prod_sucursal')
        id_color = request.form.get('id_color')
        talla = request.form.get('talla', '').strip()
        precio = request.form.get('precio')
        stock = request.form.get('stock')
        
        # Validar campos requeridos
        if not all([id_prod_sucursal, id_color, talla, precio, stock]):
            return jsonify({
                'status': False,
                'message': 'Todos los campos son requeridos'
            }), 400
        
        # Convertir a tipos correctos
        try:
            id_prod_sucursal = int(id_prod_sucursal)
            id_color = int(id_color)
            precio = float(precio)
            stock = int(stock)
        except ValueError:
            return jsonify({
                'status': False,
                'message': 'Tipos de datos inválidos'
            }), 400
        
        # Validaciones de negocio
        if precio <= 0:
            return jsonify({
                'status': False,
                'message': 'El precio debe ser mayor a 0'
            }), 400
        
        if stock < 0:
            return jsonify({
                'status': False,
                'message': 'El stock no puede ser negativo'
            }), 400
        
        # Procesar imagen si existe
        url_img = None
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and file.filename != '' and allowed_file(file.filename):
                # Crear nombre único: id_prod_sucursal_color_talla.extension
                filename = secure_filename(file.filename)
                extension = filename.rsplit('.', 1)[1].lower()
                
                # Obtener nombre del producto y color para el nombre del archivo
                from conexionBD import Conexion
                con = Conexion().open
                cursor = con.cursor()
                
                sql = """
                    SELECT ps.nombre as producto, c.nombre as color
                    FROM producto_sucursal ps, color c
                    WHERE ps.id_prod_sucursal = %s AND c.id_color = %s
                """
                cursor.execute(sql, [id_prod_sucursal, id_color])
                info = cursor.fetchone()
                cursor.close()
                con.close()
                
                if info:
                    # Limpiar nombres para usar en el archivo
                    nombre_producto = info['producto'].lower().replace(' ', '_')
                    nombre_color = info['color'].lower().replace(' ', '_')
                    talla_limpia = talla.lower().replace(' ', '_')
                    
                    new_filename = f"{id_prod_sucursal}_{nombre_producto}_{nombre_color}_{talla_limpia}.{extension}"
                    
                    # Asegurar que existe el directorio
                    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                    
                    # Guardar archivo
                    filepath = os.path.join(UPLOAD_FOLDER, new_filename)
                    file.save(filepath)
                    
                    # URL para la BD (relativa)
                    url_img = f"/uploads/fotos/productos/{new_filename}"
        
        # Crear producto_color
        exito, resultado = producto_color.crear(id_prod_sucursal, id_color, talla, precio, stock, url_img)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Producto color creado correctamente',
                'data': {'id_prod_color': resultado}
            }), 201
        else:
            return jsonify({
                'status': False,
                'message': resultado
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


@ws_producto_color.route('/productos-color/modificar/<int:id_prod_color>', methods=['PUT', 'POST'])
def modificar_producto_color(id_prod_color):
    """Modificar un producto_color existente con opción de cambiar imagen"""
    try:
        # Obtener datos del formulario
        id_prod_sucursal = request.form.get('id_prod_sucursal')
        id_color = request.form.get('id_color')
        talla = request.form.get('talla', '').strip()
        precio = request.form.get('precio')
        stock = request.form.get('stock')
        url_img_actual = request.form.get('url_img_actual')  # Imagen actual
        
        # Validar campos requeridos
        if not all([id_prod_sucursal, id_color, talla, precio, stock]):
            return jsonify({
                'status': False,
                'message': 'Todos los campos son requeridos'
            }), 400
        
        # Convertir a tipos correctos
        try:
            id_prod_sucursal = int(id_prod_sucursal)
            id_color = int(id_color)
            precio = float(precio)
            stock = int(stock)
        except ValueError:
            return jsonify({
                'status': False,
                'message': 'Tipos de datos inválidos'
            }), 400
        
        # Validaciones de negocio
        if precio <= 0:
            return jsonify({
                'status': False,
                'message': 'El precio debe ser mayor a 0'
            }), 400
        
        if stock < 0:
            return jsonify({
                'status': False,
                'message': 'El stock no puede ser negativo'
            }), 400
        
        # Mantener imagen actual por defecto
        url_img = url_img_actual
        
        # Procesar nueva imagen si existe
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and file.filename != '' and allowed_file(file.filename):
                # Crear nombre único
                filename = secure_filename(file.filename)
                extension = filename.rsplit('.', 1)[1].lower()
                
                # Obtener información para nombre del archivo
                from conexionBD import Conexion
                con = Conexion().open
                cursor = con.cursor()
                
                sql = """
                    SELECT ps.nombre as producto, c.nombre as color
                    FROM producto_sucursal ps, color c
                    WHERE ps.id_prod_sucursal = %s AND c.id_color = %s
                """
                cursor.execute(sql, [id_prod_sucursal, id_color])
                info = cursor.fetchone()
                cursor.close()
                con.close()
                
                if info:
                    nombre_producto = info['producto'].lower().replace(' ', '_')
                    nombre_color = info['color'].lower().replace(' ', '_')
                    talla_limpia = talla.lower().replace(' ', '_')
                    
                    new_filename = f"{id_prod_sucursal}_{nombre_producto}_{nombre_color}_{talla_limpia}.{extension}"
                    
                    # Asegurar que existe el directorio
                    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                    
                    # Eliminar imagen anterior si existe
                    if url_img_actual:
                        old_filepath = url_img_actual.replace('/uploads/fotos/productos/', '')
                        old_full_path = os.path.join(UPLOAD_FOLDER, old_filepath)
                        if os.path.exists(old_full_path):
                            try:
                                os.remove(old_full_path)
                            except:
                                pass
                    
                    # Guardar nueva imagen
                    filepath = os.path.join(UPLOAD_FOLDER, new_filename)
                    file.save(filepath)
                    
                    url_img = f"/uploads/fotos/productos/{new_filename}"
        
        # Modificar producto_color
        exito, mensaje = producto_color.modificar(id_prod_color, id_prod_sucursal, id_color, talla, precio, stock, url_img)
        
        if exito:
            return jsonify({
                'status': True,
                'message': mensaje
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': mensaje
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


@ws_producto_color.route('/productos-color/cambiar-estado/<int:id_prod_color>', methods=['PATCH'])
def cambiar_estado_producto_color(id_prod_color):
    """Cambiar estado de un producto_color (activar/desactivar) - ELIMINACIÓN LÓGICA"""
    try:
        exito, mensaje = producto_color.cambiar_estado(id_prod_color)
        
        if exito:
            return jsonify({
                'status': True,
                'message': mensaje
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': mensaje
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


@ws_producto_color.route('/productos-color/eliminar/<int:id_prod_color>', methods=['DELETE'])
def eliminar_producto_color(id_prod_color):
    """Eliminar FÍSICAMENTE un producto_color (DELETE permanente)"""
    try:
        # Obtener URL de imagen antes de eliminar
        exito_get, data = producto_color.obtener_por_id(id_prod_color)
        url_img = data.get('url_img') if exito_get else None
        
        # Eliminar de la BD
        exito, mensaje = producto_color.eliminar_fisico(id_prod_color)
        
        if exito:
            # Eliminar imagen del servidor si existe
            if url_img:
                filepath = url_img.replace('/uploads/fotos/productos/', '')
                full_path = os.path.join(UPLOAD_FOLDER, filepath)
                if os.path.exists(full_path):
                    try:
                        os.remove(full_path)
                    except:
                        pass
            
            return jsonify({
                'status': True,
                'message': mensaje
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': mensaje
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


# ============================================
# ENDPOINTS AUXILIARES PARA SELECTS
# ============================================

@ws_producto_color.route('/productos-color/productos-activos', methods=['GET'])
def listar_productos_activos():
    """Listar productos_sucursal activos para el select"""
    try:
        exito, resultado = producto_color.listar_productos_activos()
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Productos obtenidos correctamente',
                'data': resultado
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': resultado
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


@ws_producto_color.route('/productos-color/colores-activos', methods=['GET'])
def listar_colores_activos():
    """Listar colores activos para el select"""
    try:
        exito, resultado = producto_color.listar_colores_activos()
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Colores obtenidos correctamente',
                'data': resultado
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': resultado
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500
    
@ws_producto_color.route('/productos-color/listar-por-tipo/<int:id_tipo_prod>', methods=['GET'])
def listar_por_tipo(id_tipo_prod):
    """Listar productos_color filtrados por tipo de producto"""
    try:
        con = Conexion().open
        cursor = con.cursor()
        
        # ✅ DETECTAR ENTORNO
        user_agent = request.headers.get('User-Agent', '').lower()
        is_android = 'okhttp' in user_agent or 'android' in user_agent
        
        if os.environ.get('RENDER'):
            base_url = "https://usat-comercial-api.onrender.com" if is_android else ""
        else:
            base_url = "http://10.0.2.2:3007" if is_android else ""
        
        sql = """
            SELECT DISTINCT ON (ps.id_prod_sucursal)
                ps.id_prod_sucursal,
                ps.nombre,
                ps.material,
                ps.genero,
                m.nombre as marca,
                c.nombre as categoria,
                pc.id_prod_color,
                pc.talla,
                pc.precio,
                pc.stock,
                pc.url_img,
                col.nombre as color
            FROM producto_sucursal ps
            LEFT JOIN marca m ON ps.id_marca = m.id_marca
            LEFT JOIN categoria_producto c ON ps.id_categoria = c.id_categoria
            LEFT JOIN tipo_modelo_producto tm ON ps.id_tipo_modelo = tm.id_tipo_modelo
            LEFT JOIN producto_color pc ON ps.id_prod_sucursal = pc.id_prod_sucursal AND pc.estado = TRUE
            LEFT JOIN color col ON pc.id_color = col.id_color
            WHERE ps.estado = TRUE 
              AND tm.id_tipo_prod = %s
            ORDER BY ps.id_prod_sucursal, pc.talla, pc.id_prod_color
        """
        
        cursor.execute(sql, (id_tipo_prod,))
        resultados = cursor.fetchall()
        
        productos = []
        for row in resultados:
            url_img = row['url_img'] if row['url_img'] else ''
            
            if url_img and is_android:
                if not url_img.startswith('http'):
                    if not url_img.startswith('/'):
                        url_img = '/' + url_img
                    url_img = base_url + url_img
            
            producto = {
                "id_prod_sucursal": row['id_prod_sucursal'],
                "id_prod_color": row['id_prod_color'] if row['id_prod_color'] else None,
                "nombre": row['nombre'],
                "talla": row['talla'] if row['talla'] else '',
                "material": row['material'] if row['material'] else '',
                "url_img": url_img,
                "genero": row['genero'] if row['genero'] else 'Sin definir',
                "precio": float(row['precio']) if row['precio'] else 0.0,
                "stock": row['stock'] if row['stock'] else 0,
                "marca": row['marca'] if row['marca'] else '',
                "categoria": row['categoria'] if row['categoria'] else '',
                "color": row['color'] if row['color'] else 'Sin color'
            }
            productos.append(producto)
        
        cursor.close()
        con.close()
        
        return jsonify({
            'status': True,
            'data': productos,
            'message': f'Se encontraron {len(productos)} productos'
        }), 200
            
    except Exception as e:
        return jsonify({
            'status': False,
            'data': [],
            'message': f'Error: {str(e)}'
        }), 500