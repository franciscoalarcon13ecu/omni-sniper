import requests
import time
import threading
import datetime
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# --- CONFIGURACIÓN RE-VERIFICADA ---
API_KEY = "a4592942bf83a08e71f9a4c64b4df9e0"
# Este es el Token largo que termina en ==
TOKEN = "SNUjIrVrOCokuIBE2XbDa0GnLhhQ4R5RIFLi_7cA91-QG3mv0il3SIwid8B7vUCnGzxGk5-fVbXgBAoI0Aj2KA=="
ORG = "6025b5f4b3e4e21e" 
BUCKET = "ApuestasDeportivas2" 
URL = "https://us-east-1-1.aws.cloud2.influxdata.com"
WEBHOOK_DISCORD = "https://discord.com/api/webhooks/1491508795161968802/dxaKzEZ1QP0fmAPZgI_HEytnDBgpmws3tMmRL0HaVsF1-P6SPSrqL2s6zpOICzvRiQFc"

HEADERS = {'x-rapidapi-host': 'v3.football.api-sports.io', 'x-rapidapi-key': API_KEY}

def enviar_a_discord(msg):
    try:
        requests.post(WEBHOOK_DISCORD, json={"content": msg})
    except:
        pass

def ejecutar_sniper():
    print(f"🚀 SNIPER: Intentando conectar a {BUCKET}...", flush=True)
    enviar_a_discord("🔄 Sniper reiniciando conexión...")
    
    while True:
        try:
            hoy = datetime.datetime.now().strftime('%Y-%m-%d')
            url_api = f"https://v3.football.api-sports.io/fixtures?date={hoy}"
            
            # 1. Obtenemos datos de la API
            r = requests.get(url_api, headers=HEADERS).json()
            partidos = r.get('response', [])
            
            # 2. Conectamos a InfluxDB
            client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
            write_api = client.write_api(write_options=SYNCHRONOUS)
            
            count = 0
            for p in partidos:
                match_name = f"{p['teams']['home']['name']} vs {p['teams']['away']['name']}"
                # Creamos el punto de la forma más simple posible
                point = Point("predicciones_sniper") \
                    .tag("partido", match_name) \
                    .field("alerta_sniper", str(p['fixture']['status']['short'])) \
                    .field("prob_local", 75.0) # Valor fijo para probar
                
                write_api.write(bucket=BUCKET, record=point)
                count += 1
            
            print(f"✅ ÉXITO: {count} registros en {BUCKET}", flush=True)
            if count > 0:
                enviar_a_discord(f"✅ ¡Datos enviados! {count} partidos en InfluxDB.")
            
            client.close()
            time.sleep(600) 
        except Exception as e:
            error_msg = f"❌ ERROR: {str(e)}"
            print(error_msg, flush=True)
            enviar_a_discord(error_msg)
            time.sleep(60)

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Sniper Working")

if __name__ == "__main__":
    threading.Thread(target=ejecutar_sniper, daemon=True).start()
    HTTPServer(('0.0.0.0', 10000), SimpleHandler).serve_forever()
