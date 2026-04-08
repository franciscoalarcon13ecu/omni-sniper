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
WEBHOOK_DISCORD = "https://discord.com/api/webhooks/1491508795161968802/dxaKzEZ1QP0fmAPZgI_HEytnDBgpmws3tMmRL0HaVsF1-P6SPSrqL2s6zpOICzvRiQFc"

HEADERS = {'x-rapidapi-host': 'v3.football.api-sports.io', 'x-rapidapi-key': API_KEY}

def enviar_a_discord(titulo, descripcion, color):
    data = {
        "embeds": [{
            "title": titulo,
            "description": descripcion,
            "color": color,
            "footer": {"text": "Omni-Sniper V60.30 - Francisco Alarcón"}
        }]
    }
    requests.post(WEBHOOK_DISCORD, json=data)

def ejecutar_sniper():
    print("🚀 SNIPER: Iniciando con Alertas de Discord...", flush=True)
    enviar_a_discord("🎯 Sniper Online", "El sistema ha arrancado y está vigilando los mercados.", 3066993)
    
    while True:
        try:
            hoy = datetime.datetime.now().strftime('%Y-%m-%d')
            url_api = f"https://v3.football.api-sports.io/fixtures?date={hoy}"
            
            with InfluxDBClient(url=URL, token=TOKEN, org=ORG) as client:
                write_api = client.write_api(write_options=SYNCHRONOUS)
                r = requests.get(url_api, headers=HEADERS).json()
                partidos = r.get('response', [])
                
                for p in partidos:
                    # Simulamos una lógica de probabilidad para la alerta (Basada en datos de la API)
                    # Aquí podrías usar tus propios cálculos de prob_local
                    prob_local = 75 # Ejemplo: Esto vendría de tu modelo
                    match_name = f"{p['teams']['home']['name']} vs {p['teams']['away']['name']}"
                    estado = p['fixture']['status']['short']

                    # 1. Guardar en InfluxDB (Como siempre)
                    point = Point("predicciones_sniper") \
                        .tag("partido", match_name) \
                        .field("alerta_sniper", f"Estado: {estado}") \
                        .field("prob_local", float(prob_local))
                    write_api.write(bucket=BUCKET, record=point)

                    # 2. ALERTA CRÍTICA: Solo si la probabilidad es alta y no ha empezado (NS)
                    if prob_local >= 80 and estado == "NS":
                        enviar_a_discord(
                            "🔥 OPORTUNIDAD DETECTADA",
                            f"**Partido:** {match_name}\n**Prob. Local:** {prob_local}%\n**Estado:** Por empezar\n\n*Revisa Bet365 ahora!*",
                            15105570 # Color Naranja/Rojo
                        )
                
                print(f"✅ Ciclo completado a las {datetime.datetime.now().strftime('%H:%M')}", flush=True)
            
            time.sleep(900) # Revisar cada 15 min para no saturar Discord
        except Exception as e:
            print(f"❌ ERROR: {e}", flush=True)
            time.sleep(60)

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Sniper Discord Ready")

if __name__ == "__main__":
    threading.Thread(target=ejecutar_sniper, daemon=True).start()
    HTTPServer(('0.0.0.0', 10000), SimpleHandler).serve_forever()
