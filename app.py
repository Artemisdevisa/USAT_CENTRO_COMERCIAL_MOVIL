from flask import Flask, send_from_directory, render_template, request, make_response
from flask_cors import CORS
from routes.usuario import ws_usuario
from routes.producto_sucursal import ws_producto_sucursal
from routes.producto_color_routes import ws_producto_color
from routes.categoria_producto import ws_categoria_producto
from routes.sucursal import ws_sucursal
from routes.pregunta_frecuente import ws_pregunta_frecuente
from routes.departamento import ws_departamento
from routes.favorito import ws_favorito
from routes.tipo_documento import ws_tipo_documento
from routes.carrito import ws_carrito
from routes.resenia_routes import ws_resenia
from routes.persona_routes import ws_persona
from routes.rol import ws_rol
from routes.cupon_routes import ws_cupon
from routes.temporada_routes import ws_temporada
from routes.marca_routes import ws_marca
from routes.tipo_producto_routes import ws_tipo_producto
from routes.tipo_modelo_producto_routes import ws_tipo_modelo
from routes.color_routes import ws_color
from routes.empresa_routes import ws_empresa
from routes.provincia_routes import ws_provincia
from routes.horario_sucursal_routes import ws_horario_sucursal
from routes.distrito_routes import ws_distrito
from routes.tarjeta_routes import ws_tarjeta
from routes.venta_routes import ws_venta
from config import Config
import os

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True

# ✅ IMPRIMIR CONFIGURACIÓN AL INICIAR
Config.print_config()

# ✅ CONFIGURAR CORS CORRECTAMENTE
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": False,
        "max_age": 3600
    }
})

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Max-Age'] = '3600'
        return response

@app.after_request
def add_header(response):
    # ✅ HEADERS CORS EXPLÍCITOS
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    
    # Cache control
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

app.secret_key = Config.SECRET_KEY
app.config['SECRET_KEY'] = Config.SECRET_KEY

try:
    app.json.ensure_ascii = False
except Exception:
    pass

# Registrar blueprints
app.register_blueprint(ws_usuario)
app.register_blueprint(ws_marca)
app.register_blueprint(ws_carrito)
app.register_blueprint(ws_producto_sucursal)
app.register_blueprint(ws_producto_color)
app.register_blueprint(ws_tipo_documento)
app.register_blueprint(ws_tipo_producto)
app.register_blueprint(ws_tarjeta)
app.register_blueprint(ws_venta)
app.register_blueprint(ws_resenia)
app.register_blueprint(ws_color)
app.register_blueprint(ws_horario_sucursal)
app.register_blueprint(ws_cupon)
app.register_blueprint(ws_categoria_producto)
app.register_blueprint(ws_sucursal)
app.register_blueprint(ws_pregunta_frecuente)
app.register_blueprint(ws_temporada)
app.register_blueprint(ws_favorito)
app.register_blueprint(ws_departamento)
app.register_blueprint(ws_provincia)
app.register_blueprint(ws_distrito)
app.register_blueprint(ws_tipo_modelo)
app.register_blueprint(ws_empresa)
app.register_blueprint(ws_rol)
app.register_blueprint(ws_persona)

@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    """Servir archivos desde /uploads"""
    uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
    return send_from_directory(uploads_dir, filename)

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/productos')
def productos():
    """Catálogo de productos"""
    return render_template('productos.html')

@app.route('/categorias')
def categorias():
    """Listado de categorías públicas"""
    return render_template('categorias.html')

