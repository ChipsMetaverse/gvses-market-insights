"""
Centralized technical level field management.
Handles the transition from deprecated QE/ST/LTB naming to actual level names.
"""

def normalize_technical_levels(levels: dict) -> dict:
    """
    Normalize technical level field names for consistency across all endpoints.
    
    The system now uses actual level names instead of deprecated abbreviations:
    - sell_high_level: Exit/profit-taking level (formerly QE)
    - buy_low_level: Entry point level (formerly ST)  
    - btd_level: Buy the Dip aggressive entry (formerly LTB)
    - retest_level: Previous resistance turned support
    
    Args:
        levels: Dictionary containing technical levels with any naming convention
        
    Returns:
        Dictionary with normalized field names
    """
    if not levels:
        return {}
        
    normalized = {}
    
    # Copy all original fields
    normalized.update(levels)
    
    # No legacy mapping needed - frontend uses actual names directly
    # Remove any deprecated fields if they exist
    for deprecated_field in ['qe_level', 'st_level', 'ltb_level']:
        normalized.pop(deprecated_field, None)
    
    return normalized


def get_fallback_technical_levels(current_price: float, year_high: float = None, year_low: float = None) -> dict:
    """
    Generate fallback technical levels when advanced calculation isn't available.
    
    Args:
        current_price: Current stock price
        year_high: 52-week high (optional)
        year_low: 52-week low (optional)
        
    Returns:
        Dictionary with calculated technical levels using actual names
    """
    # Use year data if available, otherwise estimate from current price
    if not year_high:
        year_high = current_price * 1.2
    if not year_low:
        year_low = current_price * 0.8
        
    return {
        'sell_high_level': round(year_high * 0.95, 2),  # Near resistance
        'buy_low_level': round((year_high + year_low) / 2, 2),  # Mid-range entry
        'btd_level': round(year_low * 1.1, 2),  # Aggressive buy zone
        'retest_level': round(current_price * 0.98, 2)  # Near current support
    }


def format_level_for_display(level_name: str) -> str:
    """
    Convert technical level field name to display label.
    
    Args:
        level_name: Field name (e.g., 'sell_high_level')
        
    Returns:
        Human-readable label (e.g., 'Sell High')
    """
    display_names = {
        'sell_high_level': 'Sell High',
        'buy_low_level': 'Buy Low',
        'btd_level': 'BTD',
        'retest_level': 'Retest'
    }
    return display_names.get(level_name, level_name)