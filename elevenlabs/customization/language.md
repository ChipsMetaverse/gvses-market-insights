---
title: Language
subtitle: Learn how to configure your agent to speak multiple languages.
---

## Overview

This guide shows you how to configure your agent to speak multiple languages. You'll learn to:

- Configure your agent's primary language
- Add support for multiple languages
- Set language-specific voices and first messages
- Optimize voice selection for natural pronunciation
- Enable automatic language switching

## Guide

<Steps>

<Step title="Default agent language">
When you create a new agent, it's configured with:

- English as the primary language
- Flash v2 model for fast, English-only responses
- A default first message.

<Frame background="subtle">![](file:42231911-6662-4d90-9dbb-3d0d4c8a8051)</Frame>

<Note>
  Additional languages switch the agent to use the v2.5 Multilingual model. English will always use
  the v2 model.
</Note>

</Step>

<Step title="Add additional languages">
First, navigate to your agent's configuration page and locate the **Agent** tab.

1. In the **Additional Languages** add an additional language (e.g. French)
2. Review the first message, which is automatically translated using a Large Language Model (LLM). Customize it as needed for each additional language to ensure accuracy and cultural relevance.

<Frame background="subtle">![](file:0e70b11f-3343-4d9d-88e0-ec6f9792aa22)</Frame>

<Note>
  Selecting the **All** option in the **Additional Languages** dropdown will configure the agent to
  support 31 languages. Collectively, these languages are spoken by approximately 90% of the world's
  population.
</Note>

</Step>

<Step title="Configure language-specific voices">
For optimal pronunciation, configure each additional language with a language-specific voice from our [Voice Library](https://elevenlabs.io/app/voice-library).

<Note>
  To find great voices for each language curated by the ElevenLabs team, visit the [language top
  picks](https://elevenlabs.io/app/voice-library/collections).
</Note>

<Tabs>
<Tab title="Language-specific voice settings">
<Frame background="subtle">![](file:5b8d35a9-6db3-4611-9b00-5cd99d2b65c4)</Frame>
</Tab>
<Tab title="Voice library">
<Frame background="subtle">![](file:f665fcc3-6429-4b23-baa9-6a116eb101f8)</Frame>
</Tab>

</Tabs>
</Step>

<Step title="Enable language detection">

Add the [language detection tool](/docs/conversational-ai/customization/tools/system-tools/language-detection) to your agent can automatically switch to the user's preferred language.

</Step>

<Step title="Starting a call">

Now that the agent is configured to support additional languages, the widget will prompt the user for their preferred language before the conversation begins.

If using the SDK, the language can be set programmatically using conversation overrides. See the
[Overrides](/docs/conversational-ai/customization/personalization/overrides) guide for implementation details.

<Frame background="subtle">![](file:547d9f8b-f9d1-46b4-8473-3bc09eacf6f9)</Frame>

<Note>
  Language selection is fixed for the duration of the call - users cannot switch languages
  mid-conversation.
</Note>

</Step>

</Steps>

### Internationalization

You can integrate the widget with your internationalization framework by dynamically setting the language and UI text attributes.

```html title="Widget"
<elevenlabs-convai
  language="es"
  action-text={i18n["es"]["actionText"]}
  start-call-text={i18n["es"]["startCall"]}
  end-call-text={i18n["es"]["endCall"]}
  expand-text={i18n["es"]["expand"]}
  listening-text={i18n["es"]["listening"]}
  speaking-text={i18n["es"]["speaking"]}
></elevenlabs-convai>
```

<Note>
  Ensure the language codes match between your i18n framework and the agent's supported languages.
</Note>

## Best practices

<AccordionGroup>
<Accordion title="Voice selection">
  Select voices specifically trained in your target languages. This ensures:
  - Natural pronunciation
  - Appropriate regional accents
  - Better handling of language-specific nuances
</Accordion>

<Accordion title="First message customization">
While automatic translations are provided, consider:

<div>
  
 - Reviewing translations for accuracy 
 - Adapting greetings for cultural context 
 - Adjusting formal/informal tone as needed

</div>
</Accordion>
</AccordionGroup>


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
