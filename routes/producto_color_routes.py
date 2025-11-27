from flask import Blueprint, jsonify, request
from conexionBD import Conexion
from models.producto_color import ProductoColor
import cloudinary.uploader

ws_producto_color = Blueprint('ws_producto_color', __name__)
producto_color = ProductoColor()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Verificar extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def subir_a_cloudinary(file, folder):
    """Subir imagen a Cloudinary"""
    try:
        if not file:
            return None
        
        print(f"📤 Subiendo producto a Cloudinary: {file.filename}")
        
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

@ws_producto_color.route('/productos-color/listar', methods=['GET'])
def listar_productos_color():
    """
    Listar productos-color con filtro opcional por empresa
    ---
    tags:
      - Productos Color
    parameters:
      - name: id_empresa
        in: query
        required: false
        type: integer
        description: ID de la empresa para filtrar productos-color
    responses:
      200:
        description: Lista de productos-color obtenida correctamente
      500:
        description: Error en el servidor
    """
    try:
        # ✅ OBTENER id_empresa DEL QUERY PARAM
        id_empresa = request.args.get('id_empresa', type=int)
        
        print(f"📡 Listando productos-color | id_empresa: {id_empresa}")
        
        exito, resultado = producto_color.listar_todos(id_empresa)
        
        if exito:
            print(f"✅ {len(resultado)} productos-color encontrados")
            return jsonify({
                'status': True,
                'message': 'Productos-color obtenidos correctamente',
                'data': resultado
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': resultado,
                'data': []
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}',
            'data': []
        }), 500


@ws_producto_color.route('/productos-color/obtener/<int:id_prod_color>', methods=['GET'])
def obtener_producto_color(id_prod_color):
    """
    Obtener un producto-color específico por ID
    ---
    tags:
      - Productos Color
    parameters:
      - name: id_prod_color
        in: path
        required: true
        type: integer
        description: ID del producto-color (variante)
    responses:
      200:
        description: Producto-color obtenido correctamente
      404:
        description: Producto-color no encontrado
      500:
        description: Error en el servidor
    """
    try:
        exito, resultado = producto_color.obtener_por_id(id_prod_color)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Producto-color obtenido correctamente',
                'data': resultado
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': resultado,
                'data': None
            }), 404
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}',
            'data': None
        }), 500


@ws_producto_color.route('/productos-color/crear', methods=['POST'])
def crear_producto_color():
    """
    Crear una nueva variante (color/talla) con imagen en Cloudinary
    ---
    tags:
      - Productos Color
    consumes:
      - multipart/form-data
    parameters:
      - name: id_prod_sucursal
        in: formData
        required: true
        type: integer
        description: ID del producto-sucursal base
      - name: id_color
        in: formData
        required: true
        type: integer
        description: ID del color
      - name: talla
        in: formData
        required: true
        type: string
        description: Talla de la variante
      - name: precio
        in: formData
        required: true
        type: number
        format: float
        description: Precio de la variante
      - name: stock
        in: formData
        required: true
        type: integer
        description: Stock disponible de la variante
      - name: url_img
        in: formData
        required: true
        type: file
        description: Imagen de la variante a subir a Cloudinary
    responses:
      201:
        description: Variante creada correctamente
      400:
        description: Datos inválidos o incompletos
      500:
        description: Error en el servidor
    """
    try:
        print("=" * 60)
        print("📝 CREAR PRODUCTO-COLOR (VARIANTE)")
        print("=" * 60)
        
        # Obtener datos del formulario
        id_prod_sucursal = request.form.get('id_prod_sucursal')
        id_color = request.form.get('id_color')
        talla = request.form.get('talla')
        precio = request.form.get('precio')
        stock = request.form.get('stock')
        
        print(f"   Producto Sucursal: {id_prod_sucursal}")
        print(f"   Color: {id_color}")
        print(f"   Talla: {talla}")
        print(f"   Precio: {precio}")
        print(f"   Stock: {stock}")
        
        # Validar campos requeridos
        if not all([id_prod_sucursal, id_color, talla, precio, stock]):
            return jsonify({
                'status': False,
                'message': 'Faltan campos obligatorios'
            }), 400
        
        # ✅ SUBIR IMAGEN A CLOUDINARY
        url_img = None
        
        if 'url_img' in request.files:
            file = request.files['url_img']
            if file and file.filename and allowed_file(file.filename):
                print(f"📸 Imagen detectada: {file.filename}")
                url_img = subir_a_cloudinary(file, 'productos')
        
        if not url_img:
            return jsonify({
                'status': False,
                'message': 'La imagen del producto es obligatoria'
            }), 400
        
        # Crear variante en BD
        exito, mensaje = producto_color.crear(
            int(id_prod_sucursal),
            int(id_color),
            talla,
            float(precio),
            int(stock),
            url_img  # URL de Cloudinary
        )
        
        if exito:
            print(f"✅ Variante creada exitosamente")
            print("=" * 60)
            return jsonify({
                'status': True,
                'message': mensaje,
                'data': {'url_img': url_img}
            }), 201
        else:
            print(f"❌ Error al crear variante: {mensaje}")
            print("=" * 60)
            return jsonify({
                'status': False,
                'message': mensaje
            }), 400
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


