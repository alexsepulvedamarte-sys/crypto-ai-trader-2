def get_signal(previous, current):
    crossed_up = (
        previous["ema_fast"] <= previous["ema_slow"]
        and current["ema_fast"] > current["ema_slow"]
    )

    crossed_down = (
        previous["ema_fast"] >= previous["ema_slow"]
        and current["ema_fast"] < current["ema_slow"]
    )

    if crossed_up and 50 <= current["rsi"] <= 70:
        return "BUY"

    if crossed_down and current["rsi"] >= 30:
        return "SELL"

    return "HOLD"
