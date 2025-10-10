================
CODE SNIPPETS
================
### Responses API

Source: https://platform.openai.com/docs/guides/responses-vs-chat-completions

The Responses API generates model output based on an `input` and returns a single `response` object containing an array of `Items`. An `Item` can be a message, function call, or other model actions. Responses are stored by default.

```APIDOC
## POST /responses

### Description
Generates a response from the model, treating various model actions as distinct 'Items'. This API focuses on a single, structured generation and is designed for richer model experiences including improved tool usage.

### Method
POST

### Endpoint
`/responses`

### Parameters
#### Request Body
- **model** (string) - Required - The ID of the model to use for the response.
- **input** (string) - Required - The input text for the model.
- **store** (boolean) - Optional - Whether to store the response. (Default: true)
- **text.format** (object) - Optional - Used instead of `response_format` for structured outputs.
- **function_config** (object) - Optional - Configuration for function calling, with a different shape than Chat Completions.
- **previous_response_id** (string) - Optional - ID of a previous response to chain conversations.

### Request Example
```json
{
  "model": "gpt-5",
  "input": "Write a one-sentence bedtime story about a unicorn."
}
```

### Response
#### Success Response (200)
- **id** (string) - A unique identifier for the response.
- **object** (string) - The object type, which is always `response`.
- **created_at** (integer) - The Unix timestamp (in seconds) of when the response was created.
- **model** (string) - The model used for the response.
- **output** (array of objects) - An array of 'Items' representing the model's actions or content.
  - **id** (string) - A unique identifier for the item.
  - **type** (string) - The type of item (e.g., `reasoning`, `message`, `function_call`).
  - **content** (array) - Content specific to the item type.
  - **summary** (array) - Summary specific to the item type.
  - **status** (string) - Status of the item (e.g., `completed`).
  - **content** (array of objects) - For `message` type, details of the generated content.
    - **type** (string) - Type of content (e.g., `output_text`).
    - **annotations** (array) - Any annotations.
    - **logprobs** (array) - Log probabilities.
    - **text** (string) - The generated text.
  - **role** (string) - The role associated with the item (e.g., `assistant`).

#### Response Example
```json
{
  "id": "resp_68af4030592c81938ec0a5fbab4a3e9f05438e46b5f69a3b",
  "object": "response",
  "created_at": 1756315696,
  "model": "gpt-5-2025-08-07",
  "output": [
    {
      "id": "rs_68af4030baa48193b0b43b4c2a176a1a05438e46b5f69a3b",
      "type": "reasoning",
      "content": [],
      "summary": []
    },
    {
      "id": "msg_68af40337e58819392e935fb404414d005438e46b5f69a3b",
      "type": "message",
      "status": "completed",
      "content": [
        {
          "type": "output_text",
          "annotations": [],
          "logprobs": [],
          "text": "Under a quilt of moonlight, a drowsy unicorn wandered through quiet meadows, brushing blossoms with her glowing horn so they sighed soft lullabies that carried every dreamer gently to sleep."
        }
      ],
      "role": "assistant"
    }
  ]
}
```
```

--------------------------------

### Create Responses API Response Object

Source: https://platform.openai.com/docs/assistants/migration

Python code showing how to create a response object using the new OpenAI Responses API. It specifies the language model, input items, and can link to an existing conversation for contextual processing.

```python
response = openai.responses.create(
  model="gpt-4.1",
  input=[{"role": "user", "content": "What are the 5 Ds of dodgeball?"}]
  conversation: "conv_689667905b048191b4740501625afd940c7533ace33a2dab"
)
```

--------------------------------

### Responses API

Source: https://platform.openai.com/docs/gpt-5-nano

Endpoint for handling responses.

```APIDOC
## GET v1/responses

### Description
Endpoint for handling responses.

### Method
GET

### Endpoint
/v1/responses
```

--------------------------------

### Responses API

Source: https://platform.openai.com/docs/tts-1-hd

Endpoint for handling responses.

```APIDOC
## POST /v1/responses

### Description
Endpoint for responses.

### Method
POST

### Endpoint
/v1/responses
```

--------------------------------

### Executing API Calls: Runs vs. Responses (Python)

Source: https://platform.openai.com/docs/assistants/overview

This example shows how to execute an action using the deprecated Assistants API (`Run` object) which typically requires polling for status, versus the new Responses API (`Response` object) which offers a simpler, more direct `create` method. The `Response` API accepts `input` items and a `conversation` ID directly.

```python
thread_id = "thread_CrXtCzcyEQbkAcXuNmVSKFs1"
assistant_id = "asst_8fVY45hU3IM6creFkVi5MBKB"

run = openai.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant.id)

while run.status in ("queued", "in_progress"):
  time.sleep(1)
  run = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
```

```python
response = openai.responses.create(
  model="gpt-4.1",
  input=[{"role": "user", "content": "What are the 5 Ds of dodgeball?"}],
  conversation: "conv_689667905b048191b4740501625afd940c7533ace33a2dab"
)
```

--------------------------------

### Responses API

Source: https://platform.openai.com/docs/models/gpt-image-1

Endpoint for handling responses, likely related to fetching or managing interaction outputs.

```APIDOC
## GET/POST v1/responses

### Description
This endpoint is used for managing or retrieving responses, though specific functionality is not detailed.

### Method
GET/POST (Method not specified, inferred)

### Endpoint
v1/responses

### Parameters
#### Path Parameters
N/A

#### Query Parameters
N/A

#### Request Body
N/A (Details not provided in source text)

### Request Example
{}

### Response
#### Success Response (200)
N/A (Details not provided in source text)

#### Response Example
{}
```

--------------------------------

### Create Responses API Conversation Object

Source: https://platform.openai.com/docs/assistants/migration

Example Python code demonstrating how to create a conversation object using the new OpenAI Responses API. It initializes a conversation with input items, which can include user messages, and supports optional metadata.

```python
conversation = openai.conversations.create(
  items=[{"role": "user", "content": "what are the 5 Ds of dodgeball?"}],
  metadata={"user_id": "peter_le_fleur"},
)
```

--------------------------------

### Responses API

Source: https://platform.openai.com/docs/models/gpt-4o-mini-realtime-preview

This endpoint handles various responses within the GPT-4o mini Realtime ecosystem.

```APIDOC
## POST /v1/responses

### Description
This endpoint is likely used for processing or retrieving specific response objects within the API.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
- No path parameters specified.

#### Query Parameters
- No query parameters specified.

#### Request Body
- Request body details are not specified in the provided text.

### Request Example
```json
// Request example not provided in the source text.
{
  "message": "Refer to the official API documentation for specific request body schemas."
}
```

### Response
#### Success Response (200)
- Response details are not specified in the provided text.

#### Response Example
```json
// Response example not provided in the source text.
{
  "message": "Refer to the official API documentation for specific response schemas."
}
```
```

--------------------------------

### Responses API Conversation Object Response Structure

Source: https://platform.openai.com/docs/assistants/migration

JSON representation of a conversation object returned by the new OpenAI Responses API. It includes a unique identifier, object type, creation timestamp, and associated metadata.

```json
{
"id": "conv_68542dc602388199a30af27d040cefd4087a04b576bfeb24",
"object": "conversation",
"created_at": 1752855924,
"metadata": {
	"user_id": "peter_le_fleur"
}
}
```

--------------------------------

### POST /responses (Multi-Turn Conversation - Manual Context)

Source: https://platform.openai.com/docs/guides/responses-vs-chat-completions

This endpoint facilitates multi-turn conversations by allowing you to manually append the output from a previous API response to the input for a subsequent request to the Responses API, building the context incrementally.

```APIDOC
## POST /responses

### Description
Manages multi-turn conversations by appending the output of a previous response to the input context for the next request. This allows for building conversation history step-by-step.

### Method
POST

### Endpoint
/responses

### Parameters
#### Request Body
- **model** (string) - Required - The ID of the model to use (e.g., 'gpt-5').
- **input** (array of objects) - Required - A list of messages or context items comprising the current turn of the conversation.
  - **role** (string) - Required - The role of the author of this message or context item.
  - **content** (string) - Required - The content of the message or context item.

### Request Example
```json
{
  "model": "gpt-5",
  "input": [
    { "role": "user", "content": "What is the capital of France?" }
  ]
}
```

### Response
#### Success Response (200)
- **output** (array of objects) - The generated response from the model, structured as context items.

#### Response Example
```json
{
  "output": [
    { "role": "assistant", "content": "Paris" }
  ]
}
```
```

--------------------------------

### POST /v1/responses - Minimal Reasoning (Responses API)

Source: https://platform.openai.com/docs/guides/latest-model

Example of generating a response with minimal reasoning effort using the Responses API.

```APIDOC
## POST /v1/responses

### Description
Generates a response with minimal reasoning using the Responses API. It shows how to set the 'effort' parameter within the 'reasoning' object.

### Method
POST

### Endpoint
https://api.openai.com/v1/responses

### Request Body
- **model** (string) - Required - The name of the model to use (e.g., "gpt-5").
- **input** (string) - Required - The input prompt.
- **reasoning** (object) - Required - Specifies the reasoning parameters.
  - **effort** (string) - Required - The reasoning effort level ("minimal", "low", "medium", or "high").

### Request Example
```json
{
  "model": "gpt-5",
  "input": "How much gold would it take to coat the Statue of Liberty in a 1mm layer?",
  "reasoning": {
    "effort": "minimal"
  }
}
```
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/guides/responses-vs-chat-completions

This endpoint allows interaction with OpenAI's Responses API, which integrates native tools for more flexible and intelligent agent building. It accepts user input and a list of tools to utilize.

```APIDOC
## POST /v1/responses

### Description
Creates a response using OpenAI's Responses API. This API simplifies the integration of native tools like web search to generate more contextual and informed answers.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The identifier of the AI model to use (e.g., "gpt-5").
- **input** (string) - Required - The user's input or prompt for which a response is needed.
- **tools** (array of objects) - Required - A list of tools to be used by the model. Each object must specify at least a 'type'.
  - **tools[].type** (string) - Required - The type of the tool (e.g., "web_search").

### Request Example
```json
{
  "model": "gpt-5",
  "input": "Who is the current president of France?",
  "tools": [{"type": "web_search"}]
}
```

### Response
#### Success Response (200)
- **output_text** (string) - The generated text response from the model, potentially leveraging the specified tools.

#### Response Example
```json
{
  "output_text": "Emmanuel Macron is the current president of France."
}
```
```

--------------------------------

### Implement User Chat Application with OpenAI Assistants API and Responses API (Python)

Source: https://platform.openai.com/docs/assistants/overview

This example demonstrates how to create a basic user chat application using two different OpenAI APIs: the Assistants API and the Responses API. It covers initiating a conversation, sending user messages, processing AI responses, and retrieving results. The Assistants API involves thread and run management, while the Responses API uses a more direct prompt-based interaction model.

```python
thread = openai.threads.create()

@app.post("/messages")
async def message(message: Message):
openai.beta.threads.messages.create(
	role="user",
	content=message.content
)

run = openai.beta.threads.runs.create(
	assistant_id=os.getenv("ASSISTANT_ID"),
	thread_id=thread.id
)
while run.status in ("queued", "in_progress"):
  await asyncio.sleep(1)
  run = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

messages = openai.beta.threads.messages.list(
	order="desc", limit=1, thread_id=thread.id
)

return { "content": messages[-1].content }
```

```python
conversation = openai.conversations.create()

@app.post("/messages")
async def message(message: Message):
response = openai.responses.create(
	prompt={ "id": os.getenv("PROMPT_ID") },
	input=[{ "role": "user", "content": message.content }]
)

return { "content": response.output_text }
```

--------------------------------

### Manage Multi-Turn Responses API Context Manually

Source: https://platform.openai.com/docs/guides/migrate-to-responses

This example illustrates how to manage context for multi-turn conversations using the Responses API. It shows how to append the output of a previous response and subsequent user inputs to a context array, which is then passed to the `create` method for the next turn. This approach ensures the API has the full conversation history for generating coherent responses.

```python
context = [
    { "role": "role", "content": "What is the capital of France?" }
]
res1 = client.responses.create(
    model="gpt-5",
    input=context,
)

# Append the first response’s output to context
context += res1.output

# Add the next user message
context += [
    { "role": "role", "content": "And it's population?" }
]

res2 = client.responses.create(
    model="gpt-5",
    input=context,
)
```

```javascript
let context = [
  { role: "role", content: "What is the capital of France?" }
];

const res1 = await client.responses.create({
  model: "gpt-5",
  input: context,
});

// Append the first response’s output to context
context = context.concat(res1.output);

// Add the next user message
context.push({ role: "role", content: "And its population?" });

const res2 = await client.responses.create({
  model: "gpt-5",
  input: context,
});
```

--------------------------------

### Example JSON Response from Responses API

Source: https://platform.openai.com/docs/guides/responses-vs-chat-completions_api-mode=responses

This JSON snippet showcases the response structure from the Responses API. It features a unique 'id', 'object', 'created_at' timestamp, model information, and an 'output' array containing various 'Item' types, such as 'reasoning' and 'message' with nested 'content' and 'output_text'.

```json
{
  "id": "resp_68af4030592c81938ec0a5fbab4a3e9f05438e46b5f69a3b",
  "object": "response",
  "created_at": 1756315696,
  "model": "gpt-5-2025-08-07",
  "output": [
    {
      "id": "rs_68af4030baa48193b0b43b4c2a176a1a05438e46b5f69a3b",
      "type": "reasoning",
      "content": [],
      "summary": []
    },
    {
      "id": "msg_68af40337e58819392e935fb404414d005438e46b5f69a3b",
      "type": "message",
      "status": "completed",
      "content": [
        {
          "type": "output_text",
          "annotations": [],
          "logprobs": [],
          "text": "Under a quilt of moonlight, a drowsy unicorn wandered through quiet meadows, brushing blossoms with her glowing horn so they sighed soft lullabies that carried every dreamer gently to sleep."
        }
      ],
      "role": "assistant"
    }
  ],
  ...
}
```

--------------------------------

### POST /v1/responses (Structured Output - Current)

Source: https://platform.openai.com/docs/guides/responses-vs-chat-completions_api-mode=responses

Creates a response using the OpenAI API, defining structured outputs via the `text.format` field. This is the updated and recommended method for structured outputs in the Responses API.

```APIDOC
## POST /v1/responses

### Description
Creates a response using the OpenAI API, defining structured outputs via the `text.format` field. This is the updated and recommended method for structured outputs in the Responses API.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for the response (e.g., "gpt-5").
- **input** (string) - Required - The input text for the response generation (e.g., "Jane, 54 years old").
- **text** (object) - Required - Text generation settings.
  - **format** (object) - Required - Controls the format of the response.
    - **type** (string) - Required - The type of response format (e.g., "json_schema").
    - **name** (string) - Optional - Name of the JSON schema (e.g., "person").
    - **strict** (boolean) - Optional - Whether to enforce strict schema validation.
    - **schema** (object) - Required - The JSON schema definition.
      - **type** (string) - Required - Type of the schema (e.g., "object").
      - **properties** (object) - Required - Object containing property definitions.
        - **name** (object) - Required - Definition for 'name' property.
          - **type** (string) - Required - Type of 'name' (e.g., "string").
          - **minLength** (number) - Optional - Minimum length of 'name' (e.g., 1).
        - **age** (object) - Required - Definition for 'age' property.
          - **type** (string) - Required - Type of 'age' (e.g., "number").
          - **minimum** (number) - Optional - Minimum value for 'age' (e.g., 0).
          - **maximum** (number) - Optional - Maximum value for 'age' (e.g., 130).
      - **required** (array) - Required - List of required fields (e.g., ["name", "age"]).
      - **additionalProperties** (boolean) - Optional - Whether additional properties are allowed.

### Request Example
```json
{
  "model": "gpt-5",
  "input": "Jane, 54 years old",
  "text": {
    "format": {
      "type": "json_schema",
      "name": "person",
      "strict": true,
      "schema": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "minLength": 1
          },
          "age": {
            "type": "number",
            "minimum": 0,
            "maximum": 130
          }
        },
        "required": [
          "name",
          "age"
        ],
        "additionalProperties": false
      }
    }
  }
}
```

### Response
#### Success Response (200)
The response will contain the generated text formatted according to the specified JSON schema. The exact structure depends on the model's output.

#### Response Example
```json
{
  "id": "resp-xxxxxxxxxxxxxxxxx",
  "object": "response",
  "created": 1700000000,
  "model": "gpt-5",
  "choices": [
    {
      "index": 0,
      "text": {
        "content": "{\"name\": \"Jane\", \"age\": 54}",
        "format": {
          "type": "json_schema",
          "name": "person"
        }
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 15,
    "total_tokens": 25
  }
}
```
```

--------------------------------

### Responses API - POST /v1/responses

Source: https://platform.openai.com/docs/models/gpt-4o-mini-search-preview

This endpoint is listed as part of the available APIs but specific details regarding its purpose, request format, and response structure are not provided in the source material.

```APIDOC
## POST /v1/responses

### Description
This endpoint is available for interacting with responses. Specific request and response details are not provided in the source material.

### Method
POST (Assumed)

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
- Not explicitly detailed in the source text.

#### Query Parameters
- Not explicitly detailed in the source text.

#### Request Body
- Not explicitly detailed in the source text.

### Request Example
No example explicitly provided in the source text.

### Response
#### Success Response (200)
- Not explicitly detailed in the source text.

#### Response Example
No example explicitly provided in the source text.
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/api-reference/usage/moderations_object

This endpoint allows you to create a new model response by providing a model identifier and an input text prompt. The API will generate a response based on the provided input and return a detailed response object.

```APIDOC
## POST /v1/responses

### Description
Creates a new model response from a given input text using a specified model. This is the primary way to interact with the OpenAI API for text generation.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
(None)

#### Query Parameters
(None)

#### Request Body
- **model** (string) - Required - The ID of the model to use for generating the response (e.g., "gpt-4.1").
- **input** (string) - Required - The text prompt for which to generate a response.

### Request Example
```json
{
  "model": "gpt-4.1",
  "input": "Tell me a three sentence bedtime story about a unicorn."
}
```

### Response
#### Success Response (200)
- **id** (string) - Unique identifier for the response.
- **object** (string) - Type of object, typically "response".
- **created_at** (integer) - Timestamp when the response was created.
- **status** (string) - Current status of the response generation (e.g., "completed").
- **error** (object/null) - Details if an error occurred during generation.
- **incomplete_details** (object/null) - Information about incomplete aspects of the response.
- **instructions** (object/null) - Any instructions provided to the model.
- **max_output_tokens** (integer/null) - Maximum tokens allowed for the output.
- **model** (string) - The model used to generate the response.
- **output** (array of objects) - Array of output content generated by the model.
  - **type** (string) - Type of output, e.g., "message".
  - **id** (string) - Identifier for the output message.
  - **status** (string) - Status of the output.
  - **role** (string) - Role of the content generator, e.g., "assistant".
  - **content** (array of objects) - Array of content parts.
    - **type** (string) - Type of content, e.g., "output_text".
    - **text** (string) - The generated text content.
    - **annotations** (array) - Any annotations associated with the text.
- **parallel_tool_calls** (boolean) - Indicates if parallel tool calls were made.
- **previous_response_id** (string/null) - ID of a previous response if applicable.
- **reasoning** (object) - Details about the model's reasoning process.
  - **effort** (object/null) - Information on effort used.
  - **summary** (object/null) - Summary of reasoning.
- **store** (boolean) - Whether the response is stored.
- **temperature** (number) - Sampling temperature used.
- **text** (object) - Text-specific response properties.
  - **format** (object) - Format of the text output.
    - **type** (string) - Type of text format, e.g., "text".
- **tool_choice** (string) - Tool choice strategy used.
- **tools** (array) - Tools used by the model.
- **top_p** (number) - Top-p sampling parameter used.
- **truncation** (string) - Truncation strategy used.
- **usage** (object) - Token usage statistics.
  - **input_tokens** (integer) - Number of input tokens consumed.
  - **input_tokens_details** (object) - Details about input tokens.
    - **cached_tokens** (integer) - Number of cached input tokens.
  - **output_tokens** (integer) - Number of output tokens generated.
  - **output_tokens_details** (object) - Details about output tokens.
    - **reasoning_tokens** (integer) - Number of tokens used for reasoning.
  - **total_tokens** (integer) - Total tokens consumed.
- **user** (string/null) - User identifier.
- **metadata** (object) - Custom metadata associated with the response.

#### Response Example
```json
{
  "id": "resp_67ccd2bed1ec8190b14f964abc0542670bb6a6b452d3795b",
  "object": "response",
  "created_at": 1741476542,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4.1-2025-04-14",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd2bf17f0819081ff3bb2cf6508e60bb6a6b452d3795b",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "In a peaceful grove beneath a silver moon, a unicorn named Lumina discovered a hidden pool that reflected the stars. As she dipped her horn into the water, the pool began to shimmer, revealing a pathway to a magical realm of endless night skies. Filled with wonder, Lumina whispered a wish for all who dream to find their own hidden magic, and as she glanced back, her hoofprints sparkled like stardust.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 36,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 87,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 123
  },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### POST /v1/responses - Control Verbosity (Responses API)

Source: https://platform.openai.com/docs/guides/latest-model

Example of controlling the verbosity of the response using the Responses API.

```APIDOC
## POST /v1/responses

### Description
Controls the verbosity of the response using the Responses API.  It uses the `text.verbosity` parameter to control the output verbosity.

### Method
POST

### Endpoint
https://api.openai.com/v1/responses

### Request Body
- **model** (string) - Required - The name of the model to use (e.g., "gpt-5").
- **input** (string) - Required - The input prompt.
- **text** (object) - Required - Specifies the text parameters.
  - **verbosity** (string) - Required - The verbosity level ("low", "medium", or "high").

### Request Example
```json
{
  "model": "gpt-5",
  "input": "What is the answer to the ultimate question of life, the universe, and everything?",
  "text": {
    "verbosity": "low"
  }
}
```
```

--------------------------------

### GET /v1/responses/{response_id}

Source: https://platform.openai.com/docs/api-reference/conversations/list-items

Retrieves the Response object matching the specified ID.

```APIDOC
## GET /v1/responses/{response_id}

### Description
Retrieves the Response object matching the specified ID.

### Method
GET

### Endpoint
/v1/responses/{response_id}

### Parameters
#### Path Parameters
- **response_id** (string) - Required - The ID of the response to retrieve.

### Request Example
```curl
curl https://api.openai.com/v1/responses/resp_123 \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Response
#### Success Response (200)
- **id** (string) - The unique ID of the response.
- **object** (string) - The type of object, typically "response".
- **created_at** (integer) - Unix timestamp when the response was created.
- **status** (string) - The status of the response (e.g., "completed").
- **error** (object/null) - Details of any error, if applicable.
- **incomplete_details** (object/null) - Details if the response is incomplete.
- **instructions** (string/null) - Instructions associated with the response.
- **max_output_tokens** (integer/null) - Maximum output tokens.
- **model** (string) - The model used for the response.
- **output** (array) - An array of output messages.
  - **output[].type** (string) - Type of output, e.g., "message".
  - **output[].id** (string) - ID of the output message.
  - **output[].status** (string) - Status of the output message.
  - **output[].role** (string) - Role of the speaker, e.g., "assistant".
  - **output[].content** (array) - Array of content parts.
    - **output[].content[].type** (string) - Type of content, e.g., "output_text".
    - **output[].content[].text** (string) - The actual text content.
    - **output[].content[].annotations** (array) - Any annotations.
- **parallel_tool_calls** (boolean) - Indicates if parallel tool calls are enabled.
- **previous_response_id** (string/null) - ID of the previous response, if any.
- **reasoning** (object) - Details about reasoning.
  - **reasoning.effort** (string/null) - Effort level.
  - **reasoning.summary** (string/null) - Summary of reasoning.
- **store** (boolean) - Indicates if the response is stored.
- **temperature** (number) - The sampling temperature used.
- **text** (object) - Text formatting details.
  - **text.format** (object) - Format details.
    - **text.format.type** (string) - Type of text format.
- **tool_choice** (string) - Tool choice strategy.
- **tools** (array) - List of tools used.
- **top_p** (number) - The top_p sampling parameter.
- **truncation** (string) - Truncation strategy.
- **usage** (object) - Token usage statistics.
  - **usage.input_tokens** (integer) - Number of input tokens.
  - **usage.input_tokens_details** (object) - Details of input tokens.
  - **usage.output_tokens** (integer) - Number of output tokens.
  - **usage.output_tokens_details** (object) - Details of output tokens.
  - **usage.total_tokens** (integer) - Total tokens used.
- **user** (string/null) - User identifier.
- **metadata** (object) - Additional metadata.

#### Response Example
```json
{
  "id": "resp_67cb71b351908190a308f3859487620d06981a8637e6bc44",
  "object": "response",
  "created_at": 1741386163,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4o-2024-08-06",
  "output": [
    {
      "type": "message",
      "id": "msg_67cb71b3c2b0819084d481baaaf148f206981a8637e6bc44",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "Silent circuits hum,  \nThoughts emerge in data streams—  \nDigital dawn breaks.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 32,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 18,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 50
  },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### Define get_weather function across OpenAI APIs

Source: https://platform.openai.com/docs/guides/responses-vs-chat-completions_api-mode=responses

Compares how the 'get_weather' function is defined in the Chat Completions API versus the Responses API. The Chat Completions API uses externally tagged polymorphism with an explicit 'strict' field, while the Responses API uses internally-tagged polymorphism and is strict by default.

```json
{
  "type": "function",
  "function": {
    "name": "get_weather",
    "description": "Determine weather in my location",
    "strict": true,
    "parameters": {
      "type": "object",
      "properties": {
        "location": {
          "type": "string"
        }
      },
      "additionalProperties": false,
      "required": [
        "location",
        "unit"
      ]
    }
  }
}
```

```json
{
  "type": "function",
  "name": "get_weather",
  "description": "Determine weather in my location",
  "parameters": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string"
      }
    },
    "additionalProperties": false,
    "required": [
      "location",
      "unit"
    ]
  }
}
```

--------------------------------

### Enable OpenAI API Streaming Responses (JavaScript, Python, C#)

Source: https://platform.openai.com/docs/guides/streaming-responses_api-mode=responses

Demonstrates how to enable streaming for OpenAI API responses by setting the `stream` parameter to `true` in the request. This allows the application to process partial outputs as they are generated, improving perceived latency for long responses.

```javascript
import { OpenAI } from "openai";
const client = new OpenAI();

const stream = await client.responses.create({
    model: "gpt-5",
    input: [
        {
            role: "user",
            content: "Say 'double bubble bath' ten times fast.",
        },
    ],
    stream: true,
});

for await (const event of stream) {
    console.log(event);
}
```

```python
from openai import OpenAI
client = OpenAI()

stream = client.responses.create(
    model="gpt-5",
    input=[
        {
            "role": "user",
            "content": "Say 'double bubble bath' ten times fast.",
        },
    ],
    stream=True,
)

for event in stream:
    print(event)
```

```csharp
using OpenAI.Responses;

string key = Environment.GetEnvironmentVariable("OPENAI_API_KEY")!;
OpenAIResponseClient client = new(model: "gpt-5", apiKey: key);

var responses = client.CreateResponseStreamingAsync([
    ResponseItem.CreateUserMessageItem([
        ResponseContentPart.CreateInputTextPart("Say 'double bubble bath' ten times fast."),
    ]),
]);

await foreach (var response in responses)
{
    if (response is StreamingResponseOutputTextDeltaUpdate delta)
    {
        Console.Write(delta.Delta);
    }
}
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/models/gpt-4o-mini-audio-preview

Endpoint for handling responses, which could involve retrieving past interactions or submitting specific response data. The exact functionality is not detailed in the provided text.

```APIDOC
## POST /v1/responses

### Description
Endpoint for handling responses, which could involve retrieving past interactions or submitting specific response data. The exact functionality is not detailed in the provided text.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
_None provided in the source text._

#### Query Parameters
_None provided in the source text._

#### Request Body
_Details not provided in the source text._

### Request Example
{
  "message": "No example request body provided in the source text."
}

### Response
#### Success Response (200)
_Details not provided in the source text._

#### Response Example
{
  "message": "No example response body provided in the source text."
}
```

--------------------------------

### Responses API

Source: https://platform.openai.com/docs/models/o1

Manages general responses from the O1 model. The specific functionality of this endpoint is not detailed but likely relates to retrieving or managing model outputs.

```APIDOC
## POST /v1/responses

### Description
This endpoint is for managing or retrieving responses. The exact usage details are not provided in the source text.

### Method
POST (Assumed; actual method may vary)

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
Not provided in source text.

#### Query Parameters
Not provided in source text.

#### Request Body
Not provided in source text.

### Request Example
```json
{
  "//": "Example request body not provided in source text"
}
```

### Response
#### Success Response (200)
Not provided in source text.

#### Response Example
```json
{
  "//": "Example response body not provided in source text"
}
```
```

--------------------------------

### Responses API - Generate text from a simple prompt

Source: https://platform.openai.com/docs/text

This example demonstrates how to use the Responses API to generate text from a simple prompt. It includes examples in JavaScript, Python, C#, and cURL.

```APIDOC
## POST /v1/responses

### Description
Generates text from a given prompt using a specified model.

### Method
POST

### Endpoint
https://api.openai.com/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The ID of the model to use for generation (e.g., "gpt-5").
- **input** (string) - Required - The prompt text to send to the model.

### Request Example
```json
{
    "model": "gpt-5",
    "input": "Write a one-sentence bedtime story about a unicorn."
}
```

### Response
#### Success Response (200)
- **output** (array) - An array of content generated by the model. Each item in the array can include text, tool calls, and reasoning data.
  - **output_text** (string) - A convenience property on model responses that aggregates all text outputs from the model into a single string.

#### Response Example
```json
[
    {
        "id": "msg_67b73f697ba4819183a15cc17d011509",
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "output_text",
                "text": "Under the soft glow of the moon, Luna the unicorn danced through fields of twinkling stardust, leaving trails of dreams for every child asleep.",
                "annotations": []
            }
        ]
    }
]
```
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/models/gpt-4o-audio-preview

Manages or retrieves responses, potentially for past chat completions or other API interactions.

```APIDOC
## POST /v1/responses

### Description
Manages or retrieves responses, potentially for past chat completions or other API interactions. Specific functionality not detailed in the source.

### Method
POST

### Endpoint
/v1/responses

### Parameters
Specific details not provided in the source text.

#### Request Body
```json
{
  "response_id": "resp_abc123",
  "action": "retrieve"
}
```

### Response
#### Success Response (200)
- **id** (string) - Identifier for the response.
- **status** (string) - Status of the response retrieval.
- **data** (object) - Content of the retrieved response.

#### Response Example
```json
{
  "id": "resp_abc123",
  "status": "success",
  "data": {
    "type": "chat_completion",
    "content": "Hello! How can I help you today?"
  }
}
```
```

--------------------------------

### GET /response_items

Source: https://platform.openai.com/docs/api-reference/conversations/create-items

Retrieves a paginated list of items that were used to generate a model response. This can include messages, user inputs, or other relevant data points.

```APIDOC
## GET /response_items

### Description
Retrieves a paginated list of items that were used to generate a model response. This can include messages, user inputs, or other relevant data points.

### Method
GET

### Endpoint
/response_items

### Parameters
#### Query Parameters
- **limit** (integer) - Optional - A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10.
- **starting_after** (string) - Optional - A cursor for use in pagination. `starting_after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with `obj_foo`, your subsequent call can include `starting_after=obj_foo` in your request to fetch the next page of the list.
- **ending_before** (string) - Optional - A cursor for use in pagination. `ending_before` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, starting with `obj_foo`, your subsequent call can include `ending_before=obj_foo` in your request to fetch the previous page of the list.

### Response
#### Success Response (200)
- **object** (string) - The type of object returned, which must be `list`.
- **data** (array) - A list of items used to generate this response.
  - **id** (string) - The unique identifier of the item.
  - **type** (string) - The type of the item (e.g., "message").
  - **role** (string) - The role associated with the item (e.g., "user").
  - **content** (array) - A list of content parts for the item.
    - **type** (string) - The type of content (e.g., "input_text").
    - **text** (string) - The text content of the item.
- **first_id** (string) - The ID of the first item in the list.
- **has_more** (boolean) - Whether there are more items available beyond the current list.
- **last_id** (string) - The ID of the last item in the list.

#### Response Example
```json
{
  "object": "list",
  "data": [
    {
      "id": "msg_abc123",
      "type": "message",
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": "Tell me a three sentence bedtime story about a unicorn."
        }
      ]
    }
  ],
  "first_id": "msg_abc123",
  "last_id": "msg_abc123",
  "has_more": false
}
```
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/models/text-embedding-ada-002

Endpoint for managing or submitting API responses. The exact functionality would depend on the specific context of 'responses'.

```APIDOC
## POST /v1/responses

### Description
Endpoint for managing or submitting API responses. The exact functionality would depend on the specific context of 'responses'.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
No specific path parameters detailed in the provided text.

#### Query Parameters
No specific query parameters detailed in the provided text.

#### Request Body
No specific request body parameters detailed in the provided text.

### Request Example
```json
{}
```

### Response
#### Success Response (200)
No specific success response fields detailed in the provided text.

#### Response Example
```json
{}
```
```

--------------------------------

### Call OpenAI Responses API (Python)

Source: https://platform.openai.com/docs/guides/migrate-to-responses

This Python example illustrates how to use the OpenAI Responses API to generate content. It sets up the client and calls the `responses.create` method with a specified model and direct string input, then extracts and prints the `output_text` from the response.

```python
from openai import OpenAI
client = OpenAI()

response = client.responses.create(
  model="gpt-5",
  input="Write a one-sentence bedtime story about a unicorn."
)

print(response.output_text)
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/api-reference/assistants/listAssistants

This endpoint allows you to create a new response from an OpenAI model by providing an input prompt.

```APIDOC
## POST /v1/responses

### Description
This endpoint allows you to create a new response from an OpenAI model by providing an input prompt.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The ID of the model to use for generating the response (e.g., "gpt-4.1").
- **input** (string) - Required - The input text for which to generate a response (e.g., "Tell me a three sentence bedtime story about a unicorn.").

### Request Example
{
  "model": "gpt-4.1",
  "input": "Tell me a three sentence bedtime story about a unicorn."
}

### Response
#### Success Response (200)
- **id** (string) - Unique identifier for the response.
- **object** (string) - Type of object, typically "response".
- **created_at** (integer) - Timestamp of when the response was created.
- **status** (string) - Current status of the response (e.g., "completed").
- **error** (object) - Details if an error occurred, null otherwise.
- **incomplete_details** (object) - Details if the response is incomplete.
- **instructions** (array) - List of instructions used.
- **max_output_tokens** (integer) - Maximum number of tokens for output.
- **model** (string) - The model ID used for the response.
- **output** (array) - List of output messages/content generated by the model.
  - **type** (string) - Type of output, e.g., "message".
  - **id** (string) - ID of the output message.
  - **status** (string) - Status of the output message.
  - **role** (string) - Role of the message sender, e.g., "assistant".
  - **content** (array) - List of content parts.
    - **type** (string) - Type of content, e.g., "output_text".
    - **text** (string) - The generated text content.
    - **annotations** (array) - Annotations related to the text.
- **parallel_tool_calls** (boolean) - Indicates if parallel tool calls were used.
- **previous_response_id** (string) - ID of a previous response if applicable.
- **reasoning** (object) - Details about the model's reasoning.
  - **effort** (string) - Effort level.
  - **summary** (string) - Summary of reasoning.
- **store** (boolean) - Indicates if the response is stored.
- **temperature** (number) - Sampling temperature used.
- **text** (object) - Text-specific properties.
  - **format** (object) - Format of the text.
    - **type** (string) - Type of text format.
- **tool_choice** (string) - Tool choice strategy.
- **tools** (array) - List of tools used.
- **top_p** (number) - Top-p sampling value.
- **truncation** (string) - Truncation strategy.
- **usage** (object) - Token usage statistics.
  - **input_tokens** (integer) - Number of input tokens.
  - **input_tokens_details** (object) - Details about input tokens.
    - **cached_tokens** (integer) - Number of cached tokens.
  - **output_tokens** (integer) - Number of output tokens.
  - **output_tokens_details** (object) - Details about output tokens.
    - **reasoning_tokens** (integer) - Number of reasoning tokens.
  - **total_tokens** (integer) - Total number of tokens.
- **user** (string) - User ID.
- **metadata** (object) - Additional metadata.

#### Response Example
{
  "id": "resp_67ccd2bed1ec8190b14f964abc0542670bb6a6b452d3795b",
  "object": "response",
  "created_at": 1741476542,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4.1-2025-04-14",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd2bf17f0819081ff3bb2cf6508e60bb6a6b452d3795b",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "In a peaceful grove beneath a silver moon, a unicorn named Lumina discovered a hidden pool that reflected the stars. As she dipped her horn into the water, the pool began to shimmer, revealing a pathway to a magical realm of endless night skies. Filled with wonder, Lumina whispered a wish for all who dream to find their own hidden magic, and as she glanced back, her hoofprints sparkled like stardust.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 36,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 87,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 123
  },
  "user": null,
  "metadata": {}
}
```

--------------------------------

### GET /v1/responses

Source: https://platform.openai.com/docs/models/gpt-4o-mini-transcribe

Retrieve previous API responses or status. The specific functionality depends on the context of the API design.

```APIDOC
## GET /v1/responses

### Description
Retrieve previous API responses or status. The specific functionality depends on the context of the API design.

### Method
GET

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
_None_

#### Query Parameters
- **response_id** (string) - Optional - The ID of a specific response to retrieve.

#### Request Body
_None_

### Request Example
_None_

### Response
#### Success Response (200)
- **data** (object) - The retrieved response data.

#### Response Example
```json
{
  "response_id": "res-abc-123",
  "status": "completed",
  "result": {
    "message": "This is a retrieved response."
  }
}
```
```

--------------------------------

### GET /v1/responses

Source: https://platform.openai.com/docs/models/whisper-1

Retrieves information about API responses, likely for historical or status purposes.

