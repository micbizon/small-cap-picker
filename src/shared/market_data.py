import logging

import yfinance as yf

logger = logging.getLogger(__name__)


def get_price_context(ticker: str) -> str:
    try:
        info = yf.Ticker(ticker).fast_info
        return (
            f"\nAKTUALNE DANE RYNKOWE (pobrane w czasie rzeczywistym):\n"
            f"Cena: ${info['lastPrice']:.2f}\n"
            f"52-tygodniowe minimum: ${info['yearLow']:.2f}\n"
            f"52-tygodniowe maksimum: ${info['yearHigh']:.2f}\n"
        )
    except Exception as e:
        logger.warning(f"get_price_context({ticker}) failed: {e}")
        return ""
