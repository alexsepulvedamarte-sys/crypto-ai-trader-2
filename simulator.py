import json
import os
import pandas as pd

from config import (
    STARTING_BALANCE,
    FEE_RATE,
    TRADE_FRACTION,
    STOP_LOSS_PCT,
    TAKE_PROFIT_PCT,
    STATE_FILE,
    TRADES_FILE
)


class PaperBroker:

    def __init__(self):
        self.state = self.load_state()

    def load_state(self):
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as file:
                return json.load(file)

        return {
            "cash": STARTING_BALANCE,
            "positions": {}
        }

    def save(self):
        with open(STATE_FILE, "w") as file:
            json.dump(self.state, file, indent=2)

    def balance(self):
        return float(self.state["cash"])

    def position(self, symbol):
        return self.state["positions"].get(symbol)

    def log(self, symbol, side, price, amount, fee, reason):
        row = {
            "timestamp": pd.Timestamp.utcnow().isoformat(),
            "symbol": symbol,
            "side": side,
            "price": price,
            "amount": amount,
            "fee": fee,
            "reason": reason
        }

        frame = pd.DataFrame([row])

        frame.to_csv(
            TRADES_FILE,
            mode="a",
            header=not os.path.exists(TRADES_FILE),
            index=False
        )

    def buy(self, symbol, price):
        if self.position(symbol):
            return False

        budget = self.balance() * TRADE_FRACTION
        fee = budget * FEE_RATE
        spend = budget - fee

        if spend <= 0 or price <= 0:
            return False

        amount = spend / price

        self.state["cash"] -= budget

        self.state["positions"][symbol] = {
            "entry": price,
            "amount": amount,
            "stop": price * (1 - STOP_LOSS_PCT),
            "target": price * (1 + TAKE_PROFIT_PCT)
        }

        self.log(symbol, "BUY", price, amount, fee, "EMA_RSI")
        self.save()

        return True

    def sell(self, symbol, price, reason="SIGNAL"):
        position = self.position(symbol)

        if not position or price <= 0:
            return False

        gross = position["amount"] * price
        fee = gross * FEE_RATE

        self.state["cash"] += gross - fee

        self.log(
            symbol,
            "SELL",
            price,
            position["amount"],
            fee,
            reason
        )

        del self.state["positions"][symbol]

        self.save()
        return True

    def check_risk_exits(self, prices):
        for symbol, position in list(
            self.state["positions"].items()
        ):
            price = prices.get(symbol)

            if price is None:
                continue

            if price <= position["stop"]:
                self.sell(symbol, price, "STOP_LOSS")

            elif price >= position["target"]:
                self.sell(symbol, price, "TAKE_PROFIT")
