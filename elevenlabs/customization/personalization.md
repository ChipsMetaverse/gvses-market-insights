---
title: Personalization
subtitle: >-
  Learn how to personalize your agent's behavior using dynamic variables and
  overrides.
---

## Overview

Personalization allows you to adapt your agent's behavior for each individual user, enabling more natural and contextually relevant conversations. ElevenLabs offers multiple approaches to personalization:

1. **Dynamic Variables** - Inject runtime values into prompts and messages
2. **Overrides** - Completely replace system prompts or messages
3. **Twilio Integration** - Personalize inbound call experiences via webhooks

## Personalization Methods

<CardGroup cols={3}>
  <Card
    title="Dynamic Variables"
    icon="duotone lambda"
    href="/docs/conversational-ai/customization/personalization/dynamic-variables"
  >
    Define runtime values using `{{ var_name }}` syntax to personalize your agent's messages, system
    prompts, and tools.
  </Card>
  <Card
    title="Overrides"
    icon="duotone sliders"
    href="/docs/conversational-ai/customization/personalization/overrides"
  >
    Completely replace system prompts, first messages, language, or voice settings for each
    conversation.
  </Card>
  <Card
    title="Twilio Integration"
    icon="duotone phone-arrow-down-left"
    href="/docs/conversational-ai/customization/personalization/twilio-personalization"
  >
    Dynamically personalize inbound Twilio calls using webhook data.
  </Card>
</CardGroup>

## Conversation Initiation Client Data Structure

The `conversation_initiation_client_data` object defines what can be customized when starting a conversation:

```json
{
  "type": "conversation_initiation_client_data",
  "conversation_config_override": {
    "agent": {
      "prompt": {
        "prompt": "overriding system prompt"
      },
      "first_message": "overriding first message",
      "language": "en"
    },
    "tts": {
      "voice_id": "voice-id-here"
    }
  },
  "custom_llm_extra_body": {
    "temperature": 0.7,
    "max_tokens": 100
  },
  "dynamic_variables": {
    "string_var": "text value",
    "number_var": 1.2,
    "integer_var": 123,
    "boolean_var": true
  },
  "user_id": "your_custom_user_id"
}
```

## Choosing the Right Approach

<Table>
  <thead>
    <tr>
      <th>Method</th>
      <th>Best For</th>
      <th>Implementation</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>**Dynamic Variables**</td>
      <td>
        - Inserting user-specific data into templated content - Maintaining consistent agent
        behavior with personalized details - Personalizing tool parameters
      </td>
      <td>Define variables with `{{ variable_name }}` and pass values at runtime</td>
    </tr>
    <tr>
      <td>**Overrides**</td>
      <td>
        - Completely changing agent behavior per user - Switching languages or voices - Legacy
        applications (consider migrating to Dynamic Variables)
      </td>
      <td>
        Enable specific override permissions in security settings and pass complete replacement
        content
      </td>
    </tr>
  </tbody>
</Table>

## Learn More

- [Dynamic Variables Documentation](/docs/conversational-ai/customization/personalization/dynamic-variables)
- [Overrides Documentation](/docs/conversational-ai/customization/personalization/overrides)
- [Twilio Integration Documentation](/docs/conversational-ai/customization/personalization/twilio-personalization)


---
title: Dynamic variables
subtitle: Pass runtime values to personalize your agent's behavior.
---

**Dynamic variables** allow you to inject runtime values into your agent's messages, system prompts, and tools. This enables you to personalize each conversation with user-specific data without creating multiple agents.

## Overview

Dynamic variables can be integrated into multiple aspects of your agent:

- **System prompts** to customize behavior and context
- **First messages** to personalize greetings
- **Tool parameters and headers** to pass user-specific data

Here are a few examples where dynamic variables are useful:

- **Personalizing greetings** with user names
- **Including account details** in responses
- **Passing data** to tool calls
- **Customizing behavior** based on subscription tiers
- **Accessing system information** like conversation ID or call duration

<Info>
  Dynamic variables are ideal for injecting user-specific data that shouldn't be hardcoded into your
  agent's configuration.
</Info>

## System dynamic variables

Your agent has access to these automatically available system variables:

