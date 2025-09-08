# OpenAI Agents SDK - Comprehensive Research Notes

*Generated: September 4, 2025*  
*Research Sources: Official OpenAI GitHub repositories, Context7 documentation*

---

## 🏗️ **SDK Overview**

OpenAI Agents SDK provides **lightweight primitives** for building multi-agent AI applications with **minimal abstractions** but **powerful orchestration** capabilities.

### **Core Primitives**
1. **Agents** - LLMs with instructions, tools, and guardrails
2. **Handoffs** - Delegation mechanism between agents  
3. **Guardrails** - Input/output validation and safety checks
4. **Sessions** - Automatic conversation history management
5. **Tracing** - Built-in workflow visualization and debugging

### **Available Languages**
- **Python** - `pip install openai-agents` 
- **JavaScript/TypeScript** - `npm install @openai/agents`
- **Go** - `github.com/nlpodyssey/openai-agents-go` (community)

---

## 🐍 **Python SDK (openai-agents-python)**

### **Installation & Setup**
```bash
pip install openai-agents
export OPENAI_API_KEY="sk-..."
```

### **Basic Agent Creation**
```python
from agents import Agent, Runner
import asyncio

# Basic agent
agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
    model="gpt-4o-mini"  # Optional, defaults to provider settings
)

# Run agent
async def main():
    result = await Runner.run(agent, "Write a haiku about recursion")
    print(result.final_output)

asyncio.run(main())
```

### **Agent Configuration Parameters**
```python
agent = Agent(
    name="Stock Analyst",                    # Required: Human-readable identifier
    instructions="Analyze stock trends",     # Required: System prompt
    model="gpt-4o-mini",                    # Optional: Model selection
    handoffs=[other_agent1, other_agent2],  # Optional: Delegation targets
    tools=[get_weather_tool],               # Optional: Available functions
    input_guardrails=[input_guardrail],     # Optional: Input validation
    output_guardrails=[output_guardrail],   # Optional: Output validation
    output_type=MyPydanticModel,           # Optional: Structured output
    handoff_description="Stock analysis expert" # For handoff routing
)
```

### **Tools Implementation**
```python
from agents import function_tool

@function_tool
def get_weather(city: str) -> str:
    """Get weather for a city."""
    return f"Weather in {city}: sunny"

@function_tool  
def calculate(a: float, b: float, operation: str) -> float:
    """Perform basic math operations."""
    if operation == "add":
        return a + b
    elif operation == "multiply":
        return a * b
    # ... more operations

# Use in agent
agent = Agent(
    name="Calculator",
    instructions="Help with math problems",
    tools=[get_weather, calculate]
)
```

### **Handoffs Between Agents**
```python
from agents import Agent, Runner

# Specialized agents
math_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist for math problems", 
    instructions="Solve math problems step by step"
)

history_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist for historical questions",
    instructions="Explain historical events clearly"
)

# Triage agent with handoffs
triage_agent = Agent(
    name="Triage Agent", 
    instructions="Route questions to appropriate specialist",
    handoffs=[math_agent, history_agent]
)

# The LLM automatically chooses which agent to hand off to
result = await Runner.run(triage_agent, "What is 2+2?")
# Automatically hands off to math_agent
```

### **Advanced Handoffs with Customization**
```python
from agents import Agent, handoff, RunContextWrapper

def on_handoff_callback(ctx: RunContextWrapper[None]):
    print("Handoff occurred, logging context...")

# Custom handoff configuration
custom_handoff = handoff(
    agent=math_agent,
    tool_name_override="send_to_math_expert",
    tool_description_override="Transfer complex math problems",
    on_handoff=on_handoff_callback
)

triage_agent = Agent(
    name="Triage",
    instructions="Route appropriately", 
    handoffs=[custom_handoff, history_agent]
)
```

### **Guardrails Implementation**
```python
from agents import Agent, InputGuardrail, GuardrailFunctionOutput, Runner
from pydantic import BaseModel

class HomeworkCheck(BaseModel):
    is_homework: bool
    reasoning: str

# Guardrail agent
guardrail_agent = Agent(
    name="Homework Checker",
    instructions="Check if user is asking for homework help",
    output_type=HomeworkCheck
)

# Guardrail function
async def homework_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(HomeworkCheck)
    
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=final_output.is_homework  # Blocks if homework
    )

# Agent with guardrail
protected_agent = Agent(
    name="Tutor",
    instructions="Help with learning, not homework",
    input_guardrails=[InputGuardrail(guardrail_function=homework_guardrail)]
)

# Usage with exception handling
from agents.exceptions import InputGuardrailTripwireTriggered

try:
    result = await Runner.run(protected_agent, "Do my math homework")
except InputGuardrailTripwireTriggered as e:
    print("Blocked:", e.message)
```

