import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime
import config

CONFIG = config.CONFIG


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
    return macd, signal_line, macd - signal_line


def calculate_volatility(prices, period=20):
    returns = prices.pct_change()
    return returns.rolling(window=period).std() * np.sqrt(252)


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


class AgenteStock:
    def __init__(self):
        self.config = CONFIG
        self.resultados = []

    def obtener_datos(self, tickers):
        print(f"Descargando datos de {len(tickers)} tickers...")
        datos = {}
        for ticker in tickers:
            try:
                data = yf.download(
                    ticker,
                    period=self.config["period"],
                    interval=self.config["interval"],
                    progress=False,
                )
                if len(data) > 0:
                    if isinstance(data.columns, pd.MultiIndex):
                        data = data.xs(ticker, level=1, axis=1)
                    data.index = pd.to_datetime(data.index)
                    data["ticker"] = ticker
                    datos[ticker] = data
                    print(f"  [OK] {ticker}: {len(data)} datos")
                else:
                    print(f"  [--] {ticker}: Sin datos")
            except Exception as e:
                print(f"  [X] {ticker}: Error - {e}")
        return datos

    def analizar_mercado(self, tickers):
        datos = self.obtener_datos(tickers)

        print("\nAnalizando stocks...")
        resultados = []
        for ticker, data in datos.items():
            data.name = ticker
            resultado = analyze_stock(data, self.config)
            resultados.append(resultado)

        resultados.sort(key=lambda x: x["puntuacion"], reverse=True)
        self.resultados = resultados
        return resultados

    def generar_reporte(self, tickers, nombre_mercado="Mercado"):
        resultados = self.analizar_mercado(tickers)

        print("\n" + "=" * 60)
        print(f"     REPORTE DE ANALISIS - {nombre_mercado}")
        print("=" * 60)
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        print("\n[*] TOP COMPRAR:")
        comprar = [r for r in resultados if r["recommendation"] == "COMPRAR"][:5]
        for i, r in enumerate(comprar, 1):
            print(
                f"  {i}. {r['ticker']} - ${r['precio_actual']} | RSI: {r['rsi']} | Score: +{r['puntuacion']}"
            )
            print(f"     Senal: {r['senal']}")

        print("\n[*] TOP VENDER:")
        vender = [r for r in resultados if r["recommendation"] == "VENDER"][:5]
        for i, r in enumerate(vender, 1):
            print(
                f"  {i}. {r['ticker']} - ${r['precio_actual']} | RSI: {r['rsi']} | Score: {r['puntuacion']}"
            )
            print(f"     Senal: {r['senal']}")

        print("\n[*] RANKING GENERAL:")
        for i, r in enumerate(resultados[: self.config["top_n"]], 1):
            rec = r["recommendation"]
            print(
                f"  {i}. {r['ticker']}: ${r['precio_actual']} | {rec} | Tendencia: {r['tendencia']}"
            )

        print("\n" + "=" * 60)
        return resultados


def main():
    agente = AgenteStock()

    print("\n" + "=" * 60)
    print("     AGENTE DE TRADING NYSE - ANALISIS COMPLETO")
    print("=" * 60)

    # Tech Stocks
    print("\n\n>>> ANALIZANDO TECH STOCKS...")
    agente.generar_reporte(CONFIG["tickers"], "TECH STOCKS")

    # Bitcoin Miners
    print("\n\n>>> ANALIZANDO BITCOIN MINERS...")
    agente.generar_reporte(CONFIG["bitcoin_miners"], "BITCOIN MINERS")

    # ETFs
    print("\n\n>>> ANALIZANDO ETFs...")
    agente.generar_reporte(CONFIG["etfs"], "ETFs")

    # Commodities
    print("\n\n>>> ANALIZANDO COMMODITIES...")
    agente.generar_reporte(CONFIG["metals"], "COMMODITIES")

    print("\n\nAnalisis completado!")


if __name__ == "__main__":
    main()
