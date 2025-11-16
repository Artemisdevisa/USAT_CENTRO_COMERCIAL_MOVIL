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
            return False, f"Error al listar tarjetas: {str(e)}"
    
    def agregar(self, id_usuario, numero, titular, fecha_vencimiento, cvv, tipo_tarjeta, es_principal=False):
        """Agregar nueva tarjeta"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            cursor.execute("""
                SELECT fn_agregar_tarjeta(%s, %s, %s, %s, %s, %s, %s) as id_tarjeta
            """, [id_usuario, numero, titular, fecha_vencimiento, cvv, tipo_tarjeta, es_principal])
            
            resultado = cursor.fetchone()
            con.commit()
            cursor.close()
            con.close()
            
            if resultado and resultado['id_tarjeta'] > 0:
                return True, resultado['id_tarjeta']
            elif resultado and resultado['id_tarjeta'] == -2:
                return False, 'La tarjeta ya está registrada'
            else:
                return False, 'Error al agregar tarjeta'
        except Exception as e:
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
            return False, f"Error: {str(e)}"