### **Session Management & Memory**
```python
from agents import Agent, Runner, SQLiteSession

agent = Agent(name="Assistant", instructions="Be helpful")
session = SQLiteSession("conversation_123")  # Persistent ID

# First turn
result1 = await Runner.run(agent, "My name is Alice", session=session)

# Second turn - automatically remembers Alice
result2 = await Runner.run(agent, "What's my name?", session=session)
print(result2.final_output)  # "Your name is Alice"

# Works with sync runner too
result3 = Runner.run_sync(agent, "Tell me a joke", session=session)
```

### **Runner Configuration**
```python
from agents import Runner, ModelSettings

runner = Runner({
    "model": "gpt-4o-mini",                    # Force model for all agents
    "model_settings": ModelSettings(           # Global model tuning
        temperature=0.7,
        max_tokens=1000
    ),
    "input_guardrails": [global_guardrail],    # Applied to initial input
    "output_guardrails": [safety_guardrail],   # Applied to final output  
    "tracing_disabled": False,                 # Enable/disable tracing
    "workflow_name": "Stock Analysis Flow",    # For traces dashboard
    "max_turns": 10                           # Safety limit
})

result = await runner.run(agent, "Hello")
```

### **Realtime/Voice Agents**
```python
from agents.realtime import RealtimeAgent, RealtimeRunner

# Voice-enabled agent
voice_agent = RealtimeAgent(
    name="Voice Assistant",
    instructions="Respond conversationally and briefly",
    model="gpt-4o-realtime-preview",
    voice="alloy"
)

# Configure realtime runner
runner = RealtimeRunner(
    starting_agent=voice_agent,
    config={
        "model_settings": {
            "voice": "alloy",
            "modalities": ["text", "audio"],
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.5,
                "silence_duration_ms": 200
            }
        }
    }
)

# Start voice session
session = await runner.run()
async with session:
    async for event in session:
        if event.type == "response.audio_transcript.done":
            print(f"Agent: {event.transcript}")
```

---

## 🌐 **JavaScript/TypeScript SDK (@openai/agents)**

### **Installation & Setup**
```bash
npm install @openai/agents zod
export OPENAI_API_KEY="sk-..."
```

### **Basic Agent Creation**
```typescript
import { Agent, Runner } from '@openai/agents';

// Basic agent
const agent = new Agent({
  name: 'Assistant',
  instructions: 'You are a helpful assistant',
  model: 'gpt-4o-mini'
});

// Run agent
const runner = new Runner();
const result = await runner.run(agent, 'Write a haiku about recursion');
console.log(result.finalOutput);
```

### **Type-Safe Agent Creation**
```typescript
import { Agent } from '@openai/agents';
import { z } from 'zod';

// Using Agent.create for better TypeScript inference
const agent = Agent.create({
  name: 'Data Analyst', 
  instructions: 'Analyze data and provide insights',
  outputType: z.object({
    analysis: z.string(),
    confidence: z.number()
  }),
  handoffs: [otherAgent] // TypeScript knows about handoff types
});

const result = await runner.run(agent, 'Analyze sales data');
// result.finalOutput is properly typed
```

### **Tools Implementation**
```typescript
import { tool } from '@openai/agents';
import { z } from 'zod';

// Define tool with Zod validation
const getWeatherTool = tool({
  name: 'get_weather',
  description: 'Get weather for a city',
  parameters: z.object({
    city: z.string(),
    units: z.enum(['celsius', 'fahrenheit']).optional()
  }),
  execute: async (input) => {
    const { city, units = 'celsius' } = input;
    // Call weather API
    return `Weather in ${city}: 22°${units === 'celsius' ? 'C' : 'F'}`;
  }
});

// Use in agent
const weatherAgent = new Agent({
  name: 'Weather Assistant',
  instructions: 'Help with weather queries',
  tools: [getWeatherTool]
});
```

