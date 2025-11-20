from conexionBD import Conexion

class Persona:
    def __init__(self):
        pass
    
    def crear(self, nombres, apellidos, tipo_doc, documento, fecha_nacimiento, telefono, id_dist, direccion):
        """Crear persona"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                INSERT INTO persona (nombres, apellidos, tipo_doc, documento, fecha_nacimiento, telefono, id_dist, direccion, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                RETURNING id_persona
            """
            
            cursor.execute(sql, [nombres, apellidos, tipo_doc, documento, fecha_nacimiento, telefono, id_dist, direccion])
            resultado = cursor.fetchone()
            
            con.commit()
            cursor.close()
            con.close()
            
            return True, resultado['id_persona']
                
        except Exception as e:
            return False, f"Error al crear persona: {str(e)}"
    
    def actualizar(self, id_persona, nombres, apellidos, telefono, direccion, fecha_nacimiento):
        """Actualizar datos de persona - SIMPLIFICADO"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # ✅ SIMPLIFICADO: UPDATE directo sin COALESCE
            sql = """
                UPDATE persona 
                SET nombres = %s, 
                    apellidos = %s
            """
            
            params = [nombres, apellidos]
            
            # ✅ Solo actualizar si los campos tienen valor
            if telefono and telefono.strip():
                sql += ", telefono = %s"
                params.append(telefono)
            
            if direccion and direccion.strip():
                sql += ", direccion = %s"
                params.append(direccion)
            
            if fecha_nacimiento and fecha_nacimiento.strip():
                sql += ", fecha_nacimiento = %s"
                params.append(fecha_nacimiento)
            
            sql += " WHERE id_persona = %s AND estado = TRUE"
            params.append(id_persona)
            
            print(f"📋 SQL: {sql}")
            print(f"📦 Params: {params}")
            
            cursor.execute(sql, params)
            
            if cursor.rowcount == 0:
                cursor.close()
                con.close()
                return False, 'Persona no encontrada'
            
            con.commit()
            cursor.close()
            con.close()
            
            return True, 'Persona actualizada correctamente'
                
        except Exception as e:
            print(f"💥 ERROR SQL: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, f"Error al actualizar persona: {str(e)}"
    
    def obtener_por_id(self, id_persona):
        """Obtener datos de persona"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    p.id_persona,
                    p.nombres,
                    p.apellidos,
                    p.tipo_doc,
                    p.documento,
                    p.fecha_nacimiento,
                    p.telefono,
                    p.id_dist,
                    p.direccion,
                    d.nombre as distrito,
                    pr.nombre as provincia,
                    dep.nombre as departamento
                FROM persona p
                LEFT JOIN distrito d ON p.id_dist = d.id_dist
                LEFT JOIN provincia pr ON d.id_prov = pr.id_prov
                LEFT JOIN departamento dep ON pr.id_dep = dep.id_dep
                WHERE p.id_persona = %s AND p.estado = TRUE
            """
            
            cursor.execute(sql, [id_persona])
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            if resultado:
                return True, resultado
            else:
                return False, 'Persona no encontrada'
                
        except Exception as e:
            return False, f"Error: {str(e)}"