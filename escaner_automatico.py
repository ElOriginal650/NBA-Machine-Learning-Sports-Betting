import os
import requests
import numpy as np
from scipy.stats import norm

API_KEY = "cb264c06-f84b-41f9-bbc3-5c00426248fc"
BANKROLL = 50.0  # Puedes cambiar tu saldo disponible aquí

LEAGUES = [
    ("basketball_nba", "NBA"),
    ("basketball_wnba", "WNBA"),
    ("basketball_euroleague", "Euroliga"),
    ("basketball_ncaab", "NCAA")
]

def obtener_cuotas_liga(sport_key, league_name):
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
    params = {
        "apiKey": API_KEY,
        "regions": "us,eu",
        "markets": "totals",
        "oddsFormat": "american"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            print("❌ Error: API Key no válida o expirada.")
            return []
        else:
            return []
    except Exception as e:
        return []

def analizar_mercado(game, league_name):
    home_team = game.get('home_team')
    away_team = game.get('away_team')
    bookmakers = game.get('bookmakers', [])
    
    if not bookmakers:
        return None
        
    pinnacle_total = None
    soft_totals = []
    
    for bm in bookmakers:
        bm_key = bm.get('key')
        for market in bm.get('markets', []):
            if market.get('key') == 'totals':
                outcomes = market.get('outcomes', [])
                over_outcome = next((o for o in outcomes if o.get('name') == 'Over'), None)
                if over_outcome:
                    point = over_outcome.get('point')
                    price = over_outcome.get('price')
                    if bm_key == 'pinnacle':
                        pinnacle_total = (point, price)
                    else:
                        soft_totals.append((bm.get('title'), point, price))
                        
    if not soft_totals:
        return None
        
    # Análisis de cada línea encontrada
    resultados = []
    for book_name, point, price in soft_totals[:3]:
        # Conversión de cuota americana
        if price > 0:
            cuota_dec = (price / 100.0) + 1.0
        else:
            cuota_dec = (100.0 / abs(price)) + 1.0
            
        prob_implicita = 1.0 / cuota_dec
        
        # Proyección probabilística basada en desviación típica de baloncesto
        dev = 12.5 if "NBA" in league_name else 11.0
        # Referencia de línea justa
        ref_linea = pinnacle_total[0] if pinnacle_total else point
        
        # Si la línea de la casa está más baja que la línea de referencia
        diff = ref_linea - point
        prob_real_over = 1.0 - norm.cdf(point, loc=ref_linea, scale=dev)
        ev = (prob_real_over * cuota_dec) - 1.0
        
        resultados.append({
            "partido": f"{away_team} vs {home_team}",
            "liga": league_name,
            "casa": book_name,
            "linea": point,
            "cuota": price,
            "ev": ev,
            "prob_real": prob_real_over
        })
    return resultados

def escanear_todo():
    print("\n" + "="*65)
    print("🚀 ESCÁNER AUTOMÁTICO DE BALONCESTO (+EV) — POCO X6 PRO")
    print("="*65)
    print("Conectando con servidores de cuotas internacionales...")
    
    hay_partidos = False
    oportunidades = []
    
    for sport_key, league_name in LEAGUES:
        games = obtener_cuotas_liga(sport_key, league_name)
        if games:
            hay_partidos = True
            for g in games:
                analisis = analizar_mercado(g, league_name)
                if analisis:
                    for res in analisis:
                        if res['ev'] > 0.02:  # Ventaja matemática mayor al 2%
                            oportunidades.append(res)
                            
    if not hay_partidos:
        print("ℹ️ No hay partidos en vivo programados para hoy en este momento.")
        print("💡 Consejo: Ejecuta el escáner en la tarde/noche (hora de juegos).")
    elif not oportunidades:
        print("🛡️ Análisis completado. Las casas tienen las líneas muy bien ajustadas hoy.")
        print("❌ Ningún partido supera el margen de ventaja matemática (+EV > 2%).")
        print("✅ Disciplina: No apostar hoy para proteger el capital.")
    else:
        print(f"\n🎯 ¡SE ENCONTRARON {len(oportunidades)} APUESTAS CON VALOR (+EV)!\n")
        for op in oportunidades:
            b = ((op['cuota']/100)+1 if op['cuota']>0 else (100/abs(op['cuota']))+1) - 1
            p = op['prob_real']
            q = 1 - p
            kelly = max(0.0, ((p * b - q) / b) * 0.25)
            monto = BANKROLL * kelly
            
            print(f"🏀 Liga:     {op['liga']} — {op['partido']}")
            print(f"🏢 Casa:     {op['casa']}")
            print(f"🎯 Jugada:   MÁS DE {op['linea']} PUNTOS (OVER)")
            print(f"💵 Cuota:    {op['cuota']:+d}")
            print(f"💎 Ventaja:  +{op['ev']*100:.1f}% (+EV)")
            print(f"💰 Apostar:  ${monto:.2f} (de una banca de ${BANKROLL:.2f})")
            print("-" * 65)
            
    print("="*65 + "\n")

if __name__ == '__main__':
    escanear_todo()
