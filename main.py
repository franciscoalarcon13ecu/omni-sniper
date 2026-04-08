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
        self.wfile.write(b"Sniper Activo - Planificador de Apuestas")

def ejecutar_sniper():
    print("🚀 SNIPER: Iniciando...", flush=True)
    while True:
        try:
            # Traemos partidos de HOY y de MAÑANA para asegurar datos
            fechas_a_consultar = [
                datetime.datetime.now().strftime('%Y-%m-%d'),
                (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            ]
            
            with InfluxDBClient(url=URL, token=TOKEN, org=ORG) as client:
                write_api = client.write_api(write_options=SYNCHRONOUS)
                
                for fecha in fechas_a_consultar:
                    print(f"📡 Buscando partidos para: {fecha}", flush=True)
                    url_api = f"https://v3.football.api-sports.io/fixtures?date={fecha}"
                    r = requests.get(url_api, headers=HEADERS).json()
                    partidos = r.get('response', [])
                    
                    count = 0
                    for p in partidos:
                        # Solo ligas importantes para no saturar
                        if p['league']['id'] in [2, 3, 13, 39, 140, 135, 78, 61, 141, 1, 4, 9]:
                            match_name = f"{p['teams']['home']['name']} vs {p['teams']['away']['name']}"
                            point = Point("predicciones_sniper") \
                                .tag("partido", match_name) \
                                .field("alerta_sniper", f"Estado: {p['fixture']['status']['short']}") \
                                .field("minuto", float(p['fixture']['status']['elapsed'] or 0))
                            
                            write_api.write(bucket=BUCKET, record=point)
                            count += 1
                    print(f"✅ {fecha}: {count} partidos enviados.", flush=True)
            
            time.sleep(600) 
        except Exception as e:
            print(f"❌ ERROR: {e}", flush=True)
            time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=ejecutar_sniper, daemon=True).start()
    server = HTTPServer(('0.0.0.0', 10000), SimpleHandler)
    server.serve_forever()
