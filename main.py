import requests
import time
import threading
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# --- CONFIGURACIÓN ACTUALIZADA ---
API_KEY = "a4592942bf83a08e71f9a4c64b4df9e0"
TOKEN = "15c6a2f842814537" # Tu nuevo Token
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
            "footer": {"text": "Omni-Sniper V60.30"}
        }]
    }
    try:
        requests.post(WEBHOOK_DISCORD, json=data)
    except:
        pass

def ejecutar_sniper():
    print("🚀 SNIPER: Iniciando con nuevo Token...", flush=True)
    enviar_a_discord("🎯 Sniper Conectado", "Sistema listo con nuevo API Token.", 3066993)
    
    while True:
        try:
            hoy = datetime.datetime.now().strftime('%Y-%m-%d')
            url_api = f"https://v3.football.api-sports.io/fixtures?date={hoy}"
            
            with InfluxDBClient(url=URL, token=TOKEN, org=ORG) as client:
                write_api = client.write_api(write_options=SYNCHRONOUS)
                r = requests.get(url_api, headers=HEADERS).json()
                partidos = r.get('response', [])
                
                enviados = 0
                for p in partidos:
                    match_name = f"{p['teams']['home']['name']} vs {p['teams']['away']['name']}"
                    estado = p['fixture']['status']['short']
                    
                    # Usamos el ID del partido para que sea único
                    point = Point("predicciones_sniper") \
                        .tag("partido", match_name) \
                        .field("alerta_sniper", f"Estado: {estado}") \
                        .field("prob_local", 85.0 if "Home" in match_name else 45.0) # Simulación de valor
                    
                    write_api.write(bucket=BUCKET, record=point)
                    enviados += 1
                
                print(f"✅ Ciclo: {enviados} partidos enviados.", flush=True)
            time.sleep(900)
        except Exception as e:
            print(f"❌ Error: {e}", flush=True)
            time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=ejecutar_sniper, daemon=True).start()
    HTTPServer(('0.0.0.0', 10000), BaseHTTPRequestHandler).serve_forever()
