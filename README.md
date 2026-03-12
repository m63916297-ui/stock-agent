# Agente Autonomous de Trading NYSE

Analisis tecnico automatico de acciones, ETFs, Bitcoin Miners y Commodities.

## Caracteristicas

- Analisis tecnico: RSI, MACD, SMA, EMA
- 4 Mercados: Tech Stocks, Bitcoin Miners, ETFs, Commodities
- Recomendaciones: COMPRAR / MANTENER / VENDER
- Interfaz interactiva Streamlit

## Instalacion

```bash
cd genai
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

## Uso

### Interfaz Grafica (Streamlit)
```bash
streamlit run app.py
```

### Linea de Comandos
```bash
python stock_agent.py
```

## Estructura

```
genai/
├── app.py              # Interfaz Streamlit
├── stock_agent.py      # Agente CLI
├── config.py           # Configuracion y tickers
├── analisis.py         # Modulo analisis (respaldo)
├── requirements.txt    # Dependencias
└── README.md          # Documentacion
```

## Mercados

| Modulo | Activos | Descripcion |
|--------|---------|-------------|
| Tech Stocks | 28 | Empresas tecnologicas y blue chips |
| Bitcoin Miners | 15 | Empresas de mineria de Bitcoin |
| ETFs | 23 | Fondos cotizados (S&P500, sectoriales) |
| Commodities | 29 | Metales, energeticos, agricoles |

## Indicadores

| Indicador | Descripcion |
|-----------|-------------|
| RSI | Indice de Fuerza Relativa (<30 sobrevendido, >70 sobrecomprado) |
| MACD | Convergencia/Divergencia de Medias Mobiles |
| SMA | Media Movil Simple |
| EMA | Media Movil Exponencial |

## Recomendaciones

- **COMPRAR**: Score >= 3 (indicadores alcistas)
- **VENDER**: Score <= -2 (indicadores bajistas)
- **MANTENER**: Resto de casos

## Disclaimer

Solo para fines educativos. No constituye asesoramiento financiero.
