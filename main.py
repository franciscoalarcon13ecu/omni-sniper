import requests
import time
import threading
import datetime
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# --- CONFIGURACIÓN TOTALMENTE CORREGIDA ---
API_KEY = "a4592942bf83a08e71f9a4c64b4df9e0"
TOKEN = "15c6a2f842814537" 
ORG = "6025b5f4b3e4e21e" 
BUCKET = "ApuestaDeportvas2"  # Nombre exacto de tu bucket
URL = "https://us-east-1-1.aws.cloud2.influxdata.com"
WEBHOOK_DISCORD = "https://discord.com/api/webhooks/1491508795161968802/dxaKzEZ1QP0fmAPZgI_HEytnDBgpmws3tMmRL0HaVsF1-P6SPSrqL2s6zpOICzvRiQFc"

HEADERS = {
    'x-rapidapi-host': 'v3.football.api-sports.io', 
    'x-rapidapi-key': API_KEY
}

def enviar_a_discord(titulo, descripcion, color):
    """Envía notificaciones visuales a tu canal de Discord"""
    data = {
        "embeds": [{
            "title": titulo,
            "description": descripcion,
            "color": color,
            "footer": {"text": "Omni-Sniper V60.30 - Francisco Alarcón"}
        }]
    }
    try:
        requests.post(WEBHOOK_DISCORD, json=data)
    except Exception as e:
        print(f"⚠️ Error enviando a Discord: {e}")

def ejecutar_sniper():
    print("🚀 SNIPER: Iniciando sistema...", flush=True)
    enviar_a_discord("🎯 Sniper Conectado", "El bot está vigilando los mercados con el nuevo Token.", 3066993)
    
    while True:
        try:
            # Consultamos hoy y mañana para tener planificación
            hoy = datetime.datetime.now().strftime('%Y-%m-%d')
            print(f"📡 Consultando partidos para: {hoy}", flush=True)
            
            with InfluxDBClient(url=URL, token=TOKEN, org=ORG) as client:
                write_api = client.write_api(write_options=SYNCHRONOUS)
                url_api = f"https://v3.football.api-sports.io/fixtures?date={hoy}"
                
                response = requests.get(url_api, headers=HEADERS).json()
                partidos = response.get('response', [])
                
                enviados = 0
                for p in partidos:
                    match_name = f"{p['teams']['home']['name']} vs {p['teams']['away']['name']}"
                    estado = p['fixture']['status']['short']
                    # Simulamos valor para la tabla (luego lo conectaremos a tu modelo real)
                    prob_val = 85.0 if "United" in match_name or "Real" in match_name else 50.0

                    # Guardar en InfluxDB
                    point = Point("predicciones_sniper") \
                        .tag("partido", match_name) \
                        .field("alerta_sniper", f"Estado: {estado}") \
                        .field("prob_local", float(prob_val))
                    
                    write_api.write(bucket=BUCKET, record=point)
                    enviados += 1

                    # ALERTA DISCORD: Si la probabilidad es alta y el partido no ha empezado
                    if prob_val >= 85 and estado == "NS":
                        enviar_a_discord(
                            "🔥 OPORTUNIDAD DETECTADA", 
                            f"**Partido:** {match_name}\n**Probabilidad:** {prob_val}%\n**Estado:** {estado}\n\n*¡Revisa Bet365 ahora!*", 
                            15105570
                        )
                
                print(f"✅ CICLO COMPLETADO: {enviados} partidos enviados a {BUCKET}.", flush=True)
            
            # Esperar 15 minutos antes de la siguiente barrida
            time.sleep(900) 
            
        except Exception as e:
            print(f"❌ ERROR CRÍTICO: {e}", flush=True)
            time.sleep(60)

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Sniper Activo - Enviando a Discord e InfluxDB")
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

if __name__ == "__main__":
    # Iniciar el hilo del Sniper
    threading.Thread(target=ejecutar_sniper, daemon=True).start()
    
    # Iniciar el servidor web para Render
    port = 10000
    print(f"🌐 Servidor web escuchando en puerto {port}...", flush=True)
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()
