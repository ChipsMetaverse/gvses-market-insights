# ElevenLabs Knowledge Base Complete Guide

## Overview
The ElevenLabs Knowledge Base allows you to enhance your conversational AI agents with custom documents and information. It uses RAG (Retrieval-Augmented Generation) to pull relevant information during conversations.

## Current Configuration Status

### ✅ What's Working
1. **Knowledge Base Documents Exist**: Your agent has 5 documents configured:
   - GVSES Trading Guidelines (ID: lsBT1M95ifxCezXb8Zx9)
   - Encyclopedia of Chart Patterns (ID: TyDQIY5A3ajYhabxsVQX)
   - THE CANDLESTICK TRADING BIBLE (ID: tLl1ZmTqeMec2iBkVTdl)
   - Yahoo Finance - Stock Market Live (ID: ohYBBvoIOSiwp24GAyv2)
   - Cryptocurrency Prices (CoinMarketCap) (ID: D9xiACmtim4fR6cibouX)

2. **RAG is Enabled** with these settings:
   - Embedding Model: e5_mistral_7b_instruct
   - Max Vector Distance: 0.6
   - Max Documents Length: 50,000
   - Max Retrieved Chunks: 20

3. **API Access Works**: Can list and upload documents

### ⚠️ Known Issues
1. **Agent Knowledge Base Size endpoint** returns 404 (wrong format)
2. **Adding documents to agent** conflicts with tool configuration
3. **Knowledge retrieval** may not be activating properly during conversations

## API Endpoints Documentation

### 1. List All Knowledge Base Documents
```bash
GET https://api.elevenlabs.io/v1/convai/knowledge-base
Headers: xi-api-key: YOUR_API_KEY

Response: 
{
  "documents": [
    {
      "id": "doc_id",
      "name": "Document Name",
      "created_at": "timestamp"
    }
  ]
}
```

### 2. Get Specific Document
```bash
GET https://api.elevenlabs.io/v1/convai/knowledge-base/{document_id}
Headers: xi-api-key: YOUR_API_KEY
```

### 3. Upload New Document
```bash
POST https://api.elevenlabs.io/v1/convai/knowledge-base
Headers: xi-api-key: YOUR_API_KEY
Content-Type: multipart/form-data

Body:
- file: (binary)
- name: "Document Name"
- description: "Optional description"
```

### 4. Get Document's Dependent Agents
```bash
GET https://api.elevenlabs.io/v1/convai/knowledge-base/{document_id}/dependent-agents
Headers: xi-api-key: YOUR_API_KEY
```

## How Knowledge Base Works with RAG

### 1. Document Processing
When you upload a document:
- ElevenLabs processes it into chunks
- Each chunk is converted to embeddings using `e5_mistral_7b_instruct`
- Embeddings are stored in a vector database

### 2. Query Processing
During conversation:
- User query is converted to an embedding
- System searches for similar chunks (max_vector_distance: 0.6)
- Top chunks (up to 20) are retrieved
- These chunks are included in the LLM context

### 3. Response Generation
The agent:
- Uses retrieved chunks as context
- Generates response based on both prompt and retrieved knowledge
- Should reference source documents when using knowledge

## Why Knowledge Base Might Not Be Working

### Possible Issues:
1. **Activation Threshold**: The max_vector_distance of 0.6 might be too restrictive
2. **Query Matching**: User queries might not semantically match document content
3. **Tool Priority**: Agent may prefer tools over knowledge base
4. **Context Window**: Retrieved chunks might exceed context limits

### Solutions:

#### 1. Improve Document Content
Make documents more query-friendly:
```markdown
# Instead of:
"The market exhibits bullish tendencies"

# Use:
"When asked about Bitcoin price: The current Bitcoin (BTC-USD) price is..."
```

#### 2. Enhance Agent Prompt
Add explicit instructions:
```
## Knowledge Base Usage
IMPORTANT: When answering questions, ALWAYS:
1. First check if the knowledge base contains relevant information
2. Reference the source document when using knowledge base content
3. Combine knowledge base information with real-time tool data
```

#### 3. Test with Specific Queries
Test queries that should trigger knowledge base:
- "What are the GVSES trading guidelines?"
- "Explain the LTB, ST, and QE levels"
- "What chart patterns should I look for?"

## Configuration in ElevenLabs Dashboard

### To properly configure knowledge base:

1. **Navigate to Agent Settings**
   ```
   https://elevenlabs.io/app/conversational-ai/agents
   ```

2. **Select Your Agent**
   - Find "Gsves Market Insights"
   - Click Edit

3. **Knowledge Base Tab**
   - Click "Knowledge Base" section
   - Verify documents are listed
   - Check RAG settings

4. **RAG Configuration**
   - Ensure "Enable RAG" is checked
   - Adjust settings if needed:
     - Lower max_vector_distance for broader matching (try 0.4)
     - Increase max_retrieved_rag_chunks_count for more context

5. **Sync Changes**
   ```bash
   cd elevenlabs
   convai sync --env dev
   ```

## Testing Knowledge Base Retrieval

### Test Script
```python
# Test if knowledge base is being used
questions = [
    "What are the GVSES trading guidelines?",
    "Explain LTB levels",
    "What does the Encyclopedia of Chart Patterns say about head and shoulders?",
    "According to the knowledge base, what is a good risk management strategy?"
]

for question in questions:
    # Ask via API or voice
    # Check if response references knowledge base content
```

### Expected Behavior
When working properly:
- Agent should reference document content
- Responses should be more detailed for topics in knowledge base
- Agent might say "According to the trading guidelines..." or similar

## Troubleshooting Steps

1. **Verify Documents Exist**
   ```bash
   python3 test_knowledge_base.py
   ```

2. **Check Agent Configuration**
   - Ensure knowledge_base array has document IDs
   - Verify RAG is enabled

3. **Test with Direct Questions**
   - Ask about specific content you know is in documents
   - Monitor if agent uses that information

4. **Adjust RAG Settings**
   - Lower max_vector_distance (0.3-0.5)
   - Increase chunk count
   - Try different embedding models if available

5. **Monitor API Responses**
   - Check if retrieved chunks are being sent
   - Verify chunks are relevant to query

## Best Practices

### 1. Document Structure
- Use clear headings
- Include keywords users might search for
- Format as Q&A when possible
- Add synonyms and variations

### 2. Content Optimization
```markdown
# Good Document Structure
## Bitcoin Price Information
Keywords: BTC, Bitcoin, crypto, cryptocurrency
- Current price queries: Use BTC-USD
- Historical data: Available via API
- Technical analysis: Check RSI, MACD
```

### 3. Regular Updates
- Refresh documents periodically
- Add new trading strategies
- Update market information
- Include recent examples

## Next Steps

1. **Immediate Actions**:
   - Test knowledge base with specific queries
   - Monitor if agent references documents
   - Check ElevenLabs dashboard for RAG metrics

2. **If Not Working**:
   - Lower max_vector_distance to 0.4
   - Upload more targeted documents
   - Add explicit knowledge base instructions to prompt

3. **Long-term Improvements**:
   - Create topic-specific documents
   - Implement feedback loop
   - Monitor which chunks are retrieved
   - Optimize based on usage patterns

## Support Resources

- ElevenLabs Discord: https://discord.gg/elevenlabs
- Documentation: https://elevenlabs.io/docs
- API Reference: https://api.elevenlabs.io/docs

Remember: The knowledge base enhances but doesn't replace the agent's tools. Best results come from combining knowledge base context with real-time tool data.