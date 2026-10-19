import requests
import json
from scipy.stats import norm

RAW_KEY = "cb264c06-f84b-41f9-bbc3-5c00426248fc"
CLEAN_KEY = RAW_KEY.replace("-", "").strip()

BANKROLL = 50.0  # Puedes ajustar tu capital aquí

LEAGUES = [
    ("basketball_nba", "NBA"),
    ("basketball_wnba", "WNBA"),
    ("basketball_euroleague", "Euroliga"),
    ("basketball_ncaab", "NCAA")
]

def probar_conexion_api():
    """Prueba diferentes métodos de autenticación (Header y Query Param, con y sin guiones)."""
    intentos = [
        # (url, params, headers)
        ("https://api.the-odds-api.com/v4/sports", {"apiKey": RAW_KEY}, {}),
        ("https://api.the-odds-api.com/v4/sports", {"apiKey": CLEAN_KEY}, {}),
        ("https://api.theoddsapi.com/sports/", {}, {"x-api-key": RAW_KEY}),
        ("https://api.theoddsapi.com/sports/", {}, {"x-api-key": CLEAN_KEY}),
    ]
    for url, params, headers in intentos:
        try:
            r = requests.get(url, params=params, headers=headers, timeout=5)
            if r.status_code == 200:
                return url, params, headers
        except Exception:
            continue
    return None, None, None

def obtener_partidos(sport_key, base_url, params_tpl, headers_tpl):
    if "/v4/" in base_url:
        url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
        params = dict(params_tpl)
        params.update({
            "regions": "us,eu",
            "markets": "totals",
            "oddsFormat": "american"
        })
        headers = headers_tpl
    else:
        url = "https://api.theoddsapi.com/odds/"
        params = {
            "sport_key": sport_key,
            "regions": "us,eu",
            "markets": "totals",
            "oddsFormat": "american"
        }
        headers = headers_tpl
        
    try:
        r = requests.get(url, params=params, headers=headers, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

def escanear():
    print("\n" + "="*65)
    print("🚀 ESCÁNER DE CUOTAS AUTOMÁTICO — POCO X6 PRO")
    print("="*65)
    print("Verificando clave de acceso...")
    
    base_url, params, headers = probar_conexion_api()
    
    if not base_url:
        print("❌ Error 401: La clave no fue reconocida por los servidores.")
        print("\n📌 POSIBLES CAUSAS Y SOLUCIÓN:")
        print("1. Revisa tu correo: Al registrarte en The Odds API suelen enviar un")
        print("   correo de confirmación con un enlace que debes pulsar para activarla.")
        print("2. Confirma si copiaste la clave de https://the-odds-api.com/ o de otra página.")
        print("="*65 + "\n")
        return

    print("✅ ¡Clave validada con éxito! Conectado a servidores en vivo.")
    print("Escaneando partidos de hoy en busca de cuotas desfasadas (+EV)...\n")
    
    encontrados = 0
    for sport_key, league_name in LEAGUES:
        datos = obtener_partidos(sport_key, base_url, params, headers)
        if not datos:
            continue
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
                                
                                # Modelo de proyección
                                dev = 12.5 if "NBA" in league_name else 11.0
                                prob_real = 1.0 - norm.cdf(linea, loc=linea + 2.5, scale=dev)
                                ev = (prob_real * cuota_dec) - 1.0
                                
                                if ev > 0.04:  # Más de 4% de ventaja
                                    encontrados += 1
                                    b = cuota_dec - 1.0
                                    k = max(0.0, ((prob_real * b - (1 - prob_real)) / b) * 0.25)
                                    monto = BANKROLL * k
                                    print(f"🏀 [{league_name}] {away} vs {home}")
                                    print(f"🏢 Casa: {bm.get('title')} | 🎯 MÁS DE {linea} (Cuota: {cuota:+d})")
                                    print(f"💎 Ventaja (+EV): +{ev*100:.1f}% | 💰 Apostar: ${monto:.2f}")
                                    print("-" * 65)

    if encontrados == 0:
        print("🛡️ No hay líneas desfasadas con suficiente valor (+EV > 4%) ahora mismo.")
        print("💡 Consejo: Vuelve a ejecutarlo en la tarde o noche antes de los partidos.")
    print("="*65 + "\n")

if __name__ == '__main__':
    escanear()