### **Agent Handoffs**
```typescript
import { Agent, handoff } from '@openai/agents';

const dataAgent = new Agent({
  name: 'Data Agent',
  instructions: 'Handle data analysis tasks',
  handoffDescription: 'Expert in data analysis and statistics',
  tools: [analysisTools]
});

// Basic handoff
const mainAgent = new Agent({
  name: 'Main Agent',
  instructions: 'Route queries to specialists',
  handoffs: [dataAgent] // Simple handoff
});

// Advanced handoff with customization
const customAgent = new Agent({
  name: 'Custom Agent',
  instructions: 'Handle complex routing',
  handoffs: [
    handoff({
      agent: dataAgent,
      toolNameOverride: 'transfer_to_data_expert',
      toolDescriptionOverride: 'Send complex data questions here',
      onHandoff: (context, input) => {
        console.log('Handoff triggered:', context, input);
      },
      inputType: z.object({
        query: z.string(),
        priority: z.enum(['low', 'medium', 'high'])
      })
    })
  ]
});
```

### **Guardrails Implementation**
```typescript
import { Agent, type GuardrailFunction } from '@openai/agents';

// Input guardrail
const mathHomeworkGuardrail: GuardrailFunction = async (agent, input) => {
  const checkResult = await agent.call(
    'homework-checker', 
    `Is this homework: ${input.text}`
  );
  
  const isHomework = checkResult.text.toLowerCase().includes('yes');
  
  return {
    tripwireTriggered: isHomework,
    message: isHomework ? 'Homework requests blocked' : 'Input approved'
  };
};

// Output guardrail  
const profanityGuardrail: GuardrailFunction = async (agent, output) => {
  const bannedWords = ['badword1', 'badword2'];
  const hasProfanity = bannedWords.some(word => 
    output.text.toLowerCase().includes(word)
  );
  
  return {
    tripwireTriggered: hasProfanity,
    message: hasProfanity ? 'Profanity detected' : 'Output clean'
  };
};

// Agent with guardrails
const protectedAgent = new Agent({
  name: 'Protected Agent',
  instructions: 'Be helpful and safe',
  inputGuardrails: [mathHomeworkGuardrail],
  outputGuardrails: [profanityGuardrail]
});
```

### **Realtime/Voice Agents**
```typescript
import { RealtimeAgent, RealtimeSession, tool } from '@openai/agents-realtime';
import { z } from 'zod';

// Voice tool
const getInfoTool = tool({
  name: 'get_info',
  description: 'Get information about a topic',
  parameters: z.object({ topic: z.string() }),
  execute: async (input) => `Information about ${input.topic}`
});

// Realtime agent
const voiceAgent = new RealtimeAgent({
  name: 'Voice Assistant',
  instructions: 'Be conversational and brief',
  tools: [getInfoTool]
});

// Browser usage
const session = new RealtimeSession(voiceAgent);
await session.connect({ apiKey: 'sk-...' });
// Automatically handles audio input/output
```

---

## 🔄 **Key Differences: Python vs JavaScript**

| Feature | Python SDK | JavaScript SDK |
|---------|------------|----------------|
| **Agent Creation** | `Agent(...)` | `new Agent({...})` or `Agent.create({...})` |
| **Runner Usage** | `await Runner.run(agent, input)` | `await runner.run(agent, input)` |
| **Tools** | `@function_tool` decorator | `tool({...})` function |
| **Validation** | Pydantic models | Zod schemas |
| **Handoffs** | `handoffs=[agent1, agent2]` | `handoffs: [agent1, handoff({...})]` |
| **Guardrails** | `InputGuardrail(guardrail_function=fn)` | Array of GuardrailFunction |
| **Sessions** | `SQLiteSession("id")` | Built into RealtimeSession |
| **Async Pattern** | `asyncio.run(main())` | `await` directly |
| **Error Handling** | Exception classes | Promise rejection |

---

## ⚡ **Common Patterns & Best Practices**

### **Multi-Agent Orchestration**
```python/typescript
# Triage Pattern - Most Common
triage_agent = Agent(
    name="Triage",
    instructions="Analyze request and route to appropriate specialist",
    handoffs=[specialist1, specialist2, specialist3]
)

# Sequential Handoffs
research_agent = Agent(handoffs=[data_collector])
data_collector = Agent(handoffs=[report_generator]) 
report_generator = Agent(...)  # Final agent, no handoffs
```

