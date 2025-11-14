from flask import Blueprint, request, jsonify, render_template, session
from models.usuario import Usuario
import jwt
from datetime import datetime, timedelta
from conexionBD import Conexion

ws_usuario = Blueprint('ws_usuario', __name__)
usuario_model = Usuario()

# Clave secreta para JWT (cambiar en producción)
SECRET_KEY = 'tu_clave_secreta_super_segura_2025'

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
        
        # Validar que el distrito existe
        cursor.execute("SELECT 1 FROM distrito WHERE id_dist = %s AND estado = TRUE", [id_dist])
        if not cursor.fetchone():
            cursor.close()
            con.close()
            return jsonify({
                'status': False,
                'message': 'El distrito seleccionado no es válido'
            }), 400
        
        print(f"🔍 DEBUG - Datos recibidos: {data}")
        
        # ✅ CORRECCIÓN: La función retorna directamente un valor, no necesita [0]
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
        
        # ✅ ACCEDER USANDO LA CLAVE DEL DICCIONARIO
        resultado_dict = cursor.fetchone()
        resultado = resultado_dict['resultado'] if resultado_dict else -1
        
        print(f"✅ Resultado de la función: {resultado}")
        
        con.commit()
        cursor.close()
        con.close()
        
        if resultado == -1:
            return jsonify({
                'status': False,
                'message': 'Error: Ya tienes una solicitud pendiente o los datos son inválidos'
            }), 400
        
        return jsonify({
            'status': True,
            'message': '✅ Solicitud enviada correctamente. Será revisada por un administrador.',
            'id_solicitud': resultado
        }), 201
            
    except KeyError as ke:
        print(f"💥 KeyError: {str(ke)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': False,
            'message': 'Error de configuración en el servidor'
        }), 500
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
    """Registrar usuario completo con persona y dirección"""
    try:
        from models.persona import Persona
        import os
        from werkzeug.utils import secure_filename
        
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
        
        # Validar campos obligatorios
        if not all([nombres, apellidos, tipo_doc, documento, fecha_nacimiento, telefono, id_dist, direccion, nomusuario, email, password]):
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
        
        # 2. Procesar imagen si existe
        img_logo = None
        if 'img_logo' in request.files:
            file = request.files['img_logo']
            if file and file.filename:
                filename = secure_filename(f"{nomusuario}_{file.filename}")
                upload_folder = os.path.join('uploads', 'fotos', 'usuarios')
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                img_logo = filename
        
        # 3. Crear usuario con rol Cliente (id_rol = 3)
        exito, id_usuario = usuario_model.registrar(
            nomusuario, email, password, id_persona, 
            id_rol=3,  # Cliente
            id_empresa=None
        )
        
        if not exito:
            return jsonify({
                'status': False,
                'message': f'Error al crear usuario: {id_usuario}'
            }), 400
        
        # 4. Actualizar imagen si existe
        if img_logo:
            con = Conexion().open
            cursor = con.cursor()
            cursor.execute("UPDATE usuario SET img_logo = %s WHERE id_usuario = %s", [img_logo, id_usuario])
            con.commit()
            cursor.close()
            con.close()
        
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