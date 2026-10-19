import numpy as np
from scipy.stats import norm

def calcular_valor_totales(pace_a, pace_b, ortg_a, drtg_a, ortg_b, drtg_b, linea_casa, cuota_americana, bankroll=100.0, dev_estandar=11.5):
    """
    Motor cuantitativo de Totales (Over/Under) en Baloncesto.
    Optimizado para arquitectura ARM64 (MediaTek Dimensity / Cortex-A715).
    """
    posesiones_esperadas = (pace_a + pace_b) / 2.0
    eficiencia_a = (ortg_a + drtg_b) / 2.0
    eficiencia_b = (ortg_b + drtg_a) / 2.0
    puntos_proyectados = posesiones_esperadas * (eficiencia_a + eficiencia_b) / 100.0
    
    prob_over = 1.0 - norm.cdf(linea_casa, loc=puntos_proyectados, scale=dev_estandar)
    prob_under = 1.0 - prob_over
    
    if cuota_americana > 0:
        cuota_decimal = (cuota_americana / 100.0) + 1.0
    else:
        cuota_decimal = (100.0 / abs(cuota_americana)) + 1.0
        
    prob_implicita_casa = 1.0 / cuota_decimal
    ev_over = (prob_over * cuota_decimal) - 1.0
    
    print("\n" + "="*50)
    print("🏀 RESULTADOS DEL ANÁLISIS CUANTITATIVO")
    print("="*50)
    print(f"📊 PROYECCIÓN MATEMÁTICA: {puntos_proyectados:.1f} PUNTOS")
    print(f"🎯 LÍNEA DE LA CASA:      {linea_casa} (Cuota: {cuota_americana:+.0f} / Dec: {cuota_decimal:.2f})")
    print(f"📈 Probabilidad Real Over:  {prob_over*100:.1f}%")
    print(f"📉 Probabilidad Real Under: {prob_under*100:.1f}%")
    print(f"🏦 Probabilidad de la Casa: {prob_implicita_casa*100:.1f}%")
    print(f"💎 Valor Esperado (+EV):    {ev_over*100:+.2f}%")
    print("="*50)
    
    if ev_over > 0.03:
        b = cuota_decimal - 1.0
        p = prob_over
        q = 1.0 - p
        kelly_full = (p * b - q) / b
        kelly_fraccional = max(0.0, kelly_full * 0.25)
        apuesta_sugerida = bankroll * kelly_fraccional
        print(f"✅ SEÑAL +EV CONFIRMADA: APOSTAR AL OVER (Más de {linea_casa})")
        print(f"💵 Stake seguro (1/4 Kelly): {kelly_fraccional*100:.2f}% de tu capital")
        print(f"💰 Monto sugerido a apostar: ${apuesta_sugerida:.2f} (de una banca de ${bankroll:.2f})")
    elif ev_over < -0.05:
        print(f"⚠️ SIN VALOR EN OVER. (Si la cuota de Under es favorable, evalúa el Under).")
    else:
        print("❌ LÍNEA BIEN AJUSTADA POR LA CASA: No hay ventaja suficiente (+EV < 3%).")
    print("="*50 + "\n")

def menu_interactivo():
    print("\n==============================================")
    print("⚡ MOTOR DE BALONCESTO POCO X6 PRO (+EV)")
    print("==============================================")
    print("1. Ejecutar análisis del partido de ejemplo (WNBA 152.5)")
    print("2. Analizar un partido nuevo (Ingresar datos a mano)")
    print("3. Salir")
    opcion = input("\nElige una opción (1, 2 o 3): ").strip()
    
    if opcion == '1':
        calcular_valor_totales(
            pace_a=78.5, pace_b=80.2,
            ortg_a=101.4, drtg_a=98.2,
            ortg_b=99.1, drtg_b=102.5,
            linea_casa=152.5,
            cuota_americana=-113,
            bankroll=100.0
        )
    elif opcion == '2':
        print("\n--- DATOS DEL PARTIDO NUEVO ---")
        linea = float(input("Línea de totales de la casa (ej: 152.5 o 224.5): "))
        cuota = float(input("Cuota americana (ej: -113 o +105): "))
        banca = float(input("Tu saldo/banca total disponible en $ (ej: 50): "))
        
        tipo_liga = input("¿Es liga de 40 min (WNBA/Europa) o 48 min (NBA)? [40/48]: ").strip()
        if tipo_liga == '48':
            pace_default = 100.0
            dev = 13.0
        else:
            pace_default = 79.0
            dev = 11.5
            
        usar_avanzado = input("¿Tienes ritmo y rating exactos? (s/n, si pones 'n' usa promedios de liga): ").strip().lower()
        if usar_avanzado == 's':
            pa = float(input("Ritmo/Pace Equipo A: "))
            pb = float(input("Ritmo/Pace Equipo B: "))
            oa = float(input("Offensive Rating A: "))
            da = float(input("Defensive Rating A: "))
            ob = float(input("Offensive Rating B: "))
            db = float(input("Defensive Rating B: "))
        else:
            pa, pb = pace_default, pace_default
            pts_esperados_aprox = float(input(f"¿Promedio de puntos combinados que estimas para este partido? (ej: {linea}): "))
            oa, ob = pts_esperados_aprox / (pace_default * 2 / 100), pts_esperados_aprox / (pace_default * 2 / 100)
            da, db = oa, ob
            
        calcular_valor_totales(pa, pb, oa, da, ob, db, linea, cuota, banca, dev)
    else:
        print("Saliendo...")

if __name__ == '__main__':
    menu_interactivo()
