import requests, time, threading, datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- CONFIGURACIÓN ---
API_KEY = "a4592942bf83a08e71f9a4c64b4df9e0"
TOKEN = "SNUjIrVrOCokuIBE2XbDa0GnLhhQ4R5RIFLi_7cA91-QG3mv0il3SIwid8B7vUCnGzxGk5-fVbXgBAoI0Aj2KA=="
ORG = "6025b5f4b3e4e21e"
BUCKET = "ApuestasDeportivas2"
URL_INFLUX = "https://us-east-1-1.aws.cloud2.influxdata.com"
WEBHOOK_DISCORD = "https://discord.com/api/webhooks/1491508795161968802/dxaKzEZ1QP0fmAPZgI_HEytnDBgpmws3tMmRL0HaVsF1-P6SPSrqL2s6zpOICzvRiQFc"
HEADERS = {'x-rapidapi-host': 'v3.football.api-sports.io', 'x-rapidapi-key': API_KEY}

def enviar_a_discord(embed):
    # Usamos embeds para que el mensaje se vea profesional (colores y tablas)
    requests.post(WEBHOOK_DISCORD, json={"embeds": [embed]})

def obtener_analisis_partido(fixture_id):
    """ Consulta el endpoint de predicciones para obtener córners, tarjetas y 1X2 """
    url = f"https://v3.football.api-sports.io/predictions?fixture={fixture_id}"
    try:
        data = requests.get(url, headers=HEADERS).json()
        if data['response']:
            return data['response'][0]
    except: return None

def ejecutar_sniper():
    enviar_a_discord({"title": "🚀 SISTEMA OMNI-SNIPER ONLINE", "color": 3066993})
    
    while True:
        try:
            hoy = datetime.datetime.now().strftime('%Y-%m-%d')
            url_fixtures = f"https://v3.football.api-sports.io/fixtures?date={hoy}"
            partidos = requests.get(url_fixtures, headers=HEADERS).json().get('response', [])
            
            client = InfluxDBClient(url=URL_INFLUX, token=TOKEN, org=ORG)
            write_api = client.write_api(write_options=SYNCHRONOUS)

            for p in partidos:
                # Solo analizamos ligas top o partidos importantes para no saturar la API
                fix_id = p['fixture']['id']
                analisis = obtener_analisis_partido(fix_id)
                
                if analisis:
                    probs = analisis['predictions']['percent']
                    # Filtro de margen del 35%
                    p_local = float(probs['home'].replace('%',''))
                    p_empate = float(probs['draw'].replace('%',''))
                    p_visita = float(probs['away'].replace('%',''))

                    match_name = f"{p['teams']['home']['name']} vs {p['teams']['away']['name']}"
                    
                    # --- CONSTRUCCIÓN DEL MENSAJE PARA DISCORD ---
                    stats_msg = ""
                    if p_local > 35: stats_msg += f"🏠 Victoria Local: {p_local}%\n"
                    if p_empate > 35: stats_msg += f"🤝 Empate: {p_empate}%\n"
                    
                    # Datos de Córners y Goles (si superan el 35% de fuerza)
                    if analisis['comparison']['corners']['home']:
                        stats_msg += f"🚩 Fuerza Córners: {analisis['comparison']['corners']['home']}\n"

                    embed = {
                        "title": f"🎯 ANALISIS: {match_name}",
                        "description": stats_msg,
                        "color": 1515833 if p_local > 50 else 15844367,
                        "footer": {"text": f"ID: {fix_id} | Omni-Sniper V2"}
                    }
                    
                    # Solo enviamos si hay algo que supere el 35%
                    if stats_msg:
                        enviar_a_discord(embed)

                    # Guardar en InfluxDB
                    point = Point("predicciones_sniper") \
                        .tag("partido", match_name) \
                        .field("prob_local", p_local) \
                        .field("prob_empate", p_empate)
                    write_api.write(bucket=BUCKET, record=point)

            client.close()
            time.sleep(3600) # Una vez por hora es suficiente para pre-partido
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

# --- SERVIDOR WEB ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"Omni-Sniper Active")

if __name__ == "__main__":
    threading.Thread(target=ejecutar_sniper, daemon=True).start()
    HTTPServer(('0.0.0.0', 10000), SimpleHandler).serve_forever()

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Sniper Working")

if __name__ == "__main__":
    threading.Thread(target=ejecutar_sniper, daemon=True).start()
    HTTPServer(('0.0.0.0', 10000), SimpleHandler).serve_forever()
