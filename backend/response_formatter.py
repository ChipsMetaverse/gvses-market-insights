"""
Response Formatter for G'sves Market Insights
Structures market data into professional analysis format
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import json


def format_response(data: Any, meta: dict = None, status: str = "ok", error: dict = None) -> dict:
    """Format API response in standard envelope"""
    return {
        "status": status,
        "data": data,
        "meta": meta or {},
        "error": error
    }


class MarketResponseFormatter:
    """Formats market data into structured, professional responses"""
    
    @staticmethod
    def format_stock_analysis(data: Dict[str, Any]) -> str:
        """
        Format comprehensive stock analysis with all technical levels
        """
        symbol = data.get('symbol', 'N/A')
        price = data.get('price', 0)
        change = data.get('change', 0)
        change_pct = data.get('change_percent', 0)
        volume = data.get('volume', 0)
        avg_volume = data.get('avg_volume', 0)
        
        # Technical indicators
        rsi = data.get('rsi', 'N/A')
        ma_20 = data.get('ma_20', 'N/A')
        ma_50 = data.get('ma_50', 'N/A')
        ma_200 = data.get('ma_200', 'N/A')
        
        # Trading levels
        ltb = data.get('ltb_level', 'N/A')
        st = data.get('st_level', 'N/A')
        qe = data.get('qe_level', 'N/A')
        
        # Volume analysis
        volume_ratio = volume / avg_volume if avg_volume > 0 else 0
        volume_desc = "Heavy" if volume_ratio > 1.5 else "Above avg" if volume_ratio > 1 else "Light"
        
        # RSI interpretation
        rsi_signal = "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral"
        
        response = f"""
📊 **{symbol} Analysis** (as of {datetime.now().strftime('%I:%M %p ET')})

**Market Snapshot:**
• Price: ${price:.2f} ({'+' if change >= 0 else ''}{change:.2f}, {'+' if change_pct >= 0 else ''}{change_pct:.2f}%)
• Volume: {volume:,.0f} ({volume_desc}, {volume_ratio:.1f}x avg)
• RSI: {rsi} ({rsi_signal})

**Technical Levels:**
• **Load the Boat (LTB):** ${ltb} - Strong support near 200-day MA
• **Swing Trade (ST):** ${st} - Consolidation zone, 50-day MA confluence  
• **Quick Entry (QE):** ${qe} - Momentum entry, breakout potential

**Moving Averages:**
• 20-Day: ${ma_20:.2f}
• 50-Day: ${ma_50:.2f}
• 200-Day: ${ma_200:.2f}

**Strategic Insights:**
• {symbol} is trading {'above' if price > ma_50 else 'below'} its 50-day MA
• Volume shows {volume_desc.lower()} interest at {volume_ratio:.1f}x average
• RSI at {rsi} indicates {rsi_signal.lower()} conditions
"""
        
        # Add confluence analysis
        if price < ltb:
            response += f"• ⚠️ Trading below LTB - potential accumulation zone\n"
        elif price > qe:
            response += f"• 🚀 Trading above QE - momentum continuation likely\n"
        else:
            response += f"• 📍 Trading in consolidation between ST and QE\n"
            
        return response
    
    @staticmethod
    def format_market_brief(movers_data: Dict[str, Any]) -> str:
        """
        Format morning market brief with key movers and catalysts
        """
        timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p ET')
        
        response = f"""
☀️ **Good Morning! Market Brief**
📅 {timestamp}

**Pre-Market Overview:**
• S&P 500 Futures: {'🟢' if movers_data.get('spy_change', 0) > 0 else '🔴'} {movers_data.get('spy_change', 0):.2f}%
• Nasdaq Futures: {'🟢' if movers_data.get('qqq_change', 0) > 0 else '🔴'} {movers_data.get('qqq_change', 0):.2f}%
• VIX: {movers_data.get('vix', 'N/A')} ({movers_data.get('vix_change', 'N/A')}%)

**Top Gainers (Pre-Market):**
"""
        # Add top gainers
        for gainer in movers_data.get('gainers', [])[:3]:
            response += f"• {gainer['symbol']}: +{gainer['change_pct']:.2f}% (${gainer['price']:.2f})\n"
            
        response += "\n**Top Losers (Pre-Market):**\n"
        
        # Add top losers
        for loser in movers_data.get('losers', [])[:3]:
            response += f"• {loser['symbol']}: {loser['change_pct']:.2f}% (${loser['price']:.2f})\n"
            
        response += "\n**Key Catalysts Today:**\n"
        
        # Add catalysts
        for catalyst in movers_data.get('catalysts', [])[:3]:
            response += f"• {catalyst}\n"
            
        response += "\n**Watchlist Stocks:**\n"
        
        # Add watchlist
        for stock in movers_data.get('watchlist', [])[:5]:
            response += f"• {stock['symbol']}: {stock['reason']}\n"
            
        return response
    
    @staticmethod
    def format_options_strategy(options_data: Dict[str, Any]) -> str:
        """
        Format options trading strategy with Greeks
        """
        symbol = options_data.get('symbol', 'N/A')
        strategy = options_data.get('strategy', 'N/A')
        
        response = f"""
🎯 **Options Strategy for {symbol}**

**Recommended Play:** {strategy}

