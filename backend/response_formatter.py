"""
Response Formatter for G'sves Market Insights
Structures market data into professional analysis format
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import json


class DisclaimerManager:
    """Manages disclaimer addition to prevent duplicates"""
    _session_disclaimers = set()  # Track per session
    
    @staticmethod
    def get_disclaimer(response_type: str, session_id: str = "default") -> str:
        """Get appropriate disclaimer if not already shown"""
        key = f"{session_id}:{response_type}"
        
        # Only show each disclaimer type once per session
        if key in DisclaimerManager._session_disclaimers:
            return ""
            
        DisclaimerManager._session_disclaimers.add(key)
        
        disclaimers = {
            "trading": "\n\n⚠️ **Disclaimer**: Not financial advice. Past performance does not guarantee future results. Trade at your own risk.",
            "options": "\n\n⚠️ **Options Risk**: Options involve risk and are not suitable for all investors. May result in loss of entire investment.",
            "general": "\n\n💡 **Note**: For educational purposes only. Consult a licensed financial advisor before making investment decisions."
        }
        
        # Map response types to disclaimer types
        type_map = {
            "snapshot": "trading",
            "options": "options",
            "watchlist": "trading",
            "trade_review": "general",
            "market_brief": "general"
        }
        
        disclaimer_type = type_map.get(response_type, "general")
        return disclaimers.get(disclaimer_type, "")
    
    @staticmethod
    def reset_session(session_id: str = "default"):
        """Reset disclaimers for new session"""
        DisclaimerManager._session_disclaimers = {
            k for k in DisclaimerManager._session_disclaimers 
            if not k.startswith(f"{session_id}:")
        }


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
    def generate_tailored_suggestions(tool_result: dict) -> List[str]:
        """
        Generate two dynamic, tailored suggestions based on technical analysis.
        Implements Day 3.2 of integration plan.
        """
        suggestions = []
        
        try:
            # Extract relevant data
            symbol = tool_result.get("symbol", "Stock")
            price_data = tool_result.get("price_data", {})
            technical_levels = tool_result.get("technical_levels", {})
            
            current_price = price_data.get("price", price_data.get("last", 0))
            change_percent = price_data.get("change_percent", price_data.get("change_pct", 0))
            
            # Get technical levels
            sell_high_level = technical_levels.get("sell_high_level", 0)  # Sell High
            buy_low_level = technical_levels.get("buy_low_level", 0)  # Buy Low
            btd_level = technical_levels.get("btd_level", 0)  # Buy the Dip
            retest_level = technical_levels.get("retest_level", 0)  # Retest
            
            # Get advanced TA if available
            fib_levels = technical_levels.get("fib_levels", {})
            volume_profile = technical_levels.get("volume_profile", {})
            calc_method = technical_levels.get("calculation_method", "simple")
            
            # Suggestion 1: Entry/Exit based on price position
            if current_price > 0:
                if current_price > sell_high_level and sell_high_level > 0:
                    # Price above SE (Sell High) - momentum play
                    if fib_levels and "fib_1618" in fib_levels:
                        target = fib_levels["fib_1618"]
                        suggestions.append(f"Consider momentum trade: {symbol} breaking above Sell High level (${sell_high_level:.2f}). Target Fibonacci extension at ${target:.2f}")
                    else:
                        suggestions.append(f"Monitor {symbol} for continuation above Sell High level (${sell_high_level:.2f}). Consider trailing stop at ${buy_low_level:.2f}")
                
                elif current_price < btd_level and btd_level > 0:
                    # Price near BTD (Buy the Dip) - deep value opportunity
                    if volume_profile and volume_profile.get("support"):
                        support = volume_profile["support"]
                        suggestions.append(f"Value opportunity: {symbol} approaching BTD (Buy the Dip) level (${btd_level:.2f}) with volume support at ${support:.2f}")
                    else:
                        suggestions.append(f"Deep value alert: {symbol} near BTD level (${btd_level:.2f}). Consider scaling in with 30% position")
                
                elif buy_low_level > 0 and sell_high_level > 0 and buy_low_level < current_price < sell_high_level:
                    # Price in swing trade zone
                    if fib_levels and "fib_382" in fib_levels:
                        fib_382 = fib_levels["fib_382"]
                        suggestions.append(f"Swing trade setup: {symbol} between Buy Low (${buy_low_level:.2f}) and Sell High (${sell_high_level:.2f}). Watch Fibonacci 38.2% at ${fib_382:.2f}")
                    else:
                        suggestions.append(f"Consolidation zone: {symbol} between ${buy_low_level:.2f}-${sell_high_level:.2f}. Wait for directional breakout")
            
            # Suggestion 2: Risk management based on volatility and technicals
            if change_percent != 0:
                volatility = abs(change_percent)
                
                if volatility > 5:
                    # High volatility - tighten risk
                    stop_distance = current_price * 0.03  # 3% stop for volatile stocks
                    suggestions.append(f"High volatility ({volatility:.1f}% move): Use tight 3% stop-loss at ${(current_price - stop_distance):.2f}")
                
                elif volatility < 2:
                    # Low volatility - potential breakout
                    if calc_method == "advanced" and technical_levels.get("ma_20"):
                        ma_20 = technical_levels["ma_20"]
                        if current_price > ma_20:
                            suggestions.append(f"Low volatility squeeze: {symbol} coiling above 20-MA (${ma_20:.2f}). Breakout potential increasing")
                        else:
                            suggestions.append(f"Range-bound action: {symbol} below 20-MA (${ma_20:.2f}). Consider selling covered calls")
                    else:
                        suggestions.append(f"Low volatility environment: Consider iron condor or butterfly spread for {symbol}")
                
                else:
                    # Normal volatility
                    if technical_levels.get("ma_50") and technical_levels.get("ma_200"):
                        ma_50 = technical_levels["ma_50"]
                        ma_200 = technical_levels["ma_200"]
                        if ma_50 > ma_200:
                            suggestions.append(f"Bullish trend intact: 50-MA (${ma_50:.2f}) above 200-MA (${ma_200:.2f}). Hold with trailing stop")
                        else:
                            suggestions.append(f"Caution: 50-MA (${ma_50:.2f}) below 200-MA (${ma_200:.2f}). Consider reducing position size")
                    else:
                        suggestions.append(f"Standard risk management: Use 5% position sizing with stop at ${(current_price * 0.95):.2f}")
            
            # Fallback suggestions if none generated
            if len(suggestions) == 0:
                if buy_low_level > 0 and sell_high_level > 0:
                    suggestions.append(f"Monitor {symbol} for entry near support at ${buy_low_level:.2f}")
                    suggestions.append(f"Set price alerts at key levels: ${btd_level:.2f} (buy the dip) and ${sell_high_level:.2f} (sell high)")
                else:
                    suggestions.append(f"Analyze {symbol} technical setup for optimal entry points")
                    suggestions.append(f"Implement proper position sizing based on account risk tolerance")
            
            # Ensure we have exactly 2 suggestions
            if len(suggestions) == 1:
                if buy_low_level > 0:
                    suggestions.append(f"Track {symbol} daily volume for accumulation patterns above ${buy_low_level:.2f}")
                else:
                    suggestions.append(f"Monitor {symbol} for technical breakout signals")
            elif len(suggestions) > 2:
                suggestions = suggestions[:2]
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error generating tailored suggestions: {e}")
            # Fallback to generic suggestions
            suggestions = [
                "Monitor key technical levels for entry opportunities",
                "Implement proper position sizing based on account risk tolerance"
            ]
        
        return suggestions
    
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
        btd = data.get('btd_level', 'N/A')  # Buy the Dip
        buy_low = data.get('buy_low_level', 'N/A')  # Buy Low
        se = data.get('sell_high_level', 'N/A')  # Sell High
        retest = data.get('retest_level', 'N/A')  # Retest
        
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
• **Buy the Dip (BTD):** ${btd} - Strong support near 200-day MA
• **Buy Low:** ${buy_low} - Consolidation zone, 50-day MA confluence  
• **Sell High:** ${se} - Momentum exit, resistance zone
• **Retest:** ${retest} - Previous resistance turned support

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
            response += f"• ⚠️ Trading below BTD - potential accumulation zone\n"
        elif price > qe:
            response += f"• 🚀 Trading above Sell High - momentum continuation likely\n"
        else:
            response += f"• 📍 Trading in consolidation between Buy Low and Sell High\n"
            
        return response

    @staticmethod
    def format_stock_snapshot_with_headlines(symbol: str,
                                             price_data: Dict[str, Any],
                                             news: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Format a rich, structured stock snapshot with tables and proper markdown.
        Matches the ideal format with large price display and organized sections.
        """
        company = price_data.get('company_name', symbol.upper())
        price = price_data.get('price') or price_data.get('last') or 0
        change = price_data.get('change', price_data.get('change_abs', 0)) or 0
        change_pct = price_data.get('change_percent', price_data.get('change_pct', 0)) or 0
        open_px = price_data.get('open', 0)
        day_low = price_data.get('day_low', price_data.get('low', 0))
        day_high = price_data.get('day_high', price_data.get('high', 0))
        prev_close = price_data.get('previous_close', price_data.get('prev_close', 0))
        wk_low = price_data.get('week52_low') or price_data.get('year_low') or 0
        wk_high = price_data.get('week52_high') or price_data.get('year_high') or 0
        volume = price_data.get('volume', 0)
        avg_volume = price_data.get('avg_volume', 0)
        market_cap = price_data.get('market_cap', 0)
        pe_ratio = price_data.get('pe_ratio', 0)

        timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p ET')
        
        # Format volume for display
        def format_number(num):
            if num >= 1_000_000_000:
                return f"{num/1_000_000_000:.2f}B"
            elif num >= 1_000_000:
                return f"{num/1_000_000:.2f}M"
            elif num >= 1_000:
                return f"{num/1_000:.0f}K"
            return str(num)

        # Main header with large price display
        response = f"""## HERE'S YOUR REAL-TIME {symbol.upper()} SNAPSHOT

### **{company}** ({symbol.upper()})
**${price:,.2f}**
{'+' if change >= 0 else ''}{change:,.2f} ({'+' if change_pct >= 0 else ''}{change_pct:.2f}%) Today

---

## Market Snapshot & Context
*as of {timestamp}*

| Metric | Value | | Metric | Value |
|--------|-------|---|--------|-------|
| **Open** | ${open_px:,.2f} | | **Day Low** | ${day_low:,.2f} |
| **Previous Close** | ${prev_close:,.2f} | | **Day High** | ${day_high:,.2f} |
| **Volume** | {format_number(volume)} | | **52W Low** | ${wk_low:,.2f} |
| **Avg Volume** | {format_number(avg_volume) if avg_volume else 'N/A'} | | **52W High** | ${wk_high:,.2f} |"""

        # Add market cap and PE if available
        if market_cap or pe_ratio:
            response += f"""
| **Market Cap** | {format_number(market_cap) if market_cap else 'N/A'} | | **P/E Ratio** | {pe_ratio:.2f if pe_ratio else 'N/A'} |"""

        response += "\n\n---\n\n"

        # Key Headlines section with better formatting
        response += "## Key Headlines\n\n"
        if news and len(news) > 0:
            for i, item in enumerate(news[:5], 1):
                title = item.get('title') or item.get('headline') or ''
                source = item.get('source', 'News')
                published = item.get('published_at', '')
                
                # Clean up the title
                if title:
                    # Add bullet with number and bold headline
                    response += f"**{i}. {title}**\n"
                    response += f"   *{source}*"
                    if published:
                        response += f" • {published[:10]}"
                    response += "\n\n"
        else:
            response += "*No recent news available for this symbol*\n\n"

        response += "---\n\n"

        # Technical Overview section
        response += "## Technical Overview\n\n"
        
        # Price position analysis
        if wk_low and wk_high and wk_high > wk_low:
            position_pct = ((price - wk_low) / (wk_high - wk_low)) * 100
            if position_pct > 75:
                strength = "**Strong** - Near 52-week highs"
            elif position_pct > 50:
                strength = "**Moderate** - Above mid-range"
            elif position_pct > 25:
                strength = "**Weak** - Below mid-range"
            else:
                strength = "**Very Weak** - Near 52-week lows"
            
            response += f"- **Price Position**: {strength} ({position_pct:.1f}% of 52W range)\n"
        
        # Volume analysis
        if volume and avg_volume and avg_volume > 0:
            volume_ratio = volume / avg_volume
            if volume_ratio > 2:
                vol_signal = "**Extremely High** volume (unusual activity)"
            elif volume_ratio > 1.5:
                vol_signal = "**High** volume (increased interest)"
            elif volume_ratio > 0.7:
                vol_signal = "**Normal** volume"
            else:
                vol_signal = "**Low** volume (reduced activity)"
            
            response += f"- **Volume Analysis**: {vol_signal} - {volume_ratio:.1f}x average\n"
        
        # Momentum
        if change_pct != 0:
            if abs(change_pct) > 5:
                momentum = "**Strong**" if change_pct > 0 else "**Sharp decline**"
            elif abs(change_pct) > 2:
                momentum = "**Moderate**" if change_pct > 0 else "**Moderate decline**"
            else:
                momentum = "**Mild**" if change_pct > 0 else "**Mild decline**"
            
            response += f"- **Today's Momentum**: {momentum} move of {change_pct:+.2f}%\n"

        response += "\n---\n\n"

        # Summary Analysis Table
        response += "## Summary Analysis\n\n"
        response += "| Category | Details |\n"
        response += "|----------|----------|\n"
        response += f"| **Current Status** | ${price:,.2f} ({change_pct:+.2f}% today) |\n"
        response += f"| **Trading Range** | ${day_low:,.2f} - ${day_high:,.2f} (Day) |\n"
        response += f"| **52-Week Range** | ${wk_low:,.2f} - ${wk_high:,.2f} |\n"
        response += f"| **Volume Trend** | {format_number(volume)} vs {format_number(avg_volume)} avg |\n"
        
        # Market sentiment
        if change_pct > 2:
            sentiment = "Bullish momentum"
        elif change_pct < -2:
            sentiment = "Bearish pressure"
        else:
            sentiment = "Neutral consolidation"
        response += f"| **Market Sentiment** | {sentiment} |\n"

        return response

    @staticmethod
    def format_stock_snapshot_ideal(symbol: str,
                                    company_name: str,
                                    price_data: Dict[str, Any],
                                    news: Optional[List[Dict[str, Any]]] = None,
                                    technical_levels: Optional[Dict[str, Any]] = None,
                                    after_hours: Optional[Dict[str, Any]] = None) -> str:
        """
        Format response to match ideal format from screenshots.
        Chart visualization is handled by frontend TradingView component.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Extract price data
        price = price_data.get('price') or price_data.get('last') or 0
        change = price_data.get('change', price_data.get('change_abs', 0)) or 0
        change_pct = price_data.get('change_percent', price_data.get('change_pct', 0)) or 0
        open_px = price_data.get('open', 0)
        day_low = price_data.get('day_low', price_data.get('low', 0))
        day_high = price_data.get('day_high', price_data.get('high', 0))
        prev_close = price_data.get('previous_close', price_data.get('prev_close', 0))
        year_low = price_data.get('week52_low') or price_data.get('year_low') or 0
        year_high = price_data.get('week52_high') or price_data.get('year_high') or 0
        volume = price_data.get('volume', 0)
        
        def fmt_volume(v: float) -> str:
            try:
                v = float(v)
            except:
                return str(v)
            if v >= 1_000_000_000:
                return f"{v/1_000_000_000:.2f}B"
            if v >= 1_000_000:
                return f"{v/1_000_000:.1f}M"
            if v >= 1_000:
                return f"{v/1_000:.0f}K"
            return f"{v:,.0f}"
        
        # Start with header
        response = f"## Here's your real-time {company_name} snapshot:\n\n"
        
        # Price section with company name
        response += f"**{company_name} ({symbol})**\n"
        response += f"# ${price:,.2f}\n"
        response += f"{'-' if change < 0 else ''}${abs(change):.2f} ({change_pct:+.2f}%) Today\n"
        
        # After-hours if available
        if after_hours and after_hours.get('price'):
            ah_price = after_hours.get('price', 0)
            ah_change = after_hours.get('change', 0)
            ah_change_pct = after_hours.get('change_percent', 0)
            response += f"${ah_price:,.2f} {ah_change:+.2f} ({ah_change_pct:+.2f}%) After Hours\n"
        
        response += "\n"
        
        # Market data grid (chart is handled by frontend)
        response += "| | | |\n"
        response += "|---|---|---|\n"
        response += f"| **Open** | ${open_px:,.2f} | **Day Low** | ${day_low:,.2f} | **Year Low** | ${year_low:,.2f} |\n"
        response += f"| **Volume** | {fmt_volume(volume)} | **Day High** | ${day_high:,.2f} | **Year High** | ${year_high:,.2f} |\n\n"
        
        # Market Snapshot & Context
        timestamp = datetime.now().strftime('%B %d, %Y')
        response += f"### Market Snapshot & Context (as of {timestamp})\n\n"
        
        # Key Headlines
        response += "### Key Headlines\n"
        if news and len(news) > 0:
            for item in news[:3]:
                headline = item.get('title') or item.get('headline') or ''
                source = item.get('source', '')
                if headline:
                    response += f"• **{headline}** — {source}\n"
        else:
            response += "• No recent news available for this symbol\n"
        response += "\n"
        
        # Technical Overview & Forecasts (dynamic based on technical data)
        response += "### Technical Overview & Forecasts\n"
        response += MarketResponseFormatter._generate_technical_overview(
            symbol, price, change_pct, technical_levels, price_data
        )
        response += "\n"
        
        # Broader Trends & Forecasts
        response += "### Broader Trends & Forecasts\n"
        response += MarketResponseFormatter._generate_broader_trends(
            symbol, price, technical_levels, price_data
        )
        response += "\n"
        
        # Summary Table
        response += "### Summary Table\n\n"
        response += "| **Category** | **Details** |\n"
        response += "|---|---|\n"
        
        # Generate dynamic summary based on data
        price_desc = f"~${price:,.0f}—{'rebound' if change > 0 else 'decline'} after recent {'gains' if change_pct > 2 else 'moves'}"
        response += f"| **Stock Price** | {price_desc} |\n"
        
        outlook = MarketResponseFormatter._determine_outlook(change_pct, technical_levels)
        response += f"| **Short-Term Outlook** | {outlook} |\n"
        
        catalysts = MarketResponseFormatter._identify_catalysts(symbol, news)
        response += f"| **Catalysts** | {catalysts} |\n"
        
        risks = MarketResponseFormatter._identify_risks(price, technical_levels)
        response += f"| **Risks** | {risks} |\n"
        
        sentiment = MarketResponseFormatter._determine_sentiment(change_pct, price, technical_levels)
        response += f"| **Analyst Sentiment** | {sentiment} |\n\n"
        
        # Strategic Insights (replacing our 2 tailored suggestions)
        response += "### Strategic Insights\n"
        
        # Add LLM insight if available (Day 4.2)
        llm_insight = price_data.get('llm_insight')
        if llm_insight:
            response += f"**AI Analysis**: {llm_insight}\n\n"
        
        insights = MarketResponseFormatter._generate_strategic_insights(
            symbol, price, technical_levels, price_data
        )
        for insight in insights:
            response += f"• {insight}\n"
        response += "\n"
        
        # Call to action
        response += f"Would you like me to dive deeper into **specific trade setups** (BTD, Buy Low, Sell High, Retest levels), "
        response += f"**options strategies** around key catalysts (e.g., FSD release, Model Y L launch), "
        response += f"or build a **custom watchlist** based on {company_name}-related themes?\n"
        
        # Add disclaimer
        response += DisclaimerManager.get_disclaimer("snapshot")
        
        return response
    
    @staticmethod
    def _generate_technical_overview(symbol: str, price: float, change_pct: float, 
                                    technical_levels: dict, price_data: dict) -> str:
        """Generate technical overview section"""
        overview = ""
        
        # Determine momentum
        if change_pct > 2:
            momentum = "strong bullish momentum"
        elif change_pct > 0:
            momentum = "mild bullish sentiment"
        elif change_pct > -2:
            momentum = "mild bearish pressure"
        else:
            momentum = "strong bearish momentum"
        
        overview += f"{symbol} is showing {momentum}, trading at ${price:,.2f}. "
        
        if technical_levels:
            se = technical_levels.get('sell_high_level', 0)  # Sell High
            buy_low = technical_levels.get('buy_low_level', 0)  # Buy Low
            btd = technical_levels.get('btd_level', 0)  # Buy the Dip
            
            if se > 0 and price < se:
                overview += f"The stock is approaching resistance near ${se:,.0f} (Sell High level). "
            elif buy_low > 0 and price > buy_low:
                overview += f"Support is building around ${buy_low:,.0f} (Buy Low level). "
            
            # Add Fibonacci or MA analysis if available
            if technical_levels.get('ma_50') and technical_levels.get('ma_200'):
                ma_50 = technical_levels['ma_50']
                ma_200 = technical_levels['ma_200']
                if ma_50 > ma_200:
                    overview += "The 50-day MA remains above the 200-day MA, suggesting a long-term uptrend. "
                else:
                    overview += "The 50-day MA is below the 200-day MA, indicating potential long-term weakness. "
        
        # Add volume analysis
        avg_volume = price_data.get('avg_volume', 0)
        current_volume = price_data.get('volume', 0)
        if avg_volume > 0 and current_volume > avg_volume * 1.5:
            overview += "Volume is significantly above average, confirming the move. "
        
        return overview
    
    @staticmethod  
    def _generate_broader_trends(symbol: str, price: float, technical_levels: dict, price_data: dict) -> str:
        """Generate broader trends section"""
        trends = []
        
        # EV sector specific for TSLA
        if symbol == "TSLA":
            trends.append("• **EV Credit Expansion Risk**: Potential policy changes could impact EV tax credits")
            trends.append("• **FSD/Robotaxi Development**: Autonomous driving progress remains a key catalyst")
        
        # Generic trends based on technicals
        if technical_levels:
            if technical_levels.get('calculation_method') == 'advanced':
                trends.append(f"• **Medium-Term Outlook**: Fibonacci retracements suggest targets near key levels")
            else:
                trends.append(f"• **Medium-Term Outlook**: Technical indicators show mixed signals")
        
        # Long-term based on 52-week range
        year_high = price_data.get('week52_high', price_data.get('year_high', 0))
        year_low = price_data.get('week52_low', price_data.get('year_low', 0))
        if year_high > 0 and year_low > 0:
            range_position = (price - year_low) / (year_high - year_low)
            if range_position > 0.7:
                trends.append("• **Long-Term Position**: Trading in upper portion of 52-week range")
            elif range_position < 0.3:
                trends.append("• **Long-Term Position**: Near lower end of 52-week range")
            else:
                trends.append("• **Long-Term Position**: Mid-range consolidation within 52-week levels")
        
        return "\n".join(trends) if trends else "• Monitoring for emerging trend developments"
    
    @staticmethod
    def _determine_outlook(change_pct: float, technical_levels: dict) -> str:
        """Determine short-term outlook"""
        if abs(change_pct) < 1:
            base = "Mixed—sideways action"
        elif change_pct > 3:
            base = "Bullish—strong momentum"
        elif change_pct > 0:
            base = "Cautiously bullish"
        elif change_pct < -3:
            base = "Bearish—selling pressure"
        else:
            base = "Cautiously bearish"
        
        # Add technical context if available
        if technical_levels and technical_levels.get('calculation_method') == 'advanced':
            base += ", watching key Fibonacci levels"
        
        return base
    
    @staticmethod
    def _identify_catalysts(symbol: str, news: list) -> str:
        """Identify key catalysts from news or generate generic ones"""
        if news and len(news) > 0:
            # Extract catalysts from headlines
            catalysts = []
            for item in news[:2]:
                headline = item.get('title', item.get('headline', ''))
                if 'earnings' in headline.lower():
                    catalysts.append("earnings")
                elif 'product' in headline.lower() or 'launch' in headline.lower():
                    catalysts.append("product launches")
                elif 'deal' in headline.lower() or 'partner' in headline.lower():
                    catalysts.append("partnerships")
            
            if catalysts:
                return ", ".join(catalysts[:3])
        
        # Generic catalysts based on symbol
        if symbol == "TSLA":
            return "Model Y updates, FSD progress, robotaxi developments"
        else:
            return "Earnings reports, sector trends, market conditions"
    
    @staticmethod
    def _identify_risks(price: float, technical_levels: dict) -> str:
        """Identify key risks"""
        risks = []
        
        # Technical risks
        if technical_levels:
            ltb = technical_levels.get('ltb_level', 0)
            if ltb > 0 and price < ltb * 1.1:  # Within 10% of LTB
                risks.append("approaching deep support")
        
        # Generic market risks
        risks.append("market volatility")
        
        return ", ".join(risks) if risks else "Standard market risks"
    
    @staticmethod
    def _determine_sentiment(change_pct: float, price: float, technical_levels: dict) -> str:
        """Determine analyst sentiment"""
        if abs(change_pct) < 1:
            return "Neutral—wait for clearer signals"
        elif change_pct > 2:
            return "Bullish—momentum building"
        elif change_pct > 0:
            return "Cautiously optimistic"
        elif change_pct < -2:
            return "Bearish—risk management advised"
        else:
            return "Short-term mixed to cautious; long-term prospects under review"
    
    @staticmethod
    def _generate_strategic_insights(symbol: str, price: float, technical_levels: dict, price_data: dict) -> list:
        """Generate 4-5 strategic insights (replaces our 2 tailored suggestions)"""
        insights = []
        
        # Confluence zones based on technical levels
        if technical_levels:
            qe = technical_levels.get('qe_level', 0)
            st = technical_levels.get('st_level', 0)
            
            if qe > 0 and st > 0:
                insights.append(f"**Confluence Zone Near ${st:,.0f}–${qe:,.0f}**: This range could serve as a breakout trigger if volume confirms")
            
            # Support/Resistance
            if st > 0:
                insights.append(f"**Defensive Levels to Watch**: Support near ${st:,.0f} is critical—breaking below could trigger stops")
            
            # Fibonacci insights if advanced TA
            if technical_levels.get('fib_levels'):
                insights.append("**Fibonacci Retracements**: Key levels align with historical pivot points, watch for reactions")
        
        # Event-driven plays
        insights.append(f"**Event-Driven Plays**: Monitor upcoming catalysts for volatility expansion opportunities")
        
        # Outlook based on MAs
        if technical_levels and technical_levels.get('ma_50'):
            ma_50 = technical_levels['ma_50']
            if price > ma_50:
                insights.append(f"**Medium-Term Outlook Remains Constructive**: Price holding above 50-day MA at ${ma_50:,.0f}")
            else:
                insights.append(f"**Medium-Term Outlook Softening**: Price below 50-day MA at ${ma_50:,.0f} suggests caution")
        
        return insights[:5]  # Limit to 5 insights max
    
    @staticmethod
    def format_stock_snapshot_prototype(symbol: str,
                                        price_data: Dict[str, Any],
                                        news: Optional[List[Dict[str, Any]]] = None,
                                        technical_levels: Optional[Dict[str, Any]] = None,
                                        status_messages: Optional[List[str]] = None) -> str:
        """
        Compact snapshot that mirrors the prototype exactly:
        - HERE’S YOUR REAL‑TIME {SYMBOL} ({SYMBOL}) SNAPSHOT:
        - MARKET SNAPSHOT & CONTEXT (bullets)
        - KEY HEADLINES (bullets)
        - Optional TECHNICAL LEVELS (QE/ST/LTB)
        """
        price = price_data.get('price') or price_data.get('last') or 0
        change = price_data.get('change', price_data.get('change_abs', 0)) or 0
        change_pct = price_data.get('change_percent', price_data.get('change_pct', 0)) or 0
        open_px = price_data.get('open', 0)
        day_low = price_data.get('day_low', price_data.get('low', 0))
        day_high = price_data.get('day_high', price_data.get('high', 0))
        prev_close = price_data.get('previous_close', price_data.get('prev_close', 0))
        wk_low = price_data.get('week52_low') or price_data.get('year_low') or 0
        wk_high = price_data.get('week52_high') or price_data.get('year_high') or 0
        volume = price_data.get('volume', 0)

        timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p ET')

        def fmt_num(n: float) -> str:
            try:
                n = float(n)
            except Exception:
                return str(n)
            if n >= 1_000_000_000:
                return f"{n/1_000_000_000:.2f}B"
            if n >= 1_000_000:
                return f"{n/1_000_000:.2f}M"
            if n >= 1_000:
                return f"{n/1_000:.0f}K"
            return f"{n:,.0f}"

        # Title
        response = f"## HERE’S YOUR REAL‑TIME {symbol.upper()} ({symbol.upper()}) SNAPSHOT:\n\n"
        response += f"- Price: ${price:,.2f} ({change:+.2f}, {change_pct:+.2f}%)\n"

        # Market Snapshot
        response += f"\n### MARKET SNAPSHOT & CONTEXT (as of {timestamp})\n"
        response += f"- Open: ${open_px:,.2f} | Prev Close: ${prev_close:,.2f}\n"
        response += f"- Day Range: ${day_low:,.2f} – ${day_high:,.2f}\n"
        response += f"- Volume: {fmt_num(volume)}\n"
        if wk_low and wk_high:
            response += f"- 52W Range: ${wk_low:,.2f} – ${wk_high:,.2f}\n"

        # Key Headlines
        response += "\n### KEY HEADLINES\n"
        if news:
            for item in news[:3]:
                title = item.get('title') or item.get('headline') or ''
                source = item.get('source', 'News')
                if title:
                    response += f"- {title} — {source}\n"
        else:
            response += "- No recent news available for this symbol\n"
        
        # Status Messages (Day 4.1 - show timeout/error indicators)
        if status_messages:
            for status_msg in status_messages:
                if status_msg:
                    response += f"- {status_msg}\n"

        # Technical Levels (optional)
        if technical_levels:
            qe = technical_levels.get('qe_level') or technical_levels.get('quick_entry')
            st = technical_levels.get('st_level') or technical_levels.get('swing_trade')
            ltb = technical_levels.get('ltb_level') or technical_levels.get('load_the_boat')
            if any(x is not None for x in [qe, st, ltb]):
                response += "\n### TECHNICAL LEVELS\n"
                if qe is not None:
                    response += f"- QE Level: ${qe:,.2f}\n"
                if st is not None:
                    response += f"- ST Level: ${st:,.2f}\n"
                if ltb is not None:
                    response += f"- LTB Level: ${ltb:,.2f}\n"
        
        # Generate and add tailored suggestions (Day 3.2)
        # Build a tool_result dict for the suggestion generator
        tool_result = {
            "symbol": symbol,
            "price_data": price_data,
            "technical_levels": technical_levels or {}
        }
        
        suggestions = MarketResponseFormatter.generate_tailored_suggestions(tool_result)
        if suggestions:
            response += "\n### 💡 TAILORED SUGGESTIONS:\n"
            for i, suggestion in enumerate(suggestions[:2], 1):
                response += f"{i}. {suggestion}\n"

        # Add disclaimer if not already shown
        response += DisclaimerManager.get_disclaimer("snapshot")
        
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
        
        # Add disclaimer
        response += DisclaimerManager.get_disclaimer("market_brief")
        
        return response
    
    @staticmethod
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
        
        # Add disclaimer
        response += DisclaimerManager.get_disclaimer("options")
        
        return response
    
    @staticmethod
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
        # Add disclaimer
        response += DisclaimerManager.get_disclaimer("watchlist")
        
        return response
    
    @staticmethod
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
        
        # Add disclaimer
        response += DisclaimerManager.get_disclaimer("trade_review")
        
        return response
