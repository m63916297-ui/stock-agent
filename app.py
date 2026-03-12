import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import config
from datetime import datetime

st.set_page_config(
    page_title="Quant Trading Agent",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_stochastic(high, low, close, k_period=14, d_period=3):
    """Stochastic Oscillator %K y %D"""
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()

    stoch_k = 100 * (close - lowest_low) / (highest_high - lowest_low)
    stoch_d = stoch_k.rolling(window=d_period).mean()

    return stoch_k, stoch_d


def calculate_macd(prices, fast=12, slow=26, signal=9):
    """MACD - Moving Average Convergence Divergence"""
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """Bollinger Bands - Media movil con bandas de volatilidad"""
    sma = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    bandwidth = (upper_band - lower_band) / sma
    percent_b = (prices - lower_band) / (upper_band - lower_band)
    return upper_band, sma, lower_band, bandwidth, percent_b


def calculate_atr(high, low, close, period=14):
    """ATR - Average True Range (volatilidad)"""
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / period, adjust=False).mean()
    return atr


def calculate_adx(high, low, close, period=14):
    """ADX - Average Directional Index (fuerza de tendencia)"""
    plus_dm = high.diff()
    minus_dm = -low.diff()

    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0

    tr = calculate_atr(high, low, close, period) * period

    plus_di = 100 * (plus_dm.ewm(alpha=1 / period).mean() / tr)
    minus_di = 100 * (minus_dm.ewm(alpha=1 / period).mean() / tr)

    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.ewm(alpha=1 / period).mean()

    return adx, plus_di, minus_di


def calculate_vwap(high, low, close, volume):
    """VWAP - Volume Weighted Average Price"""
    typical_price = (high + low + close) / 3
    vwap = (typical_price * volume).cumsum() / volume.cumsum()
    return vwap


def calculate_obv(close, volume):
    """OBV - On Balance Volume"""
    obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
    return obv


def calculate_momentum(prices, period=10):
    """Momentum - Rate of Change"""
    return prices.pct_change(periods=period) * 100


def calculate_cci(high, low, close, period=20):
    """CCI - Commodity Channel Index"""
    tp = (high + low + close) / 3
    sma_tp = tp.rolling(window=period).mean()
    mad = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
    cci = (tp - sma_tp) / (0.015 * mad)
    return cci


def calculate_williams_r(high, low, close, period=14):
    """Williams %R"""
    highest_high = high.rolling(window=period).max()
    lowest_low = low.rolling(window=period).min()
    williams_r = -100 * (highest_high - close) / (highest_high - lowest_low)
    return williams_r


def calculate_ichimoku(
    high, low, close, conversion=9, base=26, span_b=52, displacement=26
):
    """Ichimoku Cloud (simplified)"""
    conversion_line = (
        high.rolling(window=conversion).max() + low.rolling(window=conversion).min()
    ) / 2
    base_line = (high.rolling(window=base).max() + low.rolling(window=base).min()) / 2
    span_a = ((conversion_line + base_line) / 2).shift(displacement)
    span_b = (
        (high.rolling(window=span_b).max() + low.rolling(window=span_b).min()) / 2
    ).shift(displacement)
    return conversion_line, base_line, span_a, span_b


def calculate_support_resistance(prices, window=20):
    """Soporte y Resistencia usando pivot points"""
    highs = prices.rolling(window=window).max()
    lows = prices.rolling(window=window).min()
    return highs, lows


# ============================================
# FUNCIONES AUXILIARES
# ============================================


def get_stock_data(ticker, period="6mo", interval="1d"):
    """Descarga datos de Yahoo Finance"""
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        if isinstance(data.columns, pd.MultiIndex):
            data = data.xs(ticker, level=1, axis=1)
        return data
    except Exception:
        return pd.DataFrame()


