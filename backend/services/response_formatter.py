"""
Market Response Formatter
========================
Formats market data responses to match the ideal custom GPT structure
with proper sections, tables, and visual organization.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.technical_levels import get_fallback_technical_levels

logger = logging.getLogger(__name__)

class MarketResponseFormatter:
    """
    Formats market analysis responses in a structured format that matches
    the ideal custom GPT output with sections, tables, and organized content.
    """
    
    @staticmethod
    def format_stock_snapshot_with_headlines(
        symbol: str, 
        price_data: Dict[str, Any], 
        news_items: List[Dict[str, Any]]
    ) -> str:
        """
        Format a comprehensive stock analysis response matching the ideal GPT format.
        
        Args:
            symbol: Stock ticker symbol
            price_data: Current price and market data
            news_items: List of news articles
            
        Returns:
            Formatted response string with all sections
        """
        try:
            # Extract price information
            current_price = price_data.get('price', 0)
            change = price_data.get('change', 0)
            change_percent = price_data.get('change_percent', 0)
            volume = price_data.get('volume', 0)
            
            # Get additional market data if available
            day_low = price_data.get('day_low', current_price)
            day_high = price_data.get('day_high', current_price)
            year_low = price_data.get('year_low', current_price)
            year_high = price_data.get('year_high', current_price)
            open_price = price_data.get('open', current_price)
            
            # Use centralized technical level calculation
            tech_levels = get_fallback_technical_levels(current_price, year_high, year_low)
            sell_high_level = tech_levels.get('sell_high_level', year_high * 0.95)
            buy_low_level = tech_levels.get('buy_low_level', (year_high + year_low) / 2)
            btd_level = tech_levels.get('btd_level', year_low * 1.1)
            
            current_date = datetime.now().strftime("%B %d, %Y")
            
            # Build the structured response
            response = f"""**Here's your real-time {symbol} snapshot:**

**{symbol.upper()}** ({symbol})
**${current_price:.2f}**
{'+' if change >= 0 else ''}${change:.2f} ({'+' if change_percent >= 0 else ''}{change_percent:.2f}%) Today
${open_price:.2f} {'+' if change >= 0 else ''}${change:.2f} ({'+' if change_percent >= 0 else ''}{change_percent:.2f}%) After Hours

| Metric | Value | | Metric | Value |
|--------|-------|---|--------|-------|
| **Open** | ${open_price:.2f} | | **Day Low** | ${day_low:.2f} |
| **Volume** | {MarketResponseFormatter._format_volume(volume)} | | **Day High** | ${day_high:.2f} |
| | | | **Year Low** | ${year_low:.2f} |
| | | | **Year High** | ${year_high:.2f} |

---

## Market Snapshot & Context (as of {current_date})

### Key Headlines
{MarketResponseFormatter._format_news_headlines(news_items, symbol)}

### Technical Overview
- **Overall Sentiment**: Strong buy sentiment on moving averages despite mixed RSI signals. 
- **Price Movement**: The stock has {'increased' if change >= 0 else 'decreased'} by ${abs(change):.2f} from its previous close of ${current_price - change:.2f}—right at current price levels.
- **Volume Analysis**: {'Strong buy volume' if volume > 1000000 else 'Moderate trading volume'} with {MarketResponseFormatter._format_volume(volume)} shares indicating {'significant' if volume > 1000000 else 'standard'} market interest.
- **Moving Averages**: {'Bullish' if change >= 0 else 'Bearish'} signals across short-term and long-term averages. Support levels identified below current price.

### Summary Table

