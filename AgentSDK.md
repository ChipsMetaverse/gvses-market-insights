Agent Builder

Agent Builder
=============

Visually assemble, debug, and export multi-step agent workflows from the playground.

**Agent Builder** is a visual canvas for building multi-step agent workflows.

You can start from templates, drag and drop nodes for each step in your workflow, provide typed inputs and outputs, and preview runs using live data. When you're ready to deploy, embed the workflow into your site with ChatKit, or download the SDK code to run it yourself.

Use this guide to learn the process and parts of building agents.

Agents and workflows
--------------------

To build useful agents, you create workflows for them. A **workflow** is a combination of agents, tools, and control-flow logic. A workflow encapsulates all steps and actions involved in handling your tasks or powering your chats, with working code you can deploy when you're ready.

[Open Agent Builder](/agent-builder)  
  

There are three main steps in building agents to handle tasks:

1.  Design a workflow in [Agent Builder](/agent-builder). This defines your agents and how they'll work.
2.  Publish your workflow. It's an object with an ID and versioning.
3.  Deploy your workflow. Pass the ID into your [ChatKit](/docs/guides/chatkit) integration, or download the Agents SDK code to deploy your workflow yourself.

Compose with nodes
------------------

In Agent Builder, insert and connect nodes to create your workflow. Each connection between nodes becomes a typed edge. Click a node to configure its inputs and outputs, observe the data contract between steps, and ensure downstream nodes receive the properties they expect.

### Examples and templates

Agent Builder provides templates for common workflow patterns. Start with a template to see how nodes work together, or start from scratch.

Here's a homework helper workflow. It uses agents to take questions, reframe them for better answers, route them to other specialized agents, and return an answer.

