import requests
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# --- CONFIGURACIÓN FINAL ( Francisco, usa estos datos exactos ) ---
API_KEY = "a4592942bf83a08e71f9a4c64b4df9e0"
# Tu nuevo All Access Token generado
TOKEN = "XqwrSnzkqlh8w8zDPXsfTd1Q3FzDP8pEgfawxk6HK0vVf9dQef95SsXsjX_e8nJL-JngGAN0b4MmCcnFC9uPpw=="
ORG = "6025b5f4b3e4e21e"
# Usamos el nombre del bucket que InfluxDB reconoce en tu panel
BUCKET = "ApuestasDeportivas" 
URL = "https://us-east-1-1.aws.cloud2.influxdata.com"
HEADERS = {'x-rapidapi-host': 'v3.football.api-sports.io', 'x-rapidapi-key': API_KEY}

class SimpleHandler(BaseHTTPRequestHandler):
    """Mantiene a Render feliz respondiendo a pings HTTP"""
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Sniper Online")

def run_server():
    """Servidor web para evitar que la instancia de Render se apague"""
    server = HTTPServer(('0.0.0.0', 10000), SimpleHandler)
    server.serve_forever()

def ejecutar_sniper():
    """Lógica principal de vigilancia de partidos y envío a InfluxDB"""
    print("🚀 OMNI-SNIPER ACTIVADO: Iniciando vigilancia...")
    while True:
        try:
            # Consulta a la API de Fútbol
            url_live = "https://v3.football.api-sports.io/fixtures?live=all"
            response = requests.get(url_live, headers=HEADERS).json()
            partidos = response.get('response', [])
            
            print(f"📡 Escaneo completado: {len(partidos)} partidos encontrados.")

            if len(partidos) > 0:
                with InfluxDBClient(url=URL, token=TOKEN, org=ORG) as client:
                    write_api = client.write_api(write_options=SYNCHRONOUS)
                    for p in partidos:
                        home = p['teams']['home']['name']
                        away = p['teams']['away']['name']
                        # Aseguramos que minuto y goles no sean None
                        minuto = p['fixture']['status']['elapsed'] or 0
                        gh = p['goals']['home'] if p['goals']['home'] is not None else 0
                        ga = p['goals']['away'] if p['goals']['away'] is not None else 0
                        
                        # Lógica de alertas (puedes ampliarla después)
                        alerta = "☕ Analizando..."
                        if minuto > 75:
                            alerta = "🔥 ATAQUE FINAL: Posible Córner"

                        # Creamos el punto de datos para InfluxDB
                        point = Point("predicciones_sniper") \
                            .tag("partido", f"{home} vs {away}") \
                            .field("minuto", float(minuto)) \
                            .field("goles_local", float(gh)) \
                            .field("goles_visitante", float(ga)) \
                            .field("alerta_sniper", alerta)
                        
                        # Escribimos en el bucket
                        write_api.write(bucket=BUCKET, record=point)
                        print(f"✅ Datos enviados: {home} vs {away} (Min {minuto})")
            else:
                print("📭 Sin partidos en vivo por ahora.")
            
            # Espera 5 minutos (300 seg) para optimizar el plan gratuito de la API
            time.sleep(300) 
            
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    # Iniciamos el servidor en un hilo secundario
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    # Ejecutamos el bot en el hilo principal
    ejecutar_sniper()