@ws_producto_color.route('/productos-color/modificar/<int:id_prod_color>', methods=['PUT'])
def modificar_producto_color(id_prod_color):
    """
    Modificar una variante existente con opción de nueva imagen en Cloudinary
    ---
    tags:
      - Productos Color
    consumes:
      - multipart/form-data
    parameters:
      - name: id_prod_color
        in: path
        required: true
        type: integer
        description: ID del producto-color (variante) a modificar
      - name: id_prod_sucursal
        in: formData
        required: true
        type: integer
        description: ID del producto-sucursal base
      - name: id_color
        in: formData
        required: true
        type: integer
        description: ID del color
      - name: talla
        in: formData
        required: true
        type: string
        description: Talla de la variante
      - name: precio
        in: formData
        required: true
        type: number
        format: float
        description: Precio de la variante
      - name: stock
        in: formData
        required: true
        type: integer
        description: Stock disponible de la variante
      - name: url_img
        in: formData
        required: false
        type: file
        description: Nueva imagen de la variante (opcional)
    responses:
      200:
        description: Variante modificada correctamente
      400:
        description: Datos inválidos o incompletos
      500:
        description: Error en el servidor
    """
    try:
        print("=" * 60)
        print(f"🔄 MODIFICAR PRODUCTO-COLOR ID: {id_prod_color}")
        print("=" * 60)
        
        # Obtener datos del formulario
        id_prod_sucursal = request.form.get('id_prod_sucursal')
        id_color = request.form.get('id_color')
        talla = request.form.get('talla')
        precio = request.form.get('precio')
        stock = request.form.get('stock')
        
        print(f"   Producto Sucursal: {id_prod_sucursal}")
        print(f"   Color: {id_color}")
        print(f"   Talla: {talla}")
        print(f"   Precio: {precio}")
        print(f"   Stock: {stock}")
        
        # Validar campos requeridos
        if not all([id_prod_sucursal, id_color, talla, precio, stock]):
            return jsonify({
                'status': False,
                'message': 'Faltan campos obligatorios'
            }), 400
        
        # Obtener URL actual
        con = Conexion().open
        cursor = con.cursor()
        cursor.execute("SELECT url_img FROM producto_color WHERE id_prod_color = %s", [id_prod_color])
        current = cursor.fetchone()
        cursor.close()
        con.close()
        
        url_img = current['url_img'] if current else None
        
        # ✅ SUBIR NUEVA IMAGEN SI EXISTE
        if 'url_img' in request.files:
            file = request.files['url_img']
            if file and file.filename and allowed_file(file.filename):
                print(f"📸 Nueva imagen detectada: {file.filename}")
                nueva_url = subir_a_cloudinary(file, 'productos')
                if nueva_url:
                    url_img = nueva_url
        
        if not url_img:
            return jsonify({
                'status': False,
                'message': 'La imagen del producto es obligatoria'
            }), 400
        
        # Modificar variante
        exito, mensaje = producto_color.modificar(
            id_prod_color,
            int(id_prod_sucursal),
            int(id_color),
            talla,
            float(precio),
            int(stock),
            url_img  # URL de Cloudinary (actual o nueva)
        )
        
        if exito:
            print(f"✅ Variante modificada correctamente")
            print("=" * 60)
            return jsonify({
                'status': True,
                'message': mensaje,
                'data': {'url_img': url_img}
            }), 200
        else:
            print(f"❌ Error al modificar: {mensaje}")
            print("=" * 60)
            return jsonify({
                'status': False,
                'message': mensaje
            }), 400
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


