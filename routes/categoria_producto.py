from flask import Blueprint, jsonify, request
from models.categoria_producto import CategoriaProducto
from werkzeug.utils import secure_filename
import os

ws_categoria_producto = Blueprint('ws_categoria_producto', __name__)

# Configuración de uploads
UPLOAD_FOLDER = 'uploads/fotos/categorias'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============================================
# ENDPOINTS EXISTENTES (Frontend público)
# ============================================

@ws_categoria_producto.route('/categorias/listar', methods=['GET'])
def listar_categorias():
    """Listar categorías activas para el frontend público"""
    try:
        categoria_producto = CategoriaProducto()
        resultado, categorias = categoria_producto.listar_categorias()
        
        if resultado:
            return jsonify({
                'status': True,
                'data': categorias,
                'message': f'Se encontraron {len(categorias)} categorías'
            }), 200
        else:
            return jsonify({
                'status': False,
                'data': None,
                'message': categorias
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'data': None,
            'message': f'Error interno: {str(e)}'
        }), 500


@ws_categoria_producto.route('/productos/categoria/<int:id_categoria>', methods=['GET'])
def listar_productos_por_categoria(id_categoria):
    """Listar productos por categoría para el frontend público"""
    try:
        categoria_producto = CategoriaProducto()
        resultado, productos = categoria_producto.listar_productos_por_categoria(id_categoria)
        
        if resultado:
            # ✅ DETECTAR ENTORNO Y CLIENTE
            user_agent = request.headers.get('User-Agent', '').lower()
            is_android = 'okhttp' in user_agent or 'android' in user_agent
            
            # ✅ DETERMINAR BASE_URL SEGÚN ENTORNO
            if os.environ.get('RENDER'):
                base_url = "https://usat-comercial-api.onrender.com" if is_android else ""
            else:
                base_url = "http://10.0.2.2:3007" if is_android else ""
            
            # ✅ PROCESAR URLs DE IMÁGENES
            for producto in productos:
                url_img = producto.get('urlImg', '')
                if url_img and is_android:
                    if not url_img.startswith('http'):
                        if not url_img.startswith('/'):
                            url_img = '/' + url_img
                        producto['urlImg'] = base_url + url_img
                        producto['imagen'] = base_url + url_img
            
            return jsonify({
                'status': True,
                'data': productos,
                'message': f'Se encontraron {len(productos)} productos'
            }), 200
        else:
            return jsonify({
                'status': False,
                'data': [],
                'message': productos
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'data': [],
            'message': f'Error interno: {str(e)}'
        }), 500


# ============================================
# ENDPOINTS CRUD (Dashboard/Admin)
# ============================================

@ws_categoria_producto.route('/categorias/listar-admin', methods=['GET'])
def listar_categorias_admin():
    """Listar TODAS las categorías (activas e inactivas) para el dashboard"""
    try:
        categoria = CategoriaProducto()
        exito, resultado = categoria.listar()
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Categorías obtenidas correctamente',
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


@ws_categoria_producto.route('/categorias/obtener/<int:id_categoria>', methods=['GET'])
def obtener_categoria(id_categoria):
    """Obtener una categoría específica por ID"""
    try:
        categoria = CategoriaProducto()
        exito, resultado = categoria.obtener_por_id(id_categoria)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Categoría obtenida correctamente',
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


