import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import config

CONFIG = config.CONFIG

# ============================================
# INDICADORES TECNICOS AVANZADOS (QUANT)
# ============================================


def calculate_rsi(prices, period=14):
    """RSI - Relative Strength Index (Wilder smoothing)"""
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def calculate_stochastic(high, low, close, k_period=14, d_period=3):
    """Stochastic Oscillator %K y %D"""
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    stoch_k = 100 * (close - lowest_low) / (highest_high - lowest_low)
    stoch_d = stoch_k.rolling(window=d_period).mean()
    return stoch_k, stoch_d


def calculate_macd(prices, fast=12, slow=26, signal=9):
    """MACD"""
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    return macd, signal_line, histogram


def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """Bollinger Bands"""
    sma = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    percent_b = (prices - lower) / (upper - lower)
    return upper, sma, lower, percent_b


def calculate_atr(high, low, close, period=14):
    """ATR - Average True Range"""
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False).mean()


def calculate_adx(high, low, close, period=14):
    """ADX - Average Directional Index"""
    plus_dm = high.diff().clip(lower=0)
    minus_dm = (-low.diff()).clip(lower=0)
    tr = calculate_atr(high, low, close, period) * period
    plus_di = 100 * (plus_dm.ewm(alpha=1 / period).mean() / tr)
    minus_di = 100 * (minus_dm.ewm(alpha=1 / period).mean() / tr)
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.ewm(alpha=1 / period).mean()
    return adx, plus_di, minus_di


def calculate_momentum(prices, period=10):
    """Momentum - Rate of Change"""
    return prices.pct_change(periods=period) * 100


def calculate_cci(high, low, close, period=20):
    """CCI - Commodity Channel Index"""
    tp = (high + low + close) / 3
    sma_tp = tp.rolling(window=period).mean()
    mad = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
    return (tp - sma_tp) / (0.015 * mad)


def calculate_williams_r(high, low, close, period=14):
    """Williams %R"""
    highest = high.rolling(window=period).max()
    lowest = low.rolling(window=period).min()
    return -100 * (highest - close) / (highest - lowest)


