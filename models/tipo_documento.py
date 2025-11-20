from conexionBD import Conexion

class TipoDocumento:
    def listar_tipo_documento(self):
        """Listar tipos de documento activos"""
        try:
            print("🔍 Ejecutando consulta en BD...")
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT id_tipodoc, nombre, estado 
                FROM tipo_documento 
                WHERE estado = TRUE 
                ORDER BY nombre
            """
            
            cursor.execute(sql)
            resultados = cursor.fetchall()
            
            print(f"📊 Registros encontrados: {len(resultados)}")
            
            data = []
            for row in resultados:
                data.append({
                    'id_tipodoc': row['id_tipodoc'],
                    'nombre': row['nombre'],
                    'estado': row['estado']
                })
            
            cursor.close()
            con.close()
            
            return True, data, "Tipos de documento obtenidos correctamente"
            
        except Exception as e:
            print(f"💥 ERROR en BD: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, [], f"Error al obtener tipos de documento: {str(e)}"
