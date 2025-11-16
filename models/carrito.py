from conexionBD import Conexion

class Carrito:
    def __init__(self):
        pass
    
    def listar_carrito(self, id_usuario):
        """Lista el carrito agrupado por sucursal"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    s.id_sucursal,
                    s.nombre as sucursal,
                    s.img_logo as sucursal_logo,  -- ✅ CAMBIAR: logo → img_logo
                    cc.id_carrito,
                    cc.id_prod_color,
                    cc.cantidad,
                    ps.id_prod_sucursal,
                    ps.nombre as producto_nombre,
                    pc.talla,
                    ps.genero,
                    ps.material,
                    pc.precio,
                    pc.stock,
                    pc.url_img,
                    m.nombre as marca,
                    c.nombre as categoria,
                    col.nombre as color
                FROM carrito_compra cc
                INNER JOIN producto_color pc ON cc.id_prod_color = pc.id_prod_color
                INNER JOIN producto_sucursal ps ON pc.id_prod_sucursal = ps.id_prod_sucursal
                INNER JOIN sucursal s ON ps.id_sucursal = s.id_sucursal
                INNER JOIN color col ON pc.id_color = col.id_color
                LEFT JOIN marca m ON ps.id_marca = m.id_marca
                LEFT JOIN categoria_producto c ON ps.id_categoria = c.id_categoria
                WHERE cc.id_usuario = %s AND cc.estado = TRUE AND pc.estado = TRUE
                ORDER BY s.nombre, ps.nombre
            """
            
            cursor.execute(sql, (id_usuario,))
            resultados = cursor.fetchall()
            
            # Agrupar por sucursal
            sucursales = {}
            for row in resultados:
                id_sucursal = row['id_sucursal']
                
                if id_sucursal not in sucursales:
                    sucursales[id_sucursal] = {
                        'id_sucursal': id_sucursal,
                        'nombre_sucursal': row['sucursal'],
                        'logo_sucursal': row['sucursal_logo'] if row['sucursal_logo'] else '',  # ✅ img_logo
                        'productos': [],
                        'subtotal': 0
                    }
                
                producto = {
                    'id_carrito': row['id_carrito'],
                    'id_prod_color': row['id_prod_color'],
                    'id_prod_sucursal': row['id_prod_sucursal'],
                    'producto_nombre': row['producto_nombre'],
                    'cantidad': row['cantidad'],
                    'precio': float(row['precio']),
                    'stock': row['stock'],
                    'url_img': row['url_img'] if row['url_img'] else '',
                    'talla': row['talla'] if row['talla'] else '',
                    'genero': row['genero'] if row['genero'] else '',
                    'material': row['material'] if row['material'] else '',
                    'marca': row['marca'] if row['marca'] else '',
                    'categoria': row['categoria'] if row['categoria'] else '',
                    'color': row['color']
                }
                
                sucursales[id_sucursal]['productos'].append(producto)
                sucursales[id_sucursal]['subtotal'] += producto['precio'] * producto['cantidad']
            
            cursor.close()
            con.close()
            
            return True, list(sucursales.values())
                
        except Exception as e:
            return False, f"Error al listar carrito: {str(e)}"
    
    def agregar_al_carrito(self, id_usuario, id_prod_color, cantidad=1):
        """Agrega producto al carrito"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Verificar producto
            sql_check = """
                SELECT stock FROM producto_color 
                WHERE id_prod_color = %s AND estado = TRUE
            """
            cursor.execute(sql_check, (id_prod_color,))
            producto = cursor.fetchone()
            
            if not producto:
                cursor.close()
                con.close()
                return False, "Producto no disponible"
            
            if producto['stock'] < cantidad:
                cursor.close()
                con.close()
                return False, f"Stock insuficiente. Disponible: {producto['stock']}"
            
            # ✅ VERIFICAR SI YA EXISTE (INCLUSO CON estado = FALSE)
            sql_exists = """
                SELECT id_carrito, cantidad, estado
                FROM carrito_compra 
                WHERE id_usuario = %s AND id_prod_color = %s
            """
            cursor.execute(sql_exists, (id_usuario, id_prod_color))
            existe = cursor.fetchone()
            
            if existe:
                # ✅ SI EXISTE PERO ESTÁ INACTIVO, REACTIVAR
                if not existe['estado']:
                    sql_reactivar = """
                        UPDATE carrito_compra 
                        SET cantidad = %s, estado = TRUE
                        WHERE id_carrito = %s
                    """
                    cursor.execute(sql_reactivar, (cantidad, existe['id_carrito']))
                else:
                    # ✅ SI YA ESTÁ ACTIVO, SUMAR CANTIDAD
                    nueva_cantidad = existe['cantidad'] + cantidad
                    if nueva_cantidad > producto['stock']:
                        cursor.close()
                        con.close()
                        return False, f"Stock insuficiente. Disponible: {producto['stock']}"
                    
                    sql_update = """
                        UPDATE carrito_compra 
                        SET cantidad = %s
                        WHERE id_carrito = %s
                    """
                    cursor.execute(sql_update, (nueva_cantidad, existe['id_carrito']))
            else:
                # ✅ NO EXISTE, INSERTAR NUEVO
                sql_insert = """
                    INSERT INTO carrito_compra (id_usuario, id_prod_color, cantidad, estado)
                    VALUES (%s, %s, %s, TRUE)
                """
                cursor.execute(sql_insert, (id_usuario, id_prod_color, cantidad))
            
            con.commit()
            cursor.close()
            con.close()
            return True, "Producto agregado al carrito"
                
        except Exception as e:
            return False, f"Error al agregar al carrito: {str(e)}"
        
    def actualizar_cantidad(self, id_usuario, id_carrito, cantidad):
        """Actualiza cantidad de un producto"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            if cantidad <= 0:
                cursor.close()
                con.close()
                return False, "Cantidad inválida"
            
            # Verificar stock
            sql_check = """
                SELECT pc.stock 
                FROM carrito_compra cc
                INNER JOIN producto_color pc ON cc.id_prod_color = pc.id_prod_color
                WHERE cc.id_carrito = %s AND cc.id_usuario = %s
            """
            cursor.execute(sql_check, (id_carrito, id_usuario))
            result = cursor.fetchone()
            
            if not result:
                cursor.close()
                con.close()
                return False, "Producto no encontrado"
            
            if cantidad > result['stock']:
                cursor.close()
                con.close()
                return False, f"Stock insuficiente. Disponible: {result['stock']}"
            
            sql = """
                UPDATE carrito_compra 
                SET cantidad = %s
                WHERE id_carrito = %s AND id_usuario = %s
            """
            cursor.execute(sql, (cantidad, id_carrito, id_usuario))
            
            if cursor.rowcount == 0:
                cursor.close()
                con.close()
                return False, "Producto no encontrado"
            
            con.commit()
            cursor.close()
            con.close()
            return True, "Cantidad actualizada"
                
        except Exception as e:
            return False, f"Error al actualizar cantidad: {str(e)}"
    
    def eliminar_del_carrito(self, id_usuario, id_carrito):
        """Elimina producto del carrito"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                UPDATE carrito_compra 
                SET estado = FALSE
                WHERE id_carrito = %s AND id_usuario = %s
            """
            cursor.execute(sql, (id_carrito, id_usuario))
            
            if cursor.rowcount == 0:
                cursor.close()
                con.close()
                return False, "Producto no encontrado"
            
            con.commit()
            cursor.close()
            con.close()
            return True, "Producto eliminado del carrito"
                
        except Exception as e:
            return False, f"Error al eliminar del carrito: {str(e)}"
    
    def vaciar_carrito(self, id_usuario):
        """Vacía todo el carrito"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                UPDATE carrito_compra 
                SET estado = FALSE
                WHERE id_usuario = %s
            """
            cursor.execute(sql, (id_usuario,))
            
            con.commit()
            cursor.close()
            con.close()
            return True, "Carrito vaciado"
                
        except Exception as e:
            return False, f"Error al vaciar carrito: {str(e)}"