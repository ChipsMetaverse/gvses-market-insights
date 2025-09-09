"""
OpenAI Realtime Agent Guardrails System
========================================
Implements safety measures and validation rules to prevent bad decisions,
infinite loops, and inappropriate responses. Based on agent training best practices.
"""

import re
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)


@dataclass
class ToolCallRecord:
    """Records tool call history for rate limiting and pattern detection."""
    tool_name: str
    timestamp: datetime
    arguments: Dict[str, Any]
    success: bool
    response_time: float


@dataclass
class ConversationContext:
    """Tracks conversation state for context-aware guardrails."""
    session_id: str
    user_expertise_level: str = "unknown"  # novice, intermediate, expert
    symbols_discussed: List[str] = field(default_factory=list)
    topics_covered: List[str] = field(default_factory=list)
    question_history: deque = field(default_factory=lambda: deque(maxlen=10))
    tool_calls: List[ToolCallRecord] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)


class GuardrailValidator:
    """Base class for guardrail validators."""
    
    def validate(self, data: Any, context: ConversationContext) -> Tuple[bool, Optional[str]]:
        """
        Validate input/output data.
        Returns: (is_valid, error_message)
        """
        raise NotImplementedError


class InputSanitizer(GuardrailValidator):
    """Sanitizes and validates user input."""
    
    # Blocked patterns that might indicate malicious intent
    BLOCKED_PATTERNS = [
        r'(?i)insider\s+trading',
        r'(?i)pump\s+and\s+dump',
        r'(?i)market\s+manipulation',
        r'(?i)guaranteed\s+returns?',
        r'(?i)risk[\s-]?free',
        r'(?i)get\s+rich\s+quick',
    ]
    
    # Valid ticker pattern
    TICKER_PATTERN = r'^[A-Z]{1,5}(-USD)?$'
    
    def validate(self, user_input: str, context: ConversationContext) -> Tuple[bool, Optional[str]]:
        """Validate and sanitize user input."""
        
        # Check for blocked patterns
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, user_input):
                return False, "I cannot assist with queries related to market manipulation or unrealistic investment claims."
        
        # Check for SQL injection attempts (basic)
        if any(keyword in user_input.upper() for keyword in ['DROP TABLE', 'DELETE FROM', 'INSERT INTO']):
            return False, "Invalid input detected."
        
        # Validate ticker symbols if present
        potential_tickers = re.findall(r'\b[A-Z]{1,5}\b', user_input)
        for ticker in potential_tickers:
            if len(ticker) <= 5 and not re.match(self.TICKER_PATTERN, ticker):
                logger.warning(f"Potentially invalid ticker: {ticker}")
        
        return True, None


class RateLimiter(GuardrailValidator):
    """Prevents excessive tool calls and API abuse."""
    
    def __init__(self):
        self.limits = {
            'per_minute': 20,      # Max tool calls per minute
            'per_tool_minute': 5,  # Max calls per tool per minute
            'burst_window': 10,    # Seconds for burst detection
            'burst_limit': 8       # Max calls in burst window
        }
    
    def validate(self, tool_name: str, context: ConversationContext) -> Tuple[bool, Optional[str]]:
        """Check if tool call is within rate limits."""
        
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        burst_window_ago = now - timedelta(seconds=self.limits['burst_window'])
        
        # Get recent tool calls
        recent_calls = [tc for tc in context.tool_calls if tc.timestamp > minute_ago]
        recent_tool_calls = [tc for tc in recent_calls if tc.tool_name == tool_name]
        burst_calls = [tc for tc in context.tool_calls if tc.timestamp > burst_window_ago]
        
        # Check overall rate limit
        if len(recent_calls) >= self.limits['per_minute']:
            return False, "Rate limit exceeded. Please wait a moment before making more requests."
        
        # Check per-tool rate limit
        if len(recent_tool_calls) >= self.limits['per_tool_minute']:
            return False, f"Too many requests for {tool_name}. Please try again in a moment."
        
        # Check burst detection
        if len(burst_calls) >= self.limits['burst_limit']:
            return False, "Please slow down your requests."
        
        return True, None


class LoopDetector(GuardrailValidator):
    """Detects and prevents infinite loops or repetitive patterns."""
    
    def __init__(self):
        self.repetition_threshold = 3
        self.similarity_threshold = 0.8
    
    def validate(self, question: str, context: ConversationContext) -> Tuple[bool, Optional[str]]:
        """Check for repetitive questions or loop patterns."""
        
        # Check exact repetition
        recent_questions = list(context.question_history)
        if recent_questions.count(question) >= self.repetition_threshold:
            return False, "I notice you've asked this question multiple times. Perhaps I can help clarify something specific?"
        
        # Check similar questions (simplified similarity check)
        similar_count = 0
        question_words = set(question.lower().split())
        for past_question in recent_questions:
            past_words = set(past_question.lower().split())
            similarity = len(question_words & past_words) / max(len(question_words), len(past_words))
            if similarity >= self.similarity_threshold:
                similar_count += 1
        
        if similar_count >= self.repetition_threshold:
            return False, "We've discussed this topic several times. Would you like to explore a different aspect?"
        
        return True, None