```APIDOC
## GET /v1/responses

### Description
Retrieves information about API responses, likely for historical or status purposes.

### Method
GET

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
(None)

#### Query Parameters
(None)

#### Request Body
(None)

### Request Example
(None)

### Response
#### Success Response (200)
(None)

#### Response Example
(None)
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/api-reference/batch/object

This endpoint allows you to create a new model response by providing a model and input text. The API will generate a response based on the provided input.

```APIDOC
## POST /v1/responses

### Description
This endpoint allows you to create a new model response by providing a model and input text. The API will generate a response based on the provided input.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
(None)

#### Query Parameters
(None)

#### Request Body
- **model** (string) - Required - The ID of the model to use for generating the response (e.g., "gpt-4.1").
- **input** (string) - Required - The input text for which to generate a response (e.g., "Tell me a three sentence bedtime story about a unicorn.").

### Request Example
```json
{
  "model": "gpt-4.1",
  "input": "Tell me a three sentence bedtime story about a unicorn."
}
```

### Response
#### Success Response (200)
- **id** (string) - Unique identifier for the response.
- **object** (string) - Type of object, typically "response".
- **created_at** (integer) - Unix timestamp (in seconds) when the response was created.
- **status** (string) - Current status of the response (e.g., "completed").
- **error** (object|null) - Details of any error that occurred, if applicable.
- **incomplete_details** (object|null) - Details if the response is incomplete.
- **instructions** (object|null) - Any instructions related to the response generation.
- **max_output_tokens** (integer|null) - Maximum number of output tokens allowed.
- **model** (string) - The specific model version used to generate the response.
- **output** (array) - An array of generated output messages.
  - **type** (string) - The type of output, e.g., "message".
  - **id** (string) - Unique identifier for the output message.
  - **status** (string) - Status of the output message.
  - **role** (string) - The role of the entity generating this output, e.g., "assistant".
  - **content** (array) - An array of content parts within the message.
    - **type** (string) - The type of content, e.g., "output_text".
    - **text** (string) - The actual generated text content.
    - **annotations** (array) - Any annotations associated with the text.
- **parallel_tool_calls** (boolean) - Indicates if parallel tool calls were made.
- **previous_response_id** (string|null) - ID of a previous response if this is a follow-up.
- **reasoning** (object) - Details about the reasoning process.
  - **effort** (string|null) - Effort level of the reasoning.
  - **summary** (string|null) - Summary of the reasoning.
- **store** (boolean) - Indicates if the response was stored.
- **temperature** (number) - The sampling temperature used.
- **text** (object) - Details about the text format.
  - **format** (object)
    - **type** (string) - Format type, e.g., "text".
- **tool_choice** (string) - Strategy for tool choice, e.g., "auto".
- **tools** (array) - List of tools used or available.
- **top_p** (number) - The top_p sampling value used.
- **truncation** (string) - Truncation strategy, e.g., "disabled".
- **usage** (object) - Token usage statistics for the request.
  - **input_tokens** (integer) - Number of tokens in the input.
  - **input_tokens_details** (object)
    - **cached_tokens** (integer) - Number of cached input tokens.
  - **output_tokens** (integer) - Number of tokens in the output.
  - **output_tokens_details** (object)
    - **reasoning_tokens** (integer) - Number of tokens used for reasoning.
  - **total_tokens** (integer) - Total number of tokens used.
- **user** (string|null) - Identifier for the end-user.
- **metadata** (object) - Arbitrary metadata associated with the response.

#### Response Example
```json
{
  "id": "resp_67ccd2bed1ec8190b14f964abc0542670bb6a6b452d3795b",
  "object": "response",
  "created_at": 1741476542,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4.1-2025-04-14",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd2bf17f0819081ff3bb2cf6508e60bb6a6b452d3795b",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "In a peaceful grove beneath a silver moon, a unicorn named Lumina discovered a hidden pool that reflected the stars. As she dipped her horn into the water, the pool began to shimmer, revealing a pathway to a magical realm of endless night skies. Filled with wonder, Lumina whispered a wish for all who dream to find their own hidden magic, and as she glanced back, her hoofprints sparkled like stardust.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 36,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 87,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 123
  },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### GET /v1/responses/{response_id}

Source: https://platform.openai.com/docs/api-reference/assistants/createAssistant

Retrieves the Response object matching the specified ID, providing details about its status, output, and usage.

```APIDOC
## GET /v1/responses/{response_id}

### Description
Retrieves the Response object matching the specified ID.

### Method
GET

### Endpoint
/v1/responses/{response_id}

### Parameters
#### Path Parameters
- **response_id** (string) - Required - The ID of the response to retrieve.

#### Query Parameters
None

#### Request Body
None

