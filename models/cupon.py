from conexionBD import Conexion

class Cupon:
    @staticmethod
    def listar():
        """Listar todos los cupones"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            cursor.execute("""
                SELECT 
                    c.id_cupon,
                    c.codigo,
                    c.descripcion,
                    c.porcentaje_descuento,
                    c.monto_minimo,
                    c.fecha_inicio,
                    c.fecha_fin,
                    c.cantidad_total,
                    c.cantidad_usada,
                    c.estado,
                    c.id_sucursal,
                    c.id_categoria,
                    s.nombre as nombre_sucursal,
                    cat.nombre as nombre_categoria
                FROM cupon c
                INNER JOIN sucursal s ON c.id_sucursal = s.id_sucursal
                LEFT JOIN categoria_producto cat ON c.id_categoria = cat.id_categoria
                ORDER BY c.fecha_inicio DESC
            """)
            
            resultado = cursor.fetchall()
            cursor.close()
            con.close()
            
            return resultado if resultado else []
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    @staticmethod
    def listar_por_sucursal(id_sucursal):
        """Listar cupones activos de una sucursal"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            cursor.execute("""
                SELECT fn_cupon_listar_por_sucursal(%s) as cupones
            """, [int(id_sucursal)])
            
            resultado = cursor.fetchone()
            cupones = resultado['cupones'] if resultado else []
            
            cursor.close()
            con.close()
            
            return cupones if cupones else []
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    @staticmethod
    def crear(codigo, descripcion, porcentaje_descuento, monto_minimo, 
              id_sucursal, id_categoria, fecha_inicio, fecha_fin, cantidad_total):
        """Crear un nuevo cupón"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            cursor.execute("""
                SELECT fn_cupon_crear(
                    %s, %s, %s, %s, %s, %s, %s::TIMESTAMP, %s::TIMESTAMP, %s
                ) as resultado
            """, [
                codigo,
                descripcion,
                porcentaje_descuento,
                monto_minimo,
                id_sucursal,
                id_categoria,
                fecha_inicio,
                fecha_fin,
                cantidad_total
            ])
            
            resultado = cursor.fetchone()
            id_cupon = resultado['resultado']
            
            con.commit()
            cursor.close()
            con.close()
            
            return id_cupon
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return -1

    @staticmethod
    def modificar(id_cupon, descripcion, porcentaje_descuento, monto_minimo,
                  fecha_inicio, fecha_fin, cantidad_total):
        """Modificar un cupón existente"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            cursor.execute("""
                SELECT fn_cupon_modificar(
                    %s, %s, %s, %s, %s::TIMESTAMP, %s::TIMESTAMP, %s
                ) as resultado
            """, [
                id_cupon,
                descripcion,
                porcentaje_descuento,
                monto_minimo,
                fecha_inicio,
                fecha_fin,
                cantidad_total
            ])
            
            resultado = cursor.fetchone()
            codigo = resultado['resultado']
            
            con.commit()
            cursor.close()
            con.close()
            
            return codigo
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return -1

    @staticmethod
    def eliminar(id_cupon):
        """Eliminar un cupón (lógico)"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            cursor.execute("""
                SELECT fn_cupon_eliminar(%s) as resultado
            """, [id_cupon])
            
            resultado = cursor.fetchone()
            codigo = resultado['resultado']
            
            con.commit()
            cursor.close()
            con.close()
            
            return codigo
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return -1