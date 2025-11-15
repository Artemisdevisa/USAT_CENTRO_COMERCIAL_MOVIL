from conexionBD import Conexion

class CategoriaProducto:
    def __init__(self):
        pass
    
    # ============================================
    # MÉTODOS EXISTENTES (Para listar en front público)
    # ============================================
    
    def listar_categorias(self):
        """Listar categorías activas para el frontend público"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    id_categoria,
                    nombre,
                    img
                FROM categoria_producto
                WHERE estado = TRUE
                ORDER BY nombre
            """
            
            cursor.execute(sql)
            resultados = cursor.fetchall()
            
            categorias = []
            for row in resultados:
                categoria = {
                    "idCategoriaProducto": row['id_categoria'],
                    "nombreCategoria": row['nombre'],
                    "imagen": f"/uploads/fotos/categorias/{row['img']}" if row['img'] else None
                }
                categorias.append(categoria)
            
            cursor.close()
            con.close()
            
            return True, categorias
                
        except Exception as e:
            return False, f"Error al listar categorías: {str(e)}"
    
    def listar_productos_por_categoria(self, id_categoria):
        """Listar productos por categoría para el frontend público"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    ps.id_prod_sucursal,
                    ps.nombre,
                    ps.precio,
                    ps.url_img,
                    ps.genero,
                    ps.id_marca,
                    ps.id_categoria,
                    cp.nombre AS nombre_categoria,
                    ps.id_tipo_modelo,
                    ps.talla,
                    ps.material,
                    m.nombre AS marca
                FROM producto_sucursal ps
                INNER JOIN categoria_producto cp ON ps.id_categoria = cp.id_categoria
                LEFT JOIN marca m ON ps.id_marca = m.id_marca
                WHERE ps.id_categoria = %s
                AND ps.estado = TRUE
                ORDER BY ps.id_prod_sucursal DESC
            """
            
            cursor.execute(sql, (id_categoria,))
            resultados = cursor.fetchall()
            
            productos = []
            for row in resultados:
                producto = {
                    "idProducto": row['id_prod_sucursal'],
                    "nombreProducto": row['nombre'],
                    "nombre": row['nombre'],
                    "precio": float(row['precio']),
                    "imagen": f"/uploads/fotos/productos/{row['url_img']}" if row['url_img'] else None,
                    "urlImg": f"/uploads/fotos/productos/{row['url_img']}" if row['url_img'] else None,
                    "genero": row['genero'],
                    "idCategoria": row['id_categoria'],
                    "nombreCategoria": row['nombre_categoria'],
                    "talla": row['talla'],
                    "material": row['material'],
                    "marca": row.get('marca', 'Sin marca')
                }
                productos.append(producto)
            
            cursor.close()
            con.close()
            
            return True, productos
                
        except Exception as e:
            return False, f"Error al listar productos por categoría: {str(e)}"
    
    # ============================================
    # MÉTODOS CRUD (Para dashboard/admin)
    # ============================================
    
    def listar(self):
        """Listar TODAS las categorías (activas e inactivas) para el dashboard"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    id_categoria,
                    nombre,
                    img,
                    estado
                FROM categoria_producto
                ORDER BY id_categoria
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
                        'nombre': row['nombre'],
                        'img': row['img'],
                        'estado': row['estado']
                    })
                return True, categorias
            else:
                return True, []
                
        except Exception as e:
            return False, f"Error al listar categorías: {str(e)}"
    
    def obtener_por_id(self, id_categoria):
        """Obtener una categoría por su ID"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    id_categoria,
                    nombre,
                    img,
                    estado
                FROM categoria_producto
                WHERE id_categoria = %s
            """
            
            cursor.execute(sql, [id_categoria])
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            if resultado:
                return True, {
                    'id_categoria': resultado['id_categoria'],
                    'nombre': resultado['nombre'],
                    'img': resultado['img'],
                    'estado': resultado['estado']
                }
            else:
                return False, 'Categoría no encontrada'
                
        except Exception as e:
            return False, f"Error al obtener categoría: {str(e)}"
    
    def crear(self, nombre, img=None):
        """Crear una nueva categoría usando la función de PostgreSQL"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Llamar a la función fn_categoria_producto_crear
            sql = "SELECT fn_categoria_producto_crear(%s) as resultado"
            cursor.execute(sql, [nombre])
            
            resultado = cursor.fetchone()
            id_categoria = resultado['resultado']
            
            # Si se creó correctamente y hay imagen, actualizarla
            if id_categoria and id_categoria > 0 and img:
                sql_update = "UPDATE categoria_producto SET img = %s WHERE id_categoria = %s"
                cursor.execute(sql_update, [img, id_categoria])
            
            con.commit()
            cursor.close()
            con.close()
            
            if id_categoria and id_categoria > 0:
                return True, id_categoria
            else:
                return False, 'No se pudo crear la categoría. Puede que ya exista una categoría con ese nombre.'
                
        except Exception as e:
            return False, f"Error al crear categoría: {str(e)}"
    
    def modificar(self, id_categoria, nombre, img=None):
        """Modificar una categoría usando la función de PostgreSQL"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Llamar a la función fn_categoria_producto_modificar
            sql = "SELECT fn_categoria_producto_modificar(%s, %s) as resultado"
            cursor.execute(sql, [id_categoria, nombre])
            
            resultado = cursor.fetchone()
            codigo = resultado['resultado']
            
            # Si se modificó correctamente y hay imagen, actualizarla
            if codigo == 0 and img:
                sql_update = "UPDATE categoria_producto SET img = %s WHERE id_categoria = %s"
                cursor.execute(sql_update, [img, id_categoria])
            
            con.commit()
            cursor.close()
            con.close()
            
            if codigo == 0:
                return True, 'Categoría modificada correctamente'
            else:
                return False, 'No se pudo modificar la categoría. Puede que ya exista una categoría con ese nombre.'
                
        except Exception as e:
            return False, f"Error al modificar categoría: {str(e)}"
    
    def cambiar_estado(self, id_categoria):
        """Cambiar el estado de una categoría (activar/desactivar)"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Llamar a la función fn_categoria_producto_cambiar_estado
            sql = "SELECT fn_categoria_producto_cambiar_estado(%s) as resultado"
            cursor.execute(sql, [id_categoria])
            
            resultado = cursor.fetchone()
            codigo = resultado['resultado']
            
            con.commit()
            cursor.close()
            con.close()
            
            if codigo == 0:
                return True, 'Estado cambiado correctamente'
            else:
                return False, 'No se pudo cambiar el estado de la categoría'
                
        except Exception as e:
            return False, f"Error al cambiar estado: {str(e)}"
    
    def eliminar_fisico(self, id_categoria):
        """Eliminar físicamente una categoría (DELETE permanente)"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Llamar a la función fn_categoria_producto_eliminar_fisico
            sql = "SELECT fn_categoria_producto_eliminar_fisico(%s) as resultado"
            cursor.execute(sql, [id_categoria])
            
            resultado = cursor.fetchone()
            codigo = resultado['resultado']
            
            con.commit()
            cursor.close()
            con.close()
            
            if codigo == 0:
                return True, 'Categoría eliminada permanentemente'
            elif codigo == -2:
                return False, 'No se puede eliminar la categoría porque tiene productos asociados'
            else:
                return False, 'No se pudo eliminar la categoría'
                
        except Exception as e:
            return False, f"Error al eliminar categoría: {str(e)}"
    
    def contar_productos(self, id_categoria):
        """Contar productos asociados a una categoría"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT COUNT(*) as total
                FROM producto_sucursal
                WHERE id_categoria = %s
            """
            
            cursor.execute(sql, [id_categoria])
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            return resultado['total'] if resultado else 0
                
        except Exception as e:
            return 0