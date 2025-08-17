---
title: Privacy
subtitle: Manage how your agent handles data storage and privacy.
---

Privacy settings give you fine-grained control over your data. You can manage both call audio recordings and conversation data retention to meet your compliance and privacy requirements.

<CardGroup cols={3}>
  <Card
    title="Retention"
    icon="database"
    href="/docs/conversational-ai/customization/privacy/retention"
  >
    Configure how long conversation transcripts and audio recordings are retained.
  </Card>
  <Card
    title="Audio Saving"
    icon="microphone"
    href="/docs/conversational-ai/customization/privacy/audio-saving"
  >
    Control whether call audio recordings are retained.
  </Card>
  <Card
    title="Zero Retention Mode"
    icon="shield-check"
    href="/docs/conversational-ai/customization/privacy/zero-retention-mode"
  >
    Enable per-agent zero retention for enhanced data privacy.
  </Card>
</CardGroup>

## Retention

Retention settings control the duration for which conversation transcripts and audio recordings are stored.

For detailed instructions, see our [Retention](/docs/conversational-ai/customization/privacy/retention) page.

## Audio Saving

Audio Saving settings determine if call audio recordings are stored. Adjust this feature based on your privacy and data retention needs.

For detailed instructions, see our [Audio Saving](/docs/conversational-ai/customization/privacy/audio-saving) page.

## Zero Retention Mode (Per Agent)

For granular control, Zero Retention Mode can be enabled for individual agents, ensuring no PII is logged or stored for their calls.

For detailed instructions, see our [Zero Retention Mode](/docs/conversational-ai/customization/privacy/zero-retention-mode) page.

## Recommended Privacy Configurations

<AccordionGroup>
  <Accordion title="Maximum Privacy">
    Disable audio saving, enable Zero Retention Mode for agents where possible, and set retention to
    0 days for immediate deletion of data.
  </Accordion>
  <Accordion title="Balanced Privacy">
    Enable audio saving for critical interactions while setting a moderate retention period.
    Consider ZRM for sensitive agents.
  </Accordion>
  <Accordion title="Compliance Focus">
    Enable audio saving and configure retention settings to adhere to regulatory requirements such
    as GDPR and HIPAA. For HIPAA compliance, we recommend enabling audio saving and setting a
    retention period of at least 6 years. For GDPR, retention periods should align with your data
    processing purposes. Utilize ZRM for agents handling highly sensitive data if not using global
    ZRM.
  </Accordion>
</AccordionGroup>


---
title: Retention
subtitle: Control how long your agent retains conversation history and recordings.
---

**Retention** settings allow you to configure how long your Conversational AI agent stores conversation transcripts and audio recordings. These settings help you comply with data privacy regulations.

## Overview

By default, ElevenLabs retains conversation data for 2 years. You can modify this period to:

- Any number of days (e.g., 30, 90, 365)
- Unlimited retention by setting the value to -1
- Immediate deletion by setting the value to 0

The retention settings apply separately to:

- **Conversation transcripts**: Text records of all interactions
- **Audio recordings**: Voice recordings from both the user and agent

<Info>
  For GDPR compliance, we recommend setting retention periods that align with your data processing
  purposes. For HIPAA compliance, retain records for a minimum of 6 years.
</Info>

## Modifying retention settings

### Prerequisites