@ws_producto_color.route('/productos-color/cambiar-estado/<int:id_prod_color>', methods=['PATCH'])
def cambiar_estado_producto_color(id_prod_color):
    """
    Cambiar estado de una variante (activar/desactivar)
    ---
    tags:
      - Productos Color
    parameters:
      - name: id_prod_color
        in: path
        required: true
        type: integer
        description: ID del producto-color (variante)
    responses:
      200:
        description: Estado cambiado correctamente
      400:
        description: Error al cambiar el estado
      500:
        description: Error en el servidor
    """
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
    """
    Eliminar FÍSICAMENTE una variante (DELETE permanente)
    ---
    tags:
      - Productos Color
    parameters:
      - name: id_prod_color
        in: path
        required: true
        type: integer
        description: ID del producto-color (variante) a eliminar
    responses:
      200:
        description: Variante eliminada correctamente
      400:
        description: Error al eliminar la variante
      500:
        description: Error en el servidor
    """
    try:
        exito, mensaje = producto_color.eliminar_fisico(id_prod_color)
        
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


@ws_producto_color.route('/productos-color/por-producto/<int:id_prod_sucursal>', methods=['GET'])
def listar_por_producto(id_prod_sucursal):
    """
    Listar todas las variantes de un producto específico
    ---
    tags:
      - Productos Color
    parameters:
      - name: id_prod_sucursal
        in: path
        required: true
        type: integer
        description: ID del producto-sucursal
    responses:
      200:
        description: Variantes obtenidas correctamente
      500:
        description: Error en el servidor
    """
    try:
        exito, resultado = producto_color.listar_por_producto(id_prod_sucursal)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Variantes obtenidas correctamente',
                'data': resultado
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': resultado,
                'data': []
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}',
            'data': []
        }), 500


# ============================================
# ENDPOINTS AUXILIARES PARA SELECTS
# ============================================

@ws_producto_color.route('/productos-color/productos-activos', methods=['GET'])
def listar_productos_activos():
    """
    Listar productos activos para el select con filtro por empresa
    ---
    tags:
      - Productos Color
    parameters:
      - name: id_empresa
        in: query
        required: false
        type: integer
        description: ID de la empresa para filtrar productos activos
    responses:
      200:
        description: Productos obtenidos correctamente
      500:
        description: Error en el servidor
    """
    try:
        # ✅ OBTENER id_empresa DEL QUERY PARAM
        id_empresa = request.args.get('id_empresa', type=int)
        
        exito, resultado = producto_color.listar_productos_activos(id_empresa)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Productos obtenidos correctamente',
                'data': resultado
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': resultado,
                'data': []
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}',
            'data': []
        }), 500


@ws_producto_color.route('/productos-color/colores-activos', methods=['GET'])
def listar_colores_activos():
    """
    Listar colores activos para el select
    ---
    tags:
      - Productos Color
    responses:
      200:
        description: Colores obtenidos correctamente
      500:
        description: Error en el servidor
    """
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
                'message': resultado,
                'data': []
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}',
            'data': []
        }), 500
