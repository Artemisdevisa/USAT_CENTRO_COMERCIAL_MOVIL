from conexionBD import Conexion

class Sucursal:
    def __init__(self):
        pass
    
    def listar_sucursales(self):
        """Lista todas las sucursales activas con información completa"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    s.id_sucursal,
                    s.nombre,
                    s.direccion,
                    s.telefono,
                    s.img_logo,
                    s.img_banner,
                    e.nombre_comercial as empresa,
                    e.sitio_web,
                    d.nombre as distrito,
                    s.estado,
                    s.created_at
                FROM sucursal s
                LEFT JOIN empresa e ON s.id_empresa = e.id_empresa
                LEFT JOIN distrito d ON s.id_dist = d.id_dist
                WHERE s.estado = TRUE
                ORDER BY s.nombre
            """
            
            cursor.execute(sql)
            resultados = cursor.fetchall()
            
            sucursales = []
            for row in resultados:
                sucursal = {
                    "id_sucursal": row['id_sucursal'],
                    "nombre": row['nombre'],
                    "direccion": row['direccion'],
                    "telefono": row['telefono'],
                    "img_logo": row['img_logo'] if row['img_logo'] else '',
                    "img_banner": row['img_banner'] if row['img_banner'] else '',
                    "empresa": row['empresa'] if row['empresa'] else '',
                    "sitio_web": row['sitio_web'] if row['sitio_web'] else '',
                    "distrito": row['distrito'] if row['distrito'] else '',
                    "estado": "Abierto" if row['estado'] else "Cerrado"
                }
                sucursales.append(sucursal)
            
            cursor.close()
            con.close()
            
            return True, sucursales
                
        except Exception as e:
            return False, f"Error al listar sucursales: {str(e)}"
    
    def obtener_detalle_sucursal(self, id_sucursal):
        """Obtiene el detalle completo de una sucursal con sus horarios"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Obtener información de la sucursal
            sql_sucursal = """
                SELECT 
                    s.id_sucursal,
                    s.nombre,
                    s.direccion,
                    s.telefono,
                    s.img_logo,
                    s.img_banner,
                    e.nombre_comercial as empresa,
                    e.sitio_web,
                    e.descripcion as empresa_descripcion,
                    d.nombre as distrito,
                    s.estado
                FROM sucursal s
                LEFT JOIN empresa e ON s.id_empresa = e.id_empresa
                LEFT JOIN distrito d ON s.id_dist = d.id_dist
                WHERE s.id_sucursal = %s AND s.estado = TRUE
            """
            
            cursor.execute(sql_sucursal, (id_sucursal,))
            sucursal_data = cursor.fetchone()
            
            if not sucursal_data:
                cursor.close()
                con.close()
                return False, "Sucursal no encontrada"
            
            # Obtener horarios de la sucursal
            sql_horarios = """
                SELECT 
                    dia,
                    hora_inicio,
                    hora_fin
                FROM horario_sucursal
                WHERE id_sucursal = %s AND estado = TRUE
                ORDER BY dia
            """
            
            cursor.execute(sql_horarios, (id_sucursal,))
            horarios_data = cursor.fetchall()
            
            # Mapeo de días
            dias_semana = {
                0: "Domingo",
                1: "Lunes",
                2: "Martes",
                3: "Miércoles",
                4: "Jueves",
                5: "Viernes",
                6: "Sábado"
            }
            
            horarios = []
            for horario in horarios_data:
                horarios.append({
                    "dia": dias_semana.get(horario['dia'], ""),
                    "dia_numero": horario['dia'],
                    "hora_inicio": str(horario['hora_inicio'])[:5],  # HH:MM
                    "hora_fin": str(horario['hora_fin'])[:5]  # HH:MM
                })
            
            # Construir respuesta completa
            sucursal = {
                "id_sucursal": sucursal_data['id_sucursal'],
                "nombre": sucursal_data['nombre'],
                "direccion": sucursal_data['direccion'],
                "telefono": sucursal_data['telefono'],
                "img_logo": sucursal_data['img_logo'] if sucursal_data['img_logo'] else '',
                "img_banner": sucursal_data['img_banner'] if sucursal_data['img_banner'] else '',
                "empresa": sucursal_data['empresa'] if sucursal_data['empresa'] else '',
                "sitio_web": sucursal_data['sitio_web'] if sucursal_data['sitio_web'] else '',
                "empresa_descripcion": sucursal_data['empresa_descripcion'] if sucursal_data['empresa_descripcion'] else '',
                "distrito": sucursal_data['distrito'] if sucursal_data['distrito'] else '',
                "estado": "Abierto" if sucursal_data['estado'] else "Cerrado",
                "horarios": horarios
            }
            
            cursor.close()
            con.close()
            
            return True, sucursal
                
        except Exception as e:
            return False, f"Error al obtener detalle de sucursal: {str(e)}"