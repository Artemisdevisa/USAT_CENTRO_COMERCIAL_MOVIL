from flask import Blueprint, jsonify, request
from models.categoria_producto import CategoriaProducto
import cloudinary.uploader

ws_categoria_producto = Blueprint('ws_categoria_producto', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def subir_a_cloudinary(file, folder):
    """Subir imagen a Cloudinary"""
    try:
        if not file:
            return None
        
        print(f"📤 Subiendo categoría a Cloudinary: {file.filename}")
        
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

# ============================================
# ENDPOINTS EXISTENTES (Frontend público)
# ============================================

@ws_categoria_producto.route('/categorias/listar', methods=['GET'])
def listar_categorias():
    """
    Listar categorías activas para el frontend público
    ---
    tags:
      - Categorías
    responses:
      200:
        description: Lista de categorías activas obtenida correctamente
      500:
        description: Error interno del servidor
    """
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
    """
    Listar productos por categoría para el frontend público
    ---
    tags:
      - Categorías
    parameters:
      - name: id_categoria
        in: path
        required: true
        type: integer
        description: ID de la categoría
    responses:
      200:
        description: Productos obtenidos correctamente
      500:
        description: Error interno del servidor
    """
    try:
        categoria_producto = CategoriaProducto()
        resultado, productos = categoria_producto.listar_productos_por_categoria(id_categoria)
        
        if resultado:
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
    """
    Listar TODAS las categorías (activas e inactivas) para el dashboard
    ---
    tags:
      - Categorías (Admin)
    responses:
      200:
        description: Categorías obtenidas correctamente
      500:
        description: Error interno del servidor
    """
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
    """
    Obtener una categoría específica por ID
    ---
    tags:
      - Categorías (Admin)
    parameters:
      - name: id_categoria
        in: path
        required: true
        type: integer
        description: ID de la categoría
    responses:
      200:
        description: Categoría obtenida correctamente
      404:
        description: Categoría no encontrada
      500:
        description: Error interno del servidor
    """
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
    """
    Crear una nueva categoría con Cloudinary
    ---
    tags:
      - Categorías (Admin)
    consumes:
      - multipart/form-data
    parameters:
      - name: nombre
        in: formData
        type: string
        required: true
        description: Nombre de la categoría
      - name: imagen
        in: formData
        type: file
        required: false
        description: Imagen de la categoría a subir a Cloudinary
    responses:
      201:
        description: Categoría creada correctamente
      400:
        description: Error de validación o datos incompletos
      500:
        description: Error interno del servidor
    """
    try:
        # Obtener datos del formulario
        nombre = request.form.get('nombre', '').strip()
        
        if not nombre:
            return jsonify({
                'status': False,
                'message': 'El nombre de la categoría es requerido'
            }), 400
        
        # ✅ SUBIR IMAGEN A CLOUDINARY
        img_url = None
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and file.filename and allowed_file(file.filename):
                img_url = subir_a_cloudinary(file, 'categorias')
        
        # Crear categoría
        categoria = CategoriaProducto()
        exito, resultado = categoria.crear(nombre, img_url)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Categoría creado correctamente',
                'data': {'id_categoria': resultado, 'img': img_url}
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


@ws_categoria_producto.route('/categorias/modificar/<int:id_categoria>', methods=['PUT'])
def modificar_categoria(id_categoria):
    """
    Modificar una categoría con Cloudinary
    ---
    tags:
      - Categorías (Admin)
    consumes:
      - multipart/form-data
    parameters:
      - name: id_categoria
        in: path
        required: true
        type: integer
        description: ID de la categoría a modificar
      - name: nombre
        in: formData
        type: string
        required: true
        description: Nuevo nombre de la categoría
      - name: imagen
        in: formData
        type: file
        required: false
        description: Nueva imagen de la categoría
    responses:
      200:
        description: Categoría modificada correctamente
      400:
        description: Error de validación o de negocio
      500:
        description: Error interno del servidor
    """
    try:
        # Obtener datos del formulario
        nombre = request.form.get('nombre', '').strip()
        
        if not nombre:
            return jsonify({
                'status': False,
                'message': 'El nombre de la categoría es requerido'
            }), 400
        
        # Obtener URL actual
        from conexionBD import Conexion
        con = Conexion().open
        cursor = con.cursor()
        cursor.execute("SELECT img FROM categoria_producto WHERE id_categoria = %s", [id_categoria])
        current = cursor.fetchone()
        cursor.close()
        con.close()
        
        img_url = current['img'] if current else None
        
        # ✅ SUBIR NUEVA IMAGEN SI EXISTE
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and file.filename and allowed_file(file.filename):
                nueva_url = subir_a_cloudinary(file, 'categorias')
                if nueva_url:
                    img_url = nueva_url
        
        # Modificar categoría
        categoria = CategoriaProducto()
        exito, mensaje = categoria.modificar(id_categoria, nombre, img_url)
        
        if exito:
            return jsonify({
                'status': True,
                'message': mensaje,
                'data': {'img': img_url}
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


@ws_categoria_producto.route('/categorias/cambiar-estado/<int:id_categoria>', methods=['PATCH'])
def cambiar_estado_categoria(id_categoria):
    """
    Cambiar estado de una categoría (activar/desactivar)
    ---
    tags:
      - Categorías (Admin)
    parameters:
      - name: id_categoria
        in: path
        required: true
        type: integer
        description: ID de la categoría cuyo estado será cambiado
    responses:
      200:
        description: Estado de la categoría actualizado correctamente
      400:
        description: No fue posible cambiar el estado
      500:
        description: Error interno del servidor
    """
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
    """
    Eliminar FÍSICAMENTE una categoría (DELETE permanente)
    ---
    tags:
      - Categorías (Admin)
    parameters:
      - name: id_categoria
        in: path
        required: true
        type: integer
        description: ID de la categoría a eliminar
    responses:
      200:
        description: Categoría eliminada correctamente
      400:
        description: No se pudo eliminar la categoría (tiene productos asociados u otro error)
      500:
        description: Error interno del servidor
    """
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
    """
    Obtener estadísticas de categorías y productos
    ---
    tags:
      - Categorías (Admin)
    responses:
      200:
        description: Estadísticas obtenidas correctamente
      500:
        description: Error interno del servidor
    """
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
    

@ws_categoria_producto.route('/categorias/listar-activas', methods=['GET'])
def listar_categorias_activas():
    """
    Listar solo categorías ACTIVAS para selectores en formularios
    ---
    tags:
      - Categorías (Admin)
    responses:
      200:
        description: Lista de categorías activas obtenida correctamente
      500:
        description: Error interno del servidor
    """
    try:
        categoria = CategoriaProducto()
        exito, resultado = categoria.listar_categorias()  # Usa el método existente
        
        if exito:
            # Transformar a formato simple para el select
            categorias_select = []
            for cat in resultado:
                categorias_select.append({
                    'id_categoria': cat['idCategoriaProducto'],
                    'nombre': cat['nombreCategoria']
                })
            
            return jsonify({
                'status': True,
                'data': categorias_select
            }), 200
        else:
            return jsonify({
                'status': False,
                'data': [],
                'message': resultado
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'data': [],
            'message': f'Error interno: {str(e)}'
        }), 500
