import requests
import time
import threading
import datetime
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
        self.wfile.write(b"Sniper Online")

def run_server():
    try:
        server = HTTPServer(('0.0.0.0', 10000), SimpleHandler)
        server.serve_forever()
    except Exception:
        pass

def ejecutar_sniper():
    print("🚀 SNIPER: Iniciando...")
    # Ligas: Champions, Europa League, Libertadores, Premier, España
    LIGAS_TOP = [2, 3, 13, 39, 140]
    
    while True:
        try:
            hoy = datetime.datetime.now().strftime('%Y-%m-%d')
            count = 0
            
            client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
            write_api = client.write_api(write_options=SYNCHRONOUS)
            
            for liga in LIGAS_TOP:
                # Quitamos el año para que la API use el actual por defecto
                url_api = f"https://v3.football.api-sports.io/fixtures?date={hoy}&league={liga}"
                response = requests.get(url_api, headers=HEADERS).json()
                partidos = response.get('response', [])
                
                for p in partidos:
                    home = p['teams']['home']['name']
                    away = p['teams']['away']['name']
                    estado = p['fixture']['status']['short']
                    minuto = p['fixture']['status']['elapsed'] or 0
                    
                    point = Point("predicciones_sniper") \
                        .tag("partido", f"{home} vs {away}") \
                        .field("alerta_sniper", f"Estado: {estado}") \
                        .field("minuto", float(minuto))
                    
                    write_api.write(bucket=BUCKET, record=point)
                    count += 1
            
            client.close()
            print(f"✅ {count} partidos enviados correctamente.")
            time.sleep(600) 
            
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    ejecutar_sniper()
