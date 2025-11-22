from flask import Blueprint, request, jsonify, render_template, session
from models.usuario import Usuario
import jwt
from datetime import datetime, timedelta
from conexionBD import Conexion
from config import Config
import cloudinary.uploader

ws_usuario = Blueprint('ws_usuario', __name__)
usuario_model = Usuario()

# Clave secreta para JWT
SECRET_KEY = Config.SECRET_KEY

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Verificar extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def subir_a_cloudinary(file, folder):
    """Subir imagen a Cloudinary"""
    try:
        if not file:
            return None
        
        print(f"📤 Subiendo foto de usuario a Cloudinary: {file.filename}")
        
        resultado = cloudinary.uploader.upload(
            file,
            folder=f"centro_comercial/{folder}",
            resource_type="auto",
            overwrite=True,
            invalidate=True
        )
        
        url = resultado['secure_url']
        print(f"✅ URL Cloudinary: {url}")
        return url
        
    except Exception as e:
        print(f"❌ Error Cloudinary: {str(e)}")
        return None

# ==================== VISTAS HTML ====================

@ws_usuario.route('/login', methods=['GET'])
def login_page():
    """Página de login"""
    return render_template('login.html')

@ws_usuario.route('/dashboard', methods=['GET'])
def dashboard_page():
    """Página de dashboard"""
    return render_template('dashboard.html')

# ==================== API ENDPOINTS ====================

@ws_usuario.route('/api/login', methods=['POST'])
def login():
    """Login de usuario - CORREGIDO"""
    try:
        print("\n" + "="*60)
        print("🔐 INICIANDO PROCESO DE LOGIN")
        print("="*60)
        
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        print(f"📧 Email recibido: {email}")
        print(f"🔑 Password recibido: {'*' * len(password) if password else 'None'}")
        
        if not email or not password:
            print("❌ ERROR: Email o contraseña vacíos")
            return jsonify({
                'status': False,
                'message': 'Email y contraseña son requeridos'
            }), 400
        
        # Usar el modelo Usuario que YA maneja usuario_rol
        print("🔍 Llamando a usuario_model.login()...")
        exito, resultado = usuario_model.login(email, password)
        
        print(f"📊 Resultado del login: {exito}")
        
        if not exito:
            print(f"❌ Login fallido: {resultado}")
            return jsonify({
                'status': False,
                'message': resultado
            }), 401
        
        # Si llegamos aquí, el login fue exitoso
        user_data = resultado
        print("✅ Login exitoso!")
        print(f"👤 Usuario: {user_data.get('nomusuario')}")
        print(f"🎭 Roles: {[r['nombre'] for r in user_data.get('roles', [])]}")
        
        # Generar token JWT
        token = jwt.encode({
            'id_usuario': user_data['id_usuario'],
            'email': user_data['email'],
            'exp': datetime.utcnow() + timedelta(days=7)
        }, SECRET_KEY, algorithm='HS256')
        
        print(f"🎟️ Token generado: {token[:50]}...")
        print("="*60)
        print("✅ LOGIN COMPLETADO CON ÉXITO")
        print("="*60 + "\n")
        
        return jsonify({
            'status': True,
            'message': 'Login exitoso',
            'token': token,
            'user': user_data
        }), 200
        
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO EN LOGIN: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500

@ws_usuario.route('/api/logout', methods=['POST'])
def logout():
    """Cerrar sesión"""
    try:
        session.clear()
        return jsonify({
            'status': True,
            'message': 'Sesión cerrada correctamente'
        }), 200
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error al cerrar sesión: {str(e)}'
        }), 500

@ws_usuario.route('/api/verify-token', methods=['POST'])
def verify_token():
    """Verificar token JWT"""
    try:
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({
                'status': False, 
                'message': 'Token no proporcionado'
            }), 401
        
        # Remover "Bearer " si existe
        if token.startswith('Bearer '):
            token = token[7:]
        
        # Decodificar token
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        
        return jsonify({
            'status': True,
            'user': payload
        }), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({
            'status': False, 
            'message': 'Token expirado'
        }), 401
    except jwt.InvalidTokenError:
        return jsonify({
            'status': False, 
            'message': 'Token inválido'
        }), 401
    except Exception as e:
        return jsonify({
            'status': False, 
            'message': f'Error: {str(e)}'
        }), 500