@app.route('/carrito')
def carrito():
    """Carrito de compras"""
    return render_template('carrito.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard principal - ACCESO LIBRE"""
    return render_template('dashboard.html')

@app.route('/dashboard/roles')
def dashboard_roles():
    """Gestión de roles - ACCESO LIBRE"""
    return render_template('rol/lista.html')

@app.route('/dashboard/categorias')
def dashboard_categorias():
    """Gestión de categorías - ACCESO LIBRE"""
    return render_template('categoria/lista.html')

@app.route('/dashboard/empresas')
def dashboard_empresas():
    """Gestión de empresas - ACCESO LIBRE"""
    return render_template('empresa/lista.html')

@app.route('/dashboard/empresa')
def dashboard_empresa():
    """Gestión de empresa del usuario - ACCESO LIBRE"""
    return render_template('empresa/empresa_unica.html')

@app.route('/dashboard/marcas')
def dashboard_marcas():
    """Gestión de marcas - ACCESO LIBRE"""
    return render_template('marca/lista.html')

@app.route('/dashboard/tipos')
def dashboard_tipos():
    """Gestión de tipos de producto - ACCESO LIBRE"""
    return render_template('tipo_producto/lista.html')

@app.route('/dashboard/modelos')
def dashboard_modelos():
    """Gestión de modelos de producto - ACCESO LIBRE"""
    return render_template('tipo_modelo_producto/lista.html')

@app.route('/dashboard/productos')
def dashboard_productos():
    """Gestión de productos - ACCESO LIBRE"""
    return render_template('producto_sucursal/lista.html')

@app.route('/dashboard/productos-color')
def dashboard_productos_color():
    """Gestión de variantes (color/talla) - ACCESO LIBRE"""
    return render_template('producto_color/lista.html')

@app.route('/dashboard/colores')
def dashboard_colores():
    """Gestión de colores - ACCESO LIBRE"""
    return render_template('color/lista.html')

@app.route('/dashboard/temporadas')
def dashboard_temporadas():
    """Gestión de temporadas - ACCESO LIBRE"""
    return render_template('temporada/lista.html')

@app.route('/dashboard/departamentos')
def dashboard_departamentos():
    """Gestión de ubicación geográfica - ACCESO LIBRE"""
    return render_template('departamento/lista.html')

@app.route('/dashboard/sucursales')
def dashboard_sucursales():
    """Gestión de sucursales - ACCESO LIBRE"""
    return render_template('sucursal/lista.html')

@app.route('/dashboard/preguntas-frecuentes')
def dashboard_preguntas_frecuentes():
    """Gestión de preguntas frecuentes - ACCESO LIBRE"""
    return render_template('pregunta_frecuente/lista.html')

@app.route('/login')
def login_page():
    """Página de login (opcional)"""
    return render_template('login.html')

@app.route('/postular-empresa')
def postular_empresa():
    """Formulario de postulación de empresas"""
    return render_template('postular_empresa.html')


@app.route('/dashboard/cupones')
def dashboard_cupones():
    """Gestión de cupones - ACCESO LIBRE"""
    return render_template('cupon/lista.html')


@app.route('/dashboard/horarios-sucursal')
def dashboard_horarios_sucursal():
    """Gestión de horarios de sucursales - ACCESO LIBRE"""
    return render_template('horario_sucursal/lista.html')

@app.route('/registro')
def registro_page():
    """Página de registro"""
    return render_template('registro.html')

@app.route('/dashboard/usuarios')
def dashboard_usuarios():
    """Gestión de usuarios - ACCESO LIBRE"""
    return render_template('usuario/lista.html')


@app.route('/debug/routes')
def list_routes():
    """Listar todas las rutas registradas"""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'path': str(rule)
        })
    return {'routes': sorted(routes, key=lambda x: x['path'])}

@app.route('/api/info')
def api_info():
    """Información de la API y configuración de Cloudinary"""
    return {
        'status': True,
        'app': 'Centro Comercial Elías Aguirre API',
        'version': '2.0',
        'cloudinary': {
            'enabled': True,
            'cloud_name': Config.CLOUDINARY_CLOUD_NAME
        },
        'database': {
            'host': Config.DB_HOST,
            'name': Config.DB_NAME
        }
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3007))
    print(f"\n🚀 Servidor iniciado en puerto {port}")
    print(f"📡 API URL: http://localhost:{port}")
    print(f"☁️  Cloudinary: {Config.CLOUDINARY_CLOUD_NAME}\n")
    app.run(host='0.0.0.0', port=port, debug=False)
