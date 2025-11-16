from conexionBD import Conexion

class Venta:
    def __init__(self):
        pass
    
    def crear_venta_completa(self, id_usuario, id_sucursal, id_tarjeta):
        """Crear venta completa desde el carrito"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            print(f"\n🔍 EJECUTANDO fn_crear_venta_completa:")
            print(f"   Usuario: {id_usuario}, Sucursal: {id_sucursal}, Tarjeta: {id_tarjeta}")
            
            cursor.execute("""
                SELECT * FROM fn_crear_venta_completa(%s, %s, %s)
            """, [id_usuario, id_sucursal, id_tarjeta])
            
            resultado = cursor.fetchone()
            
            print(f"\n📊 RESULTADO DE LA FUNCIÓN:")
            print(f"   ID Venta: {resultado['id_venta']}")
            print(f"   Código: {resultado['codigo_venta']}")
            print(f"   Mensaje: {resultado['mensaje']}")
            
            con.commit()
            cursor.close()
            con.close()
            
            if resultado and resultado['id_venta'] > 0:
                # ✅ OBTENER EL TOTAL DESDE LA BD
                con2 = Conexion().open
                cursor2 = con2.cursor()
                
                cursor2.execute("SELECT total FROM venta WHERE id_venta = %s", [resultado['id_venta']])
                venta_info = cursor2.fetchone()
                
                cursor2.close()
                con2.close()
                
                total_venta = float(venta_info['total']) if venta_info else 0.0
                
                print(f"   ✅ Total recuperado: {total_venta}")
                
                return True, {
                    'id_venta': resultado['id_venta'],
                    'codigo_venta': resultado['codigo_venta'],
                    'total': total_venta,
                    'mensaje': resultado['mensaje']
                }
            else:
                return False, resultado['mensaje'] if resultado else 'Error al crear venta'
        except Exception as e:
            print(f"\n💥 ERROR EN crear_venta_completa: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, f"Error: {str(e)}"
    
    def crear_venta_multiple(self, id_usuario, id_sucursal, id_tarjeta):
        """Crear venta vacía (para agregar detalles después)"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            cursor.execute("""
                SELECT fn_crear_venta_multiple(%s, %s, %s) as id_venta
            """, [id_usuario, id_sucursal, id_tarjeta])
            
            resultado = cursor.fetchone()
            
            con.commit()
            cursor.close()
            con.close()
            
            if resultado and resultado['id_venta'] > 0:
                return True, resultado['id_venta']
            else:
                return False, 'Error al crear venta'
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def agregar_detalle(self, id_venta, id_prod_color, cantidad, precio_unitario):
        """Agregar detalle a una venta"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            cursor.execute("""
                SELECT fn_agregar_detalle_venta(%s, %s, %s, %s) as id_detalle
            """, [id_venta, id_prod_color, cantidad, precio_unitario])
            
            resultado = cursor.fetchone()
            
            con.commit()
            cursor.close()
            con.close()
            
            if resultado and resultado['id_detalle'] > 0:
                return True, resultado['id_detalle']
            elif resultado and resultado['id_detalle'] == -2:
                return False, 'Producto no encontrado'
            elif resultado and resultado['id_detalle'] == -3:
                return False, 'Stock insuficiente'
            else:
                return False, 'Error al agregar detalle'
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def listar_por_usuario(self, id_usuario):
        """Listar ventas del usuario con imagen del primer producto"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    v.id_venta,
                    v.codigo_qr as codigo_venta,
                    v.created_at as fecha_venta,
                    v.total,
                    v.estado,
                    s.nombre as nombre_sucursal,
                    (SELECT COUNT(*) FROM detalle_venta dv WHERE dv.id_venta = v.id_venta AND dv.estado = TRUE) as cantidad_productos,
                    (
                        SELECT pc.url_img 
                        FROM detalle_venta dv
                        INNER JOIN producto_color pc ON dv.id_prod_color = pc.id_prod_color
                        WHERE dv.id_venta = v.id_venta 
                        AND dv.estado = TRUE
                        LIMIT 1
                    ) as url_img_producto
                FROM venta v
                INNER JOIN sucursal s ON v.id_sucursal = s.id_sucursal
                WHERE v.id_usuario = %s
                ORDER BY v.created_at DESC
            """
            
            cursor.execute(sql, [id_usuario])
            resultados = cursor.fetchall()
            
            cursor.close()
            con.close()
            
            if resultados:
                ventas = []
                for row in resultados:
                    venta = {
                        'id_venta': row['id_venta'],
                        'codigo_venta': row['codigo_venta'],
                        'fecha_venta': str(row['fecha_venta']) if row['fecha_venta'] else '',
                        'total': float(row['total']) if row['total'] else 0.0,
                        'estado': row['estado'],
                        'nombre_sucursal': row['nombre_sucursal'],
                        'cantidad_productos': int(row['cantidad_productos']) if row['cantidad_productos'] else 0,
                        'url_img_producto': row['url_img_producto'] if row['url_img_producto'] else ''
                    }
                    ventas.append(venta)
                return True, ventas
            else:
                return True, []
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def obtener_detalle(self, id_venta):
        """Obtener detalle de una venta"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            cursor.execute("SELECT * FROM fn_obtener_detalle_venta(%s)", [id_venta])
            resultados = cursor.fetchall()
            
            cursor.close()
            con.close()
            
            if resultados:
                detalles = []
                for row in resultados:
                    detalle = {
                        'id_detalle': row['id_detalle'],
                        'nombre_producto': row['nombre_producto'],
                        'color': row['color'],
                        'talla': row['talla'],
                        'cantidad': row['cantidad'],
                        'subtotal': float(row['subtotal']) if row['subtotal'] else 0.0,
                        'url_img': row['url_img'] if row['url_img'] else ''
                    }
                    detalles.append(detalle)
                return True, detalles
            else:
                return True, []
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def obtener_venta_completa(self, id_venta):
        """Obtener información completa de una venta"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            cursor.execute("SELECT * FROM fn_obtener_venta_completa(%s)", [id_venta])
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            if resultado:
                venta = {
                    'id_venta': resultado['id_venta'],
                    'codigo_venta': resultado['codigo_venta'],
                    'fecha_venta': str(resultado['fecha_venta']) if resultado['fecha_venta'] else '',
                    'total': float(resultado['total']) if resultado['total'] else 0.0,
                    'estado': resultado['estado'],
                    'nombre_sucursal': resultado['nombre_sucursal'],
                    'direccion_sucursal': resultado['direccion_sucursal'],
                    'telefono_sucursal': resultado['telefono_sucursal'],
                    'numero_tarjeta': resultado['numero_tarjeta'],
                    'tipo_tarjeta': resultado['tipo_tarjeta']
                }
                return True, venta
            else:
                return False, 'Venta no encontrada'
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def cancelar_venta(self, id_venta):
        """Cancelar venta y devolver stock"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            cursor.execute("SELECT fn_cancelar_venta(%s) as resultado", [id_venta])
            resultado = cursor.fetchone()
            
            con.commit()
            cursor.close()
            con.close()
            
            if resultado and resultado['resultado'] == 0:
                return True, 'Venta cancelada correctamente'
            else:
                return False, 'Error al cancelar venta'
        except Exception as e:
            return False, f"Error: {str(e)}"