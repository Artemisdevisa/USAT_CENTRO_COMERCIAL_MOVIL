from conexionBD import Conexion

class Empresa:
    def __init__(self):
        pass
    
    def listar(self):
        """Listar todas las empresas con URLs de Cloudinary"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    e.id_empresa,
                    e.ruc,
                    e.razon_social,
                    e.nombre_comercial,
                    e.descripcion,
                    e.sitio_web,
                    e.telefono,
                    e.email,
                    e.direccion,
                    e.img_logo,
                    e.img_banner,
                    e.estado,
                    e.created_at,
                    d.nombre as distrito
                FROM empresa e
                LEFT JOIN distrito d ON e.id_dist = d.id_dist
                ORDER BY e.created_at DESC
            """
            
            cursor.execute(sql)
            resultado = cursor.fetchall()
            
            cursor.close()
            con.close()
            
            return True, resultado
                
        except Exception as e:
            return False, f"Error al listar empresas: {str(e)}"
    
    def cambiar_estado(self, id_empresa):
        """Cambiar estado de una empresa (aprobar/rechazar)"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                UPDATE empresa 
                SET estado = NOT estado
                WHERE id_empresa = %s
            """
            
            cursor.execute(sql, [id_empresa])
            con.commit()
            
            cursor.close()
            con.close()
            
            return True, 'Estado cambiado correctamente'
                
        except Exception as e:
            return False, f"Error al cambiar estado: {str(e)}"