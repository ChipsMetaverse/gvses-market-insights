---
title: Large Language Models (LLMs)
subtitle: >-
  Understand the available LLMs for your conversational AI agents, their
  capabilities, and pricing.
---

## Overview

Our conversational AI platform supports a variety of cutting-edge Large Language Models (LLMs) to power your voice agents. Choosing the right LLM depends on your specific needs, balancing factors like performance, context window size, features, and cost. This document provides details on the supported models and their associated pricing.

The selection of an LLM is a critical step in configuring your conversational AI agent, directly impacting its conversational abilities, knowledge depth, and operational cost.

<Note>
  The maximum system prompt size is 2MB, which includes your agent's instructions, knowledge base
  content, and other system-level context.
</Note>

## Supported LLMs

We offer models from leading providers such as OpenAI, Google, and Anthropic, as well as the option to integrate your own custom LLM for maximum flexibility.

<Note>
  Pricing is typically denoted in USD per 1 million tokens unless specified otherwise. A token is a
  fundamental unit of text data for LLMs, roughly equivalent to 4 characters on average.
</Note>

<AccordionGroup>
  <Accordion title="Gemini">
    Google's Gemini models offer a balance of performance, large context windows, and competitive pricing, with the lowest latency.
    <Tabs>
      <Tab title="Token cost">

        | Model                   | Max Output Tokens | Max Context (Tokens) | Input Price ($/1M tokens) | Output Price ($/1M tokens) | Input Cache Read ($/1M tokens) | Input Cache Write ($/1M tokens) |
        | ----------------------- | ----------------- | -------------------- | ------------------------- | -------------------------- | ------------------------------ | ------------------------------- |
        | `gemini-1.5-pro`        | 8,192             | 2,097,152            | 1.25                      | 5                          | 0.3125                         | n/a                             |
        | `gemini-1.5-flash`      | 8,192             | 1,048,576            | 0.075                     | 0.3                        | 0.01875                        | n/a                             |
        | `gemini-2.0-flash`      | 8,192             | 1,048,576            | 0.1                       | 0.4                        | 0.025                          | n/a                             |
        | `gemini-2.0-flash-lite` | 8,192             | 1,048,576            | 0.075                     | 0.3                        | n/a                            | n/a                             |
        | `gemini-2.5-flash`      | 65,535            | 1,048,576            | 0.15                      | 0.6                        | n/a                            | n/a                             |

      </Tab>
      <Tab title="Per minute cost estimation">

        | Model                   | Avg LLM Cost (No KB) ($/min) | Avg LLM Cost (Large KB) ($/min) |
        | ----------------------- | ----------------------------- | ------------------------------- |
        | `gemini-1.5-pro`        | 0.009                           | 0.10                            |
        | `gemini-1.5-flash`      | 0.002                           | 0.01                            |
        | `gemini-2.0-flash`      | 0.001                           | 0.02                            |
        | `gemini-2.0-flash-lite` | 0.001                           | 0.009                           |
        | `gemini-2.5-flash`      | 0.001                           | 0.10                            |

      </Tab>
    </Tabs>
    <br />

  </Accordion>

  <Accordion title="OpenAI">
    OpenAI models are known for their strong general-purpose capabilities and wide range of options.

    <Tabs>
      <Tab title="Token information">

        | Model           | Max Output Tokens | Max Context (Tokens) | Input Price ($/1M tokens) | Output Price ($/1M tokens) | Input Cache Read ($/1M tokens) | Input Cache Write ($/1M tokens) |
        | --------------- | ----------------- | -------------------- | ------------------------- | -------------------------- | ------------------------------ | ------------------------------- |
        | `gpt-4o-mini`   | 16,384            | 128,000              | 0.15                      | 0.6                        | 0.075                          | n/a                             |
        | `gpt-4o`        | 4,096             | 128,000              | 2.5                       | 10                         | 1.25                           | n/a                             |
        | `gpt-4`         | 8,192             | 8,192                | 30                        | 60                         | n/a                            | n/a                             |
        | `gpt-4-turbo`   | 4,096             | 128,000              | 10                        | 30                         | n/a                            | n/a                             |
        | `gpt-4.1`       | 32,768            | 1,047,576            | 2                         | 8                          | n/a                            | n/a                             |
        | `gpt-4.1-mini`  | 32,768            | 1,047,576            | 0.4                       | 1.6                        | 0.1                            | n/a                             |
        | `gpt-4.1-nano`  | 32,768            | 1,047,576            | 0.1                       | 0.4                        | 0.025                          | n/a                             |
        | `gpt-3.5-turbo` | 4,096             | 16,385               | 0.5                       | 1.5                        | n/a                            | n/a                             |


      </Tab>

      <Tab  title="Per minute cost estimation">

        | Model           | Avg LLM Cost (No KB) ($/min)    | Avg LLM Cost (Large KB) ($/min) |
        | --------------- | -----------------------------   | ------------------------------- |
        | `gpt-4o-mini`   | 0.001                           | 0.10                            |
        | `gpt-4o`        | 0.01                            | 0.13                            |
        | `gpt-4`         | n/a                             | n/a                             |
        | `gpt-4-turbo`   | 0.04                            | 0.39                            |
        | `gpt-4.1`       | 0.003                           | 0.13                            |
        | `gpt-4.1-mini`  | 0.002                           | 0.07                            |
        | `gpt-4.1-nano`  | 0.000                           | 0.006                           |
        | `gpt-3.5-turbo` | 0.005                           | 0.08                            |


      </Tab>
    </Tabs>
    <br />

  </Accordion>

  <Accordion title="Anthropic">
    Anthropic's Claude models are designed with a focus on helpfulness, honesty, and harmlessness, often featuring large context windows.

     <Tabs>
      <Tab title="Token cost">

        | Model                  | Max Output Tokens | Max Context (Tokens) | Input Price ($/1M tokens) | Output Price ($/1M tokens) | Input Cache Read ($/1M tokens) | Input Cache Write ($/1M tokens) |
        | ---------------------- | ----------------- | -------------------- | ------------------------- | -------------------------- | ------------------------------ | ------------------------------- |
        | `claude-sonnet-4`      | 64,000            | 200,000              | 3                         | 15                         | 0.3                            | 3.75                            |
        | `claude-3-7-sonnet`    | 4,096             | 200,000              | 3                         | 15                         | 0.3                            | 3.75                            |
        | `claude-3-5-sonnet`    | 4,096             | 200,000              | 3                         | 15                         | 0.3                            | 3.75                            |
        | `claude-3-5-sonnet-v1` | 4,096             | 200,000              | 3                         | 15                         | 0.3                            | 3.75                            |
        | `claude-3-0-haiku`     | 4,096             | 200,000              | 0.25                      | 1.25                       | 0.03                           | 0.3                             |

      </Tab>
      <Tab title="Per minute cost estimation">

          | Model                  | Avg LLM Cost (No KB) ($/min)    | Avg LLM Cost (Large KB) ($/min) |
          | ---------------------- | -----------------------------   | ------------------------------- |
          | `claude-sonnet-4`      | 0.03                            | 0.26                            |
          | `claude-3-7-sonnet`    | 0.03                            | 0.26                            |
          | `claude-3-5-sonnet`    | 0.03                            | 0.20                            |
          | `claude-3-5-sonnet-v1` | 0.03                            | 0.17                            |
          | `claude-3-0-haiku`     | 0.002                           | 0.03                            |

      </Tab>
    </Tabs>
    <br />

  </Accordion>