def analyze_quant(ticker, cfg):
    """Analisis completo con indicadores quant"""
    data = get_stock_data(ticker, cfg["period"], cfg["interval"])

    if len(data) == 0:
        return None

    close = data["Close"]
    high = data["High"]
    low = data["Low"]
    volume = data["Volume"]

    # Calcular todos los indicadores
    rsi = calculate_rsi(close)
    stoch_k, stoch_d = calculate_stochastic(high, low, close)
    macd, signal, hist = calculate_macd(close)
    bb_upper, bb_middle, bb_lower, bb_width, bb_percent = calculate_bollinger_bands(
        close
    )
    atr = calculate_atr(high, low, close)
    adx, plus_di, minus_di = calculate_adx(high, low, close)
    vwap = calculate_vwap(high, low, close, volume)
    momentum = calculate_momentum(close)
    cci = calculate_cci(high, low, close)
    williams = calculate_williams_r(high, low, close)

    # Valores actuales
    current_price = float(close.iloc[-1])
    current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
    current_stoch_k = float(stoch_k.iloc[-1]) if not pd.isna(stoch_k.iloc[-1]) else 50.0
    current_stoch_d = float(stoch_d.iloc[-1]) if not pd.isna(stoch_d.iloc[-1]) else 50.0
    current_macd = float(macd.iloc[-1]) if not pd.isna(macd.iloc[-1]) else 0.0
    current_signal = float(signal.iloc[-1]) if not pd.isna(signal.iloc[-1]) else 0.0
    current_hist = float(hist.iloc[-1]) if not pd.isna(hist.iloc[-1]) else 0.0
    current_bb_upper = (
        float(bb_upper.iloc[-1]) if not pd.isna(bb_upper.iloc[-1]) else current_price
    )
    current_bb_lower = (
        float(bb_lower.iloc[-1]) if not pd.isna(bb_lower.iloc[-1]) else current_price
    )
    current_bb_percent = (
        float(bb_percent.iloc[-1]) if not pd.isna(bb_percent.iloc[-1]) else 0.5
    )
    current_atr = float(atr.iloc[-1]) if not pd.isna(atr.iloc[-1]) else 0.0
    current_adx = float(adx.iloc[-1]) if not pd.isna(adx.iloc[-1]) else 0.0
    current_plus_di = float(plus_di.iloc[-1]) if not pd.isna(plus_di.iloc[-1]) else 0.0
    current_minus_di = (
        float(minus_di.iloc[-1]) if not pd.isna(minus_di.iloc[-1]) else 0.0
    )
    current_momentum = (
        float(momentum.iloc[-1]) if not pd.isna(momentum.iloc[-1]) else 0.0
    )
    current_cci = float(cci.iloc[-1]) if not pd.isna(cci.iloc[-1]) else 0.0
    current_williams = (
        float(williams.iloc[-1]) if not pd.isna(williams.iloc[-1]) else -50.0
    )

    # Calificacion quant (score ponderado)
    score = 0
    signals = []

    # RSI (peso: 2)
    if current_rsi < 30:
        score += 2
        signals.append(f"RSI sobrevendido ({current_rsi:.1f})")
    elif current_rsi > 70:
        score -= 2
        signals.append(f"RSI sobrecomprado ({current_rsi:.1f})")

    # Stochastic (peso: 1.5)
    if current_stoch_k < 20 and current_stoch_d < 20:
        score += 1.5
        signals.append(
            f"Stochastic sobrevendido (K:{current_stoch_k:.1f}, D:{current_stoch_d:.1f})"
        )
    elif current_stoch_k > 80 and current_stoch_d > 80:
        score -= 1.5
        signals.append(
            f"Stochastic sobrecomprado (K:{current_stoch_k:.1f}, D:{current_stoch_d:.1f})"
        )

    # MACD (peso: 1.5)
    if current_macd > current_signal and current_hist > 0:
        score += 1.5
        signals.append(f"MACD alcista (hist: {current_hist:.2f})")
    elif current_macd < current_signal and current_hist < 0:
        score -= 1.5
        signals.append(f"MACD bajista (hist: {current_hist:.2f})")

    # Bollinger Bands (peso: 1)
    if current_bb_percent < 0.1:
        score += 1
        signals.append(f"Precio en banda inferior ({current_bb_percent:.2f})")
    elif current_bb_percent > 0.9:
        score -= 1
        signals.append(f"Precio en banda superior ({current_bb_percent:.2f})")

    # ADX - Fuerza de tendencia (peso: 1.5)
    if current_adx > 25:
        if current_plus_di > current_minus_di:
            score += 1.5
            signals.append(f"Tendencia alcista fuerte (ADX:{current_adx:.1f})")
        else:
            score -= 1.5
            signals.append(f"Tendencia bajista fuerte (ADX:{current_adx:.1f})")

    # Momentum (peso: 1)
    if current_momentum > 5:
        score += 1
        signals.append(f"Momentum positivo ({current_momentum:.1f}%)")
    elif current_momentum < -5:
        score -= 1
        signals.append(f"Momentum negativo ({current_momentum:.1f}%)")

    # Williams %R (peso: 1)
    if current_williams < -80:
        score += 1
        signals.append(f"Williams %R sobrevendido ({current_williams:.1f})")
    elif current_williams > -20:
        score -= 1
        signals.append(f"Williams %R sobrecomprado ({current_williams:.1f})")

    # CCI (peso: 1)
    if current_cci < -100:
        score += 1
        signals.append(f"CCI sobrevendido ({current_cci:.1f})")
    elif current_cci > 100:
        score -= 1
        signals.append(f"CCI sobrecomprado ({current_cci:.1f})")

    # Recomendacion
    rec = "COMPRAR" if score >= 4 else ("VENDER" if score <= -3 else "MANTENER")

    return {
        "ticker": ticker,
        "nombre": config.TICKER_NAMES.get(ticker, ticker),
        "precio": current_price,
        "rsi": current_rsi,
        "stoch_k": current_stoch_k,
        "stoch_d": current_stoch_d,
        "macd": current_macd,
        "signal": current_signal,
        "hist": current_hist,
        "bb_upper": current_bb_upper,
        "bb_lower": current_bb_lower,
        "bb_percent": current_bb_percent,
        "atr": current_atr,
        "adx": current_adx,
        "plus_di": current_plus_di,
        "minus_di": current_minus_di,
        "momentum": current_momentum,
        "cci": current_cci,
        "williams": current_williams,
        "score": round(score, 1),
        "recommendation": rec,
        "signals": signals,
        "data": data,
    }


