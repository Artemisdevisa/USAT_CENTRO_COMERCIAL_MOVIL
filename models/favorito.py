from conexionBD import Conexion

class Favorito:
    def __init__(self):
        pass
    
    def listar_favoritos(self, id_usuario):
        """Lista todos los favoritos de un usuario"""
        try:
            con = Conexion().open  # ✅ CORRECTO
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    f.id_favorito,
                    f.id_prod_color,
                    ps.id_prod_sucursal,
                    ps.nombre as producto_nombre,
                    pc.precio,
                    pc.stock,
                    pc.url_img,
                    ps.talla,
                    ps.genero,
                    ps.material,
                    m.nombre as marca,
                    c.nombre as categoria,
                    col.nombre as color,
                    s.nombre as sucursal,
                    f.created_at
                FROM favoritos f
                INNER JOIN producto_color pc ON f.id_prod_color = pc.id_prod_color
                INNER JOIN producto_sucursal ps ON pc.id_prod_sucursal = ps.id_prod_sucursal
                INNER JOIN color col ON pc.id_color = col.id_color
                LEFT JOIN marca m ON ps.id_marca = m.id_marca
                LEFT JOIN categoria_producto c ON ps.id_categoria = c.id_categoria
                LEFT JOIN sucursal s ON ps.id_sucursal = s.id_sucursal
                WHERE f.id_usuario = %s AND f.estado = TRUE AND pc.estado = TRUE
                ORDER BY f.created_at DESC
            """
            
            cursor.execute(sql, (id_usuario,))
            resultados = cursor.fetchall()
            
            favoritos = []
            for row in resultados:
                favorito = {
                    "id_favorito": row['id_favorito'],
                    "id_prod_color": row['id_prod_color'],
                    "id_prod_sucursal": row['id_prod_sucursal'],
                    "producto_nombre": row['producto_nombre'],
                    "precio": float(row['precio']) if row['precio'] else 0.0,
                    "stock": row['stock'],
                    "url_img": row['url_img'] if row['url_img'] else '',
                    "talla": row['talla'],
                    "genero": row['genero'],
                    "material": row['material'],
                    "marca": row['marca'] if row['marca'] else '',
                    "categoria": row['categoria'] if row['categoria'] else '',
                    "color": row['color'],
                    "sucursal": row['sucursal'] if row['sucursal'] else '',
                    "created_at": str(row['created_at'])
                }
                favoritos.append(favorito)
            
            cursor.close()
            con.close()
            
            return True, favoritos
                
        except Exception as e:
            return False, f"Error al listar favoritos: {str(e)}"
    
    def agregar_favorito(self, id_usuario, id_prod_color):
        """Agrega un producto a favoritos"""
        try:
            con = Conexion().open  # ✅ CORRECTO
            cursor = con.cursor()
            
            # Verificar que el producto_color existe y está activo
            sql_check_producto = """
                SELECT 1 FROM producto_color 
                WHERE id_prod_color = %s AND estado = TRUE
            """
            cursor.execute(sql_check_producto, (id_prod_color,))
            if not cursor.fetchone():
                cursor.close()
                con.close()
                return False, "Producto no válido o no disponible"
            
            # Verificar si ya existe
            sql_check = """
                SELECT id_favorito, estado 
                FROM favoritos 
                WHERE id_usuario = %s AND id_prod_color = %s
            """
            cursor.execute(sql_check, (id_usuario, id_prod_color))
            existe = cursor.fetchone()
            
            if existe:
                if existe['estado']:
                    cursor.close()
                    con.close()
                    return False, "El producto ya está en favoritos"
                else:
                    # Reactivar favorito
                    sql_update = """
                        UPDATE favoritos 
                        SET estado = TRUE, 
                            created_at = DATE_TRUNC('minute', LOCALTIMESTAMP)
                        WHERE id_favorito = %s
                    """
                    cursor.execute(sql_update, (existe['id_favorito'],))
            else:
                # Insertar nuevo
                sql_insert = """
                    INSERT INTO favoritos (id_usuario, id_prod_color, estado)
                    VALUES (%s, %s, TRUE)
                """
                cursor.execute(sql_insert, (id_usuario, id_prod_color))
            
            con.commit()
            cursor.close()
            con.close()
            return True, "Producto agregado a favoritos"
                
        except Exception as e:
            return False, f"Error al agregar favorito: {str(e)}"
    
    def eliminar_favorito(self, id_usuario, id_favorito):
        """Elimina un favorito (lógico)"""
        try:
            con = Conexion().open  # ✅ CORRECTO
            cursor = con.cursor()
            
            sql = """
                UPDATE favoritos 
                SET estado = FALSE
                WHERE id_favorito = %s AND id_usuario = %s
            """
            
            cursor.execute(sql, (id_favorito, id_usuario))
            
            if cursor.rowcount == 0:
                cursor.close()
                con.close()
                return False, "Favorito no encontrado"
            
            con.commit()
            cursor.close()
            con.close()
            return True, "Favorito eliminado"
                
        except Exception as e:
            return False, f"Error al eliminar favorito: {str(e)}"
    
    def eliminar_favorito_por_producto(self, id_usuario, id_prod_color):
        """Elimina un favorito por producto_color (lógico)"""
        try:
            con = Conexion().open  # ✅ CORRECTO
            cursor = con.cursor()
            
            sql = """
                UPDATE favoritos 
                SET estado = FALSE
                WHERE id_prod_color = %s AND id_usuario = %s AND estado = TRUE
            """
            
            cursor.execute(sql, (id_prod_color, id_usuario))
            
            if cursor.rowcount == 0:
                cursor.close()
                con.close()
                return False, "Favorito no encontrado"
            
            con.commit()
            cursor.close()
            con.close()
            return True, "Favorito eliminado"
                
        except Exception as e:
            return False, f"Error al eliminar favorito: {str(e)}"
    
    def verificar_favorito(self, id_usuario, id_prod_color):
        """Verifica si un producto está en favoritos"""
        try:
            con = Conexion().open  # ✅ CORRECTO
            cursor = con.cursor()
            
            sql = """
                SELECT id_favorito 
                FROM favoritos 
                WHERE id_usuario = %s 
                  AND id_prod_color = %s 
                  AND estado = TRUE
            """
            
            cursor.execute(sql, (id_usuario, id_prod_color))
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            if resultado:
                return True, {"es_favorito": True, "id_favorito": resultado['id_favorito']}
            else:
                return True, {"es_favorito": False, "id_favorito": None}
                
        except Exception as e:
            return False, f"Error al verificar favorito: {str(e)}"