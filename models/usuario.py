from conexionBD import Conexion
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

class Usuario:
    def __init__(self):
        self.ph = PasswordHasher()
    
    def login(self, email, password):
        """Login de usuario con Argon2 - CORREGIDO para usar usuario_rol"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # ✅ CORRECCIÓN: Ya NO existe id_rol en usuario
            sql = """
                SELECT 
                    u.id_usuario, 
                    u.nomusuario, 
                    u.email, 
                    u.password_hash,
                    u.id_empresa,
                    u.img_logo,
                    p.nombres,
                    p.apellidos,
                    p.id_persona
                FROM usuario u
                INNER JOIN persona p ON u.id_persona = p.id_persona
                WHERE u.email = %s AND u.estado = true
            """
            
            cursor.execute(sql, [email])
            resultado = cursor.fetchone()
            
            if not resultado:
                cursor.close()
                con.close()
                return False, 'Usuario no encontrado'
            
            try:
                # Verificar password con Argon2
                self.ph.verify(resultado['password_hash'], password)
                
                # ✅ Obtener roles desde usuario_rol
                sql_roles = """
                    SELECT r.id_rol, r.nombre
                    FROM usuario_rol ur
                    INNER JOIN rol r ON ur.id_rol = r.id_rol
                    WHERE ur.id_usuario = %s AND ur.estado = TRUE AND r.estado = TRUE
                    ORDER BY r.nombre
                """
                
                cursor.execute(sql_roles, [resultado['id_usuario']])
                roles = cursor.fetchall()
                
                cursor.close()
                con.close()
                
                # Si no tiene roles activos, no permitir login
                if not roles:
                    return False, 'Usuario sin roles asignados'
                
                # Retornar datos del usuario con roles
                return True, {
                    'id_usuario': resultado['id_usuario'],
                    'nomusuario': resultado['nomusuario'],
                    'email': resultado['email'],
                    'id_empresa': resultado['id_empresa'],
                    'img_logo': resultado['img_logo'],
                    'nombres': resultado['nombres'],
                    'apellidos': resultado['apellidos'],
                    'id_persona': resultado['id_persona'],
                    'roles': [{'id_rol': r['id_rol'], 'nombre': r['nombre']} for r in roles]
                }
                
            except VerifyMismatchError:
                cursor.close()
                con.close()
                return False, 'Contraseña incorrecta'
                
        except Exception as e:
            return False, f"Error en login: {str(e)}"
    
    def registrar(self, nomusuario, email, password, id_persona, id_rol, id_empresa=None):
        """Registrar nuevo usuario - USA fn_usuario_crear"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Hash de password con Argon2
            password_hash = self.ph.hash(password)
            
            # Usar función de PostgreSQL
            sql = """
                SELECT fn_usuario_crear(%s, %s, %s, %s, %s, %s, %s) as id_usuario
            """
            
            cursor.execute(sql, [
                nomusuario, 
                id_persona, 
                email, 
                password_hash, 
                id_rol,  # Se usará para asignar en usuario_rol
                None,    # img_logo
                id_empresa
            ])
            
            resultado = cursor.fetchone()
            
            con.commit()
            cursor.close()
            con.close()
            
            if resultado and resultado['id_usuario'] > 0:
                return True, resultado['id_usuario']
            else:
                return False, 'No se pudo crear el usuario. Email puede estar duplicado.'
                
        except Exception as e:
            return False, f"Error al registrar: {str(e)}"
    
    def validar_email(self, email):
        """Verificar si el email ya existe"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = "SELECT email FROM usuario WHERE email = %s"
            cursor.execute(sql, [email])
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            return resultado is not None
            
        except Exception as e:
            return False
    
    def obtener_por_id(self, id_usuario):
        """Obtener datos completos del usuario por ID - CORREGIDO para usuario_rol"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT 
                    u.id_usuario,
                    u.nomusuario,
                    u.email,
                    u.img_logo,
                    u.id_empresa,
                    p.id_persona,
                    p.nombres,
                    p.apellidos,
                    p.documento,
                    p.telefono,
                    e.ruc,
                    e.razon_social,
                    e.nombre_comercial
                FROM usuario u
                INNER JOIN persona p ON u.id_persona = p.id_persona
                LEFT JOIN empresa e ON u.id_empresa = e.id_empresa
                WHERE u.id_usuario = %s AND u.estado = TRUE
            """
            
            cursor.execute(sql, [id_usuario])
            resultado = cursor.fetchone()
            
            if not resultado:
                cursor.close()
                con.close()
                return False, 'Usuario no encontrado'
            
            # Obtener roles
            sql_roles = """
                SELECT r.id_rol, r.nombre
                FROM usuario_rol ur
                INNER JOIN rol r ON ur.id_rol = r.id_rol
                WHERE ur.id_usuario = %s AND ur.estado = TRUE AND r.estado = TRUE
            """
            
            cursor.execute(sql_roles, [id_usuario])
            roles = cursor.fetchall()
            
            cursor.close()
            con.close()
            
            return True, {
                'id_usuario': resultado['id_usuario'],
                'nomusuario': resultado['nomusuario'],
                'email': resultado['email'],
                'img_logo': resultado['img_logo'],
                'persona': {
                    'id_persona': resultado['id_persona'],
                    'nombres': resultado['nombres'],
                    'apellidos': resultado['apellidos'],
                    'documento': resultado['documento'],
                    'telefono': resultado['telefono']
                },
                'roles': [{'id_rol': r['id_rol'], 'nombre': r['nombre']} for r in roles],
                'empresa': {
                    'id_empresa': resultado['id_empresa'],
                    'ruc': resultado['ruc'],
                    'razon_social': resultado['razon_social'],
                    'nombre_comercial': resultado['nombre_comercial']
                } if resultado['id_empresa'] else None
            }
                
        except Exception as e:
            return False, f"Error al obtener usuario: {str(e)}"
    
    def cambiar_password(self, id_usuario, password_actual, password_nueva):
        """Cambiar contraseña del usuario"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Obtener password actual
            sql = "SELECT password_hash FROM usuario WHERE id_usuario = %s"
            cursor.execute(sql, [id_usuario])
            resultado = cursor.fetchone()
            
            if not resultado:
                cursor.close()
                con.close()
                return False, 'Usuario no encontrado'
            
            try:
                # Verificar password actual
                self.ph.verify(resultado['password_hash'], password_actual)
                
                # Hash nueva password
                nuevo_hash = self.ph.hash(password_nueva)
                
                # Actualizar password
                sql_update = "UPDATE usuario SET password_hash = %s WHERE id_usuario = %s"
                cursor.execute(sql_update, [nuevo_hash, id_usuario])
                
                con.commit()
                cursor.close()
                con.close()
                
                return True, 'Contraseña actualizada correctamente'
                
            except VerifyMismatchError:
                cursor.close()
                con.close()
                return False, 'Contraseña actual incorrecta'
                
        except Exception as e:
            return False, f"Error al cambiar contraseña: {str(e)}"