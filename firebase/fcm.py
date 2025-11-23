import requests
import json
import google.auth
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import os
import datetime


def notificar(device_token, title, body):
    """
    Envía una notificación push a un dispositivo específico usando Firebase Cloud Messaging V1
    """
    
    print(f"📱 Enviando notificación a dispositivo: {device_token[:20]}...")
    
    SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
    
    # ✅ CARGAR CREDENCIALES DESDE VARIABLE DE ENTORNO O ARCHIVO
    FIREBASE_CREDENTIALS = os.environ.get('FIREBASE_CREDENTIALS')
    
    try:
        if FIREBASE_CREDENTIALS:
            # ✅ EN PRODUCCIÓN: Usar variable de entorno
            print("🔑 Usando credenciales desde variable de entorno")
            credentials_dict = json.loads(FIREBASE_CREDENTIALS)
            credentials = service_account.Credentials.from_service_account_info(
                credentials_dict,
                scopes=SCOPES
            )
        else:
            # ✅ EN DESARROLLO: Usar archivo local
            print("🔑 Usando credenciales desde archivo local")
            SERVICE_ACCOUNT_FILE = 'elias-aguirre-firebase-adminsdk-fbsvc-5a7e9a2652.json'
            service_account_path = os.path.join(os.getcwd(), "firebase", SERVICE_ACCOUNT_FILE)
            
            if not os.path.isfile(service_account_path):
                raise FileNotFoundError(f"El archivo {service_account_path} no existe.")
            
            credentials = service_account.Credentials.from_service_account_file(
                service_account_path,
                scopes=SCOPES
            )
        
        credentials.refresh(Request())
        access_token = credentials.token
        
        print("🔑 Token de acceso obtenido correctamente")
        
        FCM_URL = 'https://fcm.googleapis.com/v1/projects/elias-aguirre/messages:send'
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; UTF-8',
        }
        
        message = {
            'message': {
                'token': device_token,
                'notification': {
                    'title': title,
                    'body': body,
                },
                'data': {
                    'timestamp': str(datetime.datetime.utcnow()),
                    'tipo': 'notificacion_general',
                    'origen': 'centro_comercial_elias_aguirre'
                },
                'android': {
                    'priority': 'high',
                    'notification': {
                        'sound': 'default',
                        'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                    }
                }
            }
        }
        
        print("📡 Enviando notificación a Firebase...")
        response = requests.post(FCM_URL, headers=headers, data=json.dumps(message))
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Notificación enviada exitosamente")
            return True
        else:
            print(f"❌ Error al enviar notificación")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Error en notificar(): {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def notificar_multiple(tokens, title, body):
    """
    Envía notificaciones a múltiples dispositivos
    """
    resultados = {'exitosos': 0, 'fallidos': 0}
    
    print(f"📱 Enviando notificación a {len(tokens)} dispositivos...")
    
    for token in tokens:
        try:
            if notificar(token, title, body):
                resultados['exitosos'] += 1
            else:
                resultados['fallidos'] += 1
        except Exception as e:
            print(f"❌ Error al enviar a token {token[:20]}...: {str(e)}")
            resultados['fallidos'] += 1
    
    print(f"📊 Resumen: {resultados['exitosos']} exitosas, {resultados['fallidos']} fallidas")
    return resultados