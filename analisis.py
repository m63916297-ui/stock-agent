import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_sma(prices, period):
    return prices.rolling(window=period).mean()


def calculate_ema(prices, period):
    return prices.ewm(span=period, adjust=False).mean()


def calculate_macd(prices, fast=12, slow=26, signal=9):
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    macd = ema_fast - ema_slow
    signal_line = calculate_ema(macd, signal)
    histogram = macd - signal_line
    return macd, signal_line, histogram


def calculate_volatility(prices, period=20):
    returns = prices.pct_change()
    return returns.rolling(window=period).std() * np.sqrt(252)


def calculate_momentum(prices, period=10):
    return prices.diff(period)


def predict_trend(prices, days=5):
    prices_array = prices.values[-30:].reshape(-1, 1)
    X = np.arange(len(prices_array)).reshape(-1, 1)
    model = LinearRegression()
    model.fit(X, prices_array)
    future = np.arange(len(prices_array), len(prices_array) + days).reshape(-1, 1)
    prediction = model.predict(future)
    return prediction[-1][0], model.coef_[0][0]


def analyze_stock(ticker_data, config):
    close = ticker_data["Close"]
    volume = ticker_data["Volume"]

    rsi = calculate_rsi(close)
    sma_short = calculate_sma(close, config["sma_short"])
    sma_long = calculate_sma(close, config["sma_long"])
    macd, signal_line, histogram = calculate_macd(close)
    volatility = calculate_volatility(close)
    momentum = calculate_momentum(close)
    prediction, slope = predict_trend(close)

    current_price = float(close.iloc[-1])
    current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
    current_macd = float(macd.iloc[-1]) if not pd.isna(macd.iloc[-1]) else 0.0
    current_signal = (
        float(signal_line.iloc[-1]) if not pd.isna(signal_line.iloc[-1]) else 0.0
    )
    sma_short_val = (
        float(sma_short.iloc[-1]) if not pd.isna(sma_short.iloc[-1]) else current_price
    )
    sma_long_val = (
        float(sma_long.iloc[-1]) if not pd.isna(sma_long.iloc[-1]) else current_price
    )
    volatility_val = (
        float(volatility.iloc[-1]) if not pd.isna(volatility.iloc[-1]) else 0.0
    )
    avg_volume = float(volume.tail(20).mean())

    score = 0
    signals = []

    if current_rsi < config["rsi_oversold"]:
        score += 2
        signals.append("RSI sobrevendido (posible compra)")
    elif current_rsi > config["rsi_overbought"]:
        score -= 2
        signals.append("RSI sobrecomprado (posible venta)")

    if current_price > sma_short_val > sma_long_val:
        score += 2
        signals.append("Precio arriba de SMA corto y largo (tendencia alcista)")
    elif current_price < sma_short_val < sma_long_val:
        score -= 2
        signals.append("Precio abajo de SMA corto y largo (tendencia bajista)")

    if current_macd > current_signal:
        score += 1
        signals.append("MACD cruza arriba de signal (alcista)")
    elif current_macd < current_signal:
        score -= 1
        signals.append("MACD cruza abajo de signal (bajista)")

    if slope > 0:
        score += 1
        signals.append("Tendencia positiva detectada")
    else:
        score -= 1
        signals.append("Tendencia negativa detectada")

    if avg_volume < config["min_volume"]:
        score -= 1
        signals.append("Bajo volumen")

    recommendation = (
        "COMPRAR" if score >= 3 else ("VENDER" if score <= -2 else "MANTENER")
    )

    return {
        "ticker": ticker_data.name,
        "precio_actual": round(current_price, 2),
        "rsi": round(current_rsi, 2),
        "volatilidad": round(volatility_val * 100, 2),
        "precio_predicho": round(prediction, 2),
        "tendencia": "ALCISTA" if slope > 0 else "BAJISTA",
        "senal": ", ".join(signals) if signals else "Neutral",
        "puntuacion": score,
        "recommendation": recommendation,
        "volume": int(avg_volume),
    }
