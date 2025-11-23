"""
Sentiment Scoring Service
Generates 0-100 sentiment scores for stocks based on multiple factors.

Inspired by StockWisp's sentiment scoring, enhanced for professional traders.
"""

from typing import Dict, Optional, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SentimentScorer:
    """
    Multi-factor sentiment scoring engine.

    Combines technical analysis, price momentum, news sentiment, and volume
    to generate a comprehensive 0-100 sentiment score.

    Score Interpretation:
    - 0-20: Very Bearish
    - 21-40: Bearish
    - 41-60: Neutral
    - 61-80: Bullish
    - 81-100: Very Bullish
    """

    # Weight distribution for multi-factor scoring
    WEIGHTS = {
        'price_momentum': 0.30,    # 30%
        'technical': 0.30,          # 30%
        'news_sentiment': 0.20,     # 20%
        'volume_trend': 0.20        # 20%
    }

    @classmethod
    def calculate_sentiment_score(
        cls,
        price_data: Dict,
        technical_indicators: Optional[Dict] = None,
        news_articles: Optional[List[Dict]] = None,
        volume_data: Optional[Dict] = None
    ) -> Dict:
        """
        Calculate comprehensive sentiment score (0-100).

        Args:
            price_data: Dictionary containing price info (current, change, changePercent)
            technical_indicators: Optional RSI, MACD, moving averages
            news_articles: Optional list of news articles with sentiment
            volume_data: Optional volume and volume trend info

        Returns:
            Dictionary with score, label, color, and component breakdown
        """
        try:
            # Calculate individual component scores
            momentum_score = cls._calculate_momentum_score(price_data)
            technical_score = cls._calculate_technical_score(technical_indicators)
            news_score = cls._calculate_news_score(news_articles)
            volume_score = cls._calculate_volume_score(volume_data)

            # Weighted composite score
            composite_score = (
                momentum_score * cls.WEIGHTS['price_momentum'] +
                technical_score * cls.WEIGHTS['technical'] +
                news_score * cls.WEIGHTS['news_sentiment'] +
                volume_score * cls.WEIGHTS['volume_trend']
            )

            # Round to integer
            final_score = round(composite_score)

            # Generate label and color
            label, color = cls._get_sentiment_label(final_score)

            return {
                'score': final_score,
                'label': label,
                'color': color,
                'components': {
                    'price_momentum': round(momentum_score),
                    'technical': round(technical_score),
                    'news_sentiment': round(news_score),
                    'volume_trend': round(volume_score)
                },
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error calculating sentiment score: {e}")
            return cls._default_sentiment()

    @classmethod
    def _calculate_momentum_score(cls, price_data: Dict) -> float:
        """
        Calculate price momentum score (0-100).

        Based on:
        - 1-day change percent
        - Direction and magnitude
        """
        if not price_data or 'changePercent' not in price_data:
            return 50.0  # Neutral default

        change_percent = price_data.get('changePercent', 0)

        # Map change percent to 0-100 scale
        # -10% -> 0, 0% -> 50, +10% -> 100
        # Using sigmoid-like function for smooth mapping
        if change_percent >= 10:
            return 100.0
        elif change_percent <= -10:
            return 0.0
        else:
            # Linear mapping: -10% to +10% -> 0 to 100
            score = 50 + (change_percent * 5)
            return max(0, min(100, score))

    @classmethod
    def _calculate_technical_score(cls, technical_indicators: Optional[Dict]) -> float:
        """
        Calculate technical indicator score (0-100).

        Based on:
        - RSI (Relative Strength Index)
        - MACD signal
        - Moving average crossovers
        """
        if not technical_indicators:
            return 50.0  # Neutral default

        scores = []

        # RSI Score (30 = oversold = 100, 70 = overbought = 0)
        if 'rsi' in technical_indicators:
            rsi = technical_indicators['rsi']
            if rsi is not None:
                # RSI: 0-30 = bullish (oversold), 30-70 = neutral, 70-100 = bearish (overbought)
                if rsi <= 30:
                    rsi_score = 100 - (rsi * 1.67)  # 0->100, 30->50
                elif rsi >= 70:
                    rsi_score = (100 - rsi) * 1.67  # 70->50, 100->0
                else:
                    rsi_score = 50 + ((50 - rsi) * 0.5)  # 30-70 maps to 40-60
                scores.append(rsi_score)

        # MACD Score
        if 'macd' in technical_indicators:
            macd_data = technical_indicators['macd']
            if macd_data and 'histogram' in macd_data:
                histogram = macd_data['histogram']
                # Positive histogram = bullish, negative = bearish
                if histogram > 0:
                    macd_score = 50 + min(histogram * 10, 50)  # Cap at 100
                else:
                    macd_score = 50 + max(histogram * 10, -50)  # Floor at 0
                scores.append(macd_score)

        # Moving Average Score (price above MA = bullish)
        if 'moving_averages' in technical_indicators:
            ma_data = technical_indicators['moving_averages']
            current_price = technical_indicators.get('current_price', 0)

            if current_price > 0:
                ma_scores = []

                # Check position relative to each MA
                for period in [20, 50, 200]:
                    ma_key = f'ma{period}'
                    if ma_key in ma_data and ma_data[ma_key]:
                        ma_value = ma_data[ma_key]
                        # Price above MA = bullish (>50), below = bearish (<50)
                        pct_diff = ((current_price - ma_value) / ma_value) * 100
                        ma_score = 50 + (pct_diff * 5)  # ±10% = ±50 points
                        ma_scores.append(max(0, min(100, ma_score)))

                if ma_scores:
                    scores.append(sum(ma_scores) / len(ma_scores))

        # Average all technical scores
        if scores:
            return sum(scores) / len(scores)

        return 50.0  # Neutral default

    @classmethod
    def _calculate_news_score(cls, news_articles: Optional[List[Dict]]) -> float:
        """
        Calculate news sentiment score (0-100).

        Based on:
        - Recent news article sentiment
        - Positive/negative keyword analysis
        """
        if not news_articles or len(news_articles) == 0:
            return 50.0  # Neutral default

        # Analyze recent news (last 24 hours most important)
        now = datetime.utcnow()
        sentiment_scores = []

        for article in news_articles[:10]:  # Analyze up to 10 recent articles
            # Simple keyword-based sentiment (can be enhanced with NLP)
            title = article.get('title', '').lower()
            summary = article.get('summary', '').lower()
            text = f"{title} {summary}"

            # Positive keywords
            positive_keywords = [
                'beats', 'exceeds', 'surges', 'rallies', 'gains', 'growth',
                'bullish', 'upgrade', 'outperform', 'strong', 'positive',
                'record', 'breakthrough', 'success', 'profit', 'revenue'
            ]

            # Negative keywords
            negative_keywords = [
                'misses', 'falls', 'drops', 'declines', 'plunges', 'losses',
                'bearish', 'downgrade', 'underperform', 'weak', 'negative',
                'concern', 'risk', 'warning', 'decline', 'loss'
            ]

            positive_count = sum(1 for word in positive_keywords if word in text)
            negative_count = sum(1 for word in negative_keywords if word in text)

            # Calculate article sentiment score
            if positive_count == 0 and negative_count == 0:
                article_score = 50  # Neutral
            else:
                # Range: all negative = 0, all positive = 100
                total = positive_count + negative_count
                article_score = (positive_count / total) * 100

            sentiment_scores.append(article_score)

        if sentiment_scores:
            return sum(sentiment_scores) / len(sentiment_scores)

        return 50.0  # Neutral default

    @classmethod
    def _calculate_volume_score(cls, volume_data: Optional[Dict]) -> float:
        """
        Calculate volume trend score (0-100).

        Based on:
        - Current volume vs average volume
        - Volume trend (increasing = buying pressure)
        """
        if not volume_data:
            return 50.0  # Neutral default

        current_volume = volume_data.get('current_volume', 0)
        avg_volume = volume_data.get('avg_volume', 0)

        if avg_volume == 0 or current_volume == 0:
            return 50.0  # Neutral default

        # Volume ratio: >1 = high volume, <1 = low volume
        volume_ratio = current_volume / avg_volume

        # Map to 0-100 scale
        # 0.5x avg = 25, 1x avg = 50, 2x avg = 75, 3x+ avg = 100
        if volume_ratio >= 3:
            return 100.0
        elif volume_ratio <= 0.5:
            return 25.0
        else:
            # Linear mapping
            score = 50 + ((volume_ratio - 1) * 25)
            return max(0, min(100, score))

    @classmethod
    def _get_sentiment_label(cls, score: int) -> tuple[str, str]:
        """
        Get sentiment label and color based on score.

        Returns:
            Tuple of (label, hex_color)
        """
        if score >= 81:
            return ('Very Bullish', '#10b981')  # Green
        elif score >= 61:
            return ('Bullish', '#84cc16')  # Light Green
        elif score >= 41:
            return ('Neutral', '#f59e0b')  # Orange
        elif score >= 21:
            return ('Bearish', '#f97316')  # Dark Orange
        else:
            return ('Very Bearish', '#ef4444')  # Red

    @classmethod
    def _default_sentiment(cls) -> Dict:
        """Return default neutral sentiment."""
        return {
            'score': 50,
            'label': 'Neutral',
            'color': '#f59e0b',
            'components': {
                'price_momentum': 50,
                'technical': 50,
                'news_sentiment': 50,
                'volume_trend': 50
            },
            'timestamp': datetime.utcnow().isoformat()
        }
