from flask import Blueprint, jsonify, request  # ← IMPORTANTE: debe incluir 'request'
from conexionBD import Conexion
from models.producto_sucursal import ProductoSucursal

ws_producto_sucursal = Blueprint('ws_producto_sucursal', __name__)
producto_sucursal = ProductoSucursal()

@ws_producto_sucursal.route('/productos/listar', methods=['GET'])
def listar_productos():
    """
    ---
    tags:
      - Productos
    summary: Listar todos los productos
    description: Obtiene una lista de todos los productos disponibles
    responses:
      200:
        description: Productos obtenidos correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            data:
              type: array
              items:
                type: object
            message:
              type: string
      500:
        description: Error interno del servidor
    """
    try:
        resultado, productos = producto_sucursal.listar_productos()
        
        if resultado:
            return jsonify({
                'status': True,
                'data': productos,
                'message': f'Se encontraron {len(productos)} productos'
            }), 200
        else:
            return jsonify({
                'status': False,
                'data': None,
                'message': productos
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'data': None,
            'message': f'Error interno: {str(e)}'
        }), 500
    

@ws_producto_sucursal.route('/productos/detalle/<int:id_prod_sucursal>', methods=['GET'])
def detalle_producto(id_prod_sucursal):
    """
    ---
    tags:
      - Productos
    summary: Obtener detalle de un producto
    description: Obtiene la información detallada de un producto específico
    parameters:
      - name: id_prod_sucursal
        in: path
        type: integer
        required: true
        description: ID del producto sucursal
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
            message:
              type: string
      404:
        description: Producto no encontrado
      500:
        description: Error interno del servidor
    """
    try:
        producto_sucursal = ProductoSucursal()
        resultado, data = producto_sucursal.obtener_detalle_producto(id_prod_sucursal)
        
        if resultado:
            return jsonify({
                'status': True,
                'data': data,
                'message': 'Detalle obtenido correctamente'
            }), 200
        else:
            return jsonify({
                'status': False,
                'data': None,
                'message': data
            }), 404
            
    except Exception as e:
        return jsonify({
            'status': False,
            'data': None,
            'message': f'Error interno: {str(e)}'
        }), 500
    