- `system__agent_id` - Unique identifier of the agent that initiated the conversation (stays stable throughout the conversation)
- `system__current_agent_id` - Unique identifier of the currently active agent (changes after agent transfers)
- `system__caller_id` - Caller's phone number (voice calls only)
- `system__called_number` - Destination phone number (voice calls only)
- `system__call_duration_secs` - Call duration in seconds
- `system__time_utc` - Current UTC time (ISO format)
- `system__conversation_id` - ElevenLabs' unique conversation identifier
- `system__call_sid` - Call SID (twilio calls only)

System variables:

- Are available without runtime configuration
- Are prefixed with `system__` (reserved prefix)
- In system prompts: Set once at conversation start (value remains static)
- In tool calls: Updated at execution time (value reflects current state)

<Warning>Custom dynamic variables cannot use the reserved `system__` prefix.</Warning>

## Secret dynamic variables

Secret dynamic variables are populated in the same way as normal dynamic variables but indicate to our Conversational AI platform that these should
only be used in dynamic variable headers and never sent to an LLM provider as part of an agent's system prompt or first message.

We recommend using these for auth tokens or private IDs that should not be sent to an LLM. To create a secret dynamic variable, simply prefix the dynamic variable with `secret__`.

## Updating dynamic variables from tools

[Tool calls](https://elevenlabs.io/docs/conversational-ai/customization/tools) can create or update dynamic variables if they return a valid JSON object. To specify what should be extracted, set the object path(s) using dot notation. If the field or path doesn't exist, nothing is updated.

Example of a response object and dot notation:

- Status corresponds to the path: `response.status`
- The first user's email in the users array corresponds to the path: `response.users.0.email`

<CodeGroup>
```JSON title="JSON"
{
  "response": {
    "status": 200,
    "message": "Successfully found 5 users",
    "users": [
      "user_1": {
        "user_name": "test_user_1",
        "email": "test_user_1@email.com"
      }
    ]
  }
}
```
</CodeGroup>

To update a dynamic variable to be the first user's email, set the assignment like so.

<Frame background="subtle">
  ![Query parameters](file:c7250859-0ab8-452a-8adf-a893086825ae)
</Frame>

Assignments are a field of each server tool, that can be found documented [here](/docs/conversational-ai/api-reference/tools/create#response.body.tool_config.SystemToolConfig.assignments).

## Guide

### Prerequisites

- An [ElevenLabs account](https://elevenlabs.io)
- A configured ElevenLabs Conversational Agent ([create one here](/docs/conversational-ai/quickstart))

<Steps>
  <Step title="Define dynamic variables in prompts">
    Add variables using double curly braces `{{variable_name}}` in your:
    - System prompts
    - First messages
    - Tool parameters

    <Frame background="subtle">
      ![Dynamic variables in messages](file:d486a33f-d23a-4393-9025-f4f5b334afd9)
    </Frame>

    <Frame background="subtle">
      ![Dynamic variables in messages](file:cc423c88-119c-4973-a429-208c26fbb13a)
    </Frame>

  </Step>

  <Step title="Define dynamic variables in tools">
    You can also define dynamic variables in the tool configuration.
    To create a new dynamic variable, set the value type to Dynamic variable and click the `+` button.

    <Frame background="subtle">
      ![Setting placeholders](file:ba6c7aaf-f1e9-4597-af8f-771bcea1a4b2)
    </Frame>

    <Frame background="subtle">
      ![Setting placeholders](file:dedfcef0-8a3f-43fb-8898-93ccf056c2a8)
    </Frame>

  </Step>

  <Step title="Set placeholders">
    Configure default values in the web interface for testing:

    <Frame background="subtle">
      ![Setting placeholders](file:6a93a37d-4db7-4e72-896c-28ef24044494)
    </Frame>

  </Step>

  <Step title="Pass variables at runtime">
    When starting a conversation, provide the dynamic variables in your code:

    <Tip>
      Ensure you have the latest [SDK](/docs/conversational-ai/libraries) installed.
    </Tip>

    <CodeGroup>
    ```python title="Python" focus={10-23} maxLines=25
    import os
    import signal
    from elevenlabs.client import ElevenLabs
    from elevenlabs.conversational_ai.conversation import Conversation, ConversationInitiationData
    from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

    agent_id = os.getenv("AGENT_ID")
    api_key = os.getenv("ELEVENLABS_API_KEY")
    elevenlabs = ElevenLabs(api_key=api_key)

    dynamic_vars = {
        "user_name": "Angelo",
    }

    config = ConversationInitiationData(
        dynamic_variables=dynamic_vars
    )

    conversation = Conversation(
        elevenlabs,
        agent_id,
        config=config,
        # Assume auth is required when API_KEY is set.
        requires_auth=bool(api_key),
        # Use the default audio interface.
        audio_interface=DefaultAudioInterface(),
        # Simple callbacks that print the conversation to the console.
        callback_agent_response=lambda response: print(f"Agent: {response}"),
        callback_agent_response_correction=lambda original, corrected: print(f"Agent: {original} -> {corrected}"),
        callback_user_transcript=lambda transcript: print(f"User: {transcript}"),
        # Uncomment the below if you want to see latency measurements.
        # callback_latency_measurement=lambda latency: print(f"Latency: {latency}ms"),
    )

    conversation.start_session()

    signal.signal(signal.SIGINT, lambda sig, frame: conversation.end_session())
    ```

    ```javascript title="JavaScript" focus={7-20} maxLines=25
    import { Conversation } from '@elevenlabs/client';

    class VoiceAgent {
      ...

      async startConversation() {
        try {
            // Request microphone access
            await navigator.mediaDevices.getUserMedia({ audio: true });

            this.conversation = await Conversation.startSession({
                agentId: 'agent_id_goes_here', // Replace with your actual agent ID

                dynamicVariables: {
                    user_name: 'Angelo'
                },

                ... add some callbacks here
            });
        } catch (error) {
            console.error('Failed to start conversation:', error);
            alert('Failed to start conversation. Please ensure microphone access is granted.');
        }
      }
    }
    ```

    ```swift title="Swift"
    let dynamicVars: [String: DynamicVariableValue] = [
      "customer_name": .string("John Doe"),
      "account_balance": .number(5000.50),
      "user_id": .int(12345),
      "is_premium": .boolean(true)
    ]

    // Create session config with dynamic variables
    let config = SessionConfig(
        agentId: "your_agent_id",
        dynamicVariables: dynamicVars
    )

    // Start the conversation
    let conversation = try await Conversation.startSession(
        config: config
    )
    ```

    ```html title="Widget"
    <elevenlabs-convai
      agent-id="your-agent-id"
      dynamic-variables='{"user_name": "John", "account_type": "premium"}'
    ></elevenlabs-convai>
    ```
    </CodeGroup>

  </Step>
</Steps>

## Public Talk-to Page Integration

The public talk-to page supports dynamic variables through URL parameters, enabling you to personalize conversations when sharing agent links. This is particularly useful for embedding personalized agents in websites, emails, or marketing campaigns.

### URL Parameter Methods

There are two methods to pass dynamic variables to the public talk-to page:

#### Method 1: Base64-Encoded JSON

Pass variables as a base64-encoded JSON object using the `vars` parameter:

```
https://elevenlabs.io/app/talk-to?agent_id=your_agent_id&vars=eyJ1c2VyX25hbWUiOiJKb2huIiwiYWNjb3VudF90eXBlIjoicHJlbWl1bSJ9
```

The `vars` parameter contains base64-encoded JSON:

```json
{ "user_name": "John", "account_type": "premium" }
```

#### Method 2: Individual Query Parameters

Pass variables using `var_` prefixed query parameters:

```
https://elevenlabs.io/app/talk-to?agent_id=your_agent_id&var_user_name=John&var_account_type=premium
```

### Parameter Precedence

When both methods are used simultaneously, individual `var_` parameters take precedence over the base64-encoded variables to prevent conflicts:

```
https://elevenlabs.io/app/talk-to?agent_id=your_agent_id&vars=eyJ1c2VyX25hbWUiOiJKYW5lIn0=&var_user_name=John
```

In this example, `user_name` will be "John" (from `var_user_name`) instead of "Jane" (from the base64-encoded `vars`).

### Implementation Examples

<Tabs>
  <Tab title="JavaScript URL Generation">
    ```javascript
    // Method 1: Base64-encoded JSON
    function generateTalkToURL(agentId, variables) {
      const baseURL = 'https://elevenlabs.io/app/talk-to';
      const encodedVars = btoa(JSON.stringify(variables));
      return `${baseURL}?agent_id=${agentId}&vars=${encodedVars}`;
    }

    // Method 2: Individual parameters
    function generateTalkToURLWithParams(agentId, variables) {
      const baseURL = 'https://elevenlabs.io/app/talk-to';
      const params = new URLSearchParams({ agent_id: agentId });

      Object.entries(variables).forEach(([key, value]) => {
        params.append(`var_${key}`, encodeURIComponent(value));
      });

      return `${baseURL}?${params.toString()}`;
    }

    // Usage
    const variables = {
      user_name: "John Doe",
      account_type: "premium",
      session_id: "sess_123"
    };

    const urlMethod1 = generateTalkToURL("your_agent_id", variables);
    const urlMethod2 = generateTalkToURLWithParams("your_agent_id", variables);
    ```

  </Tab>
  
  <Tab title="Python URL Generation">
    ```python
    import base64
    import json
    from urllib.parse import urlencode, quote

    def generate_talk_to_url(agent_id, variables):
        """Generate URL with base64-encoded variables"""
        base_url = "https://elevenlabs.io/app/talk-to"
        encoded_vars = base64.b64encode(json.dumps(variables).encode()).decode()
        return f"{base_url}?agent_id={agent_id}&vars={encoded_vars}"

    def generate_talk_to_url_with_params(agent_id, variables):
        """Generate URL with individual var_ parameters"""
        base_url = "https://elevenlabs.io/app/talk-to"
        params = {"agent_id": agent_id}

        for key, value in variables.items():
            params[f"var_{key}"] = value

        return f"{base_url}?{urlencode(params)}"

    # Usage
    variables = {
        "user_name": "John Doe",
        "account_type": "premium",
        "session_id": "sess_123"
    }

    url_method1 = generate_talk_to_url("your_agent_id", variables)
    url_method2 = generate_talk_to_url_with_params("your_agent_id", variables)
    ```

  </Tab>

  <Tab title="Manual URL Construction">
    ```
    # Base64-encoded method
    1. Create JSON: {"user_name": "John", "account_type": "premium"}
    2. Encode to base64: eyJ1c2VyX25hbWUiOiJKb2huIiwiYWNjb3VudF90eXBlIjoicHJlbWl1bSJ9
    3. Add to URL: https://elevenlabs.io/app/talk-to?agent_id=your_agent_id&vars=eyJ1c2VyX25hbWUiOiJKb2huIiwiYWNjb3VudF90eXBlIjoicHJlbWl1bSJ9

    # Individual parameters method
    1. Add each variable with var_ prefix
    2. URL encode values if needed
    3. Final URL: https://elevenlabs.io/app/talk-to?agent_id=your_agent_id&var_user_name=John&var_account_type=premium
    ```

  </Tab>
</Tabs>

## Supported Types

Dynamic variables support these value types:

<CardGroup cols={3}>
  <Card title="String">Text values</Card>
  <Card title="Number">Numeric values</Card>
  <Card title="Boolean">True/false values</Card>
</CardGroup>

## Troubleshooting

<AccordionGroup>
  <Accordion title="Variables not replacing">

    Verify that:

    - Variable names match exactly (case-sensitive)
    - Variables use double curly braces: `{{ variable_name }}`
    - Variables are included in your dynamic_variables object

  </Accordion>
  <Accordion title="Type errors">

    Ensure that:
    - Variable values match the expected type
    - Values are strings, numbers, or booleans only

  </Accordion>
</AccordionGroup>


---
title: Overrides
subtitle: Tailor each conversation with personalized context for each user.
---

<Warning>
  While overrides are still supported for completely replacing system prompts or first messages, we
  recommend using [Dynamic
  Variables](/docs/conversational-ai/customization/personalization/dynamic-variables) as the
  preferred way to customize your agent's responses and inject real-time data. Dynamic Variables
  offer better maintainability and a more structured approach to personalization.
</Warning>

**Overrides** enable your assistant to adapt its behavior for each user interaction. You can pass custom data and settings at the start of each conversation, allowing the assistant to personalize its responses and knowledge with real-time context. Overrides completely override the agent's default values defined in the agent's [dashboard](https://elevenlabs.io/app/conversational-ai/agents).

## Overview

Overrides allow you to modify your AI agent's behavior in real-time without creating multiple agents. This enables you to personalize responses with user-specific data.

Overrides can be enabled for the following fields in the agent's security settings:

- System prompt
- First message
- Language
- Voice ID

When overrides are enabled for a field, providing an override is still optional. If not provided, the agent will use the default values defined in the agent's [dashboard](https://elevenlabs.io/app/conversational-ai/agents). An error will be thrown if an override is provided for a field that does not have overrides enabled.

Here are a few examples where overrides can be useful:

- **Greet users** by their name
- **Include account-specific details** in responses
- **Adjust the agent's language** or tone based on user preferences
- **Pass real-time data** like account balances or order status

<Info>
  Overrides are particularly useful for applications requiring personalized interactions or handling
  sensitive user data that shouldn't be stored in the agent's base configuration.
</Info>

## Guide

### Prerequisites

- An [ElevenLabs account](https://elevenlabs.io)
- A configured ElevenLabs Conversational Agent ([create one here](/docs/conversational-ai/quickstart))

This guide will show you how to override the default agent **System prompt** & **First message**.

<Steps>
  <Step title="Enable overrides">
    For security reasons, overrides are disabled by default. Navigate to your agent's settings and
    select the **Security** tab. 
    
    Enable the `First message` and `System prompt` overrides.

    <Frame background="subtle">
      ![Enable overrides](file:a7608ac0-b7f1-4b46-b69d-871c56ef8a92)
    </Frame>

  </Step>

  <Step title="Override the conversation">
    In your code, where the conversation is started, pass the overrides as a parameter.

    <Tip>
      Ensure you have the latest [SDK](/docs/conversational-ai/libraries) installed.
    </Tip>

    <CodeGroup>

    ```python title="Python" focus={3-14} maxLines=14
    from elevenlabs.conversational_ai.conversation import Conversation, ConversationInitiationData
    ...
    conversation_override = {
        "agent": {
            "prompt": {
                "prompt": f"The customer's bank account balance is {customer_balance}. They are based in {customer_location}." # Optional: override the system prompt.
            },
            "first_message": f"Hi {customer_name}, how can I help you today?", # Optional: override the first_message.
            "language": "en" # Optional: override the language.
        },
        "tts": {
            "voice_id": "custom_voice_id" # Optional: override the voice.
        }
    }

    config = ConversationInitiationData(
        conversation_config_override=conversation_override
    )
    conversation = Conversation(
        ...
        config=config,
        ...
    )
    conversation.start_session()
    ```
    ```javascript title="JavaScript" focus={4-15} maxLines=15
    ...
    const conversation = await Conversation.startSession({
      ...
      overrides: {
          agent: {
              prompt: {
                  prompt: `The customer's bank account balance is ${customer_balance}. They are based in ${customer_location}.` // Optional: override the system prompt.
              },
              firstMessage: `Hi ${customer_name}, how can I help you today?`, // Optional: override the first message.
              language: "en" // Optional: override the language.
          },
          tts: {
              voiceId: "custom_voice_id" // Optional: override the voice.
          }
      },
      ...
    })
    ```

    ```swift title="Swift" focus={3-14} maxLines=14
    import ElevenLabsSDK

    let promptOverride = ElevenLabsSDK.AgentPrompt(
        prompt: "The customer's bank account balance is \(customer_balance). They are based in \(customer_location)." // Optional: override the system prompt.
    )
    let agentConfig = ElevenLabsSDK.AgentConfig(
        prompt: promptOverride, // Optional: override the system prompt.
        firstMessage: "Hi \(customer_name), how can I help you today?", // Optional: override the first message.
        language: .en // Optional: override the language.
    )
    let overrides = ElevenLabsSDK.ConversationConfigOverride(
        agent: agentConfig, // Optional: override agent settings.
        tts: TTSConfig(voiceId: "custom_voice_id") // Optional: override the voice.
    )

    let config = ElevenLabsSDK.SessionConfig(
        agentId: "",
        overrides: overrides
    )

    let conversation = try await ElevenLabsSDK.Conversation.startSession(
      config: config,
      callbacks: callbacks
    )
    ```

    ```html title="Widget"
      <elevenlabs-convai
        agent-id="your-agent-id"
        override-language="es"         <!-- Optional: override the language -->
        override-prompt="Custom system prompt for this user"  <!-- Optional: override the system prompt -->
        override-first-message="Hi! How can I help you today?"  <!-- Optional: override the first message -->
        override-voice-id="custom_voice_id"  <!-- Optional: override the voice -->
      ></elevenlabs-convai>
    ```

    </CodeGroup>

    <Note>
      When using overrides, omit any fields you don't want to override rather than setting them to empty strings or null values. Only include the fields you specifically want to customize.
    </Note>

  </Step>
</Steps>


---
title: Twilio personalization
subtitle: Configure personalization for incoming Twilio calls using webhooks.
---

## Overview

When receiving inbound Twilio calls, you can dynamically fetch conversation initiation data through a webhook. This allows you to customize your agent's behavior based on caller information and other contextual data.

<iframe
  width="100%"
  height="400"
  src="https://www.youtube-nocookie.com/embed/cAuSo8qNs-8"
  title="YouTube video player"
  frameborder="0"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
  allowfullscreen
></iframe>

## How it works

1. When a Twilio call is received, the ElevenLabs Conversational AI platform will make a webhook call to your specified endpoint, passing call information (`caller_id`, `agent_id`, `called_number`, `call_sid`) as arguments
2. Your webhook returns conversation initiation client data, including dynamic variables and overrides (an example is shown below)
3. This data is used to initiate the conversation

<Tip>

The system uses Twilio's connection/dialing period to fetch webhook data in parallel, creating a
seamless experience where:

- Users hear the expected telephone connection sound
- In parallel, theConversational AI platform fetches necessary webhook data
- The conversation is initiated with the fetched data by the time the audio connection is established

</Tip>

## Configuration

<Steps>

  <Step title="Configure webhook details">
    In the [settings page](https://elevenlabs.io/app/conversational-ai/settings) of the Conversational AI platform, configure the webhook URL and add any
    secrets needed for authentication.

    <Frame background="subtle">
        ![Enable webhook](file:e932ea4e-bc73-4869-899e-aa5a69d8399f)
    </Frame>

    Click on the webhook to modify which secrets are sent in the headers.

    <Frame background="subtle">
        ![Add secrets to headers](file:cf2b5cef-fc65-4b92-bf10-fadce656a972)
    </Frame>

  </Step>

  <Step title="Enable fetching conversation initiation data">
    In the "Security" tab of the [agent's page](https://elevenlabs.io/app/conversational-ai/agents/), enable fetching conversation initiation data for inbound Twilio calls, and define fields that can be overridden.

    <Frame background="subtle">
        ![Enable webhook](file:2dc96bab-9275-4091-a057-319bb61276d7)
    </Frame>

  </Step>

  <Step title="Implement the webhook endpoint to receive Twilio data">
    The webhook will receive a POST request with the following parameters:

    | Parameter       | Type   | Description                            |
    | --------------- | ------ | -------------------------------------- |
    | `caller_id`     | string | The phone number of the caller         |
    | `agent_id`      | string | The ID of the agent receiving the call |
    | `called_number` | string | The Twilio number that was called      |
    | `call_sid`      | string | Unique identifier for the Twilio call  |

  </Step>

  <Step title="Return conversation initiation client data">
   Your webhook must return a JSON response containing the initiation data for the agent.
  <Info>
    The `dynamic_variables` field must contain all dynamic variables defined for the agent. Overrides
    on the other hand are entirely optional. For more information about dynamic variables and
    overrides see the [dynamic variables](/docs/conversational-ai/customization/personalization/dynamic-variables) and
    [overrides](/docs/conversational-ai/customization/personalization/overrides) docs.
  </Info>

An example response could be:

```json
{
  "type": "conversation_initiation_client_data",
  "dynamic_variables": {
    "customer_name": "John Doe",
    "account_status": "premium",
    "last_interaction": "2024-01-15"
  },
  "conversation_config_override": {
    "agent": {
      "prompt": {
        "prompt": "The customer's bank account balance is $100. They are based in San Francisco."
      },
      "first_message": "Hi, how can I help you today?",
      "language": "en"
    },
    "tts": {
      "voice_id": "new-voice-id"
    }
  }
}
```

  </Step>
</Steps>

The Conversational AI platform will use the dynamic variables to populate the conversation initiation data, and the conversation will start smoothly.

<Warning>
  Ensure your webhook responds within a reasonable timeout period to avoid delaying the call
  handling.
</Warning>

## Security

- Use HTTPS endpoints only
- Implement authentication using request headers
- Store sensitive values as secrets through the [ElevenLabs secrets manager](https://elevenlabs.io/app/conversational-ai/settings)
- Validate the incoming request parameters