@ws_usuario.route('/api/usuario/<int:id_usuario>', methods=['GET'])
def obtener_usuario(id_usuario):
    """Obtener datos de usuario por ID"""
    try:
        resultado, data = usuario_model.obtener_por_id(id_usuario)
        
        if resultado:
            return jsonify({
                'status': True,
                'data': data,
                'message': 'Usuario obtenido correctamente'
            }), 200
        else:
            return jsonify({
                'status': False,
                'data': None,
                'message': data
            }), 404
            
    except Exception as e:
        return jsonify({
            'status': False,
            'data': None,
            'message': f'Error: {str(e)}'
        }), 500

@ws_usuario.route('/api/usuario/validar-email', methods=['POST'])
def validar_email():
    """Validar si el email ya existe"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({
                'status': False,
                'data': None,
                'message': 'Email requerido'
            }), 400
        
        existe = usuario_model.validar_email(email)
        
        if existe:
            return jsonify({
                'status': False,
                'data': None,
                'message': 'Email ya registrado'
            }), 409
        else:
            return jsonify({
                'status': True,
                'data': None,
                'message': 'Email disponible'
            }), 200
            
    except Exception as e:
        return jsonify({
            'status': False,
            'data': None,
            'message': f'Error: {str(e)}'
        }), 500

@ws_usuario.route('/api/usuario/cambiar-password', methods=['POST'])
def cambiar_password():
    """Cambiar contraseña del usuario"""
    try:
        data = request.get_json()
        id_usuario = data.get('id_usuario')
        password_actual = data.get('password_actual')
        password_nueva = data.get('password_nueva')
        
        if not all([id_usuario, password_actual, password_nueva]):
            return jsonify({
                'status': False,
                'message': 'Todos los campos son requeridos'
            }), 400
        
        resultado, mensaje = usuario_model.cambiar_password(
            id_usuario, 
            password_actual, 
            password_nueva
        )
        
        if resultado:
            return jsonify({
                'status': True,
                'message': mensaje
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': mensaje
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500

@ws_usuario.route('/api/usuario/registrar', methods=['POST'])
def registrar():
    """Registrar nuevo usuario"""
    try:
        data = request.get_json()
        
        nomusuario = data.get('nomusuario')
        email = data.get('email')
        password = data.get('password')
        id_persona = data.get('id_persona')
        id_rol = data.get('id_rol')
        id_empresa = data.get('id_empresa')  # Opcional
        
        if not all([nomusuario, email, password, id_persona, id_rol]):
            return jsonify({
                'status': False,
                'message': 'Faltan datos obligatorios'
            }), 400
        
        # Validar si email ya existe
        if usuario_model.validar_email(email):
            return jsonify({
                'status': False,
                'message': 'El email ya está registrado'
            }), 409
        
        # Registrar usuario
        resultado, data_result = usuario_model.registrar(
            nomusuario, 
            email, 
            password, 
            id_persona, 
            id_rol, 
            id_empresa
        )
        
        if resultado:
            return jsonify({
                'status': True,
                'data': {'id_usuario': data_result},
                'message': 'Usuario registrado correctamente'
            }), 201
        else:
            return jsonify({
                'status': False,
                'message': data_result
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500

@ws_usuario.route('/api/postular-empresa', methods=['POST'])
def postular_empresa():
    """Crear solicitud de empresa"""
    try:
        data = request.get_json()
        id_usuario = data.get('id_usuario')
        
        if not id_usuario:
            return jsonify({
                'status': False,
                'message': 'Usuario no identificado'
            }), 401
        
        # Validar distrito
        id_dist = data.get('id_dist')
        if not id_dist:
            return jsonify({
                'status': False,
                'message': 'Debe seleccionar un distrito válido'
            }), 400
        
        con = Conexion().open
        cursor = con.cursor()
        
        # Verificar si ya tiene solicitud pendiente
        cursor.execute("""
            SELECT COUNT(*) as total 
            FROM solicitud_empresa 
            WHERE id_usuario = %s AND estado = 'pendiente'
        """, [id_usuario])
        
        ya_tiene_solicitud = cursor.fetchone()['total'] > 0
        
        if ya_tiene_solicitud:
            cursor.close()
            con.close()
            return jsonify({
                'status': False,
                'message': 'Ya tienes una solicitud pendiente. Espera la revisión del administrador.'
            }), 400
        
        # Validar que el distrito existe
        cursor.execute("SELECT 1 FROM distrito WHERE id_dist = %s AND estado = TRUE", [id_dist])
        if not cursor.fetchone():
            cursor.close()
            con.close()
            return jsonify({
                'status': False,
                'message': 'El distrito seleccionado no es válido'
            }), 400
        
        # Llamar a la función
        cursor.execute("""
            SELECT fn_solicitud_empresa_crear(%s, %s, %s, %s, %s, %s, %s, %s, %s) as resultado
        """, [
            id_usuario,
            data.get('ruc'),
            data.get('razon_social'),
            data.get('nombre_comercial'),
            data.get('descripcion'),
            data.get('telefono'),
            data.get('email'),
            id_dist,
            data.get('direccion')
        ])
        
        resultado_row = cursor.fetchone()
        resultado = resultado_row['resultado'] if resultado_row else -1
        
        con.commit()
        cursor.close()
        con.close()
        
        if resultado == -1:
            return jsonify({
                'status': False,
                'message': 'Error: Datos inválidos o RUC duplicado'
            }), 400
        
        return jsonify({
            'status': True,
            'message': '✅ Solicitud enviada correctamente. Será revisada por un administrador.',
            'id_solicitud': resultado
        }), 201
            
    except Exception as e:
        print(f"💥 ERROR COMPLETO: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500
    
@ws_usuario.route('/api/usuario/registrar-completo', methods=['POST'])
def registrar_completo():
    """Registrar usuario completo con persona, dirección e imagen en Cloudinary"""
    try:
        from models.persona import Persona
        
        # Obtener datos del formulario
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        tipo_doc = request.form.get('tipo_doc')
        documento = request.form.get('documento')
        fecha_nacimiento = request.form.get('fecha_nacimiento')
        telefono = request.form.get('telefono')
        id_dist = request.form.get('id_dist')
        direccion = request.form.get('direccion')
        nomusuario = request.form.get('nomusuario')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # ✅ AGREGAR: google_id opcional
        google_id = request.form.get('google_id')  # Nuevo
        
        # ✅ MODIFICAR: Validar password solo si NO hay google_id
        if not google_id and not password:
            return jsonify({
                'status': False,
                'message': 'Contraseña es requerida para registro normal'
            }), 400
        
        # Validar campos obligatorios (sin password si hay google_id)
        campos_requeridos = [nombres, apellidos, tipo_doc, documento, fecha_nacimiento, telefono, id_dist, direccion, nomusuario, email]
        if not all(campos_requeridos):
            return jsonify({
                'status': False,
                'message': 'Todos los campos obligatorios son requeridos'
            }), 400
        
        # Validar email único
        if usuario_model.validar_email(email):
            return jsonify({
                'status': False,
                'message': 'El email ya está registrado'
            }), 409
        
        # 1. Crear persona
        persona_model = Persona()
        exito, id_persona = persona_model.crear(
            nombres, apellidos, int(tipo_doc), documento, 
            fecha_nacimiento, telefono, int(id_dist), direccion
        )
        
        if not exito:
            return jsonify({
                'status': False,
                'message': f'Error al crear persona: {id_persona}'
            }), 400
        
        # 2. Procesar imagen con Cloudinary
        img_logo_url = None
        if 'img_logo' in request.files:
            file = request.files['img_logo']
            if file and file.filename and allowed_file(file.filename):
                img_logo_url = subir_a_cloudinary(file, 'usuarios')
        
        # 3. ✅ MODIFICAR: Hash de password solo si NO hay google_id
        password_hash = None
        if password and not google_id:
            password_hash = usuario_model.ph.hash(password)
        
        # 4. ✅ MODIFICAR: Crear usuario con fn_usuario_crear (ya acepta google_id)
        con = Conexion().open
        cursor = con.cursor()
        
        cursor.execute("""
            SELECT fn_usuario_crear(%s, %s, %s, %s, %s, %s, %s, %s) as id_usuario
        """, [
            nomusuario,      # p_nomusuario
            id_persona,      # p_id_persona
            email,           # p_email
            password_hash,   # p_password_hash (puede ser NULL)
            3,               # p_id_rol (Cliente)
            img_logo_url,    # p_img_logo
            None,            # p_id_empresa
            google_id        # p_google_id (NUEVO)
        ])
        
        resultado = cursor.fetchone()
        id_usuario = resultado['id_usuario'] if resultado else -1
        
        con.commit()
        cursor.close()
        con.close()
        
        if id_usuario <= 0:
            return jsonify({
                'status': False,
                'message': 'Error al crear usuario'
            }), 400
        
        # 5. Crear dirección del cliente
        con = Conexion().open
        cursor = con.cursor()
        cursor.execute(
            "INSERT INTO direccion_cliente (id_usuario, id_distrito, direccion, estado) VALUES (%s, %s, %s, TRUE)",
            [id_usuario, int(id_dist), direccion]
        )
        con.commit()
        cursor.close()
        con.close()
        
        return jsonify({
            'status': True,
            'message': 'Usuario registrado correctamente',
            'data': {'id_usuario': id_usuario}
        }), 201
            
    except Exception as e:
        print(f"Error en registro completo: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500

@ws_usuario.route('/api/usuario/actualizar-foto', methods=['POST'])
def actualizar_foto():
    """Actualizar foto de perfil con Cloudinary"""
    try:
        if 'foto' not in request.files:
            return jsonify({
                'status': False,
                'message': 'No se envió ninguna imagen'
            }), 400
        
        file = request.files['foto']
        id_usuario = request.form.get('id_usuario')
        
        if not id_usuario:
            return jsonify({
                'status': False,
                'message': 'ID de usuario no proporcionado'
            }), 400
        
        if file.filename == '':
            return jsonify({
                'status': False,
                'message': 'Archivo sin nombre'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'status': False,
                'message': 'Formato de imagen no permitido. Use: png, jpg, jpeg, gif, webp'
            }), 400
        
        # ✅ Subir a Cloudinary
        img_logo_url = subir_a_cloudinary(file, 'usuarios')
        
        if not img_logo_url:
            return jsonify({
                'status': False,
                'message': 'Error al subir la imagen a Cloudinary'
            }), 500
        
        # Actualizar en base de datos
        con = Conexion().open
        cursor = con.cursor()
        
        cursor.execute("""
            UPDATE usuario 
            SET img_logo = %s 
            WHERE id_usuario = %s
        """, [img_logo_url, id_usuario])
        
        con.commit()
        cursor.close()
        con.close()
        
        return jsonify({
            'status': True,
            'message': 'Foto actualizada correctamente',
            'img_logo': img_logo_url
        }), 200
        
    except Exception as e:
        print(f"💥 ERROR en actualizar_foto: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': False,
            'message': f'Error al actualizar foto: {str(e)}'
        }), 500

@ws_usuario.route('/api/solicitudes-empresa/pendientes', methods=['GET'])
def listar_solicitudes_pendientes():
    """Listar solicitudes pendientes"""
    try:
        con = Conexion().open
        cursor = con.cursor()
        cursor.execute("SELECT fn_solicitud_empresa_listar_pendientes()")
        resultado = cursor.fetchone()[0]
        cursor.close()
        con.close()
        
        return jsonify({
            'status': True,
            'data': resultado or []
        }), 200
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500


@ws_usuario.route('/api/solicitudes-empresa/todas', methods=['GET'])
def listar_todas_solicitudes():
    """Listar todas las solicitudes"""
    try:
        con = Conexion().open
        cursor = con.cursor()
        cursor.execute("SELECT fn_solicitud_empresa_listar_todas()")
        resultado = cursor.fetchone()[0]
        cursor.close()
        con.close()
        
        return jsonify({
            'status': True,
            'data': resultado or []
        }), 200
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500


@ws_usuario.route('/api/solicitudes-empresa/<int:id_solicitud>', methods=['GET'])
def obtener_solicitud(id_solicitud):
    """Obtener una solicitud por ID"""
    try:
        con = Conexion().open
        cursor = con.cursor()
        cursor.execute("SELECT fn_solicitud_empresa_obtener(%s)", [id_solicitud])
        resultado = cursor.fetchone()[0]
        cursor.close()
        con.close()
        
        return jsonify({
            'status': True,
            'data': resultado
        }), 200
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500
    
@ws_usuario.route('/api/solicitudes-empresa/aprobar/<int:id_solicitud>', methods=['PATCH'])
def aprobar_solicitud(id_solicitud):
    """Aprobar solicitud y crear empresa"""
    try:
        data = request.get_json()
        observaciones = data.get('observaciones', '')
        
        con = Conexion().open
        cursor = con.cursor()
        cursor.execute("SELECT fn_solicitud_empresa_aprobar(%s, %s)", [id_solicitud, observaciones])
        resultado = cursor.fetchone()[0]
        con.commit()
        cursor.close()
        con.close()
        
        if resultado == -1:
            return jsonify({
                'status': False,
                'message': 'Error al aprobar la solicitud'
            }), 400
        
        return jsonify({
            'status': True,
            'message': '✅ Solicitud aprobada',
            'id_empresa': resultado
        }), 200
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500


@ws_usuario.route('/api/solicitudes-empresa/rechazar/<int:id_solicitud>', methods=['DELETE'])
def rechazar_solicitud(id_solicitud):
    """Rechazar solicitud"""
    try:
        data = request.get_json()
        observaciones = data.get('observaciones', 'Solicitud rechazada')
        
        con = Conexion().open
        cursor = con.cursor()
        cursor.execute("SELECT fn_solicitud_empresa_rechazar(%s, %s)", [id_solicitud, observaciones])
        resultado = cursor.fetchone()[0]
        con.commit()
        cursor.close()
        con.close()
        
        if resultado == -1:
            return jsonify({
                'status': False,
                'message': 'Error al rechazar la solicitud'
            }), 400
        
        return jsonify({
            'status': True,
            'message': '✅ Solicitud rechazada'
        }), 200
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500
    
@ws_usuario.route('/api/usuario/actualizar-perfil', methods=['POST'])
def actualizar_perfil():
    """Actualizar perfil de usuario"""
    try:
        data = request.get_json()
        id_usuario = data.get('id_usuario')
        id_persona = data.get('id_persona')
        
        nombres = data.get('nombres')
        apellidos = data.get('apellidos')
        telefono = data.get('telefono')
        direccion = data.get('direccion')
        fecha_nacimiento = data.get('fecha_nacimiento')
        
        # Validaciones
        if not all([id_usuario, id_persona, nombres, apellidos, telefono, direccion, fecha_nacimiento]):
            return jsonify({
                'status': False,
                'message': 'Todos los campos son requeridos'
            }), 400
        
        con = Conexion().open
        cursor = con.cursor()
        
        # Actualizar persona
        cursor.execute("""
            UPDATE persona 
            SET nombres = %s, apellidos = %s, telefono = %s, 
                direccion = %s, fecha_nacimiento = %s
            WHERE id_persona = %s AND estado = TRUE
        """, [nombres, apellidos, telefono, direccion, fecha_nacimiento, id_persona])
        
        if cursor.rowcount == 0:
            cursor.close()
            con.close()
            return jsonify({
                'status': False,
                'message': 'No se pudo actualizar. Persona no encontrada.'
            }), 404
        
        con.commit()
        cursor.close()
        con.close()
        
        return jsonify({
            'status': True,
            'message': 'Perfil actualizado correctamente'
        }), 200
        
    except Exception as e:
        print(f"💥 ERROR en actualizar_perfil: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': False,
            'message': f'Error al actualizar perfil: {str(e)}'
        }), 500


# ✅ AGREGAR ESTOS ENDPOINTS AL FINAL DEL ARCHIVO

@ws_usuario.route('/api/usuario/google/registro', methods=['POST'])
def registro_google():
    """Registrar o login con Google Sign-In"""
    try:
        data = request.get_json()
        
        google_id = data.get('google_id')
        email = data.get('email')
        nombres = data.get('nombres', '').strip()
        apellidos = data.get('apellidos', '').strip()
        img_logo = data.get('img_logo')
        
        print("\n" + "="*60)
        print("🔵 REGISTRO/LOGIN CON GOOGLE")
        print("="*60)
        print(f"📧 Email: {email}")
        print(f"🆔 Google ID: {google_id}")
        print(f"👤 Nombre: {nombres} {apellidos}")
        print("="*60)
        
        # Validar datos obligatorios
        if not all([google_id, email, nombres, apellidos]):
            return jsonify({
                'status': False,
                'message': 'Datos de Google incompletos'
            }), 400
        
        # Llamar a función SQL
        con = Conexion().open
        cursor = con.cursor()
        
        cursor.execute("""
            SELECT fn_usuario_registrar_google(%s, %s, %s, %s, %s) as resultado
        """, [google_id, email, nombres, apellidos, img_logo])
        
        resultado = cursor.fetchone()['resultado']
        
        cursor.close()
        con.close()
        
        print(f"📊 Resultado SQL: {resultado}")
        
        if resultado['success']:
            user_data = resultado['data']
            
            # Generar token JWT
            token = jwt.encode({
                'id_usuario': user_data['id_usuario'],
                'email': user_data['email'],
                'exp': datetime.utcnow() + timedelta(days=7)
            }, SECRET_KEY, algorithm='HS256')
            
            print(f"✅ Google Sign-In exitoso")
            print(f"🎟️ Token generado")
            print("="*60 + "\n")
            
            return jsonify({
                'status': True,
                'message': resultado['message'],
                'token': token,
                'user': user_data
            }), 200
        else:
            print(f"❌ Error: {resultado['message']}")
            return jsonify({
                'status': False,
                'message': resultado['message']
            }), 400
            
    except Exception as e:
        print(f"\n💥 ERROR EN GOOGLE SIGN-IN: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500


@ws_usuario.route('/api/usuario/google/login', methods=['POST'])
def login_google():
    """Login con Google ID"""
    try:
        data = request.get_json()
        google_id = data.get('google_id')
        
        if not google_id:
            return jsonify({
                'status': False,
                'message': 'Google ID no proporcionado'
            }), 400
        
        print(f"\n🔵 LOGIN CON GOOGLE ID: {google_id}")
        
        # Llamar a función SQL
        con = Conexion().open
        cursor = con.cursor()
        
        cursor.execute("""
            SELECT fn_usuario_login_google(%s) as resultado
        """, [google_id])
        
        resultado = cursor.fetchone()['resultado']
        
        cursor.close()
        con.close()
        
        if resultado['success']:
            user_data = resultado['data']
            
            # Generar token JWT
            token = jwt.encode({
                'id_usuario': user_data['id_usuario'],
                'email': user_data['email'],
                'exp': datetime.utcnow() + timedelta(days=7)
            }, SECRET_KEY, algorithm='HS256')
            
            print(f"✅ Login Google exitoso\n")
            
            return jsonify({
                'status': True,
                'message': resultado['message'],
                'token': token,
                'user': user_data
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': resultado['message']
            }), 404
            
    except Exception as e:
        print(f"💥 ERROR: {str(e)}")
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500
    

@ws_usuario.route('/api/usuario/registrar-simple', methods=['POST'])
def registrar_simple():
    """Registrar usuario simplificado"""
    try:
        data = request.get_json()
        
        nombres = data.get('nombres')
        apellidos = data.get('apellidos')
        email = data.get('email')
        password = data.get('password')
        google_id = data.get('google_id')
        img_logo = data.get('img_logo')
        
        # Validar campos obligatorios
        if not all([nombres, apellidos, email]):
            return jsonify({
                'status': False,
                'message': 'Nombres, apellidos y email son requeridos'
            }), 400
        
        # Validar password si NO hay google_id
        if not google_id and not password:
            return jsonify({
                'status': False,
                'message': 'Contraseña requerida para registro normal'
            }), 400
        
        # Registrar usuario
        exito, resultado = usuario_model.registrar_simplificado(
            nombres, apellidos, email, password, google_id, img_logo
        )
        
        if exito and resultado.get('success'):
            user_data = resultado['data']
            
            # Generar token JWT
            token = jwt.encode({
                'id_usuario': user_data['id_usuario'],
                'email': user_data['email'],
                'exp': datetime.utcnow() + timedelta(days=7)
            }, SECRET_KEY, algorithm='HS256')
            
            return jsonify({
                'status': True,
                'message': resultado['message'],
                'token': token,
                'user': user_data
            }), 201
        else:
            return jsonify({
                'status': False,
                'message': resultado.get('message', 'Error al registrar')
            }), 400
            
    except Exception as e:
        print(f"Error en registrar_simple: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500


@ws_usuario.route('/api/usuario/google/registro-simple', methods=['POST'])
def registro_google_simple():
    """Registrar con Google simplificado"""
    try:
        data = request.get_json()
        
        google_id = data.get('google_id')
        email = data.get('email')
        nombres = data.get('nombres', '').strip()
        apellidos = data.get('apellidos', '').strip()
        img_logo = data.get('img_logo')
        
        if not all([google_id, email, nombres, apellidos]):
            return jsonify({
                'status': False,
                'message': 'Datos de Google incompletos'
            }), 400
        
        # Registrar con google_id
        exito, resultado = usuario_model.registrar_simplificado(
            nombres, apellidos, email, None, google_id, img_logo
        )
        
        if exito and resultado.get('success'):
            user_data = resultado['data']
            
            # Generar token JWT
            token = jwt.encode({
                'id_usuario': user_data['id_usuario'],
                'email': user_data['email'],
                'exp': datetime.utcnow() + timedelta(days=7)
            }, SECRET_KEY, algorithm='HS256')
            
            return jsonify({
                'status': True,
                'message': resultado['message'],
                'token': token,
                'user': user_data
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': resultado.get('message', 'Error al registrar con Google')
            }), 400
            
    except Exception as e:
        print(f"Error en registro_google_simple: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500
    
@ws_usuario.route('/api/usuarios/listar', methods=['GET'])
def listar_usuarios():
    """Listar todos los usuarios con sus datos de persona"""
    try:
        con = Conexion().open
        cursor = con.cursor()
        
        sql = """
            SELECT 
                u.id_usuario,
                u.nomusuario,
                u.email,
                u.img_logo,
                u.estado,
                p.nombres,
                p.apellidos,
                p.telefono,
                COALESCE(
                    (
                        SELECT jsonb_agg(
                            jsonb_build_object('id_rol', r.id_rol, 'nombre', r.nombre)
                        )
                        FROM usuario_rol ur
                        INNER JOIN rol r ON ur.id_rol = r.id_rol
                        WHERE ur.id_usuario = u.id_usuario AND ur.estado = TRUE
                    ),
                    '[]'::jsonb
                ) as roles
            FROM usuario u
            INNER JOIN persona p ON u.id_persona = p.id_persona
            ORDER BY u.created_at DESC
        """
        
        cursor.execute(sql)
        usuarios = cursor.fetchall()
        
        cursor.close()
        con.close()
        
        return jsonify({
            'status': True,
            'data': usuarios
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500
    
@ws_usuario.route('/api/usuario/actualizar-nombre/<int:id_usuario>', methods=['PUT'])
def actualizar_nombre_usuario(id_usuario):
    """Actualizar nombre de usuario"""
    try:
        data = request.get_json()
        nomusuario = data.get('nomusuario')
        
        if not nomusuario:
            return jsonify({
                'status': False,
                'message': 'Nombre de usuario requerido'
            }), 400
        
        con = Conexion().open
        cursor = con.cursor()
        
        cursor.execute("""
            UPDATE usuario 
            SET nomusuario = %s 
            WHERE id_usuario = %s
        """, [nomusuario, id_usuario])
        
        con.commit()
        cursor.close()
        con.close()
        
        return jsonify({
            'status': True,
            'message': 'Nombre de usuario actualizado'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500

@ws_usuario.route('/api/usuario/actualizar-foto', methods=['POST'])
def actualizar_foto():
    """Actualizar foto de perfil con Cloudinary"""
    try:
        if 'foto' not in request.files:
            return jsonify({
                'status': False,
                'message': 'No se envió ninguna imagen'
            }), 400
        
        file = request.files['foto']
        id_usuario = request.form.get('id_usuario')
        
        if not id_usuario:
            return jsonify({
                'status': False,
                'message': 'ID de usuario no proporcionado'
            }), 400
        
        if file.filename == '':
            return jsonify({
                'status': False,
                'message': 'Archivo sin nombre'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'status': False,
                'message': 'Formato no permitido. Use: png, jpg, jpeg, gif, webp'
            }), 400
        
        print(f"\n📸 Subiendo foto para usuario ID: {id_usuario}")
        
        # Subir a Cloudinary
        img_logo_url = subir_a_cloudinary(file, 'usuarios')
        
        if not img_logo_url:
            return jsonify({
                'status': False,
                'message': 'Error al subir la imagen a Cloudinary'
            }), 500
        
        print(f"✅ URL Cloudinary: {img_logo_url}")
        
        # Actualizar en BD
        con = Conexion().open
        cursor = con.cursor()
        
        cursor.execute("""
            UPDATE usuario 
            SET img_logo = %s 
            WHERE id_usuario = %s
        """, [img_logo_url, id_usuario])
        
        con.commit()
        cursor.close()
        con.close()
        
        print(f"✅ Foto actualizada en BD\n")
        
        return jsonify({
            'status': True,
            'message': 'Foto actualizada correctamente',
            'img_logo': img_logo_url
        }), 200
        
    except Exception as e:
        print(f"💥 ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': False,
            'message': f'Error: {str(e)}'
        }), 500

    

