import requests
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# --- CONFIG (Tus datos) ---
API_KEY = "a4592942bf83a08e71f9a4c64b4df9e0"
TOKEN = "PB47SRHhqPq6lHe3WUhzojeKaUUBcjvNISL6PSWh2b1kSzgMOscolVFiW67mv19i8pz0TRnuLJy5m0h3WiEg9g=="
ORG = "6025b5f4b3e4e21e"
BUCKET = "19ae67debb050709"
URL = "https://us-east-1-1.aws.cloud2.influxdata.com"
HEADERS = {'x-rapidapi-host': 'v3.football.api-sports.io', 'x-rapidapi-key': API_KEY}

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Sniper Online")

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHandler)
    server.serve_forever()

def ejecutar_sniper():
    print("🚀 OMNI-SNIPER ACTIVADO: Iniciando vigilancia...") # <--- Esto debe salir en logs
    while True:
        try:
            url_live = "https://v3.football.api-sports.io/fixtures?live=all"
            response = requests.get(url_live, headers=HEADERS).json()
            partidos = response.get('response', [])
            
            print(f"📡 Escaneo completado: {len(partidos)} partidos encontrados.")

            with InfluxDBClient(url=URL, token=TOKEN, org=ORG) as client:
                write_api = client.write_api(write_options=SYNCHRONOUS)
                for p in partidos:
                    f_id = p['fixture']['id']
                    home = p['teams']['home']['name']
                    away = p['teams']['away']['name']
                    minuto = p['fixture']['status']['elapsed']
                    gh = p['goals']['home']
                    ga = p['goals']['away']
                    
                    point = Point("predicciones_sniper").tag("partido", f"{home} vs {away}") \
                        .field("minuto", float(minuto)) \
                        .field("goles_local", float(gh)) \
                        .field("goles_visitante", float(ga)) \
                        .field("alerta_sniper", "📡 Escaneando...")
                    
                    write_api.write(bucket=BUCKET, record=point)
                    print(f"✅ Datos enviados a InfluxDB: {home} vs {away} (Min {minuto})")
            
            time.sleep(300) 
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    ejecutar_sniper()
