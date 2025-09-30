# How to Enable LLM for Educational Responses

## Quick Fix (2 Lines of Code)

### Option 1: Completely Disable the Fast-Path
```python
# In backend/services/agent_orchestrator.py, line ~4424
# Simply comment out these lines:

# if intent == "educational":
#     response = await self._handle_educational_query(query)
#     return response
```

**Result**: All educational queries will now go to OpenAI GPT-5-mini

### Option 2: Keep Fast-Path for ONLY Basic Terms
```python
# Replace the current code with:
if intent == "educational":
    # Only use hardcoded for very basic, unchanging definitions
    if any(term in query.lower() for term in ["bull market", "bear market", "market order", "limit order"]):
        response = await self._handle_educational_query(query)
        return response
    # Everything else goes to LLM
    # (falls through to regular processing)
```

## Better Solution: Hybrid Approach

```python
async def process_query(self, query: str, conversation_history: Optional[List[Dict[str, str]]] = None, stream: bool = False) -> Dict[str, Any]:
    # ... existing code ...
    
    # Enhanced educational handling
    if intent == "educational":
        # Try hardcoded first for speed
        static_response = await self._handle_educational_query(query)
        
        # If no good hardcoded match, use LLM
        if static_response.get("text", "").startswith("I can help you learn"):
            # This is the generic fallback - use LLM instead
            logger.info("No specific educational content found, using LLM")
            # Continue to LLM processing (don't return)
        else:
            # We have a good hardcoded answer
            # But enhance it with LLM if there's context
            if conversation_history and len(conversation_history) > 0:
                # User has context - enhance the static response
                enhanced_query = f"The user asked: {query}. Here's a basic answer: {static_response['text']}. Please enhance this explanation based on our conversation context."
                # Continue to LLM with enhanced prompt
            else:
                # No context, static answer is fine
                return static_response
```

## Best Solution: Dedicated Educational LLM Path

```python
async def _process_educational_with_llm(self, query: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    """Process educational queries with LLM for rich, contextual responses."""
    
    # Build educational-focused prompt
    educational_system_prompt = """You are a patient and knowledgeable trading educator. 
    Your role is to teach trading concepts in a clear, beginner-friendly way.
    
    Guidelines:
    - Use simple language and avoid jargon
    - Provide practical examples
    - Build on previous conversation context
    - Never give specific investment advice
    - Encourage safe learning practices (paper trading, small positions)
    - If discussing risks, be thorough but not alarmist
    """
    
    messages = [
        {"role": "system", "content": educational_system_prompt}
    ]
    
    # Add conversation history for context
    if conversation_history:
        messages.extend(conversation_history[-5:])  # Last 5 messages for context
    
    messages.append({"role": "user", "content": query})
    
    # Call OpenAI with educational parameters
    response = await self.client.chat.completions.create(
        model="gpt-4o-mini",  # Fast, cheap model
        messages=messages,
        temperature=0.5,  # Balanced creativity/consistency
        max_tokens=600,  # Enough for thorough explanation
        presence_penalty=0.1,  # Slight penalty to avoid repetition
        frequency_penalty=0.1
    )
    
    response_text = response.choices[0].message.content
    
    # Check if we should add visual aids
    visual_commands = []
    if "support" in query.lower() or "resistance" in query.lower():
        visual_commands.append("EDUCATIONAL:SHOW_SUPPORT_RESISTANCE_EXAMPLE")
    elif "candlestick" in query.lower():
        visual_commands.append("EDUCATIONAL:SHOW_CANDLESTICK_PATTERNS")
    
    return {
        "text": response_text,
        "tools_used": ["educational_llm"],
        "structured_data": {
            "type": "educational",
            "llm_generated": True,
            "model": "gpt-4o-mini"
        },
        "chart_commands": visual_commands,
        "timestamp": datetime.now().isoformat()
    }

# Then in process_query:
if intent == "educational":
    # Always use LLM for educational content
    return await self._process_educational_with_llm(query, conversation_history)
```

## Testing the Change

After making the change:

```bash
# Test that educational queries now use LLM
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What does buy low mean?"}' 

# Should return a dynamic response, not the same static text

# Test with context
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Can you explain that in simpler terms?",
    "session_id": "previous-session-id"
  }'

# Should reference the previous explanation
```

## Environment Variable Control

Add to `.env`:
```bash
# Use LLM for educational queries (default: false for backwards compatibility)
USE_LLM_FOR_EDUCATION=true

# Educational LLM settings
EDUCATION_MODEL=gpt-4o-mini
EDUCATION_MAX_TOKENS=600
EDUCATION_TEMPERATURE=0.5
```

Then in code:
```python
USE_LLM_FOR_EDUCATION = os.getenv("USE_LLM_FOR_EDUCATION", "false").lower() == "true"

if intent == "educational":
    if USE_LLM_FOR_EDUCATION:
        return await self._process_educational_with_llm(query, conversation_history)
    else:
        # Fallback to hardcoded (current behavior)
        return await self._handle_educational_query(query)
```

## Benefits of Using LLM

### Before (Hardcoded):
```
User: "What does buy low mean?"
Bot: "Buy low, sell high is the fundamental principle of trading..."
User: "I don't understand"
Bot: "I can help you learn about trading! Here are some topics..."  # Generic fallback
```

### After (LLM):
```
User: "What does buy low mean?"
Bot: "Great question! 'Buy low, sell high' is like buying items on sale and selling them when prices go up. Imagine buying a winter coat in summer when it's cheap (low demand) and selling it in winter when everyone wants one (high demand). In stocks, you're looking for companies that are temporarily undervalued..."
User: "I don't understand"
Bot: "Let me simplify that even more! Think of it like shopping at a grocery store. Sometimes apples are $1 each (expensive/high), sometimes they're 50¢ each (cheap/low). Smart shoppers buy when they're 50¢. In the stock market..."
```

## Cost Impact

- Average educational query: ~500 tokens (input + output)
- Cost per query: ~$0.002
- 100 educational queries/day: $0.20/day
- Monthly cost: ~$6

**For $6/month, users get intelligent, contextual educational support instead of static FAQ responses.**

## Implementation Priority

1. **Immediate**: Comment out fast-path (2 minutes)
2. **Next Sprint**: Add hybrid approach with env variable control
3. **Future**: Dedicated educational LLM with specialized prompts
4. **Long-term**: Fine-tuned model specifically for trading education