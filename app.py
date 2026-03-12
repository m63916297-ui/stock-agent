import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import config
import analisis
from datetime import datetime

st.set_page_config(page_title="Agente Trading NYSE", page_icon="📈", layout="wide")

if "resultados" not in st.session_state:
    st.session_state.resultados = None
if "tickers" not in st.session_state:
    st.session_state.tickers = config.CONFIG["tickers"]


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
    return macd, signal_line


def get_stock_data(ticker, period="6mo", interval="1d"):
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        if isinstance(data.columns, pd.MultiIndex):
            data = data.xs(ticker, level=1, axis=1)
        return data
    except:
        return pd.DataFrame()


def analyze_single_stock(ticker, cfg):
    data = get_stock_data(ticker, cfg["period"], cfg["interval"])
    if len(data) == 0:
        return None

    close = data["Close"]
    volume = data["Volume"]

    rsi = calculate_rsi(close)
    sma_short = calculate_sma(close, cfg["sma_short"])
    sma_long = calculate_sma(close, cfg["sma_long"])
    macd, signal_line = calculate_macd(close)

    current_price = float(close.iloc[-1])
    current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
    current_macd = float(macd.iloc[-1]) if not pd.isna(macd.iloc[-1]) else 0.0
    current_signal = (
        float(signal_line.iloc[-1]) if not pd.isna(signal_line.iloc[-1]) else 0.0
    )

    return {
        "ticker": ticker,
        "precio": current_price,
        "rsi": current_rsi,
        "macd": current_macd,
        "signal": current_signal,
        "sma_short": float(sma_short.iloc[-1])
        if not pd.isna(sma_short.iloc[-1])
        else current_price,
        "sma_long": float(sma_long.iloc[-1])
        if not pd.isna(sma_long.iloc[-1])
        else current_price,
        "data": data,
    }


