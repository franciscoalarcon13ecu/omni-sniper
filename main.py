import requests
import time
import threading
import datetime
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# --- CONFIGURACIÓN ---
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
        self.wfile.write(b"Sniper Activo - Barrida Total")
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def ejecutar_sniper():
    print("🚀 SNIPER: Iniciando BARRIDA TOTAL de hoy...", flush=True)
    while True:
        try:
            hoy = datetime.datetime.now().strftime('%Y-%m-%d')
            url_api = f"https://v3.football.api-sports.io/fixtures?date={hoy}"
            
            with InfluxDBClient(url=URL, token=TOKEN, org=ORG) as client:
                write_api = client.write_api(write_options=SYNCHRONOUS)
                r = requests.get(url_api, headers=HEADERS).json()
                partidos = r.get('response', [])
                
                print(f"📡 API respondió con {len(partidos)} partidos totales.", flush=True)
                
                count = 0
                for p in partidos:
                    match_name = f"{p['teams']['home']['name']} vs {p['teams']['away']['name']}"
                    estado = p['fixture']['status']['short']
                    
                    # Filtramos: Solo enviamos lo que NO ha terminado (Programados o En Vivo)
                    if estado not in ['FT', 'AET', 'PEN']:
                        point = Point("predicciones_sniper") \
                            .tag("partido", match_name) \
                            .field("alerta_sniper", f"Estado: {estado}") \
                            .field("minuto", float(p['fixture']['status']['elapsed'] or 0))
                        
                        write_api.write(bucket=BUCKET, record=point)
                        count += 1
                
                print(f"✅ CICLO COMPLETADO: {count} partidos útiles enviados a Influx.", flush=True)
            
            # Esperar 10 minutos para la siguiente actualización
            time.sleep(600) 
        except Exception as e:
            print(f"❌ ERROR: {e}", flush=True)
            time.sleep(60)

if __name__ == "__main__":
    print("🎬 Arrancando sistema...", flush=True)
    # 1. Hilo del Sniper
    threading.Thread(target=ejecutar_sniper, daemon=True).start()
    
    # 2. Servidor Web para Render
    server = HTTPServer(('0.0.0.0', 10000), SimpleHandler)
    server.serve_forever()