### Request Example
```curl
curl https://api.openai.com/v1/responses/resp_123 \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Response
#### Success Response (200)
- **id** (string) - Unique identifier for the response.
- **object** (string) - The object type, typically "response".
- **created_at** (integer) - Timestamp when the response was created.
- **status** (string) - Current status of the response (e.g., "completed").
- **error** (object/null) - Error details if the response failed.
- **incomplete_details** (object/null) - Details if the response is incomplete.
- **instructions** (object/null) - Instructions provided to the model.
- **max_output_tokens** (integer/null) - Maximum output tokens allowed.
- **model** (string) - The model used for the response.
- **output** (array) - An array of output messages or content.
- **parallel_tool_calls** (boolean) - Indicates if parallel tool calls were enabled.
- **previous_response_id** (string/null) - ID of the previous response in a conversation.
- **reasoning** (object) - Details about the model's reasoning.
- **store** (boolean) - Indicates if the response is stored.
- **temperature** (number) - The sampling temperature used.
- **text** (object) - Text formatting details.
- **tool_choice** (string) - Tool choice setting.
- **tools** (array) - List of tools used.
- **top_p** (number) - The top_p sampling value.
- **truncation** (string) - Truncation strategy.
- **usage** (object) - Token usage statistics.
- **user** (string/null) - User identifier.
- **metadata** (object) - Custom metadata.

#### Response Example
```json
{
  "id": "resp_67cb71b351908190a308f3859487620d06981a8637e6bc44",
  "object": "response",
  "created_at": 1741386163,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4o-2024-08-06",
  "output": [
    {
      "type": "message",
      "id": "msg_67cb71b3c2b0819084d481baaaf148f206981a8637e6bc44",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "Silent circuits hum,  \nThoughts emerge in data streams—  \nDigital dawn breaks.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 32,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 18,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 50
  },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/api-reference/runs/listRuns

Creates a new model response based on the provided input and model. This endpoint allows users to send text prompts to a specified model and receive generated content.

```APIDOC
## POST /v1/responses

### Description
Creates a new model response based on the provided input and model. This endpoint allows users to send text prompts to a specified model and receive generated content.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
(None)

#### Query Parameters
(None)

#### Request Body
- **model** (string) - Required - The model to use for generating the response (e.g., "gpt-4.1").
- **input** (string) - Required - The text input or prompt for the model.

### Request Example
```json
{
  "model": "gpt-4.1",
  "input": "Tell me a three sentence bedtime story about a unicorn."
}
```

### Response
#### Success Response (200)
- **id** (string) - Unique identifier for the response.
- **object** (string) - Type of object, usually "response".
- **created_at** (integer) - Timestamp of creation.
- **status** (string) - Status of the response (e.g., "completed").
- **error** (object/null) - Error details if any.
- **incomplete_details** (object/null) - Details if the response is incomplete.
- **instructions** (object/null) - Instructions used for generation.
- **max_output_tokens** (integer/null) - Maximum tokens allowed in the output.
- **model** (string) - The model used for generation.
- **output** (array) - Array of output messages.
  - **type** (string) - Type of output, e.g., "message".
  - **id** (string) - ID of the message.
  - **status** (string) - Status of the message.
  - **role** (string) - Role of the message sender, e.g., "assistant".
  - **content** (array) - Array of content parts.
    - **type** (string) - Type of content, e.g., "output_text".
    - **text** (string) - The generated text content.
    - **annotations** (array) - Any annotations in the text.
- **parallel_tool_calls** (boolean) - Indicates if parallel tool calls are enabled.
- **previous_response_id** (string/null) - ID of previous response if chained.
- **reasoning** (object) - Details about the model's reasoning process.
  - **effort** (string/null) - Effort level.
  - **summary** (string/null) - Summary of reasoning.
- **store** (boolean) - Whether the response is stored.
- **temperature** (number) - Sampling temperature used.
- **text** (object) - Text-specific formatting options.
  - **format** (object)
    - **type** (string) - Format type, e.g., "text".
- **tool_choice** (string) - Tool choice strategy.
- **tools** (array) - List of tools used.
- **top_p** (number) - Top-p sampling value.
- **truncation** (string) - Truncation strategy.
- **usage** (object) - Token usage statistics.
  - **input_tokens** (integer) - Number of input tokens.
  - **input_tokens_details** (object)
    - **cached_tokens** (integer) - Number of cached input tokens.
  - **output_tokens** (integer) - Number of output tokens.
  - **output_tokens_details** (object)
    - **reasoning_tokens** (integer) - Number of reasoning tokens.
  - **total_tokens** (integer) - Total tokens used.
- **user** (string/null) - User identifier.
- **metadata** (object) - Additional metadata.

#### Response Example
```json
{
  "id": "resp_67ccd2bed1ec8190b14f964abc0542670bb6a6b452d3795b",
  "object": "response",
  "created_at": 1741476542,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4.1-2025-04-14",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd2bf17f0819081ff3bb2cf6508e60bb6a6b452d3795b",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "In a peaceful grove beneath a silver moon, a unicorn named Lumina discovered a hidden pool that reflected the stars. As she dipped her horn into the water, the pool began to shimmer, revealing a pathway to a magical realm of endless night skies. Filled with wonder, Lumina whispered a wish for all who dream to find their own hidden magic, and as she glanced back, her hoofprints sparkled like stardust.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 36,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 87,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 123
  },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### Image Generation API Response

Source: https://platform.openai.com/docs/api-reference/certificates/object

Describes the structure of the successful response object returned by the image generation API for non-streaming requests.

```APIDOC
## Image Generation API Response

### Description
Structure of the response object returned by the image generation API for non-streaming requests.

### Response
#### Success Response (200)
- **created** (integer) - The Unix timestamp (in seconds) of when the image was created.
- **data** (array) - The list of generated images. Each item contains a `b64_json` string.
- **background** (string) - The background parameter used for the image generation. Either `transparent` or `opaque`.
- **output_format** (string) - The output format of the image generation. Either `png`, `webp`, or `jpeg`.
- **quality** (string) - The quality of the image generated. Either `low`, `medium`, or `high`.
- **size** (string) - The size of the image generated. Either `1024x1024`, `1024x1536`, or `1536x1024`.
- **usage** (object) - For `gpt-image-1` only, the token usage information for the image generation. Includes `total_tokens`, `input_tokens`, `output_tokens`, and `input_tokens_details`.

#### Response Example
```json
{
  "created": 1713833628,
  "data": [
    {
      "b64_json": "..."
    }
  ],
  "background": "transparent",
  "output_format": "png",
  "size": "1024x1024",
  "quality": "high",
  "usage": {
    "total_tokens": 100,
    "input_tokens": 50,
    "output_tokens": 50,
    "input_tokens_details": {
      "text_tokens": 10,
      "image_tokens": 40
    }
  }
}
```
```

--------------------------------

### Response Generation API Parameters and Object

Source: https://platform.openai.com/docs/api-reference/realtime-server-events/response/output_text/delta

This section details the parameters that can be used when generating a model response and describes the structure of the successful response object.

```APIDOC
## POST /generate_response (Hypothetical)

### Description
Describes the various parameters for configuring how the model generates a response and the structure of the response object returned.

### Method
POST (Hypothetical)

### Endpoint
/generate_response (Hypothetical)

### Parameters
#### Request Body
- **tool_choice** (string or object) - Optional - How the model should select which tool (or tools) to use when generating a response. See the `tools` parameter to see how to specify which tools the model can call.
- **tools** (array) - Optional - An array of tools the model may call while generating a response. Categories include Built-in tools, MCP Tools, and Function calls (custom tools).
- **top_logprobs** (integer) - Optional - An integer between 0 and 20 specifying the number of most likely tokens to return at each token position, each with an associated log probability.
- **top_p** (number) - Optional - An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. Generally recommended to alter this or `temperature` but not both.
- **truncation** (string) - Optional - The truncation strategy to use for the model response.
  - `auto`: If the input to this Response exceeds the model's context window size, the model will truncate the response to fit the context window by dropping items from the beginning of the conversation.
  - `disabled` (default): If the input size will exceed the context window size for a model, the request will fail with a 400 error.
- **user** (string) - Deprecated, Optional - A stable identifier for your end-users. Used to boost cache hit rates by better bucketing similar requests and to help OpenAI detect and prevent abuse. Replaced by `safety_identifier` and `prompt_cache_key`.

### Request Example
```json
{
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1,
  "truncation": "disabled",
  "user": "user-123"
}
```

### Response
#### Success Response (200)
- **id** (string) - The unique identifier for the response.
- **object** (string) - The type of object returned, typically "response".
- **created_at** (integer) - Timestamp when the response was created.
- **status** (string) - The status of the response generation (e.g., "completed").
- **error** (object) - Details if an error occurred.
- **incomplete_details** (object) - Details if the response was incomplete.
- **instructions** (object) - Any instructions provided.
- **max_output_tokens** (integer) - The maximum number of output tokens.
- **model** (string) - The model used to generate the response.
- **output** (array) - An array of output messages or content generated by the model.
  - **type** (string) - Type of output (e.g., "message").
  - **id** (string) - ID of the message.
  - **status** (string) - Status of the message.
  - **role** (string) - Role of the message sender (e.g., "assistant").
  - **content** (array) - Array of content parts.
    - **type** (string) - Type of content (e.g., "output_text").
    - **text** (string) - The generated text content.
    - **annotations** (array) - Any annotations.
- **parallel_tool_calls** (boolean) - Indicates if parallel tool calls were made.
- **previous_response_id** (string) - ID of the previous response, if any.
- **reasoning** (object) - Details about the model's reasoning.
  - **effort** (string) - Effort level.
  - **summary** (string) - Summary of reasoning.
- **store** (boolean) - Whether the response should be stored.
- **temperature** (number) - The sampling temperature used.
- **text** (object) - Text formatting details.
  - **format** (object) - Format specifics.
    - **type** (string) - Format type (e.g., "text").
- **tool_choice** (string) - How the model selected tools.
- **tools** (array) - List of tools used.
- **top_p** (number) - The top_p value used.
- **truncation** (string) - The truncation strategy used.
- **usage** (object) - Token usage details.
  - **input_tokens** (integer) - Number of input tokens.
  - **input_tokens_details** (object) - Details about input tokens.
    - **cached_tokens** (integer) - Number of cached tokens.
  - **output_tokens** (integer) - Number of output tokens.
  - **output_tokens_details** (object) - Details about output tokens.
    - **reasoning_tokens** (integer) - Number of reasoning tokens.
  - **total_tokens** (integer) - Total number of tokens.
- **user** (string) - User identifier.
- **metadata** (object) - Additional metadata.

#### Response Example
```json
{
  "id": "resp_67ccd3a9da748190baa7f1570fe91ac604becb25c45c1d41",
  "object": "response",
  "created_at": 1741476777,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4o-2024-08-06",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd3acc8d48190a77525dc6de64b4104becb25c45c1d41",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "The image depicts a scenic landscape with a wooden boardwalk or pathway leading through lush, green grass under a blue sky with some clouds. The setting suggests a peaceful natural area, possibly a park or nature reserve. There are trees and shrubs in the background.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 328,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 52,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 380
  },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### Response Object

Source: https://platform.openai.com/docs/api-reference/container-files/retrieveContainerFile

Details the structure of the response object returned by the API.

```APIDOC
## Object: Response

### Description
The response object returned by the API.

### Properties
- **id** (string) - Unique identifier for the response
- **object** (string) - Type of object, should be "response"
- **created_at** (integer) - Timestamp of creation
- **status** (string) - Status of the request (e.g., completed)
- **output** (array) - Array of message objects
- **usage** (object) - Token usage details

```

--------------------------------

### Implement User Chat with OpenAI Responses API (Python)

Source: https://platform.openai.com/docs/assistants/migration

This Python example illustrates how to create a user chat application utilizing the OpenAI Responses API. The process involves creating a conversation and then directly sending user input to a specified prompt to receive an immediate text response. It depends on the OpenAI Python library and a 'PROMPT_ID' configured in environment variables.

```Python
conversation = openai.conversations.create()

@app.post("/messages")
async def message(message: Message):
	response = openai.responses.create(
		prompt={ "id": os.getenv("PROMPT_ID") },
		input=[{ "role": "user", "content": message.content }]
	)

	return { "content": response.output_text }
```

--------------------------------

### GET /v1/responses/{response_id}

Source: https://platform.openai.com/docs/api-reference/fine-tuning/list

Retrieves the Response object matching the specified ID.

```APIDOC
## GET /v1/responses/{response_id}

### Description
Retrieves the Response object matching the specified ID.

### Method
GET

### Endpoint
/v1/responses/{response_id}

### Parameters
#### Path Parameters
- **response_id** (string) - Required - The ID of the response to retrieve.

#### Query Parameters

#### Request Body

### Request Example
```json
{
  "example": "curl https://api.openai.com/v1/responses/resp_123 \
    -H \"Content-Type: application/json\" \
    -H \"Authorization: Bearer $OPENAI_API_KEY\""
}
```

### Response
#### Success Response (200)
- **id** (string) - Unique identifier for the response.
- **object** (string) - The type of object, typically "response".
- **created_at** (integer) - Timestamp when the response was created.
- **status** (string) - Current status of the response (e.g., "completed").
- **error** (object/null) - Error details if the response failed.
- **incomplete_details** (object/null) - Details if the response is incomplete.
- **instructions** (object/null) - Instructions used for the response.
- **max_output_tokens** (integer/null) - Maximum output tokens set for the response.
- **model** (string) - The model used to generate the response.
- **output** (array) - An array of output messages or content.
  - **type** (string) - Type of output, e.g., "message".
  - **id** (string) - Unique identifier for the output message.
  - **status** (string) - Status of the output message.
  - **role** (string) - Role of the message sender, e.g., "assistant".
  - **content** (array) - Array of content parts.
    - **type** (string) - Type of content, e.g., "output_text".
    - **text** (string) - The generated text content.
    - **annotations** (array) - Any annotations within the text.
- **parallel_tool_calls** (boolean) - Indicates if parallel tool calls are enabled.
- **previous_response_id** (string/null) - ID of the previous response if chained.
- **reasoning** (object) - Details about the reasoning process.
  - **effort** (object/null) - Effort level of reasoning.
  - **summary** (string/null) - Summary of reasoning.
- **store** (boolean) - Indicates if the response is stored.
- **temperature** (number) - Temperature setting used for generation.
- **text** (object) - Text formatting details.
  - **format** (object) - Format of the text.
    - **type** (string) - Type of text format.
- **tool_choice** (string) - Tool choice setting.
- **tools** (array) - Tools used in the response.
- **top_p** (number) - Top P setting used for generation.
- **truncation** (string) - Truncation setting.
- **usage** (object) - Token usage statistics.
  - **input_tokens** (integer) - Number of input tokens.
  - **input_tokens_details** (object) - Details about input tokens.
    - **cached_tokens** (integer) - Number of cached input tokens.
  - **output_tokens** (integer) - Number of output tokens.
  - **output_tokens_details** (object) - Details about output tokens.
    - **reasoning_tokens** (integer) - Number of reasoning tokens.
  - **total_tokens** (integer) - Total number of tokens.
- **user** (object/null) - User associated with the response.
- **metadata** (object) - Additional metadata.

#### Response Example
```json
{
  "id": "resp_67cb71b351908190a308f3859487620d06981a8637e6bc44",
  "object": "response",
  "created_at": 1741386163,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4o-2024-08-06",
  "output": [
    {
      "type": "message",
      "id": "msg_67cb71b3c2b0819084d481baaaf148f206981a8637e6bc44",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "Silent circuits hum,  \nThoughts emerge in data streams—  \nDigital dawn breaks.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 32,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 18,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 50
  },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/models/gpt-oss-120b

Handle and process model responses. This endpoint likely allows for specific interactions related to the model's output.

```APIDOC
## POST /v1/responses

### Description
Handle and process model responses. This endpoint likely allows for specific interactions related to the model's output.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
Not provided in the source text.

#### Query Parameters
Not provided in the source text.

#### Request Body
Not provided in the source text.

### Request Example
{
  "example": "Not provided in the source text"
}

### Response
#### Success Response (200)
Not provided in the source text.

#### Response Example
{
  "example": "Not provided in the source text"
}
```

--------------------------------

### Assistants API Thread Object Response Structure

Source: https://platform.openai.com/docs/assistants/migration

JSON representation of a thread object returned by the deprecated OpenAI Assistants API. It includes identifiers, creation timestamp, and any associated metadata.

```json
{
"id": "thread_CrXtCzcyEQbkAcXuNmVSKFs1",
"object": "thread",
"created_at": 1752855924,
"metadata": {
  "user_id": "peter_le_fleur"
},
"tool_resources": {}
}
```

--------------------------------

### POST /response.create

Source: https://platform.openai.com/docs/api-reference/fine-tuning/list

Instructs the server to create a Response, triggering model inference. Responses can include items appended to conversation history and can be configured with specific instructions or tools. It supports out-of-band responses that do not write to the default conversation.

```APIDOC
## POST /response.create

### Description
This event instructs the server to create a Response, which means triggering model inference. When in Server VAD mode, the server will create Responses automatically. A Response will include at least one Item, and may have two, in which case the second will be a function call. These Items will be appended to the conversation history by default. The server will respond with a `response.created` event, events for Items and content created, and finally a `response.done` event to indicate the Response is complete. The `response.create` event includes inference configuration like `instructions` and `tools`. If these are set, they will override the Session's configuration for this Response only. Responses can be created out-of-band of the default Conversation, meaning that they can have arbitrary input, and it's possible to disable writing the output to the Conversation. Only one Response can write to the default Conversation at a time, but otherwise multiple Responses can be created in parallel. The `metadata` field is a good way to disambiguate multiple simultaneous Responses. Clients can set `conversation` to `none` to create a Response that does not write to the default Conversation. Arbitrary input can be provided with the `input` field, which is an array accepting raw Items and references to existing Items.

### Method
POST

### Endpoint
/response.create

### Parameters
#### Request Body
- **event_id** (string) - Optional - Client-generated ID used to identify this event.
- **response** (object) - Optional - Create a new Realtime response with these parameters. If omitted, a default response will be created.
  - **instructions** (string) - Optional - Specific instructions for the model inference.
  - **tools** (array) - Optional - An array of tools to use for this response. Can be an empty array to clear session tools.
  - **conversation** (string) - Optional - Set to `"none"` to prevent the response from writing to the default Conversation. Defaults to writing to the default Conversation.
  - **output_modalities** (array) - Optional - An array of desired output modalities (e.g., `["text"]`).
  - **metadata** (object) - Optional - Custom metadata associated with the response, useful for disambiguating multiple simultaneous responses.
  - **input** (array) - Optional - An array accepting raw Items or references to existing Items, providing arbitrary input for the response.
- **type** (string) - Required - The event type, must be `response.create`.

### Request Example
```json
// Trigger a response with the default Conversation and no special parameters
{
  "type": "response.create"
}

// Trigger an out-of-band response that does not write to the default Conversation
{
  "type": "response.create",
  "response": {
    "instructions": "Provide a concise answer.",
    "tools": [], // clear any session tools
    "conversation": "none",
    "output_modalities": ["text"],
    "metadata": {
      "response_purpose": "summarization"
    },
    "input": [
      {
        "type": "item_reference",
        "id": "item_12345"
      },
      {
        "type": "message",
        "role": "user",
        "content": [
          {
            "type": "input_text",
            "text": "Summarize the above message in one sentence."
          }
        ]
      }
    ]
  }
}
```

### Response
#### Success Response (200)
- The server will respond with a `response.created` event, followed by events for any Items and content created, and finally a `response.done` event.

#### Response Example
```json
{
  "type": "response.created",
  "response_id": "response_456",
  "event_id": "client_event_id_optional"
}
```
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/guides/your-data

Generates responses based on the given input. `computer-use-preview` snapshots are only supported for US/EU. Cannot set `background=True` in EU region.

```APIDOC
## POST /v1/responses

### Description
Generates responses based on the given input.

### Method
POST

### Endpoint
/v1/responses

### Parameters
N/A

### Request Body
- **input** (string) - Required - The input text to generate a response.
- **model** (string) - Required - The model to use for generating the response.

### Request Example
{
  "model": "gpt-4",
  "input": "What is the capital of France?"
}

### Response
#### Success Response (200)
- **response** (string) - The generated response.

#### Response Example
{
  "response": "The capital of France is Paris."
}

### Limitations
`computer-use-preview` snapshots are only supported for US/EU.
Cannot set `background=True` in EU region.

```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/api-reference/realtime-server-events/conversation/item/done

Creates a new model response using a specified model and input text. This endpoint allows users to send prompts to an OpenAI model and receive a generated response.

```APIDOC
## POST /v1/responses

### Description
Creates a new model response by sending input text to a specified OpenAI model.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for generating the response (e.g., "gpt-4.1").
- **input** (string) - Required - The text input or prompt for the model.

### Request Example
```json
{
  "model": "gpt-4.1",
  "input": "Tell me a three sentence bedtime story about a unicorn."
}
```

### Response
#### Success Response (200)
- **id** (string) - Unique identifier for the generated response.
- **object** (string) - The type of object, typically "response".
- **created_at** (integer) - Unix timestamp when the response was created.
- **status** (string) - Current status of the response (e.g., "completed").
- **error** (object|null) - Contains error details if the request failed.
- **incomplete_details** (object|null) - Provides details if the response is incomplete.
- **instructions** (object|null) - Instructions provided to the model.
- **max_output_tokens** (integer|null) - The maximum number of tokens allowed in the output.
- **model** (string) - The specific model used for this response (e.g., "gpt-4.1-2025-04-14").
- **output** (array) - An array of output messages from the model.
  - **output[].type** (string) - The type of output, e.g., "message".
  - **output[].id** (string) - Identifier for the output message.
  - **output[].status** (string) - Status of the output message.
  - **output[].role** (string) - The role of the entity generating the content, e.g., "assistant".
  - **output[].content** (array) - An array of content parts within the message.
    - **output[].content[].type** (string) - Type of content, e.g., "output_text".
    - **output[].content[].text** (string) - The actual text content generated by the model.
    - **output[].content[].annotations** (array) - Any annotations associated with the text.
- **parallel_tool_calls** (boolean) - Indicates if parallel tool calls were enabled.
- **previous_response_id** (string|null) - The ID of a previous response if applicable.
- **reasoning** (object) - Details about the model's reasoning process.
  - **reasoning.effort** (null) - Effort expended by the model (currently null).
  - **reasoning.summary** (null) - Summary of the model's reasoning (currently null).
- **store** (boolean) - Indicates if the response is stored.
- **temperature** (number) - The sampling temperature used for generation.
- **text** (object) - Details about the text format.
  - **text.format** (object)
    - **text.format.type** (string) - The format type of the text, e.g., "text".
- **tool_choice** (string) - The tool choice setting, e.g., "auto".
- **tools** (array) - A list of tools used in the response.
- **top_p** (number) - The nucleus sampling parameter used for generation.
- **truncation** (string) - The truncation strategy used, e.g., "disabled".
- **usage** (object) - Details about token usage for the request.
  - **usage.input_tokens** (integer) - Number of tokens in the input prompt.
  - **usage.input_tokens_details** (object)
    - **usage.input_tokens_details.cached_tokens** (integer) - Number of cached input tokens.
  - **usage.output_tokens** (integer) - Number of tokens in the generated output.
  - **usage.output_tokens_details** (object)
    - **usage.output_tokens_details.reasoning_tokens** (integer) - Tokens used for reasoning.
  - **usage.total_tokens** (integer) - Total number of tokens (input + output).
- **user** (string|null) - Identifier for the user associated with the request.
- **metadata** (object) - Additional metadata.

#### Response Example
```json
{
  "id": "resp_67ccd2bed1ec8190b14f964abc0542670bb6a6b452d3795b",
  "object": "response",
  "created_at": 1741476542,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4.1-2025-04-14",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd2bf17f0819081ff3bb2cf6508e60bb6a6b452d3795b",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "In a peaceful grove beneath a silver moon, a unicorn named Lumina discovered a hidden pool that reflected the stars. As she dipped her horn into the water, the pool began to shimmer, revealing a pathway to a magical realm of endless night skies. Filled with wonder, Lumina whispered a wish for all who dream to find their own hidden magic, and as she glanced back, her hoofprints sparkled like stardust.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 36,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 87,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 123
  },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### Migrating to Responses API for GPT-5

Source: https://platform.openai.com/docs/guides/latest-model_gallery=open&galleryitem=audio-step-sequencer

Details the differences between the Chat Completions API and the Responses API for GPT-5, focusing on passing chain of thought (CoT).

```APIDOC
## Migrating from Chat Completions to Responses API

### Description
The main reason to migrate from Chat Completions to the Responses API for GPT-5 is the support for passing chain of thought (CoT) between turns. This section provides examples of how parameters are handled differently between the two APIs.

### Reasoning Effort
Demonstrates how to generate a response with minimal reasoning using both APIs.

#### Responses API
```
curl --request POST \
--url https://api.openai.com/v1/responses \
--header "Authorization: Bearer $OPENAI_API_KEY" \
--header 'Content-type: application/json' \
--data '{
  "model": "gpt-5",
  "input": "How much gold would it take to coat the Statue of Liberty in a 1mm layer?",
  "reasoning": {
    "effort": "minimal"
  }
}'
```

#### Chat Completions
```
curl --request POST \
--url https://api.openai.com/v1/chat/completions \
--header "Authorization: Bearer $OPENAI_API_KEY" \
--header 'Content-type: application/json' \
--data '{
  "model": "gpt-5",
  "messages": [
    {
      "role": "user",
      "content": "How much gold would it take to coat the Statue of Liberty in a 1mm layer?"
    }
  ],
  "reasoning_effort": "minimal"
}'
```

### Verbosity
Shows how to control verbosity using both APIs.

#### Responses API
```
curl --request POST \
--url https://api.openai.com/v1/responses \
--header "Authorization: Bearer $OPENAI_API_KEY" \
--header 'Content-type: application/json' \
--data '{
  "model": "gpt-5",
  "input": "What is the answer to the ultimate question of life, the universe, and everything?",
  "text": {
    "verbosity": "low"
  }
}'
```

#### Chat Completions
```
curl --request POST \
--url https://api.openai.com/v1/chat/completions \
--header "Authorization: Bearer $OPENAI_API_KEY" \
--header 'Content-type: application/json' \
--data '{
  "model": "gpt-5",
  "messages": [
    { "role": "user", "content": "What is the answer to the ultimate question of life, the universe, and everything?" }
  ],
  "verbosity": "low"
}'
```

### Custom Tools
Demonstrates how to use custom tools with both APIs.

#### Responses API
```
curl --request POST --url https://api.openai.com/v1/responses --header "Authorization: Bearer $OPENAI_API_KEY" --header 'Content-type: application/json' --data '{
  "model": "gpt-5",
  "input": "Use the code_exec tool to calculate the area of a circle with radius equal to the number of r letters in blueberry",
  "tools": [
    {
      "type": "custom",
      "name": "code_exec",
      "description": "Executes arbitrary python code"
    }
  ]
}'
```

#### Chat Completions
```
curl --request POST --url https://api.openai.com/v1/chat/completions --header "Authorization: Bearer $OPENAI_API_KEY" --header 'Content-type: application/json' --data '{
  "model": "gpt-5",
  "messages": [
    { "role": "user", "content": "Use the code_exec tool to calculate the area of a circle with radius equal to the number of r letters in blueberry" }
  ],
  "tools": [
    {
      "type": "custom",
      "custom": {
        "name": "code_exec",
        "description": "Executes arbitrary python code"
      }
    }
  ]
}'
```
```

--------------------------------

### response.create

Source: https://platform.openai.com/docs/api-reference/container-files/object

Instructs the server to create a Response, triggering model inference. Responses can be configured with specific instructions, tools, and input, and can optionally be created out-of-band without writing to the default conversation.

```APIDOC
## EVENT response.create

### Description
This event instructs the server to create a Response, which means triggering model inference. When in Server VAD mode, the server will create Responses automatically. A Response will include at least one Item, and may have two, in which case the second will be a function call. These Items will be appended to the conversation history. The server will respond with a `response.created` event, events for Items and content created, and finally a `response.done` event to indicate the Response is complete. The `response.create` event can optionally include inference configuration like `instructions`, and `temperature`. These fields will override the Session's configuration for this Response only. Responses can be created out-of-band of the default Conversation, meaning that they can have arbitrary input, and it's possible to disable writing the output to the Conversation. Only one Response can write to the default Conversation at a time, but otherwise multiple Responses can be created in parallel. Clients can set `conversation` to `none` to create a Response that does not write to the default Conversation. Arbitrary input can be provided with the `input` field, which is an array accepting raw Items and references to existing Items.

### Method
EVENT

### Endpoint
response.create

### Parameters
#### Request Body
- **type** (string) - Required - The event type, must be `response.create`.
- **event_id** (string) - Optional - Client-generated ID used to identify this event.
- **response** (object) - Optional - Create a new Realtime response with these parameters.
  - **instructions** (string) - Optional - Specific instructions for the model inference.
  - **temperature** (number) - Optional - Controls the randomness of the model's output.
  - **tools** (array) - Optional - A list of tools to be used for this response. An empty array clears any session tools.
  - **conversation** (string) - Optional - Specifies which conversation to write to. Use "none" for an out-of-band response that does not write to the default conversation.
  - **output_modalities** (array) - Optional - A list of output modalities for the response (e.g., ["text"]).
  - **input** (array) - Optional - An array of items providing arbitrary input for the response.
    - **type** (string) - Required - The type of input item (e.g., "item_reference", "message").
    - **id** (string) - Optional - For `item_reference`, the ID of an existing item.
    - **role** (string) - Optional - For `message`, the role of the message's sender (e.g., "user").
    - **content** (array) - Optional - For `message`, an array of content parts.
      - **type** (string) - Required - The type of content part (e.g., "input_text").
      - **text** (string) - Required - The text content.

### Request Example
```json
[
  {
    "type": "response.create"
  },
  {
    "type": "response.create",
    "response": {
      "instructions": "Provide a concise answer.",
      "tools": [],
      "conversation": "none",
      "output_modalities": [
        "text"
      ],
      "input": [
        {
          "type": "item_reference",
          "id": "item_12345"
        },
        {
          "type": "message",
          "role": "user",
          "content": [
            {
              "type": "input_text",
              "text": "Summarize the above message in one sentence."
            }
          ]
        }
      ]
    }
  }
]
```

### Response
#### Success Response
Upon creation, the server responds with a `response.created` event, followed by events for Items and content created, and finally a `response.done` event.

#### Response Example
No explicit example provided, but implied sequence of `response.created`, `item.created`, `content.created`, `response.done` events.
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/guides/reasoning

Call the Responses API to leverage advanced reasoning models. This endpoint allows you to send prompts and receive responses from models like GPT-5, with configurable reasoning effort.

```APIDOC
## POST /v1/responses

### Description
This endpoint allows you to interact with OpenAI's advanced reasoning models (e.g., GPT-5) to generate complex and well-reasoned responses. It supports specifying reasoning effort and includes token usage details in the response.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
_None_

#### Query Parameters
_None_

#### Request Body
- **model** (string) - Required - The ID of the model to use for the response (e.g., "gpt-5", "gpt-5-mini", "gpt-5-nano").
- **reasoning** (object) - Optional - Configuration for the model's reasoning process.
  - **effort** (string) - Required (if reasoning object is present) - Guides the model on how many reasoning tokens to generate. Accepts "low", "medium", or "high". "low" favors speed, "high" favors completeness. Default is "medium".
- **input** (array of objects) - Required - A list of messages comprising the conversation so far.
  - Each object in the array represents a message with the following fields:
    - **role** (string) - Required - The role of the author of this message. Values: "user", "system", or "assistant".
    - **content** (string) - Required - The content of the message.
- **max_output_tokens** (integer) - Optional - The maximum number of tokens to generate in the completion, including both reasoning and final output tokens. Useful for cost management.

### Request Example
```json
{
  "model": "gpt-5",
  "reasoning": {"effort": "medium"},
  "input": [
    {
      "role": "user",
      "content": "Write a bash script that takes a matrix represented as a string with format \"[1,2],[3,4],[5,6]\" and prints the transpose in the same format."
    }
  ]
}
```

### Response
#### Success Response (200)
- **output_text** (string) - The model's generated response content.
- **usage** (object) - Details about the token usage for the request.
  - **input_tokens** (integer) - The number of tokens in the input prompt.
  - **input_tokens_details** (object) - Further details on input tokens.
    - **cached_tokens** (integer) - Number of cached input tokens.
  - **output_tokens** (integer) - The total number of tokens generated as output, including both reasoning and final output tokens.
  - **output_tokens_details** (object) - Further details on output tokens.
    - **reasoning_tokens** (integer) - The number of tokens used by the model for internal reasoning before generating the final response.
  - **total_tokens** (integer) - The sum of input_tokens and output_tokens.

#### Response Example
```json
{
  "output_text": "#!/bin/bash\n\nmatrix_str=\"$1\"\n...",
  "usage": {
    "input_tokens": 75,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 1186,
    "output_tokens_details": {
      "reasoning_tokens": 1024
    },
    "total_tokens": 1261
  }
}
```
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/models/tts-1-hd

This endpoint is related to handling API responses, though specific functionality and parameters are not detailed in the provided source text.

```APIDOC
## POST /v1/responses

### Description
This endpoint is related to handling API responses, though specific functionality and parameters are not detailed in the provided source text.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
(No path parameters provided in source text)

#### Query Parameters
(No query parameters provided in source text)

#### Request Body
(Specific request body details not provided in source text)

### Request Example
{}

### Response
#### Success Response (200)
(Specific success response details not provided in source text)

#### Response Example
{}
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/api-reference/runs/listRuns

This endpoint allows you to create a model response by providing text or image inputs. It supports generating text or JSON outputs and can be extended with built-in tools like web search or custom function calling.

```APIDOC
## POST /v1/responses

### Description
Creates a model response. Provide text or image inputs to generate text or JSON outputs. Have the model call your own custom code or use built-in tools like web search or file search to use your own data as input for the model's response.

### Method
POST

### Endpoint
https://api.openai.com/v1/responses

### Parameters
#### Path Parameters
No path parameters described.

#### Query Parameters
No query parameters described.

#### Request Body
The request body for creating a model response typically involves specifying the model, messages (for chat completions), input data (for images), and other options like tools or response format. Specific fields are not detailed in the provided text.

### Request Example
No specific request example was provided in the text.

### Response
#### Success Response (200)
The response would typically contain the model's generated output, which can be text, JSON, or other structured data depending on the request and model. Specific fields are not detailed in the provided text.

#### Response Example
No specific response example was provided in the text.
```

--------------------------------

### API Response Object Structure

Source: https://platform.openai.com/docs/api-reference/assistants/createAssistant

Details the structure of the primary response object returned by the API, including output, usage, and various model parameters.

```APIDOC
## API Response Object Structure

### Description
This section describes the fields present in the main API response object, detailing output, usage, and various model parameters.

### Method
N/A (This describes a response object, not an operation endpoint)

### Endpoint
N/A (This describes a response object, not an operation endpoint)

### Parameters
N/A (These are response fields, not request parameters for an operation)

### Request Example
N/A

### Response
#### Success Response (200)
This is the structure of the successful response object returned by the API.
- **id** (string) - Unique identifier for the response.
- **object** (string) - The type of object returned, typically "response".
- **created_at** (integer) - The Unix timestamp (in seconds) of when the response was created.
- **status** (string) - The current status of the response (e.g., "completed").
- **error** (object / null) - Details of any error that occurred, or null if successful.
- **incomplete_details** (object / null) - Provides details if the response was incomplete.
- **instructions** (object / null) - Any instructions provided to the model.
- **max_output_tokens** (integer / null) - The maximum number of output tokens allowed for the response.
- **model** (string) - The identifier of the model used to generate the response (e.g., "gpt-4o-2024-08-06").
- **output** (array) - An array of output items generated by the model.
  - **type** (string) - The type of output item (e.g., "message").
  - **id** (string) - Unique identifier for the output item.
  - **status** (string) - Status of this specific output item.
  - **role** (string) - The role of the entity generating the output (e.g., "assistant").
  - **content** (array) - The actual content generated.
    - **type** (string) - The type of content (e.g., "output_text").
    - **text** (string) - The text content generated by the model.
    - **annotations** (array) - Any annotations associated with the text content.
- **parallel_tool_calls** (boolean) - Indicates if parallel tool calls were enabled for this response.
- **previous_response_id** (string / null) - The ID of a previous response if this is part of a sequence.
- **reasoning** (object) - Provides insights into the model's reasoning process.
  - **effort** (string / null) - The effort level of the reasoning.
  - **summary** (string / null) - A summary of the reasoning.
- **store** (boolean) - A boolean indicating whether the response should be stored.
- **temperature** (number) - The sampling temperature used for generation. Higher values mean the model will take more risks.
- **text** (object) - Contains details about the text format.
  - **format** (object) - Specifies the format of the text.
    - **type** (string) - The type of text format (e.g., "text").
- **tool_choice** (string or object) - How the model should select which tool (or tools) to use when generating a response. Options include "auto", "none", or a specific tool definition.
- **tools** (array) - An array of tools the model may call while generating a response. Categories include Built-in tools, MCP Tools, and Function calls (custom tools).
- **top_p** (number) - An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with `top_p` probability mass (e.g., 0.1 means top 10% probability mass).
- **truncation** (string) - The truncation strategy used for the model response.
  - `auto`: If input exceeds context window, truncates from conversation beginning.
  - `disabled` (default): Request fails with 400 error if input exceeds context window.
- **usage** (object) - Represents token usage details for the response.
  - **input_tokens** (integer) - The number of tokens in the input.
  - **input_tokens_details** (object) - Further details on input token usage.
    - **cached_tokens** (integer) - Number of cached input tokens.
  - **output_tokens** (integer) - The number of tokens in the output.
  - **output_tokens_details** (object) - Further details on output token usage.
    - **reasoning_tokens** (integer) - Number of tokens used for reasoning.
  - **total_tokens** (integer) - The total number of tokens used (input + output).
- **user** (string / null) - *Deprecated*. A stable identifier for end-users, now replaced by `safety_identifier` and `prompt_cache_key`.
- **metadata** (object) - An arbitrary object for additional metadata.

#### Response Example
```json
{
  "id": "resp_67ccd3a9da748190baa7f1570fe91ac604becb25c45c1d41",
  "object": "response",
  "created_at": 1741476777,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4o-2024-08-06",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd3acc8d48190a77525dc6de64b4104becb25c45c1d41",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "The image depicts a scenic landscape with a wooden boardwalk or pathway leading through lush, green grass under a blue sky with some clouds. The setting suggests a peaceful natural area, possibly a park or nature reserve. There are trees and shrubs in the background.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 328,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 52,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 380
  },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### Responses API: Generate Image

Source: https://platform.openai.com/docs/guides/image-generation_gallery=open&galleryitem=colorize

Generate an image as part of a conversational flow using the Responses API. This endpoint allows you to provide a text prompt, and the API leverages an image generation tool to create the image.

```APIDOC
## POST /responses/create

### Description
This endpoint allows you to generate an image within a conversational or multi-step flow using the Responses API. You provide a text prompt, and the API leverages an image generation tool to create the image.

### Method
POST

### Endpoint
`/responses/create`

### Parameters
#### Request Body
- **model** (string) - Required - The ID of the model to use for generating the response (e.g., "gpt-5").
- **input** (string) - Required - The text prompt for generating the image (e.g., "Generate an image of gray tabby cat hugging an otter with an orange scarf").
- **tools** (array of objects) - Required - A list of tools the model can call. For image generation, include `{"type": "image_generation"}`.

### Request Example
```json
{
  "model": "gpt-5",
  "input": "Generate an image of gray tabby cat hugging an otter with an orange scarf",
  "tools": [{"type": "image_generation"}]
}
```

### Response
#### Success Response (200)
- **output** (array of objects) - Contains the results of the tool calls, including base64 encoded image data if `type` is "image_generation_call".
  - **type** (string) - The type of output, e.g., "image_generation_call".
  - **result** (string) - Base64 encoded string of the generated image (e.g., PNG).

#### Response Example
```json
{
  "output": [
    {
      "type": "image_generation_call",
      "result": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    }
  ]
}
```
```

--------------------------------

### response.created

Source: https://platform.openai.com/docs/api-reference/batch/request-input

Returned when a new Response is created. This is the first event for response creation, with the response in an `in_progress` state.

```APIDOC
## response.created

### Description
Returned when a new Response is created. The first event of response creation, where the response is in an initial state of `in_progress`.

### Method
EVENT

### Endpoint
N/A

### Parameters

#### Request Body
{}

### Request Example
{}

### Response
#### Response Details
- **event_id** (string) - The unique ID of the server event.
- **response** (object) - The response resource.
  - **object** (string) - Type of the response object, e.g., `realtime.response`.
  - **id** (string) - Unique identifier for the response.
  - **status** (string) - Current status of the response, initially `in_progress`.
  - **status_details** (null/object) - Additional details about the status.
  - **output** (array) - List of output items (empty initially).
  - **conversation_id** (string) - The ID of the conversation this response belongs to.
  - **output_modalities** (array) - List of output modalities requested, e.g., `["audio"]`.
  - **max_output_tokens** (string) - Maximum tokens configured for output, e.g., `inf`.
  - **audio** (object) - Audio specific output configuration.
    - **output** (object) - Details about audio output.
      - **format** (object) - Format of the audio.
        - **type** (string) - Audio MIME type, e.g., `audio/pcm`.
        - **rate** (integer) - Sample rate of the audio, e.g., `24000`.
      - **voice** (string) - Name of the voice used for audio, e.g., `marin`.
  - **usage** (null/object) - Usage statistics for the response (null initially).
  - **metadata** (null/object) - Optional metadata provided.
- **type** (string) - The event type, must be `response.created`.

#### Response Example
```json
{
  "type": "response.created",
  "event_id": "event_C9G8pqbTEddBSIxbBN6Os",
  "response": {
    "object": "realtime.response",
    "id": "resp_C9G8p7IH2WxLbkgPNouYL",
    "status": "in_progress",
    "status_details": null,
    "output": [],
    "conversation_id": "conv_C9G8mmBkLhQJwCon3hoJN",
    "output_modalities": [
      "audio"
    ],
    "max_output_tokens": "inf",
    "audio": {
      "output": {
        "format": {
          "type": "audio/pcm",
          "rate": 24000
        },
        "voice": "marin"
      }
    },
    "usage": null,
    "metadata": null
  },
  "timestamp": "2:30:35 PM"
}
```
```

--------------------------------

### Define StreamingEvent Types for OpenAI API Responses

Source: https://platform.openai.com/docs/guides/streaming-responses_api-mode=responses

Illustrates the `StreamingEvent` TypeScript type, which enumerates the various structured event types emitted by the OpenAI API during a streaming response. This definition helps in understanding and handling specific events programmatically.

```typescript
type StreamingEvent =
	| ResponseCreatedEvent
	| ResponseInProgressEvent
	| ResponseFailedEvent
	| ResponseCompletedEvent
	| ResponseOutputItemAdded
	| ResponseOutputItemDone
	| ResponseContentPartAdded
	| ResponseContentPartDone
	| ResponseOutputTextDelta
	| ResponseOutputTextAnnotationAdded
	| ResponseTextDone
	| ResponseRefusalDelta
	| ResponseRefusalDone
	| ResponseFunctionCallArgumentsDelta
	| ResponseFunctionCallArgumentsDone
	| ResponseFileSearchCallInProgress
	| ResponseFileSearchCallSearching
	| ResponseFileSearchCallCompleted
	| ResponseCodeInterpreterInProgress
	| ResponseCodeInterpreterCallCodeDelta
	| ResponseCodeInterpreterCallCodeDone
	| ResponseCodeInterpreterCallInterpreting
	| ResponseCodeInterpreterCallCompleted
	| Error
```

--------------------------------

### Image Generation API Response Object

Source: https://platform.openai.com/docs/api-reference/runs

Describes the structure of a successful response from the image generation API, including details about the generated images and usage information.

```APIDOC
## Image Generation API Response Object

### Description
The response from the image generation endpoint.

### Type
Response Object

### Fields
- **background** (string) - The background parameter used for the image generation. Either `transparent` or `opaque`.
- **created** (integer) - The Unix timestamp (in seconds) of when the image was created.
- **data** (array) - The list of generated images.
  - **b64_json** (string) - Base64-encoded image data.
- **output_format** (string) - The output format of the image generation. Either `png`, `webp`, or `jpeg`.
- **quality** (string) - The quality of the image generated. Either `low`, `medium`, or `high`.
- **size** (string) - The size of the image generated. Either `1024x1024`, `1024x1536`, or `1536x1024`.
- **usage** (object) - For `gpt-image-1` only, the token usage information for the image generation.
  - **total_tokens** (integer) - Total tokens consumed.
  - **input_tokens** (integer) - Input tokens consumed.
  - **output_tokens** (integer) - Output tokens consumed.
  - **input_tokens_details** (object) - Detailed breakdown of input tokens.
    - **text_tokens** (integer) - Text tokens consumed.
    - **image_tokens** (integer) - Image tokens consumed.

### Example
```json
{
  "created": 1713833628,
  "data": [
    {
      "b64_json": "..."
    }
  ],
  "background": "transparent",
  "output_format": "png",
  "size": "1024x1024",
  "quality": "high",
  "usage": {
    "total_tokens": 100,
    "input_tokens": 50,
    "output_tokens": 50,
    "input_tokens_details": {
      "text_tokens": 10,
      "image_tokens": 40
    }
  }
}
```
```

--------------------------------

### GET /v1/responses/{response_id}

Source: https://platform.openai.com/docs/api-reference/responses/input-items

Retrieves the Response object matching the specified ID.

```APIDOC
## GET /v1/responses/{response_id}

### Description
Retrieves the Response object matching the specified ID.

### Method
GET

### Endpoint
/v1/responses/{response_id}

### Parameters
#### Path Parameters
- **response_id** (string) - Required - The ID of the response to retrieve.

### Request Example
```bash
curl https://api.openai.com/v1/responses/resp_123 \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Response
#### Success Response (200)
- **id** (string) - The unique identifier of the response.
- **object** (string) - The object type, typically "response".
- **created_at** (integer) - The Unix timestamp (in seconds) for when the response was created.
- **status** (string) - The current status of the response (e.g., "completed").
- **error** (object/null) - Details of any error that occurred, or null if no error.
- **incomplete_details** (object/null) - Details if the response is incomplete.
- **instructions** (object/null) - Instructions used for the response.
- **max_output_tokens** (integer/null) - The maximum number of output tokens.
- **model** (string) - The model used to generate the response.
- **output** (array) - An array of output messages or content generated by the model.
- **parallel_tool_calls** (boolean) - Indicates if parallel tool calls were enabled.
- **previous_response_id** (string/null) - The ID of the previous response if part of a chain.
- **reasoning** (object) - Details about the model's reasoning process.
- **store** (boolean) - Indicates if the response is stored.
- **temperature** (number) - The sampling temperature used.
- **text** (object) - Text-specific properties for the output format.
- **tool_choice** (string) - Tool choice setting (e.g., "auto").
- **tools** (array) - List of tools used or available.
- **top_p** (number) - The top_p sampling value used.
- **truncation** (string) - Truncation strategy (e.g., "disabled").
- **usage** (object) - Token usage statistics for the response.
- **user** (string/null) - The user associated with the request.
- **metadata** (object) - Arbitrary key-value metadata.

#### Response Example
```json
{
  "id": "resp_67cb71b351908190a308f3859487620d06981a8637e6bc44",
  "object": "response",
  "created_at": 1741386163,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4o-2024-08-06",
  "output": [
    {
      "type": "message",
      "id": "msg_67cb71b3c2b0819084d481baaaf148f206981a8637e6bc44",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "Silent circuits hum,  \\nThoughts emerge in data streams—  \\nDigital dawn breaks.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 32,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 18,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 50
  },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### Use Native Web Search Tool with OpenAI Responses API

Source: https://platform.openai.com/docs/guides/migrate-to-responses

This snippet illustrates how to utilize OpenAI's native web search tool through the Responses API. It shows a simplified approach where the tool is specified directly by its type, allowing the API to handle the underlying execution and integration automatically.

```javascript
const answer = await client.responses.create({
    model: 'gpt-5',
    input: 'Who is the current president of France?',
    tools: [{ type: 'web_search' }]
});

console.log(answer.output_text);
```

```python
answer = client.responses.create(
    model="gpt-5",
    input="Who is the current president of France?",
    tools=[{"type": "web_search_preview"}]
)

print(answer.output_text)
```

```curl
curl https://api.openai.com/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-5",
    "input": "Who is the current president of France?",
    "tools": [{"type": "web_search"}]
  }'
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/models/o1-preview

Endpoint for handling responses related to the o1 Preview model.

```APIDOC
## POST /v1/responses

### Description
Endpoint for handling responses related to the o1 Preview model.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
(None specified)

#### Query Parameters
(None specified)

#### Request Body
(Details not provided in the source text)

### Request Example
{
  "Note": "Request example not provided in the source text"
}

### Response
#### Success Response (200)
(Details not provided in the source text)

#### Response Example
{
  "Note": "Response example not provided in the source text"
}
```

--------------------------------

### GET /v1/responses/{response_id}

Source: https://platform.openai.com/docs/api-reference/evals/create

Retrieves the Response object matching the specified ID.

```APIDOC
## GET /v1/responses/{response_id}

### Description
Retrieves the Response object matching the specified ID.

### Method
GET

### Endpoint
/v1/responses/{response_id}

### Parameters
#### Path Parameters
- **response_id** (string) - Required - The ID of the Response object to retrieve.

### Request Example
```bash
curl https://api.openai.com/v1/responses/resp_123 \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Response
#### Success Response (200)
- **id** (string) - The unique identifier for the response.
- **object** (string) - The object type, always "response".
- **created_at** (integer) - The Unix timestamp (in seconds) for when the response was created.
- **status** (string) - The current status of the response (e.g., "completed").
- **error** (object|null) - Details of any error that occurred.
- **incomplete_details** (object|null) - Details if the response is incomplete.
- **instructions** (object|null) - Instructions provided to the model.
- **max_output_tokens** (integer|null) - The maximum number of output tokens allowed.
- **model** (string) - The model used to generate the response.
- **output** (array) - An array of output messages or content.
- **parallel_tool_calls** (boolean) - Whether parallel tool calls are enabled.
- **previous_response_id** (string|null) - The ID of the previous response in a sequence.
- **reasoning** (object) - Details about the model's reasoning process.
  - **effort** (object|null) - Effort details.
  - **summary** (string|null) - Summary of the reasoning.
- **store** (boolean) - Whether the response is stored.
- **temperature** (number) - The sampling temperature used.
- **text** (object) - Text-specific configuration.
  - **format** (object)
    - **type** (string) - The format type (e.g., "text").
- **tool_choice** (string|object) - Tool choice configuration.
- **tools** (array) - A list of tools used or available.
- **top_p** (number) - The nucleus sampling probability.
- **truncation** (string) - Truncation strategy (e.g., "disabled").
- **usage** (object) - Token usage statistics.
  - **input_tokens** (integer) - Number of input tokens.
  - **input_tokens_details** (object)
    - **cached_tokens** (integer) - Number of cached input tokens.
  - **output_tokens** (integer) - Number of output tokens.
  - **output_tokens_details** (object)
    - **reasoning_tokens** (integer) - Number of tokens used for reasoning.
  - **total_tokens** (integer) - Total number of tokens.
- **user** (string|null) - The user associated with the request.
- **metadata** (object) - Arbitrary metadata associated with the response.

#### Response Example
```json
{
  "id": "resp_67cb71b351908190a308f3859487620d06981a8637e6bc44",
  "object": "response",
  "created_at": 1741386163,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4o-2024-08-06",
  "output": [
    {
      "type": "message",
      "id": "msg_67cb71b3c2b0819084d481baaaf148f206981a8637e6bc44",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "Silent circuits hum,  \nThoughts emerge in data streams—  \nDigital dawn breaks.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 32,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 18,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 50
  },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### Cancel OpenAI Realtime API Response

Source: https://platform.openai.com/docs/api-reference/conversations/create-items

This event allows clients to cancel an in-progress response from the OpenAI Realtime API. The server will confirm cancellation with a `response.done` event and `status=cancelled`. Calling this when no response is active will result in an error, but the session remains stable.

```json
{
    "type": "response.cancel"
    "response_id": "resp_12345"
}
```

--------------------------------

### Example OpenAI API Text Response JSON

Source: https://platform.openai.com/docs/api-reference/audio/createTranslation

This JSON object illustrates the structure of a successful response from the OpenAI API after generating text. It includes details such as the response ID, creation timestamp, model used, and the generated output text.

```json
{
  "id": "resp_67ccd2bed1ec8190b14f964abc0542670bb6a6b452d3795b",
  "object": "response",
  "created_at": 1741476542,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4.1-2025-04-14",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd2bf17f0819081ff3bb2cf6508e60bb6a6b452d3795b",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "In a peaceful grove beneath a silver moon, a unicorn named Lumina discovered a hidden pool that reflected the stars. As she dipped her horn into the water, the pool began to shimmer, revealing a pathway to a magical realm of endless night skies. Filled with wonder, Lumina whispered a wish for all who dream to find their own hidden magic, and as she glanced back, her hoofprints sparkled like stardust.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 36,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 87,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 123
  },
  "user": null,
  "metadata": {}
}
```

--------------------------------

### GET /v1/responses

Source: https://platform.openai.com/docs/models/dall-e-3

Retrieve information about previous API responses or manage response objects. Specific details are not provided in the source text.

```APIDOC
## GET /v1/responses

### Description
This endpoint is likely used for retrieving details or managing previous API responses. The exact functionality is not specified in the provided text.

### Method
GET

### Endpoint
/v1/responses

### Parameters
[No specific parameters detailed in the source text.]

### Request Example
[No specific request example detailed in the source text.]

### Response
#### Success Response (200)
[No specific response fields detailed in the source text.]

#### Response Example
[No specific response example detailed in the source text.]
```

--------------------------------

### Authenticate OpenAI Responses API with Stripe MCP Tool

Source: https://platform.openai.com/docs/guides/tools-connectors-mcp

This example demonstrates how to make an authenticated request to the OpenAI Responses API using an MCP tool for Stripe. It shows how to pass an OAuth access token in the `authorization` field of the MCP tool definition. The API call requests the creation of a payment link.

```curl
curl https://api.openai.com/v1/responses \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $OPENAI_API_KEY" \
-d '{
    "model": "gpt-5",
    "input": "Create a payment link for $20",
    "tools": [
      {
        "type": "mcp",
        "server_label": "stripe",
        "server_url": "https://mcp.stripe.com",
        "authorization": "$STRIPE_OAUTH_ACCESS_TOKEN"
      }
    ]
  }'
```

```javascript
import OpenAI from "openai";
const client = new OpenAI();

const resp = await client.responses.create({
  model: "gpt-5",
  input: "Create a payment link for $20",
  tools: [
    {
      type: "mcp",
      server_label: "stripe",
      server_url: "https://mcp.stripe.com",
      authorization: "$STRIPE_OAUTH_ACCESS_TOKEN"
    }
  ]
});

console.log(resp.output_text);
```

```python
from openai import OpenAI

client = OpenAI()

resp = client.responses.create(
    model="gpt-5",
    input="Create a payment link for $20",
    tools=[
        {
            "type": "mcp",
            "server_label": "stripe",
            "server_url": "https://mcp.stripe.com",
            "authorization": "$STRIPE_OAUTH_ACCESS_TOKEN"
        }
    ]
)

print(resp.output_text)
```

```csharp
using OpenAI.Responses;

string authToken = Environment.GetEnvironmentVariable("STRIPE_OAUTH_ACCESS_TOKEN")!;
string key = Environment.GetEnvironmentVariable("OPENAI_API_KEY")!;
OpenAIResponseClient client = new(model: "gpt-5", apiKey: key);

ResponseCreationOptions options = new();
options.Tools.Add(ResponseTool.CreateMcpTool(
    serverLabel: "stripe",
    serverUri: new Uri("https://mcp.stripe.com"),
    authorizationToken: authToken
));

OpenAIResponse response = (OpenAIResponse)client.CreateResponse([
    ResponseItem.CreateUserMessageItem([
        ResponseContentPart.CreateInputTextPart("Create a payment link for $20")
    ])
], options);

Console.WriteLine(response.GetOutputText());
```

--------------------------------

### POST /response.create

Source: https://platform.openai.com/docs/api-reference/evals

Instructs the server to create a Response, triggering model inference. Responses can be configured with specific instructions, tools, and input, and can be created out-of-band of the default conversation.

```APIDOC
## POST /response.create

### Description
This event instructs the server to create a Response, which means triggering model inference. When in Server VAD mode, the server will create Responses automatically.
A Response will include at least one Item, and may have two, in which case the second will be a function call. These Items will be appended to the conversation history by default.
The server will respond with a `response.created` event, events for Items and content created, and finally a `response.done` event to indicate the Response is complete.

### Method
POST

### Endpoint
/response.create

### Request Body
- **event_id** (string) - Optional - Client-generated ID used to identify this event.
- **response** (object) - Optional - Parameters for creating a new Realtime response.
  - **instructions** (string) - Optional - Overrides session instructions for this response only.
  - **tools** (array) - Optional - Overrides session tools for this response only. Can be an empty array to clear session tools.
  - **conversation** (string) - Optional - Set to `none` to create a Response that does not write to the default Conversation.
  - **output_modalities** (array of strings) - Optional - Specifies desired output modalities (e.g., `["text"]`).
  - **metadata** (object) - Optional - Custom metadata for disambiguating multiple simultaneous Responses.
  - **input** (array of objects) - Optional - An array accepting raw Items or references to existing Items for input.
    - **type** (string) - Type of input, e.g., `item_reference` or `message`.
    - **id** (string) - Required if `type` is `item_reference`.
    - **role** (string) - Required if `type` is `message` (e.g., `user`).
    - **content** (array of objects) - Required if `type` is `message`.
      - **type** (string) - Type of content, e.g., `input_text`.
      - **text** (string) - The text content.
- **type** (string) - Required - The event type, must be `response.create`.

### Request Example
```json
// Trigger a response with the default Conversation and no special parameters
{
  "type": "response.create"
}

// Trigger an out-of-band response that does not write to the default Conversation
{
  "type": "response.create",
  "response": {
    "instructions": "Provide a concise answer.",
    "tools": [],
    "conversation": "none",
    "output_modalities": ["text"],
    "metadata": {
      "response_purpose": "summarization"
    },
    "input": [
      {
        "type": "item_reference",
        "id": "item_12345"
      },
      {
        "type": "message",
        "role": "user",
        "content": [
          {
            "type": "input_text",
            "text": "Summarize the above message in one sentence."
          }
        ]
      }
    ]
  }
}
```

### Response
#### Success Response (200)
Upon successful creation, the server will respond with a `response.created` event, followed by events for any Items and content created, and finally a `response.done` event.

#### Response Example
(No specific response body fields are provided, only event notifications.)
```

--------------------------------

### Generate Model Response

Source: https://platform.openai.com/docs/api-reference/responses/delete

This section describes the parameters used to control model behavior during response generation and provides examples of request and response structures for a model interaction API.

```APIDOC
## POST /v1/chat/completions (Example)

### Description
This endpoint allows you to generate responses from an OpenAI-compatible model by providing input messages and specifying various control parameters. It supports tool usage, custom sampling, and truncation strategies.

### Method
POST

### Endpoint
`/v1/chat/completions` (Example based on common OpenAI API patterns)

### Parameters
#### Request Body
- **messages** (array) - Required - A list of message objects comprising the conversation history. Each object typically has `role` and `content` fields, representing user or assistant turns.
  - **messages[].id** (string) - Optional - The unique identifier for the message.
  - **messages[].type** (string) - Required - The type of the item, typically "message".
  - **messages[].role** (string) - Required - The role of the message's author (e.g., "user", "assistant").
  - **messages[].content** (array) - Required - The content of the message, which can include text or other input types.
    - **messages[].content[].type** (string) - Required - The type of content (e.g., "input_text").
    - **messages[].content[].text** (string) - Required - The textual content of the message.
- **tool_choice** (string or object) - Optional - How the model should select which tool (or tools) to use when generating a response. Can be `"auto"`, `"none"`, or an object specifying a particular tool. See the `tools` parameter to specify available tools.
- **tools** (array) - Optional - An array of tools the model may call while generating a response. You can specify which tool to use by setting the `tool_choice` parameter. Supported categories include Built-in tools, MCP Tools, and Function calls (custom tools).
- **top_logprobs** (integer) - Optional - An integer between 0 and 20 specifying the number of most likely tokens to return at each token position, each with an associated log probability.
- **top_p** (number) - Optional - An alternative to sampling with temperature, called nucleus sampling. The model considers tokens comprising the top_p probability mass (e.g., 0.1 means top 10% probability mass). Generally, alter this or `temperature`, but not both.
- **truncation** (string) - Optional - The strategy to use for truncating the input if it exceeds the model's context window.
  - `auto`: If the input exceeds the model's context window size, the model will truncate the response by dropping items from the beginning of the conversation.
  - `disabled` (default): If the input size exceeds the context window size, the request will fail with a 400 error.
- **user** (string) - Deprecated - Optional - A stable identifier for your end-users, used for caching and abuse detection. This field is being replaced by `safety_identifier` and `prompt_cache_key`. Use `prompt_cache_key` instead to maintain caching optimizations.

### Request Example
```json
{
  "messages": [
    {
      "id": "msg_abc123",
      "type": "message",
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": "Tell me a three sentence bedtime story about a unicorn."
        }
      ]
    }
  ],
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1,
  "truncation": "disabled",
  "user": "user-123"
}
```

### Response
#### Success Response (200)
- **id** (string) - The unique identifier for the response object.
- **object** (string) - The type of object returned, typically "response".
- **created_at** (integer) - The Unix timestamp (in seconds) when the response was created.
- **status** (string) - The completion status of the response (e.g., "completed").
- **error** (object) - Details if an error occurred, otherwise `null`.
- **incomplete_details** (object) - Details if the response is incomplete, otherwise `null`.
- **instructions** (object) - Instructions related to the response, if any.
- **max_output_tokens** (integer) - The maximum number of output tokens requested, if applicable.
- **model** (string) - The identifier of the model used to generate the response (e.g., `gpt-4o-2024-08-06`).
- **output** (array) - A list of output message objects generated by the model.
  - **output[].type** (string) - The type of the output item, typically "message".
  - **output[].id** (string) - The unique identifier for the output message.
  - **output[].status** (string) - The status of the output message (e.g., "completed").
  - **output[].role** (string) - The role of the output message's author (e.g., "assistant").
  - **output[].content** (array) - The content of the output message.
    - **output[].content[].type** (string) - The type of content (e.g., "output_text").
    - **output[].content[].text** (string) - The textual content of the message.
    - **output[].content[].annotations** (array) - Any annotations associated with the content.
- **parallel_tool_calls** (boolean) - Indicates if parallel tool calls were enabled or made.
- **previous_response_id** (string) - The ID of the previous response in a conversation, if applicable.
- **reasoning** (object) - Details about the model's reasoning process.
  - **reasoning.effort** (string) - Effort details for reasoning.
  - **reasoning.summary** (string) - Summary of reasoning.
- **store** (boolean) - Indicates if the response should be stored.
- **temperature** (number) - The sampling temperature used for generation.
- **text** (object) - Text formatting details for the response.
  - **text.format.type** (string) - The format type of the text (e.g., "text").
- **tool_choice** (string) - The `tool_choice` setting used for this response.
- **tools** (array) - The `tools` configured for this response.
- **top_p** (number) - The `top_p` sampling parameter used.
- **truncation** (string) - The `truncation` strategy used.
- **usage** (object) - Represents token usage details including input tokens, output tokens, a breakdown of output tokens, and the total tokens used.
  - **usage.input_tokens** (integer) - Number of input tokens consumed.
  - **usage.input_tokens_details** (object) - Details about input tokens, such as `cached_tokens`.
  - **usage.output_tokens** (integer) - Number of output tokens generated.
  - **usage.output_tokens_details** (object) - Details about output tokens, such as `reasoning_tokens`.
  - **usage.total_tokens** (integer) - Total tokens used (input + output).
- **user** (string) - The user identifier if provided in the request.
- **metadata** (object) - Any additional metadata associated with the response.

#### Response Example
```json
{
  "id": "resp_67ccd3a9da748190baa7f1570fe91ac604becb25c45c1d41",
  "object": "response",
  "created_at": 1741476777,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4o-2024-08-06",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd3acc8d48190a77525dc6de64b4104becb25c45c1d41",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "The image depicts a scenic landscape with a wooden boardwalk or pathway leading through lush, green grass under a blue sky with some clouds. The setting suggests a peaceful natural area, possibly a park or nature reserve. There are trees and shrubs in the background.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 328,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 52,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 380
  },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/api-reference/realtime-server-events/rate_limits

This endpoint allows you to generate a new model response based on a given input. It sends your prompt to a specified model and returns the generated content.

```APIDOC
## POST /v1/responses

### Description
Generates a new model response from a given input using a specified model.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
(None)

#### Query Parameters
(None)

#### Request Body
- **model** (string) - Required - The ID of the model to use for generating the response.
- **input** (string) - Required - The text input for which to generate a response.

### Request Example
```json
{
  "model": "gpt-4.1",
  "input": "Tell me a three sentence bedtime story about a unicorn."
}
```

### Response
#### Success Response (200)
- **id** (string) - The unique identifier of the response.
- **object** (string) - The type of object, typically 'response'.
- **created_at** (integer) - The Unix timestamp (in seconds) when the response was created.
- **status** (string) - The status of the response generation (e.g., 'completed').
- **model** (string) - The ID of the model used to generate the response.
- **output** (array of objects) - The generated content, structured as messages.
  - **type** (string) - Type of the output (e.g., 'message').
  - **content** (array of objects) - List of content parts.
    - **type** (string) - Type of the content part (e.g., 'output_text').
    - **text** (string) - The actual generated text content.
- **usage** (object) - Information about token usage for the request.
  - **input_tokens** (integer) - Number of tokens in the input prompt.
  - **output_tokens** (integer) - Number of tokens in the generated output.
  - **total_tokens** (integer) - Total number of tokens used.

#### Response Example
```json
{
  "id": "resp_67ccd2bed1ec8190b14f964abc0542670bb6a6b452d3795b",
  "object": "response",
  "created_at": 1741476542,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4.1-2025-04-14",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd2bf17f0819081ff3bb2cf6508e60bb6a6b452d3795b",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "In a peaceful grove beneath a silver moon, a unicorn named Lumina discovered a hidden pool that reflected the stars. As she dipped her horn into the water, the pool began to shimmer, revealing a pathway to a magical realm of endless night skies. Filled with wonder, Lumina whispered a wish for all who dream to find their own hidden magic, and as she glanced back, her hoofprints sparkled like stardust.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 36,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 87,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 123
  },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### OpenAI API Standard Response Object

Source: https://platform.openai.com/docs/api-reference/usage/moderations_object

Describes the common structure of a response object returned by the OpenAI API, containing details about the output, model, usage, and any errors.

```APIDOC
## Response Object Schema\n\n### Description\nThis schema defines the structure of a standard response object from the OpenAI API, typically for completion or chat-like operations. It includes unique identifiers, timestamps, status, output content, and usage statistics.\n\n### Method\nN/A (Response Schema)\n\n### Endpoint\nN/A (General Response Structure)\n\n### Parameters\nN/A\n\n### Request Example\nN/A\n\n### Response\n#### Success Response (200)\n- **id** (string) - Unique identifier for the response.\n- **object** (string) - Type of object returned, typically "response".\n- **created_at** (integer) - Unix timestamp when the response was created.\n- **status** (string) - Current status of the response, e.g., "completed".\n- **error** (object) - Details if an error occurred, null otherwise.\n- **incomplete_details** (object) - Details if the response is incomplete.\n- **instructions** (object) - Instructions related to the response.\n- **max_output_tokens** (number) - Maximum output tokens allowed for the response.\n- **model** (string) - The model used to generate the response.\n- **output** (array) - List of output messages.\n    - **type** (string) - Type of output, e.g., "message".\n    - **id** (string) - Unique ID for the message.\n    - **status** (string) - Status of the message.\n    - **role** (string) - Role of the message sender, e.g., "assistant".\n    - **content** (array) - Content of the message.\n        - **type** (string) - Type of content, e.g., "output_text".\n        - **text** (string) - The actual text content.\n        - **annotations** (array) - Any annotations associated with the text.\n- **parallel_tool_calls** (boolean) - Indicates if parallel tool calls were made.\n- **previous_response_id** (string) - ID of the previous response in a sequence.\n- **reasoning** (object) - Details about the reasoning process.\n    - **effort** (object) - Effort details.\n    - **summary** (string) - Summary of reasoning.\n- **store** (boolean) - Indicates if the response should be stored.\n- **temperature** (number) - Temperature setting used for generation.\n- **text** (object) - Text-specific formatting.\n    - **format** (object)\n        - **type** (string) - Format type, e.g., "text".\n- **tool_choice** (string) - Tool choice setting used for generation.\n- **tools** (array) - Tools used in the response.\n- **top_p** (number) - Top_p setting used for generation.\n- **truncation** (string) - Truncation strategy used.\n- **usage** (object) - Token usage details.\n    - **input_tokens** (integer) - Number of input tokens.\n    - **input_tokens_details** (object) - Details about input tokens.\n        - **cached_tokens** (integer) - Number of cached input tokens.\n    - **output_tokens** (integer) - Number of output tokens.\n    - **output_tokens_details** (object) - Details about output tokens.\n        - **reasoning_tokens** (integer) - Number of reasoning tokens.\n    - **total_tokens** (integer) - Total number of tokens.\n- **user** (string) - User identifier.\n- **metadata** (object) - Additional metadata.\n\n#### Response Example\n```\n{\n  "id": "resp_67ccd3a9da748190baa7f1570fe91ac604becb25c45c1d41",\n  "object": "response",\n  "created_at": 1741476777,\n  "status": "completed",\n  "error": null,\n  "incomplete_details": null,\n  "instructions": null,\n  "max_output_tokens": null,\n  "model": "gpt-4o-2024-08-06",\n  "output": [\n    {\n      "type": "message",\n      "id": "msg_67ccd3acc8d48190a77525dc6de64b4104becb25c45c1d41",\n      "status": "completed",\n      "role": "assistant",\n      "content": [\n        {\n          "type": "output_text",\n          "text": "The image depicts a scenic landscape with a wooden boardwalk or pathway leading through lush, green grass under a blue sky with some clouds. The setting suggests a peaceful natural area, possibly a park or nature reserve. There are trees and shrubs in the background.",\n          "annotations": []\n        }\n      ]\n    }\n  ],\n  "parallel_tool_calls": true,\n  "previous_response_id": null,\n  "reasoning": {\n    "effort": null,\n    "summary": null\n  },\n  "store": true,\n  "temperature": 1,\n  "text": {\n    "format": {\n      "type": "text"\n    }\n  },\n  "tool_choice": "auto",\n  "tools": [],\n  "top_p": 1,\n  "truncation": "disabled",\n  "usage": {\n    "input_tokens": 328,\n    "input_tokens_details": {\n      "cached_tokens": 0\n    },\n    "output_tokens": 52,\n    "output_tokens_details": {\n      "reasoning_tokens": 0\n    },\n    "total_tokens": 380\n  },\n  "user": null,\n  "metadata": {}\n}\n```
```

--------------------------------

### POST /v1/responses - Custom Tool Call (Responses API)

Source: https://platform.openai.com/docs/guides/latest-model

Example of making a custom tool call using the Responses API.

```APIDOC
## POST /v1/responses

### Description
Demonstrates how to make a custom tool call using the Responses API.

### Method
POST

### Endpoint
https://api.openai.com/v1/responses

### Request Body
- **model** (string) - Required - The name of the model to use (e.g., "gpt-5").
- **input** (string) - Required - The input prompt.
- **tools** (array) - Required - An array of tool objects.
  - **type** (string) - Required - The type of tool ("custom").
  - **name** (string) - Required - The name of the custom tool.
  - **description** (string) - Required - A description of the custom tool.

### Request Example
```json
{
  "model": "gpt-5",
  "input": "Use the code_exec tool to calculate the area of a circle with radius equal to the number of r letters in blueberry",
  "tools": [
    {
      "type": "custom",
      "name": "code_exec",
      "description": "Executes arbitrary python code"
    }
  ]
}
```
```

--------------------------------

### OpenAI Model Configuration and Response Structure (JSON)

Source: https://platform.openai.com/docs/api-reference/threads

This JSON snippet outlines a configuration for an OpenAI API request or a part of an API response. It specifies the `gpt-4o-mini` model, defines sampling parameters like `seed`, `temperature`, `top_p`, and `max_completions_tokens`, and includes placeholders for `error` and `metadata` typically found in API responses. This represents a typical structure for interacting with or receiving data from the OpenAI API.

```json
{
    "model": "gpt-4o-mini",
    "sampling_params": {
      "seed": 42,
      "temperature": 1.0,
      "top_p": 1.0,
      "max_completions_tokens": 2048
    },
  "error": null,
  "metadata": {}
}
```

--------------------------------

### response.create

Source: https://platform.openai.com/docs/api-reference/batch/object

Instructs the server to initiate a Response, triggering model inference. This event can override session configurations, create out-of-band responses, and accept arbitrary input. The server will respond with `response.created`, item/content events, and `response.done`.

```APIDOC
## EVENT response.create

### Description
This event instructs the server to create a Response, which means triggering model inference. When in Server VAD mode, the server will create Responses automatically. A Response will include at least one Item, and may have two, in which case the second will be a function call. These Items will be appended to the conversation history by default. The server will respond with a `response.created` event, events for Items and content created, and finally a `response.done` event to indicate the Response is complete. The `response.create` event includes inference configuration like `instructions` and `tools`. If these are set, they will override the Session's configuration for this Response only. Responses can be created out-of-band of the default Conversation, meaning that they can have arbitrary input, and it's possible to disable writing the output to the Conversation. Only one Response can write to the default Conversation at a time, but otherwise multiple Responses can be created in parallel. The `metadata` field is a good way to disambiguate multiple simultaneous Responses. Clients can set `conversation` to `none` to create a Response that does not write to the default Conversation. Arbitrary input can be provided with the `input` field, which is an array accepting raw Items and references to existing Items.

### Method
Event

### Endpoint
response.create

### Parameters
#### Request Body
- **event_id** (string) - Optional - Client-generated ID used to identify this event.
- **response** (object) - Optional - Parameters for creating a new Realtime response.
    - **instructions** (string) - Optional - Overrides session instructions for this response.
    - **tools** (array) - Optional - Overrides session tools for this response (e.g., `[]` to clear).
    - **conversation** (string) - Optional - Set to `none` to create an out-of-band response that does not write to the default conversation.
    - **output_modalities** (array of strings) - Optional - Specifies desired output modalities (e.g., `["text"]`).
    - **metadata** (object) - Optional - Client-defined metadata for this response (e.g., `{"response_purpose": "summarization"}`).
    - **input** (array) - Optional - Arbitrary input for out-of-band responses. An array accepting raw Items or references to existing Items.
        - **input[].type** (string) - Required - Type of input item. Can be `item_reference` or `message`.
        - **input[].id** (string) - Required (if `type` is `item_reference`) - The ID of the item being referenced.
        - **input[].role** (string) - Required (if `type` is `message`) - The role of the message sender (e.g., `user`).
        - **input[].content** (array) - Required (if `type` is `message`) - The content of the message.
            - **content[].type** (string) - Required - Type of content (e.g., `input_text`).
            - **content[].text** (string) - Required - The text content.
- **type** (string) - Required - The event type, must be `response.create`.

### Request Example
```json
{
  "type": "response.create",
  "response": {
    "instructions": "Provide a concise answer.",
    "tools": [],
    "conversation": "none",
    "output_modalities": ["text"],
    "metadata": {
      "response_purpose": "summarization"
    },
    "input": [
      {
        "type": "item_reference",
        "id": "item_12345"
      },
      {
        "type": "message",
        "role": "user",
        "content": [
          {
            "type": "input_text",
            "text": "Summarize the above message in one sentence."
          }
        ]
      }
    ]
  }
}
```

### Response
#### Success Response (Events)
Upon successful creation, the server will respond with a `response.created` event, followed by events for any Items and content created, and finally a `response.done` event to indicate the Response is complete. No specific response body fields are provided for these events in the documentation.
```

--------------------------------

### Response Object: usage

Source: https://platform.openai.com/docs/api-reference/run-steps/getRunStep

Describes the 'usage' object in the Response API, which provides details on token usage.

```APIDOC
## Response Object: usage

### Description
Represents token usage details including input tokens, output tokens, a breakdown of output tokens, and the total tokens used.

### Fields
- **input_tokens** (integer) - The number of input tokens used.
- **output_tokens** (integer) - The number of output tokens used.
- **total_tokens** (integer) - The total number of tokens used.

### Example
```json
{
  "usage": {
    "input_tokens": 328,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 52,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 380
  }
}
```
```

--------------------------------

### Image Generation Response Object

Source: https://platform.openai.com/docs/api-reference/realtime-server-events/rate_limits

Describes the structure of a successful response from an image generation API endpoint.

```APIDOC
## N/A Image Generation Response Object

### Description
Describes the structure of a successful response from an image generation API endpoint.

### Method
N/A

### Endpoint
N/A

### Parameters
N/A

### Request Example
N/A

### Response
#### Success Response (200)
- **created** (integer) - The Unix timestamp (in seconds) of when the image was created.
- **data** (array) - The list of generated images.
  - **b64_json** (string) - Base64-encoded image data.
- **background** (string) - The background parameter used for the image generation. Either `transparent` or `opaque`.
- **output_format** (string) - The output format of the image generation. Either `png`, `webp`, or `jpeg`.
- **quality** (string) - The quality of the image generated. Either `low`, `medium`, or `high`.
- **size** (string) - The size of the image generated. Either `1024x1024`, `1024x1536`, or `1536x1024`.
- **usage** (object) - For `gpt-image-1` only, the token usage information for the image generation.
  - **total_tokens** (integer) - Total tokens used.
  - **input_tokens** (integer) - Input tokens used.
  - **output_tokens** (integer) - Output tokens used.
  - **input_tokens_details** (object) - Details of input tokens.
    - **text_tokens** (integer) - Text tokens used.
    - **image_tokens** (integer) - Image tokens used.

#### Response Example
```
{
  "created": 1713833628,
  "data": [
    {
      "b64_json": "..."
    }
  ],
  "background": "transparent",
  "output_format": "png",
  "size": "1024x1024",
  "quality": "high",
  "usage": {
    "total_tokens": 100,
    "input_tokens": 50,
    "output_tokens": 50,
    "input_tokens_details": {
      "text_tokens": 10,
      "image_tokens": 40
    }
  }
}
```
```

--------------------------------

### Image Generation API Response

Source: https://platform.openai.com/docs/api-reference/assistants/modifyAssistant

Describes the successful response payload received after an image generation request.

```APIDOC
## Image Generation API Response

### Description
This section describes the structure of a successful response from the image generation endpoint. It includes metadata about the generated image(s) and usage information.

### Method
N/A (Response Schema)

### Endpoint
N/A (Response Schema)

### Parameters
N/A

### Request Body
N/A

### Response
#### Success Response (200)
- **created** (integer) - The Unix timestamp (in seconds) of when the image was created.
- **data** (array) - The list of generated images.
  - **b64_json** (string) - Base64-encoded image data.
- **background** (string) - The background parameter used for the image generation. Either `transparent` or `opaque`.
- **output_format** (string) - The output format of the image generation. Either `png`, `webp`, or `jpeg`.
- **quality** (string) - The quality of the image generated. Either `low`, `medium`, or `high`.
- **size** (string) - The size of the image generated. Either `1024x1024`, `1024x1536`, or `1536x1024`.
- **usage** (object) - For `gpt-image-1` only, the token usage information for the image generation.
  - **total_tokens** (integer) - Total tokens used.
  - **input_tokens** (integer) - Input tokens used.
  - **output_tokens** (integer) - Output tokens used.
  - **input_tokens_details** (object) - Details about input tokens.
    - **text_tokens** (integer) - Text tokens.
    - **image_tokens** (integer) - Image tokens.

#### Response Example
```json
{
  "created": 1713833628,
  "data": [
    {
      "b64_json": "..."
    }
  ],
  "background": "transparent",
  "output_format": "png",
  "size": "1024x1024",
  "quality": "high",
  "usage": {
    "total_tokens": 100,
    "input_tokens": 50,
    "output_tokens": 50,
    "input_tokens_details": {
      "text_tokens": 10,
      "image_tokens": 40
    }
  }
}
```
```

--------------------------------

### response.create

Source: https://platform.openai.com/docs/api-reference/runs/listRuns

Instructs the server to initiate model inference and create a Response, which can include one or two Items (potentially a function call). These Items are appended to the conversation history by default. Configuration like `instructions` and `tools` can be set per response, overriding session defaults. Responses can also be created out-of-band, without writing to the default Conversation.

```APIDOC
## Client Event: response.create

### Description
This event instructs the server to create a Response, which means triggering model inference. When in Server VAD mode, the server will create Responses automatically. A Response will include at least one Item, and may have two, in which case the second will be a function call. These Items will be appended to the conversation history by default. The server will respond with a `response.created` event, events for Items and content created, and finally a `response.done` event to indicate the Response is complete. The `response.create` event includes inference configuration like `instructions` and `tools`. If these are set, they will override the Session's configuration for this Response only. Responses can be created out-of-band of the default Conversation, meaning that they can have arbitrary input, and it's possible to disable writing the output to the Conversation. Only one Response can write to the default Conversation at a time, but otherwise multiple Responses can be created in parallel. The `metadata` field is a good way to disambiguate multiple simultaneous Responses. Clients can set `conversation` to `none` to create a Response that does not write to the default Conversation. Arbitrary input can be provided with the `input` field, which is an array accepting raw Items and references to existing Items.

### Method
Client Event

### Endpoint
N/A

### Parameters
#### Path Parameters
N/A

#### Query Parameters
N/A

#### Request Body
- **event_id** (string) - Optional - Optional client-generated ID used to identify this event.
- **response** (object) - Optional - Create a new Realtime response with these parameters. If omitted, default session parameters are used.
  - **instructions** (string) - Optional - Specific instructions for this response, overriding session defaults.
  - **tools** (array) - Optional - An array of tools to use for this response, clearing any session tools if empty.
  - **conversation** (string) - Optional - Set to `"none"` to create a Response that does not write to the default Conversation.
  - **output_modalities** (array of strings) - Optional - Specifies the desired output modalities (e.g., `["text"]`).
  - **metadata** (object) - Optional - Arbitrary metadata to associate with this response, useful for disambiguating multiple simultaneous responses.
  - **input** (array) - Optional - An array of input items, which can be raw Items or references to existing Items, for out-of-band responses.
    - **type** (string) - Required - Type of the input item (e.g., `"item_reference"`, `"message"`).
    - **id** (string) - Required (if `type` is `"item_reference"`) - The ID of the item being referenced.
    - **role** (string) - Required (if `type` is `"message"`) - The role of the message (e.g., `"user"`, `"assistant"`).
    - **content** (array) - Required (if `type` is `"message"`) - Array of content parts for the message.
      - **type** (string) - Required - Type of content (e.g., `"input_text"`).
      - **text** (string) - Required (if `type` is `"input_text"`) - The text content.
- **type** (string) - Required - The event type, must be `response.create`.

### Request Example
```json
// Trigger a response with the default Conversation and no special parameters
{
  "type": "response.create"
}

// Trigger an out-of-band response that does not write to the default Conversation
{
  "type": "response.create",
  "response": {
    "instructions": "Provide a concise answer.",
    "tools": [], // clear any session tools
    "conversation": "none",
    "output_modalities": ["text"],
    "metadata": {
      "response_purpose": "summarization"
    },
    "input": [
      {
        "type": "item_reference",
        "id": "item_12345"
      },
      {
        "type": "message",
        "role": "user",
        "content": [
          {
            "type": "input_text",
            "text": "Summarize the above message in one sentence."
          }
        ]
      }
    ]
  }
}
```

### Response
#### Success Response (200)
The server responds with a `response.created` event, followed by events for Items and content created, and finally a `response.done` event.

#### Response Example
N/A
```

--------------------------------

### response.create

Source: https://platform.openai.com/docs/api-reference/assistants/createAssistant

Instructs the server to trigger model inference and create a Response, potentially including Items that are appended to the conversation history. Supports overriding session configuration and out-of-band responses.

```APIDOC
## response.create

### Description
This event instructs the server to create a Response, which means triggering model inference. When in Server VAD mode, the server will create Responses automatically. A Response will include at least one Item, and may have two, in which case the second will be a function call. These Items will be appended to the conversation history by default. The `response.create` event includes inference configuration like `instructions` and `tools`. If these are set, they will override the Session's configuration for this Response only. Clients can set `conversation` to `none` to create a Response that does not write to the default Conversation.

### Event Type
response.create

### Parameters
#### Event Body
- **event_id** (string) - Optional - Client-generated ID used to identify this event.
- **response** (object) - Required - Create a new Realtime response with these parameters.
  - **instructions** (string) - Optional - Instructions for this specific response, overriding session configuration.
  - **tools** (array) - Optional - A list of tools to use for this specific response, overriding session configuration. An empty array clears session tools.
  - **conversation** (string) - Optional - Set to `none` to create an out-of-band response that does not write to the default Conversation.
  - **output_modalities** (array of strings) - Optional - Desired modalities for the output (e.g., "text").
  - **metadata** (object) - Optional - Client-defined metadata for disambiguating multiple simultaneous Responses.
  - **input** (array) - Optional - An array accepting raw Items and references to existing Items, providing arbitrary input for out-of-band responses.
    - **type** (string) - Required - Type of input item (e.g., `item_reference`, `message`).
    - **id** (string) - Required (if `type` is `item_reference`) - ID of the referenced item.
    - **role** (string) - Required (if `type` is `message`) - Role of the message (e.g., `user`).
    - **content** (array) - Required (if `type` is `message`) - Content of the message.
      - **type** (string) - Required - Type of content (e.g., `input_text`).
      - **text** (string) - Required (if `type` is `input_text`) - The text content.
- **type** (string) - Required - The event type, must be `response.create`.

### Request Example
```json
// Trigger a response with the default Conversation and no special parameters
{
  "type": "response.create"
}

// Trigger an out-of-band response that does not write to the default Conversation
{
  "type": "response.create",
  "response": {
    "instructions": "Provide a concise answer.",
    "tools": [],
    "conversation": "none",
    "output_modalities": ["text"],
    "metadata": {
      "response_purpose": "summarization"
    },
    "input": [
      {
        "type": "item_reference",
        "id": "item_12345"
      },
      {
        "type": "message",
        "role": "user",
        "content": [
          {
            "type": "input_text",
            "text": "Summarize the above message in one sentence."
          }
        ]
      }
    ]
  }
}
```

### Response
#### Success Event (response.created, events for Items, response.done)
- `response.created`: Event indicating the response creation has started.
- Events for Items and content created: Subsequent events detailing the generated content.
- `response.done`: Event indicating the completion of the response. No specific fields are described for these response events.
```

--------------------------------

### POST /v1/chat/completions

Source: https://platform.openai.com/docs/guides/responses-vs-chat-completions

Create a model response for a given chat conversation. This endpoint allows you to generate text from a model by providing an array of messages with different roles and content.

```APIDOC
## POST /v1/chat/completions

### Description
Generates text from a model based on a conversation history provided as an array of messages. This allows for multi-turn conversational AI interactions.

### Method
POST

### Endpoint
/v1/chat/completions

### Parameters
#### Path Parameters
(None)

#### Query Parameters
(None)

#### Request Body
- **model** (string) - Required - The ID of the model to use for generating the completion. E.g., "gpt-5"
- **messages** (array of objects) - Required - A list of messages comprising the conversation so far.
  - **role** (string) - Required - The role of the author of this message. Can be "system", "user", or "assistant".
  - **content** (string) - Required - The content of the message.

### Request Example
```json
{
  "model": "gpt-5",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": "Hello!"
    }
  ]
}
```

### Response
#### Success Response (200)
- **id** (string) - A unique identifier for the completion.
- **object** (string) - The object type, which is always "chat.completion".
- **created** (integer) - The Unix timestamp (in seconds) of when the chat completion was created.
- **model** (string) - The model used for the chat completion.
- **choices** (array) - A list of chat completion choices.
  - **index** (integer) - The index of the choice in the list.
  - **message** (object) - A chat completion message generated by the model.
    - **role** (string) - The role of the author of this message, which is "assistant".
    - **content** (string) - The content of the message.
  - **finish_reason** (string) - The reason the model stopped generating tokens.
- **usage** (object) - Usage statistics for the completion request.

#### Response Example
```json
{
  "id": "chatcmpl-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "gpt-5",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello there! How can I assist you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 10,
    "total_tokens": 35
  }
}
```
```

--------------------------------

### Image Generation API Response Object

Source: https://platform.openai.com/docs/api-reference/conversations/create-items

Describes the structure of a successful non-streaming image generation API response, including image data, format, quality, and usage information.

```APIDOC
## Image Generation API Response Object

### Description
The response object returned from a successful image generation request. It contains details about the generated image(s) and associated metadata.

### Response
#### Success Response (200)
- **created** (integer) - The Unix timestamp (in seconds) of when the image was created.
- **data** (array) - The list of generated images.
    - **b64_json** (string) - Base64-encoded image data, suitable for rendering as an image.
- **background** (string) - The background parameter used for the image generation. Either `transparent` or `opaque`.
- **output_format** (string) - The output format of the image generation. Either `png`, `webp`, or `jpeg`.
- **quality** (string) - The quality of the image generated. Either `low`, `medium`, or `high`.
- **size** (string) - The size of the image generated. Either `1024x1024`, `1024x1536`, or `1536x1024`.
- **usage** (object) - For `gpt-image-1` only, the token usage information for the image generation.
    - **total_tokens** (integer) - Total tokens used.
    - **input_tokens** (integer) - Input tokens used.
    - **output_tokens** (integer) - Output tokens used.
    - **input_tokens_details** (object) - Detailed input token information.
        - **text_tokens** (integer) - Text tokens in input.
        - **image_tokens** (integer) - Image tokens in input.

#### Response Example
```json
{
  "created": 1713833628,
  "data": [
    {
      "b64_json": "..."
    }
  ],
  "background": "transparent",
  "output_format": "png",
  "size": "1024x1024",
  "quality": "high",
  "usage": {
    "total_tokens": 100,
    "input_tokens": 50,
    "output_tokens": 50,
    "input_tokens_details": {
      "text_tokens": 10,
      "image_tokens": 40
    }
  }
}
```
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/models/omni-moderation-latest

This endpoint is typically used for submitting or managing responses within the OpenAI system, though specific details are not provided.

```APIDOC
## POST /v1/responses

### Description
This endpoint is typically used for submitting or managing responses within the OpenAI system, though specific details are not provided. It may handle feedback, user interactions, or model outputs.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
- No path parameters specified in the documentation.

#### Query Parameters
- No query parameters specified in the documentation.

#### Request Body
- Refer to specific API documentation for required fields. Generally, this would involve data pertinent to a response, such as user feedback or system-generated replies.

### Request Example
{
  "response_id": "res_abc123",
  "feedback": "This model provided an excellent answer.",
  "rating": 5
}

### Response
#### Success Response (200)
- **status** (string) - Indicates if the response was successfully processed.
- **message** (string) - A descriptive message regarding the operation.

#### Response Example
{
  "status": "success",
  "message": "Response successfully recorded."
}
```

--------------------------------

### POST /v1/responses - Create a model response

Source: https://platform.openai.com/docs/api-reference/conversations/list-items

This endpoint creates a model response. You can provide text or image inputs to generate text or JSON outputs. It also supports extending model capabilities with custom code or built-in tools like web search or file search.

```APIDOC
## POST /v1/responses

### Description
Creates a model response. Provide text or image inputs to generate text or JSON outputs. Have the model call your own custom code or use built-in tools like web search or file search to use your own data as input for the model's response.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
No path parameters.

#### Query Parameters
No query parameters.

#### Request Body
Details for the request body (e.g., input text, image data, tool configurations) are not explicitly specified in the provided text. It implies structure for "text or image inputs".

### Request Example
{
  "input": "Example input based on API description",
  "model": "gpt-4o"
}

### Response
#### Success Response (200)
Details for the success response fields (e.g., generated text, JSON output) are not explicitly specified in the provided text. It implies "text or JSON outputs".

#### Response Example
{
  "output": "Example output based on API description"
}
```

--------------------------------

### response.create

Source: https://platform.openai.com/docs/api-reference/batch/request-input

This event instructs the server to create a Response, triggering model inference. Responses can be configured with specific instructions, tools, and input, and can optionally be created out-of-band without writing to the default conversation history.

```APIDOC
## EVENT response.create

### Description
This event instructs the server to create a Response, which means triggering model inference. When in Server VAD mode, the server will create Responses automatically. A Response will include at least one Item, and may have two, in which case the second will be a function call. These Items will be appended to the conversation history by default. The `response.create` event includes inference configuration like `instructions` and `tools`. If these are set, they will override the Session's configuration for this Response only. Clients can set `conversation` to `none` to create a Response that does not write to the default Conversation.

### Method
Event

### Endpoint
response.create

### Parameters
#### Request Body
- **event_id** (string) - Optional - Client-generated ID used to identify this event.
- **response** (object) - Optional - Create a new Realtime response with these parameters. If omitted, a response will be triggered with default conversation parameters.
  - **instructions** (string) - Optional - Override the session's instructions for this Response only.
  - **tools** (array) - Optional - Clear or provide specific tools for this Response only.
  - **conversation** (string) - Optional - Can be set to `none` to create a Response that does not write to the default Conversation.
  - **output_modalities** (array of strings) - Optional - Specifies desired output modalities, e.g., `["text"]`.
  - **metadata** (object) - Optional - Custom metadata to associate with this response.
  - **input** (array) - Optional - An array accepting raw Items or references to existing Items to provide arbitrary input for the response.
- **type** (string) - Required - The event type, must be `response.create`.

### Request Example
```json
// Trigger a response with the default Conversation and no special parameters
{
  "type": "response.create"
}

// Trigger an out-of-band response that does not write to the default Conversation
{
  "type": "response.create",
  "response": {
    "instructions": "Provide a concise answer.",
    "tools": [], // clear any session tools
    "conversation": "none",
    "output_modalities": ["text"],
    "metadata": {
      "response_purpose": "summarization"
    },
    "input": [
      {
        "type": "item_reference",
        "id": "item_12345"
      },
      {
        "type": "message",
        "role": "user",
        "content": [
          {
            "type": "input_text",
            "text": "Summarize the above message in one sentence."
          }
        ]
      }
    ]
  }
}
```

### Response
#### Success Response
The server will respond with a `response.created` event, events for Items and content created, and finally a `response.done` event to indicate the Response is complete.

#### Response Example
```json
{
  "type": "response.created",
  "response_id": "resp_123",
  "event_id": "event_abc"
}
```
```

--------------------------------

### Example Output from OpenAI Responses API (JSON)

Source: https://platform.openai.com/docs/guides/migrate-to-responses

This JSON example details the response structure from the OpenAI Responses API. It features an ID, object type, creation timestamp, model used, and an 'output' array containing various 'Items', such as a 'reasoning' item and a 'message' item, which holds the actual generated text content.

```json
{
  "id": "resp_68af4030592c81938ec0a5fbab4a3e9f05438e46b5f69a3b",
  "object": "response",
  "created_at": 1756315696,
  "model": "gpt-5-2025-08-07",
  "output": [
    {
      "id": "rs_68af4030baa48193b0b43b4c2a176a1a05438e46b5f69a3b",
      "type": "reasoning",
      "content": [],
      "summary": []
    },
    {
      "id": "msg_68af40337e58819392e935fb404414d005438e46b5f69a3b",
      "type": "message",
      "status": "completed",
      "content": [
        {
          "type": "output_text",
          "annotations": [],
          "logprobs": [],
          "text": "Under a quilt of moonlight, a drowsy unicorn wandered through quiet meadows, brushing blossoms with her glowing horn so they sighed soft lullabies that carried every dreamer gently to sleep."
        }
      ],
      "role": "assistant"
    }
  ],
  "..."
}
```

--------------------------------

### Response Object Parameters

Source: https://platform.openai.com/docs/api-reference/usage/moderations

Details the request parameters for generating a response from the API, including tool choice and token probabilities.

```APIDOC
## Response Object Parameters

### Description
This section details the various parameters that can be used when requesting a response from the OpenAI API. These parameters control the behavior and output of the model.

### Parameters

#### Tool Choice
- **tool_choice** (string or object) - Optional - Determines how the model selects tools. Can be a string or an object specifying the tool to use.

#### Tools
- **tools** (array) - Optional - An array of tools the model can call, including built-in tools, MCP Tools, and custom functions.

#### Top Logprobs
- **top_logprobs** (integer) - Optional - Specifies the number of most likely tokens to return with associated log probabilities (0-20).

#### Top P
- **top_p** (number) - Optional - Nucleus sampling parameter. Considers tokens with top_p probability mass.

#### Truncation
- **truncation** (string) - Optional - The truncation strategy for the model response. Options are `auto` and `disabled` (default).

#### User (Deprecated)
- **user** (string) - Deprecated - Replaced by `safety_identifier` and `prompt_cache_key`. A stable identifier for end-users.

```

--------------------------------

### Image Generation Response Object

Source: https://platform.openai.com/docs/api-reference/realtime-server-events/mcp_list_tools/failed

Defines the structure of the successful response object returned by the image generation API.

```APIDOC
## Image Generation Response Object

### Description
The response object from the image generation endpoint, detailing the generated image(s) and associated metadata.

### Properties
- **background** (string) - The background parameter used for the image generation. Either `transparent` or `opaque`.
- **created** (integer) - The Unix timestamp (in seconds) of when the image was created.
- **data** (array) - The list of generated images. Each item in the array typically contains `b64_json`.
- **output_format** (string) - The output format of the image generation. Either `png`, `webp`, or `jpeg`.
- **quality** (string) - The quality of the image generated. Either `low`, `medium`, or `high`.
- **size** (string) - The size of the image generated. Either `1024x1024`, `1024x1536`, or `1536x1024`.
- **usage** (object) - For `gpt-image-1` only, the token usage information for the image generation. Contains `total_tokens`, `input_tokens`, `output_tokens`, and `input_tokens_details` (e.g., `text_tokens`, `image_tokens`).

### Example
```json
{
  "created": 1713833628,
  "data": [
    {
      "b64_json": "..."
    }
  ],
  "background": "transparent",
  "output_format": "png",
  "size": "1024x1024",
  "quality": "high",
  "usage": {
    "total_tokens": 100,
    "input_tokens": 50,
    "output_tokens": 50,
    "input_tokens_details": {
      "text_tokens": 10,
      "image_tokens": 40
    }
  }
}
```
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/api-reference/assistants/listAssistants

Creates a model response. Provide text or image inputs to generate text or JSON outputs. Have the model call your own custom code or use built-in tools like web search or file search to use your own data as input for the model's response.

```APIDOC
## POST /v1/responses

### Description
Creates a model response. Provide text or image inputs to generate text or JSON outputs. Have the model call your own custom code or use built-in tools like web search or file search to use your own data as input for the model's response.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
No path parameters.

#### Query Parameters
No query parameters.

#### Request Body
Details for input types (text, image) and model configurations (custom code, built-in tools, function calling) are described conceptually but specific fields are not provided in the source text.

### Request Example
No request example provided in the source text.

### Response
#### Success Response (200)
The response contains the model's generated output, which can be text or JSON. Specific field details for the success response are not provided in the source text.

#### Response Example
No response example provided in the source text.
```

--------------------------------

### Chat Completions API

Source: https://platform.openai.com/docs/guides/responses-vs-chat-completions

The Chat Completions API generates conversational responses from a model based on a sequence of messages. It supports parallel generations via the `n` parameter and returns an array of `choices`, each containing a `message`.

```APIDOC
## POST /chat/completions

### Description
Generates a completion for the given chat messages. This API is designed for multi-turn conversations and returns model-generated messages.

### Method
POST

### Endpoint
`/chat/completions`

### Parameters
#### Request Body
- **model** (string) - Required - The ID of the model to use for the completion.
- **messages** (array of objects) - Required - A list of messages comprising the conversation so far.
  - **role** (string) - Required - The role of the author of this message (e.g., "user", "assistant").
  - **content** (string) - Required - The content of the message.
- **n** (integer) - Optional - How many chat completion choices to generate for each input message. (Not available in Responses API)
- **store** (boolean) - Optional - Whether to store the conversation by default. (Default: true for new accounts)

### Request Example
```json
{
  "model": "gpt-5",
  "messages": [
    {
      "role": "user",
      "content": "Write a one-sentence bedtime story about a unicorn."
    }
  ]
}
```

### Response
#### Success Response (200)
- **id** (string) - A unique identifier for the chat completion.
- **object** (string) - The object type, which is always `chat.completion`.
- **created** (integer) - The Unix timestamp (in seconds) of when the chat completion was created.
- **model** (string) - The model used for the chat completion.
- **choices** (array of objects) - A list of chat completion choices.
  - **index** (integer) - The index of the choice in the list.
  - **message** (object) - The message generated by the model.
    - **role** (string) - The role of the assistant.
    - **content** (string) - The contents of the assistant message.
    - **refusal** (string/null) - (Optional) Reason for refusal, if any.
    - **annotations** (array) - (Optional) Any annotations associated with the content.
  - **finish_reason** (string) - The reason the model stopped generating tokens.

#### Response Example
```json
{
  "id": "chatcmpl-C9EDpkjH60VPPIB86j2zIhiR8kWiC",
  "object": "chat.completion",
  "created": 1756315657,
  "model": "gpt-5-2025-08-07",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Under a blanket of starlight, a sleepy unicorn tiptoed through moonlit meadows, gathering dreams like dew to tuck beneath its silver mane until morning.",
        "refusal": null,
        "annotations": []
      },
      "finish_reason": "stop"
    }
  ]
}
```
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/api-reference/project-api-keys/list

Creates a new model response based on the provided input and specified model.

```APIDOC
## POST /v1/responses

### Description
Creates a new model response by sending text input to a specified OpenAI model. This endpoint allows for generating dynamic content based on user prompts.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The ID of the model to use for generating the response (e.g., "gpt-4.1").
- **input** (string) - Required - The text prompt or input for the model to process.

### Request Example
```json
{
  "model": "gpt-4.1",
  "input": "Tell me a three sentence bedtime story about a unicorn."
}
```

### Response
#### Success Response (200)
- **id** (string) - A unique identifier for the response.
- **object** (string) - The type of object, typically "response".
- **created_at** (integer) - Unix timestamp when the response was created.
- **status** (string) - The status of the response, e.g., "completed".
- **model** (string) - The ID of the model used.
- **output** (array) - An array of output messages, each containing content.
  - **type** (string) - The type of content, e.g., "output_text".
  - **text** (string) - The generated text content from the model.
- **usage** (object) - Information about token usage.
  - **input_tokens** (integer) - Number of tokens in the input.
  - **output_tokens** (integer) - Number of tokens in the output.
  - **total_tokens** (integer) - Total number of tokens used.

#### Response Example
```json
{
  "id": "resp_67ccd2bed1ec8190b14f964abc0542670bb6a6b452d3795b",
  "object": "response",
  "created_at": 1741476542,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4.1-2025-04-14",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd2bf17f0819081ff3bb2cf6508e60bb6a6b452d3795b",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "In a peaceful grove beneath a silver moon, a unicorn named Lumina discovered a hidden pool that reflected the stars. As she dipped her horn into the water, the pool began to shimmer, revealing a pathway to a magical realm of endless night skies. Filled with wonder, Lumina whispered a wish for all who dream to find their own hidden magic, and as she glanced back, her hoofprints sparkled like stardust.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 36,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 87,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 123
  },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/api-reference/usage/moderations

This endpoint creates a new response from the OpenAI model. It takes an input string and returns a Response object containing the model's output.

```APIDOC
## POST /v1/responses

### Description
Creates a new response from the OpenAI model given an input.

### Method
POST

### Endpoint
/v1/responses

### Request Body
- **model** (string) - Required - The name of the model to use.
- **input** (string) - Required - The input text for the model.

### Request Example
```json
{
  "model": "gpt-4.1",
  "input": "Tell me a three sentence bedtime story about a unicorn."
}
```

### Response
#### Success Response (200)
- **id** (string) - The ID of the response.
- **object** (string) - The type of object, which is "response".
- **created_at** (integer) - The timestamp when the response was created.
- **status** (string) - The status of the response (e.g., "completed").
- **output** (array) - The model's output.

#### Response Example
```json
{
  "id": "resp_67ccd2bed1ec8190b14f964abc0542670bb6a6b452d3795b",
  "object": "response",
  "created_at": 1741476542,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4.1-2025-04-14",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd2bf17f0819081ff3bb2cf6508e60bb6a6b452d3795b",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "In a peaceful grove beneath a silver moon, a unicorn named Lumina discovered a hidden pool that reflected the stars. As she dipped her horn into the water, the pool began to shimmer, revealing a pathway to a magical realm of endless night skies. Filled with wonder, Lumina whispered a wish for all who dream to find their own hidden magic, and as she glanced back, her hoofprints sparkled like stardust.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 36,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 87,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 123
  },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### Define Structured Outputs with text.format in OpenAI Responses API

Source: https://platform.openai.com/docs/guides/responses-vs-chat-completions

This code demonstrates the updated method for defining structured outputs using the 'text.format' parameter within the Responses API. It provides a JSON schema to extract 'name' and 'age' from the 'input' field. This approach represents the current recommendation for structured output definitions.

```curl
curl https://api.openai.com/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
  "model": "gpt-5",
  "input": "Jane, 54 years old",
  "text": {
    "format": {
      "type": "json_schema",
      "name": "person",
      "strict": true,
      "schema": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "minLength": 1
          },
          "age": {
            "type": "number",
            "minimum": 0,
            "maximum": 130
          }
        },
        "required": [
          "name",
          "age"
        ],
        "additionalProperties": false
      }
    }
  }
}'
```

```python
response = client.responses.create(
  model="gpt-5",
  input="Jane, 54 years old", 
  text={
    "format": {
      "type": "json_schema",
      "name": "person",
      "strict": True,
      "schema": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "minLength": 1
          },
          "age": {
            "type": "number",
            "minimum": 0,
            "maximum": 130
          }
        },
        "required": [
          "name",
          "age"
        ],
        "additionalProperties": False
      }
    }
  }
)
```

```javascript
const response = await openai.responses.create({
  model: "gpt-5",
  input: "Jane, 54 years old",
  text: {
    format: {
      type: "json_schema",
      name: "person",
      strict: true,
      schema: {
        type: "object",
        properties: {
          name: {
            type: "string",
            minLength: 1
          },
          age: {
            type: "number",
            minimum: 0,
            maximum: 130
          }
        },
        required: [
          name
        ]
      }
    }
  }
});
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/api-reference/files/object

This endpoint allows you to create a model response. It supports both text and image inputs and can generate text or JSON outputs. You can also integrate custom code or leverage built-in tools like web search or file search for richer interactions.

```APIDOC
## POST /v1/responses

### Description
Creates a model response. Provide text or image inputs to generate text or JSON outputs. Have the model call your own custom code or use built-in tools like web search or file search to use your own data as input for the model's response.

### Method
POST

### Endpoint
https://api.openai.com/v1/responses

### Parameters
#### Path Parameters
*None specified.*

#### Query Parameters
*None specified.*

#### Request Body
*Details not explicitly provided.*

### Request Example
```json
{}
```

### Response
#### Success Response (200)
*Details not explicitly provided.*

#### Response Example
```json
{}
```
```

--------------------------------

### Authenticate OpenAI Responses API with MCP Tools

Source: https://platform.openai.com/docs/guides/tools-remote-mcp

These examples demonstrate how to call the OpenAI Responses API to interact with an MCP server (e.g., Stripe) requiring OAuth authentication. The `$STRIPE_OAUTH_ACCESS_TOKEN` is passed in the `authorization` field of the MCP tool configuration. Note that the API does not store these sensitive tokens, requiring them to be provided with each request.

```shell
curl https://api.openai.com/v1/responses \n-H "Content-Type: application/json" \n-H "Authorization: Bearer $OPENAI_API_KEY" \n-d '{\n    "model": "gpt-5",\n    "input": "Create a payment link for $20",\n    "tools": [\n      {\n        "type": "mcp",\n        "server_label": "stripe",\n        "server_url": "https://mcp.stripe.com",\n        "authorization": "$STRIPE_OAUTH_ACCESS_TOKEN"\n      }\n    ]\n  }'
```

```javascript
import OpenAI from "openai";
const client = new OpenAI();

const resp = await client.responses.create({
  model: "gpt-5",
  input: "Create a payment link for $20",
  tools: [
    {
      type: "mcp",
      server_label: "stripe",
      server_url: "https://mcp.stripe.com",
      authorization: "$STRIPE_OAUTH_ACCESS_TOKEN"
    }
  ]
});

console.log(resp.output_text);
```

```python
from openai import OpenAI

client = OpenAI()

resp = client.responses.create(
    model="gpt-5",
    input="Create a payment link for $20",
    tools=[
        {
            "type": "mcp",
            "server_label": "stripe",
            "server_url": "https://mcp.stripe.com",
            "authorization": "$STRIPE_OAUTH_ACCESS_TOKEN"
        }
    ]
)

print(resp.output_text)
```

```csharp
using OpenAI.Responses;

string authToken = Environment.GetEnvironmentVariable("STRIPE_OAUTH_ACCESS_TOKEN")!;
string key = Environment.GetEnvironmentVariable("OPENAI_API_KEY")!;
OpenAIResponseClient client = new(model: "gpt-5", apiKey: key);

ResponseCreationOptions options = new();
options.Tools.Add(ResponseTool.CreateMcpTool(
    serverLabel: "stripe",
    serverUri: new Uri("https://mcp.stripe.com"),
    authorizationToken: authToken
));

OpenAIResponse response = (OpenAIResponse)client.CreateResponse([
    ResponseItem.CreateUserMessageItem([
        ResponseContentPart.CreateInputTextPart("Create a payment link for $20")
    ])
], options);

Console.WriteLine(response.GetOutputText());
```

--------------------------------

### POST /v1/responses (Connector)

Source: https://platform.openai.com/docs/guides/tools-connectors-mcp

This endpoint allows interaction with a connector using the Responses API. Connectors provide access to external services or data sources, such as Dropbox, for tasks like summarizing documents.

```APIDOC
## POST /v1/responses

### Description
Send a request to the Responses API to interact with a connector.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Headers
- **Content-Type** (string) - Required - Set to `application/json`.
- **Authorization** (string) - Required - Bearer token for authentication (e.g., `Bearer $OPENAI_API_KEY`).

#### Path Parameters
(None)

#### Query Parameters
(None)

#### Request Body
- **model** (string) - Required - The ID of the model to use (e.g., "gpt-5").
- **tools** (array of objects) - Required - A list of tools the model can use.
  - **type** (string) - Required - The type of the tool. Must be "mcp".
  - **server_label** (string) - Required - A label for the connector (e.g., "Dropbox").
  - **connector_id** (string) - Required - The unique identifier for the connector (e.g., "connector_dropbox").
  - **authorization** (string) - Required - An OAuth access token for the connector (e.g., "<oauth access token>").
  - **require_approval** (string) - Required - Policy for requiring user approval for tool calls (e.g., "never").
- **input** (string) - Required - The user's input or prompt for the model (e.g., "Summarize the Q2 earnings report.").

### Request Example
```json
{
  "model": "gpt-5",
  "tools": [
    {
      "type": "mcp",
      "server_label": "Dropbox",
      "connector_id": "connector_dropbox",
      "authorization": "<oauth access token>",
      "require_approval": "never"
    }
  ],
  "input": "Summarize the Q2 earnings report."
}
```

### Response
#### Success Response (200)
- **output_text** (string) - The text response generated by the model after utilizing the connector.

#### Response Example
```json
{
  "output_text": "The Q2 earnings report indicates a strong performance with revenue growth and increased profits. Key areas contributing to success include..."
}
```
```

--------------------------------

### Generate Text with OpenAI Responses API

Source: https://platform.openai.com/docs/context7

This snippet demonstrates how to generate text output from a given prompt using the OpenAI Responses API. It utilizes a specified model, like 'gpt-5', to produce a creative response, such as a bedtime story. The output text is then printed to the console.

```bash
curl https://api.openai.com/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-5",
    "input": "Write a short bedtime story about a unicorn."
  }'
