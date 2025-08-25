"""
Options Analysis Service for G'sves Market Insights
Provides options strategies, Greeks calculations, and trade recommendations
"""

import numpy as np
from scipy.stats import norm
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import logging
import math

logger = logging.getLogger(__name__)

class OptionsAnalysisService:
    """Service for options analysis and strategy recommendations"""
    
    @staticmethod
    def calculate_greeks(
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,  # in years
        volatility: float,  # implied volatility as decimal
        risk_free_rate: float = 0.05,  # 5% default
        option_type: str = 'call'
    ) -> Dict[str, float]:
        """
        Calculate option Greeks using Black-Scholes model
        """
        try:
            # Ensure positive values
            if time_to_expiry <= 0:
                time_to_expiry = 0.001  # Minimum time
                
            # Calculate d1 and d2
            d1 = (np.log(spot_price / strike_price) + 
                  (risk_free_rate + 0.5 * volatility ** 2) * time_to_expiry) / \
                 (volatility * np.sqrt(time_to_expiry))
            
            d2 = d1 - volatility * np.sqrt(time_to_expiry)
            
            # Calculate Greeks
            if option_type.lower() == 'call':
                delta = norm.cdf(d1)
                theta = (-spot_price * norm.pdf(d1) * volatility / (2 * np.sqrt(time_to_expiry)) -
                        risk_free_rate * strike_price * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2)) / 365
            else:  # put
                delta = norm.cdf(d1) - 1
                theta = (-spot_price * norm.pdf(d1) * volatility / (2 * np.sqrt(time_to_expiry)) +
                        risk_free_rate * strike_price * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2)) / 365
            
            gamma = norm.pdf(d1) / (spot_price * volatility * np.sqrt(time_to_expiry))
            vega = spot_price * norm.pdf(d1) * np.sqrt(time_to_expiry) / 100  # Per 1% change in IV
            rho = 0.01 * strike_price * time_to_expiry * np.exp(-risk_free_rate * time_to_expiry) * \
                  (norm.cdf(d2) if option_type.lower() == 'call' else norm.cdf(-d2))
            
            return {
                'delta': round(delta, 4),
                'gamma': round(gamma, 5),
                'theta': round(theta, 2),
                'vega': round(vega, 2),
                'rho': round(rho, 3)
            }
            
        except Exception as e:
            logger.error(f"Error calculating Greeks: {e}")
            return {
                'delta': 0.5,
                'gamma': 0.01,
                'theta': -0.05,
                'vega': 0.1,
                'rho': 0.01
            }
    
    @staticmethod
    def calculate_implied_volatility_rank(current_iv: float, historical_ivs: List[float]) -> float:
        """
        Calculate IV Rank (0-100)
        """
        if not historical_ivs or len(historical_ivs) < 2:
            return 50.0  # Default middle rank
            
        min_iv = min(historical_ivs)
        max_iv = max(historical_ivs)
        
        if max_iv == min_iv:
            return 50.0
            
        iv_rank = ((current_iv - min_iv) / (max_iv - min_iv)) * 100
        return round(max(0, min(100, iv_rank)), 1)
    
    @staticmethod
    def recommend_options_strategy(
        spot_price: float,
        volatility: float,
        trend: str,  # 'bullish', 'bearish', 'neutral'
        iv_rank: float,
        risk_tolerance: str = 'moderate'  # 'conservative', 'moderate', 'aggressive'
    ) -> Dict[str, Any]:
        """
        Recommend appropriate options strategy based on market conditions
        """
        strategies = []
        
        # High IV strategies (selling premium)
        if iv_rank > 70:
            if trend == 'bullish':
                strategies.append(OptionsAnalysisService._bull_put_spread(spot_price, volatility))
                strategies.append(OptionsAnalysisService._cash_secured_put(spot_price, volatility))
            elif trend == 'bearish':
                strategies.append(OptionsAnalysisService._bear_call_spread(spot_price, volatility))
                strategies.append(OptionsAnalysisService._covered_call(spot_price, volatility))
            else:  # neutral
                strategies.append(OptionsAnalysisService._iron_condor(spot_price, volatility))
                strategies.append(OptionsAnalysisService._short_strangle(spot_price, volatility))
                
        # Low IV strategies (buying premium)
        elif iv_rank < 30:
            if trend == 'bullish':
                strategies.append(OptionsAnalysisService._long_call(spot_price, volatility))
                strategies.append(OptionsAnalysisService._bull_call_spread(spot_price, volatility))
            elif trend == 'bearish':
                strategies.append(OptionsAnalysisService._long_put(spot_price, volatility))
                strategies.append(OptionsAnalysisService._bear_put_spread(spot_price, volatility))
            else:  # neutral
                strategies.append(OptionsAnalysisService._long_straddle(spot_price, volatility))
                strategies.append(OptionsAnalysisService._calendar_spread(spot_price, volatility))
                
        # Normal IV strategies
        else:
            if trend == 'bullish':
                strategies.append(OptionsAnalysisService._bull_call_spread(spot_price, volatility))
                strategies.append(OptionsAnalysisService._call_diagonal(spot_price, volatility))
            elif trend == 'bearish':
                strategies.append(OptionsAnalysisService._bear_put_spread(spot_price, volatility))
                strategies.append(OptionsAnalysisService._put_diagonal(spot_price, volatility))
            else:  # neutral
                strategies.append(OptionsAnalysisService._butterfly_spread(spot_price, volatility))
                strategies.append(OptionsAnalysisService._calendar_spread(spot_price, volatility))
        
        # Filter by risk tolerance
        if risk_tolerance == 'conservative':
            strategies = [s for s in strategies if s['risk_level'] in ['low', 'moderate']]
        elif risk_tolerance == 'aggressive':
            strategies = [s for s in strategies if s['risk_level'] in ['moderate', 'high']]
            
        # Return best strategy
        return strategies[0] if strategies else OptionsAnalysisService._default_strategy(spot_price)
    
    @staticmethod
    def calculate_option_premium(
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        volatility: float,
        risk_free_rate: float = 0.05,
        option_type: str = 'call'
    ) -> float:
        """
        Calculate option premium using Black-Scholes
        """
        d1 = (np.log(spot_price / strike_price) + 
              (risk_free_rate + 0.5 * volatility ** 2) * time_to_expiry) / \
             (volatility * np.sqrt(time_to_expiry))
        
        d2 = d1 - volatility * np.sqrt(time_to_expiry)
        
        if option_type.lower() == 'call':
            premium = (spot_price * norm.cdf(d1) - 
                      strike_price * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2))
        else:
            premium = (strike_price * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2) - 
                      spot_price * norm.cdf(-d1))
            
        return round(premium, 2)
    
    # Strategy builders
    @staticmethod
    def _bull_call_spread(spot: float, vol: float) -> Dict[str, Any]:
        """Bull Call Spread strategy"""
        long_strike = round(spot * 1.02, 0)  # 2% OTM
        short_strike = round(spot * 1.05, 0)  # 5% OTM
        
        return {
            'strategy': 'Bull Call Spread',
            'legs': [
                {'action': 'Buy', 'type': 'Call', 'strike': long_strike},
                {'action': 'Sell', 'type': 'Call', 'strike': short_strike}
            ],
            'max_profit': short_strike - long_strike,
            'max_loss': 2.5,  # Estimated debit
            'breakeven': long_strike + 2.5,
            'risk_level': 'moderate',
            'ideal_scenario': 'Moderate bullish move',
            'entry_conditions': [
                f'Enter when price breaks above ${spot * 1.01:.2f}',
                'Confirm uptrend with rising volume',
                'RSI between 50-70 for momentum'
            ]
        }
    
    @staticmethod
    def _bull_put_spread(spot: float, vol: float) -> Dict[str, Any]:
        """Bull Put Spread (Credit Spread)"""
        short_strike = round(spot * 0.98, 0)  # 2% OTM
        long_strike = round(spot * 0.95, 0)   # 5% OTM
        
        return {
            'strategy': 'Bull Put Spread',
            'legs': [
                {'action': 'Sell', 'type': 'Put', 'strike': short_strike},
                {'action': 'Buy', 'type': 'Put', 'strike': long_strike}
            ],
            'max_profit': 2.0,  # Estimated credit
            'max_loss': short_strike - long_strike - 2.0,
            'breakeven': short_strike - 2.0,
            'risk_level': 'moderate',
            'ideal_scenario': 'Price stays above short strike',
            'entry_conditions': [
                f'Enter when price bounces off support at ${spot * 0.97:.2f}',
                'High IV rank (>50) for premium collection',
                'Bullish trend intact on daily chart'
            ]
        }
    
    @staticmethod
    def _iron_condor(spot: float, vol: float) -> Dict[str, Any]:
        """Iron Condor strategy"""
        put_short = round(spot * 0.95, 0)
        put_long = round(spot * 0.92, 0)
        call_short = round(spot * 1.05, 0)
        call_long = round(spot * 1.08, 0)
        
        return {
            'strategy': 'Iron Condor',
            'legs': [
                {'action': 'Sell', 'type': 'Put', 'strike': put_short},
                {'action': 'Buy', 'type': 'Put', 'strike': put_long},
                {'action': 'Sell', 'type': 'Call', 'strike': call_short},
                {'action': 'Buy', 'type': 'Call', 'strike': call_long}
            ],
            'max_profit': 3.5,  # Estimated credit
            'max_loss': 3.0,  # Width of spread - credit
            'breakeven': [put_short - 3.5, call_short + 3.5],
            'risk_level': 'moderate',
            'ideal_scenario': 'Range-bound movement',
            'entry_conditions': [
                f'Enter when price is between ${put_short:.2f} and ${call_short:.2f}',
                'Low realized volatility (<20 day average)',
                'No major events in next 30 days'
            ]
        }
    
    @staticmethod
    def _long_call(spot: float, vol: float) -> Dict[str, Any]:
        """Long Call strategy"""
        strike = round(spot * 1.02, 0)  # Slightly OTM
        
        return {
            'strategy': 'Long Call',
            'legs': [
                {'action': 'Buy', 'type': 'Call', 'strike': strike}
            ],
            'max_profit': 'Unlimited',
            'max_loss': 3.5,  # Estimated premium
            'breakeven': strike + 3.5,
            'risk_level': 'moderate',
            'ideal_scenario': 'Strong bullish move',
            'entry_conditions': [
                'Enter on breakout above resistance',
                'Rising volume confirmation',
                'RSI not yet overbought (<70)'
            ]
        }
    
    @staticmethod
    def _cash_secured_put(spot: float, vol: float) -> Dict[str, Any]:
        """Cash Secured Put strategy"""
        strike = round(spot * 0.97, 0)  # 3% OTM
        
        return {
            'strategy': 'Cash Secured Put',
            'legs': [
                {'action': 'Sell', 'type': 'Put', 'strike': strike}
            ],
            'max_profit': 2.5,  # Estimated premium
            'max_loss': strike - 2.5,
            'breakeven': strike - 2.5,
            'risk_level': 'conservative',
            'ideal_scenario': 'Accumulate stock or collect premium',
            'entry_conditions': [
                f'Enter when willing to own stock at ${strike:.2f}',
                'High IV rank for better premium',
                'Stock at support level'
            ]
        }
    
    @staticmethod
    def _bear_call_spread(spot: float, vol: float) -> Dict[str, Any]:
        """Bear Call Spread"""
        short_strike = round(spot * 1.02, 0)
        long_strike = round(spot * 1.05, 0)
        
        return {
            'strategy': 'Bear Call Spread',
            'legs': [
                {'action': 'Sell', 'type': 'Call', 'strike': short_strike},
                {'action': 'Buy', 'type': 'Call', 'strike': long_strike}
            ],
            'max_profit': 2.0,  # Credit received
            'max_loss': long_strike - short_strike - 2.0,
            'breakeven': short_strike + 2.0,
            'risk_level': 'moderate',
            'ideal_scenario': 'Price stays below short strike',
            'entry_conditions': [
                'Enter on rejection at resistance',
                'Declining volume on rallies',
                'RSI showing divergence'
            ]
        }
    
    @staticmethod
    def _covered_call(spot: float, vol: float) -> Dict[str, Any]:
        """Covered Call strategy"""
        strike = round(spot * 1.03, 0)
        
        return {
            'strategy': 'Covered Call',
            'legs': [
                {'action': 'Own', 'type': 'Stock', 'shares': 100},
                {'action': 'Sell', 'type': 'Call', 'strike': strike}
            ],
            'max_profit': (strike - spot) + 2.0,  # Price appreciation + premium
            'max_loss': spot - 2.0,  # Stock price - premium
            'breakeven': spot - 2.0,
            'risk_level': 'conservative',
            'ideal_scenario': 'Slight bullish to neutral',
            'entry_conditions': [
                'Own 100 shares of stock',
                'Stock near resistance',
                'High IV for better premium'
            ]
        }
    
    @staticmethod
    def _default_strategy(spot: float) -> Dict[str, Any]:
        """Default conservative strategy"""
        return {
            'strategy': 'Wait for Better Setup',
            'recommendation': 'Market conditions unclear',
            'alternative': 'Consider paper trading or smaller position sizes',
            'risk_level': 'none',
            'entry_conditions': [
                'Wait for clearer trend',
                'Monitor IV levels',
                'Watch for catalyst events'
            ]
        }
    
    @staticmethod
    def _long_put(spot: float, vol: float) -> Dict[str, Any]:
        """Long Put strategy"""
        strike = round(spot * 0.98, 0)
        
        return {
            'strategy': 'Long Put',
            'legs': [
                {'action': 'Buy', 'type': 'Put', 'strike': strike}
            ],
            'max_profit': strike - 3.0,  # Strike - premium
            'max_loss': 3.0,  # Premium paid
            'breakeven': strike - 3.0,
            'risk_level': 'moderate',
            'ideal_scenario': 'Strong bearish move',
            'entry_conditions': [
                'Enter on breakdown below support',
                'Increasing volume on decline',
                'RSI showing weakness (<50)'
            ]
        }
    
    @staticmethod
    def _bear_put_spread(spot: float, vol: float) -> Dict[str, Any]:
        """Bear Put Spread"""
        long_strike = round(spot * 0.98, 0)
        short_strike = round(spot * 0.95, 0)
        
        return {
            'strategy': 'Bear Put Spread',
            'legs': [
                {'action': 'Buy', 'type': 'Put', 'strike': long_strike},
                {'action': 'Sell', 'type': 'Put', 'strike': short_strike}
            ],
            'max_profit': long_strike - short_strike - 2.0,
            'max_loss': 2.0,  # Net debit
            'breakeven': long_strike - 2.0,
            'risk_level': 'moderate',
            'ideal_scenario': 'Moderate bearish move',
            'entry_conditions': [
                'Enter on failed rally attempt',
                'Declining moving averages',
                'Negative momentum indicators'
            ]
        }
    
    @staticmethod
    def _long_straddle(spot: float, vol: float) -> Dict[str, Any]:
        """Long Straddle"""
        strike = round(spot, 0)  # ATM
        
        return {
            'strategy': 'Long Straddle',
            'legs': [
                {'action': 'Buy', 'type': 'Call', 'strike': strike},
                {'action': 'Buy', 'type': 'Put', 'strike': strike}
            ],
            'max_profit': 'Unlimited',
            'max_loss': 7.0,  # Combined premium
            'breakeven': [strike - 7.0, strike + 7.0],
            'risk_level': 'high',
            'ideal_scenario': 'Large move in either direction',
            'entry_conditions': [
                'Enter before major catalyst',
                'Low IV environment',
                'Expecting volatility expansion'
            ]
        }
    
    @staticmethod
    def _short_strangle(spot: float, vol: float) -> Dict[str, Any]:
        """Short Strangle"""
        put_strike = round(spot * 0.95, 0)
        call_strike = round(spot * 1.05, 0)
        
        return {
            'strategy': 'Short Strangle',
            'legs': [
                {'action': 'Sell', 'type': 'Put', 'strike': put_strike},
                {'action': 'Sell', 'type': 'Call', 'strike': call_strike}
            ],
            'max_profit': 4.0,  # Combined premium
            'max_loss': 'Unlimited',
            'breakeven': [put_strike - 4.0, call_strike + 4.0],
            'risk_level': 'high',
            'ideal_scenario': 'Range-bound with IV contraction',
            'entry_conditions': [
                'High IV rank (>70)',
                'No major events upcoming',
                'Strong support/resistance levels'
            ]
        }
    
    @staticmethod
    def _calendar_spread(spot: float, vol: float) -> Dict[str, Any]:
        """Calendar Spread"""
        strike = round(spot, 0)  # ATM
        
        return {
            'strategy': 'Calendar Spread',
            'legs': [
                {'action': 'Sell', 'type': 'Call', 'strike': strike, 'expiry': 'Front month'},
                {'action': 'Buy', 'type': 'Call', 'strike': strike, 'expiry': 'Back month'}
            ],
            'max_profit': 2.5,  # Estimated
            'max_loss': 1.5,  # Net debit
            'breakeven': 'Complex (depends on IV)',
            'risk_level': 'moderate',
            'ideal_scenario': 'Price stays near strike, IV increases',
            'entry_conditions': [
                'Low front-month IV',
                'Expecting consolidation',
                'No near-term catalysts'
            ]
        }
    
    @staticmethod
    def _butterfly_spread(spot: float, vol: float) -> Dict[str, Any]:
        """Butterfly Spread"""
        lower = round(spot * 0.97, 0)
        middle = round(spot, 0)
        upper = round(spot * 1.03, 0)
        
        return {
            'strategy': 'Butterfly Spread',
            'legs': [
                {'action': 'Buy', 'type': 'Call', 'strike': lower},
                {'action': 'Sell', 'type': 'Call', 'strike': middle, 'quantity': 2},
                {'action': 'Buy', 'type': 'Call', 'strike': upper}
            ],
            'max_profit': (middle - lower) - 1.5,
            'max_loss': 1.5,  # Net debit
            'breakeven': [lower + 1.5, upper - 1.5],
            'risk_level': 'low',
            'ideal_scenario': 'Price pins to middle strike',
            'entry_conditions': [
                'Low volatility expected',
                'Strong magnet level identified',
                'Near expiration for theta decay'
            ]
        }
    
    @staticmethod
    def _call_diagonal(spot: float, vol: float) -> Dict[str, Any]:
        """Call Diagonal Spread"""
        short_strike = round(spot * 1.02, 0)
        long_strike = round(spot * 1.03, 0)
        
        return {
            'strategy': 'Call Diagonal',
            'legs': [
                {'action': 'Sell', 'type': 'Call', 'strike': short_strike, 'expiry': 'Front month'},
                {'action': 'Buy', 'type': 'Call', 'strike': long_strike, 'expiry': 'Back month'}
            ],
            'max_profit': 2.0,  # Estimated
            'max_loss': 1.0,  # Net debit
            'breakeven': 'Variable based on time',
            'risk_level': 'moderate',
            'ideal_scenario': 'Slow upward drift',
            'entry_conditions': [
                'Moderate bullish bias',
                'High front-month IV',
                'Support holding'
            ]
        }
    
    @staticmethod
    def _put_diagonal(spot: float, vol: float) -> Dict[str, Any]:
        """Put Diagonal Spread"""
        short_strike = round(spot * 0.98, 0)
        long_strike = round(spot * 0.97, 0)
        
        return {
            'strategy': 'Put Diagonal',
            'legs': [
                {'action': 'Sell', 'type': 'Put', 'strike': short_strike, 'expiry': 'Front month'},
                {'action': 'Buy', 'type': 'Put', 'strike': long_strike, 'expiry': 'Back month'}
            ],
            'max_profit': 2.0,  # Estimated
            'max_loss': 1.0,  # Net debit
            'breakeven': 'Variable based on time',
            'risk_level': 'moderate',
            'ideal_scenario': 'Slow downward drift',
            'entry_conditions': [
                'Moderate bearish bias',
                'High front-month IV',
                'Resistance holding'
            ]
        }