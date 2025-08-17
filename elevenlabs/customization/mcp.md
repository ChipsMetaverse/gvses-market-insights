---
title: Model Context Protocol
subtitle: >-
  Connect your ElevenLabs conversational agents to external tools and data
  sources using the Model Context Protocol.
---

<Error title="User Responsibility">
  You are responsible for the security, compliance, and behavior of any third-party MCP server you
  integrate with your ElevenLabs conversational agents. ElevenLabs provides the platform for
  integration but does not manage, endorse, or secure external MCP servers.
</Error>

## Overview

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) is an open standard that defines how applications provide context to Large Language Models (LLMs). Think of MCP as a universal connector that enables AI models to seamlessly interact with diverse data sources and tools. By integrating servers that implement MCP, you can significantly extend the capabilities of your ElevenLabs conversational agents.

<Frame background="subtle">
  <iframe
    width="100%"
    height="400"
    src="https://www.youtube.com/embed/7WLfKp7FpD8"
    title="ElevenLabs Model Context Protocol integration"
    frameBorder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowFullScreen
  />
</Frame>

<Note>
  MCP support is not currently available for users on Zero Retention Mode or those requiring HIPAA
  compliance.
</Note>

ElevenLabs allows you to connect your conversational agents to external MCP servers. This enables your agents to:

- Access and process information from various data sources via the MCP server
- Utilize specialized tools and functionalities exposed by the MCP server
- Create more dynamic, knowledgeable, and interactive conversational experiences

## Getting started

<Note>
  ElevenLabs supports both SSE (Server-Sent Events) and HTTP streamable transport MCP servers.
</Note>

1. Retrieve the URL of your MCP server. In this example, we'll use [Zapier MCP](https://zapier.com/mcp), which lets you connect Conversational AI to hundreds of tools and services.