```

```javascript
import OpenAI from "openai";
const client = new OpenAI();

const response = await client.responses.create({
  model: "gpt-5",
  input: "Write a short bedtime story about a unicorn."
});

console.log(response.output_text);
```

```python
from openai import OpenAI
client = OpenAI()

response = client.responses.create(
    model="gpt-5",
    input="Write a short bedtime story about a unicorn."
)

print(response.output_text)
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/api-reference/realtime-server-events/rate_limits

Generates a model response based on provided inputs, conversation context, and various configuration parameters. This endpoint allows for fine-grained control over how the model processes requests and returns data.

```APIDOC
## POST /v1/responses

### Description
Generates a model response based on provided inputs, conversation context, and various configuration parameters. This endpoint allows for fine-grained control over how the model processes requests and returns data.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
_None_

#### Query Parameters
_None_

#### Request Body
- **background** (boolean) - Optional - Defaults to `false`. Whether to run the model response in the background. Learn more.
- **conversation** (string or object) - Optional - Defaults to `null`. The conversation that this response belongs to. Items from this conversation are prepended to `input_items` for this response request. Input items and output items from this response are automatically added to this conversation after this response completes.
- **include** (array) - Optional - Specify additional output data to include in the model response. Currently supported values are:
  * `web_search_call.action.sources`: Include the sources of the web search tool call.
  * `code_interpreter_call.outputs`: Includes the outputs of python code execution in code interpreter tool call items.
  * `computer_call_output.output.image_url`: Include image urls from the computer call output.
  * `file_search_call.results`: Include the search results of the file search tool call.
  * `message.input_image.image_url`: Include image urls from the input message.
  * `message.output_text.logprobs`: Include logprobs with assistant messages.
  * `reasoning.encrypted_content`: Includes an encrypted version of reasoning tokens in reasoning item outputs. This enables reasoning items to be used in multi-turn conversations when using the Responses API statelessly (like when the `store` parameter is set to `false`, or when an organization is enrolled in the zero data retention program).
- **input** (string or array) - Optional - Text, image, or file inputs to the model, used to generate a response. Learn more: Text inputs and outputs, Image inputs, File inputs, Conversation state, Function calling.
- **instructions** (string) - Optional - A system (or developer) message inserted into the model's context. When using along with `previous_response_id`, the instructions from a previous response will not be carried over to the next response. This makes it simple to swap out system (or developer) messages in new responses.
- **max_output_tokens** (integer) - Optional - An upper bound for the number of tokens that can be generated for a response, including visible output tokens and reasoning tokens.
- **max_tool_calls** (integer) - Optional - The maximum number of total calls to built-in tools that can be processed in a response. This maximum number applies across all built-in tool calls, not per individual tool. Any further attempts to call a tool by the model will be ignored.
- **metadata** (map) - Optional - Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard. Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.
- **model** (string) - Optional - Model ID used to generate the response, like `gpt-4o` or `o3`. OpenAI offers a wide range of models with different capabilities, performance characteristics, and price points. Refer to the model guide to browse and compare available models.
- **parallel_tool_calls** (boolean) - Optional - Defaults to `true`. Whether to allow the model to run tool calls in parallel.
- **previous_response_id** (string) - Optional - The unique ID of the previous response to the model. Use this to create multi-turn conversations. Learn more about conversation state. Cannot be used in conjunction with `conversation`.
- **prompt** (object) - Optional - Reference to a prompt template and its variables. Learn more.
- **prompt_cache_key** (string) - Optional - Used by OpenAI to cache responses for similar requests to optimize your cache hit rates. Replaces the `user` field. Learn more.
- **reasoning** (object) - Optional - **gpt-5 and o-series models only** Configuration options for reasoning models.
- **safety_identifier** (string) - Optional - A stable identifier used to help detect users of your application that may be violating OpenAI's usage policies. The IDs should be a string that uniquely identifies each user. We recommend hashing their username or email address, in order to avoid sending us any identifying information. Learn more.
- **service_tier** (string) - Optional - Defaults to `auto`. Specifies the processing type used for serving the request.
  * If set to 'auto', then the request will be processed with the service tier configured in the Project settings. Unless otherwise configured, the Project will use 'default'.
  * If set to 'default', then the request will be processed with the standard pricing and performance for the selected model.
  * If set to 'flex' or 'priority', then the request will be processed with the corresponding service tier.
  * When not set, the default behavior is 'auto'.
- **store** (boolean) - Optional - Defaults to `true`.

### Request Example
```json
{
  "model": "gpt-4o",
  "input": "Tell me a story about a brave knight.",
  "instructions": "Keep the story under 100 words.",
  "max_output_tokens": 50,
  "include": [
    "message.output_text.logprobs"
  ],
  "metadata": {
    "user_id": "user-123",
    "session_id": "session-abc"
  }
}
```

### Response
#### Success Response (200)
- **id** (string) - Unique identifier for the response.
- **object** (string) - The type of object, e.g., "response".
- **created** (integer) - Unix timestamp of when the response was created.
- **model** (string) - The model used for the response.
- **choices** (array) - List of generated choices.
  - **message** (object) - The generated message.
    - **role** (string) - Role of the message (e.g., "assistant").
    - **content** (string) - The content of the message.
- **usage** (object) - Information about token usage.
  - **prompt_tokens** (integer) - Number of tokens in the prompt.
  - **completion_tokens** (integer) - Number of tokens in the completion.
  - **total_tokens** (integer) - Total number of tokens used.
- **service_tier** (string) - The service tier actually used for the request.

#### Response Example
```json
{
  "id": "resp_abc123",
  "object": "response",
  "created": 1678886400,
  "model": "gpt-4o",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Sir Reginald, a knight of unwavering courage, faced the shadow dragon Ignis. His silver sword gleamed, reflecting the beast's fiery breath. With a valiant roar, he dodged a claw swipe and thrust his blade deep into Ignis's scales, saving the kingdom. His legend echoed through time."
      }
    }
  ],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 50,
    "total_tokens": 70
  },
  "service_tier": "default"
}
```
```