**Trade Setup:**
• Strike: ${options_data.get('strike', 0):.2f}
• Expiration: {options_data.get('expiration', 'N/A')}
• Premium: ${options_data.get('premium', 0):.2f}
• Max Profit: ${options_data.get('max_profit', 0):.2f}
• Max Risk: ${options_data.get('max_risk', 0):.2f}
• Risk/Reward: 1:{options_data.get('risk_reward_ratio', 0):.1f}

**Greeks Analysis:**
• Delta: {options_data.get('delta', 0):.3f} (${options_data.get('delta', 0) * 100:.2f} per $1 move)
• Gamma: {options_data.get('gamma', 0):.4f}
• Theta: -${options_data.get('theta', 0):.2f}/day
• Vega: ${options_data.get('vega', 0):.2f} per 1% IV
• IV: {options_data.get('iv', 0):.1f}% (Rank: {options_data.get('iv_rank', 0):.0f}%)

**Position Sizing:**
• Suggested allocation: {options_data.get('position_size_pct', 0):.1f}% of portfolio
• Number of contracts: {options_data.get('contracts', 0)}
• Stop loss: ${options_data.get('stop_loss', 0):.2f}

**Entry Conditions:**
"""
        
        for condition in options_data.get('entry_conditions', []):
            response += f"• {condition}\n"
            
        return response
    
    @staticmethod
    def format_technical_confluence(data: Dict[str, Any]) -> str:
        """
        Format technical confluence analysis
        """
        symbol = data.get('symbol', 'N/A')
        
        response = f"""
🔍 **Technical Confluence Analysis for {symbol}**

**Fibonacci Retracements:**
• 23.6%: ${data.get('fib_236', 0):.2f}
• 38.2%: ${data.get('fib_382', 0):.2f}
• 50.0%: ${data.get('fib_500', 0):.2f}
• 61.8%: ${data.get('fib_618', 0):.2f} (Golden Ratio)

**Support Levels:**
"""
        for support in data.get('support_levels', [])[:3]:
            response += f"• ${support['price']:.2f} ({support['strength']} - {support['description']})\n"
            
        response += "\n**Resistance Levels:**\n"
        for resistance in data.get('resistance_levels', [])[:3]:
            response += f"• ${resistance['price']:.2f} ({resistance['strength']} - {resistance['description']})\n"
            
        response += f"""
            
**MACD Analysis:**
• MACD Line: {data.get('macd', 0):.3f}
• Signal Line: {data.get('macd_signal', 0):.3f}
• Histogram: {data.get('macd_histogram', 0):.3f}
• Signal: {data.get('macd_signal_type', 'N/A')}

**Bollinger Bands:**
• Upper Band: ${data.get('bb_upper', 0):.2f}
• Middle Band: ${data.get('bb_middle', 0):.2f}
• Lower Band: ${data.get('bb_lower', 0):.2f}
• Width: ${data.get('bb_width', 0):.2f}

**Confluence Zone:** ${data.get('confluence_zone_low', 0):.2f} - ${data.get('confluence_zone_high', 0):.2f}
• Strength: {data.get('confluence_strength', 'N/A')}/5
• Trigger: {data.get('confluence_trigger', 'N/A')}
"""
        return response
    
    @staticmethod
    def format_watchlist(stocks: List[Dict[str, Any]]) -> str:
        """
        Format daily watchlist with catalysts
        """
        response = f"""
📋 **Daily Watchlist** ({datetime.now().strftime('%B %d, %Y')})

**Strong Catalyst Plays:**
"""
        for stock in stocks:
            emoji = "🚀" if stock.get('signal') == 'bullish' else "⚠️" if stock.get('signal') == 'bearish' else "👀"
            response += f"""
{emoji} **{stock.get('symbol', 'N/A')}** - ${stock.get('price', 0):.2f} ({'+' if stock.get('change_pct', 0) >= 0 else ''}{stock.get('change_pct', 0):.2f}%)
• Catalyst: {stock.get('catalyst', 'N/A')}
• Setup: {stock.get('setup', 'N/A')}
• Target: ${stock.get('target', 0):.2f} | Stop: ${stock.get('stop', 0):.2f}
• Risk/Reward: 1:{stock.get('risk_reward', 0):.1f}
"""
        return response
    
    @staticmethod
    def format_trade_review(performance: Dict[str, Any]) -> str:
        """
        Format weekly trade performance review
        """
        response = f"""
📈 **Weekly Trade Review** (Week of {datetime.now().strftime('%B %d, %Y')})

**Performance Summary:**
• Total Trades: {performance.get('total_trades', 0)}
• Winners: {performance.get('winners', 0)} ({performance.get('win_rate', 0):.1f}%)
• Average Winner: +{performance.get('avg_winner', 0):.2f}%
• Average Loser: {performance.get('avg_loser', 0):.2f}%
• Net P&L: {'🟢' if performance.get('net_pnl', 0) > 0 else '🔴'} {performance.get('net_pnl', 0):.2f}%

**Best Trades:**
"""
        for trade in performance.get('best_trades', [])[:3]:
            response += f"• {trade['symbol']}: +{trade['return']:.2f}% ({trade['strategy']})\n"
            
        response += "\n**Areas for Improvement:**\n"
        for area in performance.get('improvements', []):
            response += f"• {area}\n"
            
        response += "\n**Next Week Focus:**\n"
        for focus in performance.get('next_week_focus', []):
            response += f"• {focus}\n"
            
        return response