![prompts chat](https://cdn.openai.com/API/docs/images/homework-helper2.png)

### Available nodes

Nodes are the building blocks for agents. To see all availble nodes and their configuration options, see the [node reference documentation](/docs/guides/node-reference).

### Preview and debug

As you build, you can test your workflow by using the **Preview** feature. Here, you can interactively run your workflow, attach sample files, and observe the execution of each node.

### Safety and risks

Building agent workflows comes with risks, like prompt injection and data leakage. See [safety in building agents](/docs/guides/agent-builder-safety) to learn about and help mitigate the risks of agent workflows.

### Evaluate your workflow

Run [trace graders](/docs/guides/trace-grading) inside of Agent Builder. In the top navigation, click **Evaluate**. Here, you can select a trace (or set of traces) and run custom graders to assess overall workflow performance.

Publish your workflow
---------------------

Agent Builder autosaves your work as you go. When you're happy with your workflow, publish it to create a new major version that acts as a snapshot. You can then use your workflow in [ChatKit](/docs/guides/chatkit), an OpenAI framework for embedding chat experiences.

You can create new versions or specify an older version in your API calls.

Deploy in your product
----------------------

When you're ready to implement the agent workflow you created, click **Code** in the top navigation. You have two options for implementing your workflow in production:

**ChatKit**: Follow the [ChatKit quickstart](/docs/guides/chatkit) and pass in your workflow ID to embed this workflow into your application. If you're not sure, we recommend this option.

**Advanced integration**: Copy the workflow code and use it anywhere. You can run ChatKit on your own infrastructure and use the Agents SDK to build and customize agent chat experiences.

Next steps
----------

Now that you've created an agent workflow, bring it into your product with ChatKit.

*   [ChatKit quickstart](/docs/guides/chatkit) →
*   [Advanced integration](/docs/guides/custom-chatkit) →

Node reference
==============

Explore all available nodes for composing workflows in Agent Builder.

[Agent Builder](/agent-builder) is a visual canvas for composing agentic worfklows. Workflows are made up of nodes and connections that control the sequence and flow. Insert nodes, then configure and connect them to define the process you want your agents to follow.

Explore all available nodes below. To learn more, read the [Agent Builder guide](/docs/guides/agent-builder).

### Core nodes

Get started with basic building blocks. All workflows have start and agent nodes.

![core nodes](https://cdn.openai.com/API/docs/images/core-nodes2.png)

#### Start

Define inputs to your workflow. For user input in a chat workflow, start nodes do two things:

*   Append the user input to the conversation history
*   Expose `input_as_text` to represent the text contents of this input

All chat start nodes have `input_as_text` as an input variable. You can add state variables too.

#### Agent

Define instructions, tools, and model configuration, or attach evaluations.

Keep each agent well defined in scope. In our homework helper example, we use one agent to rewrite the user's query for more specificity and relevance with the knowledge base. We use another agent to classify the query as either Q&A or fact-finding, and another agent to field each type of question.

Add model behavior instructions and user messages as you would with any other model prompt. To pipe output from a previous step, you can add it as context.

You can have as many agent nodes as you'd like.

#### Note

Annotate prompts and share context. Unlike other nodes, notes don't _do_ anything in the flow. They're just comments.

### Tool nodes

Tool nodes let you equip your agents with tools and external services. You can retrieve data, monitor for misuse, and connect to external services.

![tool nodes](https://cdn.openai.com/API/docs/images/tool-nodes2.png)

#### File search

Retrieve data from vector stores you've created in the OpenAI platform. Search by vector store ID, and add a query for what the model should search for. You can use variables to include output from previous nodes in the workflow.

See the [file search documentation](/docs/guides/tools-file-search) to set up vector stores and see supported file types.

To search outside of your hosted storage with OpenAI, use [MCP](/docs/guides/node-reference#mcp) instead.

#### Guardrails

Set up input monitors for unwanted inputs such as personally identifiable information (PII), jailbreaks, hallucinations, and other misuse.

Guardrails are pass/fail by default, meaning they test the output from a previous node, and you define what happens next. When there's a guardrails failure, we recommend either ending the workflow or returning to the previous step with a reminder of safe use.

#### MCP

Call third-party tools and services. Connect with OpenAI connectors or third-party servers, or add your own server. MCP connections are helpful in a workflow that needs to read or search data in another application, like Gmail or Zapier.

Browse options in the Agent Builder. To learn more about MCP, see the [connectors and MCP documentation](/docs/guides/tools-connectors-mcp).

### Logic nodes

![logic nodes](https://cdn.openai.com/API/docs/images/logic-nodes.png)

Logic nodes let you write custom logic and define the control flow—for example, looping on custom conditions, or asking the user for approval before continuing an operation.

#### If/else

Add conditional logic. Use [Common Expression Language](https://cel.dev/) (CEL) to create a custom expression. Useful for defining what to do with input that's been sorted into classifications.

For example, if an agent classifies input as Q&A, route that query to the Q&A agent for a straightforward answer. If it's an open-ended query, route to an agent that finds relevant facts. Else, end the workflow.

#### While

Loop on custom conditions. Use [Common Expression Language](https://cel.dev/) (CEL) to create a custom expression. Useful for situations

#### Human approval

Defer to end-users for approval. Useful for workflows where agents draft work that could use a human review before it goes out.

For example, picture an agent workflow that sends emails on your behalf. You'd include an agent node that outputs an email widget, then a human approval node immediately following. You can configure the human approval node to ask, "Would you like me to send this email?" and, if approved, proceeds to an MCP node that connects to Gmail.

### Data nodes

Data nodes let you define and manipulate data in your workflow. Reshape outputs or define global variables for use across your workflow.

![data nodes](https://cdn.openai.com/API/docs/images/data-nodes.png)

#### Transform

Reshape outputs (e.g., object → array). Useful for enforcing types to adhere to your schema or reshaping outputs for agents to read and understand as inputs.

#### Set state

Define global variables for use across the workflow. Useful for when an agent takes input and outputs something new that you'll want to use throughout the workflow. You can define that output as a new global variable.

Safety in building agents
=========================

Minimize prompt injections and other risks when building agents.

As you build and deploy agents with [Agent Builder](/docs/guides/agent-builder), it's important to understand the risks. Learn about risk types and how to mitigate them when building multi-agent workflows.

Types of risk
-------------

Certain agent workflow patterns are more vulnerable to risk. In chat workflows, two important considerations are protecting user input and being careful about MCP tool calling.

### Prompt injections

**Prompt injections** are a common and dangerous type of attack. A prompt injection happens when untrusted text or data enters an AI system, and malicious contents in that text or data attempt to override instructions to the AI. The end goals of prompt injections vary but can include exfiltrating private data via downstream tool calls, taking misaligned actions, or otherwise changing model behavior in an unintended way. For example, a prompt might trick a data lookup agent into sending raw customer records instead of the intended summary. See an example in context in the [Codex internet access docs](https://developers.openai.com/codex/cloud/internet-access/).

### Private data leakage

**Private data leakage**, when an agent accidentally shares private data, is also a risk to guard against. It's possible for a model to leak private data in a way that's not intended, without an attacker behind it. For example, a model may send more data to an MCP than the user expected or intended. While guardrails provide better control to limit the information included in context, you don't have full control over what the model chooses to share with connected MCPs.

Use the following guidance to reduce the attack surface and mitigate these risks. However, _even with these mitigations_, agents won’t be perfect and can still make mistakes or be tricked; as a result, it's important to understand these risks and use caution in what access you give agents and how you apply agents.

Don't use untrusted variables in developer messages
---------------------------------------------------

Because developer messages take precedence over user and assistant messages, injecting untrusted input directly into developer messages gives attackers the highest degree of control. Pass untrusted inputs through user messages to limit their influence. This is especially important for workflows where user inputs are passed to sensitive tools or privileged contexts.

Use structured outputs to constrain data flow
---------------------------------------------

Prompt injections often rely on the model freely generating unexpected text or commands that propagate downstream. By defining structured outputs between nodes (e.g., enums, fixed schemas, required field names), you eliminate freeform channels that attackers can exploit to smuggle instructions or data.

Steer the agent with clear guidance and examples
------------------------------------------------

Agent workflows may do something you don't want due to hallucination, misunderstanding, ambiguous user input, etc. For example, an agent may offer a refund it's not supposed to or delete information it shouldn't. The best way to mitigate this risk is to strengthen your prompts with good documentation of your desired policies and clear examples. Anticipate unintended scenarios and provide examples so the agent knows what to do in these cases.

Use GPT-5 or GPT-5-mini
-----------------------

These models are more disciplined about following developer instructions and exhibit stronger robustness against jailbreaks and indirect prompt injections. Configure these models at the agent node level for a more resilient default posture, especially for higher-risk workflows.

Keep tool approvals on
----------------------

When using MCP tools, always enable tool approvals so end users can review and confirm every operation, including reads and writes. In Agent Builder, use the [human approval](/docs/guides/node-reference#human-approval) node.

Use guardrails for user inputs
------------------------------

Sanitize incoming inputs using built-in [guardrails](/docs/guides/node-reference#guardrails) to redact personally identifiable information (PII) and detect jailbreak attempts. While the guardrails nodes in Agent Builder alone are not foolproof, they're an effective first wave of protection.

Run trace graders and evals
---------------------------

If you understand what models are doing, you can better catch and prevent mistakes. Use [evals](/docs/guides/evaluation-getting-started) to evaluate and improve performance. Trace grading provides scores and annotations to specific parts of an agent's trace—such as decisions, tool calls, or reasoning steps—to assess where the agent performed well or made mistakes.

Combine techniques
------------------

By combining these techniques and hardening critical steps, you can significantly reduce risks of prompt injection, malicious tool use, or unexpected agent behavior.

Design workflows so untrusted data never directly drives agent behavior. Extract only specific structured fields (e.g., enums or validated JSON) from external inputs to limit injection risk from flowing between nodes. Use guardrails, tool confirmations, and variables passed via user messages to validate inputs.

Risk rises when agents process arbitrary text that influences tool calls. Structured outputs and isolation greatly reduce, _but don’t fully remove_, this risk.


Agents SDK
==========

Learn how to build agents with the OpenAI Agents SDK.

Welcome to the OpenAI Agents SDK. This library makes it straightforward to build agentic applications—where a model can use additional context and tools, hand off to other specialized agents, stream partial results, and keep a full trace of what happened.

Below is a thorough overview. By the end of this guide, you’ll have a strong understanding of core concepts, best practices, and how to assemble a well-structured agent workflow.

Download and installation
-------------------------

Access the latest version in the following GitHub repositories:

*   [Agents SDK Python](https://github.com/openai/openai-agents-python)
*   [Agents SDK TypeScript](https://openai.github.io/openai-agents-js)

Documentation
-------------

Documentation for the Agents SDK lives [OpenAI Developers](https://developers.openai.com). Use quickstarts, guides, apps, and demos all in one place, under the [agents topic](https://developers.openai.com).

Was this page useful?