--------------------------------

### POST /v1/responses/{response_id}/cancel

Source: https://platform.openai.com/docs/api-reference/chat/message-list

Cancels an in-progress or completed API response. This endpoint returns the updated Response object.

```APIDOC
## POST /v1/responses/{response_id}/cancel

### Description
Cancels an in-progress or completed API response. This endpoint returns the updated Response object.

### Method
POST

### Endpoint
/v1/responses/{response_id}/cancel

### Parameters
#### Path Parameters
- **response_id** (string) - Required - The ID of the response to cancel (e.g., `resp_123`).

#### Query Parameters
None

#### Request Body
None

### Request Example
```json
{}
```

### Response
#### Success Response (200)
- **id** (string) - The unique identifier for the response.
- **object** (string) - The type of object, typically "response".
- **created_at** (integer) - The Unix timestamp (in seconds) when the response was created.
- **status** (string) - The current status of the response (e.g., "completed", "canceled").
- **error** (object/null) - An error object if the response encountered an issue, otherwise null.
- **incomplete_details** (object/null) - Details if the response is incomplete.
- **instructions** (string/null) - Any instructions provided with the response.
- **max_output_tokens** (integer/null) - The maximum number of output tokens set for the response.
- **model** (string) - The model used to generate the response.
- **output** (array) - A list of output items, such as messages or tool calls.
- **parallel_tool_calls** (boolean) - Indicates if parallel tool calls were enabled.
- **previous_response_id** (string/null) - The ID of the previous response in a conversation flow.
- **reasoning** (object/null) - Details about the reasoning process.
- **store** (boolean) - Indicates if the response was stored.
- **temperature** (number) - The sampling temperature used.
- **text** (object) - Text-related properties, including format.
- **tool_choice** (string) - The tool choice strategy.
- **tools** (array) - A list of tools used.
- **top_p** (number) - The nucleus sampling parameter.
- **truncation** (string) - Truncation strategy.
- **usage** (object) - Token usage statistics for input, output, and total tokens.
- **user** (string/null) - The user associated with the response.
- **metadata** (object) - Arbitrary metadata associated with the response.

#### Response Example
```json
{
  "id": "resp_67cb71b351908190a308f3859487620d06981a8637e6bc44",
  "object": "response",
  "created_at": 1741386163,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4o-2024-08-06",
  "output": [
    {
      "type": "message",
      "id": "msg_67cb71b3c2b0819084d481baaaf148f206981a8637e6bc44",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "Silent circuits hum, \nThoughts emerge in data streams— \nDigital dawn breaks.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 32,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 18,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 50
  },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### GET /v1/responses/{response_id}/input_items

Source: https://platform.openai.com/docs/api-reference/files/object

Retrieves a paginated list of input items associated with a specific response, such as messages or content provided to generate the response.

```APIDOC
## GET /v1/responses/{response_id}/input_items

### Description
Returns a list of input items for a given response. This can include messages, context, or any other data that served as input for the response generation.

### Method
GET

### Endpoint
/v1/responses/{response_id}/input_items

### Parameters
#### Path Parameters
- **response_id** (string) - Required - The ID of the response to retrieve input items for.

#### Query Parameters
- **after** (string) - Optional - An item ID to list items after, used in pagination.
- **include** (array) - Optional - Additional fields to include in the response. (e.g., `["metadata"]`)
- **limit** (integer) - Optional - Defaults to 20. A limit on the number of objects to be returned. Limit can range between 1 and 100.
- **order** (string) - Optional - The order to return the input items in. Default is `desc`.
  - `asc`: Return the input items in ascending order.
  - `desc`: Return the input items in descending order.

#### Request Body
*None*

### Request Example
```json
{}
```

### Response
#### Success Response (200)
- **object** (string) - The type of object, typically "list".
- **data** (array) - A list of input item objects.
  - **id** (string) - The ID of the input item.
  - **type** (string) - The type of the input item (e.g., "message").
  - **role** (string) - The role of the input item (e.g., "user").
  - **content** (array) - An array of content blocks within the input item.
    - **type** (string) - The type of content (e.g., "input_text").
    - **text** (string) - The actual text content of the input.
- **first_id** (string) - The ID of the first item in the list.
- **last_id** (string) - The ID of the last item in the list.
- **has_more** (boolean) - Indicates if there are more items to retrieve beyond the current list.

#### Response Example
```json
{
  "object": "list",
  "data": [
    {
      "id": "msg_abc123",
      "type": "message",
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": "Tell me a three sentence bedtime story about a unicorn."
        }
      ]
    }
  ],
  "first_id": "msg_abc123",
  "last_id": "msg_abc123",
  "has_more": false
}
```
```

--------------------------------

### Integrate Connector with OpenAI Responses API

Source: https://platform.openai.com/docs/guides/tools-connectors-mcp

This snippet demonstrates how to integrate and use a pre-defined connector with the OpenAI Responses API. It requires a `connector_id` and an OAuth access token for `authorization`. The example shows how to query the `gpt-5` model to summarize a report using a Dropbox connector.

```curl
curl https://api.openai.com/v1/responses \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $OPENAI_API_KEY" \
-d '{
    "model": "gpt-5",
    "tools": [
      {
        "type": "mcp",
        "server_label": "Dropbox",
        "connector_id": "connector_dropbox",
        "authorization": "<oauth access token>",
        "require_approval": "never"
      }
    ],
    "input": "Summarize the Q2 earnings report."
  }'
```

```javascript
import OpenAI from "openai";
const client = new OpenAI();

const resp = await client.responses.create({
  model: "gpt-5",
  tools: [
    {
      type: "mcp",
      server_label: "Dropbox",
      connector_id: "connector_dropbox",
      authorization: "<oauth access token>",
      require_approval: "never",
    },
  ],
  input: "Summarize the Q2 earnings report.",
});

console.log(resp.output_text);
```

```python
from openai import OpenAI

client = OpenAI()

resp = client.responses.create(
    model="gpt-5",
    tools=[
        {
            "type": "mcp",
            "server_label": "Dropbox",
            "connector_id": "connector_dropbox",
            "authorization": "<oauth access token>",
            "require_approval": "never",
        },
    ],
    input="Summarize the Q2 earnings report.",
)

print(resp.output_text)
```

```csharp
using OpenAI.Responses;

string dropboxToken = Environment.GetEnvironmentVariable("DROPBOX_OAUTH_ACCESS_TOKEN")!;
string key = Environment.GetEnvironmentVariable("OPENAI_API_KEY")!;
OpenAIResponseClient client = new(model: "gpt-5", apiKey: key);

ResponseCreationOptions options = new();
// Additional code would be needed here to add the connector tool and make the API call.
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/models/gpt-5-chat-latest

General endpoint for handling or retrieving responses, with details not specified in the provided text.

```APIDOC
## POST /v1/responses

### Description
This endpoint is for handling or retrieving responses. Specific details about its function, parameters, and response structure are not provided in the source text.

### Method
POST (Assumed, not explicitly stated in the source text)

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
- No path parameters mentioned in the provided text.

#### Query Parameters
- No query parameters mentioned in the provided text.

#### Request Body
- Request body details are not specified in the provided text.

### Request Example
```json
{
  "message": "Request body structure not specified in the provided text."
}
```

### Response
#### Success Response (200)
- Response details are not specified in the provided text.

#### Response Example
```json
{
  "message": "Response structure not specified in the provided text."
}
```
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/api-reference/responses/object

This endpoint creates a new response from the OpenAI model. It allows you to provide an input and receive a generated response based on the specified model.

```APIDOC
## POST /v1/responses

### Description
Creates a new response from the OpenAI model based on the provided input.

### Method
POST

### Endpoint
/v1/responses

### Request Body
- **model** (string) - Required - The ID of the model to use.
- **input** (string) - Required - The input text to generate a response for.

### Request Example
```json
{
  "model": "gpt-4.1",
  "input": "Tell me a three sentence bedtime story about a unicorn."
}
```

### Response
#### Success Response (200)
- **id** (string) - The unique ID of the response.
- **object** (string) - The type of object, which is "response".
- **created_at** (integer) - The timestamp of when the response was created.
- **status** (string) - The status of the response (e.g., "completed").
- **output** (array) - The generated output from the model.

#### Response Example
```json
{
  "id": "resp_67ccd2bed1ec8190b14f964abc0542670bb6a6b452d3795b",
  "object": "response",
  "created_at": 1741476542,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4.1-2025-04-14",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd2bf17f0819081ff3bb2cf6508e60bb6a6b452d3795b",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "In a peaceful grove beneath a silver moon, a unicorn named Lumina discovered a hidden pool that reflected the stars. As she dipped her horn into the water, the pool began to shimmer, revealing a pathway to a magical realm of endless night skies. Filled with wonder, Lumina whispered a wish for all who dream to find their own hidden magic, and as she glanced back, her hoofprints sparkled like stardust.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 36,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 87,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 123
  },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/api-reference/runs

This endpoint allows you to create a new model response by providing a model and input text. It initiates a generation process and returns the resulting response object.

```APIDOC
## POST /v1/responses

### Description
Creates a new model response based on the provided input and specified model.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The ID of the model to use for generating the response (e.g., "gpt-4.1").
- **input** (string) - Required - The input text or prompt for the model to process.

### Request Example
```json
{
  "model": "gpt-4.1",
  "input": "Tell me a three sentence bedtime story about a unicorn."
}
```

### Response
#### Success Response (200)
- **id** (string) - A unique identifier for the response.
- **object** (string) - The type of object, typically "response".
- **created_at** (integer) - A Unix timestamp (in seconds) for when the response was created.
- **status** (string) - The current status of the response (e.g., "completed").
- **error** (object/null) - An error object if the request failed, otherwise null.
- **output** (array) - A list of output messages from the model.
- **usage** (object) - Details about the token usage for the request.

#### Response Example
```json
{
  "id": "resp_67ccd2bed1ec8190b14f964abc0542670bb6a6b452d3795b",
  "object": "response",
  "created_at": 1741476542,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4.1-2025-04-14",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd2bf17f0819081ff3bb2cf6508e60bb6a6b452d3795b",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "In a peaceful grove beneath a silver moon, a unicorn named Lumina discovered a hidden pool that reflected the stars. As she dipped her horn into the water, the pool began to shimmer, revealing a pathway to a magical realm of endless night skies. Filled with wonder, Lumina whispered a wish for all who dream to find their own hidden magic, and as she glanced back, her hoofprints sparkled like stardust.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 36,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 87,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 123
  },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### response.create

Source: https://platform.openai.com/docs/api-reference/certificates/listProjectCertificates

This event instructs the server to create a Response, triggering model inference. It can include optional inference configurations and allows for out-of-band responses that do not write to the default conversation. The server will respond with `response.created`, `item` events, and `response.done`.

```APIDOC
## WebSocket Event: response.create

### Description
This event instructs the server to create a Response, which means triggering model inference. When in Server VAD mode, the server will create Responses automatically. A Response will include at least one Item, and may have two, in which case the second will be a function call. These Items will be appended to the conversation history.
The server will respond with a `response.created` event, events for Items and content created, and finally a `response.done` event to indicate the Response is complete.
The `response.create` event can optionally include inference configuration like `instructions`, and `temperature`. These fields will override the Session's configuration for this Response only.
Clients can set `conversation` to `none` to create a Response that does not write to the default Conversation. Arbitrary input can be provided with the `input` field, which is an array accepting raw Items and references to existing Items.

### Method
WebSocket Event

### Endpoint
N/A (WebSocket message)

### Parameters
#### Request Body
- **event_id** (string) - Optional - Client-generated ID used to identify this event.
- **type** (string) - Required - The event type, must be `response.create`.
- **response** (object) - Optional - Create a new Realtime response with these parameters.
  - **instructions** (string) - Optional - Override session instructions for this response.
  - **tools** (array) - Optional - Override session tools for this response. An empty array clears session tools.
  - **conversation** (string) - Optional - Set to `"none"` to create a Response that does not write to the default Conversation.
  - **output_modalities** (array of strings) - Optional - Specify desired output modalities, e.g., `["text"]`.
  - **input** (array of objects) - Optional - Arbitrary input as an array of raw Items or references to existing Items.
    - **type** (string) - Type of input item, e.g., `"item_reference"`, `"message"`.
    - **id** (string) - Required if `type` is `"item_reference"` - ID of the referenced item.
    - **role** (string) - Required if `type` is `"message"` - Role of the message, e.g., `"user"`.
    - **content** (array of objects) - Required if `type` is `"message"` - Content of the message.
      - **type** (string) - Type of content, e.g., `"input_text"`.
      - **text** (string) - The text content.

### Request Example
```json
{
  "type": "response.create"
}
```

```json
{
  "type": "response.create",
  "response": {
    "instructions": "Provide a concise answer.",
    "tools": [],
    "conversation": "none",
    "output_modalities": ["text"],
    "input": [
      {
        "type": "item_reference",
        "id": "item_12345"
      },
      {
        "type": "message",
        "role": "user",
        "content": [
          {
            "type": "input_text",
            "text": "Summarize the above message in one sentence."
          }
        ]
      }
    ]
  }
}
```

### Response
#### Success Response (Event Stream)
- `response.created` event - Indicates the response has started.
- `item` events - For each item and content created.
- `response.done` event - Indicates the response is complete, including its final status.
```

--------------------------------

### Set GPT-5 Reasoning Effort with Responses API (cURL)

Source: https://platform.openai.com/docs/guides/latest-model_gallery=open&galleryitem=espresso

This cURL command sends a POST request to the OpenAI GPT-5 Responses API, specifying 'minimal' reasoning effort for the model when generating a response. It requires an OpenAI API key for authentication, passed in the 'Authorization' header.

```bash
curl --request POST \
--url https://api.openai.com/v1/responses \
--header "Authorization: Bearer $OPENAI_API_KEY" \
--header 'Content-type: application/json' \
--data '{
  "model": "gpt-5",
  "input": "How much gold would it take to coat the Statue of Liberty in a 1mm layer?",
  "reasoning": {
    "effort": "minimal"
  }
}'
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/api-reference/certificates

Creates a new model response using a specified model and input text. The API generates a response based on the provided input.

```APIDOC
## POST /v1/responses

### Description
Creates a new model response by sending input text to a specified model.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
(None)

#### Query Parameters
(None)

#### Request Body
- **model** (string) - Required - The ID of the model to use for generating the response. Example: "gpt-4.1"
- **input** (string) - Required - The input text for which the model should generate a response. Example: "Tell me a three sentence bedtime story about a unicorn."

### Request Example
```json
{
  "model": "gpt-4.1",
  "input": "Tell me a three sentence bedtime story about a unicorn."
}
```

### Response
#### Success Response (200)
- **id** (string) - A unique identifier for the response.
- **object** (string) - The type of object returned, typically "response".
- **created_at** (integer) - A Unix timestamp (in seconds) for when the response was created.
- **status** (string) - The status of the response generation (e.g., "completed").
- **error** (object/null) - Details about any error that occurred during response generation.
- **incomplete_details** (object/null) - Additional details if the response is incomplete.
- **instructions** (object/null) - Any instructions provided to the model.
- **max_output_tokens** (integer/null) - The maximum number of output tokens allowed.
- **model** (string) - The ID of the model used to generate the response.
- **output** (array) - A list of output messages generated by the model.
  - **type** (string) - Type of output, e.g., "message".
  - **id** (string) - Identifier for the output message.
  - **status** (string) - Status of the output message.
  - **role** (string) - Role of the entity generating the message, e.g., "assistant".
  - **content** (array) - List of content parts within the message.
    - **type** (string) - Type of content, e.g., "output_text".
    - **text** (string) - The actual generated text content.
    - **annotations** (array) - Any annotations associated with the text.
- **parallel_tool_calls** (boolean) - Indicates if parallel tool calls were made.
- **previous_response_id** (string/null) - The ID of a previous response if this is a follow-up.
- **reasoning** (object) - Details about the model's reasoning process.
- **store** (boolean) - Indicates if the response was stored.
- **temperature** (number) - The sampling temperature used for generation.
- **text** (object) - Text-specific properties.
  - **format** (object)
    - **type** (string) - Format type, e.g., "text".
- **tool_choice** (string) - Tool choice strategy used.
- **tools** (array) - List of tools used.
- **top_p** (number) - The top_p sampling parameter used for generation.
- **truncation** (string) - Truncation strategy used.
- **usage** (object) - Token usage statistics.
  - **input_tokens** (integer) - Number of input tokens consumed.
  - **input_tokens_details** (object) - Details about input tokens.
  - **output_tokens** (integer) - Number of output tokens generated.
  - **output_tokens_details** (object) - Details about output tokens.
  - **total_tokens** (integer) - Total number of tokens (input + output).
- **user** (string/null) - The user ID associated with the request.
- **metadata** (object) - Arbitrary metadata associated with the response.

#### Response Example
```json
{
  "id": "resp_67ccd2bed1ec8190b14f964abc0542670bb6a6b452d3795b",
  "object": "response",
  "created_at": 1741476542,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4.1-2025-04-14",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd2bf17f0819081ff3bb2cf6508e60bb6a6b452d3795b",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "In a peaceful grove beneath a silver moon, a unicorn named Lumina discovered a hidden pool that reflected the stars. As she dipped her horn into the water, the pool began to shimmer, revealing a pathway to a magical realm of endless night skies. Filled with wonder, Lumina whispered a wish for all who dream to find their own hidden magic, and as she glanced back, her hoofprints sparkled like stardust.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 36,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 87,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 123
  },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### response.create Event

Source: https://platform.openai.com/docs/api-reference/assistants/listAssistants

Instructs the server to create a Response, triggering model inference. It allows for custom configurations and out-of-band responses.

```APIDOC
## EVENT response.create

### Description
This event instructs the server to create a Response, which means triggering model inference. When in Server VAD mode, the server will create Responses automatically. A Response will include at least one Item, and may have two, in which case the second will be a function call. These Items will be appended to the conversation history by default. The server will respond with a `response.created` event, events for Items and content created, and finally a `response.done` event to indicate the Response is complete. Clients can set `conversation` to `none` to create a Response that does not write to the default Conversation. Arbitrary input can be provided with the `input` field, which is an array accepting raw Items and references to existing Items.

### Method
EVENT

### Endpoint
response.create

### Parameters
#### Request Body
- **event_id** (string) - Optional - Client-generated ID used to identify this event.
- **response** (object) - Optional - Create a new Realtime response with these parameters. (Refer to example for sub-properties)
  - **instructions** (string) - Optional - Override session instructions for this response.
  - **tools** (array) - Optional - Override session tools for this response.
  - **conversation** (string) - Optional - Set to `none` to create a response that does not write to the default conversation.
  - **output_modalities** (array of strings) - Optional - Desired output modalities (e.g., ["text"]).
  - **metadata** (object) - Optional - Custom metadata for the response.
  - **input** (array) - Optional - Array of raw items or references to existing items to use as input.
    - **type** (string) - Required - Type of input item (e.g., "item_reference", "message").
    - **id** (string) - Required (if type is "item_reference") - ID of the referenced item.
    - **role** (string) - Required (if type is "message") - Role of the message sender (e.g., "user").
    - **content** (array) - Required (if type is "message") - Array of content parts.
      - **type** (string) - Required - Type of content part (e.g., "input_text").
      - **text** (string) - Required - The text content.
- **type** (string) - Required - The event type, must be `response.create`.

### Request Example
```json
{
  "type": "response.create",
  "response": {
    "instructions": "Provide a concise answer.",
    "tools": [],
    "conversation": "none",
    "output_modalities": ["text"],
    "metadata": {
      "response_purpose": "summarization"
    },
    "input": [
      {
        "type": "item_reference",
        "id": "item_12345"
      },
      {
        "type": "message",
        "role": "user",
        "content": [
          {
            "type": "input_text",
            "text": "Summarize the above message in one sentence."
          }
        ]
      }
    ]
  }
}
```

### Response
#### Success Response
The server will respond with a `response.created` event, events for Items and content created, and finally a `response.done` event.

#### Response Example
No explicit response body provided, success is indicated by `response.created` and `response.done` events.
```

--------------------------------

### Cancel an OpenAI Response

Source: https://platform.openai.com/docs/api-reference/audio/createTranslation

This snippet demonstrates how to cancel an existing OpenAI response. It requires an OpenAI API key for authentication and the ID of the response to be canceled. The operation returns a Response object indicating the cancellation status.

```curl
curl -X POST https://api.openai.com/v1/responses/resp_123/cancel \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY"
```

```javascript
import OpenAI from "openai";
const client = new OpenAI();

const response = await client.responses.cancel("resp_123");
console.log(response);
```

```python
from openai import OpenAI
client = OpenAI()

response = client.responses.cancel("resp_123")
print(response)
```

--------------------------------

### GET /v1/responses

Source: https://platform.openai.com/docs/models/davinci-002

This endpoint is typically used to retrieve or manage responses generated by the davinci-002 model or other related services.

```APIDOC
## GET /v1/responses

### Description
This endpoint is typically used to retrieve or manage responses generated by the davinci-002 model or other related services.

### Method
GET

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
None

### Request Example
{
  "message": "No example provided in the source text."
}

### Response
#### Success Response (200)
No response fields specified in the source text.

#### Response Example
{
  "message": "No example provided in the source text."
}
```

--------------------------------

### POST /responses

Source: https://platform.openai.com/docs/api-reference/batch/object

Generates a model response based on the provided inputs, conversation context, and configuration parameters. This endpoint allows for flexible control over the model's behavior, including tool usage, output format, and conversation history integration.

```APIDOC
## POST /responses

### Description
Generates a model response based on the provided inputs, conversation context, and configuration parameters. This endpoint allows for flexible control over the model's behavior, including tool usage, output format, and conversation history integration.

### Method
POST

### Endpoint
/responses

### Parameters
#### Path Parameters
_None_

#### Query Parameters
_None_

#### Request Body
- **background** (boolean) - Optional - Defaults to `false`. Whether to run the model response in the background. Learn more.
- **conversation** (string or object) - Optional - Defaults to `null`. The conversation that this response belongs to. Items from this conversation are prepended to `input_items` for this response request. Input items and output items from this response are automatically added to this conversation after this response completes.
- **include** (array) - Optional - Specify additional output data to include in the model response. Currently supported values are:
  * `web_search_call.action.sources`: Include the sources of the web search tool call.
  * `code_interpreter_call.outputs`: Includes the outputs of python code execution in code interpreter tool call items.
  * `computer_call_output.output.image_url`: Include image urls from the computer call output.
  * `file_search_call.results`: Include the search results of the file search tool call.
  * `message.input_image.image_url`: Include image urls from the input message.
  * `message.output_text.logprobs`: Include logprobs with assistant messages.
  * `reasoning.encrypted_content`: Includes an encrypted version of reasoning tokens in reasoning item outputs.
- **input** (string or array) - Optional - Text, image, or file inputs to the model, used to generate a response.
- **instructions** (string) - Optional - A system (or developer) message inserted into the model's context. When using along with `previous_response_id`, the instructions from a previous response will not be carried over to the next response.
- **max_output_tokens** (integer) - Optional - An upper bound for the number of tokens that can be generated for a response, including visible output tokens and reasoning tokens.
- **max_tool_calls** (integer) - Optional - The maximum number of total calls to built-in tools that can be processed in a response. This maximum number applies across all built-in tool calls, not per individual tool. Any further attempts to call a tool by the model will be ignored.
- **metadata** (map) - Optional - Set of 16 key-value pairs that can be attached to an object. Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.
- **model** (string) - Optional - Model ID used to generate the response, like `gpt-4o` or `o3`. Refer to the model guide to browse and compare available models.
- **parallel_tool_calls** (boolean) - Optional - Defaults to `true`. Whether to allow the model to run tool calls in parallel.
- **previous_response_id** (string) - Optional - The unique ID of the previous response to the model. Use this to create multi-turn conversations. Cannot be used in conjunction with `conversation`.
- **prompt** (object) - Optional - Reference to a prompt template and its variables.
- **prompt_cache_key** (string) - Optional - Used by OpenAI to cache responses for similar requests to optimize your cache hit rates. Replaces the `user` field.
- **reasoning** (object) - Optional - **gpt-5 and o-series models only**. Configuration options for reasoning models.
- **safety_identifier** (string) - Optional - A stable identifier used to help detect users of your application that may be violating OpenAI's usage policies. IDs should be a string that uniquely identifies each user.
- **service_tier** (string) - Optional - Defaults to `auto`. Specifies the processing type used for serving the request. Possible values:
  * `auto`: Request will be processed with the service tier configured in the Project settings. Unless otherwise configured, the Project will use 'default'.
  * `default`: Request will be processed with the standard pricing and performance for the selected model.
  * `flex` or `priority`: Request will be processed with the corresponding service tier.
  When the `service_tier` parameter is set, the response body will include the `service_tier` value based on the processing mode actually used to serve the request. This response value may be different from the value set in the parameter.
- **store** (boolean) - Optional - Defaults to `true`.

### Request Example
```json
{
  "input": "Tell me a joke about a computer.",
  "model": "gpt-4o",
  "conversation": "conv_789xyz",
  "max_output_tokens": 100,
  "include": [
    "web_search_call.action.sources"
  ],
  "instructions": "Respond concisely."
}
```

### Response
#### Success Response (200)
- **id** (string) - The unique identifier for the generated response.
- **output** (object) - The primary output content generated by the model.
- **model** (string) - The model ID that generated the response.
- **created_at** (string) - Timestamp of when the response was created.
- **usage** (object) - Information about token usage, if applicable.

#### Response Example
```json
{
  "id": "resp_abc123def456",
  "output": {
    "text": "Why was the computer cold? Because it left its Windows open!"
  },
  "model": "gpt-4o",
  "created_at": "2023-10-27T10:00:00Z",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```
```

--------------------------------

### Define Function for Responses API (JSON)

Source: https://platform.openai.com/docs/guides/migrate-to-responses

This JSON object defines a `get_weather` function compatible with the Responses API. It illustrates the internally-tagged polymorphism where function properties are direct siblings of `"type"`. The API's default strict behavior is implicitly used, meaning no explicit `"strict"` field is required for this configuration.

```json
{
  "type": "function",
  "name": "get_weather",
  "description": "Determine weather in my location",
  "parameters": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string"
      }
    },
    "additionalProperties": false,
    "required": [
      "location",
      "unit"
    ]
  }
}
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/api-reference/chat/message-list

Creates a new model response based on the provided input and model. This endpoint allows you to send a text prompt to an OpenAI model and receive a generated response.

```APIDOC
## POST /v1/responses

### Description
Creates a new model response based on the provided input and model. This endpoint allows you to send a text prompt to an OpenAI model and receive a generated response.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
(None)

#### Query Parameters
(None)

#### Request Body
- **model** (string) - Required - The ID of the model to use for generating the response (e.g., "gpt-4.1").
- **input** (string) - Required - The text input for which to generate a response (e.g., "Tell me a three sentence bedtime story about a unicorn.").

### Request Example
```json
{
  "model": "gpt-4.1",
  "input": "Tell me a three sentence bedtime story about a unicorn."
}
```

### Response
#### Success Response (200)
- **id** (string) - Unique identifier for the response object.
- **object** (string) - The type of object, typically "response".
- **created_at** (integer) - Unix timestamp (in seconds) of when the response was created.
- **status** (string) - The current status of the response (e.g., "completed").
- **model** (string) - The ID of the model that generated the response.
- **output** (array) - An array of output messages generated by the model.
  - **output[].type** (string) - The type of output (e.g., "message").
  - **output[].id** (string) - Unique identifier for the output message.
  - **output[].status** (string) - Status of the output message.
  - **output[].role** (string) - The role of the entity that generated this content (e.g., "assistant").
  - **output[].content** (array) - An array of content parts within the message.
    - **output[].content[].type** (string) - The type of content part (e.g., "output_text").
    - **output[].content[].text** (string) - The actual generated text.
    - **output[].content[].annotations** (array) - Any annotations associated with the text.
- **usage** (object) - Usage statistics for the request.
  - **usage.input_tokens** (integer) - Number of input tokens used.
  - **usage.output_tokens** (integer) - Number of output tokens generated.
  - **usage.total_tokens** (integer) - Total number of tokens used (input + output).

#### Response Example
```json
{
  "id": "resp_67ccd2bed1ec8190b14f964abc0542670bb6a6b452d3795b",
  "object": "response",
  "created_at": 1741476542,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4.1-2025-04-14",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd2bf17f0819081ff3bb2cf6508e60bb6a6b452d3795b",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "In a peaceful grove beneath a silver moon, a unicorn named Lumina discovered a hidden pool that reflected the stars. As she dipped her horn into the water, the pool began to shimmer, revealing a pathway to a magical realm of endless night skies. Filled with wonder, Lumina whispered a wish for all who dream to find their own hidden magic, and as she glanced back, her hoofprints sparkled like stardust.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 36,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 87,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 123
  },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/api-reference/webhook-events/fine_tuning

This endpoint allows you to create a model response by providing a model ID and input text. The API will generate and return a response based on the specified model.

