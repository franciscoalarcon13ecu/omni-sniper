import requests
import time
import threading
from datetime import datetime
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
        self.wfile.write(b"Sniper Planificador Online")

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHandler)
    server.serve_forever()

def ejecutar_sniper():
    print("🚀 OMNI-SNIPER ACTIVADO: Modo Planificación + En Vivo")
    while True:
        try:
            # 1. Obtenemos la fecha de hoy para el escaneo general
            hoy = datetime.now().strftime('%Y-%m-%d')
            
            # 2. Consultamos todos los partidos del día
            url_hoy = f"https://v3.football.api-sports.io/fixtures?date={hoy}"
            response = requests.get(url_hoy, headers=HEADERS).json()
            partidos = response.get('response', [])
            
            print(f"📡 Escaneo: {len(partidos)} partidos encontrados para hoy ({hoy}).")

            if len(partidos) > 0:
                with InfluxDBClient(url=URL, token=TOKEN, org=ORG) as client:
                    write_api = client.write_api(write_options=SYNCHRONOUS)
                    
                    for p in partidos:
                        home = p['teams']['home']['name']
                        away = p['teams']['away']['name']
                        estado = p['fixture']['status']['short'] # NS, 1H, 2H, FT, etc.
                        minuto = p['fixture']['status']['elapsed'] or 0
                        gh = p['goals']['home'] if p['goals']['home'] is not None else 0
                        ga = p['goals']['away'] if p['goals']['away'] is not None else 0
                        
                        # --- LÓGICA DE ALERTA Y ESTADO ---
                        if estado == "NS":
                            alerta = "📅 PROGRAMADO (Aún no empieza)"
                        elif estado in ["1H", "2H", "HT"]:
                            alerta = "⚽ EN VIVO - Monitoreando"
                            if minuto > 75:
                                alerta = "🔥 ATAQUE FINAL: Posible Córner"
                        elif estado == "FT":
                            alerta = f"🏁 FINALIZADO ({gh}-{ga})"
                        else:
                            alerta = "⏱️ En pausa/Interrumpido"

                        # Creamos el punto con el campo extra de 'estado'
                        point = Point("predicciones_sniper") \
                            .tag("partido", f"{home} vs {away}") \
                            .field("minuto", float(minuto)) \
                            .field("goles_local", float(gh)) \
                            .field("goles_visitante", float(ga)) \
                            .field("alerta_sniper", alerta) \
                            .field("estado_cod", estado)
                        
                        write_api.write(bucket=BUCKET, record=point)
                    
                    print(f"✅ Dashboard actualizado: {len(partidos)} partidos procesados.")
            else:
                print("📭 No hay partidos programados para hoy según la API.")
            
            # Esperamos 10 minutos entre escaneos para no saturar la API
            time.sleep(600) 
            
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    ejecutar_sniper()
