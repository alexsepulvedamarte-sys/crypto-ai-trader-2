def add_indicators(data):
    data = data.copy()

    data["ema_fast"] = data["close"].ewm(
        span=9, adjust=False
    ).mean()

    data["ema_slow"] = data["close"].ewm(
        span=21, adjust=False
    ).mean()

    delta = data["close"].diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)

    avg_gain = gains.ewm(
        alpha=1/14, adjust=False
    ).mean()

    avg_loss = losses.ewm(
        alpha=1/14, adjust=False
    ).mean()

    rs = avg_gain / avg_loss.replace(0, float("nan"))
    data["rsi"] = (100 - (100 / (1 + rs))).fillna(50)

    return data
