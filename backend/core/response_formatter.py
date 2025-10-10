"""
Response Formatter for Voice Trading Assistant
Formats data for voice and text output
"""

from typing import Dict, Any, List, Optional
import json


class ResponseFormatter:
    """Formats responses for voice and text output."""
    
    @staticmethod
    def format_voice_response(data: Dict[str, Any], intent: str) -> str:
        """
        Format data for voice output.
        
        Args:
            data: Response data
            intent: Intent type for context
            
        Returns:
            Voice-optimized text string
        """
        if intent == "price-only":
            return ResponseFormatter._format_price_voice(data)
        elif intent == "news":
            return ResponseFormatter._format_news_voice(data)
        elif intent == "educational":
            return ResponseFormatter._format_educational_voice(data)
        elif intent == "technical":
            return ResponseFormatter._format_technical_voice(data)
        else:
            return ResponseFormatter._format_general_voice(data)
    
    @staticmethod
    def _format_price_voice(data: Dict[str, Any]) -> str:
        """Format price data for voice."""
        if "error" in data:
            return data["error"]
        
        symbol = data.get("symbol", "")
        price = data.get("price", 0)
        change = data.get("change", 0)
        change_pct = data.get("change_percent", 0)
        
        direction = "up" if change > 0 else "down" if change < 0 else "unchanged"
        
        return (
            f"{symbol} is currently trading at ${price:.2f}. "
            f"It's {direction} ${abs(change):.2f} or {abs(change_pct):.1f} percent today."
        )
    
    @staticmethod
    def _format_news_voice(data: Dict[str, Any]) -> str:
        """Format news data for voice."""
        news_items = data.get("news", [])
        symbol = data.get("symbol", "")
        
        if not news_items:
            return f"I don't have any recent news for {symbol}"
        
        response = f"Here's the latest news for {symbol}: "
        
        # Only read first 2 headlines for voice
        for item in news_items[:2]:
            title = item.get("title", "")
            response += f"{title}. "
        
        return response
    
    @staticmethod
    def _format_educational_voice(data: Dict[str, Any]) -> str:
        """Format educational content for voice."""
        title = data.get("title", "")
        content = data.get("content", "")
        
        if not content:
            return "I don't have information on that topic."
        
        # Simplify for voice - shorter sentences
        content = content.replace(". ", ". <break time='0.5s'/> ")
        
        return f"{title}. {content}"
    
    @staticmethod
    def _format_technical_voice(data: Dict[str, Any]) -> str:
        """Format technical analysis for voice."""
        symbol = data.get("symbol", "")
        analysis = data.get("analysis", {})
        
        if not analysis:
            return f"I don't have technical analysis for {symbol}"
        
        response = f"Technical analysis for {symbol}: "
        
        # Key metrics for voice
        if "trend" in analysis:
            response += f"The trend is {analysis['trend']}. "
        if "support" in analysis:
            response += f"Support at ${analysis['support']:.2f}. "
        if "resistance" in analysis:
            response += f"Resistance at ${analysis['resistance']:.2f}. "
        
        return response
    
    @staticmethod
    def _format_general_voice(data: Dict[str, Any]) -> str:
        """Format general response for voice."""
        if "message" in data:
            return data["message"]
        elif "response" in data:
            return data["response"]
        else:
            # Try to create a readable response from the data
            return ResponseFormatter._summarize_data(data)
    
    @staticmethod
    def _summarize_data(data: Dict[str, Any]) -> str:
        """Create a summary from arbitrary data."""
        if not data:
            return "I don't have information on that."
        
        # Extract key information
        summary_parts = []
        
        if "symbol" in data:
            summary_parts.append(f"For {data['symbol']}")
        
        if "price" in data:
            summary_parts.append(f"price is ${data['price']:.2f}")
        
        if "volume" in data:
            summary_parts.append(f"volume is {data['volume']:,}")
        
        if summary_parts:
            return ", ".join(summary_parts)
        else:
            return "Here's what I found: " + str(data)[:200]
    
    @staticmethod
    def format_json_response(data: Dict[str, Any]) -> str:
        """
        Format data as JSON for API responses.
        
        Args:
            data: Response data
            
        Returns:
            JSON string
        """
        return json.dumps(data, indent=2, default=str)
    
    @staticmethod
    def format_chart_command(symbol: str, action: str = "show") -> Dict[str, Any]:
        """
        Format chart display command.
        
        Args:
            symbol: Stock symbol
            action: Chart action (show, hide, update)
            
        Returns:
            Chart command dictionary
        """
        return {
            "type": "chart_command",
            "action": action,
            "symbol": symbol,
            "timestamp": None  # Will be set by caller
        }
    
    @staticmethod
    def format_error_response(error: str, user_friendly: bool = True) -> Dict[str, Any]:
        """
        Format error response.
        
        Args:
            error: Error message
            user_friendly: Whether to make message user-friendly
            
        Returns:
            Error response dictionary
        """
        if user_friendly:
            # Convert technical errors to user-friendly messages
            if "connection" in error.lower():
                message = "I'm having trouble connecting to the market data. Please try again."
            elif "not found" in error.lower():
                message = "I couldn't find that symbol. Please check and try again."
            elif "timeout" in error.lower():
                message = "The request took too long. Please try again."
            else:
                message = "Something went wrong. Please try again."
        else:
            message = error
        
        return {
            "error": True,
            "message": message,
            "technical_error": error
        }


# Export main class
__all__ = ['ResponseFormatter']