def analyze_market(tickers, cfg):
    """Analiza todos los tickers"""
    resultados = []
    for ticker in tickers:
        result = analyze_quant(ticker, cfg)
        if result:
            resultados.append(result)

    resultados.sort(key=lambda x: x["score"], reverse=True)
    return resultados


# ============================================
# COMPONENTES DE LA INTERFAZ
# ============================================


def render_metrics(resultados):
    """Muestra metricas de resumen"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        comprar = len([r for r in resultados if r["recommendation"] == "COMPRAR"])
        st.metric("COMPRAR", comprar, delta="Comprar", delta_color="normal")

    with col2:
        mantener = len([r for r in resultados if r["recommendation"] == "MANTENER"])
        st.metric("MANTENER", mantener, delta="Mantener", delta_color="off")

    with col3:
        vender = len([r for r in resultados if r["recommendation"] == "VENDER"])
        st.metric("VENDER", vender, delta="Vender", delta_color="inverse")

    with col4:
        score_avg = np.mean([r["score"] for r in resultados])
        st.metric("Score Promedio", f"{score_avg:.1f}")


def render_ranking(resultados, rec_filter):
    """Muestra tabla de ranking"""
    if rec_filter != "Todos":
        resultados = [r for r in resultados if r["recommendation"] == rec_filter]

    df_display = pd.DataFrame(
        [
            {
                "Ticker": r["ticker"],
                "Nombre": r["nombre"],
                "Precio": f"${r['precio']:.2f}",
                "RSI": f"{r['rsi']:.0f}",
                "Stoch": f"{r['stoch_k']:.0f}",
                "MACD": f"{r['macd']:.2f}",
                "ADX": f"{r['adx']:.1f}",
                "Mom": f"{r['momentum']:.1f}%",
                "Score": r["score"],
                "Rec": r["recommendation"],
            }
            for r in resultados
        ]
    )

    st.dataframe(
        df_display,
        column_config={
            "RSI": st.column_config.ProgressColumn("RSI", min_value=0, max_value=100),
            "Stoch": st.column_config.ProgressColumn(
                "Stoch %K", min_value=0, max_value=100
            ),
            "Score": st.column_config.ProgressColumn(
                "Score", min_value=-10, max_value=10
            ),
        },
        hide_index=True,
        use_container_width=True,
        height=300,
    )


def render_chart(result, period):
    """Grafica analisis tecnico avanzado"""
    if result is None or result["data"] is None:
        st.warning("No hay datos disponibles")
        return

    data = result["data"]
    close = (
        data["Close"].squeeze()
        if isinstance(data["Close"], pd.DataFrame)
        else data["Close"]
    )
    high = (
        data["High"].squeeze()
        if isinstance(data["High"], pd.DataFrame)
        else data["High"]
    )
    low = (
        data["Low"].squeeze() if isinstance(data["Low"], pd.DataFrame) else data["Low"]
    )
    volume = (
        data["Volume"].squeeze()
        if isinstance(data["Volume"], pd.DataFrame)
        else data["Volume"]
    )

    # Metricas principales
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Precio", f"${result['precio']:.2f}")
    col2.metric("RSI (14)", f"{result['rsi']:.0f}")
    col3.metric("Stoch %K", f"{result['stoch_k']:.0f}")
    col4.metric("MACD", f"{result['macd']:.2f}")
    col5.metric("ADX", f"{result['adx']:.1f}")
    col6.metric("ATR", f"{result['atr']:.2f}")

    # Grafico de precio con BB
    st.subheader("Precio con Bollinger Bands")
    bb_upper, bb_middle, bb_lower, _, _ = calculate_bollinger_bands(close)
    chart_data = pd.DataFrame(
        {
            "Precio": close,
            "BB Upper": bb_upper,
            "BB Middle": bb_middle,
            "BB Lower": bb_lower,
        }
    )
    st.line_chart(chart_data, height=300)

    # RSI y Stochastic
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("RSI (14)")
        rsi_data = calculate_rsi(close)
        st.line_chart(rsi_data, height=200)

    with col2:
        st.subheader("Stochastic %K / %D")
        stoch_k, stoch_d = calculate_stochastic(high, low, close)
        stoch_data = pd.DataFrame(
            {"%K": stoch_k, "%D": stoch_d, "Overbought": 80, "Oversold": 20}
        )
        st.line_chart(stoch_data, height=200)

    # MACD
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("MACD (12,26,9)")
        macd, signal, hist = calculate_macd(close)
        macd_data = pd.DataFrame({"MACD": macd, "Signal": signal, "Histograma": hist})
        st.bar_chart(macd_data["Histograma"], height=200)

    with col2:
        st.subheader("Momentum (%)")
        momentum = calculate_momentum(close)
        st.line_chart(momentum, height=200)

    # ADX
    st.subheader("ADX - Fuerza de Tendencia")
    adx, plus_di, minus_di = calculate_adx(high, low, close)
    adx_data = pd.DataFrame({"ADX": adx, "+DI": plus_di, "-DI": minus_di})
    st.line_chart(adx_data, height=200)


def render_recommendation(result):
    """Muestra recomendacion con senales"""
    rec = result["recommendation"]
    score = result["score"]

    st.subheader("Recomendacion del Quant")

    if rec == "COMPRAR":
        st.success(f"**{rec}** | Score: {score}")
    elif rec == "VENDER":
        st.error(f"**{rec}** | Score: {score}")
    else:
        st.warning(f"**{rec}** | Score: {score}")

    st.write("**Senales cuantitativas:**")
    for s in result["signals"]:
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

    result = analyze_quant(selected_ticker, {**config.CONFIG, "period": period})

    render_chart(result, period)
    render_recommendation(result)


# ============================================
# APLICACION PRINCIPAL
# ============================================


def main():
    st.title("Quant Trading Agent")
    st.markdown("Analisis cuantitativo profesional con multiples indicadores tecnicos")

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
        ["Tech Stocks", "Bitcoin Miners", "ETFs", "Commodities"]
    )

    with tab1:
        render_market_tab(
            "Tech Stocks",
            config.CONFIG["tickers"],
            "tech",
            "rec",
            "accion",
            "period",
            "Empresas tecnologicas",
        )

    with tab2:
        render_market_tab(
            "Bitcoin Miners",
            config.CONFIG["bitcoin_miners"],
            "btc",
            "rec",
            "accion",
            "period",
            "Empresas mineria Bitcoin",
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
            "Metales y commodities",
        )


if __name__ == "__main__":
    main()