def main():
    st.title("📈 Agente Autónomo de Trading NYSE")
    st.markdown("Análisis técnico automático de acciones de la NYSE")

    with st.sidebar:
        st.header("Configuración")

        st.subheader("Análisis")
        analyze_btn = st.button(
            "🔄 Analizar Mercado", type="primary", use_container_width=True
        )

        st.subheader("Filtros")
        rec_filter = st.selectbox(
            "Filtrar por recomendación", ["Todos", "COMPRAR", "MANTENER", "VENDER"]
        )

        st.subheader("Ticker Individual")
        selected_ticker = st.selectbox("Seleccionar acción", st.session_state.tickers)

        st.subheader("Período")
        period = st.selectbox("Período de datos", ["1mo", "3mo", "6mo", "1y"], index=2)

        st.markdown("---")
        st.caption("Actualizado: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    if analyze_btn or st.session_state.resultados is None:
        with st.spinner("Analizando mercado..."):
            resultados = []
            for ticker in st.session_state.tickers:
                result = analyze_single_stock(ticker, config.CONFIG)
                if result:
                    score = 0
                    signals = []

                    if result["rsi"] < 30:
                        score += 2
                        signals.append("RSI sobrevendido")
                    elif result["rsi"] > 70:
                        score -= 2
                        signals.append("RSI sobrecomprado")

                    if result["precio"] > result["sma_short"] > result["sma_long"]:
                        score += 2
                        signals.append("Tendencia alcista")
                    elif result["precio"] < result["sma_short"] < result["sma_long"]:
                        score -= 2
                        signals.append("Tendencia bajista")

                    if result["macd"] > result["signal"]:
                        score += 1
                        signals.append("MACD alcista")
                    else:
                        score -= 1
                        signals.append("MACD bajista")

                    rec = (
                        "COMPRAR"
                        if score >= 3
                        else ("VENDER" if score <= -2 else "MANTENER")
                    )

                    resultados.append(
                        {
                            "Ticker": result["ticker"],
                            "Precio": result["precio"],
                            "RSI": result["rsi"],
                            "MACD": result["macd"],
                            "Signal": result["signal"],
                            "SMA20": result["sma_short"],
                            "SMA50": result["sma_long"],
                            "Score": score,
                            "Recomendacion": rec,
                            "Senales": ", ".join(signals) if signals else "Neutral",
                            "data": result["data"],
                        }
                    )

            resultados.sort(key=lambda x: x["Score"], reverse=True)
            st.session_state.resultados = resultados

    resultados = st.session_state.resultados

    if rec_filter != "Todos":
        resultados = [r for r in resultados if r["Recomendacion"] == rec_filter]

    col1, col2, col3 = st.columns(3)

    with col1:
        comprar = len(
            [r for r in st.session_state.resultados if r["Recomendacion"] == "COMPRAR"]
        )
        st.metric("COMPRAR", comprar, delta="Oportunidades", delta_color="normal")

    with col2:
        mantener = len(
            [r for r in st.session_state.resultados if r["Recomendacion"] == "MANTENER"]
        )
        st.metric("MANTENER", mantener, delta="Neutral", delta_color="off")

    with col3:
        vender = len(
            [r for r in st.session_state.resultados if r["Recomendacion"] == "VENDER"]
        )
        st.metric("VENDER", vender, delta="Riesgo", delta_color="inverse")

    st.subheader("📊 Ranking de Acciones")

    df_display = pd.DataFrame(
        [
            {
                "Ticker": r["Ticker"],
                "Precio": f"${r['Precio']:.2f}",
                "RSI": f"{r['RSI']:.1f}",
                "MACD": f"{r['MACD']:.2f}",
                "Score": r["Score"],
                "Recomendacion": r["Recomendacion"],
                "Señales": r["Senales"],
            }
            for r in resultados
        ]
    )

    st.dataframe(
        df_display,
        column_config={
            "RSI": st.column_config.ProgressColumn(
                "RSI", min_value=0, max_value=100, format="%.1f"
            ),
            "Score": st.column_config.ProgressColumn(
                "Score", min_value=-5, max_value=5
            ),
            "Recomendacion": st.column_config.TextColumn(
                "Recomendación", help="Recomendación del agente"
            ),
        },
        hide_index=True,
        use_container_width=True,
    )

    st.subheader(f"📈 Análisis de {selected_ticker}")

    ticker_result = analyze_single_stock(
        selected_ticker, {**config.CONFIG, "period": period}
    )

    if ticker_result and ticker_result["data"] is not None:
        data = ticker_result["data"]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Precio", f"${ticker_result['precio']:.2f}")
        col2.metric("RSI", f"{ticker_result['rsi']:.1f}")
        col3.metric("MACD", f"{ticker_result['macd']:.2f}")
        col4.metric("Signal", f"{ticker_result['signal']:.2f}")

        st.subheader("Precio con Medias Móviles")

        chart_data = pd.DataFrame(
            {
                "Precio": data["Close"].squeeze()
                if isinstance(data["Close"], pd.DataFrame)
                else data["Close"],
                "SMA20": calculate_sma(
                    data["Close"].squeeze()
                    if isinstance(data["Close"], pd.DataFrame)
                    else data["Close"],
                    20,
                ),
                "SMA50": calculate_sma(
                    data["Close"].squeeze()
                    if isinstance(data["Close"], pd.DataFrame)
                    else data["Close"],
                    50,
                ),
            }
        )
        st.line_chart(chart_data, height=300)

        st.subheader("RSI")
        rsi_data = calculate_rsi(
            data["Close"].squeeze()
            if isinstance(data["Close"], pd.DataFrame)
            else data["Close"]
        )
        st.line_chart(rsi_data, height=200)

        st.subheader("MACD")
        macd, signal = calculate_macd(
            data["Close"].squeeze()
            if isinstance(data["Close"], pd.DataFrame)
            else data["Close"]
        )
        macd_data = pd.DataFrame(
            {"MACD": macd, "Signal": signal, "Histograma": macd - signal}
        )
        st.bar_chart(macd_data["Histograma"], height=200)

        score = 0
        signals = []

        if ticker_result["rsi"] < 30:
            score += 2
            signals.append("RSI sobrevendido - POSIBLE COMPRA")
        elif ticker_result["rsi"] > 70:
            score -= 2
            signals.append("RSI sobrecomprado - POSIBLE VENTA")

        if (
            ticker_result["precio"]
            > ticker_result["sma_short"]
            > ticker_result["sma_long"]
        ):
            score += 2
            signals.append("Precio arriba de SMA20 y SMA50 - TENDENCIA ALCISTA")
        elif (
            ticker_result["precio"]
            < ticker_result["sma_short"]
            < ticker_result["sma_long"]
        ):
            score -= 2
            signals.append("Precio abajo de SMA20 y SMA50 - TENDENCIA BAJISTA")

        if ticker_result["macd"] > ticker_result["signal"]:
            score += 1
            signals.append("MACD cruza arriba de Signal - ALCISTA")
        else:
            score -= 1
            signals.append("MACD cruza abajo de Signal - BAJISTA")

        rec = "COMPRAR" if score >= 3 else ("VENDER" if score <= -2 else "MANTENER")

        st.subheader("🎯 Recomendación")

        if rec == "COMPRAR":
            st.success(f"**{rec}** (Score: {score})")
        elif rec == "VENDER":
            st.error(f"**{rec}** (Score: {score})")
        else:
            st.warning(f"**{rec}** (Score: {score})")

        st.write("**Señales detectadas:**")
        for s in signals:
            st.write(f"- {s}")
    else:
        st.error("No se pudieron obtener datos para este ticker")


if __name__ == "__main__":
    main()