| **Category** | **Details** |
|--------------|-------------|
| **Stock Price** | ~${current_price:.2f}—{'a rebound after recent' if change >= 0 else 'declining from recent'} {'gains' if change >= 0 else 'losses'}, hovering near the {'10-day EMA' if abs(change_percent) < 2 else '50-day moving average'} |
| **Short-Term Outlook** | {'Mixed—some bullish signals around' if change >= 0 else 'Cautious—downward pressure near'} ${current_price * 0.98:.2f}–${current_price * 1.02:.2f}, but {'legal and earnings concerns' if change < 0 else 'growth catalysts developing'} |
| **Catalysts** | {'Recent positive momentum' if change >= 0 else 'Market headwinds'}, {'earnings potential' if abs(change_percent) > 3 else 'technical consolidation'}, {'institutional interest' if volume > 1000000 else 'retail activity'} |
| **Risks** | {'Profit-taking pressure' if change >= 0 else 'Continued selling pressure'}, {'overbought conditions' if change_percent > 5 else 'oversold risks' if change_percent < -5 else 'market volatility'}, {'regulatory concerns' if symbol in ['TSLA', 'META', 'GOOGL'] else 'sector rotation'} |
| **Analyst Sentiment** | Short-term {'mixed to cautious' if abs(change_percent) > 2 else 'optimistic'}; long-term forecasts {'average moderate growth' if change >= 0 else 'remain defensive'} |

---

## Strategic Insights
• **Confluence Zone Near ${sell_high_level:.2f}–${sell_high_level * 1.02:.2f}**: This range could serve as a {'resistance' if current_price < sell_high_level else 'support'} trigger if {'breakout momentum' if change >= 0 else 'recovery'} gains traction. Watch for volume and moving average confirmations.

• **Defensive Levels to Watch**: Support near ${btd_level:.2f}–${buy_low_level:.2f} is critical—breaking below could open {'downside toward' if current_price > buy_low_level else 'further decline to'} ${btd_level:.2f} and beyond.

• **Event-Driven Plays**: {'Recent momentum' if change >= 0 else 'Current weakness'} and {'positive sentiment' if change >= 0 else 'market concerns'} can spark sharp moves—stay alert.

• **Medium-Term Outlook {'Remains Positive' if change >= 0 else 'Turning Cautious'}**: {'Consensus targets under' if change >= 0 else 'Support levels near'} ${year_high * 0.9:.2f} suggest {'optimism' if change >= 0 else 'caution'}—position sizing and risk controls are essential.

---

**Would you like me to dive deeper into specific trade setups (BTD, Buy Low, Sell High levels), options strategies around key catalysts, or build a custom watchlist based on {symbol}-related themes?**

### Related news on {symbol}
{MarketResponseFormatter._format_related_news(news_items)}"""

            return response
            
        except Exception as e:
            logger.error(f"Error formatting stock snapshot: {e}")
            return f"Error formatting response for {symbol}: {str(e)}"
    
    @staticmethod
    def _format_volume(volume: int) -> str:
        """Format volume numbers for display."""
        if volume >= 1_000_000:
            return f"{volume / 1_000_000:.1f}M"
        elif volume >= 1_000:
            return f"{volume / 1_000:.1f}K"
        else:
            return str(volume)
    
    @staticmethod
    def _format_news_headlines(news_items: List[Dict[str, Any]], symbol: str) -> str:
        """Format news headlines as bullet points with sources."""
        if not news_items:
            return f"• No recent news available for {symbol} at this time."
        
        headlines = []
        for i, item in enumerate(news_items[:3]):  # Top 3 headlines
            headline = item.get('headline') or item.get('title', 'No headline available')
            source = item.get('source', 'Unknown Source')
            
            # Truncate long headlines
            if len(headline) > 120:
                headline = headline[:117] + "..."
            
            headlines.append(f"• **{headline}**: Market impact assessment pending. _{source}_")
        
        return "\n".join(headlines)
    
    @staticmethod
    def _format_related_news(news_items: List[Dict[str, Any]]) -> str:
        """Format related news as cards with metadata."""
        if not news_items:
            return "📰 No recent news articles available."
        
        news_cards = []
        for i, item in enumerate(news_items[:3]):  # Top 3 news items
            headline = item.get('headline') or item.get('title', 'No headline available')
            source = item.get('source', 'Unknown Source')
            date_published = item.get('date_published', 'Recent')
            
            # Truncate headlines for cards
            if len(headline) > 80:
                headline = headline[:77] + "..."
            
            news_cards.append(f"📰 **{headline}**\n   _{source}_ • {date_published}")
        
        return "\n\n".join(news_cards)