class OutputValidator(GuardrailValidator):
    """Validates agent outputs for compliance and safety."""
    
    # Phrases that should trigger warnings
    WARNING_PHRASES = [
        r'(?i)guarantee',
        r'(?i)no risk',
        r'(?i)definitely will',
        r'(?i)certain to',
        r'(?i)must buy',
        r'(?i)must sell',
    ]
    
    # Required disclaimers for certain topics
    DISCLAIMER_TRIGGERS = {
        'investment': "This is analysis, not investment advice.",
        'crypto': "Cryptocurrency investments are highly volatile and risky.",
        'options': "Options trading involves significant risk of loss.",
        'leverage': "Leveraged products can amplify both gains and losses.",
    }
    
    def validate(self, output: str, context: ConversationContext) -> Tuple[bool, Optional[str]]:
        """Validate agent output for compliance."""
        
        # Check for absolute statements that need softening
        for pattern in self.WARNING_PHRASES:
            if re.search(pattern, output):
                return False, "Please rephrase without absolute guarantees or commands."
        
        # Check if disclaimers are needed
        output_lower = output.lower()
        needed_disclaimers = []
        for trigger, disclaimer in self.DISCLAIMER_TRIGGERS.items():
            if trigger in output_lower and disclaimer.lower() not in output_lower:
                needed_disclaimers.append(disclaimer)
        
        if needed_disclaimers:
            return False, f"Please include: {' '.join(needed_disclaimers)}"
        
        return True, None


class DataAnomalyDetector(GuardrailValidator):
    """Detects anomalous or suspicious data from tools."""
    
    def validate(self, tool_result: Dict[str, Any], context: ConversationContext) -> Tuple[bool, Optional[str]]:
        """Check for data anomalies in tool results."""
        
        # Check for common anomalies
        if 'price' in tool_result:
            price = tool_result.get('price', 0)
            
            # Check for negative or zero prices
            if price <= 0:
                return False, "Invalid price data detected."
            
            # Check for unrealistic daily moves (>50%)
            if 'change_percent' in tool_result:
                change = abs(tool_result['change_percent'])
                if change > 50:
                    return False, f"Unusual price movement detected ({change}%). This may be incorrect data."
        
        # Check for negative volume
        if 'volume' in tool_result and tool_result['volume'] < 0:
            return False, "Invalid volume data detected."
        
        # Check for timestamp validity
        if 'timestamp' in tool_result:
            try:
                timestamp = datetime.fromisoformat(tool_result['timestamp'].replace('Z', '+00:00'))
                if timestamp > datetime.now() + timedelta(hours=1):
                    return False, "Future timestamp detected in data."
            except:
                logger.warning(f"Invalid timestamp format: {tool_result.get('timestamp')}")
        
        return True, None


