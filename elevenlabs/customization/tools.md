---
title: Tools
subtitle: >-
  Enhance Conversational AI agents with custom functionalities and external
  integrations.
---

## Overview

Tools allow Conversational AI agents to perform actions beyond generating text responses.
They enable agents to interact with external systems, execute custom logic, or access specific functionalities during a conversation.
This allows for richer, more capable interactions tailored to specific use cases.

ElevenLabs Conversational AI supports the following kinds of tools:

<CardGroup cols={3}>
  <Card
    title="Client Tools"
    href="/conversational-ai/customization/tools/client-tools"
    icon="rectangle-code"
  >
    Tools executed directly on the client-side application (e.g., web browser, mobile app).
  </Card>
  <Card
    title="Server Tools"
    href="/conversational-ai/customization/tools/server-tools"
    icon="server"
  >
    Custom tools executed on your server-side infrastructure via API calls.
  </Card>
  <Card
    title="System Tools"
    href="/conversational-ai/customization/tools/system-tools"
    icon="computer-classic"
  >
    Built-in tools provided by the platform for common actions.
  </Card>
</CardGroup>

---
title: Client tools
subtitle: Empower your assistant to trigger client-side operations.
---

**Client tools** enable your assistant to execute client-side functions. Unlike [server-side tools](/docs/conversational-ai/customization/tools), client tools allow the assistant to perform actions such as triggering browser events, running client-side functions, or sending notifications to a UI.

## Overview

Applications may require assistants to interact directly with the user's environment. Client-side tools give your assistant the ability to perform client-side operations.

Here are a few examples where client tools can be useful:

- **Triggering UI events**: Allow an assistant to trigger browser events, such as alerts, modals or notifications.
- **Interacting with the DOM**: Enable an assistant to manipulate the Document Object Model (DOM) for dynamic content updates or to guide users through complex interfaces.

<Info>
  To perform operations server-side, use
  [server-tools](/docs/conversational-ai/customization/tools/server-tools) instead.
</Info>

## Guide

### Prerequisites

