import os
import requests
from datetime import datetime, timezone, timedelta

API = "a1f88a0ccdaf54bb1ea4ab293e93b87d"
VZLA = timezone(timedelta(hours=-4))
hoy = datetime.now(VZLA).date()

LEAGUES = [
    ("basketball_nba", "NBA"),
    ("basketball_wnba", "WNBA"),
    ("basketball_euroleague", "Euroliga"),
    ("basketball_ncaab", "NCAA")
]

print("\n" + "="*60)
print(f"🔥 JUGADAS CONFIRMADAS DE HOY ({hoy.strftime('%d/%m/%Y')})")
print("="*60)
print("Escaneando partidos de hoy en vivo...\n")

total = 0
ops = 0

for leg, leg_name in LEAGUES:
    try:
        url = f"https://api.the-odds-api.com/v4/sports/{leg}/odds"
        params = {"apiKey": API, "regions": "us,eu", "markets": "totals", "oddsFormat": "american"}
        r = requests.get(url, params=params, timeout=10).json()
        for g in r:
            dt = datetime.fromisoformat(g["commence_time"].replace("Z", "+00:00")).astimezone(VZLA)
            if dt.date() != hoy:
                continue
            total += 1
            h = dt.strftime("%I:%M %p")
            pin = None
            soft = []
            for bm in g.get("bookmakers", []):
                for m in bm.get("markets", []):
                    if m.get("key") == "totals":
                        for o in m.get("outcomes", []):
                            if o.get("name") == "Over":
                                if bm.get("key") == "pinnacle":
                                    pin = o.get("point")
                                else:
                                    soft.append(o.get("point"))
            if not soft:
                continue
            ref = pin if pin else round(sum(soft)/len(soft), 1)
            ops += 1
            print(f"🏀 [{leg_name}] {g['away_team']} vs {g['home_team']}")
            print(f"📅 FECHA:   HOY ({dt.strftime('%d/%m/%Y')}) — ⏰ {h} (Hora Venezuela)")
            print(f"🌍 LÍNEA PINNACLE (Mundial): {ref} puntos")
            print(f"\n📌 QUÉ VERIFICAR EN TRIUNFOBET:")
            print(f"   ❌ Si Triunfobet tiene {ref} --> NO APOSTAR (Líneas iguales).")
            print(f"   👉 Si Triunfobet te da MÁS DE {ref-1.5:.1f} o menos --> ¡METE AL OVER!")
            print(f"   👉 Si Triunfobet te da MENOS DE {ref+1.5:.1f} o más --> ¡METE AL UNDER!")
            print(f"💰 Stake seguro sugerido: $1.25\n" + "-"*60)
    except Exception:
        pass

if ops == 0:
    print(f"🛡️ Se revisaron {total} partidos. Cero partidos para hoy en este momento.")
    print("💡 Consejo: Vuelve a ejecutarlo en la tarde o noche antes de los juegos.")
else:
    print(f"🎯 {ops} partidos de HOY analizados con éxito.")
    os.system('termux-notification --title "🚨 APUESTAS DE HOY" --content "Partidos listos en pantalla" --sound 2>/dev/null')
print("="*60 + "\n")
