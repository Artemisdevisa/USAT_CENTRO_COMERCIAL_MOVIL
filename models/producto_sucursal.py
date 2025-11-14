from conexionBD import Conexion
from flask import request


class ProductoSucursal:
    def __init__(self):
        pass
    
    def listar_productos(self):
        """Lista productos con su primera talla y primer color"""
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
                ORDER BY ps.id_prod_sucursal, pc.talla, pc.id_prod_color
            """
            
            cursor.execute(sql)
            resultados = cursor.fetchall()
            
            # ✅ DETECTAR CLIENTE
            user_agent = request.headers.get('User-Agent', '').lower()
            is_android = 'okhttp' in user_agent or 'android' in user_agent
            base_url = "http://10.0.2.2:3007" if is_android else ""
            
            productos = []
            for row in resultados:
                url_img = row['url_img'] if row['url_img'] else ''
                
                # ✅ CONSTRUIR URL COMPLETA SOLO PARA ANDROID
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
            
            return True, productos
                
        except Exception as e:
            return False, f"Error al listar productos: {str(e)}"
        
    def obtener_detalle_producto(self, id_prod_sucursal):
        """Obtiene detalle completo de un producto con todas sus tallas y colores"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Información básica del producto
            sql_producto = """
                SELECT 
                    ps.id_prod_sucursal,
                    ps.id_categoria,
                    ps.nombre,
                    ps.material,
                    ps.genero,
                    m.nombre as marca,
                    c.nombre as categoria
                FROM producto_sucursal ps
                LEFT JOIN marca m ON ps.id_marca = m.id_marca
                LEFT JOIN categoria_producto c ON ps.id_categoria = c.id_categoria
                WHERE ps.id_prod_sucursal = %s AND ps.estado = TRUE
            """
            cursor.execute(sql_producto, (id_prod_sucursal,))
            producto = cursor.fetchone()
            
            if not producto:
                cursor.close()
                con.close()
                return False, "Producto no encontrado"
            
            # Obtener todas las variantes (talla + color)
            sql_variantes = """
                SELECT 
                    pc.id_prod_color,
                    pc.talla,
                    pc.precio,
                    pc.stock,
                    pc.url_img,
                    col.id_color,
                    col.nombre as color
                FROM producto_color pc
                INNER JOIN color col ON pc.id_color = col.id_color
                WHERE pc.id_prod_sucursal = %s AND pc.estado = TRUE
                ORDER BY pc.talla, col.nombre
            """
            cursor.execute(sql_variantes, (id_prod_sucursal,))
            variantes = cursor.fetchall()
            
            # Agrupar por color y talla
            colores = {}
            tallas = set()
            
            for var in variantes:
                color_nombre = var['color']
                talla = var['talla']
                tallas.add(talla)
                
                if color_nombre not in colores:
                    colores[color_nombre] = {
                        'id_color': var['id_color'],
                        'nombre': color_nombre,
                        'tallas': {}
                    }
                
                colores[color_nombre]['tallas'][talla] = {
                    'id_prod_color': var['id_prod_color'],
                    'precio': float(var['precio']),
                    'stock': var['stock'],
                    'url_img': var['url_img'] if var['url_img'] else ''
                }
            
            resultado = {
                'id_prod_sucursal': producto['id_prod_sucursal'],
                'id_categoria': producto['id_categoria'],
                'nombre': producto['nombre'],
                'material': producto['material'] if producto['material'] else '',
                'genero': producto['genero'] if producto['genero'] else 'Sin definir',
                'marca': producto['marca'] if producto['marca'] else '',
                'categoria': producto['categoria'] if producto['categoria'] else '',
                'colores': list(colores.values()),
                'tallas_disponibles': sorted(list(tallas))
            }
            
            cursor.close()
            con.close()
            
            return True, resultado
                
        except Exception as e:
            return False, f"Error al obtener detalle: {str(e)}"
    
    def listar_todos(self):
        """Lista TODOS los productos (activos e inactivos) con información completa para el dashboard"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    ps.id_prod_sucursal,
                    ps.id_sucursal,
                    s.nombre as nombre_sucursal,
                    ps.id_temporada,
                    t.nombre as nombre_temporada,
                    ps.id_marca,
                    m.nombre as nombre_marca,
                    ps.id_categoria,
                    c.nombre as nombre_categoria,
                    ps.id_tipo_modelo,
                    tm.nombre as nombre_tipo_modelo,
                    tp.nombre as nombre_tipo_producto,
                    ps.nombre,
                    ps.material,
                    ps.genero,
                    ps.estado
                FROM producto_sucursal ps
                INNER JOIN sucursal s ON ps.id_sucursal = s.id_sucursal
                INNER JOIN temporada t ON ps.id_temporada = t.id_temporada
                INNER JOIN marca m ON ps.id_marca = m.id_marca
                INNER JOIN categoria_producto c ON ps.id_categoria = c.id_categoria
                INNER JOIN tipo_modelo_producto tm ON ps.id_tipo_modelo = tm.id_tipo_modelo
                INNER JOIN tipo_producto tp ON tm.id_tipo_prod = tp.id_tipo_prod
                ORDER BY ps.id_prod_sucursal DESC
            """
            
            cursor.execute(sql)
            resultado = cursor.fetchall()
            
            cursor.close()
            con.close()
            
            if resultado:
                productos = []
                for row in resultado:
                    productos.append({
                        'id_prod_sucursal': row['id_prod_sucursal'],
                        'id_sucursal': row['id_sucursal'],
                        'nombre_sucursal': row['nombre_sucursal'],
                        'id_temporada': row['id_temporada'],
                        'nombre_temporada': row['nombre_temporada'],
                        'id_marca': row['id_marca'],
                        'nombre_marca': row['nombre_marca'],
                        'id_categoria': row['id_categoria'],
                        'nombre_categoria': row['nombre_categoria'],
                        'id_tipo_modelo': row['id_tipo_modelo'],
                        'nombre_tipo_modelo': row['nombre_tipo_modelo'],
                        'nombre_tipo_producto': row['nombre_tipo_producto'],
                        'nombre': row['nombre'],
                        'material': row['material'],
                        'genero': row['genero'],
                        'estado': row['estado']
                    })
                return True, productos
            else:
                return True, []
                
        except Exception as e:
            return False, f"Error al listar productos: {str(e)}"
    
    def obtener_por_id(self, id_prod_sucursal):
        """Obtener un producto por su ID (para edición)"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    ps.id_prod_sucursal,
                    ps.id_sucursal,
                    ps.id_temporada,
                    ps.id_marca,
                    ps.id_categoria,
                    ps.id_tipo_modelo,
                    ps.nombre,
                    ps.material,
                    ps.genero,
                    ps.estado
                FROM producto_sucursal ps
                WHERE ps.id_prod_sucursal = %s
            """
            
            cursor.execute(sql, [id_prod_sucursal])
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            if resultado:
                return True, {
                    'id_prod_sucursal': resultado['id_prod_sucursal'],
                    'id_sucursal': resultado['id_sucursal'],
                    'id_temporada': resultado['id_temporada'],
                    'id_marca': resultado['id_marca'],
                    'id_categoria': resultado['id_categoria'],
                    'id_tipo_modelo': resultado['id_tipo_modelo'],
                    'nombre': resultado['nombre'],
                    'material': resultado['material'],
                    'genero': resultado['genero'],
                    'estado': resultado['estado']
                }
            else:
                return False, 'Producto no encontrado'
                
        except Exception as e:
            return False, f"Error al obtener producto: {str(e)}"
    
    def crear(self, id_sucursal, id_temporada, id_marca, id_categoria, id_tipo_modelo, nombre, material, genero):
        """Crear un nuevo producto usando la función de PostgreSQL"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Llamar a la función fn_producto_sucursal_crear
            sql = "SELECT fn_producto_sucursal_crear(%s, %s, %s, %s, %s, %s, %s, %s) as resultado"
            cursor.execute(sql, [id_sucursal, id_temporada, id_marca, id_categoria, id_tipo_modelo, nombre, material, genero])
            
            resultado = cursor.fetchone()
            id_prod_sucursal = resultado['resultado']
            
            con.commit()
            cursor.close()
            con.close()
            
            if id_prod_sucursal and id_prod_sucursal > 0:
                return True, id_prod_sucursal
            else:
                return False, 'No se pudo crear el producto. Verifique que todos los datos sean válidos.'
                
        except Exception as e:
            return False, f"Error al crear producto: {str(e)}"
    
    def modificar(self, id_prod_sucursal, id_sucursal, id_temporada, id_marca, id_categoria, id_tipo_modelo, nombre, material, genero):
        """Modificar un producto"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Verificar que existe
            sql_check = "SELECT COUNT(*) as total FROM producto_sucursal WHERE id_prod_sucursal = %s"
            cursor.execute(sql_check, [id_prod_sucursal])
            existe = cursor.fetchone()
            
            if existe['total'] == 0:
                cursor.close()
                con.close()
                return False, 'Producto no encontrado'
            
            # Validaciones
            if not nombre or nombre.strip() == '':
                cursor.close()
                con.close()
                return False, 'El nombre del producto es requerido'
            
            # Validar que existan las relaciones
            sql_validar = """
                SELECT 
                    (SELECT COUNT(*) FROM sucursal WHERE id_sucursal = %s AND estado = TRUE) as sucursal_existe,
                    (SELECT COUNT(*) FROM temporada WHERE id_temporada = %s AND estado = TRUE) as temporada_existe,
                    (SELECT COUNT(*) FROM marca WHERE id_marca = %s AND estado = TRUE) as marca_existe,
                    (SELECT COUNT(*) FROM categoria_producto WHERE id_categoria = %s AND estado = TRUE) as categoria_existe,
                    (SELECT COUNT(*) FROM tipo_modelo_producto WHERE id_tipo_modelo = %s AND estado = TRUE) as tipo_modelo_existe
            """
            cursor.execute(sql_validar, [id_sucursal, id_temporada, id_marca, id_categoria, id_tipo_modelo])
            validacion = cursor.fetchone()
            
            if validacion['sucursal_existe'] == 0:
                cursor.close()
                con.close()
                return False, 'La sucursal seleccionada no existe o está inactiva'
            
            if validacion['temporada_existe'] == 0:
                cursor.close()
                con.close()
                return False, 'La temporada seleccionada no existe o está inactiva'
            
            if validacion['marca_existe'] == 0:
                cursor.close()
                con.close()
                return False, 'La marca seleccionada no existe o está inactiva'
            
            if validacion['categoria_existe'] == 0:
                cursor.close()
                con.close()
                return False, 'La categoría seleccionada no existe o está inactiva'
            
            if validacion['tipo_modelo_existe'] == 0:
                cursor.close()
                con.close()
                return False, 'El modelo seleccionado no existe o está inactivo'
            
            # Actualizar
            sql_update = """
                UPDATE producto_sucursal
                SET id_sucursal = %s,
                    id_temporada = %s,
                    id_marca = %s,
                    id_categoria = %s,
                    id_tipo_modelo = %s,
                    nombre = %s,
                    material = %s,
                    genero = %s
                WHERE id_prod_sucursal = %s
            """
            cursor.execute(sql_update, [id_sucursal, id_temporada, id_marca, id_categoria, id_tipo_modelo, nombre.strip(), material, genero, id_prod_sucursal])
            
            con.commit()
            cursor.close()
            con.close()
            
            return True, 'Producto modificado correctamente'
                
        except Exception as e:
            return False, f"Error al modificar producto: {str(e)}"
    
    def cambiar_estado(self, id_prod_sucursal):
        """Cambiar el estado de un producto (activar/desactivar)"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Obtener estado actual
            sql_get = "SELECT estado FROM producto_sucursal WHERE id_prod_sucursal = %s"
            cursor.execute(sql_get, [id_prod_sucursal])
            resultado = cursor.fetchone()
            
            if not resultado:
                cursor.close()
                con.close()
                return False, 'Producto no encontrado'
            
            # Cambiar al estado contrario
            nuevo_estado = not resultado['estado']
            sql_update = "UPDATE producto_sucursal SET estado = %s WHERE id_prod_sucursal = %s"
            cursor.execute(sql_update, [nuevo_estado, id_prod_sucursal])
            
            con.commit()
            cursor.close()
            con.close()
            
            return True, 'Estado cambiado correctamente'
                
        except Exception as e:
            return False, f"Error al cambiar estado: {str(e)}"
    
    def eliminar_fisico(self, id_prod_sucursal):
        """Eliminar FÍSICAMENTE un producto (DELETE permanente)"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Verificar que existe
            sql_check_exists = "SELECT COUNT(*) as total FROM producto_sucursal WHERE id_prod_sucursal = %s"
            cursor.execute(sql_check_exists, [id_prod_sucursal])
            existe = cursor.fetchone()
            
            if existe['total'] == 0:
                cursor.close()
                con.close()
                return False, 'Producto no encontrado'
            
            # Verificar que no tenga colores/tallas asociados
            sql_check_colores = """
                SELECT COUNT(*) as total
                FROM producto_color
                WHERE id_prod_sucursal = %s
            """
            cursor.execute(sql_check_colores, [id_prod_sucursal])
            resultado = cursor.fetchone()
            
            if resultado['total'] > 0:
                cursor.close()
                con.close()
                return False, f'No se puede eliminar porque tiene {resultado["total"]} color(es)/talla(s) asociado(s)'
            
            # Eliminar físicamente (DELETE)
            sql_delete = "DELETE FROM producto_sucursal WHERE id_prod_sucursal = %s"
            cursor.execute(sql_delete, [id_prod_sucursal])
            
            con.commit()
            cursor.close()
            con.close()
            
            return True, 'Producto eliminado permanentemente de la base de datos'
                
        except Exception as e:
            return False, f"Error al eliminar producto: {str(e)}"
    
    def contar_colores(self, id_prod_sucursal):
        """Contar TODOS los colores/tallas asociados a un producto"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT COUNT(*) as total
                FROM producto_color
                WHERE id_prod_sucursal = %s
            """
            
            cursor.execute(sql, [id_prod_sucursal])
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            return resultado['total'] if resultado else 0
                
        except Exception as e:
            return 0
    
    # ============================================
    # MÉTODOS AUXILIARES PARA SELECTS
    # ============================================
    
    def listar_sucursales_activas(self):
        """Listar sucursales activas para select"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT id_sucursal, nombre
                FROM sucursal
                WHERE estado = TRUE
                ORDER BY nombre
            """
            
            cursor.execute(sql)
            resultado = cursor.fetchall()
            
            cursor.close()
            con.close()
            
            if resultado:
                sucursales = []
                for row in resultado:
                    sucursales.append({
                        'id_sucursal': row['id_sucursal'],
                        'nombre': row['nombre']
                    })
                return True, sucursales
            else:
                return True, []
                
        except Exception as e:
            return False, f"Error al listar sucursales: {str(e)}"
    
    def listar_temporadas_activas(self):
        """Listar temporadas activas para select"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT id_temporada, nombre
                FROM temporada
                WHERE estado = TRUE
                ORDER BY nombre
            """
            
            cursor.execute(sql)
            resultado = cursor.fetchall()
            
            cursor.close()
            con.close()
            
            if resultado:
                temporadas = []
                for row in resultado:
                    temporadas.append({
                        'id_temporada': row['id_temporada'],
                        'nombre': row['nombre']
                    })
                return True, temporadas
            else:
                return True, []
                
        except Exception as e:
            return False, f"Error al listar temporadas: {str(e)}"
    
    def listar_marcas_activas(self):
        """Listar marcas activas para select"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT id_marca, nombre
                FROM marca
                WHERE estado = TRUE
                ORDER BY nombre
            """
            
            cursor.execute(sql)
            resultado = cursor.fetchall()
            
            cursor.close()
            con.close()
            
            if resultado:
                marcas = []
                for row in resultado:
                    marcas.append({
                        'id_marca': row['id_marca'],
                        'nombre': row['nombre']
                    })
                return True, marcas
            else:
                return True, []
                
        except Exception as e:
            return False, f"Error al listar marcas: {str(e)}"
    
    def listar_categorias_activas(self):
        """Listar categorías activas para select"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT id_categoria, nombre
                FROM categoria_producto
                WHERE estado = TRUE
                ORDER BY nombre
            """
            
            cursor.execute(sql)
            resultado = cursor.fetchall()
            
            cursor.close()
            con.close()
            
            if resultado:
                categorias = []
                for row in resultado:
                    categorias.append({
                        'id_categoria': row['id_categoria'],
                        'nombre': row['nombre']
                    })
                return True, categorias
            else:
                return True, []
                
        except Exception as e:
            return False, f"Error al listar categorías: {str(e)}"
    
    def listar_modelos_activos(self):
        """Listar modelos activos para select"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    tm.id_tipo_modelo,
                    tm.nombre,
                    tp.nombre as tipo_producto
                FROM tipo_modelo_producto tm
                INNER JOIN tipo_producto tp ON tm.id_tipo_prod = tp.id_tipo_prod
                WHERE tm.estado = TRUE
                ORDER BY tp.nombre, tm.nombre
            """
            
            cursor.execute(sql)
            resultado = cursor.fetchall()
            
            cursor.close()
            con.close()
            
            if resultado:
                modelos = []
                for row in resultado:
                    modelos.append({
                        'id_tipo_modelo': row['id_tipo_modelo'],
                        'nombre': row['nombre'],
                        'tipo_producto': row['tipo_producto']
                    })
                return True, modelos
            else:
                return True, []
                
        except Exception as e:
            return False, f"Error al listar modelos: {str(e)}"






















