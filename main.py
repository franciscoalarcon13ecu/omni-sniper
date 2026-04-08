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

def ejecutar_sniper():
    # Ligas de interés: Champions (2), Libertadores (13), Europa League (3), Premier (39), España (140)
    LIGAS_TOP = [2, 3, 13, 39, 140] 
    print("🚀 SNIPER: Modo Planificación Ligera activado...")
    
    while True:
        try:
            hoy = datetime.now().strftime('%Y-%m-%d')
            count = 0
            
            with InfluxDBClient(url=URL, token=TOKEN, org=ORG) as client:
                write_api = client.write_api(write_options=SYNCHRONOUS)
                
                for liga in LIGAS_TOP:
                    url = f"https://v3.football.api-sports.io/fixtures?date={hoy}&league={liga}&season=2025"
                    response = requests.get(url, headers=HEADERS).json()
                    partidos = response.get('response', [])
                    
                    for p in partidos:
                        home = p['teams']['home']['name']
                        away = p['teams']['away']['name']
                        estado = p['fixture']['status']['short']
                        
                        point = Point("predicciones_sniper") \
                            .tag("partido", f"{home} vs {away}") \
                            .field("alerta_sniper", f"Estado: {estado}") \
                            .field("minuto", float(p['fixture']['status']['elapsed'] or 0))
                        
                        write_api.write(bucket=BUCKET, record=point)
                        count += 1
                
                print(f"✅ {count} partidos de ligas TOP enviados.")
            
            time.sleep(600) 
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(60)

# (Manten el resto del código del servidor igual)
