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
            
            sql = """
                SELECT 
                    u.id_usuario, 
                    u.nomusuario, 
                    u.email, 
                    u.password_hash,
                    u.google_id,
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
            
            # ✅ Validar cuenta de Google
            if resultado['google_id'] and not resultado['password_hash']:
                cursor.close()
                con.close()
                return False, 'Esta cuenta está vinculada con Google. Use "Continuar con Google"'
            
            # ✅ Validar password_hash existe
            if not resultado['password_hash']:
                cursor.close()
                con.close()
                return False, 'Cuenta sin contraseña configurada'
            
            try:
                # Verificar password con Argon2
                self.ph.verify(resultado['password_hash'], password)
                
                # Obtener roles desde usuario_rol
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
                
                if not roles:
                    return False, 'Usuario sin roles asignados'
                
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
    
    def registrar(self, nomusuario, email, password, id_persona, id_rol, id_empresa=None, google_id=None):
        """Registrar nuevo usuario - USA fn_usuario_crear"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Hash de password solo si existe
            password_hash = None
            if password:
                password_hash = self.ph.hash(password)
            
            # Usar función de PostgreSQL (8 parámetros)
            sql = """
                SELECT fn_usuario_crear(%s, %s, %s, %s, %s, %s, %s, %s) as id_usuario
            """
            
            cursor.execute(sql, [
                nomusuario, 
                id_persona, 
                email, 
                password_hash,
                id_rol,
                None,        # img_logo
                id_empresa,
                google_id
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
    
    def registrar_google(self, google_id, email, nombres, apellidos, img_logo=None):
        """Registrar usuario con Google Sign-In"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT fn_usuario_registrar_google(%s, %s, %s, %s, %s) as resultado
            """
            
            cursor.execute(sql, [google_id, email, nombres, apellidos, img_logo])
            resultado = cursor.fetchone()
            
            con.commit()
            cursor.close()
            con.close()
            
            if resultado and resultado['resultado']:
                return True, resultado['resultado']
            else:
                return False, 'Error al registrar con Google'
                
        except Exception as e:
            return False, f"Error en registro Google: {str(e)}"
    
    def login_google(self, google_id):
        """Login con Google ID"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            sql = """
                SELECT fn_usuario_login_google(%s) as resultado
            """
            
            cursor.execute(sql, [google_id])
            resultado = cursor.fetchone()
            
            cursor.close()
            con.close()
            
            if resultado and resultado['resultado']:
                return True, resultado['resultado']
            else:
                return False, 'Usuario no encontrado'
                
        except Exception as e:
            return False, f"Error en login Google: {str(e)}"
    
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
            
            sql = "SELECT password_hash FROM usuario WHERE id_usuario = %s"
            cursor.execute(sql, [id_usuario])
            resultado = cursor.fetchone()
            
            if not resultado:
                cursor.close()
                con.close()
                return False, 'Usuario no encontrado'
            
            try:
                self.ph.verify(resultado['password_hash'], password_actual)
                nuevo_hash = self.ph.hash(password_nueva)
                
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
        

    def registrar_simplificado(self, nombres, apellidos, email, password=None, google_id=None, img_logo=None):
        """Registrar usuario con datos mínimos"""
        try:
            con = Conexion().open
            cursor = con.cursor()
            
            # Hash de password solo si existe
            password_hash = None
            if password:
                password_hash = self.ph.hash(password)
            
            sql = """
                SELECT fn_usuario_registrar_simplificado(%s, %s, %s, %s, %s, %s) as resultado
            """
            
            cursor.execute(sql, [nombres, apellidos, email, password_hash, google_id, img_logo])
            resultado = cursor.fetchone()['resultado']
            
            con.commit()
            cursor.close()
            con.close()
            
            return True, resultado
                
        except Exception as e:
            return False, f"Error al registrar: {str(e)}"