</AccordionGroup>

## Choosing an LLM

Selecting the most suitable LLM for your application involves considering several factors:

- **Task Complexity**: More demanding or nuanced tasks generally benefit from more powerful models (e.g., OpenAI's GPT-4 series, Anthropic's Claude Sonnet 4, Google's Gemini 2.5 models).
- **Latency Requirements**: For applications requiring real-time or near real-time responses, such as live voice conversations, models optimized for speed are preferable (e.g., Google's Gemini Flash series, Anthropic's Claude Haiku, OpenAI's GPT-4o-mini).
- **Context Window Size**: If your application needs to process, understand, or recall information from long conversations or extensive documents, select models with larger context windows.
- **Cost-Effectiveness**: Balance the desired performance and features against your budget. LLM prices can vary significantly, so analyze the pricing structure (input, output, and cache tokens) in relation to your expected usage patterns.
- **HIPAA Compliance**: If your application involves Protected Health Information (PHI), it is crucial to use an LLM that is designated as HIPAA compliant and ensure your entire data handling process meets regulatory standards.

## HIPAA Compliance

Certain LLMs available on our platform may be suitable for use in environments requiring HIPAA compliance, please see the [HIPAA compliance docs](/docs/conversational-ai/legal/hipaa) for more details

## Understanding LLM Pricing

- **Tokens**: LLM usage is typically billed based on the number of tokens processed. As a general guideline for English text, 100 tokens is approximately equivalent to 75 words.
- **Input vs. Output Pricing**: Providers often differentiate pricing for input tokens (the data you send to the model) and output tokens (the data the model generates in response).
- **Cache Pricing**:
  - `input_cache_read`: This refers to the cost associated with retrieving previously processed input data from a cache. Utilizing cached data can lead to cost savings if identical inputs are processed multiple times.
  - `input_cache_write`: This is the cost associated with storing input data into a cache. Some LLM providers may charge for this operation.
- The prices listed in this document are per 1 million tokens and are based on the information available at the time of writing. These prices are subject to change by the LLM providers.

For the most accurate and current information on model capabilities, pricing, and terms of service, always consult the official documentation from the respective LLM providers (OpenAI, Google, Anthropic, xAI).


---
title: Optimizing LLM costs
subtitle: >-
  Practical strategies to reduce LLM inference expenses on the ElevenLabs
  platform.
---

## Overview

Managing Large Language Model (LLM) inference costs is essential for developing sustainable AI applications. This guide outlines key strategies to optimize expenditure on the ElevenLabs platform by effectively utilizing its features. For detailed model capabilities and pricing, refer to our main [LLM documentation](/docs/conversational-ai/customization/llm).

<Note>
  ElevenLabs supports reducing costs by reducing inference of the models during periods of silence.
  These periods are billed at 5% of the usual per minute rate. See [the Conversational AI overview
  page](/docs/conversational-ai/overview#pricing-during-silent-periods) for more details.
</Note>

## Understanding inference costs

LLM inference costs on our platform are primarily influenced by:

- **Input tokens**: The amount of data processed from your prompt, including user queries, system instructions, and any contextual data.
- **Output tokens**: The number of tokens generated by the LLM in its response.
- **Model choice**: Different LLMs have varying per-token pricing. More powerful models generally incur higher costs.

Monitoring your usage via the ElevenLabs dashboard or API is crucial for identifying areas for cost reduction.

## Strategic model selection

Choosing the most appropriate LLM is a primary factor in cost efficiency.

- **Right-sizing**: Select the least complex (and typically less expensive) model that can reliably perform your specific task. Avoid using high-cost models for simple operations. For instance, models like Google's `gemini-2.0-flash` offer highly competitive pricing for many common tasks. Always cross-reference with the full [Supported LLMs list](/docs/conversational-ai/customization/llm#supported-llms) for the latest pricing and capabilities.
- **Experimentation**: Test various models for your tasks, comparing output quality against incurred costs. Consider language support, context window needs, and specialized skills.

## Prompt optimization

Prompt engineering is a powerful technique for reducing token consumption and associated costs. By crafting clear, concise, and unambiguous system prompts, you can guide the model to produce more efficient responses. Eliminate redundant wording and unnecessary context that might inflate your token count. Consider explicitly instructing the model on your desired output length—for example, by adding phrases like "Limit your response to two sentences" or "Provide a brief summary." These simple directives can significantly reduce the number of output tokens while maintaining the quality and relevance of the generated content.

**Modular design**: For complex conversational flows, leverage [agent-agent transfer](/docs/conversational-ai/customization/tools/system-tools/agent-transfer). This allows you to break down a single, large system prompt into multiple, smaller, and more specialized prompts, each handled by a different agent. This significantly reduces the token count per interaction by loading only the contextually relevant prompt for the current stage of the conversation, rather than a comprehensive prompt designed for all possibilities.

## Leveraging knowledge and retrieval

For applications requiring access to large information volumes, Retrieval Augmented Generation (RAG) and a well-maintained knowledge base are key.

- **Efficient RAG**:
  - RAG reduces input tokens by providing the LLM with only relevant snippets from your [Knowledge Base](/docs/conversational-ai/customization/knowledge-base), instead of including extensive data in the prompt.
  - Optimize the retriever to fetch only the most pertinent "chunks" of information.
  - Fine-tune chunk size and overlap for a balance between context and token count.
  - Learn more about implementing [RAG](/docs/conversational-ai/customization/knowledge-base/rag).
- **Context size**:
  - Ensure your [Knowledge Base](/docs/conversational-ai/customization/knowledge-base) contains accurate, up-to-date, and relevant information.
  - Well-structured content improves retrieval precision and reduces token usage from irrelevant context.

## Intelligent tool utilization

Using [Server Tools](/docs/conversational-ai/customization/tools/server-tools) allows LLMs to delegate tasks to external APIs or custom code, which can be more cost-effective.

- **Task offloading**: Identify deterministic tasks, those requiring real-time data, complex calculations, or API interactions (e.g., database lookups, external service calls).
- **Orchestration**: The LLM acts as an orchestrator, making structured tool calls. This is often far more token-efficient than attempting complex tasks via prompting alone.
- **Tool descriptions**: Provide clear, concise descriptions for each tool, enabling the LLM to use them efficiently and accurately.

## Checklist

Consider applying these techniques to reduce cost:

| Feature           | Cost impact                                              | Action items                                                                                                                                                        |
| :---------------- | :------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| LLM choice        | Reduces per-token cost                                   | Select the smallest, most economical model that reliably performs the task. Experiment and compare cost vs. quality.                                                |
| Custom LLMs       | Potentially lower inference cost for specialized tasks   | Evaluate for high-volume, specific tasks; fine-tune on proprietary data to create smaller, efficient models.                                                        |
| System prompts    | Reduces input & output tokens, guides model behavior     | Be concise, clear, and specific. Instruct on desired output format and length (e.g., "be brief," "use JSON").                                                       |
| User prompts      | Reduces input tokens                                     | Encourage specific queries; use few-shot examples strategically; summarize or select relevant history.                                                              |
| Output control    | Reduces output tokens                                    | Prompt for summaries or key info; use `max_tokens` cautiously; iterate on prompts to achieve natural conciseness.                                                   |
| RAG               | Reduces input tokens by avoiding large context in prompt | Optimize retriever for relevance; fine-tune chunk size/overlap; ensure high-quality embeddings and search algorithms.                                               |
| Knowledge base    | Improves RAG efficiency, reducing irrelevant tokens      | Curate regularly; remove outdated info; ensure good structure, metadata, and tagging for precise retrieval.                                                         |
| Tools (functions) | Avoids LLM calls for specific tasks; reduces tokens      | Delegate deterministic, calculation-heavy, or external API tasks to tools. Design clear tool descriptions for the LLM.                                              |
| Agent transfer    | Enables use of cheaper models for simpler parts of tasks | Use simpler/cheaper agents for initial triage/FAQs; transfer to capable agents only when needed; decompose large prompts into smaller prompts across various agents |

<Note title="Conversation history management">
  For stateful conversations, rather than passing in multiple conversation transcripts as a part of
  the system prompt, implement history summarization or sliding window techniques to keep context
  lean. This can be particularly effective when building consumer applications and can often be
  managed upon receiving a post-call webhook.
</Note>

<Tip>
  Continuously monitor your LLM usage and costs. Regularly review and refine your prompts, RAG
  configurations, and tool integrations to ensure ongoing cost-effectiveness.
</Tip>


---
title: Cloudflare Workers AI
subtitle: Connect an agent to a custom LLM on Cloudflare Workers AI.
---

## Overview

[Cloudflare's Workers AI platform](https://developers.cloudflare.com/workers-ai/) lets you run machine learning models, powered by serverless GPUs, on Cloudflare's global network, even on the free plan!

Workers AI comes with a curated set of [popular open-source models](https://developers.cloudflare.com/workers-ai/models/) that enable you to do tasks such as image classification, text generation, object detection and more.

## Choosing a model

To make use of the full power of ElevenLabs Conversational AI you need to use a model that supports [function calling](https://developers.cloudflare.com/workers-ai/function-calling/#what-models-support-function-calling).

When browsing the [model catalog](https://developers.cloudflare.com/workers-ai/models/), look for models with the function calling property beside it.

<iframe
  width="100%"
  height="400"
  src="https://www.youtube-nocookie.com/embed/8iwPIdzTwAA?rel=0&autoplay=0"
  title="YouTube video player"
  frameborder="0"
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
  allowfullscreen
></iframe>

<Tip title="Try out DeepSeek R1" icon="leaf">
  Cloudflare Workers AI provides access to
  [DeepSeek-R1-Distill-Qwen-32B](https://developers.cloudflare.com/workers-ai/models/deepseek-r1-distill-qwen-32b/),
  a model distilled from DeepSeek-R1 based on Qwen2.5. It outperforms OpenAI-o1-mini across various
  benchmarks, achieving new state-of-the-art results for dense models.
</Tip>

## Set up DeepSeek R1 on Cloudflare Workers AI

<Steps>
  <Step>
    Navigate to [dash.cloudflare.com](https://dash.cloudflare.com) and create or sign in to your account. In the navigation, select AI > Workers AI, and then click on the "Use REST API" widget.

    <Frame background="subtle">
    ![Add Secret](file:8ae6938d-846a-471b-aba9-4101ec894fde)
    </Frame>

  </Step>
  <Step>
    Once you have your API key, you can try it out immediately with a curl request. Cloudflare provides an OpenAI-compatible API endpoint making this very convenient. At this point make a note of the model and the full endpoint — including the account ID. For example: `https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}c/ai/v1/`.

    ```bash
    curl https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/v1/chat/completions \
    -X POST \
    -H "Authorization: Bearer {API_TOKEN}" \
    -d '{
        "model": "@cf/deepseek-ai/deepseek-r1-distill-qwen-32b",
        "messages": [
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": "How many Rs in the word Strawberry?"}
        ],
        "stream": false
      }'
    ```

  </Step>
  <Step>
    Navigate to your [AI Agent](https://elevenlabs.io/app/conversational-ai), scroll down to the "Secrets" section and select "Add Secret". After adding the secret, make sure to hit "Save" to make the secret available to your agent.

    <Frame background="subtle">
      ![Add Secret](file:d0f43c6a-89f2-44c4-8a18-4e99f4ece67b)
    </Frame>

  </Step>
  <Step>
    Choose "Custom LLM" from the dropdown menu.
    
    <Frame background="subtle">
      ![Choose custom llm](file:d647c057-b992-4c9a-a8eb-974e81d69fb4)
    </Frame>
  </Step>
  <Step>
    For the Server URL, specify Cloudflare's OpenAI-compatible API endpoint: `https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/v1/`. For the Model ID, specify `@cf/deepseek-ai/deepseek-r1-distill-qwen-32b` as discussed above, and select your API key from the dropdown menu.

    <Frame background="subtle">
      ![Enter url](file:8e89b972-ce27-4fc0-bde2-899ee20d5a5f)
    </Frame>

  </Step>
  <Step>
   Now you can go ahead and click "Test AI Agent" to chat with your custom DeepSeek R1 model.
  </Step>
</Steps>


---
title: Groq Cloud
subtitle: Connect an agent to a custom LLM on Groq Cloud.
---

## Overview

[Groq Cloud](https://console.groq.com/) provides easy access to fast AI inference, giving you OpenAI-compatible API endpoints in a matter of clicks.

Use leading [Openly-available Models](https://console.groq.com/docs/models) like Llama, Mixtral, and Gemma as the brain for your ElevenLabs Conversational AI agents in a few easy steps.

## Choosing a model

To make use of the full power of ElevenLabs Conversational AI you need to use a model that supports tool use and structured outputs. Groq recommends the following Llama-3.3 models their versatility and performance:

- meta-llama/llama-4-scout-17b-16e-instruct (10M token context window) and support for 12 languages (Arabic, English, French, German, Hindi, Indonesian, Italian, Portuguese, Spanish, Tagalog, Thai, and Vietnamese)
- llama-3.3-70b-versatile (128k context window | 32,768 max output tokens)
- llama-3.1-8b-instant (128k context window | 8,192 max output tokens)

With this in mind, it's recommended to use `meta-llama/llama-4-scout-17b-16e-instruct` for your ElevenLabs Conversational AI agent.

## Set up Llama 3.3 on Groq Cloud

<Steps>
  <Step>
    Navigate to [console.groq.com/keys](https://console.groq.com/keys) and create a new API key.

    <Frame background="subtle">
    ![Add Secret](file:1357b314-9dcb-42f4-a404-c8314653f983)
    </Frame>

  </Step>
  <Step>
    Once you have your API key, you can test it by running the following curl command:

    ```bash
    curl https://api.groq.com/openai/v1/chat/completions -s \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $GROQ_API_KEY" \
    -d '{
    "model": "llama-3.3-70b-versatile",
    "messages": [{
        "role": "user",
        "content": "Hello, how are you?"
    }]
    }'
    ```

  </Step>
  <Step>
    Navigate to your [AI Agent](https://elevenlabs.io/app/conversational-ai), scroll down to the "Secrets" section and select "Add Secret". After adding the secret, make sure to hit "Save" to make the secret available to your agent.

    <Frame background="subtle">
      ![Add Secret](file:0cd34d29-272b-4265-a896-dcd9fc649e7d)
    </Frame>

  </Step>
  <Step>
    Choose "Custom LLM" from the dropdown menu.
    
    <Frame background="subtle">
      ![Choose custom llm](file:d647c057-b992-4c9a-a8eb-974e81d69fb4)
    </Frame>
  </Step>
  <Step>
    For the Server URL, specify Groq's OpenAI-compatible API endpoint: `https://api.groq.com/openai/v1`. For the Model ID, specify `meta-llama/llama-4-scout-17b-16e-instruct` as discussed above, and select your API key from the dropdown menu.

    <Frame background="subtle">
      ![Enter url](file:5d7632ff-63ed-4932-b580-dae8c28d7fab)
    </Frame>

  </Step>
  <Step>
   Now you can go ahead and click "Test AI Agent" to chat with your custom Llama 3.3 model.
  </Step>
</Steps>


---
title: Groq Cloud
subtitle: Connect an agent to a custom LLM on Groq Cloud.
---

## Overview

[Groq Cloud](https://console.groq.com/) provides easy access to fast AI inference, giving you OpenAI-compatible API endpoints in a matter of clicks.

Use leading [Openly-available Models](https://console.groq.com/docs/models) like Llama, Mixtral, and Gemma as the brain for your ElevenLabs Conversational AI agents in a few easy steps.

## Choosing a model

To make use of the full power of ElevenLabs Conversational AI you need to use a model that supports tool use and structured outputs. Groq recommends the following Llama-3.3 models their versatility and performance:

- meta-llama/llama-4-scout-17b-16e-instruct (10M token context window) and support for 12 languages (Arabic, English, French, German, Hindi, Indonesian, Italian, Portuguese, Spanish, Tagalog, Thai, and Vietnamese)
- llama-3.3-70b-versatile (128k context window | 32,768 max output tokens)
- llama-3.1-8b-instant (128k context window | 8,192 max output tokens)

With this in mind, it's recommended to use `meta-llama/llama-4-scout-17b-16e-instruct` for your ElevenLabs Conversational AI agent.

## Set up Llama 3.3 on Groq Cloud

<Steps>
  <Step>
    Navigate to [console.groq.com/keys](https://console.groq.com/keys) and create a new API key.

    <Frame background="subtle">
    ![Add Secret](file:1357b314-9dcb-42f4-a404-c8314653f983)
    </Frame>

  </Step>
  <Step>
    Once you have your API key, you can test it by running the following curl command:

    ```bash
    curl https://api.groq.com/openai/v1/chat/completions -s \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $GROQ_API_KEY" \
    -d '{
    "model": "llama-3.3-70b-versatile",
    "messages": [{
        "role": "user",
        "content": "Hello, how are you?"
    }]
    }'
    ```

  </Step>
  <Step>
    Navigate to your [AI Agent](https://elevenlabs.io/app/conversational-ai), scroll down to the "Secrets" section and select "Add Secret". After adding the secret, make sure to hit "Save" to make the secret available to your agent.

    <Frame background="subtle">
      ![Add Secret](file:0cd34d29-272b-4265-a896-dcd9fc649e7d)
    </Frame>

  </Step>
  <Step>
    Choose "Custom LLM" from the dropdown menu.
    
    <Frame background="subtle">
      ![Choose custom llm](file:d647c057-b992-4c9a-a8eb-974e81d69fb4)
    </Frame>
  </Step>
  <Step>
    For the Server URL, specify Groq's OpenAI-compatible API endpoint: `https://api.groq.com/openai/v1`. For the Model ID, specify `meta-llama/llama-4-scout-17b-16e-instruct` as discussed above, and select your API key from the dropdown menu.

    <Frame background="subtle">
      ![Enter url](file:5d7632ff-63ed-4932-b580-dae8c28d7fab)
    </Frame>

  </Step>
  <Step>
   Now you can go ahead and click "Test AI Agent" to chat with your custom Llama 3.3 model.
  </Step>
</Steps>


---
title: Together AI
subtitle: Connect an agent to a custom LLM on Together AI.
---

## Overview

[Together AI](https://www.together.ai/) provides an AI Acceleration Cloud, allowing you to train, fine-tune, and run inference on AI models blazing fast, at low cost, and at production scale.

Instantly run [200+ models](https://together.xyz/models) including DeepSeek, Llama3, Mixtral, and Stable Diffusion, optimized for peak latency, throughput, and context length.

## Choosing a model

To make use of the full power of ElevenLabs Conversational AI you need to use a model that supports tool use and structured outputs. Together AI supports function calling for [these models](https://docs.together.ai/docs/function-calling):

- meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo
- meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo
- meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo
- meta-llama/Llama-3.3-70B-Instruct-Turbo
- mistralai/Mixtral-8x7B-Instruct-v0.1
- mistralai/Mistral-7B-Instruct-v0.1

With this in mind, it's recommended to use at least `meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo` for your ElevenLabs Conversational AI agent.

## Set up Llama 3.1 on Together AI

<Steps>
  <Step>
    Navigate to [api.together.xyz/settings/api-keys](https://api.together.xyz/settings/api-keys) and create a new API key.

    <Frame background="subtle">
    ![Add Secret](file:29c43df4-e110-4440-baa3-8fef8fcc0525)
    </Frame>

  </Step>
  <Step>
    Once you have your API key, you can test it by running the following curl command:

    ```bash
    curl https://api.together.xyz/v1/chat/completions -s \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer <API_KEY>" \
    -d '{
    "model": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
    "messages": [{
        "role": "user",
        "content": "Hello, how are you?"
    }]
    }'
    ```

  </Step>
  <Step>
    Navigate to your [AI Agent](https://elevenlabs.io/app/conversational-ai), scroll down to the "Secrets" section and select "Add Secret". After adding the secret, make sure to hit "Save" to make the secret available to your agent.

    <Frame background="subtle">
      ![Add Secret](file:0e75c4b8-bd3f-4c7d-bf73-37904d23f2c6)
    </Frame>

  </Step>
  <Step>
    Choose "Custom LLM" from the dropdown menu.
    
    <Frame background="subtle">
      ![Choose custom llm](file:d647c057-b992-4c9a-a8eb-974e81d69fb4)
    </Frame>
  </Step>
  <Step>
    For the Server URL, specify Together AI's OpenAI-compatible API endpoint: `https://api.together.xyz/v1`. For the Model ID, specify `meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo` as discussed above, and select your API key from the dropdown menu.

    <Frame background="subtle">
      ![Enter url](file:0a45c143-a968-4e0a-9c9e-49b42109ec66)
    </Frame>

  </Step>
  <Step>
   Now you can go ahead and click "Test AI Agent" to chat with your custom Llama 3.1 model.
  </Step>
</Steps>



---
title: LLM Cascading
subtitle: >-
  Learn how Conversational AI ensures reliable LLM responses using a cascading
  fallback mechanism.
---

## Overview

Conversational AI employs an LLM cascading mechanism to enhance the reliability and resilience of its text generation capabilities. This system automatically attempts to use backup Large Language Models (LLMs) if the primary configured LLM fails, ensuring a smoother and more consistent user experience.

Failures can include API errors, timeouts, or empty responses from the LLM provider. The cascade logic handles these situations gracefully.

## How it Works

The cascading process follows a defined sequence:

1.  **Preferred LLM Attempt:** The system first attempts to generate a response using the LLM selected in the agent's configuration.

2.  **Backup LLM Sequence:** If the preferred LLM fails, the system automatically falls back to a predefined sequence of backup LLMs. This sequence is curated based on model performance, speed, and reliability. The current default sequence (subject to change) is:

    1.  Gemini 2.5 Flash
    2.  Gemini 2.0 Flash
    3.  Gemini 2.0 Flash Lite
    4.  Claude 3.7 Sonnet
    5.  Claude 3.5 Sonnet v2
    6.  Claude 3.5 Sonnet v1
    7.  GPT-4o
    8.  Gemini 1.5 Pro
    9.  Gemini 1.5 Flash

3.  **HIPAA Compliance:** If the agent operates in a mode requiring strict data privacy (HIPAA compliance / zero data retention), the backup list is filtered to include only compliant models from the sequence above.

4.  **Retries:** The system retries the generation process multiple times (at least 3 attempts) across the sequence of available LLMs (preferred + backups). If a backup LLM also fails, it proceeds to the next one in the sequence. If it runs out of unique backup LLMs within the retry limit, it may retry previously failed backup models.

5.  **Lazy Initialization:** Backup LLM connections are initialized only when needed, optimizing resource usage.

<Info>
  The specific list and order of backup LLMs are managed internally by ElevenLabs and optimized for
  performance and availability. The sequence listed above represents the current default but may be
  updated without notice.
</Info>

## Custom LLMs

When you configure a [Custom LLM](/docs/conversational-ai/customization/llm/custom-llm), the standard cascading logic to _other_ models is bypassed. The system will attempt to use your specified Custom LLM.

If your Custom LLM fails, the system will retry the request with the _same_ Custom LLM multiple times (matching the standard minimum retry count) before considering the request failed. It will not fall back to ElevenLabs-hosted models, ensuring your specific configuration is respected.

## Benefits

- **Increased Reliability:** Reduces the impact of temporary issues with a specific LLM provider.
- **Higher Availability:** Increases the likelihood of successfully generating a response even during partial LLM outages.
- **Seamless Operation:** The fallback mechanism is automatic and transparent to the end-user.

## Configuration

LLM cascading is an automatic background process. The only configuration required is selecting your **Preferred LLM** in the agent's settings. The system handles the rest to ensure robust performance.
