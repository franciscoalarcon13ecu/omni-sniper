import requests
import time
import threading
import datetime
import sys # <--- Añadido para forzar la salida de texto
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
        self.wfile.write(b"Sniper Activo")
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def ejecutar_sniper():
    # El flush=True obliga a Render a mostrar el mensaje de inmediato
    print("🚀 SNIPER: Iniciando barrida...", flush=True) 
    LIGAS_TOP = [2, 3, 13, 39, 140]
    while True:
        try:
            hoy = datetime.datetime.now().strftime('%Y-%m-%d')
            print(f"📅 Consultando para: {hoy}", flush=True)
            
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
                print(f"✅ CICLO COMPLETADO: {count} partidos enviados.", flush=True)
            
            time.sleep(600) 
        except Exception as e:
            print(f"❌ ERROR: {e}", flush=True)
            time.sleep(60)

if __name__ == "__main__":
    # Cambiamos el orden: Arrancamos el sniper y lo dejamos correr
    print("🎬 Arrancando hilo del Sniper...", flush=True)
    threading.Thread(target=ejecutar_sniper, daemon=True).start()
    
    print("🌐 Iniciando Servidor Web...", flush=True)
    server = HTTPServer(('0.0.0.0', 10000), SimpleHandler)
    server.serve_forever()
