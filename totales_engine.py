import numpy as np
from scipy.stats import norm

def calcular_valor_totales(pace_a, pace_b, ortg_a, drtg_a, ortg_b, drtg_b, linea_casa, cuota_americana, bankroll=100.0, dev_estandar=11.5):
    """
    Motor cuantitativo de Totales (Over/Under) en Baloncesto.
    - Pace: Posesiones por 40 min (WNBA/Europa) o 48 min (NBA)
    - Ortg/Drtg: Puntos anotados/concedidos por 100 posesiones
    """
    # 1. Proyección de ritmo (Posesiones esperadas)
    posesiones_esperadas = (pace_a + pace_b) / 2.0
    
    # 2. Eficiencia proyectada combinada
    eficiencia_a = (ortg_a + drtg_b) / 2.0
    eficiencia_b = (ortg_b + drtg_a) / 2.0
    
    # 3. Puntos totales esperados por el modelo
    puntos_proyectados = posesiones_esperadas * (eficiencia_a + eficiencia_b) / 100.0
    
    # 4. Probabilidad acumulada mediante distribución normal
    prob_over = 1.0 - norm.cdf(linea_casa, loc=puntos_proyectados, scale=dev_estandar)
    
    # 5. Conversión de cuota americana a decimal
    if cuota_americana > 0:
        cuota_decimal = (cuota_americana / 100.0) + 1.0
    else:
        cuota_decimal = (100.0 / abs(cuota_americana)) + 1.0
        
    prob_implicita_casa = 1.0 / cuota_decimal
    
    # 6. Cálculo del Valor Esperado (+EV)
    ev = (prob_over * cuota_decimal) - 1.0
    
    print("\n==============================================")
    print(f"📊 PROYECCIÓN DEL MODELO: {puntos_proyectados:.1f} PUNTOS")
    print(f"🎯 LÍNEA DE LA CASA:     {linea_casa} (Cuota: {cuota_americana})")
    print(f"📈 Probabilidad Real Over: {prob_over*100:.1f}% vs Implícita Casa: {prob_implicita_casa*100:.1f}%")
    print(f"💎 Valor Esperado (+EV):    {ev*100:+.2f}%")
    print("==============================================")
    
    # 7. Gestión de banca con Criterio de Kelly (Fraccional 1/4)
    if ev > 0.03:
        b = cuota_decimal - 1.0
        p = prob_over
        q = 1.0 - p
        kelly_full = (p * b - q) / b
        kelly_fraccional = max(0.0, kelly_full * 0.25)
        apuesta_sugerida = bankroll * kelly_fraccional
        print(f"✅ SEÑAL +EV DETECTADA: Apostar al OVER")
        print(f"💵 Stake sugerido (1/4 Kelly): {kelly_fraccional*100:.2f}% de tu banca (${apuesta_sugerida:.2f})")
    else:
        print("❌ SIN VALOR MATEMÁTICO: No apostar en este partido.")

if __name__ == '__main__':
    print("Iniciando motor de predicción de totales de baloncesto...")
    # Ejemplo WNBA con línea de 152.5 a cuota -113:
    calcular_valor_totales(
        pace_a=78.5, pace_b=80.2,
        ortg_a=101.4, drtg_a=98.2,
        ortg_b=99.1, drtg_b=102.5,
        linea_casa=152.5,
        cuota_americana=-113,
        bankroll=100.0
    )
