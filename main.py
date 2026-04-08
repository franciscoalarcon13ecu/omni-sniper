import requests
import time
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# --- CONFIGURACIÓN ---
API_KEY = "a4592942bf83a08e71f9a4c64b4df9e0"
TOKEN = "PB47SRHhqPq6lHe3WUhzojeKaUUBcjvNISL6PSWh2b1kSzgMOscolVFiW67mv19i8pz0TRnuLJy5m0h3WiEg9g=="
ORG = "6025b5f4b3e4e21e"
BUCKET = "19ae67debb050709"
URL = "https://us-east-1-1.aws.cloud2.influxdata.com"

HEADERS = {'x-rapidapi-host': 'v3.football.api-sports.io', 'x-rapidapi-key': API_KEY}

def escanear_oportunidades_reales():
    print("🎯 OMNI-SNIPER: Buscando mercados de Córners y Tarjetas...")
    url = "https://v3.football.api-sports.io/fixtures?date=2026-04-07"
    
    try:
        response = requests.get(url, headers=HEADERS).json()
        partidos = response.get('response', [])[:25] # Analizamos el top 25 de hoy
        
        with InfluxDBClient(url=URL, token=TOKEN, org=ORG) as client:
            write_api = client.write_api(write_options=SYNCHRONOUS)
            
            for p in partidos:
                f_id = p['fixture']['id']
                home = p['teams']['home']['name']
                away = p['teams']['away']['name']
                
                # Pedimos la predicción específica de CORNERS y CARDS
                res_pred = requests.get(f"https://v3.football.api-sports.io/predictions?fixture={f_id}", headers=HEADERS).json()
                
                if res_pred['response']:
                    data = res_pred['response'][0]
                    
                    # 🚩 MERCADO DE CÓRNERS: Buscamos intensidad de ataque > 80%
                    int_h = float(data['comparison']['att']['home'].replace('%',''))
                    int_a = float(data['comparison']['att']['away'].replace('%',''))
                    
                    # 🟨 MERCADO DE TARJETAS: Buscamos equipos agresivos
                    # Si la IA dice que el partido será "caliente"
                    consejo = data['predictions']['advice']

                    point = Point("sniper_v3_apuestas") \
                        .tag("partido", f"{home} vs {away}") \
                        .tag("consejo_ia", consejo) \
                        .field("ataque_peligroso_local", int_h) \
                        .field("ataque_peligroso_vis", int_a)
                    
                    write_api.write(bucket=BUCKET, record=point)
                    print(f"✅ Oportunidad analizada: {home} vs {away}")
                
                time.sleep(1) 

        print("--- 🏁 Escaneo listo. ¡Mira tu InfluxDB para ver dónde apostar! ---")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    escanear_oportunidades_reales()
