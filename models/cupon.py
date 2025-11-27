from conexionBD import Conexion

class Cupon:
    @staticmethod
    def listar(id_empresa=None):
        """Listar todos los cupones con filtro opcional por empresa"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
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
            """
            
            if id_empresa:
                sql += " WHERE s.id_empresa = %s"
                cursor.execute(sql + " ORDER BY c.fecha_inicio DESC", [id_empresa])
            else:
                cursor.execute(sql + " ORDER BY c.fecha_inicio DESC")
            
            resultado = cursor.fetchall()
            cursor.close()
            con.close()
            
            return resultado if resultado else []
        except Exception as e:
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    @staticmethod
    def listar_por_sucursal(id_sucursal):
        """Listar cupones activos de una sucursal"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            print(f"\n{'='*60}")
            print(f"🔍 BUSCANDO CUPONES PARA SUCURSAL {id_sucursal}")
            print(f"{'='*60}")
            
            cursor.execute("""
                SELECT 
                    c.id_cupon,
                    c.codigo,
                    c.descripcion,
                    c.porcentaje_descuento,
                    c.monto_minimo,
                    c.fecha_inicio,
                    c.fecha_fin,
                    (c.cantidad_total - c.cantidad_usada) as cantidad_disponible,
                    cat.nombre as categoria,
                    c.id_sucursal
                FROM cupon c
                LEFT JOIN categoria_producto cat ON c.id_categoria = cat.id_categoria
                WHERE c.id_sucursal = %s 
                    AND c.estado = TRUE
                    AND c.fecha_inicio <= NOW()
                    AND c.fecha_fin >= NOW()
                    AND c.cantidad_usada < c.cantidad_total
                ORDER BY c.fecha_fin
            """, [int(id_sucursal)])
            
            resultados = cursor.fetchall()
            
            print(f"✅ Cupones encontrados: {len(resultados) if resultados else 0}")
            
            cursor.close()
            con.close()
            
            if resultados:
                cupones = []
                for row in resultados:
                    cupon = {
                        'id_cupon': row['id_cupon'],
                        'codigo': row['codigo'],
                        'descripcion': row['descripcion'],
                        'porcentaje_descuento': float(row['porcentaje_descuento']),
                        'monto_minimo': float(row['monto_minimo']),
                        'fecha_inicio': row['fecha_inicio'].isoformat() if row['fecha_inicio'] else None,
                        'fecha_fin': row['fecha_fin'].isoformat() if row['fecha_fin'] else None,
                        'cantidad_disponible': row['cantidad_disponible'],
                        'categoria': row['categoria'],
                        'id_sucursal': row['id_sucursal']
                    }
                    cupones.append(cupon)
                    print(f"   📦 Cupón: {cupon['codigo']} - {cupon['porcentaje_descuento']}% - Sucursal: {cupon['id_sucursal']}")
                
                return cupones
            else:
                return []
                
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