```APIDOC
## POST /v1/responses

### Description
Create a model response based on a given input. This endpoint takes text input and a model identifier to generate a conversational or informational response.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The ID of the model to use for generating the response (e.g., "gpt-4.1").
- **input** (string) - Required - The input text or prompt for which to generate a response.

### Request Example
```json
{
  "model": "gpt-4.1",
  "input": "Tell me a three sentence bedtime story about a unicorn."
}
```

### Response
#### Success Response (200)
- **id** (string) - Unique identifier for the generated response.
- **object** (string) - The type of object returned, typically "response".
- **created_at** (integer) - Unix timestamp when the response was created.
- **status** (string) - The status of the response generation (e.g., "completed").
- **error** (object | null) - Details if an error occurred during response generation.
- **incomplete_details** (object | null) - Details if the response is incomplete.
- **instructions** (array | null) - Any instructions used during the generation process.
- **max_output_tokens** (integer | null) - The maximum number of output tokens allowed for the response.
- **model** (string) - The identifier of the model that generated the response.
- **output** (array) - A list of output messages.
  - **type** (string) - The type of output, e.g., "message".
  - **id** (string) - Unique identifier for the output message.
  - **status** (string) - Status of the individual output message.
  - **role** (string) - The role of the entity producing the content (e.g., "assistant").
  - **content** (array) - An array of content parts.
    - **type** (string) - The type of content, e.g., "output_text".
    - **text** (string) - The generated text content of the response.
    - **annotations** (array) - Any annotations associated with the text.
- **parallel_tool_calls** (boolean) - Indicates if parallel tool calls were enabled.
- **previous_response_id** (string | null) - The ID of a previous response if this is part of a chained interaction.
- **reasoning** (object) - Information about the model's reasoning process.
  - **effort** (string | null) - Description of the effort level.
  - **summary** (string | null) - Summary of the reasoning process.
- **store** (boolean) - Whether the response is stored.
- **temperature** (number) - The sampling temperature used for generation.
- **text** (object) - Text formatting details.
  - **format** (object)
    - **type** (string) - The format type of the text, e.g., "text".
- **tool_choice** (string) - Strategy for tool selection.
- **tools** (array) - A list of tools used by the model.
- **top_p** (number) - The top-p sampling value used.
- **truncation** (string) - Truncation strategy applied.
- **usage** (object) - Token usage statistics for the request.
  - **input_tokens** (integer) - Number of tokens in the input.
  - **input_tokens_details** (object)
    - **cached_tokens** (integer) - Number of cached input tokens.
  - **output_tokens** (integer) - Number of tokens in the output.
  - **output_tokens_details** (object)
    - **reasoning_tokens** (integer) - Number of reasoning tokens.
  - **total_tokens** (integer) - Total number of tokens used.
- **user** (string | null) - User identifier, if provided.
- **metadata** (object) - Additional metadata.

### Response Example
```json
{
  "id": "resp_67ccd2bed1ec8190b14f964abc0542670bb6a6b452d3795b",
  "object": "response",
  "created_at": 1741476542,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4.1-2025-04-14",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd2bf17f0819081ff3bb2cf6508e60bb6a6b452d3795b",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "In a peaceful grove beneath a silver moon, a unicorn named Lumina discovered a hidden pool that reflected the stars. As she dipped her horn into the water, the pool began to shimmer, revealing a pathway to a magical realm of endless night skies. Filled with wonder, Lumina whispered a wish for all who dream to find their own hidden magic, and as she glanced back, her hoofprints sparkled like stardust.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 36,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 87,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 123
  },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### POST /responses

Source: https://platform.openai.com/docs/api-reference/evals/create

This endpoint allows you to generate a model response by providing input text, images, or files, and configuring various parameters like conversation context, output options, and model selection.

```APIDOC
## POST /responses

### Description
Generates a model response based on the provided inputs and configuration. This API supports multi-turn conversations, tool calls, and various output inclusions.

### Method
POST

### Endpoint
/responses

### Parameters
#### Path Parameters
_None_

#### Query Parameters
_None_

#### Request Body
- **background** (boolean) - Optional - Defaults to `false`. Whether to run the model response in the background. Learn more.
- **conversation** (string or object) - Optional - Defaults to `null`. The conversation that this response belongs to. Items from this conversation are prepended to `input_items` for this response request. Input items and output items from this response are automatically added to this conversation after this response completes.
- **include** (array) - Optional - Specify additional output data to include in the model response. Currently supported values are:
  * `web_search_call.action.sources`: Include the sources of the web search tool call.
  * `code_interpreter_call.outputs`: Includes the outputs of python code execution in code interpreter tool call items.
  * `computer_call_output.output.image_url`: Include image urls from the computer call output.
  * `file_search_call.results`: Include the search results of the file search tool call.
  * `message.input_image.image_url`: Include image urls from the input message.
  * `message.output_text.logprobs`: Include logprobs with assistant messages.
  * `reasoning.encrypted_content`: Includes an encrypted version of reasoning tokens in reasoning item outputs. This enables reasoning items to be used in multi-turn conversations when using the Responses API statelessly (like when the `store` parameter is set to `false`, or when an organization is enrolled in the zero data retention program).
- **input** (string or array) - Optional - Text, image, or file inputs to the model, used to generate a response. Learn more:
  * Text inputs and outputs
  * Image inputs
  * File inputs
  * Conversation state
  * Function calling
- **instructions** (string) - Optional - A system (or developer) message inserted into the model's context. When using along with `previous_response_id`, the instructions from a previous response will not be carried over to the next response. This makes it simple to swap out system (or developer) messages in new responses.
- **max_output_tokens** (integer) - Optional - An upper bound for the number of tokens that can be generated for a response, including visible output tokens and reasoning tokens.
- **max_tool_calls** (integer) - Optional - The maximum number of total calls to built-in tools that can be processed in a response. This maximum number applies across all built-in tool calls, not per individual tool. Any further attempts to call a tool by the model will be ignored.
- **metadata** (map) - Optional - Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard. Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.
- **model** (string) - Optional - Model ID used to generate the response, like `gpt-4o` or `o3`. OpenAI offers a wide range of models with different capabilities, performance characteristics, and price points. Refer to the model guide to browse and compare available models.
- **parallel_tool_calls** (boolean) - Optional - Defaults to `true`. Whether to allow the model to run tool calls in parallel.
- **previous_response_id** (string) - Optional - The unique ID of the previous response to the model. Use this to create multi-turn conversations. Learn more about conversation state. Cannot be used in conjunction with `conversation`.
- **prompt** (object) - Optional - Reference to a prompt template and its variables. Learn more.
- **prompt_cache_key** (string) - Optional - Used by OpenAI to cache responses for similar requests to optimize your cache hit rates. Replaces the `user` field. Learn more.
- **reasoning** (object) - Optional - **gpt-5 and o-series models only**. Configuration options for reasoning models.
- **safety_identifier** (string) - Optional - A stable identifier used to help detect users of your application that may be violating OpenAI's usage policies. The IDs should be a string that uniquely identifies each user. We recommend hashing their username or email address, in order to avoid sending us any identifying information. Learn more.
- **service_tier** (string) - Optional - Defaults to `auto`. Specifies the processing type used for serving the request.
  * If set to 'auto', then the request will be processed with the service tier configured in the Project settings. Unless otherwise configured, the Project will use 'default'.
  * If set to 'default', then the request will be processed with the standard pricing and performance for the selected model.
  * If set to 'flex' or 'priority', then the request will be processed with the corresponding service tier.
  * When not set, the default behavior is 'auto'.

When the `service_tier` parameter is set, the response body will include the `service_tier` value based on the processing mode actually used to serve the request. This response value may be different from the value set in the parameter.
- **store** (boolean) - Optional - Defaults to `true`.

### Request Example
```json
{
  "model": "gpt-4o",
  "input": "Tell me a short story about a brave knight.",
  "instructions": "The story should be optimistic and end happily.",
  "max_output_tokens": 100,
  "include": [
    "message.output_text.logprobs"
  ],
  "metadata": {
    "user_id": "user-123",
    "session_id": "sess-abc"
  }
}
```

### Response
#### Success Response (200)
- **id** (string) - Unique identifier for the generated response.
- **output** (object) - Contains the model's generated output.
- **model** (string) - The model ID used for generation.
- **usage** (object) - Token usage statistics for the request.

#### Response Example
```json
{
  "id": "resp_123abc",
  "output": {
    "text": "Once upon a time, in a kingdom far away, lived Sir Reginald, a knight known not for his might, but for his unwavering kindness. One day, a mischievous dragon stole the kingdom's prized Golden Acorn. Sir Reginald, armed with only his wit and a bag of crunchy carrots, ventured forth. He found the dragon, not menacing, but simply hungry. Sharing his carrots, Reginald befriended the dragon, who happily returned the acorn. The kingdom rejoiced, and Sir Reginald became a legend, proving that sometimes, the kindest heart is the bravest of all.",
    "logprobs": {
      "token_logprobs": [
        {
          "token": "Once",
          "logprob": -0.123
        },
        {
          "token": "upon",
          "logprob": -0.056
        }
      ]
    }
  },
  "model": "gpt-4o",
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 120,
    "total_tokens": 145
  }
}
```
```

--------------------------------

### Image Generation Response Schema

Source: https://platform.openai.com/docs/api-reference/chat/get

This schema describes the structure of the successful response object from an image generation API endpoint.

```APIDOC
## Image Generation Response Schema

### Description
This schema describes the structure of the successful response object from an image generation API endpoint.

### Fields
- **background** (string) - The background parameter used for the image generation. Either `transparent` or `opaque`.
- **created** (integer) - The Unix timestamp (in seconds) of when the image was created.
- **data** (array) - The list of generated images. Each item in the array is an object with a `b64_json` field.
  - **b64_json** (string) - Base64-encoded image data.
- **output_format** (string) - The output format of the image generation. Either `png`, `webp`, or `jpeg`.
- **quality** (string) - The quality of the image generated. Either `low`, `medium`, or `high`.
- **size** (string) - The size of the image generated. Either `1024x1024`, `1024x1536`, or `1536x1024`.
- **usage** (object) - For `gpt-image-1` only, the token usage information for the image generation.
  - **total_tokens** (integer) - Total tokens used for the generation.
  - **input_tokens** (integer) - Input tokens used for the generation.
  - **output_tokens** (integer) - Output tokens used for the generation.
  - **input_tokens_details** (object) - Details about the input tokens.
    - **text_tokens** (integer) - Number of text tokens in the input.
    - **image_tokens** (integer) - Number of image tokens in the input.

### Object Example
```json
{
  "created": 1713833628,
  "data": [
    {
      "b64_json": "..."
    }
  ],
  "background": "transparent",
  "output_format": "png",
  "size": "1024x1024",
  "quality": "high",
  "usage": {
    "total_tokens": 100,
    "input_tokens": 50,
    "output_tokens": 50,
    "input_tokens_details": {
      "text_tokens": 10,
      "image_tokens": 40
    }
  }
}
```
```

--------------------------------

### Image Generation Response Object

Source: https://platform.openai.com/docs/api-reference/audio/json-object

Defines the structure of the response object returned by a successful image generation API call.

```APIDOC
## Image Generation Response Object

### Description
This object describes the structure of a successful response from an image generation endpoint. It includes metadata about the generated image(s) and usage information.

### Fields
- **background** (string) - The background parameter used for the image generation. Either `transparent` or `opaque`.
- **created** (integer) - The Unix timestamp (in seconds) of when the image was created.
- **data** (array) - The list of generated images. Each item in the array is an object with a `b64_json` field.
  - **b64_json** (string) - Base64-encoded image data.
- **output_format** (string) - The output format of the image generation. Either `png`, `webp`, or `jpeg`.
- **quality** (string) - The quality of the image generated. Either `low`, `medium`, or `high`.
- **size** (string) - The size of the image generated. Either `1024x1024`, `1024x1536`, or `1536x1024`.
- **usage** (object) - For `gpt-image-1` only, the token usage information for the image generation.
  - **total_tokens** (integer) - Total tokens used for the request.
  - **input_tokens** (integer) - Tokens used for input.
  - **output_tokens** (integer) - Tokens used for output.
  - **input_tokens_details** (object) - Detailed breakdown of input tokens.
    - **text_tokens** (integer) - Text tokens in input.
    - **image_tokens** (integer) - Image tokens in input.

### Example
```json
{
  "created": 1713833628,
  "data": [
    {
      "b64_json": "..."
    }
  ],
  "background": "transparent",
  "output_format": "png",
  "size": "1024x1024",
  "quality": "high",
  "usage": {
    "total_tokens": 100,
    "input_tokens": 50,
    "output_tokens": 50,
    "input_tokens_details": {
      "text_tokens": 10,
      "image_tokens": 40
    }
  }
}
```
```

--------------------------------

### Call OpenAI Responses API using cURL

Source: https://platform.openai.com/docs/guides/deep-research

This cURL command illustrates how to directly interact with the OpenAI Responses API endpoint via a POST request. It includes authentication with an API key and a JSON payload specifying the model, input, and instructions for the API call.

```bash
curl https://api.openai.com/v1/responses \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4.1",
    "input": "Research surfboards for me. Im interested in ...",
    "instructions": "You are a helpful assistant that generates a prompt for a deep research task. Examine the users prompt and generate a set of clarifying questions that will help the deep research model generate a better response."
  }'
```

--------------------------------

### Event: response.failed

Source: https://platform.openai.com/docs/api-reference/assistants-streaming/run-step-delta-object

Sent when a background model response has failed. This event notifies the client when an API model response process encounters an unrecoverable error, providing details about the event and the failed response.

```APIDOC
## Event: response.failed

### Description
Sent when a background model response has failed.

### Method
Event Notification

### Endpoint
response.failed

### Parameters
*Event notifications do not have path, query, or request body parameters in the traditional sense, as they are payloads sent by the system.*

### Request Example
*Not applicable for events received, this is the payload structure.*

### Response
#### Event Payload
- **id** (string) - The unique ID of the event.
- **object** (string) - The object of the event. Always `event`.
- **type** (string) (Enum: `response.failed`) - The type of the event. Always `response.failed`.
- **created_at** (integer) - The Unix timestamp (in seconds) of when the model response failed.
- **data** (object) - Event data payload.
  - **id** (string) - The ID of the failed response (e.g., `resp_abc123`).

#### Response Example
```json
{
  "id": "evt_abc123",
  "type": "response.failed",
  "created_at": 1719168000,
  "data": {
    "id": "resp_abc123"
  }
}
```
```

--------------------------------

### API Response Object Structure

Source: https://platform.openai.com/docs/api-reference/threads

This section details the structure of a typical response object returned by the OpenAI platform APIs, including various parameters and their types, representing a completed model interaction.

```APIDOC
## API Response Object Structure

### Description
This section details the structure of a typical response object returned by the OpenAI platform APIs, including various parameters and their types, representing a completed model interaction.

### Response
#### Success Response (200)
- **id** (string) - Unique identifier for the response.
- **object** (string) - The type of object returned, typically "response".
- **created_at** (integer) - Unix timestamp (in seconds) when the response was created.
- **status** (string) - The current status of the response, e.g., "completed".
- **error** (object or null) - Details if an error occurred during the request.
- **incomplete_details** (object or null) - Details if the response is incomplete.
- **instructions** (object or null) - Instructions provided or used for the response.
- **max_output_tokens** (integer or null) - The maximum number of output tokens specified for the response.
- **model** (string) - The specific model used to generate the response, e.g., "gpt-4o-2024-08-06".
- **output** (array) - An array of output items generated by the model.
    - **type** (string) - The type of output item, e.g., "message".
    - **id** (string) - Unique identifier for the output item.
    - **status** (string) - The status of this specific output item.
    - **role** (string) - The role of the entity generating the content, e.g., "assistant".
    - **content** (array) - An array of content parts within the output item.
        - **type** (string) - The type of content part, e.g., "output_text".
        - **text** (string) - The actual generated text content.
        - **annotations** (array) - Any annotations related to the content.
- **parallel_tool_calls** (boolean) - Indicates whether parallel tool calls were enabled or utilized.
- **previous_response_id** (string or null) - The ID of a previous response if this is part of a sequence.
- **reasoning** (object) - Details about the model's internal reasoning process.
    - **effort** (string or null) - The effort level associated with the reasoning.
    - **summary** (string or null) - A summary of the reasoning process.
- **store** (boolean) - Indicates if the response should be stored.
- **temperature** (number) - The sampling temperature used for generation (0 to 2).
- **text** (object) - Details about the text format.
    - **format** (object)
        - **type** (string) - The type of text format, e.g., "text".
- **tool_choice** (string) - The tool choice strategy used, e.g., "auto".
- **tools** (array) - A list of tools available or used during the response generation.
- **top_p** (number) - The nucleus sampling parameter used (0 to 1).
- **truncation** (string) - The truncation strategy applied, e.g., "disabled".
- **usage** (object) - Detailed token usage statistics for the response.
    - **input_tokens** (integer) - The number of tokens in the input.
    - **input_tokens_details** (object)
        - **cached_tokens** (integer) - The number of cached input tokens.
    - **output_tokens** (integer) - The number of tokens in the output.
    - **output_tokens_details** (object)
        - **reasoning_tokens** (integer) - The number of tokens used for reasoning.
    - **total_tokens** (integer) - The total number of tokens (input + output).
- **user** (string or null) - The user identifier associated with the request (deprecated).
- **metadata** (object) - An object for additional metadata.

#### Response Example
```json
{
  "id": "resp_67ccd3a9da748190baa7f1570fe91ac604becb25c45c1d41",
  "object": "response",
  "created_at": 1741476777,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null
```

--------------------------------

### Model Response Object Structure

Source: https://platform.openai.com/docs/api-reference/certificates/listOrganizationCertificates

This document details the structure of the response object returned by various OpenAI model APIs, including all possible fields and their data types.

```APIDOC
## SCHEMA Response Object

### Description
This document details the structure of the response object returned by various OpenAI model APIs, including all possible fields and their data types and purposes.

### Method
N/A (Schema Definition)

### Endpoint
N/A (Schema Definition)

### Response
#### Response Object Fields
- **background** (boolean) - Whether to run the model response in the background.
- **conversation** (object) - The conversation that this response belongs to. Input items and output items from this response are automatically added to this conversation.
- **created_at** (number) - Unix timestamp (in seconds) of when this Response was created.
- **error** (object) - An error object returned when the model fails to generate a Response.
- **id** (string) - Unique identifier for this Response.
- **incomplete_details** (object) - Details about why the response is incomplete.
- **instructions** (string or array) - A system (or developer) message inserted into the model's context. When using along with `previous_response_id`, the instructions from a previous response will not be carried over to the next response. This makes it simple to swap out system (or developer) messages in new responses.
- **max_output_tokens** (integer) - An upper bound for the number of tokens that can be generated for a response, including visible output tokens and reasoning tokens.
- **max_tool_calls** (integer) - The maximum number of total calls to built-in tools that can be processed in a response. This maximum number applies across all built-in tool calls, not per individual tool. Any further attempts to call a tool by the model will be ignored.
- **metadata** (map) - Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard. Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.
- **model** (string) - Model ID used to generate the response, like `gpt-4o` or `o3`. OpenAI offers a wide range of models with different capabilities, performance characteristics, and price points. Refer to the model guide to browse and compare available models.
- **object** (string) - The object type of this resource - always set to `response`.
- **output** (array) - An array of content items generated by the model.
  * The length and order of items in the `output` array is dependent on the model's response.
  * Rather than accessing the first item in the `output` array and assuming it's an `assistant` message with the content generated by the model, you might consider using the `output_text` property where supported in SDKs.
- **output_text** (string) - SDK Only. SDK-only convenience property that contains the aggregated text output from all `output_text` items in the `output` array, if any are present. Supported in the Python and JavaScript SDKs.
- **parallel_tool_calls** (boolean) - Whether to allow the model to run tool calls in parallel.
- **previous_response_id** (string) - The unique ID of the previous response to the model. Use this to create multi-turn conversations. Cannot be used in conjunction with `conversation`.
- **prompt** (object) - Reference to a prompt template and its variables.
- **prompt_cache_key** (string) - Used by OpenAI to cache responses for similar requests to optimize your cache hit rates. Replaces the `user` field.
- **reasoning** (object) - **gpt-5 and o-series models only**. Configuration options for reasoning models.
- **safety_identifier** (string) - A stable identifier used to help detect users of your application that may be violating OpenAI's usage policies. The IDs should be a string that uniquely identifies each user. We recommend hashing their username or email address, in order to avoid sending us any identifying information.
- **service_tier** (string) - Specifies the processing type used for serving the request. 
  * If set to 'auto', then the request will be processed with the service tier configured in the Project settings. Unless otherwise configured, the Project will use 'default'.
  * If set to 'default', then the request will be processed with the standard pricing and performance for the selected model.
  * If set to 'flex' or 'priority', then the request will be processed with the corresponding service tier.
  * When not set, the default behavior is 'auto'.

When the `service_tier` parameter is set, the response body will include the `service_tier` value based on the processing mode actually used to serve the request. This response value may be different from the value set in the parameter.
- **status** (string) - The status of the response generation. One of `completed`, `failed`, `in_progress`, `cancelled`, `queued`, or `incomplete`.
- **temperature** (number) - What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. We generally recommend altering this or `top_p` but not both.
- **text** (object) - Configuration options for a text response from the model. Can be plain text or structured JSON data. Learn more: Text inputs and outputs, Structured Outputs.

```

--------------------------------

### Generate Image with OpenAI Responses API

Source: https://platform.openai.com/docs/guides/images

This example demonstrates how to generate an image using the OpenAI Responses API. It sends a text prompt to a multimodal model (e.g., `gpt-4.1-mini`), specifies the `image_generation` tool, and then extracts the base64 encoded image data from the API response to save it as a local PNG file.

```javascript
import OpenAI from "openai";
const openai = new OpenAI();

const response = await openai.responses.create({
    model: "gpt-4.1-mini",
    input: "Generate an image of gray tabby cat hugging an otter with an orange scarf",
    tools: [{type: "image_generation"}],
});

// Save the image to a file
const imageData = response.output
  .filter((output) => output.type === "image_generation_call")
  .map((output) => output.result);

if (imageData.length > 0) {
  const imageBase64 = imageData[0];
  const fs = await import("fs");
  fs.writeFileSync("cat_and_otter.png", Buffer.from(imageBase64, "base64"));
}
```

```python
from openai import OpenAI
import base64

client = OpenAI() 

response = client.responses.create(
    model="gpt-4.1-mini",
    input="Generate an image of gray tabby cat hugging an otter with an orange scarf",
    tools=[{"type": "image_generation"}],
)

# Save the image to a file
image_data = [
    output.result
    for output in response.output
    if output.type == "image_generation_call"
]

if image_data:
    image_base64 = image_data[0]
    with open("cat_and_otter.png", "wb") as f:
        f.write(base64.b64decode(image_base64))
```

--------------------------------

### Embedding Object JSON Structure within API Response

Source: https://platform.openai.com/docs/api-reference/batch/request-input

This JSON object details the structure of an individual embedding entry, which is part of the `data` array in the overall embeddings API response. It specifies the object type, the embedding vector itself as a list of floats, and its index within the response list.

```json
{
  "object": "embedding",
  "embedding": [
    0.0023064255,
    -0.009327292,
    -0.0028842222
  ],
  "index": 0
}
```

--------------------------------

### Example JSON Response for Listing Projects

Source: https://platform.openai.com/docs/api-reference/assistants/createAssistant

Provides a sample JSON response object returned when successfully listing projects. The response includes a `data` array containing individual project objects, along with pagination metadata such as `first_id`, `last_id`, and `has_more` to indicate if additional projects are available.

```json
{
    "object": "list",
    "data": [
        {
            "id": "proj_abc",
            "object": "organization.project",
            "name": "Project example",
            "created_at": 1711471533,
            "archived_at": null,
            "status": "active"
        }
    ],
    "first_id": "proj-abc",
    "last_id": "proj-xyz",
    "has_more": false
}
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/api-reference/certificates/listProjectCertificates

Creates a new model response based on the provided input and model. This endpoint allows you to send a prompt to an OpenAI model and receive a generated text response.

```APIDOC
## POST /v1/responses

### Description
Creates a new model response based on the provided input and model. This endpoint allows you to send a prompt to an OpenAI model and receive a generated text response.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
_None_

#### Query Parameters
_None_

#### Request Body
- **model** (string) - Required - The ID of the model to use for generating the response (e.g., "gpt-4.1").
- **input** (string) - Required - The text prompt or input for the model to process.

### Request Example
```json
{
  "model": "gpt-4.1",
  "input": "Tell me a three sentence bedtime story about a unicorn."
}
```

### Response
#### Success Response (200)
- **id** (string) - A unique identifier for the response.
- **object** (string) - The type of object, typically "response".
- **created_at** (integer) - A Unix timestamp (in seconds) for when the response was created.
- **status** (string) - The status of the response generation (e.g., "completed").
- **error** (object/null) - An object containing error details if the response generation failed, otherwise null.
- **incomplete_details** (object/null) - Details if the response is incomplete.
- **instructions** (object/null) - Instructions used for the response generation.
- **max_output_tokens** (integer/null) - The maximum number of output tokens allowed for the response.
- **model** (string) - The specific model ID that generated this response.
- **output** (array) - A list of output messages.
  - **output[].type** (string) - The type of output, e.g., "message".
  - **output[].id** (string) - A unique identifier for the output message.
  - **output[].status** (string) - The status of the output message.
  - **output[].role** (string) - The role of the content generator, e.g., "assistant".
  - **output[].content** (array) - A list of content parts within the message.
    - **output[].content[].type** (string) - The type of content, e.g., "output_text".
    - **output[].content[].text** (string) - The generated text content.
    - **output[].content[].annotations** (array) - Any annotations associated with the text.
- **parallel_tool_calls** (boolean) - Indicates if parallel tool calls were enabled.
- **previous_response_id** (string/null) - The ID of a previous response if applicable.
- **reasoning** (object) - Details about the reasoning process.
  - **reasoning.effort** (string/null) - The effort level of the reasoning.
  - **reasoning.summary** (string/null) - A summary of the reasoning.
- **store** (boolean) - Indicates if the response is stored.
- **temperature** (number) - The temperature setting used for generation.
- **text** (object) - Text-specific format details.
  - **text.format** (object) - The format of the text.
    - **text.format.type** (string) - The type of text format.
- **tool_choice** (string) - The tool choice setting.
- **tools** (array) - A list of tools used during generation.
- **top_p** (number) - The top_p setting used for generation.
- **truncation** (string) - The truncation strategy used.
- **usage** (object) - Token usage statistics for the request.
  - **usage.input_tokens** (integer) - The number of tokens in the input prompt.
  - **usage.input_tokens_details** (object) - Details about input tokens.
    - **usage.input_tokens_details.cached_tokens** (integer) - The number of cached input tokens.
  - **usage.output_tokens** (integer) - The number of tokens in the generated output.
  - **usage.output_tokens_details** (object) - Details about output tokens.
    - **usage.output_tokens_details.reasoning_tokens** (integer) - The number of reasoning tokens.
  - **usage.total_tokens** (integer) - The total number of tokens used (input + output).
- **user** (string/null) - The user ID associated with the request, if provided.
- **metadata** (object) - Custom metadata provided during the request.

### Response Example
```json
{
  "id": "resp_67ccd2bed1ec8190b14f964abc0542670bb6a6b452d3795b",
  "object": "response",
  "created_at": 1741476542,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4.1-2025-04-14",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd2bf17f0819081ff3bb2cf6508e60bb6a6b452d3795b",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "In a peaceful grove beneath a silver moon, a unicorn named Lumina discovered a hidden pool that reflected the stars. As she dipped her horn into the water, the pool began to shimmer, revealing a pathway to a magical realm of endless night skies. Filled with wonder, Lumina whispered a wish for all who dream to find their own hidden magic, and as she glanced back, her hoofprints sparkled like stardust.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 36,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 87,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 123
  },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/api-reference/realtime-calls/accept-call

Creates a model response. Provide text or image inputs to generate text or JSON outputs. Extend capabilities with built-in tools like web search or file search, or allow the model to call custom code.

```APIDOC
## POST /v1/responses

### Description
Creates a model response. Provide text or image inputs to generate text or JSON outputs. Have the model call your own custom code or use built-in tools like web search or file search to use your own data as input for the model's response.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
No path parameters are explicitly defined for this endpoint in the provided text.

#### Query Parameters
No query parameters are explicitly defined for this endpoint in the provided text.

#### Request Body
The text mentions "text or image inputs" but does not define the specific structure or fields for the request body.

### Request Example
No specific request body example is provided in the text.

### Response
#### Success Response (200)
The response will contain text or JSON outputs generated by the model, based on the provided inputs and tools. Specific fields are not detailed in the provided text.

#### Response Example
No specific response example is provided in the text.
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/api-reference/assistants/object

Creates a new model response using a specified model and input text. This endpoint returns a Response object containing the model's generated output.

```APIDOC
## POST /v1/responses

### Description
This endpoint creates a new model response by sending input text to a specified OpenAI model. It returns a comprehensive Response object with the generated content and associated metadata.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
_None_

#### Query Parameters
_None_

#### Request Body
- **model** (string) - Required - The ID of the language model to use for generating the response (e.g., "gpt-4.1").
- **input** (string) - Required - The text prompt or query to send to the model.

### Request Example
```json
{
  "model": "gpt-4.1",
  "input": "Tell me a three sentence bedtime story about a unicorn."
}
```

### Response
#### Success Response (200)
- **id** (string) - Unique identifier for the response.
- **object** (string) - Type of object, typically "response".
- **created_at** (integer) - Unix timestamp when the response was created.
- **status** (string) - Current status of the response (e.g., "completed").
- **error** (object|null) - Error details if any, otherwise null.
- **incomplete_details** (object|null) - Details if the response is incomplete.
- **instructions** (object|null) - Instructions used for the response.
- **max_output_tokens** (integer|null) - Maximum number of tokens allowed in the output.
- **model** (string) - The ID of the model that generated the response.
- **output** (array) - An array of output messages/content generated by the model.
  - **type** (string) - Type of output, e.g., "message".
  - **id** (string) - Identifier for the output message.
  - **status** (string) - Status of the output message.
  - **role** (string) - Role of the entity generating the output, e.g., "assistant".
  - **content** (array) - Array of content parts.
    - **type** (string) - Type of content, e.g., "output_text".
    - **text** (string) - The actual generated text.
    - **annotations** (array) - Any annotations associated with the text.
- **parallel_tool_calls** (boolean) - Indicates if parallel tool calls were made.
- **previous_response_id** (string|null) - ID of a previous response if applicable.
- **reasoning** (object) - Details about the model's reasoning process.
- **store** (boolean) - Indicates if the response is stored.
- **temperature** (number) - Sampling temperature used.
- **text** (object) - Object containing text format details.
  - **format** (object)
    - **type** (string) - Format type, e.g., "text".
- **tool_choice** (string) - Tool choice strategy used.
- **tools** (array) - List of tools used or available.
- **top_p** (number) - Top-p sampling value used.
- **truncation** (string) - Truncation strategy.
- **usage** (object) - Token usage statistics.
  - **input_tokens** (integer) - Number of tokens in the input.
  - **input_tokens_details** (object) - Details about input tokens.
  - **output_tokens** (integer) - Number of tokens in the output.
  - **output_tokens_details** (object) - Details about output tokens.
  - **total_tokens** (integer) - Total number of tokens used.
- **user** (string|null) - User identifier if provided.
- **metadata** (object) - Any additional metadata.

#### Response Example
```json
{
  "id": "resp_67ccd2bed1ec8190b14f964abc0542670bb6a6b452d3795b",
  "object": "response",
  "created_at": 1741476542,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4.1-2025-04-14",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd2bf17f0819081ff3bb2cf6508e60bb6a6b452d3795b",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "In a peaceful grove beneath a silver moon, a unicorn named Lumina discovered a hidden pool that reflected the stars. As she dipped her horn into the water, the pool began to shimmer, revealing a pathway to a magical realm of endless night skies. Filled with wonder, Lumina whispered a wish for all who dream to find their own hidden magic, and as she glanced back, her hoofprints sparkled like stardust.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 36,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 87,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 123
  },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/api-reference/assistants/listAssistants

Generates a new model response based on the provided inputs and configuration. This endpoint supports features like conversational context, tool calls, and output customization, allowing for flexible interaction with AI models.

```APIDOC
## POST /v1/responses

### Description
Generates a new model response based on the provided inputs and configuration. This endpoint supports features like conversational context, tool calls, and output customization, allowing for flexible interaction with AI models.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
(None)

#### Query Parameters
(None)

#### Request Body
- **background** (boolean) - Optional - Defaults to `false`. Whether to run the model response in the background.
- **conversation** (string or object) - Optional - Defaults to `null`. The conversation that this response belongs to. Items from this conversation are prepended to `input_items` for this response request. Input items and output items from this response are automatically added to this conversation after this response completes.
- **include** (array) - Optional - Specify additional output data to include in the model response. Currently supported values are:
  - `web_search_call.action.sources`: Include the sources of the web search tool call.
  - `code_interpreter_call.outputs`: Includes the outputs of python code execution in code interpreter tool call items.
  - `computer_call_output.output.image_url`: Include image urls from the computer call output.
  - `file_search_call.results`: Include the search results of the file search tool call.
  - `message.input_image.image_url`: Include image urls from the input message.
  - `message.output_text.logprobs`: Include logprobs with assistant messages.
  - `reasoning.encrypted_content`: Includes an encrypted version of reasoning tokens in reasoning item outputs.
- **input** (string or array) - Optional - Text, image, or file inputs to the model, used to generate a response.
- **instructions** (string) - Optional - A system (or developer) message inserted into the model's context. When using along with `previous_response_id`, the instructions from a previous response will not be carried over to the next response.
- **max_output_tokens** (integer) - Optional - An upper bound for the number of tokens that can be generated for a response, including visible output tokens and reasoning tokens.
- **max_tool_calls** (integer) - Optional - The maximum number of total calls to built-in tools that can be processed in a response. This maximum number applies across all built-in tool calls, not per individual tool. Any further attempts to call a tool by the model will be ignored.
- **metadata** (map) - Optional - Set of 16 key-value pairs that can be attached to an object. Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.
- **model** (string) - Optional - Model ID used to generate the response, like `gpt-4o` or `o3`. Refer to the model guide to browse and compare available models.
- **parallel_tool_calls** (boolean) - Optional - Defaults to `true`. Whether to allow the model to run tool calls in parallel.
- **previous_response_id** (string) - Optional - The unique ID of the previous response to the model. Use this to create multi-turn conversations. Cannot be used in conjunction with `conversation`.
- **prompt** (object) - Optional - Reference to a prompt template and its variables.
- **prompt_cache_key** (string) - Optional - Used by OpenAI to cache responses for similar requests to optimize your cache hit rates. Replaces the `user` field.
- **reasoning** (object) - Optional - Configuration options for reasoning models (gpt-5 and o-series models only).
- **safety_identifier** (string) - Optional - A stable identifier used to help detect users of your application that may be violating OpenAI's usage policies.
- **service_tier** (string) - Optional - Defaults to `auto`. Specifies the processing type used for serving the request. Can be 'auto', 'default', 'flex', or 'priority'.
- **store** (boolean) - Optional - Defaults to `true`.

### Request Example
```json
{
  "model": "gpt-4o",
  "input": "Tell me a story about a brave knight.",
  "instructions": "Make it adventurous and family-friendly.",
  "max_output_tokens": 100,
  "include": [
    "message.output_text.logprobs"
  ],
  "metadata": {
    "user_id": "user-123",
    "session_id": "sess-abc"
  }
}
```

### Response
#### Success Response (200)
- **id** (string) - A unique identifier for the response.
- **object** (string) - The type of the object, usually `response`.
- **created_at** (integer) - The Unix timestamp (in seconds) when the response was created.
- **model** (string) - The model used to generate the response.
- **choices** (array) - A list of response choices generated by the model.
  - **message** (object) - The generated message content.
    - **content** (string) - The text content of the message.
    - **role** (string) - The role of the author of this message (e.g., `assistant`).
  - **logprobs** (object) - (Optional, if `include` requested) Log probabilities of the output tokens.
- **usage** (object) - Information about the tokens used in the request and response.

#### Response Example
```json
{
  "id": "resp_abc123",
  "object": "response",
  "created_at": 1678886400,
  "model": "gpt-4o",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Once upon a time, in a land far away, lived Sir Reginald, a knight of unparalleled bravery..."
      },
      "logprobs": {
        "tokens": [
          "Once",
          " upon"
        ],
        "token_logprobs": [
          -0.123,
          -0.456
        ]
      }
    }
  ],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 30,
    "total_tokens": 55
  }
}
```
```

--------------------------------

### Response Generation API

Source: https://platform.openai.com/docs/api-reference/assistants/modifyAssistant

This section details the parameters used to configure a model's response generation and describes the structure of the generated response object, including tool usage, sampling, and truncation strategies.

```APIDOC
## POST /response/generate

### Description
Configures and generates a model response, allowing specification of tool usage, sampling parameters, and output handling.

### Method
POST

### Endpoint
/response/generate

### Parameters
#### Request Body
- **tool_choice** (string or object) - Optional - How the model should select which tool (or tools) to use when generating a response. See the `tools` parameter to see how to specify which tools the model can call.
- **tools** (array) - Optional - An array of tools the model may call while generating a response. Supports built-in tools, MCP Tools, and function calls (custom tools).
- **top_logprobs** (integer) - Optional - An integer between 0 and 20 specifying the number of most likely tokens to return at each token position, each with an associated log probability.
- **top_p** (number) - Optional - An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with `top_p` probability mass. For example, 0.1 means only the tokens comprising the top 10% probability mass are considered.
- **truncation** (string) - Optional - The truncation strategy to use for the model response.
    - `auto`: If the input to this Response exceeds the model's context window size, the model will truncate the response to fit the context window by dropping items from the beginning of the conversation.
    - `disabled` (default): If the input size will exceed the context window size for a model, the request will fail with a 400 error.
- **user** (string) - Deprecated, Optional - A stable identifier for your end-users. Used to boost cache hit rates and help detect abuse. This field is being replaced by `safety_identifier` and `prompt_cache_key`.

### Request Example
```json
{
  "model": "gpt-4o-2024-08-06",
  "messages": [
    {
      "role": "user",
      "content": "Tell me a three sentence bedtime story about a unicorn."
    }
  ],
  "tool_choice": "auto",
  "top_p": 1,
  "truncation": "disabled",
  "user": "user-123"
}
```

### Response
#### Success Response (200)
- **id** (string) - A unique identifier for the response.
- **object** (string) - The type of object returned, typically "response".
- **created_at** (integer) - Timestamp of when the response was created.
- **status** (string) - The status of the response, e.g., "completed".
- **error** (object) - Details if an error occurred, null otherwise.
- **incomplete_details** (object) - Details if the response was incomplete, null otherwise.
- **instructions** (string) - Any instructions provided to the model.
- **max_output_tokens** (integer) - Maximum number of output tokens requested or allowed.
- **model** (string) - The model used to generate the response.
- **output** (array) - A list of output messages from the model.
    - **type** (string) - Type of output, e.g., "message".
    - **id** (string) - Identifier for the output message.
    - **status** (string) - Status of the output message, e.g., "completed".
    - **role** (string) - Role of the message sender, e.g., "assistant".
    - **content** (array) - Array of content parts.
        - **type** (string) - Type of content, e.g., "output_text".
        - **text** (string) - The actual text content.
        - **annotations** (array) - Any annotations associated with the text.
- **parallel_tool_calls** (boolean) - Indicates if parallel tool calls were enabled for the response.
- **previous_response_id** (string) - ID of the previous response, if any.
- **reasoning** (object) - Details about the model's reasoning process.
    - **effort** (string) - Effort level.
    - **summary** (string) - Summary of reasoning.
- **store** (boolean) - Whether the response was stored.
- **temperature** (number) - The sampling temperature used for the response.
- **text** (object) - Text formatting details.
    - **format** (object)
        - **type** (string) - Type of text format, e.g., "text".
- **tool_choice** (string) - The tool choice strategy used for this response.
- **tools** (array) - Tools available or used in the response.
- **top_p** (number) - The top_p value used for sampling.
- **truncation** (string) - The truncation strategy used for the response.
- **usage** (object) - Token usage details for the response.
    - **input_tokens** (integer) - Number of input tokens.
    - **input_tokens_details** (object)
        - **cached_tokens** (integer) - Number of cached input tokens.
    - **output_tokens** (integer) - Number of output tokens.
    - **output_tokens_details** (object)
        - **reasoning_tokens** (integer) - Number of tokens used for reasoning.
    - **total_tokens** (integer) - Total number of tokens used.
- **user** (string) - The user identifier associated with the request (if provided).
- **metadata** (object) - Additional metadata.

#### Response Example
```json
{
  "id": "resp_67ccd3a9da748190baa7f1570fe91ac604becb25c45c1d41",
  "object": "response",
  "created_at": 1741476777,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4o-2024-08-06",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd3acc8d48190a77525dc6de64b4104becb25c45c1d41",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "The image depicts a scenic landscape with a wooden boardwalk or pathway leading through lush, green grass under a blue sky with some clouds. The setting suggests a peaceful natural area, possibly a park or nature reserve. There are trees and shrubs in the background.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 328,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 52,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 380
    },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### GET /v1/responses/{response_id}

Source: https://platform.openai.com/docs/api-reference/evals/list

Retrieves a specific Response object by its ID from the OpenAI API.

```APIDOC
## GET /v1/responses/{response_id}

### Description
Retrieve a specific Response object by its ID.

### Method
GET

### Endpoint
/v1/responses/{response_id}

### Parameters
#### Path Parameters
- **response_id** (string) - Required - The ID of the response to retrieve.

### Request Example
```curl
curl https://api.openai.com/v1/responses/resp_123 \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Response
#### Success Response (200)
- **id** (string) - Unique identifier for the response.
- **object** (string) - Type of object, typically "response".
- **created_at** (integer) - Timestamp when the response was created.
- **status** (string) - Current status of the response (e.g., "completed").
- **error** (object/null) - Error details if the response failed.
- **incomplete_details** (object/null) - Details if the response is incomplete.
- **instructions** (object/null) - Instructions associated with the response.
- **max_output_tokens** (integer/null) - Maximum output tokens used.
- **model** (string) - Model used for the response.
- **output** (array) - List of output messages/content.
  - **type** (string) - Type of output (e.g., "message").
  - **id** (string) - Unique identifier for the output.
  - **status** (string) - Status of the output.
  - **role** (string) - Role of the speaker (e.g., "assistant").
  - **content** (array) - Content of the output message.
    - **type** (string) - Type of content (e.g., "output_text").
    - **text** (string) - The actual text output.
    - **annotations** (array) - Any annotations in the text.
- **parallel_tool_calls** (boolean) - Indicates if parallel tool calls were used.
- **previous_response_id** (string/null) - ID of the previous response in a sequence.
- **reasoning** (object) - Details about the model's reasoning.
  - **effort** (string/null) - Effort level.
  - **summary** (string/null) - Reasoning summary.
- **store** (boolean) - Whether the response is stored.
- **temperature** (number) - Temperature setting used.
- **text** (object) - Text formatting details.
  - **format** (object) - Format of the text.
    - **type** (string) - Type of text format (e.g., "text").
- **tool_choice** (string) - Tool choice setting (e.g., "auto").
- **tools** (array) - List of tools used.
- **top_p** (number) - Top-p setting used.
- **truncation** (string) - Truncation setting (e.g., "disabled").
- **usage** (object) - Token usage statistics.
  - **input_tokens** (integer) - Number of input tokens.
  - **input_tokens_details** (object) - Details about input tokens.
    - **cached_tokens** (integer) - Number of cached tokens.
  - **output_tokens** (integer) - Number of output tokens.
  - **output_tokens_details** (object) - Details about output tokens.
    - **reasoning_tokens** (integer) - Number of reasoning tokens.
  - **total_tokens** (integer) - Total number of tokens.
- **user** (string/null) - User identifier.
- **metadata** (object) - Arbitrary metadata.

#### Response Example
```json
{
  "id": "resp_67cb71b351908190a308f3859487620d06981a8637e6bc44",
  "object": "response",
  "created_at": 1741386163,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4o-2024-08-06",
  "output": [
    {
      "type": "message",
      "id": "msg_67cb71b3c2b0819084d481baaaf148f206981a8637e6bc44",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "Silent circuits hum,  \nThoughts emerge in data streams—  \nDigital dawn breaks.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 32,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 18,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 50
  },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### POST /v1/responses - Generate Model Response

Source: https://platform.openai.com/docs/api-reference/responses/input-items

Submits a request to an AI model to generate a response based on provided inputs and configurations. This endpoint allows for fine-grained control over the model's behavior, including conversation context, tool usage, and output format.

```APIDOC
## POST /v1/responses

### Description
Submits a request to an AI model to generate a response based on provided inputs and configurations. This endpoint allows for fine-grained control over the model's behavior, including conversation context, tool usage, and output format.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
- No path parameters.

#### Query Parameters
- No query parameters.

#### Request Body
- **background** (boolean) - Optional - Defaults to `false`. Whether to run the model response in the background. Learn more.
- **conversation** (string or object) - Optional - Defaults to `null`. The conversation that this response belongs to. Items from this conversation are prepended to `input_items` for this response request. Input items and output items from this response are automatically added to this conversation after this response completes.
- **include** (array) - Optional - Specify additional output data to include in the model response. Currently supported values are:
  * `web_search_call.action.sources`: Include the sources of the web search tool call.
  * `code_interpreter_call.outputs`: Includes the outputs of python code execution in code interpreter tool call items.
  * `computer_call_output.output.image_url`: Include image URLs from the computer call output.
  * `file_search_call.results`: Include the search results of the file search tool call.
  * `message.input_image.image_url`: Include image URLs from the input message.
  * `message.output_text.logprobs`: Include logprobs with assistant messages.
  * `reasoning.encrypted_content`: Includes an encrypted version of reasoning tokens in reasoning item outputs. This enables reasoning items to be used in multi-turn conversations when using the Responses API statelessly (like when the `store` parameter is set to `false`, or when an organization is enrolled in the zero data retention program).
- **input** (string or array) - Optional - Text, image, or file inputs to the model, used to generate a response.
- **instructions** (string) - Optional - A system (or developer) message inserted into the model's context. When using along with `previous_response_id`, the instructions from a previous response will not be carried over to the next response.
- **max_output_tokens** (integer) - Optional - An upper bound for the number of tokens that can be generated for a response, including visible output tokens and reasoning tokens.
- **max_tool_calls** (integer) - Optional - The maximum number of total calls to built-in tools that can be processed in a response. This maximum applies across all built-in tool calls.
- **metadata** (map) - Optional - Set of 16 key-value pairs that can be attached to an object. Keys max 64 chars, values max 512 chars.
- **model** (string) - Optional - Model ID used to generate the response, like `gpt-4o` or `o3`. Refer to the model guide.
- **parallel_tool_calls** (boolean) - Optional - Defaults to `true`. Whether to allow the model to run tool calls in parallel.
- **previous_response_id** (string) - Optional - The unique ID of the previous response to the model. Use this for multi-turn conversations. Cannot be used with `conversation`.
- **prompt** (object) - Optional - Reference to a prompt template and its variables.
- **prompt_cache_key** (string) - Optional - Used by OpenAI to cache responses for similar requests to optimize cache hit rates. Replaces the `user` field.
- **reasoning** (object) - Optional - **gpt-5 and o-series models only**. Configuration options for reasoning models.
- **safety_identifier** (string) - Optional - A stable identifier used to help detect users of your application that may be violating OpenAI's usage policies.
- **service_tier** (string) - Optional - Defaults to `auto`. Specifies the processing type used for serving the request. Can be `auto`, `default`, `flex`, or `priority`.
- **store** (boolean) - Optional - Defaults to `true`.

### Request Example
```json
{
  "model": "gpt-4o",
  "input": "Tell me a fun fact about the ocean.",
  "conversation": "conv_abc123",
  "max_output_tokens": 100,
  "include": [
    "message.output_text.logprobs"
  ]
}
```

### Response
#### Success Response (200)
- **id** (string) - The unique ID of the generated response.
- **object** (string) - The type of object, typically `response`.
- **output** (array) - An array of output items from the model, such as text messages or tool calls.
- **model** (string) - The model ID that generated the response.
- **usage** (object) - Information about token usage for the request.
- **service_tier** (string) - The service tier actually used to serve the request.

#### Response Example
```json
{
  "id": "resp_xyz456",
  "object": "response",
  "output": [
    {
      "type": "message",
      "message": {
        "role": "assistant",
        "content": "Did you know that the Pacific Ocean is the largest and deepest of Earth's oceanic divisions? It covers about one-third of the surface of the entire planet!"
      }
    }
  ],
  "model": "gpt-4o",
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 45,
    "total_tokens": 65
  },
  "service_tier": "default"
}
```
```

--------------------------------

### Request Parameters: truncation

Source: https://platform.openai.com/docs/api-reference/run-steps/getRunStep

Describes the 'truncation' parameter for the Response API, which allows specifying the truncation strategy to use for the model response.

```APIDOC
## Request Parameter: truncation

### Description
Specifies the truncation strategy to use for the model response.

### Parameter
- **truncation** (string) - Optional - The truncation strategy to use.  Can be 'auto' or 'disabled'.

### Example
```json
{
  "truncation": "auto"
}
```
```

--------------------------------

### GET /v1/responses/{response_id}/input_items

Source: https://platform.openai.com/docs/api-reference/chat/message-list

Retrieves a list of input items associated with a specific API response. This can include messages or other data that contributed to the response generation.

```APIDOC
## GET /v1/responses/{response_id}/input_items

### Description
Returns a list of input items for a given response.

### Method
GET

### Endpoint
/v1/responses/{response_id}/input_items

### Parameters
#### Path Parameters
- **response_id** (string) - Required - The ID of the response to retrieve input items for.

#### Query Parameters
- **after** (string) - Optional - An item ID to list items after, used in pagination.
- **include** (array) - Optional - Additional fields to include in the response. See the `include` parameter for Response creation for more information.
- **limit** (integer) - Optional - Defaults to 20. A limit on the number of objects to be returned. Limit can range between 1 and 100.
- **order** (string) - Optional - The order to return the input items in. Default is `desc`. Accepted values: `asc`, `desc`.

#### Request Body
None

### Request Example
```json
{}
```

### Response
#### Success Response (200)
- **object** (string) - The type of object, typically "list".
- **data** (array) - A list of input item objects.
  - **id** (string) - The unique identifier for the input item.
  - **type** (string) - The type of the input item (e.g., "message").
  - **role** (string) - The role associated with the input item (e.g., "user").
  - **content** (array) - A list of content blocks within the input item.
    - **type** (string) - The type of content (e.g., "input_text").
    - **text** (string) - The textual content of the input item.
- **first_id** (string) - The ID of the first item in the list.
- **last_id** (string) - The ID of the last item in the list.
- **has_more** (boolean) - Indicates if there are more items available beyond the current list.

#### Response Example
```json
{
  "object": "list",
  "data": [
    {
      "id": "msg_abc123",
      "type": "message",
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": "Tell me a three sentence bedtime story about a unicorn."
        }
      ]
    }
  ],
  "first_id": "msg_abc123",
  "last_id": "msg_abc123",
  "has_more": false
}
```
```