- An [ElevenLabs account](https://elevenlabs.io)
- A configured ElevenLabs Conversational Agent ([create one here](/docs/conversational-ai/quickstart))

Follow these steps to update your retention settings:

<Steps>
  <Step title="Access retention settings">
    Navigate to your agent's settings and select the "Advanced" tab. The retention settings are located in the "Data Retention" section.

    <Frame background="subtle">
      ![Enable overrides](file:fe52eae7-a003-46b0-ac07-929b48e7e3fb)
    </Frame>

  </Step>

  <Step title="Update retention period">
    1. Enter the desired retention period in days
    2. Choose whether to apply changes to existing data
    3. Click "Save" to confirm changes

    <Frame background="subtle">
      ![Enable overrides](file:897aba98-60d4-4a83-8d55-839492664f65)
    </Frame>

    When modifying retention settings, you'll have the option to apply the new retention period to existing conversation data or only to new conversations going forward.

  </Step>
</Steps>

<Warning>
  Reducing the retention period may result in immediate deletion of data older than the new
  retention period if you choose to apply changes to existing data.
</Warning>


---
title: Audio saving
subtitle: Control whether call audio recordings are retained.
---

**Audio Saving** settings allow you to choose whether recordings of your calls are retained in your call history, on a per-agent basis. This control gives you flexibility over data storage and privacy.

## Overview

By default, audio recordings are enabled. You can modify this setting to:

- **Enable audio saving**: Save call audio for later review.
- **Disable audio saving**: Omit audio recordings from your call history.

<Info>
  Disabling audio saving enhances privacy but limits the ability to review calls. However,
  transcripts can still be viewed. To modify transcript retention settings, please refer to the
  [retention](/docs/conversational-ai/customization/privacy/retention) documentation.
</Info>

## Modifying Audio Saving Settings

### Prerequisites

- A configured [ElevenLabs Conversational Agent](/docs/conversational-ai/quickstart)

Follow these steps to update your audio saving preference:

<Steps>
  <Step title="Access audio saving settings">
    Find your agent in the Conversational AI agents
    [page](https://elevenlabs.io/app/conversational-ai/agents) and select the "Advanced" tab. The
    audio saving control is located in the "Privacy Settings" section.
    <Frame background="subtle">
      ![Disable audio saving option](file:e54f1014-48be-43c3-b0a5-f8a94f546d29)
    </Frame>
  </Step>
  <Step title="Choose saving option">
    Toggle the control to enable or disable audio saving and click save to confirm your selection.
  </Step>
  <Step title="Review call history">
    When audio saving is enabled, calls in the call history allow you to review the audio.
    <Frame background="subtle">
      ![Call with audio saved](file:b620b2cd-3dc6-4318-922d-8a72b91aaa57)
    </Frame>
    When audio saving is disabled, calls in the call history do not include audio.
    <Frame background="subtle">
      ![Call without audio saved](file:36264d9f-f8b6-46f2-b02f-c0bc9d9daf20)
    </Frame>
  </Step>
</Steps>

<Warning>
  Disabling audio saving will prevent new call audio recordings from being stored. Existing
  recordings will remain until deleted via [retention
  settings](/docs/conversational-ai/customization/privacy/retention).
</Warning>



---
title: Zero Retention Mode (per-agent)
subtitle: >-
  Learn how to enable Zero Retention Mode for individual agents to enhance data
  privacy.
---

## Overview

Zero Retention Mode (ZRM) enhances data privacy by ensuring that no Personally Identifiable Information (PII) is logged during or stored after a call. This feature can be enabled on a per-agent basis for workspaces that do not have ZRM enforced globally. For workspaces with global ZRM enabled, all agents will automatically operate in Zero Retention Mode.

When ZRM is active for an agent:

- No call recordings will be stored.
- No transcripts or call metadata containing PII will be logged or stored by our systems post-call.

For more information about setting your workspace to have Zero Retention Mode across all eligible ElevenLabs products, see our [Zero Retention Mode](/docs/resources/zero-retention-mode) documentation.

<Note>
  For workspaces where Zero Retention Mode is enforced globally, this setting will be automatically
  enabled for all agents and cannot be disabled on a per-agent basis.
</Note>

To retrieve information about calls made with ZRM-enabled agents, you must use [post-call webhooks](/docs/conversational-ai/workflows/post-call-webhooks).

<Warning>
  Enabling Zero Retention Mode may impact ElevenLabs' ability to debug call-related issues for the
  specific agent, as limited logs or call data will be available for review.
</Warning>

## How to Enable ZRM per Agent

For workspaces not operating under global Zero Retention Mode, you can enable ZRM for individual agents:

1.  Navigate to your agent's settings.
2.  Go to the **Privacy** settings block.
3.  Select the **Advanced** tab.
4.  Toggle the "Zero Retention Mode" option to enabled.

<Frame background="subtle" caption="Enabling Zero Retention Mode for an agent in Privacy Settings.">
  <img
    src="file:fde34ea7-5c4f-440e-b673-3e3cacd058b9"
    alt="Enable Zero Retention Mode for Agent"
  />
</Frame>
