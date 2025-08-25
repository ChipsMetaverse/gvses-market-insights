from models.schemas import TechnicalOverview, MACDSeries, BollingerBandsSeries, FibonacciLevels, FibonacciLevel, IndicatorPoint


def build_technical_overview(symbol: str, candles: list) -> dict:
    """Build technical overview from OHLCV data - direct implementation"""
    
    if not candles:
        return {
            "rating": "Neutral",
            "rating_score": 0.0,
            "notes": ["Insufficient data for analysis"]
        }
    
    # Extract price data
    closes = [c.get('close', c) if isinstance(c, dict) else c for c in candles]
    times = [c.get('time', i) if isinstance(c, dict) else i for i, c in enumerate(candles)]
    
    if len(closes) < 20:
        return {
            "rating": "Neutral",
            "rating_score": 0.0,
            "notes": ["Need more data for full analysis"]
        }
    
    # Simple moving averages
    def sma(data, period):
        result = []
        for i in range(len(data)):
            if i < period - 1:
                result.append(sum(data[:i+1]) / (i+1))
            else:
                result.append(sum(data[i-period+1:i+1]) / period)
        return result
    
    # Simple MACD calculation
    def ema(data, period):
        alpha = 2 / (period + 1)
        ema_values = [data[0]]
        for i in range(1, len(data)):
            ema_values.append(alpha * data[i] + (1 - alpha) * ema_values[-1])
        return ema_values
    
    ema_12 = ema(closes, 12)
    ema_26 = ema(closes, 26) if len(closes) >= 26 else ema_12
    macd_line = [fast - slow for fast, slow in zip(ema_12, ema_26)]
    signal_line = ema(macd_line, 9)
    histogram = [m - s for m, s in zip(macd_line, signal_line)]
    
    # Build MACD series
    macd = {
        "macd_line": [{"time": t, "value": v} for t, v in zip(times, macd_line)],
        "signal_line": [{"time": t, "value": v} for t, v in zip(times, signal_line)],
        "histogram": [{"time": t, "value": v} for t, v in zip(times, histogram)],
        "fast_period": 12,
        "slow_period": 26,
        "signal_period": 9,
        "last_macd": macd_line[-1] if macd_line else None,
        "last_signal": signal_line[-1] if signal_line else None,
        "last_histogram": histogram[-1] if histogram else None,
    }
    
    # Simple Bollinger Bands
    ma_20 = sma(closes, 20)
    
    # Calculate standard deviation
    std_devs = []
    for i in range(len(closes)):
        if i < 19:
            data_slice = closes[:i+1]
        else:
            data_slice = closes[i-19:i+1]
        
        mean = sum(data_slice) / len(data_slice)
        variance = sum((x - mean) ** 2 for x in data_slice) / len(data_slice)
        std_devs.append(variance ** 0.5)
    
    bb_upper = [m + (s * 2) for m, s in zip(ma_20, std_devs)]
    bb_lower = [m - (s * 2) for m, s in zip(ma_20, std_devs)]
    
    bb = {
        "upper": [{"time": t, "value": v} for t, v in zip(times, bb_upper)],
        "middle": [{"time": t, "value": v} for t, v in zip(times, ma_20)],
        "lower": [{"time": t, "value": v} for t, v in zip(times, bb_lower)],
        "period": 20,
        "stddev": 2.0,
    }
    
    # Simple Fibonacci levels
    high_price = max(closes)
    low_price = min(closes)
    high_idx = closes.index(high_price)
    low_idx = closes.index(low_price)
    
    diff = high_price - low_price
    fib = {
        "high_anchor_time": times[high_idx],
        "low_anchor_time": times[low_idx],
        "levels": [
            {"level": 0.0, "price": low_price},
            {"level": 0.236, "price": high_price - (diff * 0.236)},
            {"level": 0.382, "price": high_price - (diff * 0.382)},
            {"level": 0.5, "price": high_price - (diff * 0.5)},
            {"level": 0.618, "price": high_price - (diff * 0.618)},
            {"level": 0.786, "price": high_price - (diff * 0.786)},
            {"level": 1.0, "price": high_price}
        ]
    }
    
    # Calculate rating
    last_close = closes[-1]
    middle_band_last = ma_20[-1]
    macd_vs_signal = histogram[-1] if histogram else 0
    
    score = 0.0
    notes = []
    
    # Price vs middle band
    if last_close >= middle_band_last:
        score += 0.3
        notes.append("Price above middle band")
    else:
        score -= 0.3
        notes.append("Price below middle band")
    
    # MACD vs signal
    if macd_vs_signal >= 0:
        score += 0.4
        notes.append("MACD above signal")
    else:
        score -= 0.4
        notes.append("MACD below signal")
    
    # Momentum check
    if len(closes) > 5:
        recent_change = (closes[-1] - closes[-5]) / closes[-5]
        if recent_change > 0.02:
            score += 0.2
            notes.append("Positive momentum")
        elif recent_change < -0.02:
            score -= 0.2
            notes.append("Negative momentum")
    
    # Determine rating
    if score >= 0.4:
        rating = "Bullish"
    elif score <= -0.2:
        rating = "Bearish"
    else:
        rating = "Neutral"
    
    return {
        "rating": rating,
        "rating_score": round(score, 2),
        "macd": macd,
        "bollinger_bands": bb,
        "fibonacci": fib,
        "notes": notes
    }