- An [ElevenLabs account](https://elevenlabs.io)
- A configured ElevenLabs Conversational Agent ([create one here](https://elevenlabs.io/app/conversational-ai))

<Steps>
  <Step title="Create a new client-side tool">
    Navigate to your agent dashboard. In the **Tools** section, click **Add Tool**. Ensure the **Tool Type** is set to **Client**. Then configure the following:

| Setting     | Parameter                                                        |
| ----------- | ---------------------------------------------------------------- |
| Name        | logMessage                                                       |
| Description | Use this client-side tool to log a message to the user's client. |

Then create a new parameter `message` with the following configuration:

| Setting     | Parameter                                                                          |
| ----------- | ---------------------------------------------------------------------------------- |
| Data Type   | String                                                                             |
| Identifier  | message                                                                            |
| Required    | true                                                                               |
| Description | The message to log in the console. Ensure the message is informative and relevant. |

    <Frame background="subtle">
      ![logMessage client-tool setup](file:6af1434c-df24-40de-91e7-3b56022af926)
    </Frame>

  </Step>

  <Step title="Register the client tool in your code">
    Unlike server-side tools, client tools need to be registered in your code.

    Use the following code to register the client tool:

    <CodeBlocks>

      ```python title="Python" focus={4-16}
      from elevenlabs import ElevenLabs
      from elevenlabs.conversational_ai.conversation import Conversation, ClientTools

      def log_message(parameters):
          message = parameters.get("message")
          print(message)

      client_tools = ClientTools()
      client_tools.register("logMessage", log_message)

      conversation = Conversation(
          client=ElevenLabs(api_key="your-api-key"),
          agent_id="your-agent-id",
          client_tools=client_tools,
          # ...
      )

      conversation.start_session()
      ```

      ```javascript title="JavaScript" focus={2-10}
      // ...
      const conversation = await Conversation.startSession({
        // ...
        clientTools: {
          logMessage: async ({message}) => {
            console.log(message);
          }
        },
        // ...
      });
      ```

      ```swift title="Swift" focus={2-10}
      // ...
      var clientTools = ElevenLabsSDK.ClientTools()

      clientTools.register("logMessage") { parameters async throws -> String? in
          guard let message = parameters["message"] as? String else {
              throw ElevenLabsSDK.ClientToolError.invalidParameters
          }
          print(message)
          return message
      }
      ```
    </CodeBlocks>

    <Note>
    The tool and parameter names in the agent configuration are case-sensitive and **must** match those registered in your code.
    </Note>

  </Step>

  <Step title="Testing">
    Initiate a conversation with your agent and say something like:

    > _Log a message to the console that says Hello World_

    You should see a `Hello World` log appear in your console.

  </Step>

  <Step title="Next steps">
    Now that you've set up a basic client-side event, you can:

    - Explore more complex client tools like opening modals, navigating to pages, or interacting with the DOM.
    - Combine client tools with server-side webhooks for full-stack interactions.
    - Use client tools to enhance user engagement and provide real-time feedback during conversations.

  </Step>
</Steps>

### Passing client tool results to the conversation context

When you want your agent to receive data back from a client tool, ensure that you tick the **Wait for response** option in the tool configuration.

<Frame background="subtle">
  <img
    src="file:983717bb-be09-4d55-bf49-391f8a2b1048"
    alt="Wait for response option in client tool configuration"
  />
</Frame>

Once the client tool is added, when the function is called the agent will wait for its response and append the response to the conversation context.

<CodeBlocks>
    ```python title="Python"
    def get_customer_details():
        # Fetch customer details (e.g., from an API or database)
        customer_data = {
            "id": 123,
            "name": "Alice",
            "subscription": "Pro"
        }
        # Return the customer data; it can also be a JSON string if needed.
        return customer_data

    client_tools = ClientTools()
    client_tools.register("getCustomerDetails", get_customer_details)

    conversation = Conversation(
        client=ElevenLabs(api_key="your-api-key"),
        agent_id="your-agent-id",
        client_tools=client_tools,
        # ...
    )

    conversation.start_session()
    ```

    ```javascript title="JavaScript"
    const clientTools = {
      getCustomerDetails: async () => {
        // Fetch customer details (e.g., from an API)
        const customerData = {
          id: 123,
          name: "Alice",
          subscription: "Pro"
        };
        // Return data directly to the agent.
        return customerData;
      }
    };

    // Start the conversation with client tools configured.
    const conversation = await Conversation.startSession({ clientTools });
    ```

</CodeBlocks>

In this example, when the agent calls **getCustomerDetails**, the function will execute on the client and the agent will receive the returned data, which is then used as part of the conversation context. The values from the response can also optionally be assigned to dynamic variables, similar to [server tools](https://elevenlabs.io/docs/conversational-ai/customization/tools/server-tools). Note system tools cannot update dynamic variables.

### Troubleshooting

<AccordionGroup>
  <Accordion title="Tools not being triggered">
  
    - Ensure the tool and parameter names in the agent configuration match those registered in your code.
    - View the conversation transcript in the agent dashboard to verify the tool is being executed.

  </Accordion>
  <Accordion title="Console errors">

    - Open the browser console to check for any errors.
    - Ensure that your code has necessary error handling for undefined or unexpected parameters.

  </Accordion>
</AccordionGroup>

## Best practices

<h4>Name tools intuitively, with detailed descriptions</h4>

If you find the assistant does not make calls to the correct tools, you may need to update your tool names and descriptions so the assistant more clearly understands when it should select each tool. Avoid using abbreviations or acronyms to shorten tool and argument names.

You can also include detailed descriptions for when a tool should be called. For complex tools, you should include descriptions for each of the arguments to help the assistant know what it needs to ask the user to collect that argument.

<h4>Name tool parameters intuitively, with detailed descriptions</h4>

Use clear and descriptive names for tool parameters. If applicable, specify the expected format for a parameter in the description (e.g., YYYY-mm-dd or dd/mm/yy for a date).

<h4>
  Consider providing additional information about how and when to call tools in your assistant's
  system prompt
</h4>

Providing clear instructions in your system prompt can significantly improve the assistant's tool calling accuracy. For example, guide the assistant with instructions like the following:

```plaintext
Use `check_order_status` when the user inquires about the status of their order, such as 'Where is my order?' or 'Has my order shipped yet?'.
```

Provide context for complex scenarios. For example:

```plaintext
Before scheduling a meeting with `schedule_meeting`, check the user's calendar for availability using check_availability to avoid conflicts.
```

<h4>LLM selection</h4>

<Warning>
  When using tools, we recommend picking high intelligence models like GPT-4o mini or Claude 3.5
  Sonnet and avoiding Gemini 1.5 Flash.
</Warning>

It's important to note that the choice of LLM matters to the success of function calls. Some LLMs can struggle with extracting the relevant parameters from the conversation.



---
title: Server tools
subtitle: Connect your assistant to external data & systems.
---

**Tools** enable your assistant to connect to external data and systems. You can define a set of tools that the assistant has access to, and the assistant will use them where appropriate based on the conversation.

## Overview

Many applications require assistants to call external APIs to get real-time information. Tools give your assistant the ability to make external function calls to third party apps so you can get real-time information.

Here are a few examples where tools can be useful:

- **Fetching data**: enable an assistant to retrieve real-time data from any REST-enabled database or 3rd party integration before responding to the user.
- **Taking action**: allow an assistant to trigger authenticated actions based on the conversation, like scheduling meetings or initiating order returns.

<Info>
  To interact with Application UIs or trigger client-side events use [client
  tools](/docs/conversational-ai/customization/tools/client-tools) instead.
</Info>

## Tool configuration

Conversational AI assistants can be equipped with tools to interact with external APIs. Unlike traditional requests, the assistant generates query, body, and path parameters dynamically based on the conversation and parameter descriptions you provide.

All tool configurations and parameter descriptions help the assistant determine **when** and **how** to use these tools. To orchestrate tool usage effectively, update the assistant’s system prompt to specify the sequence and logic for making these calls. This includes:

- **Which tool** to use and under what conditions.
- **What parameters** the tool needs to function properly.
- **How to handle** the responses.

<br />

<Tabs>

<Tab title="Configuration">
Define a high-level `Name` and `Description` to describe the tool's purpose. This helps the LLM understand the tool and know when to call it.

<Info>
  If the API requires path parameters, include variables in the URL path by wrapping them in curly
  braces `{}`, for example: `/api/resource/{id}` where `id` is a path parameter.
</Info>

<Frame background="subtle">
  ![Configuration](file:84d88518-df29-4924-96b4-da25e8582dc1)
</Frame>

</Tab>

<Tab title="Authentication">

Configure authentication by adding custom headers or using out-of-the-box authentication methods through auth connections.

<Frame background="subtle">
  ![Tool authentication](file:3640ea6d-333b-4651-b439-45ee6d26b2e0)
</Frame>

</Tab>

<Tab title="Headers">

Specify any headers that need to be included in the request.

<Frame background="subtle">![Headers](file:898aef83-635b-457d-a2a8-c7248066ee82)</Frame>

</Tab>

<Tab title="Path parameters">

Include variables in the URL path by wrapping them in curly braces `{}`:

- **Example**: `/api/resource/{id}` where `id` is a path parameter.

<Frame background="subtle">
  ![Path parameters](file:66e5c888-bc8d-4c10-82ab-ecc687869ffa)
</Frame>

</Tab>

<Tab title="Body parameters">

Specify any body parameters to be included in the request.

<Frame background="subtle">
  ![Body parameters](file:c2627a99-5ab3-4af0-b79b-7e5bf542492e)
</Frame>

</Tab>

<Tab title="Query parameters">

Specify any query parameters to be included in the request.

<Frame background="subtle">
  ![Query parameters](file:71befc80-68d3-4ff0-8fba-cc40c6c44ae1)
</Frame>

</Tab>

<Tab title="Dynamic variable assignment">

Specify dynamic variables to update from the tool response for later use in the conversation.

<Frame background="subtle">
  ![Query parameters](file:c7250859-0ab8-452a-8adf-a893086825ae)
</Frame>

</Tab>

</Tabs>

## Guide

In this guide, we'll create a weather assistant that can provide real-time weather information for any location. The assistant will use its geographic knowledge to convert location names into coordinates and fetch accurate weather data.

<div style="padding:104.25% 0 0 0;position:relative;">
  <iframe
    src="https://player.vimeo.com/video/1061374724?h=bd9bdb535e&amp;badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479"
    frameborder="0"
    allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media"
    style="position:absolute;top:0;left:0;width:100%;height:100%;"
    title="weatheragent"
  ></iframe>
</div>
<script src="https://player.vimeo.com/api/player.js"></script>

<Steps>
  <Step title="Configure the weather tool">
    First, on the **Agent** section of your agent settings page, choose **Add Tool**. Select **Webhook** as the Tool Type, then configure the weather API integration:

    <AccordionGroup>
      <Accordion title="Weather Tool Configuration">

      <Tabs>
        <Tab title="Configuration">

        | Field       | Value                                                                                                                                                                            |
        | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
        | Name        | get_weather                                                                                                                                                                      |
        | Description | Gets the current weather forecast for a location                                                                                                                                 |
        | Method      | GET                                                                                                                                                                              |
        | URL         | https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m |

        </Tab>

        <Tab title="Path Parameters">

        | Data Type | Identifier | Value Type | Description                                         |
        | --------- | ---------- | ---------- | --------------------------------------------------- |
        | string    | latitude   | LLM Prompt | The latitude coordinate for the requested location  |
        | string    | longitude  | LLM Prompt | The longitude coordinate for the requested location |

        </Tab>

      </Tabs>

      </Accordion>
    </AccordionGroup>

    <Warning>
      An API key is not required for this tool. If one is required, this should be passed in the headers and stored as a secret.
    </Warning>

  </Step>

  <Step title="Orchestration">
    Configure your assistant to handle weather queries intelligently with this system prompt:

    ```plaintext System prompt
    You are a helpful conversational AI assistant with access to a weather tool. When users ask about
    weather conditions, use the get_weather tool to fetch accurate, real-time data. The tool requires
    a latitude and longitude - use your geographic knowledge to convert location names to coordinates
    accurately.

    Never ask users for coordinates - you must determine these yourself. Always report weather
    information conversationally, referring to locations by name only. For weather requests:

    1. Extract the location from the user's message
    2. Convert the location to coordinates and call get_weather
    3. Present the information naturally and helpfully

    For non-weather queries, provide friendly assistance within your knowledge boundaries. Always be
    concise, accurate, and helpful.

    First message: "Hey, how can I help you today?"
    ```

    <Success>
      Test your assistant by asking about the weather in different locations. The assistant should
      handle specific locations ("What's the weather in Tokyo?") and ask for clarification after general queries ("How's
      the weather looking today?").
    </Success>

  </Step>
</Steps>

## Supported Authentication Methods

Conversational AI supports multiple authentication methods to securely connect your tools with external APIs. Authentication methods are configured in your agent settings and then connected to individual tools as needed.

<Frame background="subtle">
  ![Workspace Auth Connection](file:0259e719-abcf-4385-a37e-c6bc0567f066)
</Frame>

Once configured, you can connect these authentication methods to your tools and manage custom headers in the tool configuration:

<Frame background="subtle">
  ![Tool Auth Connection](file:3398c8ea-aa51-431f-9970-7042f34ddda3)
</Frame>

#### OAuth2 Client Credentials

Automatically handles the OAuth2 client credentials flow. Configure with your client ID, client secret, and token URL (e.g., `https://api.example.com/oauth/token`). Optionally specify scopes as comma-separated values and additional JSON parameters. Set up by clicking **Add Auth** on **Workspace Auth Connections** on the **Agent** section of your agent settings page.

#### OAuth2 JWT

Uses JSON Web Token authentication for OAuth 2.0 JWT Bearer flow. Requires your JWT signing secret, token URL, and algorithm (default: HS256). Configure JWT claims including issuer, audience, and subject. Optionally set key ID, expiration (default: 3600 seconds), scopes, and extra parameters. Set up by clicking **Add Auth** on **Workspace Auth Connections** on the **Agent** section of your agent settings page.

#### Basic Authentication

Simple username and password authentication for APIs that support HTTP Basic Auth. Set up by clicking **Add Auth** on **Workspace Auth Connections** in the **Agent** section of your agent settings page.

#### Bearer Tokens

Token-based authentication that adds your bearer token value to the request header. Configure by adding a header to the tool configuration, selecting **Secret** as the header type, and clicking **Create New Secret**.

#### Custom Headers

Add custom authentication headers with any name and value for proprietary authentication methods. Configure by adding a header to the tool configuration and specifying its **name** and **value**.

## Best practices

<h4>Name tools intuitively, with detailed descriptions</h4>

If you find the assistant does not make calls to the correct tools, you may need to update your tool names and descriptions so the assistant more clearly understands when it should select each tool. Avoid using abbreviations or acronyms to shorten tool and argument names.

You can also include detailed descriptions for when a tool should be called. For complex tools, you should include descriptions for each of the arguments to help the assistant know what it needs to ask the user to collect that argument.

<h4>Name tool parameters intuitively, with detailed descriptions</h4>

Use clear and descriptive names for tool parameters. If applicable, specify the expected format for a parameter in the description (e.g., YYYY-mm-dd or dd/mm/yy for a date).

<h4>
  Consider providing additional information about how and when to call tools in your assistant's
  system prompt
</h4>

Providing clear instructions in your system prompt can significantly improve the assistant's tool calling accuracy. For example, guide the assistant with instructions like the following:

```plaintext
Use `check_order_status` when the user inquires about the status of their order, such as 'Where is my order?' or 'Has my order shipped yet?'.
```

Provide context for complex scenarios. For example:

```plaintext
Before scheduling a meeting with `schedule_meeting`, check the user's calendar for availability using check_availability to avoid conflicts.
```

<h4>LLM selection</h4>

<Warning>
  When using tools, we recommend picking high intelligence models like GPT-4o mini or Claude 3.5
  Sonnet and avoiding Gemini 1.5 Flash.
</Warning>

It's important to note that the choice of LLM matters to the success of function calls. Some LLMs can struggle with extracting the relevant parameters from the conversation.



---
title: Agent tools deprecation
subtitle: Migrate from legacy `prompt.tools` to the new `prompt.tool_ids` field.
---

## Overview

<Info>The way you wire tools into your ConvAI agents is getting a refresh.</Info>

### What's changing?

- The old request field `body.conversation_config.agent.prompt.tools` is **deprecated**.
- Use `body.conversation_config.agent.prompt.tool_ids` to list the IDs of the client or server tools your agent should use.
- **New field** `prompt.built_in_tools` is introduced for **system tools** (e.g., `end_call`, `language_detection`). These tools are referenced by **name**, not by ID.

### Critical deadlines

<Check>
  **July 14, 2025** - Last day for full backwards compatibility. You can continue using
  `prompt.tools` until this date.
</Check>

<Note>
  **July 15, 2025** - GET endpoints will stop returning the `tools` field. Only `prompt.tool_ids`
  will be included in responses.
</Note>

<Warning>
  **July 23, 2025** - Legacy `prompt.tools` field will be permanently removed. All requests
  containing this field will be rejected.
</Warning>

## Why the change?

Decoupling tools from agents brings several advantages:

- **Re-use** – the same tool can be shared across multiple agents.
- **Simpler audits** – inspect, update or delete a tool in one place.
- **Cleaner payloads** – agent configurations stay lightweight.

## What has already happened?

<Check>
  Good news — we've already migrated your data! Every tool that previously lived in `prompt.tools`
  now exists as a standalone record, and its ID is present in the agent's `prompt.tool_ids` array.
  No scripts required.
</Check>

We have **automatically migrated all existing data**:

- Every tool that was previously in an agent's `prompt.tools` array now exists as a standalone record.
- The agent's `prompt.tool_ids` array already references those new tool records.

No one-off scripts are required — your agents continue to work unchanged.

## Deprecation timeline

| Date              | Status                   | Behaviour                                                                        |
| ----------------- | ------------------------ | -------------------------------------------------------------------------------- |
| **July 14, 2025** | ✅ Full compatibility    | You may keep sending `prompt.tools`. GET responses include the `tools` field.    |
| **July 15, 2025** | ⚠️ Partial compatibility | GET endpoints stop returning the `tools` field. Only `prompt.tool_ids` included. |
| **July 23, 2025** | ❌ No compatibility      | POST and PATCH endpoints **reject** any request containing `prompt.tools`.       |

## Toolbox endpoint

All tool management lives under a dedicated endpoint:

```http title="Tool management"
POST | GET | PATCH | DELETE  https://api.elevenlabs.io/v1/convai/tools
```

Use it to:

- **Create** a tool and obtain its ID.
- **Update** it when requirements change.
- **Delete** it when it is no longer needed.

Anything that once sat in the old `tools` array now belongs here.

## Migration guide

<Error>
  System tools are **not** supported in `prompt.tool_ids`. Instead, specify them in the **new**
  `prompt.built_in_tools` field.
</Error>

If you are still using the legacy field, follow the steps below.

<Steps>
  ### 1. Stop sending `prompt.tools`
  Remove the `tools` array from your agent configuration.

### 2. Send the tool IDs instead

Replace it with `prompt.tool_ids`, containing the IDs of the client or server tools the agent
should use.

### 3. (Optional) Clean up

After 23 July, delete any unused standalone tools via the toolbox endpoint.

</Steps>

## Example payloads

<Note>
  A request must include **either** `prompt.tool_ids` **or** the legacy `prompt.tools` array —
  **never both**. Sending both fields results in an error.
</Note>

<CodeBlocks>
```json title="Legacy format (deprecated)"
{
  "conversation_config": {
    "agent": {
      "prompt": {
        "tools": [
          {
            "type": "client", 
            "name": "open_url",
            "description": "Open a provided URL in the user's browser."
          },
          {
            "type": "system",
            "name": "end_call", 
            "description": "",
            "response_timeout_secs": 20,
            "params": {
              "system_tool_type": "end_call"
            }
          }
        ]
      }
    }
  }
}
```

```json title="New format (recommended) – client tool via ID + system tool"
{
  "conversation_config": {
    "agent": {
      "prompt": {
        "tool_ids": ["tool_123456789abcdef0"],
        "built_in_tools": {
          "end_call": {
            "name": "end_call",
            "description": "",
            "response_timeout_secs": 20,
            "type": "system",
            "params": {
              "system_tool_type": "end_call"
            }
          },
          "language_detection": null,
          "transfer_to_agent": null,
          "transfer_to_number": null,
          "skip_turn": null
        }
      }
    }
  }
}
```

</CodeBlocks>

## FAQ

<AccordionGroup>
  <Accordion title="Will my existing integrations break?">
    No. Until July 23, the API will silently migrate any `prompt.tools` array you send. However,
    starting July 15, GET and PATCH responses will no longer include full tool objects. After July
    23, any POST/PATCH requests containing `prompt.tools` will be rejected.
  </Accordion>
  <Accordion title="Can I mix both fields in one request?">
    No. A request must use **either** `prompt.tool_ids` **or** `prompt.tools` — never both.
  </Accordion>
  <Accordion title="How do I find a tool's ID?">
    List your tools via `GET /v1/convai/tools` or inspect the response when you create one.
  </Accordion>
</AccordionGroup>


---
title: System tools
subtitle: Update the internal state of conversations without external requests.
---

**System tools** enable your assistant to update the internal state of a conversation. Unlike [server tools](/docs/conversational-ai/customization/tools/server-tools) or [client tools](/docs/conversational-ai/customization/tools/client-tools), system tools don't make external API calls or trigger client-side functions—they modify the internal state of the conversation without making external calls.

## Overview

Some applications require agents to control the flow or state of a conversation.
System tools provide this capability by allowing the assistant to perform actions related to the state of the call that don't require communicating with external servers or the client.

### Available system tools

<CardGroup cols={2}>
  <Card
    title="End call"
    icon="duotone square-phone-hangup"
    href="/docs/conversational-ai/customization/tools/system-tools/end-call"
  >
    Let your agent automatically terminate a conversation when appropriate conditions are met.
  </Card>
  <Card
    title="Language detection"
    icon="duotone earth-europe"
    href="/docs/conversational-ai/customization/tools/system-tools/language-detection"
  >
    Enable your agent to automatically switch to the user's language during conversations.
  </Card>
  <Card
    title="Agent transfer"
    icon="duotone arrow-right-arrow-left"
    href="/docs/conversational-ai/customization/tools/system-tools/agent-transfer"
  >
    Seamlessly transfer conversations between AI agents based on defined conditions.
  </Card>
  <Card
    title="Transfer to human"
    icon="duotone user-headset"
    href="/docs/conversational-ai/customization/tools/system-tools/transfer-to-human"
  >
    Seamlessly transfer the user to a human operator.
  </Card>
  <Card
    title="Skip turn"
    icon="duotone forward"
    href="/docs/conversational-ai/customization/tools/system-tools/skip-turn"
  >
    Enable the agent to skip their turns if the LLM detects the agent should not speak yet.
  </Card>
  <Card
    title="Play keypad touch tone"
    icon="duotone phone-office"
    href="/docs/conversational-ai/customization/tools/system-tools/play-keypad-touch-tone"
  >
    Enable agents to play DTMF tones to interact with automated phone systems and navigate menus.
  </Card>
  <Card
    title="Voicemail detection"
    icon="duotone voicemail"
    href="/docs/conversational-ai/customization/tools/system-tools/voicemail-detection"
  >
    Enable agents to automatically detect voicemail systems and optionally leave messages.
  </Card>
</CardGroup>

## Implementation

When creating an agent via API, you can add system tools to your agent configuration. Here's how to implement both the end call and language detection tools:

## Custom LLM integration

When using a custom LLM with ElevenLabs agents, system tools are exposed as function definitions that your LLM can call. Each system tool has specific parameters and trigger conditions:

### Available system tools

<AccordionGroup>
  <Accordion title="End call">
    ## Custom LLM integration
    
    **Purpose**: Automatically terminate conversations when appropriate conditions are met.
    
    **Trigger conditions**: The LLM should call this tool when:
    
    - The main task has been completed and user is satisfied
    - The conversation reached natural conclusion with mutual agreement
    - The user explicitly indicates they want to end the conversation
    
    **Parameters**:
    
    - `reason` (string, required): The reason for ending the call
    - `message` (string, optional): A farewell message to send to the user before ending the call
    
    **Function call format**:
    
    ```json
    {
      "type": "function",
      "function": {
        "name": "end_call",
        "arguments": "{\"reason\": \"Task completed successfully\", \"message\": \"Thank you for using our service. Have a great day!\"}"
      }
    }
    ```
    
    **Implementation**: Configure as a system tool in your agent settings. The LLM will receive detailed instructions about when to call this function.
    

    Learn more: [End call tool](/docs/conversational-ai/customization/tools/end-call)

  </Accordion>

  <Accordion title="Language detection">
    ## Custom LLM integration
    
    **Purpose**: Automatically switch to the user's detected language during conversations.
    
    **Trigger conditions**: The LLM should call this tool when:
    
    - User speaks in a different language than the current conversation language
    - User explicitly requests to switch languages
    - Multi-language support is needed for the conversation
    
    **Parameters**:
    
    - `reason` (string, required): The reason for the language switch
    - `language` (string, required): The language code to switch to (must be in supported languages list)
    
    **Function call format**:
    
    ```json
    {
      "type": "function",
      "function": {
        "name": "language_detection",
        "arguments": "{\"reason\": \"User requested Spanish\", \"language\": \"es\"}"
      }
    }
    ```
    
    **Implementation**: Configure supported languages in agent settings and add the language detection system tool. The agent will automatically switch voice and responses to match detected languages.
    

    Learn more: [Language detection tool](/docs/conversational-ai/customization/tools/language-detection)

  </Accordion>

  <Accordion title="Agent transfer">
    ## Custom LLM integration
    
    **Purpose**: Transfer conversations between specialized AI agents based on user needs.
    
    **Trigger conditions**: The LLM should call this tool when:
    
    - User request requires specialized knowledge or different agent capabilities
    - Current agent cannot adequately handle the query
    - Conversation flow indicates need for different agent type
    
    **Parameters**:
    
    - `reason` (string, optional): The reason for the agent transfer
    - `agent_number` (integer, required): Zero-indexed number of the agent to transfer to (based on configured transfer rules)
    
    **Function call format**:
    
    ```json
    {
      "type": "function",
      "function": {
        "name": "transfer_to_agent",
        "arguments": "{\"reason\": \"User needs billing support\", \"agent_number\": 0}"
      }
    }
    ```
    
    **Implementation**: Define transfer rules mapping conditions to specific agent IDs. Configure which agents the current agent can transfer to. Agents are referenced by zero-indexed numbers in the transfer configuration.
    

    Learn more: [Agent transfer tool](/docs/conversational-ai/customization/tools/agent-transfer)

  </Accordion>

  <Accordion title="Transfer to human">
    ## Custom LLM integration
    
    **Purpose**: Seamlessly hand off conversations to human operators when AI assistance is insufficient.
    
    **Trigger conditions**: The LLM should call this tool when:
    
    - Complex issues requiring human judgment
    - User explicitly requests human assistance
    - AI reaches limits of capability for the specific request
    - Escalation protocols are triggered
    
    **Parameters**:
    
    - `reason` (string, optional): The reason for the transfer
    - `transfer_number` (string, required): The phone number to transfer to (must match configured numbers)
    - `client_message` (string, required): Message read to the client while waiting for transfer
    - `agent_message` (string, required): Message for the human operator receiving the call
    
    **Function call format**:
    
    ```json
    {
      "type": "function",
      "function": {
        "name": "transfer_to_number",
        "arguments": "{\"reason\": \"Complex billing issue\", \"transfer_number\": \"+15551234567\", \"client_message\": \"I'm transferring you to a billing specialist who can help with your account.\", \"agent_message\": \"Customer has a complex billing dispute about order #12345 from last month.\"}"
      }
    }
    ```
    
    **Implementation**: Configure transfer phone numbers and conditions. Define messages for both customer and receiving human operator. Works with both Twilio and SIP trunking.
    

    Learn more: [Transfer to human tool](/docs/conversational-ai/customization/tools/human-transfer)

  </Accordion>

  <Accordion title="Skip turn">
    ## Custom LLM integration
    
    **Purpose**: Allow the agent to pause and wait for user input without speaking.
    
    **Trigger conditions**: The LLM should call this tool when:
    
    - User indicates they need a moment ("Give me a second", "Let me think")
    - User requests pause in conversation flow
    - Agent detects user needs time to process information
    
    **Parameters**:
    
    - `reason` (string, optional): Free-form reason explaining why the pause is needed
    
    **Function call format**:
    
    ```json
    {
      "type": "function",
      "function": {
        "name": "skip_turn",
        "arguments": "{\"reason\": \"User requested time to think\"}"
      }
    }
    ```
    
    **Implementation**: No additional configuration needed. The tool simply signals the agent to remain silent until the user speaks again.
    

    Learn more: [Skip turn tool](/docs/conversational-ai/customization/tools/skip-turn)

  </Accordion>

  <Accordion title="Play keypad touch tone">
    ## Custom LLM integration
    
    **Parameters**:
    
    - `reason` (string, optional): The reason for playing the DTMF tones (e.g., "navigating to extension", "entering PIN")
    - `dtmf_tones` (string, required): The DTMF sequence to play. Valid characters: 0-9, \*, #, w (0.5s pause), W (1s pause)
    
    **Function call format**:
    
    ```json
    {
      "type": "function",
      "function": {
        "name": "play_keypad_touch_tone",
        "arguments": "{"reason": "Navigating to customer service", "dtmf_tones": "2"}"
      }
    }
    ```
    

    Learn more: [Play keypad touch tone tool](/docs/conversational-ai/customization/tools/play-keypad-touch-tone)

  </Accordion>

  <Accordion title="Voicemail detection">
    ## Custom LLM integration
    
    **Parameters**:
    
    - `reason` (string, required): The reason for detecting voicemail (e.g., "automated greeting detected", "no human response")
    
    **Function call format**:
    
    ```json
    {
      "type": "function",
      "function": {
        "name": "voicemail_detection",
        "arguments": "{\"reason\": \"Automated greeting detected with request to leave message\"}"
      }
    }
    ```
    

    Learn more: [Voicemail detection tool](/docs/conversational-ai/customization/tools/voicemail-detection)

  </Accordion>
</AccordionGroup>

<CodeGroup>

```python
from elevenlabs import (
    ConversationalConfig,
    ElevenLabs,
    AgentConfig,
    PromptAgent,
    PromptAgentInputToolsItem_System,
)

# Initialize the client
elevenlabs = ElevenLabs(api_key="YOUR_API_KEY")

# Create system tools
end_call_tool = PromptAgentInputToolsItem_System(
    name="end_call",
    description=""  # Optional: Customize when the tool should be triggered
)

language_detection_tool = PromptAgentInputToolsItem_System(
    name="language_detection",
    description=""  # Optional: Customize when the tool should be triggered
)

# Create the agent configuration with both tools
conversation_config = ConversationalConfig(
    agent=AgentConfig(
        prompt=PromptAgent(
            tools=[end_call_tool, language_detection_tool]
        )
    )
)

# Create the agent
response = elevenlabs.conversational_ai.agents.create(
    conversation_config=conversation_config
)
```

```javascript
import { ElevenLabs } from '@elevenlabs/elevenlabs-js';

// Initialize the client
const elevenlabs = new ElevenLabs({
  apiKey: 'YOUR_API_KEY',
});

// Create the agent with system tools
await elevenlabs.conversationalAi.agents.create({
  conversationConfig: {
    agent: {
      prompt: {
        tools: [
          {
            type: 'system',
            name: 'end_call',
            description: '',
          },
          {
            type: 'system',
            name: 'language_detection',
            description: '',
          },
        ],
      },
    },
  },
});
```

</CodeGroup>

## FAQ

<AccordionGroup>
  <Accordion title="Can system tools be combined with other tool types?">
    Yes, system tools can be used alongside server tools and client tools in the same assistant.
    This allows for comprehensive functionality that combines internal state management with
    external interactions.
  </Accordion>
</AccordionGroup>
```


---
title: End call
subtitle: Let your agent automatically hang up on the user.
---

<Warning>
  The **End Call** tool is added to agents created in the ElevenLabs dashboard by default. For
  agents created via API or SDK, if you would like to enable the End Call tool, you must add it
  manually as a system tool in your agent configuration. [See API Implementation
  below](#api-implementation) for details.
</Warning>

<Frame background="subtle">![End call](file:2d674283-0f4e-41c2-a4a8-16a4a153b866)</Frame>

## Overview

The **End Call** tool allows your conversational agent to terminate a call with the user. This is a system tool that provides flexibility in how and when calls are ended.

## Functionality

- **Default behavior**: The tool can operate without any user-defined prompts, ending the call when the conversation naturally concludes.
- **Custom prompts**: Users can specify conditions under which the call should end. For example:
  - End the call if the user says "goodbye."
  - Conclude the call when a specific task is completed.

## Custom LLM integration

**Purpose**: Automatically terminate conversations when appropriate conditions are met.

**Trigger conditions**: The LLM should call this tool when:

- The main task has been completed and user is satisfied
- The conversation reached natural conclusion with mutual agreement
- The user explicitly indicates they want to end the conversation

**Parameters**:

- `reason` (string, required): The reason for ending the call
- `message` (string, optional): A farewell message to send to the user before ending the call

**Function call format**:

```json
{
  "type": "function",
  "function": {
    "name": "end_call",
    "arguments": "{\"reason\": \"Task completed successfully\", \"message\": \"Thank you for using our service. Have a great day!\"}"
  }
}
```

**Implementation**: Configure as a system tool in your agent settings. The LLM will receive detailed instructions about when to call this function.


### API Implementation

When creating an agent via API, you can add the End Call tool to your agent configuration. It should be defined as a system tool:

<CodeBlocks>

```python
from elevenlabs import (
    ConversationalConfig,
    ElevenLabs,
    AgentConfig,
    PromptAgent,
    PromptAgentInputToolsItem_System
)

# Initialize the client
elevenlabs = ElevenLabs(api_key="YOUR_API_KEY")

# Create the end call tool
end_call_tool = PromptAgentInputToolsItem_System(
    name="end_call",
    description=""  # Optional: Customize when the tool should be triggered
)

# Create the agent configuration
conversation_config = ConversationalConfig(
    agent=AgentConfig(
        prompt=PromptAgent(
            tools=[end_call_tool]
        )
    )
)

# Create the agent
response = elevenlabs.conversational_ai.agents.create(
    conversation_config=conversation_config
)
```

```javascript
import { ElevenLabs } from '@elevenlabs/elevenlabs-js';

// Initialize the client
const elevenlabs = new ElevenLabs({
  apiKey: 'YOUR_API_KEY',
});

// Create the agent with end call tool
await elevenlabs.conversationalAi.agents.create({
  conversationConfig: {
    agent: {
      prompt: {
        tools: [
          {
            type: 'system',
            name: 'end_call',
            description: '', // Optional: Customize when the tool should be triggered
          },
        ],
      },
    },
  },
});
```

```bash
curl -X POST https://api.elevenlabs.io/v1/convai/agents/create \
     -H "xi-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
  "conversation_config": {
    "agent": {
      "prompt": {
        "tools": [
          {
            "type": "system",
            "name": "end_call",
            "description": ""
          }
        ]
      }
    }
  }
}'
```

</CodeBlocks>

<Tip>Leave the description blank to use the default end call prompt.</Tip>

## Example prompts

**Example 1: Basic End Call**

```
End the call when the user says goodbye, thank you, or indicates they have no more questions.
```

**Example 2: End Call with Custom Prompt**

```
End the call when the user says goodbye, thank you, or indicates they have no more questions. You can only end the call after all their questions have been answered. Please end the call only after confirming that the user doesn't need any additional assistance.
```


---
title: Language detection
subtitle: Let your agent automatically switch to the language
---

## Overview

The `language detection` system tool allows your Conversational AI agent to switch its output language to any the agent supports.
This system tool is not enabled automatically. Its description can be customized to accommodate your specific use case.

<iframe
  width="100%"
  height="400"
  src="https://www.youtube-nocookie.com/embed/YhF2gKv9ozc"
  title="YouTube video player"
  frameborder="0"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
  allowfullscreen
></iframe>

<Note>
  Where possible, we recommend enabling all languages for an agent and enabling the language
  detection system tool.
</Note>

Our language detection tool triggers language switching in two cases, both based on the received audio's detected language and content:

- `detection` if a user speaks a different language than the current output language, a switch will be triggered
- `content` if the user asks in the current language to change to a new language, a switch will be triggered

## Custom LLM integration

**Purpose**: Automatically switch to the user's detected language during conversations.

**Trigger conditions**: The LLM should call this tool when:

- User speaks in a different language than the current conversation language
- User explicitly requests to switch languages
- Multi-language support is needed for the conversation

**Parameters**:

- `reason` (string, required): The reason for the language switch
- `language` (string, required): The language code to switch to (must be in supported languages list)

**Function call format**:

```json
{
  "type": "function",
  "function": {
    "name": "language_detection",
    "arguments": "{\"reason\": \"User requested Spanish\", \"language\": \"es\"}"
  }
}
```

**Implementation**: Configure supported languages in agent settings and add the language detection system tool. The agent will automatically switch voice and responses to match detected languages.


## Enabling language detection

<Steps>
    <Step title="Configure supported languages">
        The languages that the agent can switch to must be defined in the `Agent` settings tab.

        <Frame background="subtle">
            ![Agent languages](file:823c27a0-db97-4c99-a351-3fbfaebb83b4)
        </Frame>
    </Step>

    <Step title="Add the language detection tool">
        Enable language detection by selecting the pre-configured system tool to your agent's tools in the `Agent` tab.
        This is automatically available as an option when selecting `add tool`.

        <Frame background="subtle">
            ![System tool](file:7575b982-36f8-47df-9e6c-ae6f0ec8c29a)
        </Frame>
    </Step>

    <Step title="Configure tool description">
        Add a description that specifies when to call the tool

        <Frame background="subtle">
            ![Description](file:a252ed05-28c0-4ef2-ae20-5229c3cc310e)
        </Frame>
    </Step>

</Steps>

### API Implementation

When creating an agent via API, you can add the `language detection` tool to your agent configuration. It should be defined as a system tool:

<CodeBlocks>

```python
from elevenlabs import (
    ConversationalConfig,
    ElevenLabs,
    AgentConfig,
    PromptAgent,
    PromptAgentInputToolsItem_System,
    LanguagePresetInput,
    ConversationConfigClientOverrideInput,
    AgentConfigOverride,
)

# Initialize the client
elevenlabs = ElevenLabs(api_key="YOUR_API_KEY")

# Create the language detection tool
language_detection_tool = PromptAgentInputToolsItem_System(
    name="language_detection",
    description=""  # Optional: Customize when the tool should be triggered
)

# Create language presets
language_presets = {
    "nl": LanguagePresetInput(
        overrides=ConversationConfigClientOverrideInput(
            agent=AgentConfigOverride(
                prompt=None,
                first_message="Hoi, hoe gaat het met je?",
                language=None
            ),
            tts=None
        ),
        first_message_translation=None
    ),
    "fi": LanguagePresetInput(
        overrides=ConversationConfigClientOverrideInput(
            agent=AgentConfigOverride(
                first_message="Hei, kuinka voit?",
            ),
            tts=None
        ),
    ),
    "tr": LanguagePresetInput(
        overrides=ConversationConfigClientOverrideInput(
            agent=AgentConfigOverride(
                prompt=None,
                first_message="Merhaba, nasılsın?",
                language=None
            ),
            tts=None
        ),
    ),
    "ru": LanguagePresetInput(
        overrides=ConversationConfigClientOverrideInput(
            agent=AgentConfigOverride(
                prompt=None,
                first_message="Привет, как ты?",
                language=None
            ),
            tts=None
        ),
    ),
    "pt": LanguagePresetInput(
        overrides=ConversationConfigClientOverrideInput(
            agent=AgentConfigOverride(
                prompt=None,
                first_message="Oi, como você está?",
                language=None
            ),
            tts=None
        ),
    )
}

# Create the agent configuration
conversation_config = ConversationalConfig(
    agent=AgentConfig(
        prompt=PromptAgent(
            tools=[language_detection_tool],
            first_message="Hi how are you?"
        )
    ),
    language_presets=language_presets
)

# Create the agent
response = elevenlabs.conversational_ai.agents.create(
    conversation_config=conversation_config
)
```

```javascript
import { ElevenLabs } from '@elevenlabs/elevenlabs-js';

// Initialize the client
const elevenlabs = new ElevenLabs({
  apiKey: 'YOUR_API_KEY',
});

// Create the agent with language detection tool
await elevenlabs.conversationalAi.agents.create({
  conversationConfig: {
    agent: {
      prompt: {
        tools: [
          {
            type: 'system',
            name: 'language_detection',
            description: '', // Optional: Customize when the tool should be triggered
          },
        ],
        firstMessage: 'Hi, how are you?',
      },
    },
    languagePresets: {
      nl: {
        overrides: {
          agent: {
            prompt: null,
            firstMessage: 'Hoi, hoe gaat het met je?',
            language: null,
          },
          tts: null,
        },
      },
      fi: {
        overrides: {
          agent: {
            prompt: null,
            firstMessage: 'Hei, kuinka voit?',
            language: null,
          },
          tts: null,
        },
        firstMessageTranslation: {
          sourceHash: '{"firstMessage":"Hi how are you?","language":"en"}',
          text: 'Hei, kuinka voit?',
        },
      },
      tr: {
        overrides: {
          agent: {
            prompt: null,
            firstMessage: 'Merhaba, nasılsın?',
            language: null,
          },
          tts: null,
        },
      },
      ru: {
        overrides: {
          agent: {
            prompt: null,
            firstMessage: 'Привет, как ты?',
            language: null,
          },
          tts: null,
        },
      },
      pt: {
        overrides: {
          agent: {
            prompt: null,
            firstMessage: 'Oi, como você está?',
            language: null,
          },
          tts: null,
        },
      },
      ar: {
        overrides: {
          agent: {
            prompt: null,
            firstMessage: 'مرحبًا كيف حالك؟',
            language: null,
          },
          tts: null,
        },
      },
    },
  },
});
```

```bash
curl -X POST https://api.elevenlabs.io/v1/convai/agents/create \
     -H "xi-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
  "conversation_config": {
    "agent": {
      "prompt": {
        "first_message": "Hi how are you?",
        "tools": [
          {
            "type": "system",
            "name": "language_detection",
            "description": ""
          }
        ]
      }
    },
    "language_presets": {
      "nl": {
        "overrides": {
          "agent": {
            "prompt": null,
            "first_message": "Hoi, hoe gaat het met je?",
            "language": null
          },
          "tts": null
        }
      },
      "fi": {
        "overrides": {
          "agent": {
            "prompt": null,
            "first_message": "Hei, kuinka voit?",
            "language": null
          },
          "tts": null
        }
      },
      "tr": {
        "overrides": {
          "agent": {
            "prompt": null,
            "first_message": "Merhaba, nasılsın?",
            "language": null
          },
          "tts": null
        }
      },
      "ru": {
        "overrides": {
          "agent": {
            "prompt": null,
            "first_message": "Привет, как ты?",
            "language": null
          },
          "tts": null
        }
      },
      "pt": {
        "overrides": {
          "agent": {
            "prompt": null,
            "first_message": "Oi, como você está?",
            "language": null
          },
          "tts": null
        }
      },
      "ar": {
        "overrides": {
          "agent": {
            "prompt": null,
            "first_message": "مرحبًا كيف حالك؟",
            "language": null
          },
          "tts": null
        }
      }
    }
  }
}'
```

</CodeBlocks>

<Tip>Leave the description blank to use the default language detection prompt.</Tip>


---
title: Agent transfer
subtitle: >-
  Seamlessly transfer the user between Conversational AI agents based on defined
  conditions.
---

## Overview

Agent-agent transfer allows a Conversational AI agent to hand off the ongoing conversation to another designated agent when specific conditions are met. This enables the creation of sophisticated, multi-layered conversational workflows where different agents handle specific tasks or levels of complexity.

For example, an initial agent (Orchestrator) could handle general inquiries and then transfer the call to a specialized agent based on the conversation's context. Transfers can also be nested:

<Frame background="subtle" caption="Example Agent Transfer Hierarchy">

```text
Orchestrator Agent (Initial Qualification)
│
├───> Agent 1 (e.g., Availability Inquiries)
│
├───> Agent 2 (e.g., Technical Support)
│     │
│     └───> Agent 2a (e.g., Hardware Support)
│
└───> Agent 3 (e.g., Billing Issues)

```

</Frame>

<Note>

We recommend using the `gpt-4o` or `gpt-4o-mini` models when using agent-agent transfers due to better tool calling.

</Note>

## Custom LLM integration

**Purpose**: Transfer conversations between specialized AI agents based on user needs.

**Trigger conditions**: The LLM should call this tool when:

- User request requires specialized knowledge or different agent capabilities
- Current agent cannot adequately handle the query
- Conversation flow indicates need for different agent type

**Parameters**:

- `reason` (string, optional): The reason for the agent transfer
- `agent_number` (integer, required): Zero-indexed number of the agent to transfer to (based on configured transfer rules)

**Function call format**:

```json
{
  "type": "function",
  "function": {
    "name": "transfer_to_agent",
    "arguments": "{\"reason\": \"User needs billing support\", \"agent_number\": 0}"
  }
}
```

**Implementation**: Define transfer rules mapping conditions to specific agent IDs. Configure which agents the current agent can transfer to. Agents are referenced by zero-indexed numbers in the transfer configuration.


## Enabling agent transfer

Agent transfer is configured using the `transfer_to_agent` system tool.

<Steps>
    <Step title="Add the transfer tool">
        Enable agent transfer by selecting the `transfer_to_agent` system tool in your agent's configuration within the `Agent` tab. Choose "Transfer to AI Agent" when adding a tool.

        <Frame background="subtle">
            <img src="file:efe1efa3-221c-4237-b22c-033dc4c98910" alt="Add Transfer Tool" />
        </Frame>
    </Step>

    <Step title="Configure tool description (optional)">
        You can provide a custom description to guide the LLM on when to trigger a transfer. If left blank, a default description encompassing the defined transfer rules will be used.

        <Frame background="subtle">
             <img src="file:46b5b2ed-8eb3-47bf-9c0b-be2b5fbaed15" alt="Transfer Tool Description" />
        </Frame>
    </Step>

    <Step title="Define transfer rules">
        Configure the specific rules for transferring to other agents. For each rule, specify:
        - **Agent**: The target agent to transfer the conversation to.
        - **Condition**: A natural language description of the circumstances under which the transfer should occur (e.g., "User asks about billing details", "User requests technical support for product X").
        - **Delay before transfer (milliseconds)**: The minimum delay (in milliseconds) before the transfer occurs. Defaults to 0 for immediate transfer.
        - **Transfer Message**: An optional custom message to play during the transfer. If left blank, the transfer will occur silently.
        - **Enable First Message**: Whether the transferred agent should play its first message after the transfer. Defaults to off.

        The LLM will use these conditions, along with the tool description, to decide when and to which agent (by number) to transfer.

        <Frame background="subtle">
            <img src="file:afe58c28-06f4-44fe-a262-953216d33806" alt="Transfer Rules Configuration" />
        </Frame>

        <Note>
            Ensure that the user account creating the agent has at least viewer permissions for any target agents specified in the transfer rules.
        </Note>
    </Step>

</Steps>

## API Implementation

You can configure the `transfer_to_agent` system tool when creating or updating an agent via the API.

<CodeBlocks>

```python
from elevenlabs import (
    ConversationalConfig,
    ElevenLabs,
    AgentConfig,
    PromptAgent,
    PromptAgentInputToolsItem_System,
    SystemToolConfigInputParams_TransferToAgent,
    AgentTransfer
)

# Initialize the client
elevenlabs = ElevenLabs(api_key="YOUR_API_KEY")

# Define transfer rules with new options
transfer_rules = [
    AgentTransfer(
        agent_id="AGENT_ID_1",
        condition="When the user asks for billing support.",
        delay_ms=1000,  # 1 second delay
        transfer_message="I'm connecting you to our billing specialist.",
        enable_transferred_agent_first_message=True
    ),
    AgentTransfer(
        agent_id="AGENT_ID_2",
        condition="When the user requests advanced technical help.",
        delay_ms=0,  # Immediate transfer
        transfer_message=None,  # Silent transfer
        enable_transferred_agent_first_message=False
    )
]

# Create the transfer tool configuration
transfer_tool = PromptAgentInputToolsItem_System(
    type="system",
    name="transfer_to_agent",
    description="Transfer the user to a specialized agent based on their request.", # Optional custom description
    params=SystemToolConfigInputParams_TransferToAgent(
        transfers=transfer_rules
    )
)

# Create the agent configuration
conversation_config = ConversationalConfig(
    agent=AgentConfig(
        prompt=PromptAgent(
            prompt="You are a helpful assistant.",
            first_message="Hi, how can I help you today?",
            tools=[transfer_tool],
        )
    )
)

# Create the agent
response = elevenlabs.conversational_ai.agents.create(
    conversation_config=conversation_config
)

print(response)
```

```javascript
import { ElevenLabs } from '@elevenlabs/elevenlabs-js';

// Initialize the client
const elevenlabs = new ElevenLabs({
  apiKey: 'YOUR_API_KEY',
});

// Define transfer rules with new options
const transferRules = [
  {
    agentId: 'AGENT_ID_1',
    condition: 'When the user asks for billing support.',
    delayMs: 1000, // 1 second delay
    transferMessage: "I'm connecting you to our billing specialist.",
    enableTransferredAgentFirstMessage: true,
  },
  {
    agentId: 'AGENT_ID_2',
    condition: 'When the user requests advanced technical help.',
    delayMs: 0, // Immediate transfer
    transferMessage: null, // Silent transfer
    enableTransferredAgentFirstMessage: false,
  },
];

// Create the agent with the transfer tool
await elevenlabs.conversationalAi.agents.create({
  conversationConfig: {
    agent: {
      prompt: {
        prompt: 'You are a helpful assistant.',
        firstMessage: 'Hi, how can I help you today?',
        tools: [
          {
            type: 'system',
            name: 'transfer_to_agent',
            description: 'Transfer the user to a specialized agent based on their request.', // Optional custom description
            params: {
              systemToolType: 'transfer_to_agent',
              transfers: transferRules,
            },
          },
        ],
      },
    },
  },
});
```

</CodeBlocks>



---
title: Transfer to human
subtitle: >-
  Seamlessly transfer the user to a human operator via phone number based on
  defined conditions.
---

## Overview

Human transfer allows a Conversational AI agent to transfer the ongoing call to a specified phone number or SIP URI when certain conditions are met. This enables agents to hand off complex issues, specific requests, or situations requiring human intervention to a live operator.

This feature utilizes the `transfer_to_number` system tool which supports transfers via Twilio and SIP trunk numbers. When triggered, the agent can provide a message to the user while they wait and a separate message summarizing the situation for the human operator receiving the call.

<Note>
  The `transfer_to_number` system tool is only available for phone calls and is not available in the
  chat widget.
</Note>

## Transfer Types

The system supports two types of transfers:

- **Conference Transfer**: Default behavior that calls the destination and adds the participant to a conference room, then removes the AI agent so only the caller and transferred participant remain.
- **SIP REFER Transfer**: Uses the SIP REFER protocol to transfer calls directly to the destination. Works with both phone numbers and SIP URIs, but only available when using SIP protocol during the conversation and requires your SIP Trunk to allow transfer via SIP REFER.

## Custom LLM integration

**Purpose**: Seamlessly hand off conversations to human operators when AI assistance is insufficient.

**Trigger conditions**: The LLM should call this tool when:

- Complex issues requiring human judgment
- User explicitly requests human assistance
- AI reaches limits of capability for the specific request
- Escalation protocols are triggered

**Parameters**:

- `reason` (string, optional): The reason for the transfer
- `transfer_number` (string, required): The phone number to transfer to (must match configured numbers)
- `client_message` (string, required): Message read to the client while waiting for transfer
- `agent_message` (string, required): Message for the human operator receiving the call

**Function call format**:

```json
{
  "type": "function",
  "function": {
    "name": "transfer_to_number",
    "arguments": "{\"reason\": \"Complex billing issue\", \"transfer_number\": \"+15551234567\", \"client_message\": \"I'm transferring you to a billing specialist who can help with your account.\", \"agent_message\": \"Customer has a complex billing dispute about order #12345 from last month.\"}"
  }
}
```

**Implementation**: Configure transfer phone numbers and conditions. Define messages for both customer and receiving human operator. Works with both Twilio and SIP trunking.


## Numbers that can be transferred to

Currently only [SIP trunking](/docs/conversational-ai/phone-numbers/sip-trunking) phone numbers support transferring to external numbers.
[Twilio phone numbers](/docs/conversational-ai/phone-numbers/twilio-integration/native-integration) currently can only transfer to phone numbers hosted on Twilio. If this is needed we recommended using Twilio numbers via [Twilio elastic SIP trunking](https://www.twilio.com/docs/sip-trunking) and our SIP trunking support, rather than via the native integration.

## Enabling human transfer

Human transfer is configured using the `transfer_to_number` system tool.

<Steps>
    <Step title="Add the transfer tool">
        Enable human transfer by selecting the `transfer_to_number` system tool in your agent's configuration within the `Agent` tab. Choose "Transfer to Human" when adding a tool.

        <Frame background="subtle" caption="Select 'Transfer to Human' tool">
            {/* Placeholder for image showing adding the 'Transfer to Human' tool */}
            <img src="file:28f9756e-a01a-49b5-86ea-1cd32af74715" alt="Add Human Transfer Tool" />
        </Frame>
    </Step>

    <Step title="Configure tool description (optional)">
        You can provide a custom description to guide the LLM on when to trigger a transfer. If left blank, a default description encompassing the defined transfer rules will be used.

        <Frame background="subtle" caption="Configure transfer tool description">
             {/* Placeholder for image showing the tool description field */}
             <img src="file:87bcfdaa-b3e5-4104-a85a-b865f276ede4" alt="Human Transfer Tool Description" />
        </Frame>
    </Step>

    <Step title="Define transfer rules">
        Configure the specific rules for transferring to phone numbers or SIP URIs. For each rule, specify:

        - **Transfer Type**: Choose between Conference (default) or SIP REFER transfer methods
        - **Number Type**: Select Phone for regular phone numbers or SIP URI for SIP addresses
        - **Phone Number/SIP URI**: The target destination in the appropriate format:
          - Phone numbers: E.164 format (e.g., +12125551234)
          - SIP URIs: SIP format (e.g., sip:1234567890@example.com)
        - **Condition**: A natural language description of the circumstances under which the transfer should occur (e.g., "User explicitly requests to speak to a human", "User needs to update sensitive account information").

        The LLM will use these conditions, along with the tool description, to decide when and to which destination to transfer.

        <Note>
            **SIP REFER transfers** require SIP protocol during the conversation and your SIP Trunk must allow transfer via SIP REFER. Only SIP REFER supports transferring to a SIP URI.
        </Note>

        <Frame background="subtle" caption="Define transfer rules with phone number and condition">
            {/* Placeholder for image showing transfer rules configuration */}
            <img src="file:d817a021-9845-4ab3-b4c7-ee1ecdc0492c" alt="Human Transfer Rules Configuration" />
        </Frame>

        <Note>
            Ensure destinations are correctly formatted:
            - Phone numbers: E.164 format and associated with a properly configured account
            - SIP URIs: Valid SIP format (sip:user@domain or sips:user@domain)
        </Note>
    </Step>

</Steps>

## API Implementation

You can configure the `transfer_to_number` system tool when creating or updating an agent via the API. The tool allows specifying messages for both the client (user being transferred) and the agent (human operator receiving the call).

<CodeBlocks>

```python
from elevenlabs import (
    ConversationalConfig,
    ElevenLabs,
    AgentConfig,
    PromptAgent,
    PromptAgentInputToolsItem_System,
    SystemToolConfigInputParams_TransferToNumber,
    PhoneNumberTransfer,
)

# Initialize the client
elevenlabs = ElevenLabs(api_key="YOUR_API_KEY")

# Define transfer rules
transfer_rules = [
    PhoneNumberTransfer(
        transfer_destination={"type": "phone", "phone_number": "+15551234567"},
        condition="When the user asks for billing support.",
        transfer_type="conference"
    ),
    PhoneNumberTransfer(
        transfer_destination={"type": "sip_uri", "sip_uri": "sip:support@example.com"},
        condition="When the user requests to file a formal complaint.",
        transfer_type="sip_refer"
    )
]

# Create the transfer tool configuration
transfer_tool = PromptAgentInputToolsItem_System(
    type="system",
    name="transfer_to_human",
    description="Transfer the user to a specialized agent based on their request.", # Optional custom description
    params=SystemToolConfigInputParams_TransferToNumber(
        transfers=transfer_rules
    )
)

# Create the agent configuration
conversation_config = ConversationalConfig(
    agent=AgentConfig(
        prompt=PromptAgent(
            prompt="You are a helpful assistant.",
            first_message="Hi, how can I help you today?",
            tools=[transfer_tool],
        )
    )
)

# Create the agent
response = elevenlabs.conversational_ai.agents.create(
    conversation_config=conversation_config
)

# Note: When the LLM decides to call this tool, it needs to provide:
# - transfer_number: The phone number to transfer to (must match one defined in rules).
# - client_message: Message read to the user during transfer.
# - agent_message: Message read to the human operator receiving the call.
```

```javascript
import { ElevenLabs } from '@elevenlabs/elevenlabs-js';

// Initialize the client
const elevenlabs = new ElevenLabs({
  apiKey: 'YOUR_API_KEY',
});

// Define transfer rules
const transferRules = [
  {
    transferDestination: { type: 'phone', phoneNumber: '+15551234567' },
    condition: 'When the user asks for billing support.',
    transferType: 'conference'
  },
  {
    transferDestination: { type: 'sip_uri', sipUri: 'sip:support@example.com' },
    condition: 'When the user requests to file a formal complaint.',
    transferType: 'sip_refer'
  },
];

// Create the agent with the transfer tool
await elevenlabs.conversationalAi.agents.create({
  conversationConfig: {
    agent: {
      prompt: {
        prompt: 'You are a helpful assistant.',
        firstMessage: 'Hi, how can I help you today?',
        tools: [
          {
            type: 'system',
            name: 'transfer_to_number',
            description: 'Transfer the user to a human operator based on their request.', // Optional custom description
            params: {
              systemToolType: 'transfer_to_number',
              transfers: transferRules,
            },
          },
        ],
      },
    },
  },
});

// Note: When the LLM decides to call this tool, it needs to provide:
// - transfer_number: The phone number to transfer to (must match one defined in rules).
// - client_message: Message read to the user during transfer.
// - agent_message: Message read to the human operator receiving the call.
</code_block_to_apply_changes_from>
```

</CodeBlocks>



---
title: Skip turn
subtitle: Allow your agent to pause and wait for the user to speak next.
---

## Overview

The **Skip Turn** tool allows your conversational agent to explicitly pause and wait for the user to speak or act before continuing. This system tool is useful when the user indicates they need a moment, for example, by saying "Give me a second," "Let me think," or "One moment please."

## Functionality

- **User-Initiated Pause**: The tool is designed to be invoked by the LLM when it detects that the user needs a brief pause without interruption.
- **No Verbal Response**: After this tool is called, the assistant will not speak. It waits for the user to re-engage or for another turn-taking condition to be met.
- **Seamless Conversation Flow**: It helps maintain a natural conversational rhythm by respecting the user's need for a short break without ending the interaction or the agent speaking unnecessarily.

## Custom LLM integration

**Purpose**: Allow the agent to pause and wait for user input without speaking.

**Trigger conditions**: The LLM should call this tool when:

- User indicates they need a moment ("Give me a second", "Let me think")
- User requests pause in conversation flow
- Agent detects user needs time to process information

**Parameters**:

- `reason` (string, optional): Free-form reason explaining why the pause is needed

**Function call format**:

```json
{
  "type": "function",
  "function": {
    "name": "skip_turn",
    "arguments": "{\"reason\": \"User requested time to think\"}"
  }
}
```

**Implementation**: No additional configuration needed. The tool simply signals the agent to remain silent until the user speaks again.


### API implementation

When creating an agent via API, you can add the Skip Turn tool to your agent configuration. It should be defined as a system tool, with the name `skip_turn`.

<CodeBlocks>

```python
from elevenlabs import (
    ConversationalConfig,
    ElevenLabs,
    AgentConfig,
    PromptAgent,
    PromptAgentInputToolsItem_System
)

# Initialize the client
elevenlabs = ElevenLabs(api_key="YOUR_API_KEY")

# Create the skip turn tool
skip_turn_tool = PromptAgentInputToolsItem_System(
    name="skip_turn",
    description=""  # Optional: Customize when the tool should be triggered, or leave blank for default.
)

# Create the agent configuration
conversation_config = ConversationalConfig(
    agent=AgentConfig(
        prompt=PromptAgent(
            tools=[skip_turn_tool]
        )
    )
)

# Create the agent
response = elevenlabs.conversational_ai.agents.create(
    conversation_config=conversation_config
)
```

```javascript
import { ElevenLabs } from '@elevenlabs/elevenlabs-js';

// Initialize the client
const elevenlabs = new ElevenLabs({
  apiKey: 'YOUR_API_KEY',
});

// Create the agent with skip turn tool
await elevenlabs.conversationalAi.agents.create({
  conversationConfig: {
    agent: {
      prompt: {
        tools: [
          {
            type: 'system',
            name: 'skip_turn',
            description: '', // Optional: Customize when the tool should be triggered, or leave blank for default.
          },
        ],
      },
    },
  },
});
```

</CodeBlocks>

## UI configuration

You can also configure the Skip Turn tool directly within the Agent's UI, in the tools section.

<Steps>

### Step 1: Add a new tool

Navigate to your agent's configuration page. In the "Tools" section, click on "Add tool", the `Skip Turn` option will already be available.

<Frame background="subtle">
  <img
    src="file:acc95173-e6b7-4ca2-933b-0f9332fba11a"
    alt="Add Skip Turn Tool Option"
  />
</Frame>

### Step 2: Configure the tool

You can optionally provide a description to customize when the LLM should trigger this tool, or leave it blank to use the default behavior.

<Frame background="subtle">
  <img src="file:197c0c81-7e0a-4969-8663-9e7769a52f30" alt="Configure Skip Turn Tool" />
</Frame>

### Step 3: Enable the tool

Once configured, the `Skip Turn` tool will appear in your agent's list of enabled tools and the agent will be able to skip turns. .

<Frame background="subtle">
  <img src="file:9e19dee1-6403-408c-b96a-b692a065ff1f" alt="Skip Turn Tool Enabled" />
</Frame>

</Steps>



---
title: Play keypad touch tone
subtitle: >-
  Enable agents to play DTMF tones to interact with automated phone systems and
  navigate menus.
---

## Overview

The keypad touch tone tool allows Conversational AI agents to play DTMF (Dual-Tone Multi-Frequency) tones during phone calls; these are the tones that are played when you press numbers on your keypad. This enables agents to interact with automated phone systems, navigate voice menus, enter extensions, input PIN codes, and perform other touch-tone operations that would typically require a human caller to press keys on their phone keypad.

This system tool supports standard DTMF tones (0-9, \*, #) as well as pause commands for timing control. It works seamlessly with both Twilio and SIP trunking phone integrations, automatically generating the appropriate audio tones for the underlying telephony infrastructure.

## Functionality

- **Standard DTMF tones**: Supports all standard keypad characters (0-9, \*, #)
- **Pause control**: Includes pause commands for precise timing (w = 0.5s, W = 1.0s)
- **Multi-provider support**: Works with both Twilio and SIP trunking integrations

This system tool can be used to navigate phone menus, enter extensions and input codes.
The LLM determines when and what tones to play based on conversation context.

The default tool description explains to the LLM powering the conversation that it has access to play these tones,
and we recommend updating your agent's system prompt to explain when the agent should call this tool.

## Custom LLM integration

**Parameters**:

- `reason` (string, optional): The reason for playing the DTMF tones (e.g., "navigating to extension", "entering PIN")
- `dtmf_tones` (string, required): The DTMF sequence to play. Valid characters: 0-9, \*, #, w (0.5s pause), W (1s pause)

**Function call format**:

```json
{
  "type": "function",
  "function": {
    "name": "play_keypad_touch_tone",
    "arguments": "{"reason": "Navigating to customer service", "dtmf_tones": "2"}"
  }
}
```


## Supported characters

The tool supports the following DTMF characters and commands:

- **Digits**: `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`
- **Special tones**: `*` (star), `#` (pound/hash)
- **Pause commands**:
  - `w` - Short pause (0.5 seconds)
  - `W` - Long pause (1.0 second)

## API Implementation

You can configure the `play_keypad_touch_tone` system tool when creating or updating an agent via the API. This tool requires no additional configuration parameters beyond enabling it.

<CodeBlocks>

```python
from elevenlabs import (
    ConversationalConfig,
    ElevenLabs,
    AgentConfig,
    PromptAgent,
    PromptAgentInputToolsItem_System,
    SystemToolConfigInputParams_PlayKeypadTouchTone,
)

# Initialize the client
elevenlabs = ElevenLabs(api_key="YOUR_API_KEY")

# Create the keypad touch tone tool configuration
keypad_tool = PromptAgentInputToolsItem_System(
    type="system",
    name="play_keypad_touch_tone",
    description="Play DTMF tones to interact with automated phone systems.", # Optional custom description
    params=SystemToolConfigInputParams_PlayKeypadTouchTone(
        system_tool_type="play_keypad_touch_tone"
    )
)

# Create the agent configuration
conversation_config = ConversationalConfig(
    agent=AgentConfig(
        prompt=PromptAgent(
            prompt="You are a helpful assistant that can interact with phone systems.",
            first_message="Hi, I can help you navigate phone systems. How can I assist you today?",
            tools=[keypad_tool],
        )
    )
)

# Create the agent
response = elevenlabs.conversational_ai.agents.create(
    conversation_config=conversation_config
)
```

```javascript
import { ElevenLabs } from '@elevenlabs/elevenlabs-js';

// Initialize the client
const elevenlabs = new ElevenLabs({
  apiKey: 'YOUR_API_KEY',
});

// Create the agent with the keypad touch tone tool
await elevenlabs.conversationalAi.agents.create({
  conversationConfig: {
    agent: {
      prompt: {
        prompt: 'You are a helpful assistant that can interact with phone systems.',
        firstMessage: 'Hi, I can help you navigate phone systems. How can I assist you today?',
        tools: [
          {
            type: 'system',
            name: 'play_keypad_touch_tone',
            description: 'Play DTMF tones to interact with automated phone systems.', // Optional custom description
            params: {
              systemToolType: 'play_keypad_touch_tone',
            },
          },
        ],
      },
    },
  },
});
```

</CodeBlocks>

<Note>
  The tool only works during active phone calls powered by Twilio or SIP trunking. It will return an
  error if called outside of a phone conversation context.
</Note>




---
title: Voicemail detection
subtitle: >-
  Enable agents to automatically detect voicemail systems and optionally leave
  messages.
---

## Overview

The **Voicemail Detection** tool allows your Conversational AI agent to automatically identify when a call has been answered by a voicemail system rather than a human. This system tool enables agents to handle automated voicemail scenarios gracefully by either leaving a pre-configured message or ending the call immediately.

## Functionality

- **Automatic Detection**: The LLM analyzes conversation patterns to identify voicemail systems based on automated greetings and prompts
- **Configurable Response**: Choose to either leave a custom voicemail message or end the call immediately when voicemail is detected
- **Call Termination**: After detection and optional message delivery, the call is automatically terminated
- **Status Tracking**: Voicemail detection events are logged and can be viewed in conversation history and batch call results

## Custom LLM integration

**Parameters**:

- `reason` (string, required): The reason for detecting voicemail (e.g., "automated greeting detected", "no human response")

**Function call format**:

```json
{
  "type": "function",
  "function": {
    "name": "voicemail_detection",
    "arguments": "{\"reason\": \"Automated greeting detected with request to leave message\"}"
  }
}
```


## Configuration Options

The voicemail detection tool can be configured with the following options:

<Frame background="subtle">
  ![Voicemail detection configuration
  interface](file:2597facf-1bbc-48e2-8aa1-5437046c7025)
</Frame>

- **Voicemail Message**: You can configure an optional custom message to be played when voicemail is detected

## API Implementation

When creating an agent via API, you can add the Voicemail Detection tool to your agent configuration. It should be defined as a system tool:

<CodeBlocks>

```python
from elevenlabs import (
    ConversationalConfig,
    ElevenLabs,
    AgentConfig,
    PromptAgent,
    PromptAgentInputToolsItem_System
)

# Initialize the client
elevenlabs = ElevenLabs(api_key="YOUR_API_KEY")

# Create the voicemail detection tool
voicemail_detection_tool = PromptAgentInputToolsItem_System(
    name="voicemail_detection",
    description=""  # Optional: Customize when the tool should be triggered
)

# Create the agent configuration
conversation_config = ConversationalConfig(
    agent=AgentConfig(
        prompt=PromptAgent(
            tools=[voicemail_detection_tool]
        )
    )
)

# Create the agent
response = elevenlabs.conversational_ai.agents.create(
    conversation_config=conversation_config
)
```

```javascript
import { ElevenLabs } from '@elevenlabs/elevenlabs-js';

// Initialize the client
const elevenlabs = new ElevenLabs({
  apiKey: 'YOUR_API_KEY',
});

// Create the agent with voicemail detection tool
await elevenlabs.conversationalAi.agents.create({
  conversationConfig: {
    agent: {
      prompt: {
        tools: [
          {
            type: 'system',
            name: 'voicemail_detection',
            description: '', // Optional: Customize when the tool should be triggered
          },
        ],
      },
    },
  },
});
```

</CodeBlocks>
