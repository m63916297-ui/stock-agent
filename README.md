# Agente Autónomo de Trading - NYSE

Agente IA que analiza automáticamente acciones de la NYSE y genera recomendaciones de compra/venta basadas en análisis técnico.

## Características

- **Análisis Técnico**: RSI, MACD, SMA, EMA
- **Predicción de Tendencia**: Regresión lineal
- **Dos Mercados**: Tech Stocks y Bitcoin Miners
- **Recomendaciones**: COMPRAR / MANTENER / VENDER
- **Ranking automático**: Ordena mejores oportunidades
- **Interfaz Streamlit**: Visualización interactiva

## Instalación

```bash
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

## Uso

```bash
streamlit run app.py
```

## Estructura

```
genai/
├── app.py              # Interfaz Streamlit
├── stock_agent.py      # Agente CLI
├── analisis.py         # Módulo de análisis técnico
├── config.py          # Configuración
├── requirements.txt   # Dependencias
└── README.md          # Este archivo
```

## Mercados

### 💻 Tech Stocks (28 empresas)
AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA, JPM, JNJ, V, PG, UNH, HD, MA, DIS, PYPL, NFLX, ADBE, CRM, INTC, VZ, T, PFE, MRK, KO, PEP, WMT, BRK-B

### ₿ Bitcoin Miners (15 empresas)
MARA, RIOT, CLSK, BTDR, HIVE, BITF, DMGI, SFIL, WULF, BBOX, ARBK, LFG, CGX, BRCC, BITN

## Indicadores

| Indicador | Descripción |
|-----------|-------------|
| RSI | Índice de Fuerza Relativa (<30 sobrevendido, >70 sobrecomprado) |
| MACD | Convergencia/Divergencia de Medias Móviles |
| SMA | Media Móvil Simple |
| EMA | Media Móvil Exponencial |

## Recomendaciones

- **COMPRAR**: Score >= 3
- **VENDER**: Score <= -2
- **MANTENER**: Resto

## Disclaimer

Solo para fines educativos. No constituye asesoramiento financiero.
