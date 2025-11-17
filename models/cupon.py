from conexionBD import Conexion

class Cupon:
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