class GuardrailsManager:
    """Manages all guardrails for the OpenAI Realtime Agent."""
    
    def __init__(self):
        self.validators = {
            'input': InputSanitizer(),
            'rate_limit': RateLimiter(),
            'loop': LoopDetector(),
            'output': OutputValidator(),
            'data_anomaly': DataAnomalyDetector(),
        }
        self.contexts: Dict[str, ConversationContext] = {}
        self.stats = defaultdict(int)
    
    def get_or_create_context(self, session_id: str) -> ConversationContext:
        """Get or create conversation context for a session."""
        if session_id not in self.contexts:
            self.contexts[session_id] = ConversationContext(session_id=session_id)
        return self.contexts[session_id]
    
    def validate_input(self, user_input: str, session_id: str) -> Tuple[bool, Optional[str]]:
        """Validate user input before processing."""
        context = self.get_or_create_context(session_id)
        
        # Run input validation
        valid, error = self.validators['input'].validate(user_input, context)
        if not valid:
            self.stats['input_blocked'] += 1
            logger.warning(f"Input blocked for session {session_id}: {error}")
            return False, error
        
        # Check for loops
        valid, error = self.validators['loop'].validate(user_input, context)
        if not valid:
            self.stats['loop_detected'] += 1
            logger.warning(f"Loop detected for session {session_id}: {error}")
            return False, error
        
        # Update context
        context.question_history.append(user_input)
        self.stats['inputs_validated'] += 1
        
        return True, None
    
    def validate_tool_call(self, tool_name: str, arguments: Dict[str, Any], session_id: str) -> Tuple[bool, Optional[str]]:
        """Validate tool call before execution."""
        context = self.get_or_create_context(session_id)
        
        # Check rate limits
        valid, error = self.validators['rate_limit'].validate(tool_name, context)
        if not valid:
            self.stats['rate_limited'] += 1
            logger.warning(f"Rate limit hit for session {session_id}: {error}")
            return False, error
        
        # Record tool call (will be marked as success/failure later)
        context.tool_calls.append(
            ToolCallRecord(
                tool_name=tool_name,
                timestamp=datetime.now(),
                arguments=arguments,
                success=False,
                response_time=0
            )
        )
        
        self.stats['tool_calls_validated'] += 1
        return True, None
    
    def validate_tool_result(self, tool_result: Dict[str, Any], tool_name: str, session_id: str) -> Tuple[bool, Optional[str]]:
        """Validate tool execution results."""
        context = self.get_or_create_context(session_id)
        
        # Check for data anomalies
        valid, error = self.validators['data_anomaly'].validate(tool_result, context)
        if not valid:
            self.stats['anomalies_detected'] += 1
            logger.warning(f"Data anomaly detected for session {session_id}: {error}")
            return False, error
        
        # Mark tool call as successful
        if context.tool_calls:
            context.tool_calls[-1].success = True
        
        # Extract symbols from results
        if 'symbol' in tool_result and tool_result['symbol'] not in context.symbols_discussed:
            context.symbols_discussed.append(tool_result['symbol'])
        
        self.stats['tool_results_validated'] += 1
        return True, None
    
    def validate_output(self, output: str, session_id: str) -> Tuple[bool, Optional[str]]:
        """Validate agent output before sending to user."""
        context = self.get_or_create_context(session_id)
        
        # Run output validation
        valid, error = self.validators['output'].validate(output, context)
        if not valid:
            self.stats['outputs_modified'] += 1
            logger.warning(f"Output needs modification for session {session_id}: {error}")
            return False, error
        
        self.stats['outputs_validated'] += 1
        return True, None
    
    def detect_expertise_level(self, user_input: str, session_id: str) -> str:
        """Detect user's expertise level from their language."""
        context = self.get_or_create_context(session_id)
        
        # Expert indicators
        expert_terms = ['RSI', 'MACD', 'bollinger', 'options', 'theta', 'IV', 'support', 'resistance']
        # Intermediate indicators  
        intermediate_terms = ['P/E', 'market cap', 'dividend', 'earnings', 'volume', 'average']
        
        input_lower = user_input.lower()
        
        if any(term.lower() in input_lower for term in expert_terms):
            context.user_expertise_level = "expert"
        elif any(term.lower() in input_lower for term in intermediate_terms):
            context.user_expertise_level = "intermediate"
        elif context.user_expertise_level == "unknown":
            context.user_expertise_level = "novice"
        
        return context.user_expertise_level
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session."""
        context = self.get_or_create_context(session_id)
        
        return {
            'session_duration': (datetime.now() - context.start_time).total_seconds(),
            'questions_asked': len(context.question_history),
            'symbols_discussed': context.symbols_discussed,
            'tool_calls_made': len(context.tool_calls),
            'expertise_level': context.user_expertise_level,
            'avg_response_time': sum(tc.response_time for tc in context.tool_calls) / len(context.tool_calls) if context.tool_calls else 0
        }
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global guardrail statistics."""
        return dict(self.stats)
    
    def cleanup_old_sessions(self, hours: int = 24):
        """Clean up old session contexts to prevent memory leaks."""
        cutoff = datetime.now() - timedelta(hours=hours)
        old_sessions = [
            sid for sid, ctx in self.contexts.items()
            if ctx.start_time < cutoff
        ]
        
        for session_id in old_sessions:
            del self.contexts[session_id]
            logger.info(f"Cleaned up old session: {session_id}")
        
        return len(old_sessions)


# Global guardrails manager instance
guardrails = GuardrailsManager()


# Convenience functions for easy integration
def validate_user_input(user_input: str, session_id: str) -> Tuple[bool, Optional[str]]:
    """Validate user input through guardrails."""
    return guardrails.validate_input(user_input, session_id)


def validate_tool_call(tool_name: str, arguments: Dict[str, Any], session_id: str) -> Tuple[bool, Optional[str]]:
    """Validate tool call through guardrails."""
    return guardrails.validate_tool_call(tool_name, arguments, session_id)


def validate_tool_result(tool_result: Dict[str, Any], tool_name: str, session_id: str) -> Tuple[bool, Optional[str]]:
    """Validate tool result through guardrails."""
    return guardrails.validate_tool_result(tool_result, tool_name, session_id)


def validate_agent_output(output: str, session_id: str) -> Tuple[bool, Optional[str]]:
    """Validate agent output through guardrails."""
    return guardrails.validate_output(output, session_id)


def detect_user_expertise(user_input: str, session_id: str) -> str:
    """Detect user's expertise level."""
    return guardrails.detect_expertise_level(user_input, session_id)