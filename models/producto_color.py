from conexionBD import Conexion
from flask import request


class ProductoColor:
    def __init__(self):
        pass
    
    def listar_todos(self):
        """Lista TODOS los productos_color con URLs adaptadas al cliente"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    pc.id_prod_color,
                    pc.id_prod_sucursal,
                    ps.nombre as nombre_producto,
                    pc.id_color,
                    c.nombre as nombre_color,
                    pc.talla,
                    pc.precio,
                    pc.stock,
                    pc.url_img,
                    pc.estado,
                    m.nombre as nombre_marca,
                    cat.nombre as nombre_categoria
                FROM producto_color pc
                INNER JOIN producto_sucursal ps ON pc.id_prod_sucursal = ps.id_prod_sucursal
                INNER JOIN color c ON pc.id_color = c.id_color
                LEFT JOIN marca m ON ps.id_marca = m.id_marca
                LEFT JOIN categoria_producto cat ON ps.id_categoria = cat.id_categoria
                WHERE pc.estado = TRUE
                ORDER BY pc.id_prod_color DESC
            """
            
            cursor.execute(sql)
            resultado = cursor.fetchall()
            
            cursor.close()
            con.close()
            
            if resultado:
                productos_color = []
                
                # ✅ DETECTAR SI ES ANDROID
                user_agent = request.headers.get('User-Agent', '').lower()
                is_android = 'okhttp' in user_agent or 'android' in user_agent
                base_url = "http://10.0.2.2:3007" if is_android else ""
                
                for row in resultado:
                    url_img = row['url_img'] if row['url_img'] else ''
                    
                    # ✅ CONSTRUIR URL COMPLETA SOLO PARA ANDROID
                    if url_img and is_android:
                        if not url_img.startswith('http'):
                            if not url_img.startswith('/'):
                                url_img = '/' + url_img
                            url_img = base_url + url_img
                    
                    productos_color.append({
                        'id_prod_color': row['id_prod_color'],
                        'id_prod_sucursal': row['id_prod_sucursal'],
                        'nombre_producto': row['nombre_producto'],
                        'id_color': row['id_color'],
                        'nombre_color': row['nombre_color'],
                        'talla': row['talla'],
                        'precio': float(row['precio']) if row['precio'] else 0.0,
                        'stock': row['stock'],
                        'url_img': url_img,
                        'estado': row['estado'],
                        'nombre_marca': row['nombre_marca'] if row['nombre_marca'] else '',
                        'nombre_categoria': row['nombre_categoria'] if row['nombre_categoria'] else ''
                    })
                return True, productos_color
            else:
                return True, []
                
        except Exception as e:
            return False, f"Error al listar productos color: {str(e)}"
    
    def obtener_por_id(self, id_prod_color):
        """Obtener un producto_color por su ID (para edición)"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    pc.id_prod_color,
                    pc.id_prod_sucursal,
                    pc.id_color,
                    pc.talla,
                    pc.precio,
                    pc.stock,
                    pc.url_img,
                    pc.estado
                FROM producto_color pc
                WHERE pc.id_prod_color = %s
            """
            
            cursor.execute(sql, [id_prod_color])
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            if resultado:
                return True, {
                    'id_prod_color': resultado['id_prod_color'],
                    'id_prod_sucursal': resultado['id_prod_sucursal'],
                    'id_color': resultado['id_color'],
                    'talla': resultado['talla'],
                    'precio': float(resultado['precio']) if resultado['precio'] else 0.0,
                    'stock': resultado['stock'],
                    'url_img': resultado['url_img'],
                    'estado': resultado['estado']
                }
            else:
                return False, 'Producto color no encontrado'
                
        except Exception as e:
            return False, f"Error al obtener producto color: {str(e)}"
    
    def crear(self, id_prod_sucursal, id_color, talla, precio, stock, url_img):
        """Crear un nuevo producto_color usando la función de PostgreSQL"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Llamar a la función fn_producto_color_crear
            sql = "SELECT fn_producto_color_crear(%s, %s, %s, %s, %s, %s) as resultado"
            cursor.execute(sql, [id_prod_sucursal, id_color, talla, precio, stock, url_img])
            
            resultado = cursor.fetchone()
            id_prod_color = resultado['resultado']
            
            con.commit()
            cursor.close()
            con.close()
            
            if id_prod_color and id_prod_color > 0:
                return True, id_prod_color
            else:
                return False, 'No se pudo crear el producto color. Verifique que todos los datos sean válidos y que no exista ya esta combinación de producto, color y talla.'
                
        except Exception as e:
            return False, f"Error al crear producto color: {str(e)}"
    
    def modificar(self, id_prod_color, id_prod_sucursal, id_color, talla, precio, stock, url_img):
        """Modificar un producto_color"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Verificar que existe
            sql_check = "SELECT COUNT(*) as total FROM producto_color WHERE id_prod_color = %s"
            cursor.execute(sql_check, [id_prod_color])
            existe = cursor.fetchone()
            
            if existe['total'] == 0:
                cursor.close()
                con.close()
                return False, 'Producto color no encontrado'
            
            # Validaciones
            if not talla or talla.strip() == '':
                cursor.close()
                con.close()
                return False, 'La talla es requerida'
            
            if precio is None or precio <= 0:
                cursor.close()
                con.close()
                return False, 'El precio debe ser mayor a 0'
            
            if stock is None or stock < 0:
                cursor.close()
                con.close()
                return False, 'El stock no puede ser negativo'
            
            # Validar que existan las relaciones
            sql_validar = """
                SELECT 
                    (SELECT COUNT(*) FROM producto_sucursal WHERE id_prod_sucursal = %s AND estado = TRUE) as producto_existe,
                    (SELECT COUNT(*) FROM color WHERE id_color = %s AND estado = TRUE) as color_existe
            """
            cursor.execute(sql_validar, [id_prod_sucursal, id_color])
            validacion = cursor.fetchone()
            
            if validacion['producto_existe'] == 0:
                cursor.close()
                con.close()
                return False, 'El producto seleccionado no existe o está inactivo'
            
            if validacion['color_existe'] == 0:
                cursor.close()
                con.close()
                return False, 'El color seleccionado no existe o está inactivo'
            
            # Verificar que no exista otra variante con la misma combinación producto+color+talla
            sql_check_duplicado = """
                SELECT COUNT(*) as total 
                FROM producto_color 
                WHERE id_prod_sucursal = %s 
                  AND id_color = %s 
                  AND UPPER(talla) = UPPER(%s)
                  AND id_prod_color != %s
                  AND estado = TRUE
            """
            cursor.execute(sql_check_duplicado, [id_prod_sucursal, id_color, talla.strip(), id_prod_color])
            duplicado = cursor.fetchone()
            
            if duplicado['total'] > 0:
                cursor.close()
                con.close()
                return False, 'Ya existe una variante con esta combinación de producto, color y talla'
            
            # Actualizar
            sql_update = """
                UPDATE producto_color
                SET id_prod_sucursal = %s,
                    id_color = %s,
                    talla = %s,
                    precio = %s,
                    stock = %s,
                    url_img = %s
                WHERE id_prod_color = %s
            """
            cursor.execute(sql_update, [id_prod_sucursal, id_color, talla.strip().upper(), precio, stock, url_img, id_prod_color])
            
            con.commit()
            cursor.close()
            con.close()
            
            return True, 'Producto color modificado correctamente'
                
        except Exception as e:
            return False, f"Error al modificar producto color: {str(e)}"
    
    def cambiar_estado(self, id_prod_color):
        """Cambiar el estado de un producto_color (activar/desactivar) - ELIMINACIÓN LÓGICA"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Obtener estado actual
            sql_get = "SELECT estado FROM producto_color WHERE id_prod_color = %s"
            cursor.execute(sql_get, [id_prod_color])
            resultado = cursor.fetchone()
            
            if not resultado:
                cursor.close()
                con.close()
                return False, 'Producto color no encontrado'
            
            # Cambiar al estado contrario
            nuevo_estado = not resultado['estado']
            sql_update = "UPDATE producto_color SET estado = %s WHERE id_prod_color = %s"
            cursor.execute(sql_update, [nuevo_estado, id_prod_color])
            
            con.commit()
            cursor.close()
            con.close()
            
            accion = 'activado' if nuevo_estado else 'desactivado'
            return True, f'Producto color {accion} correctamente'
                
        except Exception as e:
            return False, f"Error al cambiar estado: {str(e)}"
    
    def eliminar_fisico(self, id_prod_color):
        """Eliminar FÍSICAMENTE un producto_color (DELETE permanente)"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Verificar que existe
            sql_check_exists = "SELECT COUNT(*) as total FROM producto_color WHERE id_prod_color = %s"
            cursor.execute(sql_check_exists, [id_prod_color])
            existe = cursor.fetchone()
            
            if existe['total'] == 0:
                cursor.close()
                con.close()
                return False, 'Producto color no encontrado'
            
            # Verificar que no esté en uso en otras tablas
            sql_check_uso = """
                SELECT 
                    (SELECT COUNT(*) FROM detalle_venta WHERE id_prod_color = %s) as en_ventas,
                    (SELECT COUNT(*) FROM favoritos WHERE id_prod_color = %s) as en_favoritos,
                    (SELECT COUNT(*) FROM carrito_compra WHERE id_prod_color = %s) as en_carrito,
                    (SELECT COUNT(*) FROM resenia_producto WHERE id_prod_color = %s) as en_resenias
            """
            cursor.execute(sql_check_uso, [id_prod_color, id_prod_color, id_prod_color, id_prod_color])
            uso = cursor.fetchone()
            
            total_uso = uso['en_ventas'] + uso['en_favoritos'] + uso['en_carrito'] + uso['en_resenias']
            
            if total_uso > 0:
                detalles = []
                if uso['en_ventas'] > 0:
                    detalles.append(f"{uso['en_ventas']} venta(s)")
                if uso['en_favoritos'] > 0:
                    detalles.append(f"{uso['en_favoritos']} favorito(s)")
                if uso['en_carrito'] > 0:
                    detalles.append(f"{uso['en_carrito']} carrito(s)")
                if uso['en_resenias'] > 0:
                    detalles.append(f"{uso['en_resenias']} reseña(s)")
                
                cursor.close()
                con.close()
                return False, f'No se puede eliminar porque está asociado a: {", ".join(detalles)}'
            
            # Eliminar físicamente (DELETE)
            sql_delete = "DELETE FROM producto_color WHERE id_prod_color = %s"
            cursor.execute(sql_delete, [id_prod_color])
            
            con.commit()
            cursor.close()
            con.close()
            
            return True, 'Producto color eliminado permanentemente de la base de datos'
                
        except Exception as e:
            return False, f"Error al eliminar producto color: {str(e)}"
    
    # ============================================
    # MÉTODOS AUXILIARES PARA SELECTS
    # ============================================
    
    def listar_productos_activos(self):
        """Listar productos_sucursal activos para select"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    ps.id_prod_sucursal, 
                    ps.nombre,
                    m.nombre as marca,
                    c.nombre as categoria
                FROM producto_sucursal ps
                LEFT JOIN marca m ON ps.id_marca = m.id_marca
                LEFT JOIN categoria_producto c ON ps.id_categoria = c.id_categoria
                WHERE ps.estado = TRUE
                ORDER BY ps.nombre
            """
            
            cursor.execute(sql)
            resultado = cursor.fetchall()
            
            cursor.close()
            con.close()
            
            if resultado:
                productos = []
                for row in resultado:
                    marca = row['marca'] if row['marca'] else ''
                    categoria = row['categoria'] if row['categoria'] else ''
                    nombre_completo = f"{row['nombre']} - {marca} ({categoria})"
                    productos.append({
                        'id_prod_sucursal': row['id_prod_sucursal'],
                        'nombre': row['nombre'],
                        'nombre_completo': nombre_completo
                    })
                return True, productos
            else:
                return True, []
                
        except Exception as e:
            return False, f"Error al listar productos: {str(e)}"
    
    def listar_colores_activos(self):
        """Listar colores activos para select"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT id_color, nombre
                FROM color
                WHERE estado = TRUE
                ORDER BY nombre
            """
            
            cursor.execute(sql)
            resultado = cursor.fetchall()
            
            cursor.close()
            con.close()
            
            if resultado:
                colores = []
                for row in resultado:
                    colores.append({
                        'id_color': row['id_color'],
                        'nombre': row['nombre']
                    })
                return True, colores
            else:
                return True, []
                
        except Exception as e:
            return False, f"Error al listar colores: {str(e)}"