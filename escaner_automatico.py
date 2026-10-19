import requests
import numpy as np
from scipy.stats import norm
from collections import defaultdict

API_KEY = "a1f88a0ccdaf54bb1ea4ab293e93b87d"
BANKROLL = 50.0  # Tu capital de trabajo en $

LEAGUES = [
    ("basketball_nba", "NBA"),
    ("basketball_wnba", "WNBA"),
    ("basketball_euroleague", "Euroliga"),
    ("basketball_ncaab", "NCAA")
]

def obtener_partidos(sport_key):
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
    params = {
        "apiKey": API_KEY,
        "regions": "us,eu",
        "markets": "totals",
        "oddsFormat": "american"
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            creditos = r.headers.get('x-requests-remaining', 'N/A')
            return r.json(), creditos
        return [], "OK"
    except Exception:
        return [], "Error"

def procesar_mercado_limpio():
    print("\n" + "="*65)
    print("🎯 ESCÁNER MAESTRO PARA TRIUNFOBET / ALTERNA — BALONCESTO")
    print("="*65)
    print("Analizando líneas mundiales (Over y Under) sin repeticiones...\n")
    
    creditos = None
    partidos_procesados = {}
    
    for sport_key, league_name in LEAGUES:
        datos, cred = obtener_partidos(sport_key)
        if cred and cred not in ("Error 401", "Error", "OK"):
            creditos = cred
            
        if not datos:
            continue
            
        for game in datos:
            home = game.get('home_team')
            away = game.get('away_team')
            partido_id = f"{away} vs {home}"
            
            pinnacle_point = None
            todas_las_lineas = []
            
            for bm in game.get('bookmakers', []):
                es_pinnacle = (bm.get('key') == 'pinnacle')
                for m in bm.get('markets', []):
                    if m.get('key') == 'totals':
                        for out in m.get('outcomes', []):
                            pt = out.get('point')
                            price = out.get('price')
                            name = out.get('name')  # 'Over' o 'Under'
                            todas_las_lineas.append((name, pt, price))
                            if es_pinnacle and name == 'Over':
                                pinnacle_point = pt
                                
            if not todas_las_lineas:
                continue
                
            # Calcular la línea de consenso mundial promedio
            overs = [pt for name, pt, price in todas_las_lineas if name == 'Over']
            if overs:
                linea_media = round(float(np.median(overs)), 1)
                linea_sharp = pinnacle_point if pinnacle_point else linea_media
                partidos_procesados[partido_id] = {
                    "liga": league_name,
                    "partido": partido_id,
                    "linea_media": linea_media,
                    "linea_pinnacle": linea_sharp
                }

    if not partidos_procesados:
        print("ℹ️ No hay partidos de baloncesto activos en este momento.")
    else:
        print(f"📊 Se analizaron {len(partidos_procesados)} partidos únicos. Aquí están las señales claras:\n")
        
        for p_id, info in partidos_procesados.items():
            l_med = info['linea_media']
            l_pin = info['linea_pinnacle']
            liga = info['liga']
            
            print(f"🏀 [{liga}] {p_id}")
            print(f"🌍 Línea de Consenso Mundial: {l_med} puntos (Pinnacle: {l_pin})")
            print(f"📌 QUÉ BUSCAR EXACTAMENTE EN TRIUNFOBET / ALTERNA:")
            print(f"   👉 Opción A (OVER):  Si Triunfobet te da MÁS DE {l_med - 1.5:.1f} o menos  --> ¡METE AL OVER!")
            print(f"   👉 Opción B (UNDER): Si Triunfobet te da MENOS DE {l_med + 1.5:.1f} o más --> ¡METE AL UNDER!")
            print(f"💰 Apuesta recomendada: $1.25 (2.5% de tu banca)")
            print("-" * 65)

    if creditos:
        print(f"\n📊 Créditos restantes de tu plan gratuito: {creditos} de 500")
    print("="*65 + "\n")

if __name__ == '__main__':
    procesar_mercado_limpio()
