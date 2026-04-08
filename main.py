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
    try:
        requests.post(WEBHOOK_DISCORD, json={"embeds": [embed]})
    except:
        pass

def obtener_analisis_partido(fixture_id):
    url = f"https://v3.football.api-sports.io/predictions?fixture={fixture_id}"
    try:
        data = requests.get(url, headers=HEADERS).json()
        if data['response']:
            return data['response'][0]
    except: return None

def ejecutar_sniper():
    print("🚀 OMNI-SNIPER V3.0 INICIADO")
    enviar_a_discord({"title": "🚀 SISTEMA OMNI-SNIPER ONLINE", "color": 3066993})
    
    while True:
        try:
            hoy = datetime.datetime.now().strftime('%Y-%m-%d')
            url_fixtures = f"https://v3.football.api-sports.io/fixtures?date={hoy}"
            partidos = requests.get(url_fixtures, headers=HEADERS).json().get('response', [])
            
            client = InfluxDBClient(url=URL_INFLUX, token=TOKEN, org=ORG)
            write_api = client.write_api(write_options=SYNCHRONOUS)

            for p in partidos:
                fix_id = p['fixture']['id']
                analisis = obtener_analisis_partido(fix_id)
                
                if analisis:
                    probs = analisis['predictions']['percent']
                    p_local = float(probs['home'].replace('%',''))
                    p_empate = float(probs['draw'].replace('%',''))
                    p_visita = float(probs['away'].replace('%',''))

                    match_name = f"{p['teams']['home']['name']} vs {p['teams']['away']['name']}"
                    
                    # --- FILTRO MAESTRO > 35% ---
                    stats_msg = ""
                    if p_local > 35: stats_msg += f"🏠 Victoria Local: **{p_local}%**\n"
                    if p_empate > 35: stats_msg += f"🤝 Empate: **{p_empate}%**\n"
                    if p_visita > 35: stats_msg += f"🚀 Victoria Visita: **{p_visita}%**\n"
                    
                    # Córners y Tarjetas (Comparativa)
                    comp = analisis['comparison']
                    if comp['corners']['home']:
                        stats_msg += f"🚩 Fuerza Córners: {comp['corners']['home']}\n"
                    if comp['cards']['home']:
                        stats_msg += f"🟨 Prob. Tarjetas: {comp['cards']['home']}\n"

                    if stats_msg:
                        embed = {
                            "title": f"🏟️ {match_name}",
                            "description": stats_msg,
                            "color": 3066993 if p_local > 50 else 15105570,
                            "footer": {"text": f"ID: {fix_id} | Margen >35%"},
                            "timestamp": datetime.datetime.utcnow().isoformat()
                        }
                        enviar_a_discord(embed)

                    # Guardar en InfluxDB para tu query de Flux
                    point = Point("predicciones_sniper") \
                        .tag("partido", match_name) \
                        .field("prob_local", p_local) \
                        .field("prob_empate", p_empate) \
                        .field("prob_visita", p_visita)
                    write_api.write(bucket=BUCKET, record=point)

            client.close()
            time.sleep(3600) 
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

# --- SERVIDOR WEB (UNIFICADO) ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Omni-Sniper Active and Working")

if __name__ == "__main__":
    # Iniciamos el sniper en un hilo separado
    threading.Thread(target=ejecutar_sniper, daemon=True).start()
    # Iniciamos el servidor web en el hilo principal
    print("🌍 Servidor Web en puerto 10000")
    HTTPServer(('0.0.0.0', 10000), SimpleHandler).serve_forever()