2. Navigate to the [MCP server integrations dashboard](https://elevenlabs.io/app/conversational-ai/integrations) and click "Add Custom MCP Server".

   <Frame background="subtle">
     ![Creating your first MCP server](file:a4757a5e-07da-446f-bfa3-ce58ae3460dd)
   </Frame>

3. Configure the MCP server with the following details:

   - **Name**: The name of the MCP server (e.g., "Zapier MCP Server")
   - **Description**: A description of what the MCP server can do (e.g., "An MCP server with access to Zapier's tools and services")
   - **Server URL**: The URL of the MCP server. In some cases this contains a secret key, treat it like a password and store it securely as a workspace secret.
   - **Secret Token (Optional)**: If the MCP server requires a secret token (Authorization header), enter it here.
   - **HTTP Headers (Optional)**: If the MCP server requires additional HTTP headers, enter them here.

4. Click "Add Integration" to save the integration and test the connection to list available tools.

   <Frame background="subtle">
     ![Zapier example tools](file:05039934-dc77-4544-bff3-70becebbb2bf)
   </Frame>

5. The MCP server is now available to add to your agents. MCP support is available for both public and private agents.

   <Frame background="subtle">
     ![Adding the MCP server to an agent](file:fe910274-e661-4e00-8341-a29e9594cb6a)
   </Frame>

## Tool approval modes

ElevenLabs provides flexible approval controls to manage how agents request permission to use tools from MCP servers. You can configure approval settings at both the MCP server level and individual tool level for maximum security control.

<Frame background="subtle">
  ![Tool approval mode settings](file:15789d44-3c2f-4c29-9634-e4eaf11f9433)
</Frame>

### Available approval modes

- **Always Ask (Recommended)**: Maximum security. The agent will request your permission before each tool use.
- **Fine-Grained Tool Approval**: Disable and pre-select tools which can run automatically and those requiring approval.
- **No Approval**: The assistant can use any tool without approval.

### Fine-grained tool control

The Fine-Grained Tool Approval mode allows you to configure individual tools with different approval requirements, giving you precise control over which tools can run automatically and which require explicit permission.

<Frame background="subtle">
  ![Fine-grained tool approval
  settings](file:f23cfbf4-bdf0-4109-b00d-e1238a918de2)
</Frame>

For each tool, you can set:

- **Auto-approved**: Tool runs automatically without requiring permission
- **Requires approval**: Tool requires explicit permission before execution
- **Disabled**: Tool is completely disabled and cannot be used

<Tip>
  Use Fine-Grained Tool Approval to allow low-risk read-only tools to run automatically while
  requiring approval for tools that modify data or perform sensitive operations.
</Tip>

## Key considerations for ElevenLabs integration

- **External servers**: You are responsible for selecting the external MCP servers you wish to integrate. ElevenLabs provides the means to connect to them.
- **Supported features**: ElevenLabs supports MCP servers that communicate over SSE (Server-Sent Events) and HTTP streamable transports for real-time interactions.
- **Dynamic tools**: The tools and capabilities available from an integrated MCP server are defined by that external server and can change if the server's configuration is updated.

## Security and disclaimer

Integrating external MCP servers can expose your agents and data to third-party services. It is crucial to understand the security implications.

<Warning title="Important Disclaimer">
  By enabling MCP server integrations, you acknowledge that this may involve data sharing with
  third-party services not controlled by ElevenLabs. This could incur additional security risks.
  Please ensure you fully understand the implications, vet the security of any MCP server you
  integrate, and review our [MCP Integration Security
  Guidelines](/docs/conversational-ai/customization/mcp/security) before proceeding.
</Warning>

Refer to our [MCP Integration Security Guidelines](/docs/conversational-ai/customization/mcp/security) for detailed best practices.

## Finding or building MCP servers

- Utilize publicly available MCP servers from trusted providers
- Develop your own MCP server to expose your proprietary data or tools
- Explore the Model Context Protocol community and resources for examples and server implementations

### Resources

- [Anthropic's MCP server examples](https://docs.anthropic.com/en/docs/agents-and-tools/remote-mcp-servers#remote-mcp-server-examples) - A list of example servers by Anthropic
- [Awesome Remote MCP Servers](https://github.com/jaw9c/awesome-remote-mcp-servers) - A curated, open-source list of remote MCP servers
- [Remote MCP Server Directory](https://remote-mcp.com/) - A searchable list of Remote MCP servers


---
title: MCP integration security
subtitle: >-
  Tips for securely integrating third-party Model Context Protocol servers with
  your ElevenLabs conversational agents.
---

<Error title="User Responsibility">
  You are responsible for the security, compliance, and behavior of any third-party MCP server you
  integrate with your ElevenLabs conversational agents. ElevenLabs provides the platform for
  integration but does not manage, endorse, or secure external MCP servers.
</Error>

## Overview

Integrating external servers via the Model Context Protocol (MCP) can greatly enhance your ElevenLabs conversational agents. However, this also means connecting to systems outside of ElevenLabs' direct control, which introduces important security considerations. As a user, you are responsible for the security and trustworthiness of any third-party MCP server you choose to integrate.

This guide outlines key security practices to consider when using MCP server integrations within ElevenLabs.

## Tool approval controls

ElevenLabs provides built-in security controls through tool approval modes that help you manage the security risks associated with MCP tool usage. These controls allow you to balance functionality with security based on your specific needs.

<Frame background="subtle">
  ![Tool approval mode settings](file:15789d44-3c2f-4c29-9634-e4eaf11f9433)
</Frame>

### Approval mode options

- **Always Ask (Recommended)**: Provides maximum security by requiring explicit approval for every tool execution. This mode ensures you maintain full control over all MCP tool usage.
- **Fine-Grained Tool Approval**: Allows you to configure approval requirements on a per-tool basis, enabling automatic execution of trusted tools while requiring approval for sensitive operations.
- **No Approval**: Permits unrestricted tool usage without approval prompts. Only use this mode with thoroughly vetted and highly trusted MCP servers.

### Fine-grained security controls

Fine-Grained Tool Approval mode provides the most flexible security configuration, allowing you to classify each tool based on its risk profile:

<Frame background="subtle">
  ![Fine-grained tool approval
  settings](file:f23cfbf4-bdf0-4109-b00d-e1238a918de2)
</Frame>

- **Auto-approved tools**: Suitable for low-risk, read-only operations or tools you completely trust
- **Approval-required tools**: For tools that modify data, access sensitive information, or perform potentially risky operations
- **Disabled tools**: Completely block tools that are unnecessary or pose security risks

<Warning>
  Even with approval controls in place, carefully evaluate the trustworthiness of MCP servers and
  understand what each tool can access or modify before integration.
</Warning>

## Security tips

### 1. Vet your MCP servers

- **Trusted Sources**: Only integrate MCP servers from sources you trust and have verified. Understand who operates the server and their security posture.
- **Understand Capabilities**: Before integrating, thoroughly review the tools and data resources the MCP server exposes. Be aware of what actions its tools can perform (e.g., accessing files, calling external APIs, modifying data). The MCP `destructiveHint` and `readOnlyHint` annotations can provide clues but should not be solely relied upon for security decisions.
- **Review Server Security**: If possible, review the security practices of the MCP server provider. For MCP servers you develop, ensure you follow general server security best practices and the MCP-specific security guidelines.

### 2. Data sharing and privacy

- **Data Flow**: Be aware that when your agent uses an integrated MCP server, data from the conversation (which may include user inputs) will be sent to that external server.
- **Sensitive Information**: Exercise caution when allowing agents to send Personally Identifiable Information (PII) or other sensitive data to an MCP server. Ensure the server handles such data securely and in compliance with relevant privacy regulations.
- **Purpose Limitation**: Configure your agents and prompts to only share the necessary information with MCP server tools to perform their tasks.

### 3. Credential and connection security

- **Secure Storage**: If an MCP server requires API keys or other secrets for authentication, use any available secret management features within the ElevenLabs platform to store these credentials securely. Avoid hardcoding secrets.
- **HTTPS**: Ensure connections to MCP servers are made over HTTPS to encrypt data in transit.
- **Network Access**: If the MCP server is on a private network, ensure appropriate firewall rules and network ACLs are in place.

### 4. Understand code execution risks

- **Remote Execution**: Tools exposed by an MCP server execute code on that server. While this is the basis of their functionality, it's a critical security consideration. Malicious or poorly secured tools could pose a risk.
- **Input Validation**: Although the MCP server is responsible for validating inputs to its tools, be mindful of the data your agent might send. The LLM should be guided to use tools as intended.

### 5. Add guardrails

- **Prompt Injections**: Connecting to untrusted external MCP servers exposes the risk of prompt injection attacks. Ensure to add thorough guardrails to your system prompt to reduce the risk of exposure to a malicious attack.
- **Tool Approval Configuration**: Use the appropriate approval mode for your security requirements. Start with "Always Ask" for new integrations and only move to less restrictive modes after thorough testing and trust establishment.

### 6. Monitor and review

- **Logging (Server-Side)**: If you control the MCP server, implement comprehensive logging of tool invocations and data access.
- **Regular Review**: Periodically review your integrated MCP servers. Check if their security posture has changed or if new tools have been added that require re-assessment.
- **Approval Patterns**: Monitor tool approval requests to identify unusual patterns that might indicate security issues or misuse.

## Disclaimer

<Warning title="Important Disclaimer">
  By enabling MCP server integrations, you acknowledge that this may involve data sharing with
  third-party services not controlled by ElevenLabs. This could incur additional security risks.
  Please ensure you fully understand the implications, vet the security of any MCP server you
  integrate, and adhere to these security guidelines before proceeding.
</Warning>

For general information on the Model Context Protocol, refer to official MCP documentation and community resources.
