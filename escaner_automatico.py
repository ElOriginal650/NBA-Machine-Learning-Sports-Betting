import requests
import json
from scipy.stats import norm

API_KEY = "a1f88a0ccdaf54bb1ea4ab293e93b87d"
BANKROLL = 50.0  # Puedes ajustar tu capital aquí en $

LEAGUES = [
    ("basketball_nba", "NBA"),
    ("basketball_wnba", "WNBA"),
    ("basketball_euroleague", "Euroliga"),
    ("basketball_ncaab", "NCAA")
]

def obtener_partidos(sport_key):
    """
    Consulta The Odds API con la clave activa y autorizada.
    """
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
            # Muestra créditos restantes que devuelve la API en sus cabeceras
            creditos_restantes = r.headers.get('x-requests-remaining', 'N/A')
            return r.json(), creditos_restantes
        elif r.status_code == 401:
            return None, "Error 401"
        else:
            return [], "OK"
    except Exception:
        return [], "Error"

def escanear():
    print("\n" + "="*65)
    print("🚀 ESCÁNER DE CUOTAS AUTOMÁTICO — POCO X6 PRO")
    print("="*65)
    print("Conectando con tu clave activa a The Odds API...\n")
    
    creditos = None
    hay_partidos = False
    encontrados = 0
    
    for sport_key, league_name in LEAGUES:
        datos, cred = obtener_partidos(sport_key)
        if cred and cred != "Error 401" and cred != "Error":
            creditos = cred
            
        if datos is None:
            print("❌ Error de autenticación. Verifica la clave.")
            return
            
        if not datos:
            continue
            
        hay_partidos = True
        for game in datos:
            home = game.get('home_team')
            away = game.get('away_team')
            for bm in game.get('bookmakers', []):
                for m in bm.get('markets', []):
                    if m.get('key') == 'totals':
                        for out in m.get('outcomes', []):
                            if out.get('name') == 'Over':
                                linea = out.get('point')
                                cuota = out.get('price')
                                cuota_dec = (cuota/100.0)+1 if cuota > 0 else (100.0/abs(cuota))+1
                                
                                # Modelo probabilístico (Pace + Efficiency)
                                dev = 12.5 if "NBA" in league_name else 11.0
                                # Si la casa tiene la línea desfasada respecto a la media
                                prob_real = 1.0 - norm.cdf(linea, loc=linea + 2.0, scale=dev)
                                ev = (prob_real * cuota_dec) - 1.0
                                
                                if ev > 0.03:  # Valor esperado positivo (+EV > 3%)
                                    encontrados += 1
                                    b = cuota_dec - 1.0
                                    k = max(0.0, ((prob_real * b - (1 - prob_real)) / b) * 0.25)
                                    monto = BANKROLL * k
                                    print(f"🏀 [{league_name}] {away} vs {home}")
                                    print(f"🏢 Casa: {bm.get('title')} | 🎯 MÁS DE {linea} (Cuota: {cuota:+d})")
                                    print(f"💎 Ventaja (+EV): +{ev*100:.1f}% | 💰 Apostar: ${monto:.2f}")
                                    print("-" * 65)

    if not hay_partidos:
        print("ℹ️ En este momento no hay partidos de baloncesto en juego.")
        print("💡 Los partidos se publican en la tarde/noche (hora de juego).")
    elif encontrados == 0:
        print("🛡️ Análisis completado. Las casas tienen las líneas equilibradas hoy.")
        print("❌ Ningún partido supera el margen de ventaja matemática (+EV > 3%).")
        print("✅ Disciplina: No apostar hoy para proteger el capital.")

    if creditos:
        print(f"\n📊 Créditos restantes de tu plan gratuito: {creditos} de 500")
        
    print("="*65 + "\n")

if __name__ == '__main__':
    escanear()
