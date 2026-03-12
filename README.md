# Quant Trading Agent

Analisis cuantitativo profesional con multiples indicadores tecnicos.

## Caracteristicas

- **9 Indicadores Tecnicos** especializados
- **4 Mercados**: Tech Stocks, Bitcoin Miners, ETFs, Commodities
- **Sistema de Scoring** ponderado
- **Interfaz Streamlit** interactiva

## Instalacion

```bash
cd genai
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

## Uso

### Interfaz Grafica
```bash
streamlit run app.py
```

### Linea de Comandos
```bash
python stock_agent.py
```

## Indicadores Cuantitativos

| Indicador | Descripcion | Peso |
|-----------|-------------|------|
| RSI (14) | Relative Strength Index | 2.0 |
| Stochastic %K | Oscilador estocastico | 1.5 |
| MACD | Convergencia/Divergencia media movil | 1.5 |
| Bollinger Bands | Bandas de volatilidad | 1.0 |
| ADX | Indice de direccion promedio | 1.5 |
| Momentum | Tasa de cambio porcentual | 1.0 |
| Williams %R | Porcentaje de Williams | 1.0 |
| CCI | Indice de canal de commodities | 1.0 |

## Sistema de Recomendacion

- **COMPRAR**: Score >= 4 (indicadores alcistas fuertes)
- **VENDER**: Score <= -3 (indicadores bajistas fuertes)
- **MANTENER**: Resto de casos

## Mercados

| Modulo | Activos |
|--------|---------|
| Tech Stocks | 28 empresas |
| Bitcoin Miners | 15 empresas |
| ETFs | 23 fondos |
| Commodities | 27 activos |

## Disclaimer

Solo para fines educativos. No constituye asesoramiento financiero.
