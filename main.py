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
    except: pass

def obtener_predicciones(fixture_id):
    url = f"https://v3.football.api-sports.io/predictions?fixture={fixture_id}"
    try:
        data = requests.get(url, headers=HEADERS).json()
        return data['response'][0] if data['response'] else None
    except: return None

def ejecutar_sniper():
    print("🚀 OMNI-SNIPER V5.1 ACTIVADO")
    client = InfluxDBClient(url=URL_INFLUX, token=TOKEN, org=ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    while True:
        try:
            hoy = datetime.datetime.now().strftime('%Y-%m-%d')
            r = requests.get(f"https://v3.football.api-sports.io/fixtures?date={hoy}", headers=HEADERS).json()
            partidos = r.get('response', [])
            
            for p in partidos:
                fix_id = p['fixture']['id']
                match_name = f"{p['teams']['home']['name']} vs {p['teams']['away']['name']}"
                data = obtener_predicciones(fix_id)
                
                if data:
                    perc = data['predictions']['percent']
                    p_local = float(perc['home'].replace('%',''))
                    p_empate = float(perc['draw'].replace('%',''))
                    p_visita = float(perc['away'].replace('%',''))

                    if p_local > 35 or p_empate > 35 or p_visita > 35:
                        embed = {
                            "title": f"🏟️ {match_name}",
                            "description": f"🏠 Local: {p_local}% | 🤝 Empate: {p_empate}% | 🚀 Visita: {p_visita}%",
                            "color": 3066993 if p_local > 50 else 15105570,
                            "footer": {"text": f"ID: {fix_id} | Margen >35%"}
                        }
                        enviar_a_discord(embed)

                        point = Point("predicciones_sniper") \
                            .tag("partido", match_name) \
                            .field("prob_local", p_local) \
                            .field("prob_empate", p_empate) \
                            .field("prob_visita", p_visita)
                        write_api.write(bucket=BUCKET, record=point)

            print("✅ Ciclo completado. Esperando 1 hora...")
            time.sleep(3600)
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(60)

# --- SERVIDOR PARA EVITAR ERROR DE DEPLOY ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Sniper V5.1 is Alive")

if __name__ == "__main__":
    # El Sniper corre en el fondo
    threading.Thread(target=ejecutar_sniper, daemon=True).start()
    # El servidor web mantiene vivo el Deploy en Render
    port = 10000
    print(f"🌍 Servidor escuchando en puerto {port}")
    HTTPServer(('0.0.0.0', port), SimpleHandler).serve_forever()
