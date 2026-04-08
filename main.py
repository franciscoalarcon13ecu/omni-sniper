import requests
import time
import threading
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# --- CONFIGURACIÓN (Francisco, verifica que el BUCKET sea exacto) ---
API_KEY = "a4592942bf83a08e71f9a4c64b4df9e0"
TOKEN = "XqwrSnzkqlh8w8zDPXsfTd1Q3FzDP8pEgfawxk6HK0vVf9dQef95SsXsjX_e8nJL-JngGAN0b4MmCcnFC9uPpw=="
ORG = "6025b5f4b3e4e21e" 
BUCKET = "ApuestasDeportivas" 
URL = "https://us-east-1-1.aws.cloud2.influxdata.com"
HEADERS = {'x-rapidapi-host': 'v3.football.api-sports.io', 'x-rapidapi-key': API_KEY}

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Sniper Activo y Enviando Datos")
    def do_HEAD(self): # Esto evita el error 501 que salía en tus logs
        self.send_response(200)
        self.end_headers()

def ejecutar_sniper():
    print("🚀 SNIPER: Iniciando barrida de partidos...")
    LIGAS_TOP = [2, 3, 13, 39, 140]
    while True:
        try:
            hoy = datetime.datetime.now().strftime('%Y-%m-%d')
            print(f"📅 Consultando partidos para: {hoy}")
            
            with InfluxDBClient(url=URL, token=TOKEN, org=ORG) as client:
                write_api = client.write_api(write_options=SYNCHRONOUS)
                count = 0
                for liga in LIGAS_TOP:
                    url_api = f"https://v3.football.api-sports.io/fixtures?date={hoy}&league={liga}"
                    r = requests.get(url_api, headers=HEADERS).json()
                    partidos = r.get('response', [])
                    
                    for p in partidos:
                        match_name = f"{p['teams']['home']['name']} vs {p['teams']['away']['name']}"
                        point = Point("predicciones_sniper") \
                            .tag("partido", match_name) \
                            .field("alerta_sniper", f"Estado: {p['fixture']['status']['short']}") \
                            .field("minuto", float(p['fixture']['status']['elapsed'] or 0))
                        
                        write_api.write(bucket=BUCKET, record=point)
                        count += 1
                print(f"✅ CICLO COMPLETADO: {count} partidos enviados.")
            
            time.sleep(600) 
        except Exception as e:
            print(f"❌ ERROR EN EL SNIPER: {e}")
            time.sleep(60)

if __name__ == "__main__":
    # 1. Arrancamos el Sniper en un hilo separado primero
    threading.Thread(target=ejecutar_sniper, daemon=True).start()
    
    # 2. Luego arrancamos el servidor para Render
    print("🌐 Iniciando Servidor Web en puerto 10000...")
    server = HTTPServer(('0.0.0.0', 10000), SimpleHandler)
    server.serve_forever()
