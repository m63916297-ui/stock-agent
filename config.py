# Configuracion del Agente de Trading

CONFIG = {
    # Tech Stocks - Empresas tecnologicas y azules
    "tickers": [
        "AAPL",
        "MSFT",
        "GOOGL",
        "AMZN",
        "NVDA",
        "META",
        "TSLA",
        "BRK-B",
        "JPM",
        "JNJ",
        "V",
        "PG",
        "UNH",
        "HD",
        "MA",
        "DIS",
        "PYPL",
        "NFLX",
        "ADBE",
        "CRM",
        "INTC",
        "VZ",
        "T",
        "PFE",
        "MRK",
        "KO",
        "PEP",
        "WMT",
    ],
    # Bitcoin Miners - Empresas de mineria de Bitcoin
    "bitcoin_miners": [
        "MARA",
        "RIOT",
        "CLSK",
        "BTDR",
        "HIVE",
        "BITF",
        "DMGI",
        "SFIL",
        "WULF",
        "BBOX",
        "ARBK",
        "LFG",
        "CGX",
        "BRCC",
        "BITN",
    ],
    # ETFs - Fondos cotizados
    "etfs": [
        "SPY",
        "QQQ",
        "IWM",
        "DIA",
        "VOO",
        "VTI",
        "IVV",
        "SCHD",
        "VGT",
        "XLK",
        "XLF",
        "XLE",
        "XLV",
        "XLI",
        "XLP",
        "XLY",
        "XLC",
        "XLU",
        "XLB",
        "TLT",
        "GLD",
        "SLV",
        "USO",
    ],
    # Commodities - Metales, energeticos y agricoles
    "metals": [
        # Metales preciosos
        "GC=F",  # Oro
        "SI=F",  # Plata
        "PL=F",  # Platino
        "PA=F",  # Paladio
        # Metales industriales
        "HG=F",  # Cobre
        "ZI=F",  # Zinc
        "PB=F",  # Plomo
        "AL=F",  # Aluminum
        "NI=F",  # Niquel
        "SN=F",  # Estaño
        # Energeticos
        "CL=F",  # Petroleo Crudo
        "NG=F",  # Gas Natural
        "RB=F",  # Gasolina
        "HO=F",  # Heating Oil
        # Agricolas
        "ZC=F",  # Maiz
        "ZS=F",  # Soja
        "ZW=F",  # Trigo
        "KE=F",  # Trigo Kansas
        "LE=F",  # Ganado Vacuno
        "HE=F",  # Cerdos
        "CT=F",  # Algodon
        "KC=F",  # Cafe
        "SB=F",  # Azucar
        "OJ=F",  # Jugo de Naranja
        "CC=F",  # Cacao
    ],
    # Parametros de analisis
    "period": "6mo",
    "interval": "1d",
    "rsi_oversold": 30,
    "rsi_overbought": 70,
    "sma_short": 20,
    "sma_long": 50,
    "min_volume": 1000000,
    "top_n": 10,
}

# Nombres descriptivos para tickers
TICKER_NAMES = {
    # Tech Stocks
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft",
    "GOOGL": "Alphabet",
    "AMZN": "Amazon",
    "NVDA": "NVIDIA",
    "META": "Meta Platforms",
    "TSLA": "Tesla",
    "BRK-B": "Berkshire Hathaway",
    "JPM": "JPMorgan Chase",
    "JNJ": "Johnson & Johnson",
    "V": "Visa",
    "PG": "Procter & Gamble",
    "UNH": "UnitedHealth",
    "HD": "Home Depot",
    "MA": "Mastercard",
    "DIS": "Walt Disney",
    "PYPL": "PayPal",
    "NFLX": "Netflix",
    "ADBE": "Adobe",
    "CRM": "Salesforce",
    "INTC": "Intel",
    "VZ": "Verizon",
    "T": "AT&T",
    "PFE": "Pfizer",
    "MRK": "Merck",
    "KO": "Coca-Cola",
    "PEP": "PepsiCo",
    "WMT": "Walmart",
    # Bitcoin Miners
    "MARA": "Marathon Digital",
    "RIOT": "Riot Platforms",
    "CLSK": "CleanSpark",
    "BTDR": "Bitfarms",
    "HIVE": "HIVE Blockchain",
    "BITF": "Bitfarms",
    "DMGI": "DMG Blockchain",
    "SFIL": "Filecoin",
    "WULF": "WULF",
    "BBOX": "Tidewater",
    "ARBK": "Argo Blockchain",
    "LFG": "LFG",
    "CGX": "Cgx",
    "BRCC": "B. Riley Principal",
    "BITN": "Bitn",
    # ETFs
    "SPY": "S&P 500 ETF",
    "QQQ": "Nasdaq-100 ETF",
    "IWM": "Russell 2000 ETF",
    "DIA": "Dow Jones ETF",
    "VOO": "Vanguard S&P 500",
    "VTI": "Vanguard Total Stock",
    "IVV": "iShares Core S&P 500",
    "SCHD": "Schwab Dividend",
    "VGT": "Vanguard Tech",
    "XLK": "Tech Sector ETF",
    "XLF": "Financial Sector",
    "XLE": "Energy Sector",
    "XLV": "Health Sector",
    "XLI": "Industrial Sector",
    "XLP": "Consumer Staples",
    "XLY": "Consumer Disc.",
    "XLC": "Comm. Services",
    "XLU": "Utilities",
    "XLB": "Materials",
    "TLT": "20+ Year Treasury",
    "GLD": "SPDR Gold Shares",
    "SLV": "iShares Silver",
    "USO": "United States Oil",
    # Commodities
    "GC=F": "Oro",
    "SI=F": "Plata",
    "PL=F": "Platino",
    "PA=F": "Paladio",
    "HG=F": "Cobre",
    "ZI=F": "Zinc",
    "PB=F": "Plomo",
    "AL=F": "Aluminio",
    "NI=F": "Niquel",
    "SN=F": "Estaño",
    "CL=F": "Petroleo Crudo",
    "NG=F": "Gas Natural",
    "RB=F": "Gasolina",
    "HO=F": "Heating Oil",
    "ZC=F": "Maiz",
    "ZS=F": "Soja",
    "ZW=F": "Trigo",
    "KE=F": "Trigo Kansas",
    "LE=F": "Ganado Vacuno",
    "HE=F": "Cerdos",
    "CT=F": "Algodon",
    "KC=F": "Cafe",
    "SB=F": "Azucar",
    "OJ=F": "Jugo Naranja",
    "CC=F": "Cacao",
}