@ws_categoria_producto.route('/categorias/crear', methods=['POST'])
def crear_categoria():
    """Crear una nueva categoría"""
    try:
        # Obtener datos del formulario
        nombre = request.form.get('nombre', '').strip()
        
        if not nombre:
            return jsonify({
                'status': False,
                'message': 'El nombre de la categoría es requerido'
            }), 400
        
        # Manejar archivo de imagen
        img_filename = None
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and file.filename != '' and allowed_file(file.filename):
                # Generar nombre seguro
                filename = secure_filename(file.filename)
                # Agregar timestamp para evitar duplicados
                import time
                img_filename = f"{int(time.time())}_{filename}"
                
                # Guardar archivo
                filepath = os.path.join(UPLOAD_FOLDER, img_filename)
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file.save(filepath)
        
        # Crear categoría
        categoria = CategoriaProducto()
        exito, resultado = categoria.crear(nombre, img_filename)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Categoría creada correctamente',
                'data': {'id_categoria': resultado}
            }), 201
        else:
            # Si falló, eliminar imagen subida
            if img_filename:
                try:
                    os.remove(os.path.join(UPLOAD_FOLDER, img_filename))
                except:
                    pass
            
            return jsonify({
                'status': False,
                'message': resultado
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


@ws_categoria_producto.route('/categorias/modificar/<int:id_categoria>', methods=['PUT'])
def modificar_categoria(id_categoria):
    """Modificar una categoría existente"""
    try:
        # Obtener datos del formulario
        nombre = request.form.get('nombre', '').strip()
        
        if not nombre:
            return jsonify({
                'status': False,
                'message': 'El nombre de la categoría es requerido'
            }), 400
        
        # Manejar archivo de imagen
        img_filename = None
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and file.filename != '' and allowed_file(file.filename):
                # Generar nombre seguro
                filename = secure_filename(file.filename)
                import time
                img_filename = f"{int(time.time())}_{filename}"
                
                # Guardar archivo
                filepath = os.path.join(UPLOAD_FOLDER, img_filename)
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file.save(filepath)
        
        # Modificar categoría
        categoria = CategoriaProducto()
        exito, mensaje = categoria.modificar(id_categoria, nombre, img_filename)
        
        if exito:
            return jsonify({
                'status': True,
                'message': mensaje
            }), 200
        else:
            # Si falló, eliminar imagen subida
            if img_filename:
                try:
                    os.remove(os.path.join(UPLOAD_FOLDER, img_filename))
                except:
                    pass
            
            return jsonify({
                'status': False,
                'message': mensaje
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


@ws_categoria_producto.route('/categorias/cambiar-estado/<int:id_categoria>', methods=['PATCH'])
def cambiar_estado_categoria(id_categoria):
    """Cambiar estado de una categoría (activar/desactivar)"""
    try:
        categoria = CategoriaProducto()
        exito, mensaje = categoria.cambiar_estado(id_categoria)
        
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


@ws_categoria_producto.route('/categorias/eliminar/<int:id_categoria>', methods=['DELETE'])
def eliminar_categoria(id_categoria):
    """Eliminar FÍSICAMENTE una categoría (DELETE permanente)"""
    try:
        categoria = CategoriaProducto()
        
        # Verificar si tiene productos asociados
        total_productos = categoria.contar_productos(id_categoria)
        
        if total_productos > 0:
            return jsonify({
                'status': False,
                'message': f'No se puede eliminar la categoría porque tiene {total_productos} producto(s) asociado(s)'
            }), 400
        
        # Eliminar categoría físicamente
        exito, mensaje = categoria.eliminar_fisico(id_categoria)
        
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


@ws_categoria_producto.route('/categorias/estadisticas', methods=['GET'])
def estadisticas_categorias():
    """Obtener estadísticas de categorías y productos"""
    try:
        categoria = CategoriaProducto()
        exito, categorias = categoria.listar()
        
        if not exito:
            return jsonify({
                'status': False,
                'message': 'Error al obtener estadísticas'
            }), 500
        
        estadisticas = []
        for c in categorias:
            total_productos = categoria.contar_productos(c['id_categoria'])
            estadisticas.append({
                'id_categoria': c['id_categoria'],
                'nombre': c['nombre'],
                'img': c['img'],
                'estado': c['estado'],
                'total_productos': total_productos
            })
        
        return jsonify({
            'status': True,
            'message': 'Estadísticas obtenidas correctamente',
            'data': estadisticas
        }), 200
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500