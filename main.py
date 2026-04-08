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

# --- TRUCO PARA EVITAR TIMEOUT ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Sniper Online")

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHandler)
    server.serve_forever()

# --- TU CÓDIGO SNIPER ---
def ejecutar_sniper():
    print("🚀 OMNI-SNIPER ACTIVADO...")
    while True:
        try:
            url_live = "https://v3.football.api-sports.io/fixtures?live=all"
            response = requests.get(url_live, headers=HEADERS).json()
            partidos = response.get('response', [])
            
            with InfluxDBClient(url=URL, token=TOKEN, org=ORG) as client:
                write_api = client.write_api(write_options=SYNCHRONOUS)
                for p in partidos:
                    f_id, home, away = p['fixture']['id'], p['teams']['home']['name'], p['teams']['away']['name']
                    minuto, gh, ga = p['fixture']['status']['elapsed'], p['goals']['home'], p['goals']['away']
                    
                    point = Point("predicciones_sniper").tag("partido", f"{home} vs {away}") \
                        .field("minuto", float(minuto)).field("goles_local", float(gh)).field("goles_visitante", float(ga))
                    
                    write_api.write(bucket=BUCKET, record=point)
                    print(f"✅ Monitor: {home} vs {away} (Min {minuto})")
            
            time.sleep(300)
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    # Arrancamos el servidor falso en un hilo y el sniper en otro
    threading.Thread(target=run_server, daemon=True).start()
    ejecutar_sniper()