@ws_producto_sucursal.route('/productos/relacionados/<int:id_categoria>/<int:id_actual>', methods=['GET'])
def productos_relacionados(id_categoria, id_actual):
    """
    ---
    tags:
      - Productos
    summary: Obtener productos relacionados
    description: Obtiene productos de la misma categoría excluyendo el producto actual
    parameters:
      - name: id_categoria
        in: path
        type: integer
        required: true
        description: ID de la categoría
      - name: id_actual
        in: path
        type: integer
        required: true
        description: ID del producto actual a excluir
    responses:
      200:
        description: Productos relacionados obtenidos correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            data:
              type: array
              items:
                type: object
            message:
              type: string
      500:
        description: Error interno del servidor
    """
    try:
        con = Conexion().open
        cursor = con.cursor()
        
        # ✅ DETECTAR ENTORNO
        user_agent = request.headers.get('User-Agent', '').lower()
        is_android = 'okhttp' in user_agent or 'android' in user_agent
        
        import os
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
            LEFT JOIN producto_color pc ON ps.id_prod_sucursal = pc.id_prod_sucursal AND pc.estado = TRUE
            LEFT JOIN color col ON pc.id_color = col.id_color
            WHERE ps.estado = TRUE 
              AND ps.id_categoria = %s 
              AND ps.id_prod_sucursal != %s
            ORDER BY ps.id_prod_sucursal, pc.talla, pc.id_prod_color
            LIMIT 10
        """
        
        cursor.execute(sql, (id_categoria, id_actual))
        resultados = cursor.fetchall()
        
        productos = []
        for row in resultados:
            url_img = row['url_img'] if row['url_img'] else ''
            
            # ✅ AGREGAR BASE_URL PARA ANDROID
            if url_img and is_android:
                if not url_img.startswith('http'):
                    if not url_img.startswith('/'):
                        url_img = '/' + url_img
                    url_img = base_url + url_img
            
            # ✅ CRÍTICO: Enviar TODOS los aliases posibles
            producto = {
                # ✅ IDs (todos los formatos)
                "id_prod_sucursal": row['id_prod_sucursal'],
                "idProdSucursal": row['id_prod_sucursal'],      # ← AGREGAR
                "idProducto": row['id_prod_sucursal'],           # ← AGREGAR
                "id_prod_color": row['id_prod_color'] if row['id_prod_color'] else None,
                "idProdColor": row['id_prod_color'] if row['id_prod_color'] else None,  # ← AGREGAR
                
                # ✅ Nombre (todos los formatos)
                "nombre": row['nombre'],
                "nombreProducto": row['nombre'],                 # ← AGREGAR
                
                # ✅ URLs (todos los formatos)
                "url_img": url_img,
                "urlImg": url_img,                               # ← AGREGAR
                "imagen": url_img,                               # ← AGREGAR
                
                # ✅ Otros campos
                "talla": row['talla'] if row['talla'] else '',
                "material": row['material'] if row['material'] else '',
                "genero": row['genero'] if row['genero'] else 'Sin definir',
                "precio": float(row['precio']) if row['precio'] else 0.0,
                "stock": row['stock'] if row['stock'] else 0,
                "marca": row['marca'] if row['marca'] else '',
                "categoria": row['categoria'] if row['categoria'] else '',
                "nombreCategoria": row['categoria'] if row['categoria'] else '',  # ← AGREGAR
                "color": row['color'] if row['color'] else 'Sin color'
            }
            productos.append(producto)
        
        cursor.close()
        con.close()
        
        # ✅ LOG PARA DEBUGGING
        print(f"🔍 Productos relacionados encontrados: {len(productos)}")
        if productos:
            print(f"📦 Primer producto: {productos[0]}")
        
        return jsonify({
            'status': True,
            'data': productos,
            'message': f'Se encontraron {len(productos)} productos relacionados'
        }), 200
            
    except Exception as e:
        import traceback
        print(f"❌ ERROR en productos_relacionados: {str(e)}")
        traceback.print_exc()
        
        return jsonify({
            'status': False,
            'data': [],
            'message': f'Error: {str(e)}'
        }), 500
    
@ws_producto_sucursal.route('/productos-sucursal/listar', methods=['GET'])
def listar_productos_admin():
    """
    ---
    tags:
      - Administración de Productos
    summary: Listar productos con filtro por empresa
    description: Obtiene la lista de productos con filtro opcional por empresa
    parameters:
      - name: id_empresa
        in: query
        type: integer
        description: ID de la empresa para filtrar
    responses:
      200:
        description: Productos obtenidos correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
            data:
              type: array
      500:
        description: Error en el servidor
    """
    try:
        # ✅ OBTENER id_empresa DEL QUERY PARAM
        id_empresa = request.args.get('id_empresa', type=int)
        
        exito, resultado = producto_sucursal.listar_todos(id_empresa)
        
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


@ws_producto_sucursal.route('/productos-sucursal/obtener/<int:id_prod_sucursal>', methods=['GET'])
def obtener_producto_admin(id_prod_sucursal):
    """
    ---
    tags:
      - Administración de Productos
    summary: Obtener producto específico para edición
    description: Obtiene un producto específico por ID para su edición
    parameters:
      - name: id_prod_sucursal
        in: path
        type: integer
        required: true
        description: ID del producto sucursal
    responses:
      200:
        description: Producto obtenido correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
            data:
              type: object
      404:
        description: Producto no encontrado
      500:
        description: Error en el servidor
    """
    try:
        exito, resultado = producto_sucursal.obtener_por_id(id_prod_sucursal)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Producto obtenido correctamente',
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


@ws_producto_sucursal.route('/productos-sucursal/crear', methods=['POST'])
def crear_producto():
    """
    ---
    tags:
      - Administración de Productos
    summary: Crear un nuevo producto
    description: Crea un nuevo producto con los datos proporcionados
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - id_sucursal
            - id_temporada
            - id_marca
            - id_categoria
            - id_tipo_modelo
            - nombre
            - genero
          properties:
            id_sucursal:
              type: integer
            id_temporada:
              type: integer
            id_marca:
              type: integer
            id_categoria:
              type: integer
            id_tipo_modelo:
              type: integer
            nombre:
              type: string
            material:
              type: string
            genero:
              type: string
    responses:
      201:
        description: Producto creado correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
            data:
              type: object
      400:
        description: Datos inválidos
      500:
        description: Error en el servidor
    """
    try:
        data = request.get_json()
        
        # Validaciones
        if not data:
            return jsonify({
                'status': False,
                'message': 'No se recibieron datos'
            }), 400
        
        # Validar campos requeridos
        campos_requeridos = ['id_sucursal', 'id_temporada', 'id_marca', 'id_categoria', 'id_tipo_modelo', 'nombre', 'genero']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({
                    'status': False,
                    'message': f'El campo {campo} es requerido'
                }), 400
        
        id_sucursal = data.get('id_sucursal')
        id_temporada = data.get('id_temporada')
        id_marca = data.get('id_marca')
        id_categoria = data.get('id_categoria')
        id_tipo_modelo = data.get('id_tipo_modelo')
        nombre = data.get('nombre', '').strip()
        material = data.get('material', '').strip() if data.get('material') else None
        genero = data.get('genero', '').strip() if data.get('genero') else None
        
        if not nombre:
            return jsonify({
                'status': False,
                'message': 'El nombre del producto no puede estar vacío'
            }), 400
        

        # Crear producto
        exito, resultado = producto_sucursal.crear(id_sucursal, id_temporada, id_marca, id_categoria, id_tipo_modelo, nombre, material, genero)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Producto creado correctamente',
                'data': {'id_prod_sucursal': resultado}
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


@ws_producto_sucursal.route('/productos-sucursal/modificar/<int:id_prod_sucursal>', methods=['PUT'])
def modificar_producto(id_prod_sucursal):
    """
    ---
    tags:
      - Administración de Productos
    summary: Modificar un producto existente
    description: Actualiza los datos de un producto existente
    parameters:
      - name: id_prod_sucursal
        in: path
        type: integer
        required: true
        description: ID del producto sucursal
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - id_sucursal
            - id_temporada
            - id_marca
            - id_categoria
            - id_tipo_modelo
            - nombre
            - genero
          properties:
            id_sucursal:
              type: integer
            id_temporada:
              type: integer
            id_marca:
              type: integer
            id_categoria:
              type: integer
            id_tipo_modelo:
              type: integer
            nombre:
              type: string
            material:
              type: string
            genero:
              type: string
    responses:
      200:
        description: Producto modificado correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
      400:
        description: Datos inválidos
      500:
        description: Error en el servidor
    """
    try:
        data = request.get_json()
        
        # Validaciones
        if not data:
            return jsonify({
                'status': False,
                'message': 'No se recibieron datos'
            }), 400
        
        # Validar campos requeridos
        campos_requeridos = ['id_sucursal', 'id_temporada', 'id_marca', 'id_categoria', 'id_tipo_modelo', 'nombre', 'genero']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({
                    'status': False,
                    'message': f'El campo {campo} es requerido'
                }), 400
        
        id_sucursal = data.get('id_sucursal')
        id_temporada = data.get('id_temporada')
        id_marca = data.get('id_marca')
        id_categoria = data.get('id_categoria')
        id_tipo_modelo = data.get('id_tipo_modelo')
        nombre = data.get('nombre', '').strip()
        material = data.get('material', '').strip() if data.get('material') else None
        genero = data.get('genero', '').strip() if data.get('genero') else None
        
        if not nombre:
            return jsonify({
                'status': False,
                'message': 'El nombre del producto no puede estar vacío'
            }), 400

        # Modificar producto
        exito, mensaje = producto_sucursal.modificar(id_prod_sucursal, id_sucursal, id_temporada, id_marca, id_categoria, id_tipo_modelo, nombre, material, genero)
        
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


@ws_producto_sucursal.route('/productos-sucursal/cambiar-estado/<int:id_prod_sucursal>', methods=['PATCH'])
def cambiar_estado_producto(id_prod_sucursal):
    """
    ---
    tags:
      - Administración de Productos
    summary: Cambiar estado de un producto
    description: Activa o desactiva un producto (toggle de estado)
    parameters:
      - name: id_prod_sucursal
        in: path
        type: integer
        required: true
        description: ID del producto sucursal
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
      400:
        description: Error al cambiar estado
      500:
        description: Error en el servidor
    """
    try:
        exito, mensaje = producto_sucursal.cambiar_estado(id_prod_sucursal)
        
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


@ws_producto_sucursal.route('/productos-sucursal/eliminar/<int:id_prod_sucursal>', methods=['DELETE'])
def eliminar_producto(id_prod_sucursal):
    """
    ---
    tags:
      - Administración de Productos
    summary: Eliminar permanentemente un producto
    description: Elimina FÍSICAMENTE un producto de la base de datos (DELETE permanente)
    parameters:
      - name: id_prod_sucursal
        in: path
        type: integer
        required: true
        description: ID del producto sucursal
    responses:
      200:
        description: Producto eliminado correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
      400:
        description: No se puede eliminar el producto
      500:
        description: Error en el servidor
    """
    try:
        # Verificar si tiene colores/tallas asociados
        total_colores = producto_sucursal.contar_colores(id_prod_sucursal)
        
        if total_colores > 0:
            return jsonify({
                'status': False,
                'message': f'No se puede eliminar el producto porque tiene {total_colores} color(es)/talla(s) asociado(s). Primero debe eliminar las variantes.'
            }), 400
        
        # Eliminar FÍSICAMENTE (DELETE FROM)
        exito, mensaje = producto_sucursal.eliminar_fisico(id_prod_sucursal)
        
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


@ws_producto_sucursal.route('/productos-sucursal/estadisticas', methods=['GET'])
def estadisticas_productos():
    """
    ---
    tags:
      - Administración de Productos
    summary: Obtener estadísticas de productos
    description: Obtiene estadísticas con filtro opcional por empresa
    parameters:
      - name: id_empresa
        in: query
        type: integer
        description: ID de la empresa para filtrar
    responses:
      200:
        description: Estadísticas obtenidas correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
            data:
              type: array
      500:
        description: Error en el servidor
    """
    try:
        # ✅ OBTENER id_empresa DEL QUERY PARAM
        id_empresa = request.args.get('id_empresa', type=int)
        
        exito, productos = producto_sucursal.listar_todos(id_empresa)
        
        if not exito:
            return jsonify({
                'status': False,
                'message': 'Error al obtener estadísticas'
            }), 500
        
        estadisticas = []
        for p in productos:
            total_colores = producto_sucursal.contar_colores(p['id_prod_sucursal'])
            estadisticas.append({
                'id_prod_sucursal': p['id_prod_sucursal'],
                'nombre': p['nombre'],
                'nombre_sucursal': p['nombre_sucursal'],
                'nombre_marca': p['nombre_marca'],
                'nombre_categoria': p['nombre_categoria'],
                'estado': p['estado'],
                'total_variantes': total_colores
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


# ============================================
# ENDPOINTS AUXILIARES PARA SELECTS
# ============================================

@ws_producto_sucursal.route('/productos-sucursal/sucursales-activas', methods=['GET'])
def listar_sucursales_activas():
    """
    ---
    tags:
      - Auxiliares
    summary: Listar sucursales activas
    description: Obtiene lista de sucursales activas filtradas por empresa
    parameters:
      - name: id_empresa
        in: query
        type: integer
        description: ID de la empresa para filtrar
    responses:
      200:
        description: Sucursales obtenidas correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
            data:
              type: array
      500:
        description: Error en el servidor
    """
    try:
        # ✅ OBTENER id_empresa DEL QUERY PARAM
        id_empresa = request.args.get('id_empresa', type=int)
        
        exito, resultado = producto_sucursal.listar_sucursales_activas(id_empresa)
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Sucursales obtenidas correctamente',
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

@ws_producto_sucursal.route('/productos-sucursal/temporadas-activas', methods=['GET'])
def listar_temporadas_activas():
    """
    ---
    tags:
      - Auxiliares
    summary: Listar temporadas activas
    description: Obtiene lista de temporadas activas para los selects
    responses:
      200:
        description: Temporadas obtenidas correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
            data:
              type: array
      500:
        description: Error en el servidor
    """
    try:
        exito, resultado = producto_sucursal.listar_temporadas_activas()
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Temporadas obtenidas correctamente',
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


@ws_producto_sucursal.route('/productos-sucursal/marcas-activas', methods=['GET'])
def listar_marcas_activas():
    """
    ---
    tags:
      - Auxiliares
    summary: Listar marcas activas
    description: Obtiene lista de marcas activas para los selects
    responses:
      200:
        description: Marcas obtenidas correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
            data:
              type: array
      500:
        description: Error en el servidor
    """
    try:
        exito, resultado = producto_sucursal.listar_marcas_activas()
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Marcas obtenidas correctamente',
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


@ws_producto_sucursal.route('/productos-sucursal/categorias-activas', methods=['GET'])
def listar_categorias_activas():
    """
    ---
    tags:
      - Auxiliares
    summary: Listar categorías activas
    description: Obtiene lista de categorías activas para los selects
    responses:
      200:
        description: Categorías obtenidas correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
            data:
              type: array
      500:
        description: Error en el servidor
    """
    try:
        exito, resultado = producto_sucursal.listar_categorias_activas()
        
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


@ws_producto_sucursal.route('/productos-sucursal/modelos-activos', methods=['GET'])
def listar_modelos_activos():
    """
    ---
    tags:
      - Auxiliares
    summary: Listar modelos activos
    description: Obtiene lista de modelos activos para los selects
    responses:
      200:
        description: Modelos obtenidos correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            message:
              type: string
            data:
              type: array
      500:
        description: Error en el servidor
    """
    try:
        exito, resultado = producto_sucursal.listar_modelos_activos()
        
        if exito:
            return jsonify({
                'status': True,
                'message': 'Modelos obtenidos correctamente',
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
    
@ws_producto_sucursal.route('/productos/por-temporada/<int:id_temporada>', methods=['GET'])
def productos_por_temporada(id_temporada):
    """
    ---
    tags:
      - Productos
    summary: Listar productos por temporada
    description: Obtiene productos filtrados por temporada específica
    parameters:
      - name: id_temporada
        in: path
        type: integer
        required: true
        description: ID de la temporada
    responses:
      200:
        description: Productos obtenidos correctamente
        schema:
          type: object
          properties:
            status:
              type: boolean
            data:
              type: array
            message:
              type: string
      500:
        description: Error interno del servidor
    """
    try:
        con = Conexion().open
        cursor = con.cursor()
        
        # ✅ DETECTAR ENTORNO
        user_agent = request.headers.get('User-Agent', '').lower()
        is_android = 'okhttp' in user_agent or 'android' in user_agent
        
        import os
        if os.environ.get('RENDER'):
            base_url = "https://usat-comercial-api.onrender.com" if is_android else ""
        else:
            base_url = "http://10.0.2.2:3007" if is_android else ""
        
        sql = """
            SELECT DISTINCT ON (ps.id_prod_sucursal)
                ps.id_prod_sucursal,
                ps.id_temporada,
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
            LEFT JOIN producto_color pc ON ps.id_prod_sucursal = pc.id_prod_sucursal AND pc.estado = TRUE
            LEFT JOIN color col ON pc.id_color = col.id_color
            WHERE ps.estado = TRUE 
              AND ps.id_temporada = %s
            ORDER BY ps.id_prod_sucursal, pc.talla, pc.id_prod_color
        """
        
        cursor.execute(sql, (id_temporada,))
        resultados = cursor.fetchall()
        
        productos = []
        for row in resultados:
            url_img = row['url_img'] if row['url_img'] else ''
            
            # ✅ AGREGAR BASE_URL PARA ANDROID
            if url_img and is_android:
                if not url_img.startswith('http'):
                    if not url_img.startswith('/'):
                        url_img = '/' + url_img
                    url_img = base_url + url_img
            
            producto = {
                "id_prod_sucursal": row['id_prod_sucursal'],
                "idProducto": row['id_prod_sucursal'],
                "id_temporada": row['id_temporada'],
                "id_prod_color": row['id_prod_color'] if row['id_prod_color'] else None,
                "idProdColor": row['id_prod_color'] if row['id_prod_color'] else None,
                "nombre": row['nombre'],
                "nombreProducto": row['nombre'],
                "talla": row['talla'] if row['talla'] else '',
                "material": row['material'] if row['material'] else '',
                "url_img": url_img,
                "urlImg": url_img,
                "imagen": url_img,
                "genero": row['genero'] if row['genero'] else 'Sin definir',
                "precio": float(row['precio']) if row['precio'] else 0.0,
                "stock": row['stock'] if row['stock'] else 0,
                "marca": row['marca'] if row['marca'] else '',
                "categoria": row['categoria'] if row['categoria'] else '',
                "nombreCategoria": row['categoria'] if row['categoria'] else '',
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
            'message': f'Error interno: {str(e)}'
        }), 500