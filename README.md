# Agente Autónomo de Trading - NYSE

Agente IA que analiza automáticamente stocks de la NYSE y genera recomendaciones de compra/venta basadas en análisis técnico.

## Características

- **Análisis Técnico**: RSI, MACD, SMA, EMA, Volatilidad, Momentum
- **Predicción de Tendencia**: Regresión lineal para predecir dirección del precio
- **Recomendaciones**: COMPRAR / MANTENER / VENDER
- **Ranking automático**: Ordena los mejores oportunidades de inversión
- **Interfaz Streamlit**: Visualización interactiva de resultados

## Instalación

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
venv\Scripts\activate.bat

# Instalar dependencias
pip install -r requirements.txt
```

## Uso

### Interfaz Gráfica (Streamlit)
```bash
streamlit run app.py
```

### Línea de Comandos
```bash
python stock_agent.py
```

## Estructura de Archivos

```
genai/
├── app.py              # Interfaz Streamlit
├── stock_agent.py      # Agente principal
├── analisis.py         # Módulo de análisis técnico
├── config.py          # Configuración
├── requirements.txt   # Dependencias
└── README.md          # Este archivo
```

## Indicadores Técnicos

| Indicador | Descripción |
|-----------|-------------|
| RSI | Índice de Fuerza Relativa (sobrevendido <30, sobrecomprado >70) |
| MACD | Convergencia/Divergencia de Medias Móviles |
| SMA | Media Móvil Simple |
| EMA | Media Móvil Exponencial |
| Volatilidad | Desviación estándar anualizada |
| Momentum | Diferencia de precio en período |

## Recomendaciones

- **COMPRAR**: Score >= 3 (múltiples indicadores alcistas)
- **VENDER**: Score <= -2 (múltiples indicadores bajistas)
- **MANTENER**: Resto de casos

## Configuración

Editar `config.py` para modificar:
- Lista de tickers a analizar
- Período de datos (default: 6 meses)
- Parámetros de indicadores (RSI, SMA, etc.)
- Volumen mínimo

## Disclaimer

Este agente es solo para fines educativos. No constituye asesoramiento financiero.