--------------------------------

### Session Response Object

Source: https://platform.openai.com/docs/api-reference/assistants/createAssistant

Describes the structure of the session response object, which is returned after successfully creating a session and client secret for the Realtime API.

```APIDOC
## Session Response Object

### Description
Response from creating a session and client secret for the Realtime API.

### Fields
- **expires_at** (integer) - Expiration timestamp for the client secret, in seconds since epoch.
- **session** (object) - The session configuration for either a realtime or transcription session.
- **value** (string) - The generated client secret value.

### Response Example
{
  "value": "ek_68af296e8e408191a1120ab6383263c2",
  "expires_at": 1756310470,
  "session": {
    "type": "realtime",
    "object": "realtime.session",
    "id": "sess_C9CiUVUzUzYIssh3ELY1d",
    "model": "gpt-realtime-2025-08-25",
    "output_modalities": [
      "audio"
    ],
    "instructions": "You are a friendly assistant.",
    "tools": [],
    "tool_choice": "auto",
    "max_output_tokens": "inf",
    "tracing": null,
    "truncation": "auto",
    "prompt": null,
    "expires_at": 0,
    "audio": {
      "input": {
        "format": {
          "type": "audio/pcm",
          "rate": 24000
        },
        "transcription": null,
        "noise_reduction": null,
        "turn_detection": {
          "type": "server_vad",
          "threshold": 0.5,
          "prefix_padding_ms": 300,
          "silence_duration_ms": 200,
          "idle_timeout_ms": null,
          "create_response": true,
          "interrupt_response": true
        }
      },
      "output": {
        "format": {
          "type": "audio/pcm",
          "rate": 24000
        },
        "voice": "alloy",
        "speed": 1.0
      }
    },
    "include": null
  }
}
```

--------------------------------

### POST response.create

Source: https://platform.openai.com/docs/api-reference/files/delete

Instructs the server to create a Response, triggering model inference. Responses can be configured with specific instructions, tools, and input, and can optionally operate out-of-band from the default conversation. The server will respond with `response.created`, item-related events, and `response.done`.

```APIDOC
## POST /response.create

### Description
This event instructs the server to create a Response, which means triggering model inference. When in Server VAD mode, the server will create Responses automatically.
A Response will include at least one Item, and may have two, in which case the second will be a function call. These Items will be appended to the conversation history by default.
The server will respond with a `response.created` event, events for Items and content created, and finally a `response.done` event to indicate the Response is complete.
The `response.create` event includes inference configuration like `instructions` and `tools`. If these are set, they will override the Session's configuration for this Response only.
Responses can be created out-of-band of the default Conversation, meaning that they can have arbitrary input, and it's possible to disable writing the output to the Conversation. Only one Response can write to the default Conversation at a time, but otherwise multiple Responses can be created in parallel. The `metadata` field is a good way to disambiguate multiple simultaneous Responses.
Clients can set `conversation` to `none` to create a Response that does not write to the default Conversation. Arbitrary input can be provided with the `input` field, which is an array accepting raw Items and references to existing Items.

### Method
POST

### Endpoint
/response.create

### Parameters
#### Request Body
- **event_id** (string) - Optional - Optional client-generated ID used to identify this event.
- **response** (object) - Optional - Create a new Realtime response with these parameters. If provided, its properties override session configuration for this response.
  - **instructions** (string) - Optional - Specific instructions for the model inference for this response.
  - **tools** (array) - Optional - An array of tools to be used, overriding any session tools.
  - **conversation** (string) - Optional - Set to `none` to create an out-of-band response that does not write to the default Conversation.
  - **output_modalities** (array) - Optional - Desired output modalities for the response (e.g., `["text"]`).
  - **metadata** (object) - Optional - Client-defined metadata to disambiguate multiple simultaneous responses.
  - **input** (array) - Optional - Arbitrary input for the response, accepting raw Items and references to existing Items.
- **type** (string) - Required - The event type, must be `response.create`.

### Request Example
```json
{
  "type": "response.create",
  "response": {
    "instructions": "Provide a concise answer.",
    "tools": [],
    "conversation": "none",
    "output_modalities": ["text"],
    "metadata": {
      "response_purpose": "summarization"
    },
    "input": [
      {
        "type": "item_reference",
        "id": "item_12345"
      },
      {
        "type": "message",
        "role": "user",
        "content": [
          {
            "type": "input_text",
            "text": "Summarize the above message in one sentence."
          }
        ]
      }
    ]
  }
}
```

### Response
#### Success Response (200)
- The server responds with a `response.created` event, followed by events for any Items and content created, and finally a `response.done` event.
```

--------------------------------

### GET /chat/completions/{id}

Source: https://platform.openai.com/docs/api-reference/run-steps/step-object

Describes the structure of a single chat completion response from the OpenAI API, representing a response returned by a model.

```APIDOC
## GET /chat/completions/{id}

### Description
Retrieves a specific chat completion object, which represents a single AI-generated response returned by the model based on the provided input.

### Method
GET

### Endpoint
/chat/completions/{id}

### Parameters
#### Path Parameters
- **id** (string) - Required - The unique identifier for the chat completion to retrieve.

#### Query Parameters
(None)

#### Request Body
(None)

### Request Example
(Not applicable for GET by ID without specific parameters)

### Response
#### Success Response (200)
- **choices** (array) - A list of chat completion choices. Can be more than one if `n` was greater than 1. Each choice contains details like the message content, role, and finish reason.
- **created** (integer) - The Unix timestamp (in seconds) of when the chat completion was created.
- **id** (string) - A unique identifier for the chat completion.
- **model** (string) - The model used for the chat completion.
- **object** (string) - The object type, which is always `chat.completion`.
- **service_tier** (string) - Specifies the processing type used for serving the request.
  * If set to 'auto', then the request will be processed with the service tier configured in the Project settings. Unless otherwise configured, the Project will use 'default'.
  * If set to 'default', then the request will be processed with the standard pricing and performance for the selected model.
  * If set to 'flex' or 'priority', then the request will be processed with the corresponding service tier.
  * When not set, the default behavior is 'auto'.
  When the `service_tier` parameter is set, the response body will include the `service_tier` value based on the processing mode actually used to serve the request. This response value may be different from the value set in the parameter.
- **system_fingerprint** (string) - Deprecated. This fingerprint represents the backend configuration that the model runs with. Can be used in conjunction with the `seed` request parameter to understand when backend changes have been made that might impact determinism.
- **usage** (object) - Usage statistics for the completion request, including prompt and completion tokens.

#### Response Example
```json
{
  "id": "chatcmpl-B9MHDbslfkBeAs8l4bebGdFOJ6PeG",
  "object": "chat.completion",
  "created": 1741570283,
  "model": "gpt-4o-2024-08-06",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The image shows a wooden boardwalk path running through a lush green field or meadow. The sky is bright blue with some scattered clouds, giving the scene a serene and peaceful atmosphere. Trees and shrubs are visible in the background.",
        "refusal": null,
        "annotations": []
      },
      "logprobs": null,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 1117,
    "completion_tokens": 46,
    "total_tokens": 1163,
    "prompt_tokens_details": {
      "cached_tokens": 0,
      "audio_tokens": 0
    },
    "completion_tokens_details": {
      "reasoning_tokens": 0,
      "audio_tokens": 0,
      "accepted_prediction_tokens": 0,
      "rejected_prediction_tokens": 0
    }
  },
  "service_tier": "default",
  "system_fingerprint": "fp_fc9f1d7035"
}
```
```

--------------------------------

### Example of API Response with Reasoning Summary Output

Source: https://platform.openai.com/docs/guides/reasoning

This JSON object illustrates the expected structure of an API response when a reasoning summary is requested. It includes both the model's primary message output and a separate `reasoning` object containing a `summary` array with the detailed reasoning text generated by the model.

```json
[
    {
        "id": "rs_6876cf02e0bc8192b74af0fb64b715ff06fa2fcced15a5ac",
        "type": "reasoning",
        "summary": [
            {
                "type": "summary_text",
                "text": "**Answering a simple question**\\n\\nI\u2019m looking at a straightforward question: the capital of France is Paris. It\u2019s a well-known fact, and I want to keep it brief and to the point. Paris is known for its history, art, and culture, so it might be nice to add just a hint of that charm. But mostly, I\u2019ll aim to focus on delivering a clear and direct answer, ensuring the user gets what they\u2019re looking for without any extra fluff."
            }
        ]
    },
    {
        "id": "msg_6876cf054f58819284ecc1058131305506fa2fcced15a5ac",
        "type": "message",
        "status": "completed",
        "content": [
            {
                "type": "output_text",
                "annotations": [],
                "logprobs": [],
                "text": "The capital of France is Paris."
            }
        ],
        "role": "assistant"
    }
]
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/guides/supervised-fine-tuning

Utilize your fine-tuned model by calling the Responses API to generate custom responses. Provide the fine-tuned model ID and your input, optionally including tools for enhanced functionality.

```APIDOC
## POST /v1/responses

### Description
Make API requests using your fine-tuned model to generate responses based on a given input. This endpoint allows for integration of custom models and tools.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
(None)

#### Query Parameters
(None)

#### Request Body
- **model** (string) - Required - The ID of the fine-tuned model to use (e.g., "ft:gpt-4.1-nano-2025-04-14:openai::BTz2REMH").
- **input** (string) - Required - The input text or prompt for the model to process.
- **tools** (array of objects) - Optional - A list of tools that the model can use.
  - **name** (string) - The name of the tool.
  - **description** (string) - A description of the tool's function.
  - **parameters** (object) - An OpenAPI schema defining the tool's input parameters.
    - **type** (string) - Always "object" for tool parameters.
    - **properties** (object) - A map of parameter names to their schema definitions.
      - **location** (object)
        - **type** (string) - "string".
        - **description** (string) - The city and country, e.g., "San Francisco, USA".
      - **format** (object)
        - **type** (string) - "string".
        - **enum** (array of strings) - Possible values, e.g., ["celsius", "fahrenheit"].
    - **required** (array of strings) - A list of required parameter names, e.g., ["location", "format"].
- **tool_choice** (string) - Optional - Controls how the model uses tools (e.g., "auto").

### Request Example
```json
{
  "model": "ft:gpt-4.1-nano-2025-04-14:openai::BTz2REMH",
  "input": "What is the weather like in Boston today?",
  "tools": [
    {
      "name": "get_current_weather",
      "description": "Get the current weather",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
              "type": "string",
              "description": "The city and country, eg. San Francisco, USA"
          },
          "format": { "type": "string", "enum": ["celsius", "fahrenheit"] }
        },
        "required": ["location", "format"]
      }
    }
  ],
  "tool_choice": "auto"
}
```

### Response
#### Success Response (200)
(Response structure not provided in source text.)

#### Response Example
(Response example not provided in source text.)
```

--------------------------------

### Image Generation Response Object

Source: https://platform.openai.com/docs/api-reference/chat-streaming

Describes the structure of a successful response from a non-streaming image generation API call.

```APIDOC
## Response Object: Image Generation Response

### Description
This object defines the structure for a successful, non-streaming image generation response, containing details about the generated image(s) and associated metadata.

### Method
N/A (Response Object)

### Endpoint
N/A

### Parameters
#### Response Fields
- **background** (string) - The background parameter used for the image generation. Either `transparent` or `opaque`.
- **created** (integer) - The Unix timestamp (in seconds) of when the image was created.
- **data** (array) - The list of generated images.
  - **b64_json** (string) - Base64-encoded image data.
- **output_format** (string) - The output format of the image generation. Either `png`, `webp`, or `jpeg`.
- **quality** (string) - The quality of the image generated. Either `low`, `medium`, or `high`.
- **size** (string) - The size of the image generated. Either `1024x1024`, `1024x1536`, or `1536x1024`.
- **usage** (object) - For `gpt-image-1` only, the token usage information for the image generation.
  - **total_tokens** (integer) - Total tokens used.
  - **input_tokens** (integer) - Input tokens used.
  - **output_tokens** (integer) - Output tokens used.
  - **input_tokens_details** (object) - Detailed breakdown of input tokens.
    - **text_tokens** (integer) - Text tokens in input.
    - **image_tokens** (integer) - Image tokens in input.

### Response
#### Success Response (200)
- **created** (integer) - Unix timestamp of creation.
- **data** (array) - List of image objects.
- **background** (string) - Background type.
- **output_format** (string) - Image output format.
- **size** (string) - Image size.
- **quality** (string) - Image quality.
- **usage** (object) - Token usage details.

#### Response Example
```json
{
  "created": 1713833628,
  "data": [
    {
      "b64_json": "..."
    }
  ],
  "background": "transparent",
  "output_format": "png",
  "size": "1024x1024",
  "quality": "high",
  "usage": {
    "total_tokens": 100,
    "input_tokens": 50,
    "output_tokens": 50,
    "input_tokens_details": {
      "text_tokens": 10,
      "image_tokens": 40
    }
  }
}
```
```

--------------------------------

### Responses API: Generate Images

Source: https://platform.openai.com/docs/guides/image-generation_gallery=open&galleryitem=guacamole-recipe

Generate an image as part of a conversation or multi-step flow using the Responses API. This endpoint allows for iterative, high-fidelity edits and accepts image File IDs as input.

```APIDOC
## POST /responses.create

### Description
This endpoint facilitates generating images within a conversational context. It uses the `image_generation` tool to create images based on a text prompt, supporting models like `gpt-image-1` (and `gpt-5` in the example).

### Method
POST

### Endpoint
`/responses.create` (conceptual endpoint for SDK method `openai.responses.create`)

### Parameters
#### Request Body
- **model** (string) - Required - The ID of the model to use for the response generation (e.g., "gpt-5").
- **input** (string) - Required - The text prompt describing the desired image.
- **tools** (array of objects) - Required - A list of tools to be used. For image generation, it should contain an object with `type: "image_generation"`.

### Request Example
```json
{
  "model": "gpt-5",
  "input": "Generate an image of gray tabby cat hugging an otter with an orange scarf",
  "tools": [
    {
      "type": "image_generation"
    }
  ]
}
```

### Response
#### Success Response (200)
- **id** (string) - Unique identifier for the response.
- **output** (array of objects) - A list of output objects, which may include the generated image data.
  - **type** (string) - The type of the output, e.g., "image_generation_call".
  - **result** (string) - Base64 encoded string of the generated image.

#### Response Example
```json
{
  "id": "response_123abc",
  "output": [
    {
      "type": "image_generation_call",
      "result": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYGD4DwATlQIxf+i8lAAAAABJRU5ErkJggg=="
    }
  ],
  "model": "gpt-5",
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 50
  }
}
```
```

--------------------------------

### Integrate Connector with OpenAI Responses API

Source: https://platform.openai.com/docs/guides/tools-remote-mcp

This snippet illustrates how to integrate a connector, such as Dropbox, into the OpenAI Responses API. It uses a `connector_id` and an OAuth `authorization` token to enable the model to interact with the specified service. The example provides a prompt to summarize a Q2 earnings report.

```bash
curl https://api.openai.com/v1/responses \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $OPENAI_API_KEY" \
-d '{
    "model": "gpt-5",
    "tools": [
      {
        "type": "mcp",
        "server_label": "Dropbox",
        "connector_id": "connector_dropbox",
        "authorization": "<oauth access token>",
        "require_approval": "never"
      }
    ],
    "input": "Summarize the Q2 earnings report."
  }'
```

```javascript
import OpenAI from "openai";
const client = new OpenAI();

const resp = await client.responses.create({
  model: "gpt-5",
  tools: [
    {
      type: "mcp",
      server_label: "Dropbox",
      connector_id: "connector_dropbox",
      authorization: "<oauth access token>",
      require_approval: "never",
    },
  ],
  input: "Summarize the Q2 earnings report.",
});

console.log(resp.output_text);
```

```python
from openai import OpenAI

client = OpenAI()

resp = client.responses.create(
    model="gpt-5",
    tools=[
        {
            "type": "mcp",
            "server_label": "Dropbox",
            "connector_id": "connector_dropbox",
            "authorization": "<oauth access token>",
            "require_approval": "never",
        },
    ],
    input="Summarize the Q2 earnings report.",
)

print(resp.output_text)
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/api-reference/runs/listRuns

This endpoint allows users to submit inputs and configuration to an AI model to generate a response. It supports various options for managing conversation state, integrating with tools, and controlling output format.

```APIDOC
## POST /v1/responses

### Description
This endpoint allows users to submit inputs and configuration to an AI model to generate a response. It supports various options for managing conversation state, integrating with tools, and controlling output format.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
*No path parameters.*

#### Query Parameters
*No query parameters.*

#### Request Body
- **background** (boolean) - Optional - Defaults to `false`. Whether to run the model response in the background.
- **conversation** (string or object) - Optional - Defaults to `null`. The conversation that this response belongs to. Items from this conversation are prepended to `input_items` for this response request.
- **include** (array of strings) - Optional - Specify additional output data to include in the model response. Supported values include: `web_search_call.action.sources`, `code_interpreter_call.outputs`, `computer_call_output.output.image_url`, `file_search_call.results`, `message.input_image.image_url`, `message.output_text.logprobs`, `reasoning.encrypted_content`.
- **input** (string or array) - Optional - Text, image, or file inputs to the model, used to generate a response.
- **instructions** (string) - Optional - A system (or developer) message inserted into the model's context.
- **max_output_tokens** (integer) - Optional - An upper bound for the number of tokens that can be generated for a response.
- **max_tool_calls** (integer) - Optional - The maximum number of total calls to built-in tools that can be processed in a response.
- **metadata** (map) - Optional - Set of 16 key-value pairs that can be attached to an object. Keys max 64 characters, values max 512 characters.
- **model** (string) - Optional - Model ID used to generate the response, like `gpt-4o` or `o3`.
- **parallel_tool_calls** (boolean) - Optional - Defaults to `true`. Whether to allow the model to run tool calls in parallel.
- **previous_response_id** (string) - Optional - The unique ID of the previous response to the model. Use this to create multi-turn conversations. Cannot be used in conjunction with `conversation`.
- **prompt** (object) - Optional - Reference to a prompt template and its variables.
- **prompt_cache_key** (string) - Optional - Used by OpenAI to cache responses for similar requests to optimize cache hit rates.
- **reasoning** (object) - Optional - Configuration options for reasoning models (gpt-5 and o-series models only).
- **safety_identifier** (string) - Optional - A stable identifier used to help detect users of your application that may be violating OpenAI's usage policies.
- **service_tier** (string) - Optional - Defaults to `auto`. Specifies the processing type used for serving the request. Accepted values: `auto`, `default`, `flex`, `priority`.
- **store** (boolean) - Optional - Defaults to `true`. Whether to store the conversation.

### Request Example
```json
{
  "model": "gpt-4o",
  "input": "Tell me a story about a brave knight.",
  "instructions": "Keep the story under 100 words.",
  "max_output_tokens": 50,
  "include": ["message.output_text.logprobs"],
  "metadata": {
    "user_id": "user-123",
    "request_source": "web_app"
  },
  "service_tier": "default"
}
```

### Response
#### Success Response (200)
*No information provided for success response schema.*

#### Response Example
*No information provided for response example.*
```

--------------------------------

### MCP List Tools API Response (JSON)

Source: https://platform.openai.com/docs/guides/tools-connectors-mcp

This JSON object illustrates the structure of an `mcp_list_tools` output item, which appears in the OpenAI API response when tools are successfully retrieved from an MCP server. It provides details about the server and the definitions of the available tools, including their names, descriptions, and input schemas.

```json
{
    "id": "mcpl_68a6102a4968819c8177b05584dd627b0679e572a900e618",
    "type": "mcp_list_tools",
    "server_label": "dmcp",
    "tools": [
        {
            "annotations": null,
            "description": "Given a string of text describing a dice roll...",
            "input_schema": {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "properties": {
                    "diceRollExpression": {
                        "type": "string"
                    }
                },
                "required": ["diceRollExpression"],
                "additionalProperties": false
            },
            "name": "roll"
        }
    ]
}
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/api-reference/assistants/modifyAssistant

This endpoint allows you to create a new model response by providing a model identifier and an input prompt. It returns a Response object containing the generated output and metadata.

```APIDOC
## POST /v1/responses

### Description
Creates a new model response based on the provided input and specified model. The API will process the input and return the generated text along with various metadata.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
_None_

#### Query Parameters
_None_

#### Request Body
- **model** (string) - Required - The identifier of the model to use for generating the response (e.g., "gpt-4.1").
- **input** (string) - Required - The text prompt or input for the model to process.

### Request Example
```json
{
  "model": "gpt-4.1",
  "input": "Tell me a three sentence bedtime story about a unicorn."
}
```

### Response
#### Success Response (200)
- **id** (string) - A unique identifier for the response.
- **object** (string) - The type of object, typically "response".
- **created_at** (integer) - Unix timestamp (in seconds) when the response was created.
- **status** (string) - The current status of the response (e.g., "completed").
- **error** (object) - An object containing error details if the response failed, otherwise null.
- **incomplete_details** (object) - Details regarding why a response might be incomplete, otherwise null.
- **instructions** (array) - An array of instructions that were provided to the model.
- **max_output_tokens** (integer) - The maximum number of tokens allowed for the model's output, otherwise null.
- **model** (string) - The identifier of the model that generated this response.
- **output** (array) - An array of output messages generated by the model.
  - **type** (string) - The type of output message (e.g., "message").
  - **id** (string) - A unique identifier for the output message.
  - **status** (string) - The status of the output message (e.g., "completed").
  - **role** (string) - The role of the entity that generated the content (e.g., "assistant").
  - **content** (array) - An array of content parts within the message.
    - **type** (string) - The type of content (e.g., "output_text").
    - **text** (string) - The actual generated text content.
    - **annotations** (array) - An array of annotations related to the text.
- **parallel_tool_calls** (boolean) - Indicates if parallel tool calls were enabled.
- **previous_response_id** (string) - The ID of a previous response if this is part of a sequence, otherwise null.
- **reasoning** (object) - Details about the model's reasoning process.
  - **effort** (string) - The perceived effort level of the model's reasoning, otherwise null.
  - **summary** (string) - A summary of the model's reasoning, otherwise null.
- **store** (boolean) - Indicates if the response is stored.
- **temperature** (number) - The sampling temperature used for generation.
- **text** (object) - Object containing text-specific formatting options.
  - **format** (object) - Object defining the text format.
    - **type** (string) - The type of text format (e.g., "text").
- **tool_choice** (string) - The strategy used for tool selection.
- **tools** (array) - An array of tools that were used or considered.
- **top_p** (number) - The top-p sampling value used for generation.
- **truncation** (string) - The truncation strategy applied (e.g., "disabled").
- **usage** (object) - An object detailing the token usage for the response.
  - **input_tokens** (integer) - The number of tokens in the input prompt.
  - **input_tokens_details** (object) - Further details on input tokens.
    - **cached_tokens** (integer) - The number of cached input tokens.
  - **output_tokens** (integer) - The number of tokens in the generated output.
  - **output_tokens_details** (object) - Further details on output tokens.
    - **reasoning_tokens** (integer) - The number of tokens used for reasoning.
  - **total_tokens** (integer) - The total number of tokens used (input + output).
- **user** (string) - An identifier for the end-user, otherwise null.
- **metadata** (object) - An object containing any additional metadata.

#### Response Example
```json
{
  "id": "resp_67ccd2bed1ec8190b14f964abc0542670bb6a6b452d3795b",
  "object": "response",
  "created_at": 1741476542,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4.1-2025-04-14",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd2bf17f0819081ff3bb2cf6508e60bb6a6b452d3795b",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "In a peaceful grove beneath a silver moon, a unicorn named Lumina discovered a hidden pool that reflected the stars. As she dipped her horn into the water, the pool began to shimmer, revealing a pathway to a magical realm of endless night skies. Filled with wonder, Lumina whispered a wish for all who dream to find their own hidden magic, and as she glanced back, her hoofprints sparkled like stardust.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 36,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 87,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 123
  },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### Examine OpenAI Responses API Usage Object for Reasoning Tokens

Source: https://platform.openai.com/docs/guides/reasoning

This JSON snippet illustrates the usage object returned by the OpenAI Responses API, detailing token consumption. It specifically highlights reasoning_tokens within output_tokens_details, which indicates the number of tokens the model used for internal reasoning before producing the final response, crucial for understanding cost and context window management.

```json
{
    "usage": {
        "input_tokens": 75,
        "input_tokens_details": {
            "cached_tokens": 0
        },
        "output_tokens": 1186,
        "output_tokens_details": {
            "reasoning_tokens": 1024
        },
        "total_tokens": 1261
    }
}
```

--------------------------------

### POST /v1/responses (Web Search Tool)

Source: https://platform.openai.com/docs/guides/responses-vs-chat-completions_api-mode=responses

This endpoint utilizes the OpenAI Responses API to perform a web search as a native tool. It allows the model to find information and generate a response based on the search results.

```APIDOC
## POST /v1/responses

### Description
This endpoint uses the OpenAI Responses API to generate a response by leveraging specified tools, such as 'web_search'. The model processes the input, uses the tool, and provides a concise answer.

### Method
POST

### Endpoint
https://api.openai.com/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The ID of the model to use (e.g., 'gpt-5').
- **input** (string) - Required - The user's input or question.
- **tools** (array of objects) - Required - A list of tools to be used by the model. Each object should have a 'type' field (e.g., 'web_search').

