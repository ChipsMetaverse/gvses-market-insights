---
title: Voice customization
subtitle: Learn how to customize your AI agent's voice and speech patterns.
---

## Overview

You can customize various aspects of your AI agent's voice to create a more natural and engaging conversation experience. This includes controlling pronunciation, speaking speed, and language-specific voice settings.

## Available customizations

<CardGroup cols={2}>
  <Card
    title="Multi-voice support"
    icon="microphone-lines"
    href="/docs/conversational-ai/customization/voice/multi-voice-support"
  >
    Enable your agent to switch between different voices for multi-character conversations,
    storytelling, and language tutoring.
  </Card>
  <Card
    title="Pronunciation dictionary"
    icon="microphone-stand"
    href="/docs/conversational-ai/customization/voice/pronunciation-dictionary"
  >
    Control how your agent pronounces specific words and phrases using
    [IPA](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet) or
    [CMU](https://en.wikipedia.org/wiki/CMU_Pronouncing_Dictionary) notation.
  </Card>
  <Card
    title="Speed control"
    icon="waveform"
    href="/docs/conversational-ai/customization/voice/speed-control"
  >
    Adjust how quickly or slowly your agent speaks, with values ranging from 0.7x to 1.2x.
  </Card>
  <Card
    title="Language-specific voices"
    icon="language"
    href="/docs/conversational-ai/customization/language"
  >
    Configure different voices for each supported language to ensure natural pronunciation.
  </Card>
</CardGroup>

## Best practices

<AccordionGroup>
  <Accordion title="Voice selection">
    Choose voices that match your target language and region for the most natural pronunciation.
    Consider testing multiple voices to find the best fit for your use case.
  </Accordion>
  <Accordion title="Speed optimization">
    Start with the default speed (1.0) and adjust based on your specific needs. Test different
    speeds with your content to find the optimal balance between clarity and natural flow.
  </Accordion>
  <Accordion title="Pronunciation dictionaries">
    Focus on terms specific to your business or use case that need consistent pronunciation and are
    not widely used in everyday conversation. Test pronunciations with your chosen voice and model
    combination.
  </Accordion>
</AccordionGroup>

<Note>
  Some voice customization features may be model-dependent. For example, phoneme-based pronunciation
  control is only available with the Turbo v2 model.
</Note>


---
title: Multi-voice support
subtitle: >-
  Enable your AI agent to switch between different voices for multi-character
  conversations and enhanced storytelling.
---

## Overview

Multi-voice support allows your conversational AI agent to dynamically switch between different ElevenLabs voices during a single conversation. This powerful feature enables:

- **Multi-character storytelling**: Different voices for different characters in narratives
- **Language tutoring**: Native speaker voices for different languages
- **Emotional agents**: Voice changes based on emotional context
- **Role-playing scenarios**: Distinct voices for different personas

<Frame background="subtle">
  <img
    src="file:5ab86c2d-7b99-49a4-90f3-0319781d0db4"
    alt="Multi-voice configuration interface"
  />
</Frame>

## How it works

When multi-voice support is enabled, your agent can use XML-style markup to switch between configured voices during text generation. The agent automatically returns to the default voice when no specific voice is specified.

<CodeBlocks>
```xml title="Example voice switching"
The teacher said, <spanish>¡Hola estudiantes!</spanish> 
Then the student replied, <student>Hello! How are you today?</student>
```

```xml title="Multi-character dialogue"
<narrator>Once upon a time, in a distant kingdom...</narrator>
<princess>I need to find the magic crystal!</princess>
<wizard>The crystal lies beyond the enchanted forest.</wizard>
```

</CodeBlocks>

## Configuration

### Adding supported voices

Navigate to your agent settings and locate the **Multi-voice support** section under the `Voice` tab.

<Steps>

### Add a new voice

Click **Add voice** to configure a new supported voice for your agent.

<Frame background="subtle">
  <img
    src="file:9f7a953e-0996-4772-be32-e4cdcb03a961"
    alt="Multi-voice configuration interface"
  />
</Frame>

### Configure voice properties

Set up the voice with the following details:

- **Voice label**: Unique identifier (e.g., "Joe", "Spanish", "Happy")
- **Voice**: Select from your available ElevenLabs voices
- **Model Family**: Choose Turbo, Flash, or Multilingual (optional)
- **Language**: Override the default language for this voice (optional)
- **Description**: When the agent should use this voice

### Save configuration

Click **Add voice** to save the configuration. The voice will be available for your agent to use immediately.

</Steps>

### Voice properties

<AccordionGroup>
  <Accordion title="Voice label">
    A unique identifier that the LLM uses to reference this voice. Choose descriptive labels like: -
    Character names: "Alice", "Bob", "Narrator" - Languages: "Spanish", "French", "German" -
    Emotions: "Happy", "Sad", "Excited" - Roles: "Teacher", "Student", "Guide"
  </Accordion>

<Accordion title="Model family">
  Override the agent's default model family for this specific voice: - **Flash**: Fastest eneration,
  optimized for real-time use - **Turbo**: Balanced speed and quality - **Multilingual**: Highest
  quality, best for non-English languages - **Same as agent**: Use agent's default setting
</Accordion>

<Accordion title="Language override">
  Specify a different language for this voice, useful for: - Multilingual conversations - Language
  tutoring applications - Region-specific pronunciations
</Accordion>

  <Accordion title="Description">
    Provide context for when the agent should use this voice. 
    Examples: 
    - "For any Spanish words or phrases" 
    - "When the message content is joyful or excited" 
    - "Whenever the character Joe is speaking"
  </Accordion>
</AccordionGroup>

## Implementation

### XML markup syntax

Your agent uses XML-style tags to switch between voices:

```xml
<VOICE_LABEL>text to be spoken</VOICE_LABEL>
```

**Key points:**

- Replace `VOICE_LABEL` with the exact label you configured
- Text outside tags uses the default voice
- Tags are case-sensitive
- Nested tags are not supported

### System prompt integration

When you configure supported voices, the system automatically adds instructions to your agent's prompt:

```
When a message should be spoken by a particular person, use markup: "<CHARACTER>message</CHARACTER>" where CHARACTER is the character label.

Available voices are as follows:
- default: any text outside of the CHARACTER tags
- Joe: Whenever Joe is speaking
- Spanish: For any Spanish words or phrases
- Narrator: For narrative descriptions
```

### Example usage

<Tabs>

    <Tab title="Language tutoring">
        ```
        Teacher: Let's practice greetings. In Spanish, we say <Spanish>¡Hola! ¿Cómo estás?</Spanish>
        Student: How do I respond?
        Teacher: You can say <Spanish>¡Hola! Estoy bien, gracias.</Spanish> which means Hello! I'm fine, thank you.
        ```
    </Tab>

    <Tab title="Storytelling">
      ```
      Once upon a time, a brave princess ventured into a dark cave.
      <Princess>I'm not afraid of you, dragon!</Princess> she declared boldly. The dragon rumbled from
      the shadows, <Dragon>You should be, little one.</Dragon>
      But the princess stood her ground, ready for whatever came next.
      ```
    </Tab>

</Tabs>

## Best practices

<AccordionGroup>

<Accordion title="Voice selection">

- Choose voices that clearly differentiate between characters or contexts
- Test voice combinations to ensure they work well together
- Consider the emotional tone and personality for each voice
- Ensure voices match the language and accent when switching languages

</Accordion>

<Accordion title="Label naming">

- Use descriptive, intuitive labels that the LLM can understand
- Keep labels short and memorable
- Avoid special characters or spaces in labels

</Accordion>

<Accordion title="Performance optimization">

- Limit the number of supported voices to what you actually need
- Use the same model family when possible to reduce switching overhead
- Test with your expected conversation patterns
- Monitor response times with multiple voice switches

</Accordion>

  <Accordion title="Content guidelines">
    - Provide clear descriptions for when each voice should be used 
    - Test edge cases where voice switching might be unclear
     - Consider fallback behavior when voice labels are ambiguous 
     - Ensure voice switches enhance rather than distract from the conversation
  </Accordion>
  
</AccordionGroup>

## Limitations

<Note>

- Maximum of 10 supported voices per agent (including default)
- Voice switching adds minimal latency during generation
- XML tags must be properly formatted and closed
- Voice labels are case-sensitive in markup
- Nested voice tags are not supported

</Note>

## FAQ

<AccordionGroup>

    <Accordion title="What happens if I use an undefined voice label?">
        If the agent uses a voice label that hasn't been configured, the text will be spoken using the
        default voice. The XML tags will be ignored.
    </Accordion>

    <Accordion title="Can I change voices mid-sentence?">
    Yes, you can switch voices within a single response. Each tagged section will use the specified
    voice, while untagged text uses the default voice.
    </Accordion>


    <Accordion title="Do voice switches affect conversation latency?">
    Voice switching adds minimal overhead. The first use of each voice in a conversation may have
    slightly higher latency as the voice is initialized.
    </Accordion>


    <Accordion title="Can I use the same voice with different labels?">
    Yes, you can configure multiple labels that use the same ElevenLabs voice but with different model
    families, languages, or contexts.
    </Accordion>

    <Accordion title="How do I train my agent to use voice switching effectively?">
        Provide clear examples in your system prompt and test thoroughly. You can include specific
        scenarios where voice switching should occur and examples of the XML markup format.
    </Accordion>

</AccordionGroup>


---
title: Pronunciation dictionaries
subtitle: Learn how to control how your AI agent pronounces specific words and phrases.
---

## Overview

Pronunciation dictionaries allow you to customize how your AI agent pronounces specific words or phrases. This is particularly useful for:

- Correcting pronunciation of names, places, or technical terms
- Ensuring consistent pronunciation across conversations
- Customizing regional pronunciation variations

<Frame background="subtle">
  <img
    src="file:955281b5-05e4-46ae-aeb2-a872ac559c34"
    alt="Pronunciation dictionary settings under the Voice tab"
  />
</Frame>

## Configuration

You can find the pronunciation dictionary settings under the **Voice** tab in your agent's configuration.

<Note>
  The phoneme function of pronunciation dictionaries only works with the Turbo v2 model, while the
  alias function works with all models.
</Note>

## Dictionary file format

Pronunciation dictionaries use XML-based `.pls` files. Here's an example structure:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<lexicon version="1.0"
      xmlns="http://www.w3.org/2005/01/pronunciation-lexicon"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.w3.org/2005/01/pronunciation-lexicon
        http://www.w3.org/TR/2007/CR-pronunciation-lexicon-20071212/pls.xsd"
      alphabet="ipa" xml:lang="en-GB">
  <lexeme>
    <grapheme>Apple</grapheme>
    <phoneme>ˈæpl̩</phoneme>
  </lexeme>
  <lexeme>
    <grapheme>UN</grapheme>
    <alias>United Nations</alias>
  </lexeme>
</lexicon>
```

## Supported formats

We support two types of pronunciation notation:

1. **IPA (International Phonetic Alphabet)**

   - More precise control over pronunciation
   - Requires knowledge of IPA symbols
   - Example: "nginx" as `/ˈɛndʒɪnˈɛks/`

2. **CMU (Carnegie Mellon University) Dictionary format**
   - Simpler ASCII-based format
   - More accessible for English pronunciations
   - Example: "tomato" as "T AH M EY T OW"

<Tip>
  You can use AI tools like Claude or ChatGPT to help generate IPA or CMU notations for specific
  words.
</Tip>

## Best practices

1. **Case sensitivity**: Create separate entries for capitalized and lowercase versions of words if needed
2. **Testing**: Always test pronunciations with your chosen voice and model
3. **Maintenance**: Keep your dictionary organized and documented
4. **Scope**: Focus on words that are frequently mispronounced or critical to your use case

## FAQ

<AccordionGroup>
  <Accordion title="Which models support phoneme-based pronunciation?">
    Currently, only the Turbo v2 model supports phoneme-based pronunciation. Other models will
    silently skip phoneme entries.
  </Accordion>
  <Accordion title="Can I use multiple dictionaries?">
    Yes, you can upload multiple dictionary files to handle different sets of pronunciations.
  </Accordion>
  <Accordion title="What happens if a word isn't in the dictionary?">
    The model will use its default pronunciation rules for any words not specified in the
    dictionary.
  </Accordion>
</AccordionGroup>

## Additional resources

- [Professional Voice Cloning](/docs/product-guides/voices/voice-cloning/professional-voice-cloning)
- [Voice Design](/docs/product-guides/voices/voice-design)
- [Text to Speech API Reference](/docs/api-reference/text-to-speech)


---
title: Speed control
subtitle: Learn how to adjust the speaking speed of your conversational AI agent.
---

## Overview

The speed control feature allows you to adjust how quickly or slowly your agent speaks. This can be useful for:

- Making speech more accessible for different audiences
- Matching specific use cases (e.g., slower for educational content)
- Optimizing for different types of conversations

<Frame background="subtle">
  <img
    src="file:468bd28d-12e3-4a2b-97c1-eff4487ae535"
    alt="Speed control settings under the Voice tab"
  />
</Frame>

## Configuration

Speed is controlled through the [`speed` parameter](/docs/api-reference/agents/create#request.body.conversation_config.tts.speed) with the following specifications:

- **Range**: 0.7 to 1.2
- **Default**: 1.0
- **Type**: Optional

## How it works

The speed parameter affects the pace of speech generation:

- Values below 1.0 slow down the speech
- Values above 1.0 speed up the speech
- 1.0 represents normal speaking speed

<Note>
  Extreme values near the minimum or maximum may affect the quality of the generated speech.
</Note>

## Best practices

- Start with the default speed (1.0) and adjust based on user feedback
- Test different speeds with your specific content
- Consider your target audience when setting the speed
- Monitor speech quality at extreme values

<Warning>Values outside the 0.7-1.2 range are not supported.</Warning>
