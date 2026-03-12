import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import config
from datetime import datetime

st.set_page_config(
    page_title="Agente Trading NYSE",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================
# FUNCIONES DE ANALISIS TECNICO
# ============================================


def calculate_rsi(prices, period=14):
    """Calcula el Indice de Fuerza Relativa"""
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_sma(prices, period):
    """Calcula Media Movil Simple"""
    return prices.rolling(window=period).mean()


def calculate_ema(prices, period):
    """Calcula Media Movil Exponencial"""
    return prices.ewm(span=period, adjust=False).mean()


def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calcula MACD"""
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    macd = ema_fast - ema_slow
    signal_line = calculate_ema(macd, signal)
    return macd, signal_line


def get_stock_data(ticker, period="6mo", interval="1d"):
    """Descarga datos de Yahoo Finance"""
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        if isinstance(data.columns, pd.MultiIndex):
            data = data.xs(ticker, level=1, axis=1)
        return data
    except Exception:
        return pd.DataFrame()


def analyze_single_stock(ticker, cfg):
    """Analiza un solo activo"""
    data = get_stock_data(ticker, cfg["period"], cfg["interval"])
    if len(data) == 0:
        return None

    close = data["Close"]

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


def calculate_score(result):
    """Calcula score y recomendacion"""
    score = 0
    signals = []

    # RSI
    if result["rsi"] < 30:
        score += 2
        signals.append("RSI sobrevendido")
    elif result["rsi"] > 70:
        score -= 2
        signals.append("RSI sobrecomprado")

    # Tendencia SMA
    if result["precio"] > result["sma_short"] > result["sma_long"]:
        score += 2
        signals.append("Tendencia alcista")
    elif result["precio"] < result["sma_short"] < result["sma_long"]:
        score -= 2
        signals.append("Tendencia bajista")

    # MACD
    if result["macd"] > result["signal"]:
        score += 1
        signals.append("MACD alcista")
    else:
        score -= 1
        signals.append("MACD bajista")

    rec = "COMPRAR" if score >= 3 else ("VENDER" if score <= -2 else "MANTENER")

    return score, signals, rec


def analyze_market(tickers, cfg):
    """Analiza todos los tickers de una lista"""
    resultados = []
    for ticker in tickers:
        result = analyze_single_stock(ticker, cfg)
        if result:
            score, signals, rec = calculate_score(result)
            resultados.append(
                {
                    "Ticker": result["ticker"],
                    "Nombre": config.TICKER_NAMES.get(
                        result["ticker"], result["ticker"]
                    ),
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
    return resultados


# ============================================
# COMPONENTES DE LA INTERFAZ
# ============================================


def render_metrics(resultados):
    """Muestra metricas de resumen"""
    col1, col2, col3 = st.columns(3)

    with col1:
        comprar = len([r for r in resultados if r["Recomendacion"] == "COMPRAR"])
        st.metric("COMPRAR", comprar, delta="Comprar", delta_color="normal")

    with col2:
        mantener = len([r for r in resultados if r["Recomendacion"] == "MANTENER"])
        st.metric("MANTENER", mantener, delta="Mantener", delta_color="off")

    with col3:
        vender = len([r for r in resultados if r["Recomendacion"] == "VENDER"])
        st.metric("VENDER", vender, delta="Vender", delta_color="inverse")


def render_ranking(resultados, rec_filter):
    """Muestra tabla de ranking"""
    if rec_filter != "Todos":
        resultados = [r for r in resultados if r["Recomendacion"] == rec_filter]

    df_display = pd.DataFrame(
        [
            {
                "Ticker": r["Ticker"],
                "Nombre": r["Nombre"],
                "Precio": f"${r['Precio']:.2f}",
                "RSI": f"{r['RSI']:.1f}",
                "MACD": f"{r['MACD']:.2f}",
                "Score": r["Score"],
                "Recomendacion": r["Recomendacion"],
                "Senales": r["Senales"],
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
        },
        hide_index=True,
        use_container_width=True,
        height=300,
    )


def render_chart(ticker_result, period):
    """Grafica analisis tecnico"""
    if ticker_result is None or ticker_result["data"] is None:
        st.warning("No hay datos disponibles")
        return

    data = ticker_result["data"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Precio", f"${ticker_result['precio']:.2f}")
    col2.metric("RSI", f"{ticker_result['rsi']:.1f}")
    col3.metric("MACD", f"{ticker_result['macd']:.2f}")
    col4.metric("Signal", f"{ticker_result['signal']:.2f}")

    close_prices = (
        data["Close"].squeeze()
        if isinstance(data["Close"], pd.DataFrame)
        else data["Close"]
    )

    st.subheader("Precio con Medias Moviles")
    chart_data = pd.DataFrame(
        {
            "Precio": close_prices,
            "SMA20": calculate_sma(close_prices, 20),
            "SMA50": calculate_sma(close_prices, 50),
        }
    )
    st.line_chart(chart_data, height=300)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("RSI")
        rsi_data = calculate_rsi(close_prices)
        st.line_chart(rsi_data, height=200)

    with col2:
        st.subheader("MACD")
        macd, signal = calculate_macd(close_prices)
        macd_data = pd.DataFrame(
            {"MACD": macd, "Signal": signal, "Histograma": macd - signal}
        )
        st.bar_chart(macd_data["Histograma"], height=200)


def render_recommendation(ticker_result):
    """Muestra recomendacion final"""
    score, signals, rec = calculate_score(ticker_result)

    st.subheader("Recomendacion")

    if rec == "COMPRAR":
        st.success(f"**{rec}** (Score: {score})")
    elif rec == "VENDER":
        st.error(f"**{rec}** (Score: {score})")
    else:
        st.warning(f"**{rec}** (Score: {score})")

    st.write("**Senales detectadas:**")
    for s in signals:
        st.write(f"- {s}")


def render_market_tab(
    tab_name, tickers, session_key, rec_key, ticker_key, period_key, info_text
):
    """Renderiza una pestaña de mercado"""

    col1, col2 = st.columns([3, 1])

    with col1:
        rec_filter = st.selectbox(
            f"Filtrar por {rec_key}",
            ["Todos", "COMPRAR", "MANTENER", "VENDER"],
            key=f"rec_{session_key}",
        )

    with col2:
        period = st.selectbox(
            "Periodo", ["1mo", "3mo", "6mo", "1y"], index=2, key=f"period_{session_key}"
        )

    st.markdown("---")

    if st.session_state.get(f"resultados_{session_key}") is None:
        with st.spinner(f"Analizando {tab_name}..."):
            st.session_state[f"resultados_{session_key}"] = analyze_market(
                tickers, config.CONFIG
            )

    resultados = st.session_state[f"resultados_{session_key}"]

    render_metrics(resultados)

    st.subheader(f"Ranking {tab_name}")
    render_ranking(resultados, rec_filter)

    st.markdown("---")

    selected_ticker = st.selectbox(
        f"Seleccionar {ticker_key}", tickers, key=f"ticker_{session_key}"
    )

    ticker_result = analyze_single_stock(
        selected_ticker, {**config.CONFIG, "period": period}
    )

    render_chart(ticker_result, period)
    render_recommendation(ticker_result)


# ============================================
# APLICACION PRINCIPAL
# ============================================


def main():
    st.title("📈 Agente Trading NYSE")
    st.markdown("Analisis tecnico automatico de acciones, ETFs y commodities")

    # Sidebar
    with st.sidebar:
        st.header("Configuracion")

        analyze_btn = st.button(
            "Actualizar Analisis", type="primary", use_container_width=True
        )

        if analyze_btn:
            st.session_state.resultados_tech = None
            st.session_state.resultados_btc = None
            st.session_state.resultados_etf = None
            st.session_state.resultados_metals = None
            st.rerun()

        st.markdown("---")
        st.caption(f"Actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Pestanas
    tab1, tab2, tab3, tab4 = st.tabs(
        ["💻 Tech Stocks", "₿ Bitcoin Miners", "📊 ETFs", "🥇 Commodities"]
    )

    with tab1:
        render_market_tab(
            "Tech Stocks",
            config.CONFIG["tickers"],
            "tech",
            "rec",
            "accion",
            "period",
            "Empresas tecnologicas y blue chips",
        )

    with tab2:
        render_market_tab(
            "Bitcoin Miners",
            config.CONFIG["bitcoin_miners"],
            "btc",
            "rec",
            "accion",
            "period",
            "Empresas de mineria de Bitcoin",
        )

    with tab3:
        render_market_tab(
            "ETFs",
            config.CONFIG["etfs"],
            "etf",
            "rec",
            "ETF",
            "period",
            "Fondos cotizados",
        )

    with tab4:
        render_market_tab(
            "Commodities",
            config.CONFIG["metals"],
            "metals",
            "rec",
            "commodity",
            "period",
            "Metales, energeticos y agricoles",
        )


if __name__ == "__main__":
    main()