def analyze_quant(ticker, cfg):
    """Analisis cuantitativo completo"""
    try:
        data = yf.download(
            ticker, period=cfg["period"], interval=cfg["interval"], progress=False
        )
        if isinstance(data.columns, pd.MultiIndex):
            data = data.xs(ticker, level=1, axis=1)
    except:
        return None

    if len(data) == 0:
        return None

    close = data["Close"]
    high = data["High"]
    low = data["Low"]

    rsi = calculate_rsi(close)
    stoch_k, stoch_d = calculate_stochastic(high, low, close)
    macd, signal, hist = calculate_macd(close)
    bb_upper, bb_middle, bb_lower, bb_percent = calculate_bollinger_bands(close)
    atr = calculate_atr(high, low, close)
    adx, plus_di, minus_di = calculate_adx(high, low, close)
    momentum = calculate_momentum(close)
    cci = calculate_cci(high, low, close)
    williams = calculate_williams_r(high, low, close)

    def val(x):
        return (
            float(x.iloc[-1])
            if not pd.isna(x.iloc[-1])
            else (
                50
                if "rsi" in str(type(x)).lower() or "stoch" in str(type(x)).lower()
                else 0
            )
        )

    current_price = float(close.iloc[-1])
    current_rsi = val(rsi)
    current_stoch_k = val(stoch_k)
    current_stoch_d = val(stoch_d)
    current_macd = val(macd)
    current_hist = val(hist)
    current_bb_percent = val(bb_percent)
    current_adx = val(adx)
    current_momentum = val(momentum)
    current_cci = val(cci)
    current_williams = val(williams)
    current_plus_di = val(plus_di)
    current_minus_di = val(minus_di)

    score = 0
    signals = []

    # RSI
    if current_rsi < 30:
        score += 2
        signals.append(f"RSI sobrevendido ({current_rsi:.1f})")
    elif current_rsi > 70:
        score -= 2
        signals.append(f"RSI sobrecomprado ({current_rsi:.1f})")

    # Stochastic
    if current_stoch_k < 20 and current_stoch_d < 20:
        score += 1.5
        signals.append(f"Stochastic sobrevendido")
    elif current_stoch_k > 80 and current_stoch_d > 80:
        score -= 1.5
        signals.append(f"Stochastic sobrecomprado")

    # MACD
    if current_macd > val(signal) and current_hist > 0:
        score += 1.5
        signals.append(f"MACD alcista")
    elif current_macd < val(signal) and current_hist < 0:
        score -= 1.5
        signals.append(f"MACD bajista")

    # Bollinger
    if current_bb_percent < 0.1:
        score += 1
        signals.append(f"Banda inferior")
    elif current_bb_percent > 0.9:
        score -= 1
        signals.append(f"Banda superior")

    # ADX
    if current_adx > 25:
        if current_plus_di > current_minus_di:
            score += 1.5
            signals.append(f"Tendencia alcista (ADX:{current_adx:.1f})")
        else:
            score -= 1.5
            signals.append(f"Tendencia bajista (ADX:{current_adx:.1f})")

    # Momentum
    if current_momentum > 5:
        score += 1
        signals.append(f"Momentum positivo")
    elif current_momentum < -5:
        score -= 1
        signals.append(f"Momentum negativo")

    # Williams %R
    if current_williams < -80:
        score += 1
        signals.append(f"Williams %R sobrevendido")
    elif current_williams > -20:
        score -= 1
        signals.append(f"Williams %R sobrecomprado")

    # CCI
    if current_cci < -100:
        score += 1
        signals.append(f"CCI sobrevendido")
    elif current_cci > 100:
        score -= 1
        signals.append(f"CCI sobrecomprado")

    rec = "COMPRAR" if score >= 4 else ("VENDER" if score <= -3 else "MANTENER")

    return {
        "ticker": ticker,
        "precio": round(current_price, 2),
        "rsi": round(current_rsi, 1),
        "stoch": round(current_stoch_k, 1),
        "macd": round(current_macd, 2),
        "hist": round(current_hist, 2),
        "adx": round(current_adx, 1),
        "momentum": round(current_momentum, 1),
        "score": round(score, 1),
        "recommendation": rec,
        "signals": signals,
    }


def analyze_market(tickers, nombre):
    """Analiza todos los tickers de un mercado"""
    print(f"\n{'=' * 60}")
    print(f"  ANALISIS {nombre}")
    print(f"{'=' * 60}")

    resultados = []
    for ticker in tickers:
        print(f"  Analizando {ticker}...", end=" ")
        result = analyze_quant(ticker, CONFIG)
        if result:
            print(f"[OK] RSI:{result['rsi']} Score:{result['score']}")
            resultados.append(result)
        else:
            print(f"[X] Error")

    resultados.sort(key=lambda x: x["score"], reverse=True)

    print(f"\n{nombre} - TOP COMPRAR:")
    for r in [x for x in resultados if x["recommendation"] == "COMPRAR"][:3]:
        print(
            f"  {r['ticker']}: ${r['precio']} | Score: +{r['score']} | RSI: {r['rsi']}"
        )

    print(f"\n{nombre} - TOP VENDER:")
    for r in [x for x in resultados if x["recommendation"] == "VENDER"][:3]:
        print(
            f"  {r['ticker']}: ${r['precio']} | Score: {r['score']} | RSI: {r['rsi']}"
        )

    return resultados


def main():
    print("\n" + "=" * 60)
    print("  QUANT TRADING AGENT - ANALISIS COMPLETO")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Tech Stocks
    analyze_market(CONFIG["tickers"], "TECH STOCKS")

    # Bitcoin Miners
    analyze_market(CONFIG["bitcoin_miners"], "BITCOIN MINERS")

    # ETFs
    analyze_market(CONFIG["etfs"], "ETFs")

    # Commodities
    analyze_market(CONFIG["metals"], "COMMODITIES")

    print("\n" + "=" * 60)
    print("  ANALISIS COMPLETADO")
    print("=" * 60)


if __name__ == "__main__":
    main()
