from flask import Flask
from routes.localizacion import ws_localizacion
from routes.tipo_documento import ws_tipo_documento
from routes.usuario2 import ws_usuario2

# from routes.usuario import ws_usuario
# from routes.vehiculo import ws_vehiculo
# from routes.reserva import ws_reserva

app = Flask(__name__)
try:
    app.json.ensure_ascii = False
except Exception:
    pass


app.register_blueprint(ws_localizacion)
app.register_blueprint(ws_tipo_documento)
app.register_blueprint(ws_usuario2)


#app.register_blueprint(ws_usuario)
#app.register_blueprint(ws_vehiculo)
#app.register_blueprint(ws_reserva)


@app.route('/')
def home():
    return 'Centro Comercial Elias Aguirre - Running API Restful'

#Iniciar el servicio web con Flask
if __name__ == '__main__':
    app.run(port=3007, debug=True, host='0.0.0.0')