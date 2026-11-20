import time
import ccxt
import pandas as pd

from config import SYMBOLS, TIMEFRAME, CANDLE_LIMIT
from indicators import add_indicators
from strategy import get_signal
from simulator import PaperBroker


def main():
    exchange = ccxt.binance({
        "enableRateLimit": True
    })

    broker = PaperBroker()

    print("CRYPTO AI TRADER 2.0")
    print("MODO: SIMULACIÓN CON DINERO VIRTUAL")
    print("No se realizan operaciones reales.")

    print(
        f"Saldo virtual: {broker.balance():.2f} USDT"
    )

    while True:

        prices = {}

        for symbol in SYMBOLS:

            try:
                candles = exchange.fetch_ohlcv(
                    symbol,
                    timeframe=TIMEFRAME,
                    limit=CANDLE_LIMIT
                )

                frame = pd.DataFrame(
                    candles,
                    columns=[
                        "time",
                        "open",
                        "high",
                        "low",
                        "close",
                        "volume"
                    ]
                )

                if len(frame) < 25:
                    continue

                data = add_indicators(frame.iloc[:-1])

                previous = data.iloc[-2]
                current = data.iloc[-1]

                price = float(current["close"])
                prices[symbol] = price

                signal = get_signal(previous, current)
                position = broker.position(symbol)

                if position:
                    if price <= position["stop"]:
                        broker.sell(
                            symbol,
                            price,
                            "STOP_LOSS"
                        )

                    elif price >= position["target"]:
                        broker.sell(
                            symbol,
                            price,
                            "TAKE_PROFIT"
                        )

                    elif signal == "SELL":
                        broker.sell(
                            symbol,
                            price,
                            "EMA_RSI"
                        )

                elif signal == "BUY":
                    broker.buy(symbol, price)

                print(
                    f"{symbol} | {signal} | "
                    f"Precio: {price:.2f} | "
                    f"Saldo: {broker.balance():.2f} USDT"
                )

            except Exception as error:
                print(f"Error en {symbol}: {error}")

        print("--------------------------------")
        time.sleep(60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Simulación detenida.")
