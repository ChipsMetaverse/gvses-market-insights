from typing import List, Dict, Any
from datetime import datetime, timedelta


def get_insights(symbol: str, spot: float, horizon_days: int = 30) -> dict:
    """Get strategic insights for options strategies - simplified direct implementation"""
    
    # Direct mock data generation without wrappers
    strategies = []
    
    # Long Call Strategy
    strategies.append({
        "strategy_code": "long_call",
        "title": "Long Call - Bullish Play",
        "rationale": "Expecting upward movement with limited downside risk",
        "recommended_legs": [
            {
                "right": "CALL",
                "action": "BUY",
                "strike": round(spot * 1.02, 2),
                "expiry": (datetime.now() + timedelta(days=30)).date().isoformat(),
                "quantity": 1
            }
        ],
        "net_debit_credit": 250.0,
        "max_profit": None,
        "max_profit_text": "Unlimited",
        "max_loss": 250.0,
        "max_loss_text": None,
        "breakevens": [round(spot * 1.02 + 2.50, 2)],
        "probability_of_profit_pct": 42.5,
        "greeks_delta": 0.45,
        "greeks_gamma": 0.02,
        "greeks_theta": -8.5,
        "greeks_vega": 12.3,
        "greeks_rho": 5.2,
        "time_horizon_days": horizon_days,
        "tags": ["directional-bullish", "leverage"]
    })
    
    # Iron Condor Strategy
    strategies.append({
        "strategy_code": "iron_condor",
        "title": "Iron Condor - Range Bound",
        "rationale": "Profit from low volatility within expected range",
        "recommended_legs": [
            {
                "right": "PUT",
                "action": "SELL",
                "strike": round(spot * 0.95, 2),
                "expiry": (datetime.now() + timedelta(days=30)).date().isoformat(),
                "quantity": 1
            },
            {
                "right": "PUT",
                "action": "BUY",
                "strike": round(spot * 0.92, 2),
                "expiry": (datetime.now() + timedelta(days=30)).date().isoformat(),
                "quantity": 1
            },
            {
                "right": "CALL",
                "action": "SELL",
                "strike": round(spot * 1.05, 2),
                "expiry": (datetime.now() + timedelta(days=30)).date().isoformat(),
                "quantity": 1
            },
            {
                "right": "CALL",
                "action": "BUY",
                "strike": round(spot * 1.08, 2),
                "expiry": (datetime.now() + timedelta(days=30)).date().isoformat(),
                "quantity": 1
            }
        ],
        "net_debit_credit": -180.0,
        "max_profit": 180.0,
        "max_profit_text": None,
        "max_loss": 320.0,
        "max_loss_text": None,
        "breakevens": [round(spot * 0.95 - 1.80, 2), round(spot * 1.05 + 1.80, 2)],
        "probability_of_profit_pct": 68.2,
        "greeks_delta": -0.02,
        "greeks_gamma": -0.01,
        "greeks_theta": 12.5,
        "greeks_vega": -18.6,
        "greeks_rho": -2.1,
        "time_horizon_days": horizon_days,
        "tags": ["income", "neutral", "theta-positive"]
    })
    
    return {
        "spot_price": spot,
        "iv_rank": 45.2,
        "iv_percentile": 62.8,
        "skew_25d": -2.3,
        "items": strategies
    }