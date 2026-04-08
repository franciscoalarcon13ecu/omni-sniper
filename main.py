import requests
import time
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# --- CONFIGURACIÓN (Tus llaves ya están puestas) ---
API_KEY = "a4592942bf83a08e71f9a4c64b4df9e0"
TOKEN = "PB47SRHhqPq6lHe3WUhzojeKaUUBcjvNISL6PSWh2b1kSzgMOscolVFiW67mv19i8pz0TRnuLJy5m0h3WiEg9g=="
ORG = "6025b5f4b3e4e21e"
BUCKET = "19ae67debb050709"
URL = "https://us-east-1-1.aws.cloud2.influxdata.com"

HEADERS = {'x-rapidapi-host': 'v3.football.api-sports.io', 'x-rapidapi-key': API_KEY}

def ejecutar_sniper():
    print("🚀 OMNI-SNIPER ACTIVADO: Iniciando vigilancia mundial...")
    
    while True:
        try:
            # 1. Buscamos partidos que se están jugando EN VIVO
            print(f"🕒 {time.strftime('%H:%M:%S')} - Escaneando partidos en vivo...")
            url_live = "https://v3.football.api-sports.io/fixtures?live=all"
            response = requests.get(url_live, headers=HEADERS).json()
            
            partidos = response.get('response', [])
            
            if not partidos:
                print("📭 No hay partidos en vivo ahora mismo. Esperando...")
            
            with InfluxDBClient(url=URL, token=TOKEN, org=ORG) as client:
                write_api = client.write_api(write_options=SYNCHRONOUS)
                
                for p in partidos:
                    f_id = p['fixture']['id']
                    home = p['teams']['home']['name']
                    away = p['teams']['away']['name']
                    minuto = p['fixture']['status']['elapsed']
                    goles_h = p['goals']['home']
                    goles_a = p['goals']['away']
                    
                    # 2. Guardamos el estado actual del partido
                    point = Point("predicciones_sniper") \
                        .tag("partido", f"{home} vs {away}") \
                        .field("minuto", float(minuto)) \
                        .field("goles_local", float(goles_h)) \
                        .field("goles_visitante", float(goles_a))
                    
                    # 3. Lógica simple de alerta: Si es minuto 70+ y van empatados (ideal para córners)
                    if minuto > 70 and goles_h == goles_a:
                        point.field("alerta_sniper", "🔥 ATAQUE FINAL: Posible Córner/Tarjeta")
                    else:
                        point.field("alerta_sniper", "☕ Analizando...")

                    write_api.write(bucket=BUCKET, record=point)
                    print(f"✅ Monitor: {home} {goles_h}-{goles_a} {away} (Min {minuto})")

            # Esperamos 5 minutos para no saturar tu API gratuita
            print("💤 Barrido completado. Descansando 5 minutos...")
            time.sleep(300)

        except Exception as e:
            print(f"⚠️ Error temporal: {e}. Reintentando en 60s...")
            time.sleep(60)

if __name__ == "__main__":
    ejecutar_sniper()
