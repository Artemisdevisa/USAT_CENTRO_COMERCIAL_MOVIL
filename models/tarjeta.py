from conexionBD import Conexion

class Tarjeta:
    def __init__(self):
        pass
    
    def listar_por_usuario(self, id_usuario):
        """Lista tarjetas del usuario"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            cursor.execute("SELECT * FROM fn_listar_tarjetas_usuario(%s)", [id_usuario])
            resultados = cursor.fetchall()
            
            cursor.close()
            con.close()
            
            if resultados:
                tarjetas = []
                for row in resultados:
                    tarjeta = {
                        'id_tarjeta': row['id_tarjeta'],
                        'numero_tarjeta': row['numero_tarjeta'],
                        'numero_completo': row['numero_completo'],
                        'titular': row['titular'],
                        'fecha_vencimiento': str(row['fecha_vencimiento']) if row['fecha_vencimiento'] else '',
                        'tipo_tarjeta': row['tipo_tarjeta'],
                        'es_principal': row['es_principal']
                    }
                    tarjetas.append(tarjeta)
                return True, tarjetas
            else:
                return True, []
        except Exception as e:
            print(f"❌ Error en listar_por_usuario: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, f"Error al listar tarjetas: {str(e)}"
    
    def agregar(self, id_usuario, numero, titular, fecha_vencimiento, cvv, tipo_tarjeta, es_principal=False):
        """Agregar nueva tarjeta"""
        con = None
        cursor = None
        try:
            print(f"   id_usuario: {id_usuario}")
            print(f"   numero: {numero}")
            print(f"   titular: {titular}")
            print(f"   fecha_vencimiento: {fecha_vencimiento}")
            print(f"   cvv: {cvv}")
            print(f"   tipo_tarjeta: {tipo_tarjeta}")
            print(f"   es_principal: {es_principal}")
            
            print("Abriendo conexión...")
            con = Conexion().open
            cursor = con.cursor()
            print("Conexión abierta")
            
            sql = "SELECT fn_agregar_tarjeta(%s, %s, %s, %s::DATE, %s, %s, %s) as id_tarjeta"
            params = [id_usuario, numero, titular, fecha_vencimiento, cvv, tipo_tarjeta, es_principal]
            
            print(f"   SQL: {sql}")
            print(f"   Params: {params}")
            
            cursor.execute(sql, params)
            
            resultado = cursor.fetchone()
            print(f"Resultado: {resultado}")
            
            if resultado:
                id_tarjeta_result = resultado['id_tarjeta']
                print(f"ID Tarjeta: {id_tarjeta_result}")
                
                if id_tarjeta_result and id_tarjeta_result > 0:
                    print(f"Tarjeta creada con ID: {id_tarjeta_result}")
                    con.commit()
                    cursor.close()
                    con.close()
                    return True, id_tarjeta_result
                    
                elif id_tarjeta_result == -2:
                    print("La tarjeta ya está registrada")
                    con.rollback()
                    cursor.close()
                    con.close()
                    return False, 'La tarjeta ya está registrada'
                    
                elif id_tarjeta_result == -1:
                    print("Error en validación")
                    con.rollback()
                    cursor.close()
                    con.close()
                    return False, 'Datos inválidos o error en la base de datos'
                    
                else:
                    print(f"Código desconocido: {id_tarjeta_result}")
                    con.rollback()
                    cursor.close()
                    con.close()
                    return False, f'Error desconocido: código {id_tarjeta_result}'
            else:
                print("resultado es None")
                if cursor:
                    cursor.close()
                if con:
                    con.close()
                return False, 'No se obtuvo respuesta de la base de datos'
                
        except Exception as e:
            print(f"EXCEPCIÓN: {str(e)}")
            import traceback
            traceback.print_exc()
            
            if con:
                try:
                    con.rollback()
                except:
                    pass
            
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            
            if con:
                try:
                    con.close()
                except:
                    pass
            
            return False, f"Error: {str(e)}"
    
    def eliminar(self, id_usuario, id_tarjeta):
        """Eliminar tarjeta (lógico)"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            cursor.execute("SELECT fn_eliminar_tarjeta(%s, %s) as resultado", [id_usuario, id_tarjeta])
            resultado = cursor.fetchone()
            
            con.commit()
            cursor.close()
            con.close()
            
            if resultado and resultado['resultado'] == 0:
                return True, 'Tarjeta eliminada correctamente'
            else:
                return False, 'Error al eliminar tarjeta'
        except Exception as e:
            print(f"❌ Error en eliminar: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, f"Error: {str(e)}"
    
    def establecer_principal(self, id_usuario, id_tarjeta):
        """Establecer tarjeta como principal"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            cursor.execute("SELECT fn_establecer_tarjeta_principal(%s, %s) as resultado", [id_usuario, id_tarjeta])
            resultado = cursor.fetchone()
            
            con.commit()
            cursor.close()
            con.close()
            
            if resultado and resultado['resultado'] == 0:
                return True, 'Tarjeta establecida como principal'
            else:
                return False, 'Error al establecer tarjeta principal'
        except Exception as e:
            print(f"❌ Error en establecer_principal: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, f"Error: {str(e)}"