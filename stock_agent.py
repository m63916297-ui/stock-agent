import yfinance as yf
from datetime import datetime
import config
import analisis
import pandas as pd


class AgenteStock:
    def __init__(self):
        self.config = config.CONFIG
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

    def analizar_mercado(self):
        tickers = self.config["tickers"]
        datos = self.obtener_datos(tickers)

        print("\nAnalizando stocks...")
        resultados = []
        for ticker, data in datos.items():
            data.name = ticker
            resultado = analisis.analyze_stock(data, self.config)
            resultados.append(resultado)

        resultados.sort(key=lambda x: x["puntuacion"], reverse=True)
        self.resultados = resultados
        return resultados

    def generar_reporte(self):
        if not self.resultados:
            self.analizar_mercado()

        print("\n" + "=" * 60)
        print("     REPORTE DE ANALISIS DE STOCKS - NYSE")
        print("=" * 60)
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        print("\n[*] TOP COMPRAR:")
        comprar = [r for r in self.resultados if r["recommendation"] == "COMPRAR"][:5]
        for i, r in enumerate(comprar, 1):
            print(
                f"  {i}. {r['ticker']} - ${r['precio_actual']} | RSI: {r['rsi']} | Score: +{r['puntuacion']}"
            )
            print(f"     Senal: {r['senal']}")

        print("\n[*] TOP VENDER:")
        vender = [r for r in self.resultados if r["recommendation"] == "VENDER"][:5]
        for i, r in enumerate(vender, 1):
            print(
                f"  {i}. {r['ticker']} - ${r['precio_actual']} | RSI: {r['rsi']} | Score: {r['puntuacion']}"
            )
            print(f"     Senal: {r['senal']}")

        print("\n[*] RANKING GENERAL:")
        for i, r in enumerate(self.resultados[: self.config["top_n"]], 1):
            rec = (
                "COMPRAR"
                if r["recommendation"] == "COMPRAR"
                else ("VENDER" if r["recommendation"] == "VENDER" else "MANTENER")
            )
            print(
                f"  {i}. {r['ticker']}: ${r['precio_actual']} | {rec} | Tendencia: {r['tendencia']}"
            )

        print("\n" + "=" * 60)
        return self.resultados

    def buscar_oportunidades(self, tipo="comprar"):
        if not self.resultados:
            self.analizar_mercado()

        if tipo == "comprar":
            return [r for r in self.resultados if r["recommendation"] == "COMPRAR"]
        elif tipo == "vender":
            return [r for r in self.resultados if r["recommendation"] == "VENDER"]
        return self.resultados


def main():
    agente = AgenteStock()
    resultados = agente.generar_reporte()

    print("\n[*] Resumen Ejecutivo:")
    mejores = resultados[0] if resultados else None
    if mejores:
        print(f"   Mejor opcion: {mejores['ticker']} ({mejores['recommendation']})")
        print(
            f"   Precio: ${mejores['precio_actual']} | Prediccion: ${mejores['precio_predicho']}"
        )

    return resultados


if __name__ == "__main__":
    main()
