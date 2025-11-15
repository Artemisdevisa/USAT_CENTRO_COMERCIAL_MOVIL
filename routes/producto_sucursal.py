from flask import Blueprint, jsonify, request  # ← IMPORTANTE: debe incluir 'request'
from conexionBD import Conexion
from models.producto_sucursal import ProductoSucursal

ws_producto_sucursal = Blueprint('ws_producto_sucursal', __name__)
producto_sucursal = ProductoSucursal()

@ws_producto_sucursal.route('/productos/listar', methods=['GET'])
def listar_productos():
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
    try:
        con = Conexion().open
        cursor = con.cursor()
        
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
            LIMIT 5
        """
        
        cursor.execute(sql, (id_categoria, id_actual))
        resultados = cursor.fetchall()
        
        productos = []
        for row in resultados:
            producto = {
                "id_prod_sucursal": row['id_prod_sucursal'],
                "id_prod_color": row['id_prod_color'] if row['id_prod_color'] else None,
                "nombre": row['nombre'],
                "talla": row['talla'] if row['talla'] else '',
                "material": row['material'] if row['material'] else '',
                "url_img": row['url_img'] if row['url_img'] else '',
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
            'message': 'Productos relacionados obtenidos'
        }), 200
            
    except Exception as e:
        return jsonify({
            'status': False,
            'data': [],
            'message': f'Error: {str(e)}'
        }), 500
    
@ws_producto_sucursal.route('/productos-sucursal/listar', methods=['GET'])
def listar_productos_admin():
    """Listar TODOS los productos para administración"""
    try:
        exito, resultado = producto_sucursal.listar_todos()
        
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
    """Obtener un producto específico por ID para edición"""
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
    """Crear un nuevo producto"""
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
    """Modificar un producto existente"""
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
    """Cambiar estado de un producto (activar/desactivar)"""
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
    """Eliminar FÍSICAMENTE un producto (DELETE permanente)"""
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
    """Obtener estadísticas de productos y sus variantes"""
    try:
        exito, productos = producto_sucursal.listar_todos()
        
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
    """Listar sucursales activas para el select"""
    try:
        exito, resultado = producto_sucursal.listar_sucursales_activas()
        
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
    """Listar temporadas activas para el select"""
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
    """Listar marcas activas para el select"""
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
    """Listar categorías activas para el select"""
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
    """Listar modelos activos para el select"""
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


# ============================================
# NOTA IMPORTANTE:
# ============================================
# Asegúrate de agregar el import de 'request' al inicio del archivo:
# from flask import Blueprint, jsonify, request
# 
# Y también el import de Conexion si lo usas en productos_relacionados:
# from conexionBD import Conexion






