### **Guardrail Strategies** 
```python/typescript
# Layered Protection
agent = Agent(
    input_guardrails=[
        safety_filter,      # Block unsafe content
        homework_blocker,   # Block homework requests  
        rate_limiter       # Prevent spam
    ],
    output_guardrails=[
        profanity_filter,   # Clean output
        accuracy_checker,   # Verify facts
        length_limiter     # Keep responses brief
    ]
)
```

### **Session Management**
```python/typescript
# Conversation Context
session = SQLiteSession(f"user_{user_id}_conversation")

# Multi-turn interaction
for user_input in conversation:
    result = await Runner.run(agent, user_input, session=session)
    # Agent automatically remembers previous context
```

---

## 🚨 **Current Codebase Issues & Fixes**

### **Issue 1: Incorrect Agent Creation**
```python
# ❌ CURRENT (Broken)
self.triage_agent = Agent.create({...})  # Agent.create() doesn't exist

# ✅ CORRECT FIX
self.triage_agent = Agent(
    name='Triage Agent',
    instructions='Route stock queries appropriately',
    handoffs=[self.stock_agent, self.conversation_agent],
    input_guardrails=[StockIntentGuardrail()]
)
```

### **Issue 2: Missing Handoff Configuration** 
```python
# ❌ CURRENT (Incomplete)
handoffs=[self.stock_agent, self.conversation_agent]

# ✅ ENHANCED FIX
stock_agent = Agent(
    name='Stock Chart Agent',
    handoff_description='Handles stock symbol requests and chart display',
    instructions='Process stock symbols and return chart commands'
)

conversation_agent = Agent(
    name='Conversation Agent', 
    handoff_description='Handles general conversation',
    instructions='Respond to non-stock related questions'
)
```

### **Issue 3: Guardrail Integration**
```python
# ❌ CURRENT (Not working)
class StockIntentGuardrail(InputGuardrail):
    async def execute(self, input_text: str, context: Optional[Dict] = None):
        # Custom implementation that doesn't follow SDK patterns

# ✅ CORRECT INTEGRATION
async def stock_intent_guardrail(ctx, agent, input_data):
    intent_result = self.detector.detect_with_context(input_data)
    
    return GuardrailFunctionOutput(
        output_info=intent_result.__dict__,
        tripwire_triggered=not intent_result.is_stock_intent
    )

# Use in agent
triage_agent = Agent(
    name='Triage Agent',
    instructions='Handle user queries',
    input_guardrails=[InputGuardrail(guardrail_function=stock_intent_guardrail)]
)
```

---

## 📚 **Official Documentation References**

### **Python SDK**
- **Main Repository**: https://github.com/openai/openai-agents-python
- **Documentation**: https://openai.github.io/openai-agents-python
- **PyPI Package**: `pip install openai-agents`
- **Examples**: https://github.com/openai/openai-agents-python/tree/main/examples

### **JavaScript SDK**
- **Main Repository**: https://github.com/openai/openai-agents-js  
- **Documentation**: https://openai.github.io/openai-agents-js
- **NPM Package**: `npm install @openai/agents`
- **Examples**: https://github.com/openai/openai-agents-js/tree/main/examples

### **Additional Resources**
- **MCP Integration**: Model Context Protocol for external data sources
- **Tracing Dashboard**: Built-in visualization for debugging workflows
- **Community Examples**: https://github.com/openai/openai-agents-examples
- **API Reference**: Comprehensive TypeScript/Python API documentation

---

## 🔧 **Quick Reference Commands**

### **Python Development**
```bash
# Install
pip install openai-agents

# Test basic agent
python -c "from agents import Agent, Runner; import asyncio; asyncio.run(Runner.run(Agent(name='Test', instructions='Say hello'), 'Hi'))"

# Run examples
git clone https://github.com/openai/openai-agents-python
cd openai-agents-python/examples && python quickstart.py
```

### **JavaScript Development**
```bash
# Install  
npm install @openai/agents zod

# Test basic agent
node -e "import('@openai/agents').then(({Agent, Runner}) => new Runner().run(new Agent({name:'Test', instructions:'Say hello'}), 'Hi').then(console.log))"

# Run examples
git clone https://github.com/openai/openai-agents-js
cd openai-agents-js && pnpm install && pnpm -F basic start
```

---

*Research completed on September 4, 2025 for voice-enabled stock trading application integration.*