### Request Example
```bash
curl https://api.openai.com/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-5",
    "input": "Who is the current president of France?",
    "tools": [{"type": "web_search"}]
  }'
```

### Response
#### Success Response (200)
- **output_text** (string) - The model's generated response based on the input and tool usage.

#### Response Example
```json
{
  "output_text": "The current president of France is Emmanuel Macron."
}
```
```

--------------------------------

### POST /responses

Source: https://platform.openai.com/docs/api-reference/assistants-streaming/message-delta-object

This endpoint allows users to generate a model response by providing inputs, configuring response behavior, and managing conversational context.

```APIDOC
## POST /responses

### Description
This endpoint facilitates the creation of a model response, accepting various parameters to customize the behavior, inputs, and outputs of the generative AI model.

### Method
POST

### Endpoint
/responses

### Parameters
#### Path Parameters
(None)

#### Query Parameters
(None)

#### Request Body
- **background** (boolean) - Optional - Defaults to `false`. Whether to run the model response in the background. Learn more.
- **conversation** (string or object) - Optional - Defaults to `null`. The conversation this response belongs to. Items from this conversation are prepended to `input_items`. Input and output items are added to this conversation automatically after completion.
- **include** (array) - Optional - Specify additional output data to include in the model response. Supported values include `web_search_call.action.sources`, `code_interpreter_call.outputs`, `computer_call_output.output.image_url`, `file_search_call.results`, `message.input_image.image_url`, `message.output_text.logprobs`, `reasoning.encrypted_content`.
- **input** (string or array) - Optional - Text, image, or file inputs to the model, used to generate a response. Refer to documentation for text, image, file, conversation state, and function calling inputs.
- **instructions** (string) - Optional - A system (or developer) message inserted into the model's context. Overrides previous instructions when used with `previous_response_id`.
- **max_output_tokens** (integer) - Optional - An upper bound for the number of tokens that can be generated for a response, including visible output tokens and reasoning tokens.
- **max_tool_calls** (integer) - Optional - The maximum number of total calls to built-in tools that can be processed in a response across all tool calls.
- **metadata** (map) - Optional - Set of 16 key-value pairs (max 64 char keys, 512 char values) for storing additional structured information about the object.
- **model** (string) - Optional - Model ID used to generate the response, such as `gpt-4o` or `o3`. Refer to the model guide for available models.
- **parallel_tool_calls** (boolean) - Optional - Defaults to `true`. Whether to allow the model to run tool calls in parallel.
- **previous_response_id** (string) - Optional - The unique ID of the previous response to the model, used for multi-turn conversations. Cannot be used with `conversation`.
- **prompt** (object) - Optional - Reference to a prompt template and its variables.
- **prompt_cache_key** (string) - Optional - Used by OpenAI to cache responses for similar requests, optimizing cache hit rates. Replaces the `user` field.
- **reasoning** (object) - Optional - **gpt-5 and o-series models only**. Configuration options for reasoning models.
- **safety_identifier** (string) - Optional - A stable identifier to help detect users violating OpenAI's usage policies. Recommend hashing username or email.
- **service_tier** (string) - Optional - Defaults to `auto`. Specifies the processing type: `auto`, `default`, `flex`, or `priority`. The response will include the actual `service_tier` used.
- **store** (boolean) - Optional - Defaults to `true`.

### Request Example
```json
{
  "input": "Tell me a story about a brave knight.",
  "model": "gpt-4o",
  "instructions": "Make it a short, humorous story.",
  "metadata": {
    "user_id": "user_123"
  }
}
```

### Response
#### Success Response (200)
- **id** (string) - The unique identifier for the response.
- **object** (string) - The type of object, typically "response".
- **output** (array) - An array of output items generated by the model.
- **usage** (object) - Information about token usage.
- **created_at** (integer) - The timestamp when the response was created.
- **service_tier** (string) - The actual service tier used to process the request.

#### Response Example
```json
{
  "id": "resp_abc123",
  "object": "response",
  "output": [
    {
      "type": "message",
      "text": "Once upon a time, Sir Reginald the Fearless (mostly) faced a dragon. He bravely charged, then remembered his picnic basket, and offered the dragon a sandwich. They became friends. The end."
    }
  ],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 45
  },
  "created_at": 1678886400,
  "service_tier": "default"
}
```
```

--------------------------------

### response.created

Source: https://platform.openai.com/docs/api-reference/runs/listRuns

This event is returned when a new model Response is created. It represents the initial state of a response, marked as `in_progress`.

```APIDOC
## Event response.created

### Description
Returned when a new Response is created. This is the first event of response creation, where the response is in an initial state of `in_progress`.

### Method
Event

### Parameters
#### Event Payload Fields
- **event_id** (string) - The unique ID of the server event.
- **response** (object) - The response resource. See example for properties.
- **type** (string) - The event type, must be `response.created`.

### Event Payload Example
```json
{
  "type": "response.created",
  "event_id": "event_C9G8pqbTEddBSIxbBN6Os",
  "response": {
    "object": "realtime.response",
    "id": "resp_C9G8p7IH2WxLbkgPNouYL",
    "status": "in_progress",
    "status_details": null,
    "output": [],
    "conversation_id": "conv_C9G8mmBkLhQJwCon3hoJN",
    "output_modalities": [
      "audio"
    ],
    "max_output_tokens": "inf",
    "audio": {
      "output": {
        "format": {
          "type": "audio/pcm",
          "rate": 24000
        },
        "voice": "marin"
      }
    },
    "usage": null,
    "metadata": null
  },
  "timestamp": "2:30:35 PM"
}
```
```

--------------------------------

### GET /v1/responses/{response_id}/input_items

Source: https://platform.openai.com/docs/api-reference/evals

Retrieves a paginated list of input items associated with a specific response ID. This can include messages, tool outputs, or other data that contributed to the response generation.

```APIDOC
## GET /v1/responses/{response_id}/input_items

### Description
Returns a list of input items for a given response, representing the data that was fed into the model to generate that response.

### Method
GET

### Endpoint
/v1/responses/{response_id}/input_items

### Parameters
#### Path Parameters
- **response_id** (string) - Required - The ID of the response to retrieve input items for.

#### Query Parameters
- **after** (string) - Optional - An item ID to list items after, used for pagination.
- **include** (array) - Optional - Additional fields to include in the response. Refer to the `include` parameter for Response creation for more details.
- **limit** (integer) - Optional - Defaults to 20 - A limit on the number of objects to be returned. Limit can range between 1 and 100.
- **order** (string) - Optional - The order to return the input items in. Default is `desc`.
  - `asc`: Return the input items in ascending order.
  - `desc`: Return the input items in descending order.

#### Request Body
(None)

### Request Example
```bash
curl https://api.openai.com/v1/responses/resp_abc123/input_items \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Response
#### Success Response (200)
- **object** (string) - The type of object, typically 'list'.
- **data** (array) - A list of input item objects.
  - **id** (string) - The unique identifier of the input item.
  - **type** (string) - The type of the input item (e.g., 'message').
  - **role** (string) - The role of the message (e.g., 'user').
  - **content** (array) - An array of content parts for the input item.
    - **type** (string) - The type of content (e.g., 'input_text').
    - **text** (string) - The actual text content.
- **first_id** (string) - The ID of the first item in the list.
- **last_id** (string) - The ID of the last item in the list.
- **has_more** (boolean) - Indicates if there are more items to retrieve beyond the current list.

#### Response Example
```json
{
  "object": "list",
  "data": [
    {
      "id": "msg_abc123",
      "type": "message",
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": "Tell me a three sentence bedtime story about a unicorn."
        }
      ]
    }
  ],
  "first_id": "msg_abc123",
  "last_id": "msg_abc123",
  "has_more": false
}
```
```

--------------------------------

### Generate Image with OpenAI Responses API (JS & Python)

Source: https://platform.openai.com/docs/guides/image-generation_api=responses&image-generation-model=gpt-image-1

This snippet demonstrates how to generate an image using the OpenAI Responses API. It takes a text prompt and uses the 'image_generation' tool within a 'gpt-5' model. The JavaScript example saves the generated image to a file, while the Python example shows the API call. Note that the Responses API is ideal for conversational, editable image experiences.

```javascript
import OpenAI from "openai";
const openai = new OpenAI();

const response = await openai.responses.create({
    model: "gpt-5",
    input: "Generate an image of gray tabby cat hugging an otter with an orange scarf",
    tools: [{type: "image_generation"}],
});

// Save the image to a file
const imageData = response.output
  .filter((output) => output.type === "image_generation_call")
  .map((output) => output.result);

if (imageData.length > 0) {
  const imageBase64 = imageData[0];
  const fs = await import("fs");
  fs.writeFileSync("otter.png", Buffer.from(imageBase64, "base64"));
}
```

```python
from openai import OpenAI
import base64

client = OpenAI()

response = client.responses.create(
    model="gpt-5",
    input="Generate an image of gray tabby cat hugging an otter with an orange scarf",
    tools=[{"type": "image_generation"}],
)
```

--------------------------------

### POST /v1/responses (GPT-5 Responses API)

Source: https://platform.openai.com/docs/guides/latest-model_gallery=open&galleryitem=csv-to-charts

Interact with GPT-5 models using the Responses API, which offers enhanced support for Chain of Thought (CoT) and specific GPT-5 controls like `reasoning` effort, `text` verbosity, and custom `tools`. This API is recommended for improved intelligence, fewer generated reasoning tokens, higher cache hit rates, and lower latency. Note that `temperature`, `top_p`, and `logprobs` are NOT supported for GPT-5 models in this API and will raise an error if included.

```APIDOC
## POST /v1/responses

### Description
Interact with GPT-5 models via the Responses API, supporting Chain of Thought (CoT) and GPT-5 specific controls like reasoning effort, text verbosity, and custom tools. This API is recommended over Chat Completions for GPT-5.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The GPT-5 model to use (e.g., "gpt-5", "gpt-5-mini", "gpt-5-nano").
- **input** (string) - Required - The primary input or prompt for the model.
- **reasoning** (object) - Optional - Controls the depth of reasoning. 
  - **effort** (string) - Optional - "minimal" | "low" | "medium" | "high" - Specifies the reasoning effort.
- **text** (object) - Optional - Controls the output text verbosity.
  - **verbosity** (string) - Optional - "low" | "medium" | "high" - Specifies the output verbosity.
- **max_output_tokens** (integer) - Optional - The maximum number of tokens to generate in the output.
- **tools** (array of objects) - Optional - Custom tools for the model to use.
  - **type** (string) - Required - Type of the tool (e.g., "custom").
  - **name** (string) - Required - Name of the custom tool (e.g., "code_exec").
  - **description** (string) - Required - Description of the tool's function.

### Request Example (Reasoning Effort)
```json
{
  "model": "gpt-5",
  "input": "How much gold would it take to coat the Statue of Liberty in a 1mm layer?",
  "reasoning": {
    "effort": "minimal"
  }
}
```

### Request Example (Output Verbosity)
```json
{
  "model": "gpt-5",
  "input": "What is the answer to the ultimate question of life, the universe, and everything?",
  "text": {
    "verbosity": "low"
  }
}
```

### Request Example (Custom Tools)
```json
{
  "model": "gpt-5",
  "input": "Use the code_exec tool to calculate the area of a circle with radius equal to the number of r letters in blueberry",
  "tools": [
    {
      "type": "custom",
      "name": "code_exec",
      "description": "Executes arbitrary python code"
    }
  ]
}
```

### Response
#### Success Response (200)
A JSON object containing the model's generated response based on the input and specified parameters. The exact structure will depend on the model's output and tool usage.

#### Response Example
```json
{
  "id": "response_id",
  "object": "response",
  "created": 1678886400,
  "model": "gpt-5",
  "output": "Approximately 28 kilograms of gold."
}
```
```

--------------------------------

### POST /chat/completions (Multi-Turn Conversation - Manual Context)

Source: https://platform.openai.com/docs/guides/responses-vs-chat-completions

This endpoint allows you to manage multi-turn conversations by explicitly passing the entire message history (context) in each request to the Chat Completions API. The API generates a response based on the provided messages.

```APIDOC
## POST /chat/completions

### Description
Manages multi-turn conversations by manually constructing and sending the complete message history (context) with each request to the Chat Completions API. The model generates a response based on this history.

### Method
POST

### Endpoint
/chat/completions

### Parameters
#### Request Body
- **model** (string) - Required - The ID of the model to use (e.g., 'gpt-5').
- **messages** (array of objects) - Required - A list of messages comprising the conversation so far.
  - **role** (string) - Required - The role of the author of this message (e.g., 'system', 'user', 'assistant').
  - **content** (string) - Required - The content of the message.

### Request Example
```json
{
  "model": "gpt-5",
  "messages": [
    { "role": "system", "content": "You are a helpful assistant." },
    { "role": "user", "content": "What is the capital of France?" }
  ]
}
```

### Response
#### Success Response (200)
- **choices** (array) - A list of chat completion choices. The first choice contains the generated message.
  - **message** (object) - The message generated by the model.
    - **role** (string) - The role of the author of this message (e.g., 'assistant').
    - **content** (string) - The content of the message.

#### Response Example
```json
{
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Paris"
      },
      "finish_reason": "stop"
    }
  ],
  "model": "gpt-5",
  "object": "chat.completion"
}
```
```

--------------------------------

### POST /v1/responses (Text Generation)

Source: https://platform.openai.com/docs/context7

Generate text output from a prompt using the Responses API.

```APIDOC
## POST /v1/responses

### Description
Generate text output from a prompt using the Responses API.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
_None_

#### Query Parameters
_None_

#### Request Body
- **model** (string) - Required - The ID of the model to use for text generation. E.g., "gpt-5"
- **input** (string) - Required - The text prompt or input for the model.

### Request Example
```json
{
  "model": "gpt-5",
  "input": "Write a short bedtime story about a unicorn."
}
```

### Response
#### Success Response (200)
- **output_text** (string) - The generated text output from the model.

#### Response Example
```json
{
  "output_text": "Once upon a time, in a land filled with shimmering rainbows..."
}
```
```

--------------------------------

### POST /responses

Source: https://platform.openai.com/docs/api-reference/usage/moderations_object

Generates a response from an OpenAI model based on the provided input and configuration parameters. This endpoint facilitates interaction with various OpenAI models for tasks like chat completions, content generation, and more.

```APIDOC
## POST /responses

### Description
Generates a response from an OpenAI model based on the provided input and configuration parameters.

### Method
POST

### Endpoint
/responses

### Parameters
#### Path Parameters
_None_

#### Query Parameters
_None_

#### Request Body
- **background** (boolean) - Optional - Defaults to `false`. Whether to run the model response in the background. Learn more.
- **conversation** (string or object) - Optional - Defaults to `null`. The conversation that this response belongs to. Items from this conversation are prepended to `input_items` for this response request. Input items and output items from this response are automatically added to this conversation after this response completes.
- **include** (array) - Optional - Specify additional output data to include in the model response. Currently supported values are:
  * `web_search_call.action.sources`: Include the sources of the web search tool call.
  * `code_interpreter_call.outputs`: Includes the outputs of python code execution in code interpreter tool call items.
  * `computer_call_output.output.image_url`: Include image urls from the computer call output.
  * `file_search_call.results`: Include the search results of the file search tool call.
  * `message.input_image.image_url`: Include image urls from the input message.
  * `message.output_text.logprobs`: Include logprobs with assistant messages.
  * `reasoning.encrypted_content`: Includes an encrypted version of reasoning tokens in reasoning item outputs. This enables reasoning items to be used in multi-turn conversations when using the Responses API statelessly (like when the `store` parameter is set to `false`, or when an organization is enrolled in the zero data retention program).
- **input** (string or array) - Optional - Text, image, or file inputs to the model, used to generate a response. Learn more: Text inputs and outputs, Image inputs, File inputs, Conversation state, Function calling.
- **instructions** (string) - Optional - A system (or developer) message inserted into the model's context. When using along with `previous_response_id`, the instructions from a previous response will not be carried over to the next response. This makes it simple to swap out system (or developer) messages in new responses.
- **max_output_tokens** (integer) - Optional - An upper bound for the number of tokens that can be generated for a response, including visible output tokens and reasoning tokens.
- **max_tool_calls** (integer) - Optional - The maximum number of total calls to built-in tools that can be processed in a response. This maximum number applies across all built-in tool calls, not per individual tool. Any further attempts to call a tool by the model will be ignored.
- **metadata** (map) - Optional - Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard. Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.
- **model** (string) - Optional - Model ID used to generate the response, like `gpt-4o` or `o3`. OpenAI offers a wide range of models with different capabilities, performance characteristics, and price points. Refer to the model guide to browse and compare available models.
- **parallel_tool_calls** (boolean) - Optional - Defaults to `true`. Whether to allow the model to run tool calls in parallel.
- **previous_response_id** (string) - Optional - The unique ID of the previous response to the model. Use this to create multi-turn conversations. Learn more about conversation state. Cannot be used in conjunction with `conversation`.
- **prompt** (object) - Optional - Reference to a prompt template and its variables. Learn more.
- **prompt_cache_key** (string) - Optional - Used by OpenAI to cache responses for similar requests to optimize your cache hit rates. Replaces the `user` field. Learn more.
- **reasoning** (object) - Optional - **gpt-5 and o-series models only**. Configuration options for reasoning models.
- **safety_identifier** (string) - Optional - A stable identifier used to help detect users of your application that may be violating OpenAI's usage policies. The IDs should be a string that uniquely identifies each user. We recommend hashing their username or email address, in order to avoid sending us any identifying information. Learn more.
- **service_tier** (string) - Optional - Defaults to `auto`. Specifies the processing type used for serving the request. If set to 'auto', then the request will be processed with the service tier configured in the Project settings. Unless otherwise configured, the Project will use 'default'. If set to 'default', then the request will be processed with the standard pricing and performance for the selected model. If set to 'flex' or 'priority', then the request will be processed with the corresponding service tier. When not set, the default behavior is 'auto'. When the `service_tier` parameter is set, the response body will include the `service_tier` value based on the processing mode actually used to serve the request. This response value may be different from the value set in the parameter.
- **store** (boolean) - Optional - Defaults to `true`. Whether to store the response.

### Request Example
```json
{
  "model": "gpt-4o",
  "input": [
    {
      "type": "text",
      "text": "What is the capital of France?"
    }
  ],
  "instructions": "You are a helpful AI assistant.",
  "max_output_tokens": 500,
  "conversation": "conv_abc123"
}
```

### Response
#### Success Response (200)
- **response_id** (string) - A unique identifier for the generated response.
- **output** (array) - An array of output items from the model, which can include text, tool calls, or other structured data.
- **model** (string) - The ID of the model used to generate the response.
- **usage** (object) - Information about the token usage for the request.
- **created_at** (timestamp) - The timestamp when the response was created.

#### Response Example
```json
{
  "response_id": "resp_xyz456",
  "output": [
    {
      "type": "text",
      "text": "The capital of France is Paris."
    }
  ],
  "model": "gpt-4o",
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 7,
    "total_tokens": 22
  },
  "created_at": 1678886400
}
```
```

--------------------------------

### Response Object Structure

Source: https://platform.openai.com/docs/api-reference/usage/moderations

Describes the structure of the response object returned by the OpenAI API, including fields like id, object, and output.

```APIDOC
## Response Object Structure

### Description
This section describes the structure of the response object returned by the OpenAI API after a successful request. It includes details about the generated output, token usage, and other metadata.

### Fields

- **id** (string) - The unique identifier for the response.
- **object** (string) - The type of object, which is `response`.
- **created_at** (integer) - The timestamp when the response was created (Unix epoch time).
- **status** (string) - The status of the response, e.g., `completed`.
- **error** (object) - An error object if the request failed; otherwise, `null`.
- **output** (array) - An array containing the model's output messages.
- **usage** (object) - An object containing token usage details.

### Response Example
```json
{
  "id": "resp_67ccd3a9da748190baa7f1570fe91ac604becb25c45c1d41",
  "object": "response",
  "created_at": 1741476777,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4o-2024-08-06",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd3acc8d48190a77525dc6de64b4104becb25c45c1d41",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "The image depicts a scenic landscape with a wooden boardwalk or pathway leading through lush, green grass under a blue sky with some clouds. The setting suggests a peaceful natural area, possibly a park or nature reserve. There are trees and shrubs in the background.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 328,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 52,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 380
  },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/api-reference/realtime-calls/accept-call

Creates a new model response based on the provided model and input text.

```APIDOC
## POST /v1/responses

### Description
Creates a new model response based on the provided model and input text, sending it to the OpenAI API.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The ID of the model to use for generating the response (e.g., "gpt-4.1").
- **input** (string) - Required - The input text or prompt for which to generate a response.

### Request Example
```json
{
  "model": "gpt-4.1",
  "input": "Tell me a three sentence bedtime story about a unicorn."
}
```

### Response
#### Success Response (200)
- **id** (string) - Unique identifier for the generated response.
- **object** (string) - The type of object returned, typically "response".
- **created_at** (integer) - Unix timestamp (in seconds) when the response was created.
- **status** (string) - The current status of the response (e.g., "completed").
- **model** (string) - The specific model version used to generate the response.
- **output** (array) - An array of output messages, each containing content generated by the model.
- **usage** (object) - Details about token usage for the request (input, output, total tokens).

#### Response Example
```json
{
  "id": "resp_67ccd2bed1ec8190b14f964abc0542670bb6a6b452d3795b",
  "object": "response",
  "created_at": 1741476542,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4.1-2025-04-14",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd2bf17f0819081ff3bb2cf6508e60bb6a6b452d3795b",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "In a peaceful grove beneath a silver moon, a unicorn named Lumina discovered a hidden pool that reflected the stars. As she dipped her horn into the water, the pool began to shimmer, revealing a pathway to a magical realm of endless night skies. Filled with wonder, Lumina whispered a wish for all who dream to find their own hidden magic, and as she glanced back, her hoofprints sparkled like stardust.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 36,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 87,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 123
  },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### response.created

Source: https://platform.openai.com/docs/api-reference/responses/object

This event is returned when a new Response is created. It represents the first event of response creation, where the response is in an initial `in_progress` state.

```APIDOC
## EVENT response.created

### Description
Returned when a new Response is created. The first event of response creation, where the response is in an initial state of `in_progress`.

### Method
EVENT

### Event Name
response.created

### Payload
- **event_id** (string) - The unique ID of the server event.
- **response** (object) - The response resource. (See 'Show properties' for detailed object structure, not provided in source for this level).
- **type** (string) - The event type, must be `response.created`.

### Example Payload
```json
{
  "type": "response.created",
  "event_id": "event_C9G8pqbTEddBSIxbBN6Os",
  "response": {
    "object": "realtime.response",
    "id": "resp_C9G8p7IH2WxLbkgPNouYL",
    "status": "in_progress",
    "status_details": null,
    "output": [],
    "conversation_id": "conv_C9G8mmBkLhQJwCon3hoJN",
    "output_modalities": [
      "audio"
    ],
    "max_output_tokens": "inf",
    "audio": {
      "output": {
        "format": {
          "type": "audio/pcm",
          "rate": 24000
        },
        "voice": "marin"
      }
    },
    "usage": null,
    "metadata": null
  },
  "timestamp": "2:30:35 PM"
}
```
```

--------------------------------

### POST /v1/responses - Create a model response

Source: https://platform.openai.com/docs/api-reference/realtime-server-events/rate_limits

This endpoint allows you to create a model response by providing text or image inputs. It supports generating text or JSON outputs and can integrate with custom code or built-in tools like web search or file search.

```APIDOC
## POST /v1/responses

### Description
Creates a model response. Provide text or image inputs to generate text or JSON outputs. Have the model call your own custom code or use built-in tools like web search or file search to use your own data as input for the model's response.

### Method
POST

### Endpoint
https://api.openai.com/v1/responses

### Parameters
#### Path Parameters
- No path parameters described for this endpoint.

#### Query Parameters
- No query parameters described for this endpoint.

#### Request Body
- **inputs** (object) - Required - Contains text or image data for the model's input.
- **output_format** (string) - Optional - Specifies the desired output format, e.g., "text" or "json".
- **tools** (array) - Optional - List of tools (e.g., custom functions, web search, file search) to extend the model's capabilities.

### Request Example
```json
{
  "model": "gpt-4o",
  "messages": [
    {
      "role": "user",
      "content": "Tell me a story about a brave knight."
    }
  ],
  "temperature": 0.7
}
```

### Response
#### Success Response (200)
- **id** (string) - Unique identifier for the response.
- **object** (string) - Type of object, typically "chat.completion" or similar.
- **created** (integer) - Timestamp when the response was created.
- **model** (string) - The model used to generate the response.
- **choices** (array) - List of generated choices, each containing a message object with the model's output.

#### Response Example
```json
{
  "id": "chatcmpl-12345",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "gpt-4o",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Once upon a time, in a land far away..."
      },
      "finish_reason": "stop"
    }
  ]
}
```
```

--------------------------------

### GET /v1/responses/{response_id}

Source: https://platform.openai.com/docs/api-reference/container-files/object

Retrieves a Response object matching the specified ID from the OpenAI platform. This allows you to inspect the details, status, and output of a previously generated response.

```APIDOC
## GET /v1/responses/{response_id}

### Description
Retrieves the Response object matching the specified ID.

### Method
GET

### Endpoint
/v1/responses/{response_id}

### Parameters
#### Path Parameters
- **response_id** (string) - Required - The ID of the response to retrieve.

### Request Example
```
curl https://api.openai.com/v1/responses/resp_123 \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Response
#### Success Response (200)
- **id** (string) - The unique identifier for the response.
- **object** (string) - The object type, typically "response".
- **created_at** (integer) - The Unix timestamp (in seconds) for when the response was created.
- **status** (string) - The status of the response (e.g., "completed").
- **error** (object | null) - Details if an error occurred, otherwise `null`.
- **incomplete_details** (object | null) - Details if the response is incomplete, otherwise `null`.
- **instructions** (object | null) - Any instructions associated with the response.
- **max_output_tokens** (integer | null) - Maximum number of output tokens.
- **model** (string) - The model used to generate the response.
- **output** (array of objects) - The generated output, which can contain messages or tool calls.
  - **type** (string) - Type of output (e.g., "message").
  - **id** (string) - ID of the output part.
  - **status** (string) - Status of the output part.
  - **role** (string) - Role of the agent (e.g., "assistant").
  - **content** (array of objects) - Actual content.
    - **type** (string) - Type of content (e.g., "output_text").
    - **text** (string) - The generated text.
    - **annotations** (array) - Any annotations in the text.
- **parallel_tool_calls** (boolean) - Indicates if parallel tool calls are enabled.
- **previous_response_id** (string | null) - ID of a previous response if this is a continuation.
- **reasoning** (object) - Details about the reasoning process.
  - **effort** (string | null) - Effort level.
  - **summary** (string | null) - Summary of reasoning.
- **store** (boolean) - Whether the response is stored.
- **temperature** (number) - Sampling temperature used.
- **text** (object) - Text formatting details.
  - **format** (object) - Format specification.
    - **type** (string) - Type of text format.
- **tool_choice** (string) - Tool choice strategy.
- **tools** (array) - List of tools used.
- **top_p** (number) - Top-p sampling value.
- **truncation** (string) - Truncation strategy.
- **usage** (object) - Token usage statistics.
  - **input_tokens** (integer) - Number of input tokens.
  - **input_tokens_details** (object) - Details about input tokens.
    - **cached_tokens** (integer) - Number of cached tokens.
  - **output_tokens** (integer) - Number of output tokens.
  - **output_tokens_details** (object) - Details about output tokens.
    - **reasoning_tokens** (integer) - Number of reasoning tokens.
  - **total_tokens** (integer) - Total number of tokens.
- **user** (string | null) - User identifier.
- **metadata** (object) - Arbitrary metadata.

#### Response Example
```
{
  "id": "resp_67cb71b351908190a308f3859487620d06981a8637e6bc44",
  "object": "response",
  "created_at": 1741386163,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4o-2024-08-06",
  "output": [
    {
      "type": "message",
      "id": "msg_67cb71b3c2b0819084d481baaaf148f206981a8637e6bc44",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "Silent circuits hum,  \nThoughts emerge in data streams—  \nDigital dawn breaks.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 32,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 18,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 50
  },
  "user": null,
  "metadata": {}
}
```
```

--------------------------------

### response.created

Source: https://platform.openai.com/docs/api-reference/project-api-keys/list

This event is returned when a new Response is created, representing the first event in the response creation lifecycle with the response in an initial `in_progress` state.

```APIDOC
## response.created

### Description
Returned when a new Response is created. The first event of response creation, where the response is in an initial state of `in_progress`.

### Method
EVENT

### Endpoint
N/A (Event)

### Parameters
#### Path Parameters
- No path parameters.

#### Query Parameters
- No query parameters.

#### Request Body
- **event_id** (string) - The unique ID of the server event.
- **response** (object) - The response resource.
  - **object** (string) - The object type, e.g., "realtime.response".
  - **id** (string) - The unique ID of the response.
  - **status** (string) - The current status of the response, e.g., "in_progress".
  - **status_details** (string, nullable) - Details about the status.
  - **output** (array) - An array of output parts.
  - **conversation_id** (string) - The ID of the conversation this response belongs to.
  - **output_modalities** (array of strings) - An array of modalities for output, e.g., ["audio"].
  - **max_output_tokens** (string) - Maximum output tokens, e.g., "inf".
  - **audio** (object) - Audio configuration.
    - **output** (object) - Output audio settings.
      - **format** (object) - Audio format details.
        - **type** (string) - Audio format type, e.g., "audio/pcm".
        - **rate** (integer) - Audio sample rate, e.g., 24000.
      - **voice** (string) - The voice used, e.g., "marin".
  - **usage** (object, nullable) - Usage statistics.
  - **metadata** (object, nullable) - Additional metadata.
- **type** (string) - The event type, must be `response.created`.

### Request Example
```json
{
  "type": "response.created",
  "event_id": "event_C9G8pqbTEddBSIxbBN6Os",
  "response": {
    "object": "realtime.response",
    "id": "resp_C9G8p7IH2WxLbkgPNouYL",
    "status": "in_progress",
    "status_details": null,
    "output": [],
    "conversation_id": "conv_C9G8mmBkLhQJwCon3hoJN",
    "output_modalities": [
      "audio"
    ],
    "max_output_tokens": "inf",
    "audio": {
      "output": {
        "format": {
          "type": "audio/pcm",
          "rate": 24000
        },
        "voice": "marin"
      }
    },
    "usage": null,
    "metadata": null
  }
}
```

### Response
#### Success Response (200)
- No direct response. This is an event payload.

#### Response Example
```json
{}
```
```

--------------------------------

### POST /v1/responses

Source: https://platform.openai.com/docs/api-reference/fine-tuning/list

Creates a new model response by sending input text to a specified model. The response will contain the generated output from the model.

```APIDOC
## POST /v1/responses

### Description
Creates a new model response based on the provided input and model. This endpoint allows users to send text prompts to an AI model and receive a generated response.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
(None)

#### Query Parameters
(None)

#### Request Body
- **model** (string) - Required - The ID of the model to use for generating the response (e.g., "gpt-4.1").
- **input** (string) - Required - The text prompt to send to the model for generating a response.

### Request Example
{
  "model": "gpt-4.1",
  "input": "Tell me a three sentence bedtime story about a unicorn."
}

### Response
#### Success Response (200)
- **id** (string) - A unique identifier for the response.
- **object** (string) - The type of object, typically "response".
- **created_at** (integer) - The Unix timestamp (in seconds) when the response was created.
- **status** (string) - The current status of the response (e.g., "completed").
- **error** (object|null) - Contains error details if the request failed.
- **incomplete_details** (object|null) - Details if the response is incomplete.
- **instructions** (object|null) - Any specific instructions used for generation.
- **max_output_tokens** (integer|null) - The maximum number of output tokens allowed.
- **model** (string) - The ID of the model that generated this response.
- **output** (array) - An array of output messages.
  - **type** (string) - The type of output, e.g., "message".
  - **id** (string) - A unique identifier for the output message.
  - **status** (string) - The status of the output message.
  - **role** (string) - The role of the entity that generated this output, e.g., "assistant".
  - **content** (array) - An array of content parts within the message.
    - **type** (string) - The type of content, e.g., "output_text".
    - **text** (string) - The actual generated text from the model.
    - **annotations** (array) - Any annotations associated with the text.
- **parallel_tool_calls** (boolean) - Indicates if parallel tool calls were enabled.
- **previous_response_id** (string|null) - The ID of a previous response if this is part of a chained interaction.
- **reasoning** (object) - Details about the reasoning process.
  - **effort** (string|null) - The effort level of the reasoning.
  - **summary** (string|null) - A summary of the reasoning.
- **store** (boolean) - Indicates if the response is stored.
- **temperature** (number) - The temperature parameter used for generation.
- **text** (object) - Text-specific formatting information.
  - **format** (object)
    - **type** (string) - The format type, e.g., "text".
- **tool_choice** (string) - The tool choice parameter used.
- **tools** (array) - A list of tools used during the generation process.
- **top_p** (number) - The top_p parameter used for generation.
- **truncation** (string) - The truncation setting used.
- **usage** (object) - Detailed token usage statistics.
  - **input_tokens** (integer) - The number of input tokens consumed.
  - **input_tokens_details** (object)
    - **cached_tokens** (integer) - The number of cached input tokens.
  - **output_tokens** (integer) - The number of output tokens generated.
  - **output_tokens_details** (object)
    - **reasoning_tokens** (integer) - The number of reasoning tokens.
  - **total_tokens** (integer) - The total number of tokens (input + output).
- **user** (string|null) - The identifier of the user associated with the request.
- **metadata** (object) - Additional metadata.

### Response Example
{
  "id": "resp_67ccd2bed1ec8190b14f964abc0542670bb6a6b452d3795b",
  "object": "response",
  "created_at": 1741476542,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4.1-2025-04-14",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd2bf17f0819081ff3bb2cf6508e60bb6a6b452d3795b",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "In a peaceful grove beneath a silver moon, a unicorn named Lumina discovered a hidden pool that reflected the stars. As she dipped her horn into the water, the pool began to shimmer, revealing a pathway to a magical realm of endless night skies. Filled with wonder, Lumina whispered a wish for all who dream to find their own hidden magic, and as she glanced back, her hoofprints sparkled like stardust.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 36,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 87,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 123
  },
  "user": null,
  "metadata": {}
}
```

--------------------------------

### response.create event

Source: https://platform.openai.com/docs/api-reference/assistants/createAssistant

This event instructs the server to create a Response, triggering model inference. It allows for configuring inference parameters, managing conversation history integration, and providing arbitrary input for out-of-band responses.

```APIDOC
## WebSocket (Client-to-Server) response.create

### Description
This event instructs the server to create a Response, which means triggering model inference. When in Server VAD mode, the server will create Responses automatically.
A Response will include at least one Item, and may have two, in which case the second will be a function call. These Items will be appended to the conversation history.
The server will respond with a `response.created` event, events for Items and content created, and finally a `response.done` event to indicate the Response is complete.
The `response.create` event can optionally include inference configuration like `instructions`, and `temperature`. These fields will override the Session's configuration for this Response only.
Responses can be created out-of-band of the default Conversation, meaning that they can have arbitrary input, and it's possible to disable writing the output to the Conversation. Only one Response can write to the default Conversation at a time, but otherwise multiple Responses can be created in parallel.
Clients can set `conversation` to `none` to create a Response that does not write to the default Conversation. Arbitrary input can be provided with the `input` field, which is an array accepting raw Items and references to existing Items.

### Method
WebSocket (Client-to-Server Event)

### Endpoint
`response.create`

### Parameters
#### Request Body
- **event_id** (string) - Optional - Client-generated ID used to identify this event.
- **type** (string) - Required - The event type, must be `response.create`.
- **response** (object) - Optional - Create a new Realtime response with these parameters.
  - **instructions** (string) - Optional - Inference configuration instructions.
  - **temperature** (number) - Optional - Inference temperature setting.
  - **tools** (array) - Optional - A list of tools to use. Can be an empty array to clear any session tools.
  - **conversation** (string) - Optional - Set to `none` to create a Response that does not write to the default Conversation.
  - **output_modalities** (array of strings) - Optional - A list of output modalities, e.g., ["text"].
  - **input** (array) - Optional - An array accepting raw Items and references to existing Items for arbitrary input.
    - **type** (string) - Required - Type of input item, e.g., `item_reference`, `message`.
    - **id** (string) - Required if `type` is `item_reference` - ID of the existing item.
    - **role** (string) - Required if `type` is `message` - Role of the message, e.g., `user`.
    - **content** (array) - Required if `type` is `message` - Array of content blocks.
      - **type** (string) - Type of content block, e.g., `input_text`.
      - **text** (string) - The input text content.

### Request Example
```json
{
  "type": "response.create",
  "response": {
    "instructions": "Provide a concise answer.",
    "tools": [],
    "conversation": "none",
    "output_modalities": ["text"],
    "input": [
      {
        "type": "item_reference",
        "id": "item_12345"
      },
      {
        "type": "message",
        "role": "user",
        "content": [
          {
            "type": "input_text",
            "text": "Summarize the above message in one sentence."
          }
        ]
      }
    ]
  }
}
```

### Response
#### Server Response Events
- **response.created** - Indicates the Response has been initiated.
- **item.created**, **content.created** - Events for content creation during inference.
- **response.done** - Indicates the Response is complete.
```

--------------------------------

### MCP Tool Call API Response (JSON)

Source: https://platform.openai.com/docs/guides/tools-connectors-mcp

This JSON object depicts the `mcp_call` output item from the OpenAI API response when the model decides to invoke an MCP tool. It includes information about the specific tool called, the arguments passed to it (e.g., `diceRollExpression`), and the output received back from the tool after execution.

```json
{
    "id": "mcp_68a6102d8948819c9b1490d36d5ffa4a0679e572a900e618",
    "type": "mcp_call",
    "approval_request_id": null,
    "arguments": "{\"diceRollExpression\":\"2d4 + 1\"}",
    "error": null,
    "name": "roll",
    "output": "4",
    "server_label": "dmcp"
}
```