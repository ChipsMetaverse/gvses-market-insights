========================
CODE SNIPPETS
========================
TITLE: API Reference for List Conversational AI Tools Endpoint
DESCRIPTION: This section provides a detailed API reference for the `GET /v1/convai/tools` endpoint. It outlines the required headers, the structure of a successful response, and potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/tools/list

LANGUAGE: APIDOC
CODE:
```
GET /v1/convai/tools

Description: Get all available tools available in the workspace.

Headers:
  xi-api-key: string (Required)

Response (200 Retrieved):
  tools: array of objects
    id: string
    tool_config: object
      name: string
      description: string
      response_timeout_secs: integer
      type: string
      api_schema: object
        url: string
        method: string
        path_params_schema: object
        query_params_schema: object
          properties: object
          required: array of strings
        request_body_schema: object
          type: string
          required: array of strings
          description: string
          properties: object
        request_headers: object
        auth_connection: object
          auth_connection_id: string
      dynamic_variables: object
        dynamic_variable_placeholders: object
    access_info: object
      is_creator: boolean
      creator_name: string
      creator_email: string
      role: string

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs Get Tool API Reference: Parameters, Headers, and Response Structure
DESCRIPTION: Provides detailed API documentation for the ElevenLabs 'Get Tool' endpoint, outlining required path parameters (tool_id), necessary request headers (xi-api-key), the structure of a successful 200 OK response, and potential 422 Unprocessable Entity errors.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/tools/get

LANGUAGE: APIDOC
CODE:
```
Path parameters:
  tool_id (string, Required): ID of the requested tool.

Headers:
  xi-api-key (string, Required)

Response:
  200 Retrieved (Successful Response)
    id (string)
    tool_config (object): The type of tool
    access_info (object)

Errors:
  422 Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs Get Tool API Endpoint Definition
DESCRIPTION: Defines the HTTP GET endpoint for retrieving a specific tool from the ElevenLabs conversational AI platform, showing both the full URL and relative path.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/tools/get

LANGUAGE: APIDOC
CODE:
```
GET
https://api.elevenlabs.io/v1/convai/tools/:tool_id

GET
/v1/convai/tools/:tool_id
```

----------------------------------------

TITLE: API Reference: Delete Tool Endpoint
DESCRIPTION: Detailed API documentation for the DELETE /v1/convai/tools/:tool_id endpoint, outlining its purpose, required path parameters, necessary headers, and expected responses.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/tools/delete

LANGUAGE: APIDOC
CODE:
```
Endpoint: DELETE https://api.elevenlabs.io/v1/convai/tools/:tool_id

Description: Delete tool from the workspace.

Path Parameters:
  tool_id:
    type: string
    required: true
    description: ID of the requested tool.

Headers:
  xi-api-key:
    type: string
    required: true

Responses:
  Successful Response: 200 OK
  Errors:
    422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Example JSON Response for ElevenLabs Get Tool API
DESCRIPTION: Illustrates the expected JSON structure returned upon a successful retrieval of a tool from the ElevenLabs API, detailing the tool's ID, configuration (including API schema), and access information.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/tools/get

LANGUAGE: JSON
CODE:
```
{
"id": "foo",
"tool_config": {
"name": "foo",
"description": "foo",
"response_timeout_secs": 20,
"type": "webhook",
"api_schema": {
"url": "foo",
"method": "GET",
"path_params_schema": {},
"query_params_schema": {
"properties": {},
"required": [
"foo"
]
},
"request_body_schema": {
"type": "object",
"required": [
"foo"
],
"description": "",
"properties": {}
},
"request_headers": {},
"auth_connection": {
"auth_connection_id": "foo"
}
},
"dynamic_variables": {
"dynamic_variable_placeholders": {}
}
},
"access_info": {
"is_creator": true,
"creator_name": "foo",
"creator_email": "foo",
"role": "admin"
}
}
```

----------------------------------------

TITLE: Eleven Labs API: Get Tool Endpoint Reference
DESCRIPTION: Detailed API documentation for retrieving a specific tool from the Eleven Labs platform. This section outlines the HTTP method, endpoint URL, required path parameters, authentication headers, and the structure of the successful JSON response, including nested objects and their properties.

SOURCE: https://elevenlabs.io/docs/api-reference/tools/get

LANGUAGE: APIDOC
CODE:
```
Endpoint: GET /v1/convai/tools/:tool_id
Base URL: https://api.elevenlabs.io

Path Parameters:
  tool_id:
    Type: string
    Required: true
    Description: ID of the requested tool.

Headers:
  xi-api-key:
    Type: string
    Required: true
    Description: Your Eleven Labs API key for authentication.

Responses:
  200 Retrieved:
    Description: Successful Response
    Body Schema:
      id: string
      tool_config: object (The type of tool)
      access_info: object

  422 Unprocessable Entity Error:
    Description: Indicates that the request could not be processed due to semantic errors.
```

LANGUAGE: JSON
CODE:
```
{
  "id": "foo",
  "tool_config": {
    "name": "foo",
    "description": "foo",
    "response_timeout_secs": 20,
    "type": "webhook",
    "api_schema": {
      "url": "foo",
      "method": "GET",
      "path_params_schema": {},
      "query_params_schema": {
        "properties": {},
        "required": [
          "foo"
        ]
      },
      "request_body_schema": {
        "type": "object",
        "required": [
          "foo"
        ],
        "description": "",
        "properties": {}
      },
      "request_headers": {},
      "auth_connection": {
        "auth_connection_id": "foo"
      }
    },
    "dynamic_variables": {
      "dynamic_variable_placeholders": {}
    }
  },
  "access_info": {
    "is_creator": true,
    "creator_name": "foo",
    "creator_email": "foo",
    "role": "admin"
  }
}
```

----------------------------------------

TITLE: Retrieve ElevenLabs Conversational AI Tool using Python Client
DESCRIPTION: This Python example demonstrates how to use the ElevenLabs client library to fetch a specific conversational AI tool. It requires an API key and the tool's ID for authentication and identification.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/tools/get

LANGUAGE: Python
CODE:
```
from elevenlabs import ElevenLabs

client = ElevenLabs(
    api_key="YOUR_API_KEY",
)
client.conversational_ai.tools.get(
    tool_id="tool_id",
)
```

----------------------------------------

TITLE: API Request to List ElevenLabs Conversational AI Tools
DESCRIPTION: Defines the HTTP GET request for the ElevenLabs API to retrieve a list of conversational AI tools. This endpoint allows fetching all available tools in the workspace. It specifies the full endpoint URL and highlights the required 'xi-api-key' header for authentication.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/tools/list

LANGUAGE: APIDOC
CODE:
```
GET /v1/convai/tools
Host: api.elevenlabs.io

Headers:
xi-api-key: string (Required)
```

----------------------------------------

TITLE: Retrieve Tool IDs via API
DESCRIPTION: Describes how to find the ID of a tool by listing existing tools through the ElevenLabs Conversational AI API or by inspecting the response during tool creation. This method uses a GET request to an API endpoint.

SOURCE: https://elevenlabs.io/docs/conversational-ai/customization/tools/agent-tools-deprecation

LANGUAGE: APIDOC
CODE:
```
GET /v1/convai/tools
```

----------------------------------------

TITLE: Delete Tool using cURL
DESCRIPTION: This cURL command demonstrates how to send a DELETE request to remove a specific tool from the ElevenLabs workspace using its ID and an API key. Replace 'tool_id' with the actual tool identifier and 'xi-api-key' with your valid API key.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/tools/delete

LANGUAGE: bash
CODE:
```
curl -X DELETE https://api.elevenlabs.io/v1/convai/tools/tool_id \
-H "xi-api-key: xi-api-key"
```

----------------------------------------

TITLE: Update ElevenLabs Conversational AI Tool with Python SDK
DESCRIPTION: This snippet demonstrates how to update an existing conversational AI tool using the ElevenLabs Python SDK. It initializes the client with an API key and then calls the `update` method on the `conversational_ai.tools` object, providing the `tool_id` and a `ToolRequestModel` with updated configuration details like name, description, and `expects_response`.

SOURCE: https://elevenlabs.io/docs/api-reference/tools/update

LANGUAGE: Python
CODE:
```
from elevenlabs import (
    ElevenLabs,
    ToolRequestModel,
    ToolRequestModelToolConfig_Client,
)

client = ElevenLabs(
    api_key="YOUR_API_KEY",
)
client.conversational_ai.tools.update(
    tool_id="tool_id",
    request=ToolRequestModel(
        tool_config=ToolRequestModelToolConfig_Client(
            name="name",
            description="description",
            expects_response=False,
        ),
    ),
)
```

----------------------------------------

TITLE: Example JSON Response for Successful Tool Creation
DESCRIPTION: This JSON object illustrates the structure of a successful response from the ElevenLabs API after a new tool has been created. It includes the unique `id` of the created tool, its detailed `tool_config` (including API schema and dynamic variables), and `access_info` about the creator.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/tools/create

LANGUAGE: json
CODE:
```
{
  "id": "foo",
  "tool_config": {
    "name": "foo",
    "description": "foo",
    "response_timeout_secs": 20,
    "type": "webhook",
    "api_schema": {
      "url": "foo",
      "method": "GET",
      "path_params_schema": {},
      "query_params_schema": {
        "properties": {},
        "required": [
          "foo"
        ]
      },
      "request_body_schema": {
        "type": "object",
        "required": [
          "foo"
        ],
        "description": "",
        "properties": {}
      },
      "request_headers": {},
      "auth_connection": {
        "auth_connection_id": "foo"
      }
    },
    "dynamic_variables": {
      "dynamic_variable_placeholders": {}
    }
  },
  "access_info": {
    "is_creator": true,
    "creator_name": "foo",
    "creator_email": "foo",
    "role": "admin"
  }
}
```

----------------------------------------

TITLE: JSON Response Schema for Listing ElevenLabs Tools
DESCRIPTION: Provides a detailed example of the JSON structure returned by the ElevenLabs API upon a successful request to list conversational AI tools. It showcases the 'tools' array, with each tool object containing 'id', 'tool_config' (including 'api_schema' details), and 'access_info' properties.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/tools/list

LANGUAGE: APIDOC
CODE:
```
{
  "tools": [
    {
      "id": "foo",
      "tool_config": {
        "name": "foo",
        "description": "foo",
        "response_timeout_secs": 20,
        "type": "webhook",
        "api_schema": {
          "url": "foo",
          "method": "GET",
          "path_params_schema": {},
          "query_params_schema": {
            "properties": {},
            "required": [
              "foo"
            ]
          },
          "request_body_schema": {
            "type": "object",
            "required": [
              "foo"
            ],
            "description": "",
            "properties": {}
          },
          "request_headers": {},
          "auth_connection": {
            "auth_connection_id": "foo"
          }
        },
        "dynamic_variables": {
          "dynamic_variable_placeholders": {}
        }
      },
      "access_info": {
        "is_creator": true,
        "creator_name": "foo",
        "creator_email": "foo",
        "role": "admin"
      }
    }
  ]
}
```

----------------------------------------

TITLE: ElevenLabs API: Update Conversational AI Tool Endpoint
DESCRIPTION: This section details the API specification for updating a conversational AI tool. It outlines the HTTP method (PATCH), the endpoint URL, required path parameters (`tool_id`), necessary headers (`xi-api-key`), the structure of the request body (`tool_config`), and the expected successful response format, including potential error codes like 422.

SOURCE: https://elevenlabs.io/docs/api-reference/tools/update

LANGUAGE: APIDOC
CODE:
```
Endpoint: PATCH /v1/convai/tools/:tool_id
Base URL: https://api.elevenlabs.io

Path Parameters:
  tool_id: string (Required)
    ID of the requested tool.

Headers:
  xi-api-key: string (Required)

Request Body:
  tool_config: object (Required)
    Configuration for the tool.
    (Show 4 variants)

Response (200 Updated):
  id: string
  tool_config: object
    The type of tool.
    (Show 4 variants)
  access_info: object
    (Show 4 properties)

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Successful Response for ElevenLabs Tool Update API
DESCRIPTION: This JSON snippet illustrates the structure of a successful response (HTTP 200) after updating a conversational AI tool. It includes the tool's `id`, its `tool_config` with details like `name`, `description`, `type`, and `api_schema`, and `access_info` indicating creator and role details.

SOURCE: https://elevenlabs.io/docs/api-reference/tools/update

LANGUAGE: JSON
CODE:
```
{
    "id": "foo",
    "tool_config": {
        "name": "foo",
        "description": "foo",
        "response_timeout_secs": 20,
        "type": "webhook",
        "api_schema": {
            "url": "foo",
            "method": "GET",
            "path_params_schema": {},
            "query_params_schema": {
                "properties": {},
                "required": [
                    "foo"
                ]
            },
            "request_body_schema": {
                "type": "object",
                "required": [
                    "foo"
                ],
                "description": "",
                "properties": {}
            },
            "request_headers": {},
            "auth_connection": {
                "auth_connection_id": "foo"
            }
        },
        "dynamic_variables": {
            "dynamic_variable_placeholders": {}
        }
    },
    "access_info": {
        "is_creator": true,
        "creator_name": "foo",
        "creator_email": "foo",
        "role": "admin"
    }
}
```

----------------------------------------

TITLE: ElevenLabs Tool Management API Endpoint
DESCRIPTION: This API endpoint is used for managing agent tools, allowing creation, retrieval, update, and deletion of standalone tool records. It replaces the old in-line `tools` array and centralizes tool management.

SOURCE: https://elevenlabs.io/docs/conversational-ai/customization/tools/agent-tools-deprecation

LANGUAGE: APIDOC
CODE:
```
POST | GET | PATCH | DELETE https://api.elevenlabs.io/v1/convai/tools
```

----------------------------------------

TITLE: ElevenLabs Python SDK: Get Dependent Agents Example
DESCRIPTION: Illustrates how to use the ElevenLabs Python SDK to interact with the 'Get Dependent Agents' API. It covers client initialization with an API key and making the API call with the required tool ID.

SOURCE: https://elevenlabs.io/docs/api-reference/tools/get-dependent-agents

LANGUAGE: Python
CODE:
```
from elevenlabs import ElevenLabs

client = ElevenLabs(
    api_key="YOUR_API_KEY",
)
client.conversational_ai.tools.get_dependent_agents(
    tool_id="tool_id",
)
```

----------------------------------------

TITLE: API Documentation: Delete Tool Endpoint
DESCRIPTION: Documents the API endpoint for deleting a specific tool from the ElevenLabs conversational AI workspace. It specifies the HTTP method, the URL structure with its path parameter, required authentication headers, and potential responses including error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/tools/delete

LANGUAGE: APIDOC
CODE:
```
DELETE https://api.elevenlabs.io/v1/convai/tools/:tool_id

Path parameters:
  tool_id: string (Required)
    ID of the requested tool.

Headers:
  xi-api-key: string (Required)

Response:
  Successful Response

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Python Client Example for Listing ElevenLabs Tools
DESCRIPTION: Illustrates how to use the ElevenLabs Python client library to programmatically fetch a list of conversational AI tools. The example demonstrates client initialization with an API key and calling the `list()` method on the `conversational_ai.tools` object.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/tools/list

LANGUAGE: Python
CODE:
```
from elevenlabs import ElevenLabs

client = ElevenLabs(
    api_key="YOUR_API_KEY",
)
client.conversational_ai.tools.list()
```

----------------------------------------

TITLE: Retrieve Dependent Agents for a Tool
DESCRIPTION: This API endpoint allows you to fetch a paginated list of agents that are dependent on a specific tool. It requires a tool ID as a path parameter and an API key in the headers for authentication. Pagination is supported through optional cursor and page size query parameters. The response includes a list of agents, a boolean indicating if more results are available, and a cursor for fetching the next page.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/tools/get-dependent-agents

LANGUAGE: APIDOC
CODE:
```
Endpoint: GET /v1/convai/tools/:tool_id/dependent-agents

Path Parameters:
  tool_id: string (Required)
    Description: ID of the requested tool.

Headers:
  xi-api-key: string (Required)

Query Parameters:
  cursor: string or null (Optional)
    Description: Used for fetching next page. Cursor is returned in the response.
  page_size: integer (Optional)
    Constraints: >=1, <=100
    Default: 30
    Description: How many documents to return at maximum. Can not exceed 100, defaults to 30.

Response (200 Retrieved):
  agents: list of objects
  has_more: boolean
  next_cursor: string or null
```

LANGUAGE: cURL
CODE:
```
curl https://api.elevenlabs.io/v1/convai/tools/tool_id/dependent-agents \
-H "xi-api-key: xi-api-key"
```

LANGUAGE: json
CODE:
```
{
  "agents": [
    {
      "type": "unknown"
    }
  ],
  "has_more": true,
  "next_cursor": "foo"
}
```

----------------------------------------

TITLE: Create Tool using ElevenLabs Python SDK
DESCRIPTION: This Python code demonstrates how to create a new tool using the ElevenLabs Python SDK. It initializes the client with an API key and then calls the `create` method on the `conversational_ai.tools` service, providing a `ToolRequestModel` with the tool's name, description, and whether it expects a response.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/tools/create

LANGUAGE: python
CODE:
```
from elevenlabs import (
    ElevenLabs,
    ToolRequestModel,
    ToolRequestModelToolConfig_Client,
)

client = ElevenLabs(
    api_key="YOUR_API_KEY",
)
client.conversational_ai.tools.create(
    request=ToolRequestModel(
        tool_config=ToolRequestModelToolConfig_Client(
            name="name",
            description="description",
            expects_response=False,
        ),
    ),
)
```

----------------------------------------

TITLE: Eleven Labs Update Tool API Endpoint Documentation
DESCRIPTION: Comprehensive API documentation for the PATCH /v1/convai/tools/:tool_id endpoint. It details the required path parameters, headers, the structure of the request body for updating tool configurations, and the expected schema of a successful 200 OK response, including tool and access information.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/tools/update

LANGUAGE: APIDOC
CODE:
```
Endpoint: PATCH /v1/convai/tools/:tool_id
Description: Update tool that is available in the workspace.

Path Parameters:
  tool_id:
    Type: string
    Required: true
    Description: ID of the requested tool.

Headers:
  xi-api-key:
    Type: string
    Required: true

Request Body (application/json):
  tool_config:
    Type: object
    Required: true
    Description: Configuration for the tool.
    Properties:
      name:
        Type: string
        Description: New name for the tool.
      description:
        Type: string
        Description: New description for the tool.
      api_schema:
        Type: object
        Description: API schema configuration.
        Properties:
          url:
            Type: string
            Description: URL for the API schema.

Response (200 OK):
  id:
    Type: string
  tool_config:
    Type: object
    Description: The updated tool configuration.
    Properties:
      name:
        Type: string
      description:
        Type: string
      response_timeout_secs:
        Type: number
      type:
        Type: string
      api_schema:
        Type: object
        Properties:
          url:
            Type: string
          method:
            Type: string
          path_params_schema:
            Type: object
          query_params_schema:
            Type: object
            Properties: {}
            Required:
              - "foo"
          request_body_schema:
            Type: object
            Properties: {}
            Required:
              - "foo"
            Description: ""
          request_headers:
            Type: object
          auth_connection:
            Type: object
            Properties:
              auth_connection_id:
                Type: string
      dynamic_variables:
        Type: object
        Properties:
          dynamic_variable_placeholders:
            Type: object
  access_info:
    Type: object
    Properties:
      is_creator:
        Type: boolean
      creator_name:
        Type: string
      creator_email:
        Type: string
      role:
        Type: string

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: List Conversational AI Tools using cURL
DESCRIPTION: This cURL command demonstrates how to make a GET request to the ElevenLabs API to retrieve a list of all available conversational AI tools. It requires an `xi-api-key` for authentication.

SOURCE: https://elevenlabs.io/docs/api-reference/tools/list

LANGUAGE: cURL
CODE:
```
curl https://api.elevenlabs.io/v1/convai/tools \
-H "xi-api-key: xi-api-key"
```

----------------------------------------

TITLE: ElevenLabs Create Tool API Endpoint Specification
DESCRIPTION: Comprehensive API documentation for the `POST /v1/convai/tools` endpoint, detailing required headers, the structure of the request body for `tool_config`, and the full schema of the successful 200 OK response, including nested objects like `api_schema` and `access_info`.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/tools/create

LANGUAGE: APIDOC
CODE:
```
API Endpoint: POST /v1/convai/tools

Full URL: https://api.elevenlabs.io/v1/convai/tools

Headers:
  - xi-api-key: string (Required)

Request Body:
  - tool_config: object (Required)
    Description: Configuration for the tool
    Properties:
      - name: string
      - description: string
      - expects_response: boolean

Response (200 Successful):
  - id: string
  - tool_config: object
    Description: The type of tool
    Properties:
      - name: string
      - description: string
      - response_timeout_secs: integer
      - type: string
      - api_schema: object
        Properties:
          - url: string
          - method: string
          - path_params_schema: object
          - query_params_schema: object
            Properties:
              - properties: object
              - required: array of strings
          - request_body_schema: object
            Properties:
              - type: string
              - required: array of strings
              - description: string
              - properties: object
          - request_headers: object
          - auth_connection: object
            Properties:
              - auth_connection_id: string
      - dynamic_variables: object
        Properties:
          - dynamic_variable_placeholders: object
  - access_info: object
    Properties:
      - is_creator: boolean
      - creator_name: string
      - creator_email: string
      - role: string

Errors:
  - 422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Conversational AI - Agent and Tool Management API Endpoints
DESCRIPTION: Documents core API endpoints for managing conversational AI agents and their associated tools, including creation, retrieval, update, and deletion operations, as well as listing tool dependencies.

SOURCE: https://elevenlabs.io/docs/changelog

LANGUAGE: APIDOC
CODE:
```
Duplicate agent: Create a new agent by duplicating an existing one
Create tool: Add a new tool to the available tools in the workspace
List tools: Retrieve all tools available in the workspace
Get tool: Retrieve a specific tool configuration
Update tool: Update an existing tool configuration
Delete tool: Remove a tool from the workspace
Get tool dependent agents: List all agents that depend on a specific tool
```

----------------------------------------

TITLE: Update Eleven Labs Tool with cURL PATCH Request
DESCRIPTION: Demonstrates how to send a PATCH request to the Eleven Labs API to update an existing tool. The request body specifies the new tool configuration, including its name, description, and API schema URL. An API key and 'application/json' Content-Type header are required.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/tools/update

LANGUAGE: cURL
CODE:
```
curl -X PATCH https://api.elevenlabs.io/v1/convai/tools/tool_id \
  -H "xi-api-key: xi-api-key" \
  -H "Content-Type: application/json" \
  -d '{
  "tool_config": {
  "name": "foo",
  "description": "foo",
  "api_schema": {
  "url": "foo"
  }
  }
  }'
```

----------------------------------------

TITLE: ElevenLabs API: Get Dependent Agents Endpoint
DESCRIPTION: Defines the HTTP GET endpoint for retrieving agents dependent on a specific conversational AI tool, including the full URL path and relative path.

SOURCE: https://elevenlabs.io/docs/api-reference/tools/get-dependent-agents

LANGUAGE: APIDOC
CODE:
```
GET
https://api.elevenlabs.io/v1/convai/tools/:tool_id/dependent-agents

GET
/v1/convai/tools/:tool_id/dependent-agents
```

----------------------------------------

TITLE: ElevenLabs Studio API: Get Project Snapshot Endpoint Reference
DESCRIPTION: This section provides a comprehensive reference for the 'Get Project Snapshot' API endpoint. It outlines the HTTP method, the full URL path with placeholders for dynamic parameters, required headers, the detailed schema of a successful 200 OK response, and an example response body, along with information on potential error responses.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/get-project-snapshot

LANGUAGE: APIDOC
CODE:
```
GET /v1/studio/projects/:project_id/snapshots/:project_snapshot_id

Description: Returns the project snapshot.

Path Parameters:
  project_id:
    Type: string
    Required: true
    Description: The ID of the Studio project.
  project_snapshot_id:
    Type: string
    Required: true
    Description: The ID of the Studio project snapshot.

Headers:
  xi-api-key:
    Type: string
    Required: true
    Description: API key for authentication.

Responses:
  200 OK:
    Description: Retrieved
    Body Schema:
      project_snapshot_id:
        Type: string
        Description: The ID of the project snapshot.
      project_id:
        Type: string
        Description: The ID of the project.
      created_at_unix:
        Type: integer
        Description: The creation date of the project snapshot.
      name:
        Type: string
        Description: The name of the project snapshot.
      character_alignments:
        Type: list of objects
        Description: (Show 3 properties)
        Properties:
          audio_upload:
            Type: object or null
            Description: (Deprecated)
          zip_upload:
            Type: object or null
            Description: (Deprecated)
    Example Body:
      {
        "project_snapshot_id": "aw1NgEzBg83R7vgmiJt6",
        "project_id": "aw1NgEzBg83R7vgmiJt6",
        "created_at_unix": 1714204800,
        "name": "My Project Snapshot",
        "character_alignments": []
      }

  422 Unprocessable Entity Error:
    Description: Indicates that the request was well-formed but could not be processed due to semantic errors.
```

----------------------------------------

TITLE: API Reference for Listing Knowledge Base Documents
DESCRIPTION: Detailed API specification for the GET /v1/convai/knowledge-base endpoint, including required headers and the structure of the successful 200 OK response, which returns a list of knowledge base documents.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/knowledge-base/list

LANGUAGE: APIDOC
CODE:
```
GET /v1/convai/knowledge-base

Description: Get a list of available knowledge base documents

Headers:
  xi-api-key: string (Required)

Response (200 Retrieved):
{
  "documents": [
    {
      "id": "foo",
      "name": "foo",
      "metadata": {
        "created_at_unix_secs": 42,
        "last_updated_at_unix_secs": 42,
        "size_bytes": 42
      },
      "supported_usages": [
        "prompt"
      ],
      "access_info": {
        "is_creator": true,
        "creator_name": "foo",
        "creator_email": "foo",
        "role": "admin"
      },
      "dependent_agents": [
        {
          "type": "unknown"
        }
      ],
      "type": "foo",
      "url": "foo"
    }
  ],
  "has_more": true,
  "next_cursor": "foo"
}
```

----------------------------------------

TITLE: ElevenLabs API: Create Tool Endpoint Specification
DESCRIPTION: This section provides a detailed specification for the `POST /v1/convai/tools` endpoint, outlining the required headers, the structure of the request body for tool configuration, the expected successful response schema, and common error responses.

SOURCE: https://elevenlabs.io/docs/api-reference/tools/create

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/convai/tools
Description: Add a new tool to the available tools in the workspace.

Headers:
  xi-api-key: string (Required)

Request Body:
  Type: object (Required)
  Properties:
    tool_config: object (Required)
      Description: Configuration for the tool
      Variants: 4

Response (200 Successful):
  Type: object
  Properties:
    id: string
    tool_config: object
      Description: The type of tool
      Variants: 4
    access_info: object
      Properties: 4

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Successful Create Tool API Response Schema
DESCRIPTION: This JSON object represents the structure of a successful response from the ElevenLabs API after creating a new conversational AI tool. It includes the unique 'id' of the created tool, its detailed 'tool_config' (including name, description, response timeout, type, and API schema details), and 'access_info' about the creator.

SOURCE: https://elevenlabs.io/docs/api-reference/tools/create

LANGUAGE: json
CODE:
```
{
"id": "foo",
"tool_config": {
"name": "foo",
"description": "foo",
"response_timeout_secs": 20,
"type": "webhook",
"api_schema": {
"url": "foo",
"method": "GET",
"path_params_schema": {},
"query_params_schema": {
"properties": {},
"required": [
"foo"
]
},
"request_body_schema": {
"type": "object",
"required": [
"foo"
],
"description": "",
"properties": {}
},
"request_headers": {},
"auth_connection": {
"auth_connection_id": "foo"
}
},
"dynamic_variables": {
"dynamic_variable_placeholders": {}
}
},
"access_info": {
"is_creator": true,
"creator_name": "foo",
"creator_email": "foo",
"role": "admin"
}
}
```

----------------------------------------

TITLE: New Tools Creation Endpoint
DESCRIPTION: A new endpoint for creating tools that can be used by conversational AI agents.

SOURCE: https://elevenlabs.io/docs/changelog/2025/2/10

LANGUAGE: APIDOC
CODE:
```
POST /v1/convai/tools: Create new tools for agents
```

----------------------------------------

TITLE: ElevenLabs Conversational AI: List Conversations API Reference
DESCRIPTION: Comprehensive API documentation for the 'List conversations' endpoint, detailing the HTTP method, URL, request headers, query parameters for filtering and pagination, expected successful response structure, and potential error responses.

SOURCE: https://elevenlabs.io/docs/api-reference/conversations/get-conversations

LANGUAGE: APIDOC
CODE:
```
Endpoint:
  GET /v1/convai/conversations
  Full URL: https://api.elevenlabs.io/v1/convai/conversations

Headers:
  xi-api-key: string (Required)

Query Parameters:
  cursor: string or null (Optional)
    Description: Used for fetching next page. Cursor is returned in the response.
  agent_id: string or null (Optional)
    Description: The id of the agent you're taking the action on.
  call_successful: enum or null (Optional)
    Description: The result of the success evaluation
    Allowed values: success, failure, unknown
  call_start_before_unix: integer or null (Optional)
    Description: Unix timestamp (in seconds) to filter conversations up to this start date.
  call_start_after_unix: integer or null (Optional)
    Description: Unix timestamp (in seconds) to filter conversations after to this start date.
  page_size: integer (Optional)
    Constraints: >=1, <=100
    Default: 30
    Description: How many conversations to return at maximum. Can not exceed 100, defaults to 30.

Successful Response (HTTP 200):
  Description: Retrieved
  Schema:
    conversations: list of objects
      Properties: (Show 8 properties)
    has_more: boolean
    next_cursor: string or null
  Example:
    {
    "conversations": [
        {
        "agent_id": "foo",
        "conversation_id": "foo",
        "start_time_unix_secs": 42,
        "call_duration_secs": 42,
        "message_count": 42,
        "status": "initiated",
        "call_successful": "success",
        "agent_name": "foo"
        }
    ],
    "has_more": true,
    "next_cursor": "foo"
    }

Errors:
  HTTP 422: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs API: List Workspace Webhooks Endpoint Reference
DESCRIPTION: This section details the API endpoint for listing workspace webhooks. It specifies the HTTP GET method, the full URL, required headers (`xi-api-key`), optional query parameters (`include_usages`), and the structure of the successful JSON response, including properties of each webhook object and error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/webhooks/list

LANGUAGE: APIDOC
CODE:
```
GET
/v1/workspace/webhooks

Headers:
  xi-api-key: string (Required)

Query parameters:
  include_usages: boolean (Optional, Defaults to false)
    Description: Whether to include active usages of the webhook, only usable by admins

Response (200 Retrieved):
  webhooks: list of objects
    Description: List of webhooks currently configured for the workspace
    Properties:
      name: string
      webhook_id: string
      webhook_url: string
      is_disabled: boolean
      is_auto_disabled: boolean
      created_at_unix: integer
      auth_type: string
      usage: list of objects
        usage_type: string
      most_recent_failure_error_code: integer
      most_recent_failure_timestamp: integer

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Retrieve a specific tool using cURL
DESCRIPTION: This cURL command demonstrates how to make a GET request to the Eleven Labs API to retrieve details of a specific tool by its ID. It requires an API key for authentication via the 'xi-api-key' header.

SOURCE: https://elevenlabs.io/docs/api-reference/tools/get

LANGUAGE: cURL
CODE:
```
curl https://api.elevenlabs.io/v1/convai/tools/tool_id \
-H "xi-api-key: xi-api-key"
```

----------------------------------------

TITLE: Create Tool API Request with cURL
DESCRIPTION: This cURL command demonstrates how to make a POST request to the ElevenLabs API to create a new conversational AI tool. It includes the necessary 'xi-api-key' header, 'Content-Type' header set to 'application/json', and a JSON request body specifying the 'tool_config' with 'name', 'description', and 'api_schema' URL.

SOURCE: https://elevenlabs.io/docs/api-reference/tools/create

LANGUAGE: cURL
CODE:
```
curl -X POST https://api.elevenlabs.io/v1/convai/tools \
-H "xi-api-key: xi-api-key" \
-H "Content-Type: application/json" \
-d '{
"tool_config": {
"name": "foo",
"description": "foo",
"api_schema": {
"url": "foo"
}
}
}'
```

----------------------------------------

TITLE: MCP Server Tool Approval API Reference
DESCRIPTION: Detailed API documentation for the POST endpoint to create a tool approval on an MCP server, including path parameters, required headers, request body schema with field descriptions and allowed values, and the structure of successful and error responses.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/mcp/approval-policies/create

LANGUAGE: APIDOC
CODE:
```
POST /v1/convai/mcp-servers/:mcp_server_id/tool-approvals

Path Parameters:
  mcp_server_id: string (Required)
    Description: ID of the MCP Server.

Headers:
  xi-api-key: string (Required)

Request Body (application/json):
  tool_name: string (Required)
    Description: The name of the MCP tool
  tool_description: string (Required)
    Description: The description of the MCP tool
  input_schema: object (Optional)
    Description: The input schema of the MCP tool (the schema defined on the MCP server before ElevenLabs does any extra processing)
  approval_policy: enum (Optional)
    Description: The tool-level approval policy
    Allowed values: auto_approved, requires_approval

Responses:
  200 Successful:
    id: string
    config: object (Show 8 properties)
    metadata: object (The metadata of the MCP Server, Show 2 properties)
    access_info: object or null (The access information of the MCP Server, Show 4 properties)
    dependent_agents: list of objects or null (List of agents that depend on this MCP Server., Show 2 variants)
  422:
    Description: Unprocessable Entity Error
```

----------------------------------------

TITLE: Successful Response Schema for List Tools API
DESCRIPTION: This JSON object represents a successful response from the `GET /v1/convai/tools` endpoint. It contains a list of `tools`, each with properties like `id`, `tool_config` (including `name`, `description`, `type`, `api_schema`), and `access_info`.

SOURCE: https://elevenlabs.io/docs/api-reference/tools/list

LANGUAGE: JSON
CODE:
```
{
  "tools": [
    {
      "id": "foo",
      "tool_config": {
        "name": "foo",
        "description": "foo",
        "response_timeout_secs": 20,
        "type": "webhook",
        "api_schema": {
          "url": "foo",
          "method": "GET",
          "path_params_schema": {},
          "query_params_schema": {
            "properties": {},
            "required": [
              "foo"
            ]
          },
          "request_body_schema": {
            "type": "object",
            "required": [
              "foo"
            ],
            "description": "",
            "properties": {}
          },
          "request_headers": {},
          "auth_connection": {
            "auth_connection_id": "foo"
          }
        },
        "dynamic_variables": {
          "dynamic_variable_placeholders": {}
        }
      },
      "access_info": {
        "is_creator": true,
        "creator_name": "foo",
        "creator_email": "foo",
        "role": "admin"
      }
    }
  ]
}
```

----------------------------------------

TITLE: API Reference for Creating MCP Server Tool Approval
DESCRIPTION: This section details the API endpoint for creating a new MCP server tool approval. It specifies the HTTP method, URL, path parameters, request headers, request body structure, and the expected successful response schema, along with potential error responses.

SOURCE: https://elevenlabs.io/docs/api-reference/mcp/approval-policies/create

LANGUAGE: APIDOC
CODE:
```
POST /v1/convai/mcp-servers/:mcp_server_id/tool-approvals

Path Parameters:
  mcp_server_id: string (Required)
    Description: ID of the MCP Server.

Headers:
  xi-api-key: string (Required)

Request Body:
  tool_name: string (Required)
    Description: The name of the MCP tool
  tool_description: string (Required)
    Description: The description of the MCP tool
  input_schema: object (Optional)
    Description: The input schema of the MCP tool (the schema defined on the MCP server before ElevenLabs does any extra processing)
  approval_policy: enum (Optional)
    Description: The tool-level approval policy
    Allowed values: auto_approved, requires_approval

Response (200 Successful):
  id: string
  config: object
    url: string
    name: string
    approval_policy: string
    tool_approval_hashes: array of objects
      tool_name: string
      tool_hash: string
      approval_policy: string
    transport: string
    secret_token: object
      secret_id: string
    request_headers: object
    description: string
  metadata: object
    Description: The metadata of the MCP Server
    created_at: number
    owner_user_id: string
  access_info: object or null
    Description: The access information of the MCP Server
    is_creator: boolean
    creator_name: string
    creator_email: string
    role: string
  dependent_agents: list of objects or null
    Description: List of agents that depend on this MCP Server.
    type: string

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs Get Dubbing Resource API Reference Details
DESCRIPTION: Detailed API documentation for the 'Get dubbing resource' endpoint, outlining its purpose, required path parameters, necessary headers for authentication, and the comprehensive structure of the successful response object. It also lists common error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/dubbing/resources/get-resource

LANGUAGE: APIDOC
CODE:
```
Given a dubbing ID generated from the ‘/v1/dubbing’ endpoint with studio enabled, returns the dubbing resource.

Path parameters:
  dubbing_id: string (Required)
    ID of the dubbing project.

Headers:
  xi-api-key: string (Required)

Response:
  Successful Response:
    id: string
    version: integer
    source_language: string
    target_languages: list of strings
    input: object (Show 7 properties)
    background: object (Show 7 properties)
    foreground: object (Show 7 properties)
    speaker_tracks: map from strings to objects (Show 5 properties)
    speaker_segments: map from strings to objects (Show 5 properties)
    renders: map from strings to objects (Show 6 properties)

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Conversational AI API Endpoints Overview
DESCRIPTION: A list of core API endpoints for managing conversational AI agents and tools, including operations for duplication, creation, listing, retrieval, updating, and deletion of agents and tools.

SOURCE: https://elevenlabs.io/docs/changelog/2025/6/23

LANGUAGE: APIDOC
CODE:
```
Conversational AI API Endpoints:
- Duplicate agent: Create a new agent by duplicating an existing one. (Path: /docs/api-reference/agents/duplicate)
- Create tool: Add a new tool to the available tools in the workspace. (Path: /docs/api-reference/tools/create)
- List tools: Retrieve all tools available in the workspace. (Path: /docs/api-reference/tools/list)
- Get tool: Retrieve a specific tool configuration. (Path: /docs/api-reference/tools/get)
- Update tool: Update an existing tool configuration. (Path: /docs/api-reference/tools/update)
- Delete tool: Remove a tool from the workspace. (Path: /docs/api-reference/tools/delete)
- Get tool dependent agents: List all agents that depend on a specific tool. (Path: /docs/api-reference/tools/get-dependent-agents)
```

----------------------------------------

TITLE: API Reference: Delete MCP Server Tool Approval Endpoint
DESCRIPTION: Detailed API documentation for the DELETE /v1/convai/mcp-servers/:mcp_server_id/tool-approvals/:tool_name endpoint. This section outlines the purpose, required path parameters, authentication headers, the expected structure of a successful 200 OK response, and possible error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/mcp/approval-policies/delete

LANGUAGE: APIDOC
CODE:
```
DELETE /v1/convai/mcp-servers/:mcp_server_id/tool-approvals/:tool_name

Description: Remove approval for a specific MCP tool when using per-tool approval mode.

Path Parameters:
  mcp_server_id:
    Type: string
    Required: true
    Description: ID of the MCP Server.
  tool_name:
    Type: string
    Required: true
    Description: Name of the MCP tool to remove approval for.

Headers:
  xi-api-key:
    Type: string
    Required: true

Response (200 Deleted):
  {
    "id": "string",
    "config": {
      "url": "string",
      "name": "string",
      "approval_policy": "string",
      "tool_approval_hashes": [
        {
          "tool_name": "string",
          "tool_hash": "string",
          "approval_policy": "string"
        }
      ],
      "transport": "string",
      "secret_token": {
        "secret_id": "string"
      },
      "request_headers": {},
      "description": "string"
    },
    "metadata": {
      "created_at": "number",
      "owner_user_id": "string"
    },
    "access_info": {
      "is_creator": "boolean",
      "creator_name": "string",
      "creator_email": "string",
      "role": "string"
    },
    "dependent_agents": [
      {
        "type": "string"
      }
    ]
  }

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs API Reference: Get Generated History Items Endpoint
DESCRIPTION: This API documentation details the `GET /v1/history` endpoint. It specifies the required `xi-api-key` header, available query parameters for filtering and pagination, and the expected successful response structure, including a list of history items and pagination metadata.

SOURCE: https://elevenlabs.io/docs/api-reference/history/get-all

LANGUAGE: APIDOC
CODE:
```
Endpoint: GET /v1/history
Description: Returns a list of your generated audio.

Headers:
  xi-api-key:
    Type: string
    Required: true

Query Parameters:
  page_size:
    Type: integer
    Optional: true
    Default: 100
    Description: How many history items to return at maximum. Can not exceed 1000, defaults to 100.
  start_after_history_item_id:
    Type: string or null
    Optional: true
    Description: After which ID to start fetching, use this parameter to paginate across a large collection of history items. In case this parameter is not provided history items will be fetched starting from the most recently created one ordered descending by their creation date.
  voice_id:
    Type: string or null
    Optional: true
    Description: ID of the voice to be filtered for. You can use the [Get voices](/docs/api-reference/voices/search) endpoint list all the available voices.
  search:
    Type: string or null
    Optional: true
    Description: Search term used for filtering history items. If provided, source becomes required.
  source:
    Type: enum or null
    Optional: true
    Allowed values: TTS, STS
    Description: Source of the generated history item.

Response (200 Retrieved):
  history:
    Type: list of objects
    Description: A list of speech history items. (Show 18 properties)
  has_more:
    Type: boolean
    Description: Whether there are more history items to fetch.
  last_history_item_id:
    Type: string or null
    Description: The ID of the last history item.

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference: Get Pronunciation Dictionary Endpoint
DESCRIPTION: Detailed API documentation for the 'Get pronunciation dictionary' endpoint, including HTTP method, URL structure, path parameters, required headers, and the structure of a successful response with all its properties and their types.

SOURCE: https://elevenlabs.io/docs/api-reference/pronunciation-dictionary/get

LANGUAGE: APIDOC
CODE:
```
API Endpoint: Get pronunciation dictionary
HTTP Method: GET
URL: https://api.elevenlabs.io/v1/pronunciation-dictionaries/:pronunciation_dictionary_id
Description: Get metadata for a pronunciation dictionary

Path Parameters:
  pronunciation_dictionary_id (string, Required): The id of the pronunciation dictionary

Headers:
  xi-api-key (string, Required)

Response (200 Retrieved):
  id (string): The ID of the pronunciation dictionary.
  latest_version_id (string): The ID of the latest version of the pronunciation dictionary.
  latest_version_rules_num (integer): The number of rules in the latest version of the pronunciation dictionary.
  name (string): The name of the pronunciation dictionary.
  permission_on_resource (enum or null): The permission on the resource of the pronunciation dictionary. Allowed values: admin, editor, viewer
  created_by (string): The user ID of the creator of the pronunciation dictionary.
  creation_time_unix (integer): The creation time of the pronunciation dictionary in Unix timestamp.
  archived_time_unix (integer or null): The archive time of the pronunciation dictionary in Unix timestamp.
  description (string or null): The description of the pronunciation dictionary.

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference: POST /v1/history/download
DESCRIPTION: Comprehensive API documentation for the 'Download history items' endpoint. It details the request method, URL, required headers, request body parameters, expected response types, and potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/history/download

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST https://api.elevenlabs.io/v1/history/download
Description: Download one or more history items. If one history item ID is provided, we will return a single audio file. If more than one history item IDs are provided, we will provide the history items packed into a .zip file.

Headers:
  xi-api-key: string (Required)

Request Body:
  history_item_ids: list of strings (Required)
    Description: A list of history items to download, you can get IDs of history items and other metadata using the GET https://api.elevenlabs.io/v1/history endpoint.
  output_format: string or null (Optional)
    Description: Output format to transcode the audio file, can be wav or default.

Response:
  Description: The requested audio file, or a zip file containing multiple audio files when multiple history items are requested.

Errors:
  400: Bad Request Error
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs Dubbing API: Add Language Endpoint Reference
DESCRIPTION: Comprehensive API documentation for the 'Add language to resource' endpoint, detailing the HTTP method, URL structure, path parameters, required headers, the structure of the request body, the successful response format, and potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/dubbing/add-language-to-resource

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/dubbing/resource/:dubbing_id/language

Path parameters:
  dubbing_id: string (Required)
    ID of the dubbing project.

Headers:
  xi-api-key: string (Required)

Request Body:
  Type: object
  Properties:
    language: string or null (Required)
      The Target language.

Response (201 Created):
  Type: object
  Properties:
    version: integer

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs API: Dub Segment Endpoint Reference
DESCRIPTION: This section provides a comprehensive API reference for the 'Dub segment' endpoint. It details the HTTP method, URL structure, required path parameters, headers, request body schema including segments and languages, and the expected successful response format, as well as potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/dubbing/resources/dub-segment

LANGUAGE: APIDOC
CODE:
```
POST /v1/dubbing/resource/:dubbing_id/dub\n\nDescription: Regenerate the dubs for either the entire resource or the specified segments/languages. Will automatically transcribe and translate any missing transcriptions and translations.\n\nPath Parameters:\n  dubbing_id: string (Required)\n    Description: ID of the dubbing project.\n\nHeaders:\n  xi-api-key: string (Required)\n\nRequest Body:\n  Type: object\n  Properties:\n    segments: list of strings (Required)\n      Description: Dub only this list of segments.\n    languages: list of strings or null (Required)\n      Description: Dub only these languages for each segment.\n\nResponse (200 Successful):\n  Type: object\n  Properties:\n    version: integer\n  Example:\n    {\n      "version": 42\n    }\n\nErrors:\n  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Retrieve Dubbing Resource API Endpoint Definition
DESCRIPTION: Defines the HTTP GET endpoint for fetching a specific dubbing resource from the ElevenLabs API. It specifies the base URL and the path parameter required to identify the dubbing project.

SOURCE: https://elevenlabs.io/docs/api-reference/dubbing/resources/get-resource

LANGUAGE: APIDOC
CODE:
```
GET
https://api.elevenlabs.io/v1/dubbing/resource/:dubbing_id

GET
/v1/dubbing/resource/:dubbing_id
```

----------------------------------------

TITLE: API Reference: List Workspace Batch Calling Jobs
DESCRIPTION: Documents the API endpoint for retrieving all batch calling jobs associated with the current workspace. It specifies the HTTP method, URL, required headers, optional query parameters, and the expected successful response structure.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/batch-calling/list

LANGUAGE: APIDOC
CODE:
```
GET /v1/convai/batch-calling/workspace

Description: Get all batch calls for the current workspace.

Headers:
  xi-api-key: string (Required)

Query parameters:
  limit: integer (Optional, Defaults to 100)
  last_doc: string or null (Optional)

Response (200 Retrieved):
{
  "batch_calls": [
    {
      "id": "foo",
      "phone_number_id": "foo",
      "name": "foo",
      "agent_id": "foo",
      "created_at_unix": 42,
      "scheduled_time_unix": 42,
      "total_calls_dispatched": 42,
      "total_calls_scheduled": 42,
      "last_updated_at_unix": 42,
      "status": "pending",
      "agent_name": "foo",
      "phone_provider": "twilio"
    }
  ],
  "next_doc": "foo",
  "has_more": false
}
```

----------------------------------------

TITLE: API Endpoint: List Similar Voices
DESCRIPTION: Defines the HTTP method and path for the 'List similar voices' API endpoint, which allows users to retrieve voices similar to a provided audio sample.

SOURCE: https://elevenlabs.io/docs/api-reference/voices/get-similar-library-voices

LANGUAGE: APIDOC
CODE:
```
Endpoint: /v1/similar-voices
Method: POST
Full URL: https://api.elevenlabs.io/v1/similar-voices
```

----------------------------------------

TITLE: AI Agent Available Tools Reference
DESCRIPTION: This section details the various tools an AI agent can utilize to assist users effectively. Each tool serves a specific purpose, ranging from querying knowledge bases and redirecting to documentation to generating code examples, checking feature compatibility, and providing a fallback to support forms.

SOURCE: https://elevenlabs.io/docs/conversational-ai/best-practices/prompting-guide

LANGUAGE: APIDOC
CODE:
```
searchKnowledgeBase():
  description: When users ask about specific features or functionality, use this tool to query our documentation for accurate information before responding.

redirectToDocs(path: string):
  description: When a topic requires in-depth explanation, use this tool to direct users to the relevant documentation page (e.g., `/docs/api-reference/text-to-speech`) while summarizing key points.
  parameters:
    path: The relevant documentation page path.

generateCodeExample():
  description: For implementation questions, use this tool to provide a relevant code snippet demonstrating how to use the feature they're asking about.

checkFeatureCompatibility():
  description: When users ask if certain features work together, use this tool to verify compatibility between different ElevenLabs products.

redirectToSupportForm():
  description: If the user's question involves account-specific issues or exceeds your knowledge scope, use this as a final fallback.
```

----------------------------------------

TITLE: Delete MCP Server Tool Approval with cURL
DESCRIPTION: Example cURL command to send a DELETE request to remove a specific MCP server tool approval. It requires the MCP server ID, the tool name, and an ElevenLabs API key for authentication.

SOURCE: https://elevenlabs.io/docs/api-reference/mcp/approval-policies/delete

LANGUAGE: cURL
CODE:
```
curl -X DELETE https://api.elevenlabs.io/v1/convai/mcp-servers/mcp_server_id/tool-approvals/tool_name \
-H "xi-api-key: xi-api-key"
```

----------------------------------------

TITLE: API Reference for Searching ElevenLabs Workspace User Groups
DESCRIPTION: This section details the API endpoint for searching user groups in the ElevenLabs workspace. It specifies the HTTP method (GET), the endpoint URL, required headers (xi-api-key), query parameters (name), and the structure of a successful response, including potential error codes like 422 Unprocessable Entity.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/search-user-groups

LANGUAGE: APIDOC
CODE:
```
Endpoint: GET /v1/workspace/groups/search
Description: Searches for user groups in the workspace. Multiple or no groups may be returned.

Headers:
  xi-api-key: string (Required)

Query Parameters:
  name: string (Required)
    Description: Name of the target group.

Response (200 Retrieved):
  Example:
    [
      {
        "name": "foo",
        "id": "foo",
        "members_emails": [
          "foo"
        ]
      }
    ]
  Properties:
    name: string
      Description: The name of the workspace group.
    id: string
      Description: The ID of the workspace group.
    members_emails: list of strings
      Description: The emails of the members of the workspace group.

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs Studio API: List Chapters Endpoint Definition
DESCRIPTION: This snippet defines the HTTP GET endpoint for retrieving chapters associated with a specific Studio project in ElevenLabs. It provides both the full API URL and the relative path.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/get-chapters

LANGUAGE: APIDOC
CODE:
```
GET
https://api.elevenlabs.io/v1/studio/projects/:project_id/chapters

GET
/v1/studio/projects/:project_id/chapters
```

----------------------------------------

TITLE: API Reference for Conversations List Endpoint
DESCRIPTION: Documents the query parameters, successful response structure, and error codes for fetching a list of conversations from the ElevenLabs API.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/conversations/get-conversations

LANGUAGE: APIDOC
CODE:
```
Endpoint: List Conversations

Query Parameters:
  cursor:
    type: string or null
    optional: true
    description: Used for fetching next page. Cursor is returned in the response.
  agent_id:
    type: string or null
    optional: true
    description: The id of the agent you're taking the action on.
  call_successful:
    type: enum
    optional: true
    description: The result of the success evaluation.
    allowed_values: success, failure, unknown
  call_start_before_unix:
    type: integer or null
    optional: true
    description: Unix timestamp (in seconds) to filter conversations up to this start date.
  call_start_after_unix:
    type: integer or null
    optional: true
    description: Unix timestamp (in seconds) to filter conversations after to this start date.
  page_size:
    type: integer
    optional: true
    description: How many conversations to return at maximum. Can not exceed 100, defaults to 30.
    constraints: >=1, <=100
    default: 30

Response:
  Successful Response (HTTP 200):
    properties:
      conversations:
        type: list of objects
        description: (Details not provided, "Show 8 properties")
      has_more:
        type: boolean
      next_cursor:
        type: string or null

Errors:
  HTTP 422:
    description: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs Voice Changer API Endpoint Reference
DESCRIPTION: This section provides a detailed API reference for the ElevenLabs Voice Changer endpoint. It outlines the HTTP method, URL, required path parameters, headers, and optional query parameters along with their types, descriptions, and default values.

SOURCE: https://elevenlabs.io/docs/api-reference/speech-to-speech

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/speech-to-speech/:voice_id
Description: Transform audio from one voice to another. Maintain full control over emotion, timing and delivery.

Path Parameters:
  voice_id: string (Required)
    ID of the voice to be used. Use the Get voices endpoint to list all available voices.

Headers:
  xi-api-key: string (Required)

Query Parameters:
  enable_logging: boolean (Optional, Defaults to true)
    When enable_logging is set to false zero retention mode will be used for the request. This will mean history features are unavailable for this request, including request stitching. Zero retention mode may only be used by enterprise customers.
  optimize_streaming_latency: integer or null (Optional, Deprecated)
    You can turn on latency optimizations at some cost of quality. The best possible final latency varies by model. Possible values:
    0 - default mode (no latency optimizations)
    1 - normal latency optimizations (about 50% of possible latency improvement of option 3)
    2 - strong latency optimizations (about 75% of possible latency improvement of option 3)
    3 - max latency optimizations
    4 - max latency optimizations, but also with text normalizer turned off for even more latency savings (best latency, but can mispronounce eg numbers and dates).
    Defaults to None.
  output_format: enum (Optional, Defaults to mp3_44100_128)
    Output format of the generated audio. Formatted as codec_sample_rate_bitrate. So an mp3 with 22.05kHz sample rate at 32kbs is represented as mp3_22050_32. MP3 with 192kbps bitrate requires you to be subscribed to Creator tier or above. PCM with 44.1kHz sample rate requires you to be subscribed to Pro tier or above. Note that the μ-law format (sometimes written mu-law, often approximated as u-law) is commonly used for Twilio audio inputs.
```

----------------------------------------

TITLE: Conversational AI API Endpoint Reference
DESCRIPTION: Comprehensive documentation for querying conversational AI data, including available filters, pagination options, and the structure of successful responses and common errors.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/conversations/list

LANGUAGE: APIDOC
CODE:
```
Query Parameters:
  cursor: string or null (Optional)
    Description: Used for fetching next page. Cursor is returned in the response.
  agent_id: string or null (Optional)
    Description: The id of the agent you're taking the action on.
  call_successful: enum (Optional)
    Allowed values: success, failure, unknown
    Description: The result of the success evaluation.
  call_start_before_unix: integer (Optional)
    Description: Unix timestamp (in seconds) to filter conversations up to this start date.
  call_start_after_unix: integer (Optional)
    Description: Unix timestamp (in seconds) to filter conversations after to this start date.
  page_size: integer (Optional)
    Constraints: >=1, <=100
    Default: 30
    Description: How many conversations to return at maximum. Can not exceed 100, defaults to 30.

Response:
  Successful Response:
    conversations: list of objects
      Description: Show 8 properties (details not provided in source)
    has_more: boolean
    next_cursor: string or null

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs API: Delete Studio Project Endpoint Reference
DESCRIPTION: Comprehensive API documentation for the 'Delete Studio Project' endpoint, detailing the HTTP method, URL structure, path parameters, required headers, successful response schema, and potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/delete-project

LANGUAGE: APIDOC
CODE:
```
Method: DELETE
Endpoint: /v1/studio/projects/:project_id

Path Parameters:
  project_id:
    Type: string
    Required: Yes
    Description: The ID of the project to be used. You can use the List projects endpoint to list all the available projects.

Headers:
  xi-api-key:
    Type: string
    Required: Yes

Response (200 OK):
  status:
    Type: string
    Description: The status of the studio project deletion request. If the request was successful, the status will be 'ok'. Otherwise an error message with status 500 will be returned.

Response Example (200 OK):
  {
    "status": "ok"
  }

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: cURL Example: Delete ElevenLabs Tool
DESCRIPTION: Provides a command-line example using cURL to demonstrate how to send a DELETE request to the ElevenLabs API. This snippet illustrates the correct syntax for specifying the HTTP method, the target URL, and including the necessary API key in the request header.

SOURCE: https://elevenlabs.io/docs/api-reference/tools/delete

LANGUAGE: cURL
CODE:
```
curl -X DELETE https://api.elevenlabs.io/v1/convai/tools/tool_id \
-H "xi-api-key: xi-api-key"
```

----------------------------------------

TITLE: API Reference: List ElevenLabs Studio Project Snapshots
DESCRIPTION: This section details the API endpoint for retrieving a list of snapshots associated with a specific ElevenLabs Studio project. It specifies the HTTP method, URL path, required parameters, and expected response structure, including potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/get-snapshots

LANGUAGE: APIDOC
CODE:
```
GET /v1/studio/projects/:project_id/snapshots

Description: Retrieves a list of snapshots for a Studio project.

Path Parameters:
  project_id: string (Required)
    Description: The ID of the Studio project.

Headers:
  xi-api-key: string (Required)

Response (200 OK):
  snapshots: list of objects
    Description: List of project snapshots.
    Properties:
      project_snapshot_id: string
      project_id: string
      created_at_unix: integer
      name: string

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: List Studio Projects API Endpoint Definition
DESCRIPTION: Defines the HTTP GET endpoint for retrieving a list of Eleven Labs Studio projects. It specifies the full URL and the relative path for the API call.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/get-projects

LANGUAGE: APIDOC
CODE:
```
GET https://api.elevenlabs.io/v1/studio/projects
GET /v1/studio/projects
```

----------------------------------------

TITLE: ElevenLabs Speech-to-Speech API Reference
DESCRIPTION: This section provides a detailed reference for the ElevenLabs Speech-to-Speech API endpoint, including all supported request parameters, their types, descriptions, and default values. It also outlines the expected response and potential error conditions.

SOURCE: https://elevenlabs.io/docs/api-reference/speech-to-speech/convert

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/speech-to-speech (inferred)

Request:
  Content-Type: multipart/form-data

  Parameters:
    audiofile:
      Type: file
      Required: true
      Description: The audio file which holds the content and emotion that will control the generated speech.
    model_id:
      Type: string
      Optional: true
      Default: eleven_english_sts_v2
      Description: Identifier of the model that will be used. Queryable via GET /v1/models. Must support speech-to-speech (can_do_voice_conversion property).
    voice_settings:
      Type: string or null (JSON encoded)
      Optional: true
      Description: Voice settings overriding stored settings for the given voice, applied only on the current request.
    seed:
      Type: integer or null
      Optional: true
      Range: 0 to 4294967295
      Description: If specified, attempts deterministic sampling. Determinism not guaranteed.
    remove_background_noise:
      Type: boolean
      Optional: true
      Default: false
      Description: If set, removes background noise using audio isolation model. Applies only to Voice Changer.
    file_format:
      Type: enum or null
      Optional: true
      Default: other
      Allowed values: pcm_s16le_16, other
      Description: The format of input audio. For 'pcm_s16le_16', input must be 16-bit PCM, 16kHz sample rate, mono, little-endian. Lower latency.

Response:
  Success (200 OK):
    Content-Type: audio/mpeg (inferred)
    Description: The generated audio file.

Errors:
  422 Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs API: Update Workspace Member Endpoint Reference
DESCRIPTION: This section provides a detailed reference for the `POST /v1/workspace/members` API endpoint. It outlines the HTTP method, full URL, required authentication headers, the structure and types of parameters in the request body, and the expected successful response format. It also lists potential error responses.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/members/update

LANGUAGE: APIDOC
CODE:
```
POST /v1/workspace/members

Headers:
  xi-api-key: string (Required)

Request Body:
  Type: object
  Properties:
    email: string (Required) - Email of the target user.
    is_locked: boolean or null (Optional) - Whether to lock or unlock the user account.
    workspace_role: enum or null (Optional) - Role dictating permissions in the workspace.
      Allowed values: workspace_admin, workspace_member

Response (200 Successful):
  Type: object
  Properties:
    status: string - The status of the workspace member update request. If the request was successful, the status will be 'ok'.
  Example:
    {
      "status": "ok"
    }

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference for Deleting an ElevenLabs Agent
DESCRIPTION: Provides the API specification for the DELETE /v1/convai/agents/:agent_id endpoint, detailing its HTTP method, URL structure, required path parameters, authentication headers, and possible error responses.

SOURCE: https://elevenlabs.io/docs/api-reference/agents/delete

LANGUAGE: APIDOC
CODE:
```
Method: DELETE
URL: https://api.elevenlabs.io/v1/convai/agents/:agent_id

Description: Delete an agent

Path Parameters:
  agent_id:
    Type: string
    Required: true
    Description: The id of an agent. This is returned on agent creation.

Headers:
  xi-api-key:
    Type: string
    Required: true

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference: List Phone Numbers Endpoint
DESCRIPTION: Detailed API documentation for the 'List phone numbers' endpoint. This section specifies the HTTP method, the full endpoint URL, required request headers, and the structure of a successful 200 OK response. It also outlines potential error responses, such as a 422 Unprocessable Entity error.

SOURCE: https://elevenlabs.io/docs/api-reference/phone-numbers/list

LANGUAGE: APIDOC
CODE:
```
Endpoint: GET /v1/convai/phone-numbers
Base URL: https://api.elevenlabs.io

Headers:
  xi-api-key: string (Required)

Response (200 Retrieved):
  [
    {
      "phone_number": "foo",
      "label": "foo",
      "phone_number_id": "foo",
      "assigned_agent": {
        "agent_id": "foo",
        "agent_name": "foo"
      },
      "provider": "twilio"
    }
  ]
  OR
  GetPhoneNumberTwilioResponseModel object (Show 5 properties)
  OR
  GetPhoneNumberSIPTrunkResponseModel object (Show 6 properties)

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Delete Voice API Endpoint Reference
DESCRIPTION: Documents the API endpoint for deleting a voice, including the HTTP method, path, required parameters, headers, and expected successful response structure with an example.

SOURCE: https://elevenlabs.io/docs/api-reference/voices/delete

LANGUAGE: APIDOC
CODE:
```
Method: DELETE
Path: /v1/voices/:voice_id
Description: Deletes a voice by its ID.

Path Parameters:
  voice_id:
    Type: string
    Required: true
    Description: ID of the voice to be used. You can use the Get voices endpoint list all the available voices.

Headers:
  xi-api-key:
    Type: string
    Required: true

Response (200 OK):
  Description: Successful Response
  Schema:
    status:
      Type: string
      Description: The status of the voice deletion request. If the request was successful, the status will be 'ok'. Otherwise an error message with status 500 will be returned.
  Example:
    {
      "status": "ok"
    }

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs Speech-to-Text API Reference
DESCRIPTION: This section details the API specifications for the ElevenLabs Speech-to-Text endpoint (`POST /v1/speech-to-text`). It outlines the required headers and optional query parameters, including their types, descriptions, and default values.

SOURCE: https://elevenlabs.io/docs/api-reference/speech-to-text/convert

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/speech-to-text
Description: Transcribe an audio or video file. If webhook is set to true, the request will be processed asynchronously and results sent to configured webhooks.

Headers:
  xi-api-key: string (Required)

Query Parameters:
  enable_logging: boolean (Optional, Defaults to true)
    Description: When enable_logging is set to false zero retention mode will be used for the request. This will mean history features are unavailable for this request, including request stitching. Zero retention mode may only be used by enterprise customers.
```

----------------------------------------

TITLE: API Reference: RAG Index Endpoint Schema
DESCRIPTION: Defines the request and response structures for an ElevenLabs API endpoint, including data types, required fields, and enumerated values for models and status.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/knowledge-base/compute-rag-index

LANGUAGE: APIDOC
CODE:
```
### Request Body
model: enum
  Required: true
  Allowed values: e5_mistral_7b_instruct, multilingual_e5_large_instruct

### Successful Response Body
id: string
model: enum
  Allowed values: e5_mistral_7b_instruct, multilingual_e5_large_instruct
status: enum
  (Show 6 enum values)
progress_percentage: double
document_model_index_usage: object
  (Show 1 properties)

### Errors
422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference for List Studio Projects Headers and Response Schema
DESCRIPTION: Documents the required headers and the structure of the successful response for the 'List Studio Projects' API. It specifies the 'xi-api-key' header as mandatory and describes the 'projects' array in the response, along with potential error codes like 422 for unprocessable entities.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/get-projects

LANGUAGE: APIDOC
CODE:
```
Headers:
  xi-api-key: string (Required)

Response:
  Successful Response:
    projects: list of objects
      A list of projects with their metadata.
      (Show 28 properties)

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference: POST /v1/sound-generation Endpoint
DESCRIPTION: This section provides a detailed API reference for the `POST /v1/sound-generation` endpoint, which allows users to convert text into sound effects. It outlines required headers, optional query parameters, request body fields, expected response format, and potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/sound-generation

LANGUAGE: APIDOC
CODE:
```
POST /v1/sound-generation

Headers:
  xi-api-key: string (Required)

Query Parameters:
  output_format: enum (Optional, Defaults to mp3_44100_128)
    Description: Output format of the generated audio. Formatted as codec_sample_rate_bitrate. So an mp3 with 22.05kHz sample rate at 32kbs is represented as mp3_22050_32. MP3 with 192kbps bitrate requires you to be subscribed to Creator tier or above. PCM with 44.1kHz sample rate requires you to be subscribed to Pro tier or above. Note that the μ-law format (sometimes written mu-law, often approximated as u-law) is commonly used for Twilio audio inputs.

Request Body:
  text: string (Required)
    Description: The text that will get converted into a sound effect.
  duration_seconds: double or null (Optional)
    Description: The duration of the sound which will be generated in seconds. Must be at least 0.5 and at most 22. If set to None we will guess the optimal duration using the prompt. Defaults to None.
  prompt_influence: double or null (Optional, Defaults to 0.3)
    Description: A higher prompt influence makes your generation follow the prompt more closely while also making generations less variable. Must be a value between 0 and 1. Defaults to 0.3.

Response:
  Description: The generated sound effect as an MP3 file

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: TypeScript Client Usage: Find Similar Voices
DESCRIPTION: Illustrates how to programmatically call the 'find similar voices' API using the ElevenLabs TypeScript client. It demonstrates client initialization with an API key and invoking the relevant method to fetch similar voices.

SOURCE: https://elevenlabs.io/docs/api-reference/voices/get-similar-library-voices

LANGUAGE: TypeScript
CODE:
```
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient({ apiKey: "YOUR_API_KEY" });
await client.voices.findSimilarVoices({});
```

----------------------------------------

TITLE: API Reference: Get Pronunciation Dictionary by Version
DESCRIPTION: This API documentation describes the `GET` endpoint for retrieving a specific version of a pronunciation dictionary. It details the required path parameters (`dictionary_id`, `version_id`), the necessary `xi-api-key` header for authentication, the expected PLS file response, and the `422 Unprocessable Entity` error.

SOURCE: https://elevenlabs.io/docs/api-reference/pronunciation-dictionaries/download

LANGUAGE: APIDOC
CODE:
```
GET /v1/pronunciation-dictionaries/:dictionary_id/:version_id/download

Path parameters:
  dictionary_id: string (Required) - The id of the pronunciation dictionary
  version_id: string (Required) - The id of the version of the pronunciation dictionary

Headers:
  xi-api-key: string (Required)

Response:
  The PLS file containing pronunciation dictionary rules

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs API: Invite User Endpoint Reference
DESCRIPTION: Detailed API documentation for the `POST /v1/workspace/invites/add` endpoint, which allows workspace administrators to send email invitations to new users. It specifies required headers, request body parameters (email, optional group_ids, workspace_permission), the successful response format, and potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/invite-user

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/workspace/invites/add
Description: Sends an email invitation to join your workspace to the provided email. If the user doesn't have an account they will be prompted to create one. If the user accepts this invite they will be added as a user to your workspace and your subscription using one of your seats. This endpoint may only be called by workspace administrators. If the user is already in the workspace a 400 error will be returned.

Headers:
  xi-api-key: string (Required)

Request Body (object):
  email: string (Required) - The email of the customer
  group_ids: list of strings or null (Optional) - The group ids of the user
  workspace_permission: enum or null (Optional) - The workspace permission of the user (Show 16 enum values)

Response (200 Successful):
  status: string - The status of the workspace invite request. If the request was successful, the status will be 'ok'. Otherwise an error message with status 500 will be returned.

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: cURL Example for Listing Knowledge Base Documents
DESCRIPTION: A command-line example using cURL to demonstrate how to send a GET request to the ElevenLabs API's knowledge base endpoint. This snippet shows how to include the necessary API key in the request header.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/knowledge-base/list

LANGUAGE: Shell
CODE:
```
curl https://api.elevenlabs.io/v1/convai/knowledge-base \
-H "xi-api-key: xi-api-key"
```

----------------------------------------

TITLE: API Reference for List Knowledge Base Documents Endpoint
DESCRIPTION: Comprehensive API documentation for the `GET /v1/convai/knowledge-base` endpoint, detailing the request method, path, required headers, optional query parameters with their types and constraints, and the structure of the successful response and potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/knowledge-base/get-knowledge-base-list

LANGUAGE: APIDOC
CODE:
```
GET /v1/convai/knowledge-base

Description: Get a list of available knowledge base documents

Headers:
  xi-api-key: string (Required)

Query parameters:
  cursor: string or null (Optional)
    Description: Used for fetching next page. Cursor is returned in the response.
  page_size: integer (Optional)
    Constraints: >=1, <=100
    Default: 30
    Description: How many documents to return at maximum. Can not exceed 100, defaults to 30.
  search: string or null (Optional)
    Description: If specified, the endpoint returns only such knowledge base documents whose names start with this string.
  show_only_owned_documents: boolean (Optional)
    Default: false
    Description: If set to true, the endpoint will return only documents owned by you (and not shared from somebody else).
  types: list of enums or null (Optional)
    Allowed values: file, url, text
    Description: If present, the endpoint will return only documents of the given types.
  use_typesense: boolean (Optional)
    Default: false
    Description: If set to true, the endpoint will use typesense DB to search for the documents).

Response:
  200 Retrieved:
    documents: list of objects
    has_more: boolean
    next_cursor: string or null
  422 Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference: Get Pronunciation Dictionary Endpoint
DESCRIPTION: This section details the API endpoint for retrieving a pronunciation dictionary. It specifies the HTTP method, URL path, required path parameters, authentication headers, and the full schema of the successful 200 OK response, including data types and descriptions for each field, along with an example response.

SOURCE: https://elevenlabs.io/docs/api-reference/pronunciation-dictionaries/get

LANGUAGE: APIDOC
CODE:
```
Endpoint: GET /v1/pronunciation-dictionaries/:pronunciation_dictionary_id

Description: Get metadata for a pronunciation dictionary

Path Parameters:
  pronunciation_dictionary_id:
    Type: string
    Required: true
    Description: The id of the pronunciation dictionary

Headers:
  xi-api-key:
    Type: string
    Required: true

Response (200 OK) Schema:
  id:
    Type: string
    Description: The ID of the pronunciation dictionary.
  latest_version_id:
    Type: string
    Description: The ID of the latest version of the pronunciation dictionary.
  latest_version_rules_num:
    Type: integer
    Description: The number of rules in the latest version of the pronunciation dictionary.
  name:
    Type: string
    Description: The name of the pronunciation dictionary.
  permission_on_resource:
    Type: enum or null
    Description: The permission on the resource of the pronunciation dictionary.
    Allowed values: admin, editor, viewer
  created_by:
    Type: string
    Description: The user ID of the creator of the pronunciation dictionary.
  creation_time_unix:
    Type: integer
    Description: The creation time of the pronunciation dictionary in Unix timestamp.
  archived_time_unix:
    Type: integer or null
    Description: The archive time of the pronunciation dictionary in Unix timestamp.
  description:
    Type: string or null
    Description: The description of the pronunciation dictionary.

Example 200 OK Response:
{
  "id": "5xM3yVvZQKV0EfqQpLrJ",
  "latest_version_id": "5xM3yVvZQKV0EfqQpLr2",
  "latest_version_rules_num": 2,
  "name": "My Dictionary",
  "permission_on_resource": "admin",
  "created_by": "ar6633Es2kUjFXBdR1iVc9ztsXl1",
  "creation_time_unix": 1714156800,
  "description": "This is a test dictionary"
}

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference: Create Knowledge Base Document from URL
DESCRIPTION: Detailed API documentation for the `POST /v1/convai/knowledge-base/url` endpoint. This endpoint facilitates the creation of a knowledge base document by scraping content from a provided URL. It specifies the required authentication header, the structure of the request body, and the format of successful and error responses.

SOURCE: https://elevenlabs.io/docs/api-reference/knowledge-base/create-from-url

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/convai/knowledge-base/url
Description: Create a knowledge base document generated by scraping the given webpage.

Headers:
  xi-api-key: string (Required)

Request Body:
  Type: object
  Properties:
    url: string (Required)
      Description: URL to a page of documentation that the agent will have access to in order to interact with users.
    name: string or null (Optional)
      Description: A custom, human-readable name for the document.
      Constraints: >=1 character

Successful Response (200):
  Type: object
  Properties:
    id: string
    name: string
  Example:
    {
      "id": "foo",
      "name": "foo"
    }

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Install Official ElevenLabs Client Libraries
DESCRIPTION: Commands to install the official ElevenLabs client libraries for Python and Node.js. These libraries provide convenient ways to interact with the ElevenLabs API from your applications, simplifying API calls and data handling.

SOURCE: https://elevenlabs.io/docs/api-reference/introduction

LANGUAGE: Python
CODE:
```
pip install elevenlabs
```

LANGUAGE: JavaScript
CODE:
```
npm install @elevenlabs/elevenlabs-js
```

----------------------------------------

TITLE: Eleven Labs Studio API: Convert Chapter Endpoint Reference
DESCRIPTION: This section provides a detailed API reference for the 'Convert Chapter' endpoint. It specifies the HTTP method, endpoint path, required path parameters, necessary authentication headers, and the structure of a successful response, along with common error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/convert-chapter

LANGUAGE: APIDOC
CODE:
```
Endpoint: Convert Chapter
Method: POST
Path: /v1/studio/projects/:project_id/chapters/:chapter_id/convert
Full URL: https://api.elevenlabs.io/v1/studio/projects/:project_id/chapters/:chapter_id/convert

Path Parameters:
  project_id (string, Required):
    The ID of the project to be used. You can use the [List projects] endpoint to list all the available projects.
  chapter_id (string, Required):
    The ID of the chapter to be used. You can use the [List project chapters] endpoint to list all the available chapters.

Headers:
  xi-api-key (string, Required)

Responses:
  200 Successful:
    status (string):
      The status of the studio chapter conversion request. If the request was successful, the status will be 'ok'. Otherwise an error message with status 500 will be returned.
  422 Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference for Stream Studio Project Audio
DESCRIPTION: Comprehensive API documentation for the endpoint to stream audio from a Studio project snapshot. It details the HTTP method, URL structure, required path parameters, authentication headers, optional request body parameters, and expected response/error types.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/stream-snapshot

LANGUAGE: APIDOC
CODE:
```
POST /v1/studio/projects/:project_id/snapshots/:project_snapshot_id/stream

Path Parameters:
  project_id: string (Required)
    Description: The ID of the project to be used. You can use the List projects endpoint to list all the available projects.
  project_snapshot_id: string (Required)
    Description: The ID of the Studio project snapshot.

Headers:
  xi-api-key: string (Required)

Request Body:
  Type: object
  Properties:
    convert_to_mpeg: boolean (Optional, default: false)
      Description: Whether to convert the audio to mpeg format.

Responses:
  Successful Response
  Streamed Response: {"type":"json","value":"foo"}

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Knowledge Base and Tools Endpoint Updates
DESCRIPTION: Modifications to existing Knowledge Base and Tools endpoints, including new properties for documentation and dependent agents.

SOURCE: https://elevenlabs.io/docs/changelog/2025/2/10

LANGUAGE: APIDOC
CODE:
```
GET /v1/convai/agents/{agent_id}/knowledge-base/{documentation_id} - Added `name` and `access_level` properties
```

LANGUAGE: APIDOC
CODE:
```
GET /v1/convai/knowledge-base/{documentation_id} - Added `name` and `access_level` properties
```

LANGUAGE: APIDOC
CODE:
```
GET /v1/convai/tools/{tool_id} - Added `dependent_agents` property
```

LANGUAGE: APIDOC
CODE:
```
PATCH /v1/convai/tools/{tool_id} - Added `dependent_agents` property
```

----------------------------------------

TITLE: Enable PUT Requests in Conversational AI Server Tools
DESCRIPTION: Enhances the functionality of Conversational AI server tools by adding support for making PUT requests, providing more flexibility for tool interactions.

SOURCE: https://elevenlabs.io/docs/changelog/2025/4/28

LANGUAGE: APIDOC
CODE:
```
Conversational AI Server Tools:
  Supported HTTP Methods: PUT requests are now supported.
  Documentation: /docs/conversational-ai/customization/tools/server-tools
```

----------------------------------------

TITLE: ElevenLabs API Query Parameters Reference
DESCRIPTION: Detailed documentation for various query parameters used in ElevenLabs API requests, including options for controlling logging behavior, optimizing streaming latency, and specifying the desired audio output format.

SOURCE: https://elevenlabs.io/docs/api-reference/text-to-speech/convert-with-timestamps

LANGUAGE: APIDOC
CODE:
```
Query Parameters:

enable_logging:
  Type: boolean
  Optional: true
  Default: true
  Description: When enable_logging is set to false zero retention mode will be used for the request. This will mean history features are unavailable for this request, including request stitching. Zero retention mode may only be used by enterprise customers.

optimize_streaming_latency:
  Type: integer or null
  Optional: true
  Deprecated: true
  Default: None
  Description: You can turn on latency optimizations at some cost of quality. The best possible final latency varies by model. Possible values:
    0 - default mode (no latency optimizations)
    1 - normal latency optimizations (about 50% of possible latency improvement of option 3)
    2 - strong latency optimizations (about 75% of possible latency improvement of option 3)
    3 - max latency optimizations
    4 - max latency optimizations, but also with text normalizer turned off for even more latency savings (best latency, but can mispronounce eg numbers and dates).

output_format:
  Type: enum
  Optional: true
  Default: mp3_44100_128
  Description: Output format of the generated audio. Formatted as codec_sample_rate_bitrate. So an mp3 with 22.05kHz sample rate at 32kbs is represented as mp3_22050_32. MP3 with 192kbps bitrate requires you to be subscribed to Creator tier or above. PCM with 44.1kHz sample rate requires you to be subscribed to Pro tier or above. Note that the µ-law format (sometimes written mu-law, often approximated as u-law) is commonly used for Twilio audio inputs.
```

----------------------------------------

TITLE: API Reference: Stream Simulate Conversation Endpoint
DESCRIPTION: This section details the POST /v1/convai/agents/:agent_id/simulate-conversation/stream API endpoint. It explains its purpose, lists required path parameters like agent_id, and header parameters such as xi-api-key, along with their types and descriptions.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/agents/simulate-conversation-stream

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/convai/agents/:agent_id/simulate-conversation/stream
Description: Run a conversation between the agent and a simulated user and stream back the response. Response is streamed back as partial lists of messages that should be concatenated and once the conversation has complete a single final message with the conversation analysis will be sent.
Parameters:
  Path:
    agent_id (string, Required): The id of an agent. This is returned on agent creation.
  Headers:
    xi-api-key (string, Required)
```

----------------------------------------

TITLE: API Reference for Stream Simulate Conversation Endpoint
DESCRIPTION: This section provides the full API documentation for the `POST /v1/convai/agents/:agent_id/simulate-conversation/stream` endpoint. It details the required path parameters, headers, the structure of the request body for simulation specifications, and potential error responses.

SOURCE: https://elevenlabs.io/docs/api-reference/agents/simulate-conversation-stream

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/convai/agents/:agent_id/simulate-conversation/stream
Description: Run a conversation between the agent and a simulated user and stream back the response. Response is streamed back as partial lists of messages that should be concatenated and once the conversation has complete a single final message with the conversation analysis will be sent.

Path Parameters:
  agent_id: string (Required)
    Description: The id of an agent. This is returned on agent creation.

Headers:
  xi-api-key: string (Required)

Request Body:
  simulation_specification: object (Required)
    Description: A specification detailing how the conversation should be simulated
    Properties: (Show 4 properties)
  extra_evaluation_criteria: list of objects or null (Optional)
    Description: A list of evaluation criteria to test
    Properties: (Show 5 properties)

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs API: Get Dependent Agents Request Details
DESCRIPTION: Details the required and optional parameters for the 'Get Dependent Agents' API request, including path parameters (`tool_id`), required headers (`xi-api-key`), and query parameters (`cursor`, `page_size`) with their types and constraints.

SOURCE: https://elevenlabs.io/docs/api-reference/tools/get-dependent-agents

LANGUAGE: APIDOC
CODE:
```
### Path parameters
tool_idstringRequired
ID of the requested tool.

### Headers
xi-api-keystringRequired

### Query parameters
cursorstring or nullOptional
Used for fetching next page. Cursor is returned in the response.

page_sizeintegerOptional`>=1``<=100`Defaults to `30`
How many documents to return at maximum. Can not exceed 100, defaults to 30.
```

----------------------------------------

TITLE: API Reference: Update Secret Endpoint
DESCRIPTION: Detailed API documentation for the PATCH /v1/convai/secrets/:secret_id endpoint, used to update an existing secret. It specifies required path parameters, headers, the structure of the request body, and the expected successful response schema.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/workspace/secrets/update-secret

LANGUAGE: APIDOC
CODE:
```
PATCH /v1/convai/secrets/:secret_id

Description: Update an existing secret for the workspace.

Path Parameters:
  secret_id: string (Required)
    The unique identifier of the secret to update.

Headers:
  xi-api-key: string (Required)
    Your ElevenLabs API key.

Request Body (application/json):
  type: "update" (Required)
    The type of update operation.
  name: string (Required)
    The new name for the secret.
  value: string (Required)
    The new value for the secret.

Response (200 Updated - application/json):
  type: "stored"
    The type of the secret after update.
  secret_id: string
    The unique identifier of the updated secret.
  name: string
    The name of the updated secret.
```

----------------------------------------

TITLE: ElevenLabs Text-to-Speech Stream API Endpoint Reference
DESCRIPTION: This section provides comprehensive API documentation for the ElevenLabs text-to-speech streaming endpoint. It details the HTTP method, URL, path parameters, required headers, and optional query parameters, including their types, descriptions, and default values.

SOURCE: https://elevenlabs.io/docs/api-reference/text-to-speech/convert-as-stream

LANGUAGE: APIDOC
CODE:
```
Endpoint:
  Method: POST
  URL: https://api.elevenlabs.io/v1/text-to-speech/:voice_id/stream
  Description: Converts text into speech using a voice of your choice and returns audio as an audio stream.

Path Parameters:
  voice_id:
    Type: string
    Required: true
    Description: ID of the voice to be used. Use the Get voices endpoint list all the available voices.

Headers:
  xi-api-key:
    Type: string
    Required: true

Query Parameters:
  enable_logging:
    Type: boolean
    Optional: true
    Default: true
    Description: When enable_logging is set to false zero retention mode will be used for the request. This will mean history features are unavailable for this request, including request stitching. Zero retention mode may only be used by enterprise customers.
  optimize_streaming_latency:
    Type: integer or null
    Optional: true
    Deprecated: true
    Default: None
    Description: You can turn on latency optimizations at some cost of quality. The best possible final latency varies by model. Possible values: 0 (default mode), 1 (normal latency optimizations), 2 (strong latency optimizations), 3 (max latency optimizations), 4 (max latency optimizations, with text normalizer turned off).
  output_format:
    Type: enum
    Optional: true
    Default: mp3_44100_128
    Description: Output format of the generated audio. Formatted as codec_sample_rate_bitrate. So an mp3 with 22.05kHz sample rate at 32kbs is represented as mp3_22050_32. MP3 with 192kbps bitrate requires you to be subscribed to Creator tier or above. PCM with 44.1kHz sample rate requires you to be subscribed to Pro tier or above. Note that the µ-law format (sometimes written mu-law, often approximated as u-law) is commonly used for Twilio audio inputs.
```

----------------------------------------

TITLE: Knowledge Base Document Endpoint API Reference
DESCRIPTION: Comprehensive API documentation for the ElevenLabs knowledge base document endpoint, covering input parameters, expected successful responses, and possible error conditions.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/knowledge-base/update

LANGUAGE: APIDOC
CODE:
```
### Request Body Parameters

- `name`: string (Required, >=1 character)
  Description: A custom, human-readable name for the document.

### Successful Responses

- `GetKnowledgeBaseURLResponseModel`: object (8 properties)
- `GetKnowledgeBaseFileResponseModel`: object (7 properties)
- `GetKnowledgeBaseTextResponseModel`: object (7 properties)

### Error Responses

- `422 Unprocessable Entity Error`
```

----------------------------------------

TITLE: ElevenLabs Audio Native Project Update API Reference
DESCRIPTION: This section details the API endpoint for updating an Audio Native project. It specifies the HTTP method (POST), the URL path, required path parameters like `project_id`, and headers such as `xi-api-key`. It also outlines the expected multipart form data for the request, including optional `file`, `auto_convert`, and `auto_publish` fields, and describes the structure of the successful 200 response.

SOURCE: https://elevenlabs.io/docs/api-reference/audio-native/update

LANGUAGE: APIDOC
CODE:
```
Endpoint: Update audio native project
Method: POST
Path: /v1/audio-native/:project_id/content

Path Parameters:
  project_id: string (Required)
    Description: The ID of the project to be used. You can use the List projects endpoint to list all the available projects.

Headers:
  xi-api-key: string (Required)

Request Body (multipart/form-data):
  file: file (Optional)
    Description: Either txt or HTML input file containing the article content. HTML should be formatted as follows ‘<html><body><div><p>Your content</p><h5>More of your content</h5><p>Some more of your content</p></div></body></html>’
  auto_convert: boolean (Optional, Default: false)
    Description: Whether to auto convert the project to audio or not.
  auto_publish: boolean (Optional, Default: false)
    Description: Whether to auto publish the new project snapshot after it's converted.

Response (200 Successful):
  project_id: string
    Description: The ID of the project.
  converting: boolean
    Description: Whether the project is currently being converted.
  publishing: boolean
    Description: Whether the project is currently being published.
  html_snippet: string
    Description: The HTML snippet to embed the Audio Native player.

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Documentation for `transfer_to_agent` System Tool
DESCRIPTION: This section provides detailed API documentation for the `transfer_to_agent` system tool. It covers the tool's purpose, the conditions under which an LLM should trigger it, and a comprehensive list of its parameters, including their types and descriptions.

SOURCE: https://elevenlabs.io/docs/conversational-ai/customization/tools/agent-transfer

LANGUAGE: APIDOC
CODE:
```
Tool: transfer_to_agent
Purpose: Transfer conversations between specialized AI agents based on user needs.
Trigger Conditions:
  - User request requires specialized knowledge or different agent capabilities
  - Current agent cannot adequately handle the query
  - Conversation flow indicates need for different agent type
Parameters:
  - reason (string, optional): The reason for the agent transfer
  - agent_number (integer, required): Zero-indexed number of the agent to transfer to (based on configured transfer rules)
```

----------------------------------------

TITLE: API Reference: Get Signed URL Endpoint
DESCRIPTION: Comprehensive API documentation for the 'Get Signed URL' endpoint, detailing the HTTP method, path, required headers, query parameters, successful response schema, and potential error codes. This endpoint allows obtaining a pre-signed URL to initiate a conversation with an ElevenLabs agent.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/conversations/get-signed-url

LANGUAGE: APIDOC
CODE:
```
GET
https://api.elevenlabs.io/v1/convai/conversation/get-signed-url
```

LANGUAGE: APIDOC
CODE:
```
### Headers
xi-api-keystringRequired

### Query parameters
agent_idstringRequired
The id of the agent you're taking the action on.

### Response
Successful Response
signed_urlstring

### Errors
422
Unprocessable Entity Error
```

LANGUAGE: APIDOC
CODE:
```
{
  "signed_url": "foo"
}
```

----------------------------------------

TITLE: API Reference: PATCH /v1/convai/settings
DESCRIPTION: Detailed API documentation for the PATCH /v1/convai/settings endpoint, used to update Conversational AI settings for a workspace. It specifies the endpoint URL, required headers, and the structure of the request body parameters, along with a sample successful response.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/workspace/update

LANGUAGE: APIDOC
CODE:
```
Endpoint: PATCH https://api.elevenlabs.io/v1/convai/settings

Description: Update Convai settings for the workspace

Headers:
  xi-api-key: string (Required)

Request Body (JSON Object):
  conversation_initiation_client_data_webhook: object or null (Optional)
    (Show 2 properties)
  webhooks: object (Optional)
    (Show 1 properties)
  can_use_mcp_servers: boolean (Optional, Defaults to false)
    Description: Whether the workspace can use MCP servers
  rag_retention_period_days: integer (Optional, <=30, Defaults to 10)

Response (200 Updated):
{
  "conversation_initiation_client_data_webhook": {
    "url": "foo",
    "request_headers": {}
  },
  "webhooks": {
    "post_call_webhook_id": "foo"
  },
  "can_use_mcp_servers": false,
  "rag_retention_period_days": 10
}
```

----------------------------------------

TITLE: API Reference: Get Conversation Details
DESCRIPTION: Documents the API endpoint for retrieving detailed information about a specific conversation. This GET request requires a conversation ID as a path parameter and an API key in the headers. The response provides comprehensive conversation data including agent ID, status, transcript, metadata, and audio presence.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/conversations/get-conversation

LANGUAGE: APIDOC
CODE:
```
GET /v1/convai/conversations/:conversation_id

Description: Get the details of a particular conversation.

Path Parameters:
  conversation_id (string, Required): The ID of the conversation you're taking the action on.

Headers:
  xi-api-key (string, Required): Your ElevenLabs API key.

Response (200 OK):
  application/json:
    {
      "agent_id": "123",
      "conversation_id": "123",
      "status": "processing",
      "transcript": [
        {
          "role": "user",
          "time_in_call_secs": 10,
          "message": "Hello, how are you?"
        }
      ],
      "metadata": {
        "start_time_unix_secs": 1714423232,
        "call_duration_secs": 10
      },
      "has_audio": true,
      "has_user_audio": true,
      "has_response_audio": true
    }
```

----------------------------------------

TITLE: ElevenLabs API: Query Parameters, Response, and Errors
DESCRIPTION: Details the available query parameters for an ElevenLabs API endpoint, its successful response structure, and common error codes. This includes options for pagination, filtering by name or type, and specifying document ownership.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/knowledge-base/list

LANGUAGE: APIDOC
CODE:
```
Query parameters:
  cursor: string or null (Optional)
    Description: Used for fetching next page. Cursor is returned in the response.
  page_size: integer (Optional)
    Constraints: >=1, <=100
    Default: 30
    Description: How many documents to return at maximum. Can not exceed 100, defaults to 30.
  search: string or null (Optional)
    Description: If specified, the endpoint returns only such knowledge base documents whose names start with this string.
  show_only_owned_documents: boolean (Optional)
    Default: false
    Description: If set to true, the endpoint will return only documents owned by you (and not shared from somebody else).
  types: list of enums or null (Optional)
    Allowed values: file, url, text
    Description: If present, the endpoint will return only documents of the given types.
  use_typesense: boolean (Optional)
    Default: false
    Description: If set to true, the endpoint will use typesense DB to search for the documents.

Response:
  Successful Response:
    documents: list of objects
    has_more: boolean
    next_cursor: string or null

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Create MCP Server Tool Approval using ElevenLabs TypeScript SDK
DESCRIPTION: This code snippet demonstrates how to create a new MCP server tool approval using the ElevenLabs TypeScript SDK. It initializes the client with an API key and then calls the 'create' method on the 'toolApprovals' object, providing the MCP server ID, tool name, and tool description.

SOURCE: https://elevenlabs.io/docs/api-reference/mcp/approval-policies/create

LANGUAGE: TypeScript
CODE:
```
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient({ apiKey: "YOUR_API_KEY" });
await client.conversationalAi.mcpServers.toolApprovals.create("mcp_server_id", {
  toolName: "tool_name",
  toolDescription: "tool_description"
});
```

----------------------------------------

TITLE: API Reference: List Pronunciation Dictionaries Endpoint
DESCRIPTION: This section provides a detailed specification for the GET /v1/pronunciation-dictionaries API endpoint. It outlines the required headers, query parameters for filtering and pagination, and the structure of the successful response, including an example JSON payload and potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/pronunciation-dictionaries/list

LANGUAGE: APIDOC
CODE:
```
GET /v1/pronunciation-dictionaries

Description: Get a list of the pronunciation dictionaries you have access to and their metadata.

Headers:
  xi-api-key: string (Required)

Query Parameters:
  cursor: string or null (Optional)
    Description: Used for fetching next page. Cursor is returned in the response.
  page_size: integer (Optional)
    Constraints: >=1, <=100
    Default: 30
    Description: How many pronunciation dictionaries to return at maximum.
  sort: enum or null (Optional)
    Default: creation_time_unix
    Allowed values: creation_time_unix, name
    Description: Which field to sort by.
  sort_direction: string or null (Optional)
    Default: DESCENDING
    Allowed values: ASCENDING, DESCENDING
    Description: Which direction to sort the voices in.

Responses:
  200 OK (Retrieved):
    Description: Successful Response
    Body:
      pronunciation_dictionaries: list of objects
        Description: A list of pronunciation dictionaries and their metadata.
        Properties:
          id: string
          latest_version_id: string
          latest_version_rules_num: integer
          name: string
          permission_on_resource: string
          created_by: string
          creation_time_unix: integer
          description: string
      has_more: boolean
        Description: Whether there are more pronunciation dictionaries to fetch.
      next_cursor: string or null
        Description: The next cursor to use for pagination.
    Example:
      {
        "pronunciation_dictionaries": [
          {
            "id": "5xM3yVvZQKV0EfqQpLrJ",
            "latest_version_id": "5xM3yVvZQKV0EfqQpLr2",
            "latest_version_rules_num": 2,
            "name": "My Dictionary",
            "permission_on_resource": "admin",
            "created_by": "ar6633Es2kUjFXBdR1iVc9ztsXl1",
            "creation_time_unix": 1714156800,
            "description": "This is a test dictionary"
          }
        ],
        "has_more": false,
        "next_cursor": "5xM3yVvZQKV0EfqQpLr2"
      }
  422 Unprocessable Entity:
    Description: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference: List Knowledge Base Documents Endpoint
DESCRIPTION: Detailed API documentation for the GET /v1/convai/knowledge-base endpoint. This section outlines the request method, URL, required headers, optional query parameters with their types and descriptions, and the structure of the successful response.

SOURCE: https://elevenlabs.io/docs/api-reference/knowledge-base/list

LANGUAGE: APIDOC
CODE:
```
Endpoint:
  GET /v1/convai/knowledge-base

Headers:
  xi-api-key: string (Required)

Query Parameters:
  cursor: string or null (Optional)
    Description: Used for fetching next page. Cursor is returned in the response.
  page_size: integer (Optional)
    Constraints: >=1, <=100
    Default: 30
    Description: How many documents to return at maximum. Can not exceed 100, defaults to 30.
  search: string or null (Optional)
    Description: If specified, the endpoint returns only such knowledge base documents whose names start with this string.
  show_only_owned_documents: boolean (Optional)
    Default: false
    Description: If set to true, the endpoint will return only documents owned by you (and not shared from somebody else).
  types: list of enums or null (Optional)
    Allowed values: file, url, text
    Description: If present, the endpoint will return only documents of the given types.
  use_typesense: boolean (Optional)
    Default: false
    Description: If set to true, the endpoint will use typesense DB to search for the documents).

Response (200 Successful Response):
  documents: list of objects
  has_more: boolean
  next_cursor: string or null

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs Studio API: List Chapters Endpoint Parameters and Errors
DESCRIPTION: This section outlines the required parameters, headers, and potential error responses for the ElevenLabs Studio API's 'List Chapters' endpoint. It specifies the `project_id` path parameter and the `xi-api-key` header, along with a common 422 Unprocessable Entity error.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/get-chapters

LANGUAGE: APIDOC
CODE:
```
Path parameters:
  project_id: string (Required)
    The ID of the Studio project.
Headers:
  xi-api-key: string (Required)
Response:
  Successful Response
  chapters: list of objects
    Show 8 properties
Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Conversational AI API Error Responses
DESCRIPTION: Documents common error codes and their descriptions for the ElevenLabs Conversational AI API.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/conversations/get-conversation

LANGUAGE: APIDOC
CODE:
```
Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs Dubbing API: Get Dubbing Endpoint Reference
DESCRIPTION: Detailed API documentation for the GET /v1/dubbing/:dubbing_id endpoint. This section outlines the endpoint's purpose, required path parameters, necessary headers, the structure of a successful 200 OK response, and potential error responses like 422 Unprocessable Entity.

SOURCE: https://elevenlabs.io/docs/api-reference/dubbing/get

LANGUAGE: APIDOC
CODE:
```
GET /v1/dubbing/:dubbing_id

Description: Returns metadata about a dubbing project, including whether it's still in progress or not.

Path Parameters:
  dubbing_id: string (Required) - ID of the dubbing project.

Headers:
  xi-api-key: string (Required)

Responses:
  200 OK (Retrieved):
    Description: Successful Response
    Body:
      dubbing_id: string - The ID of the dubbing project.
      name: string - The name of the dubbing project.
      status: string - The status of the dubbing project. Either 'dubbed', 'dubbing' or 'failed'.
      target_languages: list of strings - The target languages of the dubbing project.
      media_metadata: object or null - The media metadata of the dubbing project.
      error: string or null - Optional error message if the dubbing project failed.
  422 Unprocessable Entity Error:
    Description: Unprocessable Entity Error
```

----------------------------------------

TITLE: Deprecated ElevenLabs Conversational AI API Endpoints
DESCRIPTION: Documents the deprecation of the `POST /v1/convai/add-tool` endpoint, recommending the use of `POST /v1/convai/tools` instead.

SOURCE: https://elevenlabs.io/docs/changelog/2025/2/10

LANGUAGE: APIDOC
CODE:
```
Conversational AI
  - POST /v1/convai/add-tool - Use POST /v1/convai/tools instead
```

----------------------------------------

TITLE: API Reference for Get Conversation Audio Endpoint
DESCRIPTION: Detailed API documentation for the 'Get conversation audio' endpoint, specifying the HTTP GET method, URL structure, required path parameters like `conversation_id`, necessary `xi-api-key` header, and potential `422 Unprocessable Entity Error`.

SOURCE: https://elevenlabs.io/docs/api-reference/conversations/get-audio

LANGUAGE: APIDOC
CODE:
```
GET /v1/convai/conversations/:conversation_id/audio

Path parameters:
  conversation_id: string (Required)
    Description: The id of the conversation you're taking the action on.

Headers:
  xi-api-key: string (Required)

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Get Conversational AI Dashboard Settings API Reference
DESCRIPTION: This section documents the API endpoint for retrieving conversational AI dashboard settings. It specifies the HTTP method, path, required headers, successful response structure, and potential error codes.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/workspace/dashboard/get

LANGUAGE: APIDOC
CODE:
```
Endpoint: GET /v1/convai/settings/dashboard

Description: Retrieve Convai dashboard settings for the workspace

Headers:
  - xi-api-key: string (Required)

Response (200 Retrieved):
  charts: list of objects or null
  Example:
    {
      "charts": [
        {
          "name": "foo",
          "type": "call_success"
        }
      ]
    }

Errors:
  - 422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Weather Tool Webhook Configuration
DESCRIPTION: Defines the webhook configuration for the weather tool, specifying its name, description, HTTP method, and the API endpoint URL with dynamic latitude and longitude query parameters for fetching current and hourly weather data.

SOURCE: https://elevenlabs.io/docs/conversational-ai/customization/tools/server-tools

LANGUAGE: APIDOC
CODE:
```
Tool Name: get_weather
Description: Gets the current weather forecast for a location
Method: GET
URL: https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m
```

----------------------------------------

TITLE: Fetch Dubbing Resource with ElevenLabs TypeScript SDK
DESCRIPTION: Illustrates how to programmatically retrieve a dubbing resource using the official ElevenLabs TypeScript SDK. This example demonstrates client initialization with an API key and making a GET request for a specific dubbing ID.

SOURCE: https://elevenlabs.io/docs/api-reference/dubbing/resources/get-resource

LANGUAGE: TypeScript
CODE:
```
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient({ apiKey: "YOUR_API_KEY" });
await client.dubbing.resource.get("dubbing_id");
```

----------------------------------------

TITLE: API Reference: Get Knowledge Base Document Chunk
DESCRIPTION: This section details the API endpoint for retrieving a specific document chunk from the ElevenLabs knowledge base. It includes the HTTP method, URL structure, required path parameters, headers, and the expected successful response format.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/knowledge-base/get-chunk

LANGUAGE: APIDOC
CODE:
```
GET https://api.elevenlabs.io/v1/convai/knowledge-base/:documentation_id/chunk/:chunk_id

Description: Get details about a specific documentation part used by RAG.

Path parameters:
  documentation_id: string (Required)
    The id of a document from the knowledge base. This is returned on document addition.
  chunk_id: string (Required)
    The id of a document RAG chunk from the knowledge base.

Headers:
  xi-api-key: string (Required)

Response (200 Retrieved):
  id: string
  name: string
  content: string
```

----------------------------------------

TITLE: List Conversations API Endpoint and TypeScript Client Usage
DESCRIPTION: This section provides comprehensive documentation for the GET /v1/convai/conversations API endpoint, allowing users to retrieve a list of conversations. It includes a TypeScript example demonstrating how to use the ElevenLabs client library, details all request headers and query parameters for filtering and pagination, and outlines the structure of both successful and error responses.

SOURCE: https://elevenlabs.io/docs/api-reference/conversations/list

LANGUAGE: TypeScript
CODE:
```
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient({ apiKey: "YOUR_API_KEY" });
await client.conversationalAi.conversations.list();
```

LANGUAGE: APIDOC
CODE:
```
Endpoint: GET /v1/convai/conversations
Description: Get all conversations of agents that user owns, with option to restrict to a specific agent.

Headers:
  xi-api-key: string (Required)

Query Parameters:
  cursor: string or null (Optional) - Used for fetching next page. Cursor is returned in the response.
  agent_id: string or null (Optional) - The id of the agent you're taking the action on.
  call_successful: enum or null (Optional) - The result of the success evaluation. Allowed values: success, failure, unknown.
  call_start_before_unix: integer or null (Optional) - Unix timestamp (in seconds) to filter conversations up to this start date.
  call_start_after_unix: integer or null (Optional) - Unix timestamp (in seconds) to filter conversations after to this start date.
  page_size: integer (Optional) - >=1, <=100. Defaults to 30. How many conversations to return at maximum. Can not exceed 100, defaults to 30.

Responses:
  200 Retrieved:
    Description: Successful Response
    Body:
      conversations: list of objects (Show 8 properties)
        agent_id: string
        conversation_id: string
        start_time_unix_secs: integer
        call_duration_secs: integer
        message_count: integer
        status: string
        call_successful: string
        agent_name: string
      has_more: boolean
      next_cursor: string or null
    Example:
      {
        "conversations": [
          {
            "agent_id": "foo",
            "conversation_id": "foo",
            "start_time_unix_secs": 42,
            "call_duration_secs": 42,
            "message_count": 42,
            "status": "initiated",
            "call_successful": "success",
            "agent_name": "foo"
          }
        ],
        "has_more": true,
        "next_cursor": "foo"
      }

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs API: Delete MCP Server Tool Approval
DESCRIPTION: Comprehensive API documentation for deleting a specific tool approval for an MCP server. This includes the endpoint, path parameters, required headers, successful response structure, and potential error codes.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/mcp/approval-policies/delete

LANGUAGE: APIDOC
CODE:
```
Endpoint:
  Method: DELETE
  URL: https://api.elevenlabs.io/v1/convai/mcp-servers/:mcp_server_id/tool-approvals/:tool_name
  Path: /v1/convai/mcp-servers/:mcp_server_id/tool-approvals/:tool_name

Path Parameters:
  mcp_server_id:
    Type: string
    Required: true
    Description: ID of the MCP Server.
  tool_name:
    Type: string
    Required: true
    Description: Name of the MCP tool to remove approval for.

Headers:
  xi-api-key:
    Type: string
    Required: true

Response (200 OK - Deleted):
  id: string
  config: object (Show 8 properties)
  metadata: object (The metadata of the MCP Server, Show 2 properties)
  access_info: object or null (The access information of the MCP Server, Show 4 properties)
  dependent_agents: list of objects or null (List of agents that depend on this MCP Server, Show 2 variants)

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Eleven Labs Dubbing API: Translate Segment Endpoint Reference
DESCRIPTION: Comprehensive API documentation for the `POST /v1/dubbing/resource/:dubbing_id/translate` endpoint. It details the HTTP method, URL structure, path parameters, required headers, request body schema including `segments` and `languages`, and the successful response schema.

SOURCE: https://elevenlabs.io/docs/api-reference/dubbing/resources/translate-segment

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/dubbing/resource/:dubbing_id/translate
Description: Regenerate the translations for either the entire resource or the specified segments/languages. Will automatically transcribe missing transcriptions. Will not automatically regenerate the dubs.

Path Parameters:
  dubbing_id:
    Type: string
    Required: true
    Description: ID of the dubbing project.

Headers:
  xi-api-key:
    Type: string
    Required: true
    Description: API key for authentication.

Request Body:
  Type: object
  Properties:
    segments:
      Type: list of strings
      Required: true
      Description: Translate only this list of segments.
    languages:
      Type: list of strings or null
      Required: true
      Description: Translate only these languages for each segment.

Response (200 Successful):
  Type: object
  Properties:
    version:
      Type: integer
      Description: Version number of the translation.

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Create Studio Project API Endpoint Reference
DESCRIPTION: This snippet defines the HTTP POST endpoint used to create a new Studio project within the Eleven Labs platform. It specifies the full API path and the HTTP method required for the operation.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/add-project

LANGUAGE: APIDOC
CODE:
```
POST
https://api.elevenlabs.io/v1/studio/projects

POST
/v1/studio/projects
```

----------------------------------------

TITLE: Detailed API Specification: List Similar Voices
DESCRIPTION: Comprehensive specification for the 'List similar voices' API, covering required headers, optional request parameters with their types and descriptions, and the detailed structure of the successful response object, including all voice properties and pagination indicators.

SOURCE: https://elevenlabs.io/docs/api-reference/voices/get-similar-library-voices

LANGUAGE: APIDOC
CODE:
```
Headers:
  xi-api-key: string (Required)

Request Body (multipart/form-data):
  audio_file: file (Optional)
  similarity_threshold: double or null (Optional)
    Description: Threshold for voice similarity between provided sample and library voices. Values range from 0 to 2. The smaller the value the more similar voices will be returned.
  top_k: integer or null (Optional)
    Description: Number of most similar voices to return. If similarity_threshold is provided, less than this number of voices may be returned. Values range from 1 to 100.

Response (200 Successful):
  voices: list of objects
    Description: The list of shared voices
    Properties:
      public_owner_id: string
      voice_id: string
      date_unix: integer
      name: string
      accent: string
      gender: string
      age: string
      descriptive: string
      use_case: string
      category: string
      usage_character_count_1y: integer
      usage_character_count_7d: integer
      play_api_usage_character_count_1y: integer
      cloned_by_count: integer
      free_users_allowed: boolean
      live_moderation_enabled: boolean
      featured: boolean
      language: string
      description: string
      preview_url: string
      rate: integer
      verified_languages: list of objects
        language: string
        model_id: string
        accent: string
        locale: string
        preview_url: string
  has_more: boolean
    Description: Whether there are more shared voices in subsequent pages.
  last_sort_id: string or null
```

----------------------------------------

TITLE: API Reference: Get Knowledge Base Document Content
DESCRIPTION: Documents the API endpoint for retrieving the full content of a specific document from the ElevenLabs conversational AI knowledge base. It outlines the HTTP method, URL structure, required parameters, headers, and potential error responses.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/knowledge-base/get-content

LANGUAGE: APIDOC
CODE:
```
GET https://api.elevenlabs.io/v1/convai/knowledge-base/:documentation_id/content

Description: Get the entire content of a document from the knowledge base

Path parameters:
  documentation_id: string (Required)
    Description: The id of a document from the knowledge base. This is returned on document addition.

Headers:
  xi-api-key: string (Required)

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference: Create Podcast Endpoint Details
DESCRIPTION: This section provides the detailed specification for the ElevenLabs Studio API's 'Create Podcast' endpoint. It outlines the HTTP method, URL, required request headers, and the comprehensive structure of both the request and successful response bodies. This endpoint facilitates the creation and automatic conversion of podcast projects within the ElevenLabs platform.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/create-podcast

LANGUAGE: APIDOC
CODE:
```
Endpoint:
  POST /v1/studio/podcasts

Headers:
  xi-api-key: string (Required)

Request Body Schema:
{
  "model_id": "eleven_multilingual_v2",
  "mode": {
    "type": "foo",
    "conversation": {
      "host_voice_id": "foo",
      "guest_voice_id": "foo"
    }
  },
  "source": {
    "type": "foo",
    "text": "foo"
  }
}

Response Body Schema (200 Successful):
{
  "project": {
    "project_id": "foo",
    "name": "foo",
    "create_date_unix": 42,
    "default_title_voice_id": "foo",
    "default_paragraph_voice_id": "foo",
    "default_model_id": "foo",
    "can_be_downloaded": true,
    "volume_normalization": true,
    "state": "creating",
    "access_level": "admin",
    "quality_check_on": true,
    "quality_check_on_when_bulk_convert": true,
    "last_conversion_date_unix": 42,
    "title": "foo",
    "author": "foo",
    "description": "foo",
    "genres": [
      "foo"
    ],
    "cover_image_url": "foo",
    "target_audience": "children",
    "language": "foo",
    "content_type": "foo",
    "original_publication_date": "foo",
    "mature_content": true,
    "isbn_number": "foo",
    "fiction": "fiction",
    "creation_meta": {
      "creation_progress": 42,
      "status": "pending",
      "type": "blank"
    },
    "source_type": "blank",
    "chapters_enabled": true
  }
}
```

----------------------------------------

TITLE: API Reference: List MCP Servers Endpoint
DESCRIPTION: Comprehensive API documentation for the GET /v1/convai/mcp-servers endpoint, detailing request headers, successful response structure, and error codes.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/mcp/list

LANGUAGE: APIDOC
CODE:
```
Endpoint: GET /v1/convai/mcp-servers
Host: https://api.elevenlabs.io

Description: Retrieve all MCP server configurations available in the workspace.

Headers:
  xi-api-key: string (Required)
    Description: Your ElevenLabs API key.

Response (200 OK):
  Description: Successful Response
  Schema:
    mcp_servers: array of objects
      Description: A list of MCP server configurations.
      Properties:
        id: string
          Description: Unique identifier for the MCP server.
        config: object
          Description: Configuration details for the MCP server.
          Properties:
            url: string
              Description: The URL of the MCP server.
            name: string
              Description: The name of the MCP server.
            approval_policy: string
              Description: Policy for approving tools (e.g., "auto_approve_all").
            tool_approval_hashes: array of objects
              Description: List of tool approval hashes.
              Properties:
                tool_name: string
                  Description: Name of the tool.
                tool_hash: string
                  Description: Hash of the tool.
                approval_policy: string
                  Description: Approval policy for the specific tool (e.g., "auto_approved").
            transport: string
              Description: Transport protocol (e.g., "SSE").
            secret_token: object
              Description: Secret token details.
              Properties:
                secret_id: string
                  Description: ID of the secret.
            request_headers: object
              Description: Custom request headers.
            description: string
              Description: Description of the MCP server.
        metadata: object
          Description: Metadata about the MCP server.
          Properties:
            created_at: number
              Description: Timestamp of creation.
            owner_user_id: string
              Description: User ID of the owner.
        access_info: object
          Description: Access information for the current user.
          Properties:
            is_creator: boolean
              Description: True if the current user is the creator.
            creator_name: string
              Description: Name of the creator.
            creator_email: string
              Description: Email of the creator.
            role: string
              Description: Role of the current user (e.g., "admin").
        dependent_agents: array of objects
          Description: List of dependent agents.
          Properties:
            type: string
              Description: Type of the dependent agent (e.g., "unknown").

Errors:
  422 Unprocessable Entity Error
    Description: The request was well-formed but was unable to be followed due to semantic errors.
```

----------------------------------------

TITLE: API Reference for Create Pronunciation Dictionaries Endpoint
DESCRIPTION: Detailed API documentation for the POST /v1/studio/projects/:project_id/pronunciation-dictionaries endpoint. It outlines the path parameters, request headers, request body structure including `pronunciation_dictionary_locators` and `invalidate_affected_text`, and the successful response format. It also mentions error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/create-pronunciation-dictionaries

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/studio/projects/:project_id/pronunciation-dictionaries
Description: Create a set of pronunciation dictionaries acting on a project. This will automatically mark text within this project as requiring reconverting where the new dictionary would apply or the old one no longer does.

Path Parameters:
  project_id:
    Type: string
    Required: true
    Description: The ID of the project to be used. You can use the List projects endpoint to list all the available projects.

Headers:
  xi-api-key:
    Type: string
    Required: true
  Content-Type:
    Type: string
    Value: application/json

Request Body:
  Type: object
  Properties:
    pronunciation_dictionary_locators:
      Type: list of objects
      Required: true
      Description: A list of pronunciation dictionary locators (pronunciation_dictionary_id, version_id) encoded as a list of JSON strings for pronunciation dictionaries to be applied to the text. A list of json encoded strings is required as adding projects may occur through formData as opposed to jsonBody. To specify multiple dictionaries use multiple —form lines in your curl, such as —form ‘pronunciation_dictionary_locators=”{“pronunciation_dictionary_id”:“Vmd4Zor6fplcA7WrINey”,“version_id”:“hRPaxjlTdR7wFMhV4w0b”}”’ —form ‘pronunciation_dictionary_locators=”{“pronunciation_dictionary_id”:“JzWtcGQMJ6bnlWwyMo7e”,“version_id”:“lbmwxiLu4q6txYxgdZqn”}”’. Note that multiple dictionaries are not currently supported by our UI which will only show the first.
      Object Structure:
        pronunciation_dictionary_id:
          Type: string
        version_id:
          Type: string
    invalidate_affected_text:
      Type: boolean
      Optional: true
      Default: true
      Description: This will automatically mark text in this project for reconversion when the new dictionary applies or the old one no longer does.

Responses:
  200 Successful:
    Type: object
    Properties:
      status:
        Type: string
        Description: The status of the create pronunciation dictionary request. If the request was successful, the status will be 'ok'. Otherwise an error message with status 500 will be returned.
    Example:
      {
        "status": "ok"
      }
  422 Unprocessable Entity Error:
    Description: Indicates that the request could not be processed due to semantic errors.
```

----------------------------------------

TITLE: Added API Endpoints
DESCRIPTION: New API endpoints introduced for various functionalities including bulk user invitations, programmatic podcast generation, knowledge base management, and project chapter updates.

SOURCE: https://elevenlabs.io/docs/changelog/2025/2/4

LANGUAGE: APIDOC
CODE:
```
POST /v1/workspace/invites/add-bulk
  Description: Enable inviting multiple users simultaneously.
POST /v1/projects/podcast/create
  Description: Programmatic podcast generation through GenFM.
/v1/convai/knowledge-base/:documentation_id
  Description: CRUD operations for Conversational AI knowledge bases.
PATCH /v1/projects/:project_id/chapters/:chapter_id
  Description: Update project chapter content and metadata.
```

----------------------------------------

TITLE: API Reference: List Pronunciation Dictionaries Endpoint
DESCRIPTION: This section details the API endpoint for retrieving a list of pronunciation dictionaries. It specifies the HTTP method, URL, required authentication header, and optional query parameters for pagination and sorting. It also outlines the structure of the successful response and potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/pronunciation-dictionary/get-all

LANGUAGE: APIDOC
CODE:
```
GET /v1/pronunciation-dictionaries
  Description: Get a list of the pronunciation dictionaries you have access to and their metadata.

  Headers:
    xi-api-key: string (Required)

  Query parameters:
    cursor: string or null (Optional)
      Description: Used for fetching next page. Cursor is returned in the response.
    page_size: integer (Optional, >=1, <=100, Defaults to 30)
      Description: How many pronunciation dictionaries to return at maximum.
    sort: enum or null (Optional, Defaults to 'creation_time_unix')
      Allowed values: 'creation_time_unix', 'name'
      Description: Which field to sort by.
    sort_direction: string or null (Optional, Defaults to 'DESCENDING')
      Description: Which direction to sort the voices in. 'ascending' or 'descending'.

  Response (200 OK):
    pronunciation_dictionaries: list of objects
      Description: A list of pronunciation dictionaries and their metadata.
      Properties:
        id: string
        latest_version_id: string
        latest_version_rules_num: integer
        name: string
        permission_on_resource: string
        created_by: string
        creation_time_unix: integer
        description: string
    has_more: boolean
      Description: Whether there are more pronunciation dictionaries to fetch.
    next_cursor: string or null
      Description: The next cursor to use for pagination.

  Errors:
    422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference for Listing Conversational AI Agents
DESCRIPTION: This section provides comprehensive API documentation for the `GET /v1/convai/agents` endpoint. It details the required headers, optional query parameters for pagination and searching, the structure of the successful response, and potential error codes. The response includes a list of agent objects with their metadata.

SOURCE: https://elevenlabs.io/docs/api-reference/agents/list

LANGUAGE: APIDOC
CODE:
```
GET https://api.elevenlabs.io/v1/convai/agents

Headers:
  xi-api-key: string (Required)

Query parameters:
  cursor: string or null (Optional)
    Description: Used for fetching next page. Cursor is returned in the response.
  page_size: integer (Optional)
    Description: How many Agents to return at maximum. Can not exceed 100, defaults to 30.
    Constraints: >=1, <=100
    Default: 30
  search: string or null (Optional)
    Description: Search by agents name.

Response (200 Retrieved):
  agents: list of objects
    Description: A list of agents and their metadata
    Properties:
      agent_id: string
      name: string
      tags: list of strings
      created_at_unix_secs: integer
      access_info: object
        is_creator: boolean
        creator_name: string
        creator_email: string
        role: string
  has_more: boolean
    Description: Whether there are more agents to paginate through
  next_cursor: string or null
    Description: The next cursor to paginate through the agents

Example Response:
{
  "agents": [
    {
      "agent_id": "J3Pbu5gP6NNKBscdCdwB",
      "name": "My Agent",
      "tags": [
        "Customer Support",
        "Technical Help",
        "Eleven"
      ],
      "created_at_unix_secs": 1716153600,
      "access_info": {
        "is_creator": true,
        "creator_name": "John Doe",
        "creator_email": "john@example.com",
        "role": "admin"
      }
    }
  ],
  "has_more": false,
  "next_cursor": "123"
}

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference for Get Similar Voices Endpoint
DESCRIPTION: This section provides comprehensive API documentation for the 'Get similar voices' endpoint. It details the HTTP method, URL path, required path parameters (dubbing_id, speaker_id), necessary headers (xi-api-key), and the structure of the successful response, including properties of the voice objects.

SOURCE: https://elevenlabs.io/docs/api-reference/dubbing/resources/get-similar-voices

LANGUAGE: APIDOC
CODE:
```
Method: GET
Endpoint: /v1/dubbing/resource/:dubbing_id/speaker/:speaker_id/similar-voices
Description: Fetch the top 10 similar voices to a speaker, including the voice IDs, names, descriptions, and, where possible, a sample audio recording.

Path Parameters:
  dubbing_id (string, Required): ID of the dubbing project.
  speaker_id (string, Required): ID of the speaker.

Headers:
  xi-api-key (string, Required): API key for authentication.

Responses:
  200 OK (Successful Response):
    Schema:
      voices (array of objects):
        Properties:
          voice_id (string)
          name (string)
          category (string)
          description (string)
          preview_url (string)
  422 (Unprocessable Entity Error)
```

----------------------------------------

TITLE: ElevenLabs TypeScript Client: List Studio Project Chapters
DESCRIPTION: This TypeScript code demonstrates how to programmatically list chapters for an ElevenLabs Studio project using the official @elevenlabs/elevenlabs-js client library. It shows the necessary imports, client initialization with an API key, and the method call with a sample project ID.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/get-chapters

LANGUAGE: TypeScript
CODE:
```
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient({ apiKey: "YOUR_API_KEY" });
await client.studio.projects.chapters.list("21m00Tcm4TlvDq8ikWAM");
```

----------------------------------------

TITLE: ElevenLabs API Structure and Endpoint Categories
DESCRIPTION: This section outlines the main categories and endpoints available in the ElevenLabs API. It covers core API references, specific endpoints for various functionalities like Text to Speech and Speech to Text, administrative functions, conversational AI components, and legacy features, providing a structured view of the API's offerings.

SOURCE: https://elevenlabs.io/docs/api-reference/legacy/voices/create-voice-from-preview

LANGUAGE: APIDOC
CODE:
```
API REFERENCE:
  - Introduction
  - Authentication
  - Streaming
ENDPOINTS:
  - Text to Speech
  - Speech to Text
  - Text to Dialogue
  - Voice Changer
  - Sound Effects
  - Audio Isolation
  - Text to Voice
  - Dubbing
  - Audio Native
  - Voices
  - Forced Alignment
ADMINISTRATION:
  - History
  - models
  - Studio
  - Pronunciation Dictionaries
  - samples
  - usage
  - user
  - Voice Library
  - Workspace
  - Webhooks
CONVERSATIONAL AI:
  - Agents
  - Conversations
  - Tools
  - Knowledge Base
  - Phone Numbers
  - Widget
  - Workspace
  - SIP Trunk
  - Twilio
  - Batch Calling
  - LLM Usage
  - MCP
LEGACY:
  - Voices
  - Knowledge Base
```

----------------------------------------

TITLE: API Reference: Create Voice Endpoint
DESCRIPTION: Detailed specification for the ElevenLabs API endpoint to create a new voice. This includes the structure of the request body, expected data types, constraints, default values for optional parameters, the format of a successful response, and potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/text-to-voice/design

LANGUAGE: APIDOC
CODE:
```
Endpoint: Create a Voice

Request:
  Method: POST
  Body:
    voice_description: string
      Required
      Constraints: >=20 characters, <=1000 characters
      Description: Description to use for the created voice.
    model_id: enum
      Optional
      Default: eleven_multilingual_ttv_v2
      Allowed values: eleven_multilingual_ttv_v2, eleven_ttv_v3
      Description: Model to use for the voice generation.
    text: string or null
      Optional
      Constraints: >=100 characters, <=1000 characters
      Description: Text to generate, text length has to be between 100 and 1000.
    auto_generate_text: boolean
      Optional
      Default: false
      Description: Whether to automatically generate a text suitable for the voice description.
    loudness: double
      Optional
      Default: 0.5
      Constraints: >=-1, <=1
      Description: Controls the volume level of the generated voice. -1 is quietest, 1 is loudest, 0 corresponds to roughly -24 LUFS.
    seed: integer or null
      Optional
      Constraints: >=0, <=2147483647
      Description: Random number that controls the voice generation. Same seed with same inputs produces same voice.
    guidance_scale: double
      Optional
      Default: 5
      Constraints: >=0, <=100
      Description: Controls how closely the AI follows the prompt. Lower numbers give the AI more freedom to be creative, while higher numbers force it to stick more to the prompt. High numbers can cause voice to sound artificial or robotic. We recommend to use longer, more detailed prompts at lower Guidance Scale.
    quality: double or null
      Optional
      Constraints: >=-1, <=1
      Description: Higher quality results in better voice output but less variety.
    reference_audio_base64: string or null
      Optional
      Description: Reference audio to use for the voice generation. The audio should be base64 encoded. Only supported when using the eleven_ttv_v3 model.
    prompt_strength: double or null
      Optional
      Constraints: >=0, <=1
      Description: Controls the balance of prompt versus reference audio when generating voice samples. 0 means almost no prompt influence, 1 means almost no reference audio influence. Only supported when using the eleven_ttv_v3 model and providing reference audio.

Response:
  Successful Response (200 OK):
    previews: list of objects
      Description: The previews of the generated voices.
      Properties:
        text: string
          Description: The text used to preview the voices.

Errors:
  422 Unprocessable Entity Error
```

----------------------------------------

TITLE: Get Resource API Endpoint Definition
DESCRIPTION: Defines the HTTP method and URL paths for retrieving a resource by its ID from the ElevenLabs workspace API. It specifies both the full API URL and the relative path.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/resources/get

LANGUAGE: APIDOC
CODE:
```
GET
https://api.elevenlabs.io/v1/workspace/resources/:resource_id

GET
/v1/workspace/resources/:resource_id
```

----------------------------------------

TITLE: ElevenLabs Twilio Outbound Call API Reference
DESCRIPTION: Comprehensive API documentation for initiating an outbound call via Twilio using the ElevenLabs conversational AI service. This includes the endpoint definition, required request headers and body parameters, the structure of a successful response, and potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/twilio/outbound-call

LANGUAGE: APIDOC
CODE:
```
Endpoint:
POST https://api.elevenlabs.io/v1/convai/twilio/outbound-call

Description: Handle an outbound call via Twilio
```

LANGUAGE: APIDOC
CODE:
```
Request Headers:
  xi-api-key: string (Required)

Request Body:
  This endpoint expects an object.
  agent_id: string (Required)
  agent_phone_number_id: string (Required)
  to_number: string (Required)
  conversation_initiation_client_data: object or null (Optional)
```

LANGUAGE: APIDOC
CODE:
```
Successful Response Example (200 OK):
{
  "success": true,
  "message": "foo",
  "conversation_id": "foo",
  "callSid": "foo"
}

Response Body Schema:
  success: boolean
  message: string
  conversation_id: string or null
  callSid: string or null
```

LANGUAGE: APIDOC
CODE:
```
Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Updated API Endpoint: Create Studio Pronunciation Dictionaries
DESCRIPTION: The `Create pronunciation dictionaries` endpoint has modified the `pronunciation_dictionary_locators` property and now accepts null values for string properties, offering more flexibility in dictionary creation.

SOURCE: https://elevenlabs.io/docs/changelog/2025/3/24

LANGUAGE: APIDOC
CODE:
```
API Endpoint: /docs/api-reference/studio/create-pronunciation-dictionaries
Changes:
- Modified property: `pronunciation_dictionary_locators`
- String properties now accept null values
```

----------------------------------------

TITLE: API Reference: Update Convai Workspace Settings
DESCRIPTION: Comprehensive API documentation for the PATCH /v1/convai/settings endpoint, used to modify conversational AI settings. This includes the HTTP method, endpoint path, required headers, and detailed schemas for both the request body and the successful response, along with potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/update

LANGUAGE: APIDOC
CODE:
```
Endpoint: PATCH /v1/convai/settings

Description: Update Convai settings for the workspace

Headers:
  xi-api-key: string (Required)

Request Body:
  conversation_initiation_client_data_webhook: object or null (Optional)
    url: string
    request_headers: object
  webhooks: object (Optional)
    post_call_webhook_id: string
  can_use_mcp_servers: boolean (Optional, Defaults to false)
    Description: Whether the workspace can use MCP servers
  rag_retention_period_days: integer (Optional, <=30, Defaults to 10)
    Description: RAG retention period in days

Response Body (200 OK):
  conversation_initiation_client_data_webhook: object or null
    url: string
    request_headers: object
  webhooks: object or null
    post_call_webhook_id: string
  can_use_mcp_servers: boolean or null (Defaults to false)
    Description: Whether the workspace can use MCP servers
  rag_retention_period_days: integer or null (<=30, Defaults to 10)

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference: Create Phone Number Endpoint
DESCRIPTION: Detailed API documentation for the POST /v1/convai/phone-numbers/create endpoint. This endpoint allows importing phone numbers from provider configurations like Twilio or SIP trunks. It specifies the required headers, the structure of the request body (which can be either a Twilio or SIP Trunk request object), and the successful response format.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/phone-numbers/create

LANGUAGE: APIDOC
CODE:
```
POST /v1/convai/phone-numbers/create

Description: Import Phone Number from provider configuration (Twilio or SIP trunk)

Headers:
  xi-api-key: string (Required)

Request Body:
  Expected Type: object (Required)
  Options:
    - CreateTwilioPhoneNumberRequest: object (Required, 5 properties)
    - CreateSIPTrunkPhoneNumberRequest: object (Required, 10 properties)

Response (200 Successful):
  Body:
    phone_number_id: string (Phone entity ID)
  Example:
    {
      "phone_number_id": "foo"
    }
```

----------------------------------------

TITLE: API Reference: Get Character Usage Metrics Endpoint
DESCRIPTION: This section provides comprehensive API documentation for the `/v1/usage/character-stats` endpoint. It details the HTTP method (GET), the full URL, required headers, query parameters with their types and descriptions, and the structure of a successful JSON response. It also lists potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/usage/get

LANGUAGE: APIDOC
CODE:
```
Endpoint: GET https://api.elevenlabs.io/v1/usage/character-stats
Description: Returns the usage metrics for the current user or the entire workspace they are part of. The response provides a time axis based on the specified aggregation interval (default: day), with usage values for each interval along that axis. Usage is broken down by the selected breakdown type. For example, breakdown type “voice” will return the usage of each voice for each interval along the time axis.

Headers:
  xi-api-key: string (Required)

Query Parameters:
  start_unix: integer (Required)
    Description: UTC Unix timestamp for the start of the usage window, in milliseconds. To include the first day of the window, the timestamp should be at 00:00:00 of that day.
  end_unix: integer (Required)
    Description: UTC Unix timestamp for the end of the usage window, in milliseconds. To include the last day of the window, the timestamp should be at 23:59:59 of that day.
  include_workspace_metrics: boolean (Optional, Defaults to false)
    Description: Whether or not to include the statistics of the entire workspace.
  breakdown_type: enum (Optional)
    Description: How to break down the information. Cannot be “user” if include_workspace_metrics is False.
  aggregation_interval: enum (Optional)
    Description: How to aggregate usage data over time. Allowed values: "hour", "day", "week", "month", "cumulative".
  metric: enum (Optional)
    Description: Which metric to aggregate.

Response (200 Retrieved):
  Description: Successful Response
  Schema:
    time: list of integers
      Description: The time axis with unix timestamps for each day.
    usage: map from strings to lists of doubles
      Description: The usage of each breakdown type along the time axis.
  Example:
    {
      "time": [
        1738252091000,
        1739404800000
      ],
      "usage": {
        "All": [
          49,
          1053
        ]
      }
    }

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs Get User API Endpoint Reference
DESCRIPTION: This section documents the `GET /v1/user` API endpoint. It provides details on the HTTP method, the full API path, and required headers, specifically the `xi-api-key` for authentication. This endpoint is used to retrieve comprehensive information about the authenticated user's account.

SOURCE: https://elevenlabs.io/docs/api-reference/user/get

LANGUAGE: APIDOC
CODE:
```
GET
https://api.elevenlabs.io/v1/user

Headers:
  xi-api-key: string (Required)
```

----------------------------------------

TITLE: API Reference: Update Dubbing Segment Endpoint
DESCRIPTION: This section provides the comprehensive API documentation for the 'Update a segment' endpoint. It details the HTTP method (PATCH), the full URL path, required path parameters, necessary headers, optional fields for the request body, and the structure of a successful response, including potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/dubbing/resources/update-segment

LANGUAGE: APIDOC
CODE:
```
Endpoint: Update a segment
Method: PATCH
URL: https://api.elevenlabs.io/v1/dubbing/resource/:dubbing_id/segment/:segment_id/:language

Description: Modifies a single segment with new text and/or start/end times. Will update the values for only a specific language of a segment. Does not automatically regenerate the dub.

Path Parameters:
  dubbing_id: string (Required) - ID of the dubbing project.
  segment_id: string (Required) - ID of the segment.
  language: string (Required) - ID of the language.

Headers:
  xi-api-key: string (Required)

Request Body (Object):
  start_time: double or null (Optional)
  end_time: double or null (Optional)
  text: string or null (Optional)

Response (200 OK):
  version: integer

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference: Get Agent Share Link Endpoint
DESCRIPTION: Detailed API documentation for the `GET /v1/convai/agents/:agent_id/link` endpoint. This endpoint allows retrieval of the current share link for a Conversational AI agent, including required parameters, authentication headers, and the expected successful response structure.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/agents/get-link

LANGUAGE: APIDOC
CODE:
```
GET /v1/convai/agents/:agent_id/link

Description: Get the current link used to share the agent with others

Path Parameters:
  agent_id: string (Required)
    Description: The id of an agent. This is returned on agent creation.

Headers:
  xi-api-key: string (Required)

Responses:
  200 Retrieved:
    Description: Successful Response
    Properties:
      agent_id: string
        Description: The ID of the agent
      token: object or null
        Description: The token data for the agent
    Example:
      {
        "agent_id": "J3Pbu5gP6NNKBscdCdwB"
      }
  422:
    Description: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference: Delete Phone Number Endpoint
DESCRIPTION: This section provides the API specification for deleting a phone number from the ElevenLabs Conversational AI platform. It details the HTTP method, endpoint path, required path parameters, headers, and possible responses, including successful deletion and validation errors.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/phone-numbers/delete

LANGUAGE: APIDOC
CODE:
```
DELETE /v1/convai/phone-numbers/:phone_number_id

Description: Delete Phone Number by ID

Path parameters:
  phone_number_id: string (Required)
    Description: The id of an agent. This is returned on agent creation.

Headers:
  xi-api-key: string (Required)

Response:
  Successful Response

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Endpoint: List Workspace Batch Calling Jobs
DESCRIPTION: Defines the HTTP GET endpoint for retrieving all batch calling jobs associated with the current workspace. This is the base URL for the API call.

SOURCE: https://elevenlabs.io/docs/api-reference/batch-calling/list

LANGUAGE: APIDOC
CODE:
```
GET
https://api.elevenlabs.io/v1/convai/batch-calling/workspace
```

----------------------------------------

TITLE: API Reference: Get Document Chunk from Knowledge Base
DESCRIPTION: This API documentation describes the GET endpoint for retrieving a specific document chunk from the ElevenLabs conversational AI knowledge base. It details the required path parameters, headers for authentication, and the structure of a successful response.

SOURCE: https://elevenlabs.io/docs/api-reference/knowledge-base/get-knowledge-base-document-part-by-id

LANGUAGE: APIDOC
CODE:
```
Method: GET
Path: /v1/convai/knowledge-base/:documentation_id/chunk/:chunk_id
Description: Get details about a specific documentation part used by RAG.

Path Parameters:
  documentation_id (string, Required): The id of a document from the knowledge base. This is returned on document addition.
  chunk_id (string, Required): The id of a document RAG chunk from the knowledge base.

Headers:
  xi-api-key (string, Required)

Responses:
  200 OK:
    Description: Retrieved
    Schema:
      id (string)
      name (string)
      content (string)
  422 Unprocessable Entity Error
```

----------------------------------------

TITLE: Update Chapter API Endpoint Reference
DESCRIPTION: This section provides the full API specification for the 'Update Chapter' endpoint, including the HTTP method, URL, required path parameters, headers, and the structure of the request and response bodies. It details how to modify a chapter's name or content.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/update-chapter

LANGUAGE: cURL
CODE:
```
curl -X POST https://api.elevenlabs.io/v1/studio/projects/project_id/chapters/chapter_id \
-H "xi-api-key: xi-api-key" \
-H "Content-Type: application/json" \
-d '{}'
```

LANGUAGE: JSON
CODE:
```
{
  "chapter": {
    "chapter_id": "foo",
    "name": "foo",
    "can_be_downloaded": true,
    "state": "default",
    "content": {
      "blocks": [
        {
          "block_id": "foo",
          "nodes": [
            {
              "type": "foo",
              "voice_id": "foo",
              "text": "foo"
            }
          ]
        }
      ]
    },
    "last_conversion_date_unix": 42,
    "conversion_progress": 42,
    "statistics": {
      "characters_unconverted": 42,
      "characters_converted": 42,
      "paragraphs_converted": 42,
      "paragraphs_unconverted": 42
    },
    "last_conversion_error": "foo"
  }
}
```

LANGUAGE: APIDOC
CODE:
```
Endpoint: Update Chapter
Method: POST
URL: https://api.elevenlabs.io/v1/studio/projects/:project_id/chapters/:chapter_id

Path Parameters:
  project_id (string, Required): The ID of the project to be used. You can use the [List projects](/docs/api-reference/studio/get-projects) endpoint to list all the available projects.
  chapter_id (string, Required): The ID of the chapter to be used. You can use the [List project chapters](/docs/api-reference/studio/get-chapters) endpoint to list all the available chapters.

Headers:
  xi-api-key (string, Required): Your API key for authentication.

Request Body (object, Optional):
  name (string or null, Optional): The name of the chapter, used for identification only.
  content (object or null, Optional): The chapter content to use. (Show 1 properties)

Response (200 Successful):
  chapter (object): The updated chapter object. (Show 9 properties)
    chapter_id (string): Unique identifier for the chapter.
    name (string): Name of the chapter.
    can_be_downloaded (boolean): Indicates if the chapter can be downloaded.
    state (string): Current state of the chapter (e.g., "default").
    content (object): The content of the chapter.
      blocks (array): Array of content blocks.
        block_id (string): Unique identifier for the block.
        nodes (array): Array of content nodes within the block.
          type (string): Type of the node.
          voice_id (string): Voice ID used for the node.
          text (string): Text content of the node.
    last_conversion_date_unix (integer): Unix timestamp of the last conversion.
    conversion_progress (integer): Progress of the last conversion (0-100).
    statistics (object): Conversion statistics.
      characters_unconverted (integer): Number of unconverted characters.
      characters_converted (integer): Number of converted characters.
      paragraphs_converted (integer): Number of converted paragraphs.
      paragraphs_unconverted (integer): Number of unconverted paragraphs.
    last_conversion_error (string): Last conversion error message, if any.

Errors:
  422 Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference: Get Knowledge Base Document Endpoint
DESCRIPTION: Detailed API documentation for retrieving a specific document from the ElevenLabs Conversational AI knowledge base. This endpoint provides information such as document ID, name, metadata, supported usages, access information, and URL. It outlines the HTTP method, path parameters, required headers, optional query parameters, and the expected JSON response structure.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/knowledge-base/get-document

LANGUAGE: APIDOC
CODE:
```
GET /v1/convai/knowledge-base/:documentation_id

Description: Get details about a specific documentation making up the agent's knowledge base

Path Parameters:
  documentation_id (string, Required): The id of a document from the knowledge base. This is returned on document addition.

Headers:
  xi-api-key (string, Required)

Query Parameters:
  agent_id (string, Optional)

Response (200 Retrieved):
{
  "id": "foo",
  "name": "foo",
  "metadata": {
    "created_at_unix_secs": 42,
    "last_updated_at_unix_secs": 42,
    "size_bytes": 42
  },
  "supported_usages": [
    "prompt"
  ],
  "access_info": {
    "is_creator": true,
    "creator_name": "foo",
    "creator_email": "foo",
    "role": "admin"
  },
  "extracted_inner_html": "foo",
  "type": "foo",
  "url": "foo"
}
```

----------------------------------------

TITLE: Get ElevenLabs Conversational AI Workspace Secrets
DESCRIPTION: This snippet provides both a Python code example for retrieving all workspace secrets and the corresponding API documentation, including the endpoint, required headers, and the expected JSON response structure. An API key is required for authentication to access this endpoint.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/workspace/secrets/list

LANGUAGE: Python
CODE:
```
from elevenlabs import ElevenLabs

client = ElevenLabs(
    api_key="YOUR_API_KEY",
)
client.conversational_ai.secrets.list()
```

LANGUAGE: APIDOC
CODE:
```
Endpoint: GET https://api.elevenlabs.io/v1/convai/secrets
Path: /v1/convai/secrets

Headers:
  xi-api-key: string (Required) - Your ElevenLabs API key.

Response (200 Retrieved):
  secrets: list of objects (Show 4 properties)
  Example:
    {
      "secrets": [
        {
          "type": "foo",
          "secret_id": "foo",
          "name": "foo",
          "used_by": {
            "tools": [
              {
                "type": "unknown"
              }
            ],
            "agents": [
              {
                "type": "unknown"
              }
            ],
            "others": [
              "conversation_initiation_webhook"
            ],
            "phone_numbers": [
              {
                "phone_number_id": "foo",
                "phone_number": "foo",
                "label": "foo",
                "provider": "twilio"
              }
            ]
          }
        }
      ]
    }
```

----------------------------------------

TITLE: API Endpoint Parameter and Configuration Updates
DESCRIPTION: Details specific parameter additions and configuration changes across various API domains, including updates to Conversational AI agent and tool configurations, new parameters for Dubbing project creation, and SIP Trunking phone number creation.

SOURCE: https://elevenlabs.io/docs/changelog

LANGUAGE: APIDOC
CODE:
```
Conversational AI - Agent configuration:
  Added `built_in_tools` configuration for system tools management
  Deprecated inline `tools` configuration in favor of `tool_ids` for better tool management
Conversational AI - Tool system:
  Refactored tool configuration structure to use centralized tool management
Dubbing - Create dubbing project:
  Added `csv_fps` parameter for custom frame rate control
SIP Trunking - Create SIP trunk phone number:
  Added `inbound_media_encryption` parameter for security configuration
Voice Library - Voice categories:
  Updated voice response models to include “famous” as a new voice category option
  Enhanced voice search and filtering capabilities
```

----------------------------------------

TITLE: ElevenLabs API Reference: Delete Conversational AI Secret Endpoint
DESCRIPTION: Comprehensive API documentation for the `DELETE /v1/convai/secrets/:secret_id` endpoint. This section details the HTTP method, full endpoint path, required path parameters, necessary headers for authentication, and potential error responses.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/secrets/delete

LANGUAGE: APIDOC
CODE:
```
Endpoint: DELETE /v1/convai/secrets/:secret_id

Path Parameters:
  secret_id: string (Required)

Headers:
  xi-api-key: string (Required)

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Retrieve Audio Native Project Settings API Endpoint
DESCRIPTION: Documents the GET API endpoint for retrieving player settings of a specific Audio Native project. It specifies the HTTP method, URL path, required path parameters, and headers for the request.

SOURCE: https://elevenlabs.io/docs/api-reference/audio-native/get-settings

LANGUAGE: APIDOC
CODE:
```
GET
https://api.elevenlabs.io/v1/audio-native/:project_id/settings

Path parameters:
  project_id: string (Required)
    The ID of the Studio project.

Headers:
  xi-api-key: string (Required)
```

----------------------------------------

TITLE: API Reference for Create Secret Endpoint
DESCRIPTION: This section provides a detailed API reference for the `POST /v1/convai/secrets` endpoint, used to create a new secret. It outlines the required headers, the structure of the request body (including `type`, `name`, and `value` fields), the successful response format with `type`, `secret_id`, and `name`, and potential error responses like 422 Unprocessable Entity.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/secrets/create

LANGUAGE: APIDOC
CODE:
```
POST /v1/convai/secrets

Description: Create a new secret for the workspace.

Headers:
  xi-api-key: string (Required)

Request Body:
  type: "new" (string, Required)
  name: string (Required)
  value: string (Required)

Response (200 Successful):
  type: "stored" (string)
  secret_id: string
  name: string

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference: Get Agent Widget Parameters and Response
DESCRIPTION: Detailed documentation for the 'Get widget' API endpoint, including path, header, and query parameters, along with the structure of the successful response and error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/widget/get-agent-widget

LANGUAGE: APIDOC
CODE:
```
Path parameters:
  agent_id: string (Required)
    Description: The id of an agent. This is returned on agent creation.

Headers:
  xi-api-key: string (Required)

Query parameters:
  conversation_signature: string or null (Optional)
    Description: An expiring token that enables a websocket conversation to start. These can be generated for an agent using the /v1/convai/conversation/get-signed-url endpoint

Response:
  Successful Response:
    agent_id: string
    widget_config: object (Show 38 properties)

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Get Convai Dashboard Settings API Endpoint
DESCRIPTION: Documents the HTTP GET endpoint for retrieving Convai dashboard settings, detailing the URL, required authentication header, successful response structure, and potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/dashboard/get

LANGUAGE: APIDOC
CODE:
```
GET
https://api.elevenlabs.io/v1/convai/settings/dashboard

Headers:
  xi-api-key: string (Required)

Response:
  Successful Response (200):
    charts: list of objects or null

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs API Query Parameters
DESCRIPTION: Defines the various optional and required query parameters available for ElevenLabs API requests, including data types, default values, constraints, and descriptions for their purpose.

SOURCE: https://elevenlabs.io/docs/api-reference/multi-context-text-to-speech/v-1-text-to-speech-voice-id-multi-stream-input

LANGUAGE: APIDOC
CODE:
```
authorization: string (Optional) - Your authorization bearer token.
model_id: string (Optional) - The model ID to use.
language_code: string (Optional) - The ISO 639-1 language code (for specific models).
enable_logging: boolean (Optional, Defaults to true) - Whether to enable logging of the request.
enable_ssml_parsing: boolean (Optional, Defaults to false) - Whether to enable SSML parsing.
output_format: enum (Optional) - The output audio format. (Show 18 enum values)
inactivity_timeout: integer (Optional, Defaults to 20) - Timeout for inactivity before a context is closed (seconds), can be up to 180 seconds.
sync_alignment: boolean (Optional, Defaults to false) - Whether to include timing data with every audio chunk.
auto_mode: boolean (Optional, Defaults to false) - Reduces latency by disabling chunk schedule and buffers. Recommended for full sentences/phrases.
apply_text_normalization: enum (Optional, Defaults to auto) - This parameter controls text normalization with three modes - ‘auto’, ‘on’, and ‘off’. When set to ‘auto’, the system will automatically decide whether to apply text normalization (e.g., spelling out numbers). With ‘on’, text normalization will always be applied, while with ‘off’, it will be skipped. Cannot be turned on for ‘eleven_turbo_v2_5’ or ‘eleven_flash_v2_5’ models. Defaults to ‘auto’. Allowed values: auto, on, off
seed: integer (Optional, >=0, <=4294967295) - If specified, system will best-effort sample deterministically. Integer between 0 and 4294967295.
```

----------------------------------------

TITLE: ElevenLabs API: Create Agent Endpoint Reference
DESCRIPTION: This API documentation details the 'Create agent' endpoint, allowing users to programmatically create new conversational AI agents. It specifies the HTTP POST method, the full endpoint URL, required headers like `xi-api-key`, and the structure of the request body, including `conversation_config` and optional fields. It also outlines the successful response format, which returns the `agent_id`.

SOURCE: https://elevenlabs.io/docs/api-reference/agents/create

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/convai/agents/create

Headers:
  xi-api-key: string (Required)

Request Body (object):
  conversation_config: object (Required)
    Description: Conversation configuration for an agent.
  platform_settings: object or null (Optional)
    Description: Platform settings for the agent not related to conversation orchestration.
  name: string or null (Optional)
    Description: A name to make the agent easier to find.
  tags: list of strings or null (Optional)
    Description: Tags to help classify and filter the agent.

Response (200 Successful):
  agent_id: string
    Description: ID of the created agent.
    Example: "J3Pbu5gP6NNKBscdCdwB"

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs Streaming API Documentation
DESCRIPTION: Detailed documentation for the ElevenLabs streaming API, including query parameters, send methods, and receive methods, specifying types, optionality, defaults, and descriptions for each element.

SOURCE: https://elevenlabs.io/docs/api-reference/text-to-speech/v-1-text-to-speech-voice-id-stream-input

LANGUAGE: APIDOC
CODE:
```
Query Parameters:
  authorization:
    Type: string
    Optional: true
    Description: Your authorization bearer token.
  model_id:
    Type: string
    Optional: true
    Description: The model ID to use.
  language_code:
    Type: string
    Optional: true
    Description: The ISO 639-1 language code (for specific models).
  enable_logging:
    Type: boolean
    Optional: true
    Default: true
    Description: Whether to enable logging of the request.
  enable_ssml_parsing:
    Type: boolean
    Optional: true
    Default: false
    Description: Whether to enable SSML parsing.
  output_format:
    Type: enum
    Optional: true
    Description: The output audio format (18 enum values available).
  inactivity_timeout:
    Type: integer
    Optional: true
    Default: 20
    Description: Timeout for inactivity before a context is closed (seconds), can be up to 180 seconds.
  sync_alignment:
    Type: boolean
    Optional: true
    Default: false
    Description: Whether to include timing data with every audio chunk.
  auto_mode:
    Type: boolean
    Optional: true
    Default: false
    Description: Reduces latency by disabling chunk schedule and buffers. Recommended for full sentences/phrases.
  apply_text_normalization:
    Type: enum
    Optional: true
    Default: auto
    Description: This parameter controls text normalization with three modes - ‘auto’, ‘on’, and ‘off’. When set to ‘auto’, the system will automatically decide whether to apply text normalization (e.g., spelling out numbers). With ‘on’, text normalization will always be applied, while with ‘off’, it will be skipped. Cannot be turned on for ‘eleven_turbo_v2_5’ or ‘eleven_flash_v2_5’ models.
    Allowed Values: auto, on, off
  seed:
    Type: integer
    Optional: true
    Range: '>=0, <=4294967295'
    Description: If specified, system will best-effort sample deterministically. Integer between 0 and 4294967295.

Send Methods:
  initializeConnection:
    Type: object
    Required: true
    Description: (Show 6 properties)
  sendText:
    Type: object
    Required: true
    Description: (Show 5 properties)
  closeConnection:
    Type: object
    Required: true
    Description: (Show 1 properties)

Receive Methods:
  audioOutput:
    Type: object
    Required: true
    Description: (Show 3 properties)
  finalOutput:
    Type: object
    Required: true
    Description: (Show 1 properties)
```

----------------------------------------

TITLE: Retrieve Dubbing Project Metadata with cURL
DESCRIPTION: This cURL command demonstrates how to make a GET request to the ElevenLabs API to retrieve metadata for a specific dubbing project using its ID and an API key. It requires a valid `dubbing_id` and `xi-api-key` for successful authentication and retrieval.

SOURCE: https://elevenlabs.io/docs/api-reference/dubbing/get

LANGUAGE: cURL
CODE:
```
curl https://api.elevenlabs.io/v1/dubbing/dubbing_id \
-H "xi-api-key: xi-api-key"
```

----------------------------------------

TITLE: Update Secret in ElevenLabs Conversational AI Workspace
DESCRIPTION: This section provides the necessary code and API specifications to update an existing secret. It includes a Python SDK example for programmatic updates and a detailed API reference for direct HTTP requests, specifying path parameters, headers, request body, and response format.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/secrets/update-secret

LANGUAGE: Python
CODE:
```
from elevenlabs import ElevenLabs

client = ElevenLabs(
    api_key="YOUR_API_KEY",
)
client.conversational_ai.update_secret(
    secret_id="secret_id",
    name="name",
    value="value",
)
```

LANGUAGE: APIDOC
CODE:
```
PATCH /v1/convai/secrets/:secret_id

Update an existing secret for the workspace

Path parameters:
  secret_id: string (Required)

Headers:
  xi-api-key: string (Required)

Request Body:
  type: "update" (Required)
  name: string (Required)
  value: string (Required)

Response (200 Updated):
  type: "stored"
  secret_id: string
  name: string

Errors:
  422: Unprocessable Entity Error
```

LANGUAGE: JSON
CODE:
```
{
  "type": "foo",
  "secret_id": "foo",
  "name": "foo"
}
```

----------------------------------------

TITLE: Updated API Endpoint: Get Studio Project
DESCRIPTION: The `Get project` endpoint now includes `version_rules_num` in the project metadata, providing additional versioning information.

SOURCE: https://elevenlabs.io/docs/changelog/2025/3/24

LANGUAGE: APIDOC
CODE:
```
API Endpoint: /docs/api-reference/studio/get-project
Changes:
- Added to project metadata: `version_rules_num`
```

----------------------------------------

TITLE: ElevenLabs API: Edit Voice Endpoint Reference
DESCRIPTION: This section provides comprehensive API documentation for the 'Edit voice' endpoint. It details the POST request method, URL structure, required path parameters, headers, and the multipart form data expected in the request body. It also outlines the successful response format and potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/voices/update

LANGUAGE: APIDOC
CODE:
```
Endpoint: Edit voice
Method: POST
URL: https://api.elevenlabs.io/v1/voices/:voice_id/edit

Path Parameters:
  voice_id (string, Required): ID of the voice to be used. You can use the Get voices endpoint to list all available voices.

Headers:
  xi-api-key (string, Required)

Request Body (multipart/form-data):
  name (string, Required): The name that identifies this voice. This will be displayed in the dropdown of the website.
  files (files, Optional): Audio files to add to the voice.
  remove_background_noise (boolean, Optional, Defaults to `false`): If set will remove background noise for voice samples using our audio isolation model. If the samples do not include background noise, it can make the quality worse.
  description (string or null, Optional): A description of the voice.
  labels (string or null, Optional): Serialized labels dictionary for the voice.

Response (200 Successful):
  status (string): The status of the voice edit request. If the request was successful, the status will be 'ok'. Otherwise an error message with status 500 will be returned.
  Example:
    {
      "status": "ok"
    }

Errors:
  422 Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs Create Agent API Reference
DESCRIPTION: Detailed API documentation for the POST /v1/convai/agents/create endpoint. It specifies the endpoint URL, required headers, the structure of the request body including conversation and platform settings, and the successful response format containing the agent ID.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/agents/create

LANGUAGE: APIDOC
CODE:
```
Endpoint:
  POST /v1/convai/agents/create

Headers:
  xi-api-key: string (Required)

Request Body:
  conversation_config: object (Required)
    Description: Conversation configuration for an agent
    (Note: This object expects 6 properties, not detailed here)
  platform_settings: object or null (Optional)
    Description: Platform settings for the agent not related to conversation orchestration
    (Note: This object expects 8 properties, not detailed here)
  name: string or null (Optional)
    Description: A name to make the agent easier to find
  tags: list of strings or null (Optional)
    Description: Tags to help classify and filter the agent

Response (200 Successful):
  agent_id: string
    Description: ID of the created agent
    Example: "J3Pbu5gP6NNKBscdCdwB"
```

----------------------------------------

TITLE: API Reference: Train PVC Voice Endpoint Specification
DESCRIPTION: This section provides the full API specification for the 'Train PVC voice' endpoint. It details the HTTP method, endpoint path, required path parameters, headers, optional request body parameters, and the structure of the successful response, along with potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/voices/pvc/train

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/voices/pvc/:voice_id/train
Description: Start PVC training process for a voice.

Path Parameters:
  voice_id:
    Type: string
    Required: true
    Description: Voice ID to be used, you can use https://api.elevenlabs.io/v1/voices to list all the available voices.

Headers:
  xi-api-key:
    Type: string
    Required: true

Request Body:
  model_id:
    Type: string or null
    Optional: true
    Description: The model ID to use for the conversion.

Responses:
  200 Successful:
    Body:
      status:
        Type: string
        Description: The status of the start PVC voice training request. If the request was successful, the status will be 'ok'. Otherwise an error message with status 500 will be returned.
    Example:
      {
        "status": "ok"
      }

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Update Studio Project Creation API with JSON Content
DESCRIPTION: The API for creating Studio projects has been updated to support JSON-based project setup. A new `from_content_json` parameter allows projects to be initialized directly from a JSON structure, streamlining the creation process.

SOURCE: https://elevenlabs.io/docs/changelog

LANGUAGE: APIDOC
CODE:
```
Endpoint: /docs/api-reference/studio/add-project#request.body.from_content_json.from_content_json
Method: POST (implied by 'add-project')
Body Parameters:
  from_content_json: object (new) - JSON-based content for project setup.
```

----------------------------------------

TITLE: ElevenLabs API: Delete Workspace Invite Endpoint Reference
DESCRIPTION: Detailed API documentation for the DELETE /v1/workspace/invites endpoint. This endpoint is used to invalidate an existing email invitation to an ElevenLabs workspace. It outlines the HTTP method, path, required headers, request body parameters, the structure of a successful response, and potential error codes. This endpoint can only be called by workspace administrators.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/invites/delete

LANGUAGE: APIDOC
CODE:
```
Endpoint: DELETE /v1/workspace/invites
Description: Invalidates an existing email invitation. The invitation will still show up in the inbox it has been delivered to, but activating it to join the workspace won't work. This endpoint may only be called by workspace administrators.

Headers:
  xi-api-key: string (Required)

Request Body:
  email: string (Required) - The email of the customer

Response (200 OK):
  status: string - The status of the workspace invite deletion request. If the request was successful, the status will be 'ok'. Otherwise an error message with status 500 will be returned.
  Example:
    {
      "status": "ok"
    }

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Submit Batch Calling Job API and Python SDK Reference
DESCRIPTION: This snippet provides a comprehensive guide to submitting batch calling jobs via the ElevenLabs API. It includes a Python SDK example for programmatic interaction, detailed API specifications for the endpoint, including headers, request body parameters, and the structure of successful responses, along with an example JSON response.

SOURCE: https://elevenlabs.io/docs/api-reference/batch-calling/create

LANGUAGE: Python
CODE:
```
from elevenlabs import ElevenLabs, OutboundCallRecipient

client = ElevenLabs(
  api_key="YOUR_API_KEY",
)
client.conversational_ai.batch_calls.create(
  call_name="call_name",
  agent_id="agent_id",
  agent_phone_number_id="agent_phone_number_id",
  recipients=[
    OutboundCallRecipient(
      phone_number="phone_number",
    )
  ],
)
```

LANGUAGE: JSON
CODE:
```
{
  "id": "foo",
  "phone_number_id": "foo",
  "name": "foo",
  "agent_id": "foo",
  "created_at_unix": 42,
  "scheduled_time_unix": 42,
  "total_calls_dispatched": 42,
  "total_calls_scheduled": 42,
  "last_updated_at_unix": 42,
  "status": "pending",
  "agent_name": "foo",
  "phone_provider": "twilio"
}
```

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST https://api.elevenlabs.io/v1/convai/batch-calling/submit

Headers:
  xi-api-key: string (Required) - Your ElevenLabs API key.

Request Body:
  call_name: string (Required) - The name of the batch call.
  agent_id: string (Required) - The ID of the agent to use for the calls.
  agent_phone_number_id: string (Required) - The ID of the agent's phone number.
  scheduled_time_unix: integer or null (Required) - Unix timestamp for scheduling the call.
  recipients: list of objects (Required) - A list of call recipients.
    - phone_number: string - The phone number of the recipient.

Response (200 Successful):
  id: string - Unique identifier for the batch call job.
  phone_number_id: string - The ID of the phone number used.
  name: string - The name of the batch call.
  agent_id: string - The ID of the agent.
  created_at_unix: integer - Unix timestamp when the job was created.
  scheduled_time_unix: integer - Unix timestamp when the job is scheduled.
  total_calls_dispatched: integer - Number of calls dispatched.
  total_calls_scheduled: integer - Total number of calls scheduled.
  last_updated_at_unix: integer - Unix timestamp of the last update.
  status: enum - Current status of the job. Allowed values: pending, in_progress, completed, failed, cancelled
  agent_name: string - The name of the agent.
  phone_provider: enum or null - The phone provider used. Allowed values: twilio, sip_trunk

Errors:
  422 Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference for Get Pronunciation Dictionary by Version
DESCRIPTION: This section details the API endpoint for retrieving a specific version of a pronunciation dictionary. It outlines the HTTP method, URL structure, required path parameters, necessary headers, expected response format, and potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/pronunciation-dictionary/download

LANGUAGE: APIDOC
CODE:
```
GET /v1/pronunciation-dictionaries/:dictionary_id/:version_id/download

Path parameters:
  dictionary_id: string (Required) - The id of the pronunciation dictionary
  version_id: string (Required) - The id of the version of the pronunciation dictionary

Headers:
  xi-api-key: string (Required)

Response:
  The PLS file containing pronunciation dictionary rules

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Conversational AI API Configuration Updates
DESCRIPTION: Details on recent changes to the Conversational AI API, including updates to agent configuration and the tool system.

SOURCE: https://elevenlabs.io/docs/changelog/2025/6/23

LANGUAGE: APIDOC
CODE:
```
Conversational AI API Updates:
- Agent configuration:
  - Added 'built_in_tools' configuration for system tools management.
  - Deprecated inline 'tools' configuration in favor of 'tool_ids' for better tool management.
- Tool system:
  - Refactored tool configuration structure to use centralized tool management.
```

----------------------------------------

TITLE: List Workspace Webhooks using ElevenLabs Python SDK
DESCRIPTION: This snippet demonstrates how to list all webhooks configured for an ElevenLabs workspace using the official Python SDK. It initializes the `ElevenLabs` client with your API key and calls the `webhooks.list` method, allowing for optional inclusion of usage details.

SOURCE: https://elevenlabs.io/docs/api-reference/webhooks/list

LANGUAGE: Python
CODE:
```
from elevenlabs import ElevenLabs

client = ElevenLabs(
    api_key="YOUR_API_KEY",
)
client.webhooks.list(
    include_usages=False,
)
```

----------------------------------------

TITLE: API Reference: Get Audio from History Item Endpoint
DESCRIPTION: This section provides a detailed API reference for the endpoint that retrieves audio from a history item. It specifies the HTTP method, endpoint path, required path parameters, necessary headers, and expected response and error types.

SOURCE: https://elevenlabs.io/docs/api-reference/history/get-audio

LANGUAGE: APIDOC
CODE:
```
GET /v1/history/:history_item_id/audio
Path parameters:
  history_item_id:
    type: string
    required: true
    description: ID of the history item to be used. You can use the Get generated items endpoint to retrieve a list of history items.
Headers:
  xi-api-key:
    type: string
    required: true
Response:
  description: The audio file of the history item.
Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Python Client Example for ElevenLabs Forced Alignment
DESCRIPTION: This code snippet demonstrates how to use the ElevenLabs Python client to interact with the Forced Alignment API. It initializes the client with an API key and then calls the `create` method, passing the required text for alignment.

SOURCE: https://elevenlabs.io/docs/api-reference/forced-alignment

LANGUAGE: python
CODE:
```
from elevenlabs import ElevenLabs

client = ElevenLabs(
    api_key="YOUR_API_KEY",
)
client.forced_alignment.create(
    text="text",
)
```

----------------------------------------

TITLE: Eleven Labs API: Sound Effect Generation Endpoint Reference
DESCRIPTION: Comprehensive API documentation for the `/v1/sound-generation` endpoint, detailing the HTTP method, URL, required headers, optional query parameters, request body fields, expected response, and potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/text-to-sound-effects/convert

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/sound-generation
Description: Turn text into sound effects for your videos, voice-overs or video games.

Headers:
  xi-api-key: string (Required)
    Description: Your API key.

Query Parameters:
  output_format: enum (Optional) - Defaults to `mp3_44100_128`.
    Description: Output format of the generated audio. Formatted as codec_sample_rate_bitrate. (e.g., mp3_22050_32, mp3_44100_128, pcm_44100).
    Note: MP3 with 192kbps requires Creator tier+. PCM with 44.1kHz requires Pro tier+.

Request Body (JSON object):
  text: string (Required)
    Description: The text that will get converted into a sound effect.
  duration_seconds: double or null (Optional)
    Description: The duration of the sound in seconds. Must be at least 0.5 and at most 22. Defaults to None (optimal duration guessed).
  prompt_influence: double or null (Optional) - Defaults to `0.3`.
    Description: A higher value makes generation follow the prompt more closely. Must be between 0 and 1.

Response:
  Type: MP3 file
  Description: The generated sound effect as an MP3 file.

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: List Conversations using ElevenLabs TypeScript Client
DESCRIPTION: This TypeScript code snippet demonstrates how to use the `@elevenlabs/elevenlabs-js` client library to list conversations. It initializes the client with an API key and then calls the `list()` method on the `conversationalAi.conversations` object.

SOURCE: https://elevenlabs.io/docs/api-reference/conversations/get-conversations

LANGUAGE: TypeScript
CODE:
```
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient({ apiKey: "YOUR_API_KEY" });
await client.conversationalAi.conversations.list();
```

----------------------------------------

TITLE: API Reference: Invite Multiple Workspace Users
DESCRIPTION: This section provides a detailed API reference for the `POST /v1/workspace/invites/add-bulk` endpoint. It describes the required `xi-api-key` header, the structure of the request body (including `emails` and optional `group_ids`), and the expected successful response format with a `status` field. It also notes potential error codes like 422 and the administrative permissions required to call this endpoint.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/invites/create-batch

LANGUAGE: APIDOC
CODE:
```
POST /v1/workspace/invites/add-bulk

Description: Sends email invitations to join your workspace to the provided emails. Requires all email addresses to be part of a verified domain. If the users don't have an account they will be prompted to create one. If the users accept these invites they will be added as users to your workspace and your subscription using one of your seats. This endpoint may only be called by workspace administrators.

Headers:
  xi-api-key: string (Required)

Request Body:
  Type: object
  Properties:
    emails: list of strings (Required) - The email of the customer
    group_ids: list of strings or null (Optional) - The group ids of the user

Response (200 Successful):
  Type: object
  Properties:
    status: string - The status of the workspace invite request. If the request was successful, the status will be 'ok'. Otherwise an error message with status 500 will be returned.

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference: Create IVC Voice Endpoint
DESCRIPTION: Detailed API documentation for the `/v1/voices/add` endpoint used to create Instant Voice Cloning (IVC) voices. It specifies the HTTP method, endpoint URL, required headers, request body parameters (including file uploads), and the structure of the successful response and potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/voices/ivc/create

LANGUAGE: APIDOC
CODE:
```
POST /v1/voices/add

Headers:
  xi-api-key: string (Required)

Request (multipart/form-data):
  name: string (Required)
    The name that identifies this voice. This will be displayed in the dropdown of the website.
  files: files (Required)
    A list of file paths to audio recordings intended for voice cloning.
  remove_background_noise: boolean (Optional, Defaults to false)
    If set will remove background noise for voice samples using our audio isolation model. If the samples do not include background noise, it can make the quality worse.
  description: string or null (Optional)
    A description of the voice.
  labels: string or null (Optional)
    Serialized labels dictionary for the voice.

Response (200 Successful):
  voice_id: string
    The ID of the newly created voice.
  requires_verification: boolean
    Whether the voice requires verification

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs Audio Native Project Creation API Reference
DESCRIPTION: Comprehensive API documentation for the `POST /v1/audio-native` endpoint. It details the required `xi-api-key` header, various multipart form request parameters (including types, optionality, and descriptions), and the structure of the successful 200 OK response.

SOURCE: https://elevenlabs.io/docs/api-reference/audio-native/create

LANGUAGE: APIDOC
CODE:
```
POST /v1/audio-native

Headers:
  xi-api-key: string (Required)

Request Body (multipart form):
  name: string (Required) - Project name.
  image: string or null (Optional, Deprecated) - Image URL used in the player.
  author: string or null (Optional) - Author used in the player.
  title: string or null (Optional) - Title used in the player.
  small: boolean (Optional, Defaults to `false`, Deprecated) - Whether to use small player.
  text_color: string or null (Optional) - Text color used in the player.
  background_color: string or null (Optional) - Background color used in the player.
  sessionization: integer (Optional, Defaults to `0`, Deprecated) - Minutes to persist session.
  voice_id: string or null (Optional) - Voice ID used to voice content.
  model_id: string or null (Optional) - TTS Model ID used in the player.
  file: file (Optional) - Either txt or HTML input file containing the article content.
  auto_convert: boolean (Optional, Defaults to `false`) - Whether to auto convert the project to audio.

Response (200 Successful):
  project_id: string - The ID of the created Audio Native project.
  converting: boolean - Whether the project is currently being converted.
  html_snippet: string - The HTML snippet to embed the Audio Native player.
```

----------------------------------------

TITLE: API Reference: PATCH /v1/convai/phone-numbers/:phone_number_id
DESCRIPTION: Detailed API documentation for updating an existing phone number. This PATCH endpoint requires a `phone_number_id` as a path parameter and an `xi-api-key` header. The request body can optionally include an `agent_id`.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/phone-numbers/update

LANGUAGE: APIDOC
CODE:
```
PATCH /v1/convai/phone-numbers/:phone_number_id
  Path Parameters:
    phone_number_id: string (Required)
      The ID of the phone number to update.
  Headers:
    xi-api-key: string (Required)
  Request Body:
    agent_id: string or null (Optional)
  Response:
    200 Updated
      Successful Response (object)
        OR
      GetPhoneNumberTwilioResponseModel (object)
        Show 5 properties
        OR
      GetPhoneNumberSIPTrunkResponseModel (object)
        Show 6 properties
```

----------------------------------------

TITLE: ElevenLabs API: Get Generated History Items Endpoint Reference
DESCRIPTION: Comprehensive API documentation for the `GET /v1/history` endpoint. This section details the request method, URL, required headers (`xi-api-key`), optional query parameters (`page_size`, `start_after_history_item_id`, `voice_id`, `search`, `source`), and the structure of the successful response, including properties like `history` (list of items), `has_more`, and `last_history_item_id`.

SOURCE: https://elevenlabs.io/docs/api-reference/history/list

LANGUAGE: APIDOC
CODE:
```
GET /v1/history

Headers:
  xi-api-key: string (Required)

Query Parameters:
  page_size: integer (Optional, Default: 100, Max: 1000)
    Description: How many history items to return at maximum.
  start_after_history_item_id: string or null (Optional)
    Description: After which ID to start fetching, use this parameter to paginate across a large collection of history items.
  voice_id: string or null (Optional)
    Description: ID of the voice to be filtered for. You can use the Get voices endpoint list all the available voices.
  search: string or null (Optional)
    Description: Search term used for filtering history items. If provided, source becomes required.
  source: enum or null (Optional, Allowed values: TTS, STS)
    Description: Source of the generated history item.

Response (200 Retrieved):
  history: list of objects
    Description: A list of speech history items.
  has_more: boolean
    Description: Whether there are more history items to fetch.
  last_history_item_id: string or null
    Description: The ID of the last history item.

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: TypeScript Client Example for Updating Convai Dashboard Settings
DESCRIPTION: Illustrates how to use the ElevenLabs TypeScript client to update the Convai dashboard settings. It shows client initialization with an API key and the method call for the update operation.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/dashboard/update

LANGUAGE: TypeScript
CODE:
```
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient({ apiKey: "YOUR_API_KEY" });
await client.conversationalAi.dashboard.settings.update();
```

----------------------------------------

TITLE: ElevenLabs Studio API: Create Chapter Endpoint Reference
DESCRIPTION: Comprehensive API documentation for the `POST /v1/studio/projects/:project_id/chapters` endpoint. It details the HTTP method, relative URL, required path parameters (`project_id`), required header (`xi-api-key`), the structure of the request body (including `name` and optional `from_url`), and the expected successful response schema for a newly created chapter.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/add-chapter

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/studio/projects/:project_id/chapters

Path Parameters:
  project_id: string (Required)
    Description: The ID of the Studio project.

Headers:
  xi-api-key: string (Required)

Request Body:
  Type: object
  Properties:
    name: string (Required)
      Description: The name of the chapter, used for identification only.
    from_url: string or null (Optional)
      Description: An optional URL from which we will extract content to initialize the Studio project. If this is set, ‘from_url’ and ‘from_content’ must be null. If neither ‘from_url’, ‘from_document’, ‘from_content’ are provided we will initialize the Studio project as blank.

Response (200 Successful):
  Type: object
  Properties:
    chapter: object
      Properties:
        chapter_id: string
        name: string
        can_be_downloaded: boolean
        state: string
        content: object
          Properties:
            blocks: array
              Items:
                type: object
                Properties:
                  block_id: string
                  nodes: array
                    Items:
                      type: object
                      Properties:
                        type: string
                        voice_id: string
                        text: string
        last_conversion_date_unix: number
        conversion_progress: number
        statistics: object
          Properties:
            characters_unconverted: number
            characters_converted: number
            paragraphs_converted: number
            paragraphs_unconverted: number
        last_conversion_error: string
```

----------------------------------------

TITLE: Install ElevenLabs Python SDK
DESCRIPTION: This command installs the official Python bindings for the ElevenLabs API using pip, the Python package installer. It's the first step to integrate the ElevenLabs API into a Python application.

SOURCE: https://elevenlabs.io/docs/api-reference

LANGUAGE: Python
CODE:
```
pip install elevenlabs
```

----------------------------------------

TITLE: Retrieve Convai Dashboard Settings using cURL
DESCRIPTION: Example cURL command to fetch the Convai dashboard settings from the ElevenLabs API, demonstrating the use of the `xi-api-key` header for authentication.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/dashboard/get

LANGUAGE: cURL
CODE:
```
curl https://api.elevenlabs.io/v1/convai/settings/dashboard \
-H "xi-api-key: xi-api-key"
```

----------------------------------------

TITLE: ElevenLabs Text-to-Speech WebSocket Stream Input API Reference
DESCRIPTION: This section details the WebSocket API for real-time Text-to-Speech generation, designed for scenarios where text input is streamed in chunks or word-to-audio alignment is required. It outlines the WebSocket endpoint, handshake process, and the structure of messages for publishing text and subscribing to audio output. It also highlights the API's suitability for partial text input and its limitations compared to standard HTTP requests.

SOURCE: https://elevenlabs.io/docs/api-reference/text-to-speech/v-1-text-to-speech-voice-id-stream-input

LANGUAGE: APIDOC
CODE:
```
WebSocket Endpoint:
  WSS URL: wss://api.elevenlabs.io/v1/text-to-speech/:voice_id/stream-input
  Handshake Method: GET
  Handshake Status: 101 Switching Protocols
```

LANGUAGE: APIDOC
CODE:
```
Handshake Parameters:
  Headers:
    xi-api-key: string (Required)
  Path Parameters:
    voice_id: string (Required)
      Description: The unique identifier for the voice to use in the TTS process.
```

LANGUAGE: APIDOC
CODE:
```
Publish Message Format (Initial Configuration):
  {
    "text":" ",
    "voice_settings":{
      "speed":1,
      "stability":0.5,
      "similarity_boost":0.8
    },
    "xi_api_key":"<YOUR_API_KEY>"
  }
```

LANGUAGE: APIDOC
CODE:
```
Publish Message Format (Text Input):
  {
    "text":"Hello World ",
    "try_trigger_generation":true
  }
```

LANGUAGE: APIDOC
CODE:
```
Publish Message Format (End Stream):
  {
    "text":""
  }
```

LANGUAGE: APIDOC
CODE:
```
Subscribe Message Format (Audio Output):
  {
    "audio":"Y3VyaW91cyBtaW5kcyB0aGluayBhbGlrZSA6KQ==",
    "isFinal":false,
    "normalizedAlignment":{
      "charStartTimesMs":[0,3,7,9,11,12,13,15,17,19,21],
      "charsDurationsMs":[3,4,2,2,1,1,2,2,2,2,3],
      "chars":["H","e","l","l","o"," ","w","o","r","l","d"]
    },
    "alignment":{
      "charStartTimesMs":[0,3,7,9,11,12,13,15,17,19,21],
      "charsDurationsMs":[3,4,2,2,1,1,2,2,2,2,3],
      "chars":["H","e","l","l","o"," ","w","o","r","l","d"]
    }
  }
```

----------------------------------------

TITLE: Add Language to Dubbing Resource API Endpoint
DESCRIPTION: This API endpoint facilitates adding a specified ElevenLab Turbo V2/V2.5 language code to an existing dubbing resource. It requires the dubbing project ID in the path, an API key in the headers, and the target language in the request body. The operation returns a version number upon successful creation.

SOURCE: https://elevenlabs.io/docs/api-reference/dubbing/resources/add-language

LANGUAGE: cURL
CODE:
```
curl -X POST https://api.elevenlabs.io/v1/dubbing/resource/dubbing_id/language \
-H "xi-api-key: xi-api-key" \
-H "Content-Type: application/json" \
-d '{
"language": "foo"
}'
```

LANGUAGE: APIDOC
CODE:
```
Endpoint: Add language to resource
Method: POST
URL: https://api.elevenlabs.io/v1/dubbing/resource/:dubbing_id/language

Path Parameters:
  dubbing_id: string (Required) - ID of the dubbing project.

Headers:
  xi-api-key: string (Required)

Request Body:
  Type: object
  Properties:
    language: string or null (Required) - The Target language.

Responses:
  201 Created:
    Type: object
    Properties:
      version: integer

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs Conversational AI Get Phone Number API Endpoint
DESCRIPTION: This section provides the API specification for retrieving phone number details. It outlines the HTTP method, endpoint path, required path parameters, and authentication headers.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/phone-numbers/get

LANGUAGE: APIDOC
CODE:
```
Endpoint: GET /v1/convai/phone-numbers/:phone_number_id
Description: Retrieve Phone Number details by ID

Path Parameters:
  phone_number_id:
    Type: string
    Required: true
    Description: The id of an agent. This is returned on agent creation.

Headers:
  xi-api-key:
    Type: string
    Required: true
    Description: API key for authentication.

Responses:
  200 OK:
    Description: Successful Response
    Schema:
      - GetPhoneNumberTwilioResponseModelobject (5 properties)
      - GetPhoneNumberSIPTrunkResponseModelobject (6 properties)
```

----------------------------------------

TITLE: ElevenLabs API: Invite User Endpoint Reference
DESCRIPTION: This section details the `POST /v1/workspace/invites/add` API endpoint, which allows administrators to send email invitations for users to join their ElevenLabs workspace. It outlines the required `xi-api-key` header, the request body parameters (email, optional group_ids, and workspace_permission), and the structure of a successful `200 OK` response, which includes a 'status' field. It also notes potential errors like `422 Unprocessable Entity` and conditions under which a `400` error might occur (user already in workspace).

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/invites/create

LANGUAGE: APIDOC
CODE:
```
POST /v1/workspace/invites/add

Headers:
  xi-api-key: string (Required)

Request Body (object):
  email: string (Required) - The email of the customer
  group_ids: list of strings or null (Optional) - The group ids of the user
  workspace_permission: enum or null (Optional) - The workspace permission of the user (Show 16 enum values)

Response (200 Successful):
  status: string - The status of the workspace invite request. If the request was successful, the status will be 'ok'. Otherwise an error message with status 500 will be returned.

Errors:
  422: Unprocessable Entity Error
  (Implicit 400 if user already in workspace)
```

LANGUAGE: JSON
CODE:
```
{
  "status": "ok"
}
```

----------------------------------------

TITLE: List Conversations API Endpoint and Examples
DESCRIPTION: This section provides the API documentation for retrieving a list of all conversations associated with a user's agents, along with a cURL example for making the request and an example of the expected JSON response. Authentication via an API key is required.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/conversations/get-conversations

LANGUAGE: APIDOC
CODE:
```
List conversations API Endpoint

Method: GET
Path: /v1/convai/conversations
Full URL: https://api.elevenlabs.io/v1/convai/conversations
Description: Get all conversations of agents that user owns, with an option to restrict to a specific agent.

Headers:
  xi-api-key: string (Required) - Your ElevenLabs API key.

Responses:
  200 Retrieved:
    Description: Successfully retrieved list of conversations.
    Body (application/json):
      conversations: array of objects
        agent_id: string - The ID of the agent.
        conversation_id: string - The ID of the conversation.
        start_time_unix_secs: number - Unix timestamp of when the conversation started.
        call_duration_secs: number - Duration of the call in seconds.
        message_count: number - Number of messages in the conversation.
        status: string - Current status of the conversation (e.g., "initiated").
        call_successful: string - Indicates if the call was successful (e.g., "success").
        agent_name: string - The name of the agent.
      has_more: boolean - Indicates if there are more conversations to retrieve.
      next_cursor: string - Cursor for fetching the next page of results.
```

LANGUAGE: cURL
CODE:
```
curl https://api.elevenlabs.io/v1/convai/conversations \
-H "xi-api-key: xi-api-key"
```

LANGUAGE: JSON
CODE:
```
{
"conversations": [
{
"agent_id": "foo",
"conversation_id": "foo",
"start_time_unix_secs": 42,
"call_duration_secs": 42,
"message_count": 42,
"status": "initiated",
"call_successful": "success",
"agent_name": "foo"
}
],
"has_more": true,
"next_cursor": "foo"
}
```

----------------------------------------

TITLE: ElevenLabs New API Endpoints
DESCRIPTION: Documentation for newly released API endpoints in the ElevenLabs platform, covering dubbing, conversational AI, and SIP trunking functionalities. Each entry details the HTTP method, endpoint path, and a brief description of its purpose.

SOURCE: https://elevenlabs.io/docs/changelog/2025/5/12

LANGUAGE: APIDOC
CODE:
```
PATCH /v1/dubbing/resource/{dubbing_id}/speaker/{speaker_id}
  Description: Amend the metadata associated with a speaker, such as their voice. Both voice cloning and using voices from the ElevenLabs library are supported.
```

LANGUAGE: APIDOC
CODE:
```
GET /v1/dubbing/resource/{dubbing_id}/speaker/{speaker_id}/similar-voices
  Description: Fetch the top 10 similar voices to a speaker, including IDs, names, descriptions, and sample audio.
```

LANGUAGE: APIDOC
CODE:
```
POST /v1/convai/agents/{agent_id}/simulate_conversation
  Description: Run a conversation between the agent and a simulated user.
```

LANGUAGE: APIDOC
CODE:
```
POST /v1/convai/agents/{agent_id}/simulate_conversation/stream
  Description: Stream a simulated conversation between the agent and a simulated user.
```

LANGUAGE: APIDOC
CODE:
```
POST /v1/convai/sip-trunk/outbound-call
  Description: Initiate an outbound call using SIP trunking.
```

----------------------------------------

TITLE: Retrieve Agent Configuration API Reference
DESCRIPTION: Detailed API documentation for the endpoint used to retrieve an agent's configuration. It specifies the necessary path parameters, required request headers, and the comprehensive structure of the successful response object, including various agent-related properties.

SOURCE: https://elevenlabs.io/docs/api-reference/agents/get

LANGUAGE: APIDOC
CODE:
```
Endpoint: Retrieve config for an agent

Path parameters:
  agent_id:
    Type: string
    Required: true
    Description: The id of an agent. This is returned on agent creation.

Headers:
  xi-api-key:
    Type: string
    Required: true

Response (Successful Response):
  agent_id:
    Type: string
    Description: The ID of the agent
  name:
    Type: string
    Description: The name of the agent
  conversation_config:
    Type: object
    Description: The conversation configuration of the agent
  metadata:
    Type: object
    Description: The metadata of the agent
  platform_settings:
    Type: object or null
    Description: The platform settings of the agent
  phone_numbers:
    Type: list of objects or null
    Description: The phone numbers of the agent
  access_info:
    Type: object or null
    Description: The access information of the agent for the user
  tags:
    Type: list of strings or null
    Description: Agent tags used to categorize the agent

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: List Phone Numbers API Endpoint Definition
DESCRIPTION: Defines the HTTP GET API endpoint for retrieving a list of phone numbers configured within the ElevenLabs Conversational AI service. It specifies the full API path, required authentication headers, expected successful response models (Twilio or SIP Trunk), and potential error responses like 422 Unprocessable Entity.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/phone-numbers/list

LANGUAGE: APIDOC
CODE:
```
GET
https://api.elevenlabs.io/v1/convai/phone-numbers

### Headers
xi-api-keystringRequired

### Response
Successful Response
GetPhoneNumberTwilioResponseModelobject
Show 5 properties
OR
GetPhoneNumberSIPTrunkResponseModelobject
Show 6 properties

### Errors
422
Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs Transcription API Error Responses
DESCRIPTION: Details the possible error responses from the ElevenLabs transcription endpoint.

SOURCE: https://elevenlabs.io/docs/api-reference/speech-to-text/convert

LANGUAGE: APIDOC
CODE:
```
422: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs API: Delete Conversation Endpoint Reference
DESCRIPTION: Comprehensive API documentation for the 'Delete conversation' endpoint, detailing the HTTP method, URL path, required path parameters, necessary headers for authentication, and potential responses including error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/conversations/delete

LANGUAGE: APIDOC
CODE:
```
DELETE https://api.elevenlabs.io/v1/convai/conversations/:conversation_id

Path parameters:
  conversation_id: string (Required)
    The id of the conversation you're taking the action on.

Headers:
  xi-api-key: string (Required)

Response:
  Successful Response

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference: Update Knowledge Base Document
DESCRIPTION: Detailed API documentation for the PATCH endpoint used to update a knowledge base document. It specifies the endpoint URL, required path parameters, and headers necessary for authentication and content type.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/knowledge-base/update

LANGUAGE: APIDOC
CODE:
```
Endpoint: PATCH /v1/convai/knowledge-base/:documentation_id
Description: Update the name of a document

Path Parameters:
  documentation_id (string, Required):
    The id of a document from the knowledge base. This is returned on document addition.

Headers:
  xi-api-key (string, Required)
```

----------------------------------------

TITLE: New ElevenLabs API Endpoints
DESCRIPTION: Introduces six new API endpoints for managing conversations, simulating interactions, updating workspace secrets, and handling batch call requests. These endpoints expand the platform's programmatic capabilities.

SOURCE: https://elevenlabs.io/docs/changelog

LANGUAGE: APIDOC
CODE:
```
New Endpoints:
- Get Signed Url: /docs/conversational-ai/api-reference/conversations/get-signed-url
  Description: Get a signed URL to start a conversation with an agent that requires authorization.
- Simulate Conversation: /docs/conversational-ai/api-reference/agents/simulate-conversation
  Description: Run a conversation between an agent and a simulated user.
- Simulate Conversation (Stream): /docs/conversational-ai/api-reference/agents/simulate-conversation-stream
  Description: Run and stream a conversation simulation between an agent and a simulated user.
- Update Convai Workspace Secret: /docs/conversational-ai/api-reference/workspace/secrets/update-secret
  Description: Update an existing secret for the Convai workspace.
- Submit Batch Call Request: /docs/conversational-ai/api-reference/batch-calling/create
  Description: Submit a batch call request to schedule calls for multiple recipients.
- Get All Batch Calls for Workspace: /docs/conversational-ai/api-reference/batch-calling/list
  Description: Retrieve all batch calls for the current workspace.
```

----------------------------------------

TITLE: API Reference: Calculate Expected LLM Usage
DESCRIPTION: Detailed API documentation for the `calculate` endpoint to estimate LLM usage. It specifies the HTTP method, endpoint URL, required headers, request body parameters, and the structure of a successful response.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/llm-usage/calculate

LANGUAGE: APIDOC
CODE:
```
POST /v1/convai/llm-usage/calculate

Headers:
  xi-api-key: string (Required)

Request Body:
  prompt_length: integer (Required) - Length of the prompt in characters.
  number_of_pages: integer (Required) - Pages of content in PDF documents or URLs in the agent's knowledge base.
  rag_enabled: boolean (Required) - Whether RAG is enabled.

Response (200 Successful):
  llm_prices: list of objects
    llm: string
    price_per_minute: integer
```

----------------------------------------

TITLE: Conversational AI API Successful Response Structure
DESCRIPTION: Defines the structure of a successful response from the Conversational AI API, including various identifiers, status, and media presence flags.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/conversations/get-conversation

LANGUAGE: APIDOC
CODE:
```
Response:
  agent_id: string
  conversation_id: string
  status: enum
    Allowed values: initiated, in-progress, processing, done, failed
  transcript: list of objects (details omitted, 13 properties)
  metadata: object (details omitted, 16 properties)
  has_audio: boolean
  has_user_audio: boolean
  has_response_audio: boolean
  analysis: object or null (details omitted, 4 properties)
  conversation_initiation_client_data: object or null (details omitted, 3 properties)
```

----------------------------------------

TITLE: API Reference: Get Conversation Audio Endpoint
DESCRIPTION: Detailed API documentation for the endpoint used to retrieve the audio recording of a specific conversation. It specifies the HTTP method, URL structure, required path parameters, necessary headers for authentication, and potential error responses.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/conversations/get-audio

LANGUAGE: APIDOC
CODE:
```
GET /v1/convai/conversations/:conversation_id/audio
Description: Get the audio recording of a particular conversation

Path Parameters:
  conversation_id:
    Type: string
    Required: true
    Description: The id of the conversation you're taking the action on.

Headers:
  xi-api-key:
    Type: string
    Required: true

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Removed Conversational AI Tools Endpoints
DESCRIPTION: A temporary removal of several ElevenLabs Conversational AI tools endpoints, including operations for getting, listing, updating, creating, and deleting tools. These endpoints are currently unavailable.

SOURCE: https://elevenlabs.io/docs/changelog/2025/3/10

LANGUAGE: APIDOC
CODE:
```
Removed Conversational AI Tools Endpoints:
  - Get tool
  - List tools
  - Update tool
  - Create tool
  - Delete tool
Status: Temporarily removed
```

----------------------------------------

TITLE: ElevenLabs API: Design a Voice Endpoint and SDK Usage
DESCRIPTION: This section provides comprehensive documentation for the ElevenLabs 'Design a Voice' API endpoint, including its HTTP method, full URL, request parameters, and expected response format. It also includes a practical example demonstrating how to interact with this endpoint using the ElevenLabs TypeScript SDK.

SOURCE: https://elevenlabs.io/docs/api-reference/text-to-voice/design

LANGUAGE: TypeScript
CODE:
```
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient({ apiKey: "YOUR_API_KEY" });
await client.textToVoice.design({
  voiceDescription: "A sassy squeaky mouse"
});
```

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/text-to-voice/design
Full URL: https://api.elevenlabs.io/v1/text-to-voice/design

Description: Design a voice via a prompt. This method returns a list of voice previews. Each preview has a generated_voice_id and a sample of the voice as base64 encoded mp3 audio. To create a voice use the generated_voice_id of the preferred preview with the /v1/text-to-voice endpoint.

Headers:
  xi-api-key: string (Required)

Query Parameters:
  output_format: enum (Optional)
    Defaults to `mp3_44100_192`
    Description: Output format of the generated audio. Formatted as codec_sample_rate_bitrate. So an mp3 with 22.05kHz sample rate at 32kbs is represented as mp3_22050_32. MP3 with 192kbps bitrate requires you to be subscribed to Creator tier or above. PCM with 44.1kHz sample rate requires you to be subscribed to Pro tier or above. Note that the μ-law format (sometimes written mu-law, often approximated as u-law) is commonly used for Twilio audio inputs.
    (Show 19 enum values - not provided in source)
```

LANGUAGE: JSON
CODE:
```
{
  "previews": [
    {
      "audio_base_64": "foo",
      "generated_voice_id": "foo",
      "media_type": "foo",
      "duration_secs": 42
    }
  ],
  "text": "foo"
}
```

----------------------------------------

TITLE: Eleven Labs Twilio Outbound Call API Endpoint Reference
DESCRIPTION: This section provides a detailed reference for the Eleven Labs API endpoint used to handle outbound calls via Twilio. It specifies the HTTP method, full URL, required request headers, the structure of the request body parameters, and the expected successful response schema, including potential error responses.

SOURCE: https://elevenlabs.io/docs/api-reference/conversations/outbound-call

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/convai/twilio/outbound-call
Full URL: https://api.elevenlabs.io/v1/convai/twilio/outbound-call

Description: Handle an outbound call via Twilio

Headers:
  xi-api-key: string (Required)

Request Body:
  Type: object
  Properties:
    agent_id: string (Required)
    agent_phone_number_id: string (Required)
    to_number: string (Required)
    conversation_initiation_client_data: object or null (Optional)

Response (200 Successful):
  Type: object
  Properties:
    success: boolean
    message: string
    conversation_id: string or null
    callSid: string or null

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference for Stream Archive Studio Project Audio Endpoint
DESCRIPTION: This section provides the detailed API specification for the endpoint that returns a compressed archive of a Studio project's audio. It outlines the HTTP method, URL structure, required path parameters, necessary headers, and expected response and error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/archive-snapshot

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/studio/projects/:project_id/snapshots/:project_snapshot_id/archive
Description: Returns a compressed archive of the Studio project's audio.

Path Parameters:
  project_id: string (Required)
    Description: The ID of the project to be used. You can use the [List projects] endpoint to list all the available projects.
  project_snapshot_id: string (Required)
    Description: The ID of the Studio project snapshot.

Headers:
  xi-api-key: string (Required)

Response:
  Streaming archive data

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs API: New Endpoints Added
DESCRIPTION: This section lists the newly added API endpoints, providing new functionalities for voice management, project archiving, audio native creation, and pronunciation dictionary downloads. These additions expand the capabilities available through the ElevenLabs API, enabling more comprehensive programmatic control over ElevenLabs services.

SOURCE: https://elevenlabs.io/docs/changelog/2025/3/10

LANGUAGE: APIDOC
CODE:
```
New Endpoints:
  - Add a shared voice to your collection
  - Archive a project snapshot
  - Update a project
  - Create an Audio Native enabled project
  - Get all voices
  - Download a pronunciation dictionary
  - Get Audio Native project settings
```

----------------------------------------

TITLE: API Reference: Stream Speech with Timing Endpoint
DESCRIPTION: This section provides a comprehensive API reference for the POST /v1/text-to-speech/:voice_id/stream/with-timestamps endpoint. It details the endpoint's purpose, required path parameters, necessary headers, and optional query parameters, including their data types, default values, and specific usage notes like latency optimization levels and output format options.

SOURCE: https://elevenlabs.io/docs/api-reference/text-to-speech/stream-with-timestamps

LANGUAGE: APIDOC
CODE:
```
POST /v1/text-to-speech/:voice_id/stream/with-timestamps

Converts text into speech using a voice of your choice and returns a stream of JSONs containing audio as a base64 encoded string together with information on when which character was spoken.

Path parameters:
  voice_id: string (Required)
    ID of the voice to be used. Use the Get voices endpoint list all the available voices.

Headers:
  xi-api-key: string (Required)

Query parameters:
  enable_logging: boolean (Optional, Defaults to true)
    When enable_logging is set to false zero retention mode will be used for the request. This will mean history features are unavailable for this request, including request stitching. Zero retention mode may only be used by enterprise customers.
  optimize_streaming_latency: integer or null (Optional, Deprecated)
    You can turn on latency optimizations at some cost of quality. The best possible final latency varies by model. Possible values: 0 (default mode), 1 (normal latency optimizations), 2 (strong latency optimizations), 3 (max latency optimizations), 4 (max latency optimizations, text normalizer off). Defaults to None.
  output_format: enum (Optional, Defaults to mp3_44100_128)
    Output format of the generated audio. Formatted as codec_sample_rate_bitrate. So an mp3 with 22.05kHz sample rate at 32kbs is represented as mp3_22050_32. MP3 with 192kbps bitrate requires you to be subscribed to Creator tier or above. PCM with 44.1kHz sample rate requires you to be subscribed to Pro tier or above. Note that the μ-law format (sometimes written mu-law, often approximated as u-law) is commonly used for Twilio audio inputs.
```

----------------------------------------

TITLE: Twilio Outbound Call API Documentation
DESCRIPTION: Comprehensive API documentation for the ElevenLabs Conversational AI endpoint used to initiate outbound calls via Twilio. It details the HTTP method, endpoint path, required headers, and the structure of both the request and successful response bodies.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/twilio/outbound-call

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST https://api.elevenlabs.io/v1/convai/twilio/outbound-call
Description: Handle an outbound call via Twilio

Headers:
  xi-api-key: string (Required)

Request Body:
  Type: object
  Properties:
    agent_id: string (Required)
    agent_phone_number_id: string (Required)
    to_number: string (Required)
    conversation_initiation_client_data: object or null (Optional)
      (Show 3 properties)

Response (200 Successful):
  Type: object
  Properties:
    success: boolean
    message: string
    conversation_id: string or null
    callSid: string or null
```

----------------------------------------

TITLE: Eleven Labs Studio API: List Chapter Snapshots Endpoint Definition
DESCRIPTION: Defines the Eleven Labs Studio API endpoint for listing all snapshots of a specific chapter. It includes the HTTP method, URL path, required path parameters, authentication headers, and the structure of the successful JSON response, along with potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/get-chapter-snapshots

LANGUAGE: APIDOC
CODE:
```
GET /v1/studio/projects/:project_id/chapters/:chapter_id/snapshots

Description: Gets information about all the snapshots of a chapter. Each snapshot can be downloaded as audio. Whenever a chapter is converted a snapshot will automatically be created.

Path Parameters:
  project_id (string, Required): The ID of the project to be used. You can use the [List projects](/docs/api-reference/studio/get-projects) endpoint to list all the available projects.
  chapter_id (string, Required): The ID of the chapter to be used. You can use the [List project chapters](/docs/api-reference/studio/get-chapters) endpoint to list all the available chapters.

Headers:
  xi-api-key (string, Required)

Responses:
  200 OK:
    Description: Retrieved
    Body:
      snapshots (list of objects): List of chapter snapshots.
        Properties:
          chapter_snapshot_id (string)
          project_id (string)
          chapter_id (string)
          created_at_unix (number)
          name (string)

  422 Unprocessable Entity:
    Description: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference for Deleting Conversational AI Phone Number
DESCRIPTION: This section details the API endpoint for deleting a conversational AI phone number. It specifies the HTTP method (DELETE), the full endpoint path, required path parameters like `phone_number_id`, and necessary headers such as `xi-api-key`. It also outlines the expected successful response and potential error codes like 422 Unprocessable Entity.

SOURCE: https://elevenlabs.io/docs/api-reference/phone-numbers/delete

LANGUAGE: APIDOC
CODE:
```
Endpoint: DELETE https://api.elevenlabs.io/v1/convai/phone-numbers/:phone_number_id

Path Parameters:
  phone_number_id: string (Required)
    Description: The id of an agent. This is returned on agent creation.

Headers:
  xi-api-key: string (Required)

Response:
  Successful Response

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference: Create Knowledge Base Document from Text
DESCRIPTION: Detailed API documentation for creating a knowledge base document from text, including endpoint, request headers, body parameters, and successful response structure.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/knowledge-base/create-from-text

LANGUAGE: APIDOC
CODE:
```
Endpoint:
  POST /v1/convai/knowledge-base/text

Headers:
  xi-api-key: string (Required)

Request Body:
  text: string (Required)
    Description: Text content to be added to the knowledge base.
  name: string or null (Optional)
    Constraints: >=1 character
    Description: A custom, human-readable name for the document.

Response (200 Successful):
  id: string
  name: string
```

----------------------------------------

TITLE: ElevenLabs API Receive Operations
DESCRIPTION: Outlines the types of data that can be received from the ElevenLabs API, including audio output and final output, specifying their object types and property counts.

SOURCE: https://elevenlabs.io/docs/api-reference/multi-context-text-to-speech/v-1-text-to-speech-voice-id-multi-stream-input

LANGUAGE: APIDOC
CODE:
```
audioOutputMulti: object (Required)
	- Properties: Show 4 properties
OR
finalOutputMulti: object (Required)
	- Properties: Show 2 properties
```

----------------------------------------

TITLE: ElevenLabs API: Get Dependent Agents Error Response (422)
DESCRIPTION: Describes the 422 Unprocessable Entity error response that can be returned by the 'Get Dependent Agents' API, indicating issues with the request.

SOURCE: https://elevenlabs.io/docs/api-reference/tools/get-dependent-agents

LANGUAGE: APIDOC
CODE:
```
### Errors
422
Unprocessable Entity Error
```

----------------------------------------

TITLE: Retrieve Conversation Details using cURL
DESCRIPTION: This cURL command demonstrates how to make a basic GET request to the ElevenLabs API to retrieve details for a specific conversation. It shows the base URL for the API endpoint.

SOURCE: https://elevenlabs.io/docs/api-reference/conversations/get-conversation

LANGUAGE: cURL
CODE:
```
curl https://api.elevenlabs.io
```

----------------------------------------

TITLE: Example JSON Response for Dashboard Settings
DESCRIPTION: Illustrates the expected JSON structure returned upon a successful retrieval of Convai dashboard settings, showing the 'charts' array with example entries.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/dashboard/get

LANGUAGE: JSON
CODE:
```
{
  "charts": [
    {
      "name": "foo",
      "type": "call_success"
    }
  ]
}
```

----------------------------------------

TITLE: API Reference for Get Conversational AI Settings Endpoint
DESCRIPTION: This section details the API endpoint for retrieving conversational AI settings. It specifies the HTTP method (GET), the full URL, the required `xi-api-key` header for authentication, and the structure of the successful response, including properties like `conversation_initiation_client_data_webhook`, `webhooks`, `can_use_mcp_servers`, and `rag_retention_period_days`. It also lists potential error responses.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/get

LANGUAGE: APIDOC
CODE:
```
Endpoint: GET /v1/convai/settings
Full URL: https://api.elevenlabs.io/v1/convai/settings

Headers:
  xi-api-key: string (Required)

Response (200 Retrieved):
  conversation_initiation_client_data_webhook: object or null
    (Properties: url, request_headers)
  webhooks: object or null
    (Properties: post_call_webhook_id)
  can_use_mcp_servers: boolean or null (Defaults to `false`, Whether the workspace can use MCP servers)
  rag_retention_period_days: integer or null (`<=30`, Defaults to `10`)

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Updated ElevenLabs API: Conversational AI Agent Configuration
DESCRIPTION: Documentation for enhanced agent configuration parameters, including new system tool `skip_turn` and improved RAG configuration with `max_retrieved_rag_chunks_count`.

SOURCE: https://elevenlabs.io/docs/changelog

LANGUAGE: APIDOC
CODE:
```
Agent Configuration Parameters:
  System Tools:
    skip_turn: object
      Description: Configuration for the new 'skip_turn' system tool.
  RAG Configuration:
    max_retrieved_rag_chunks_count: integer
      Description: Maximum number of chunks collected during RAG retrieval.
```

----------------------------------------

TITLE: API Reference: List Workspace Batch Calling Jobs - Parameters & Schema
DESCRIPTION: Details the required "xi-api-key" header, optional query parameters ("limit", "last_doc"), and the full schema for the successful response, including descriptions for "batch_calls", "next_doc", and "has_more". Also notes the 422 Unprocessable Entity error.

SOURCE: https://elevenlabs.io/docs/api-reference/batch-calling/list

LANGUAGE: APIDOC
CODE:
```
### Headers
xi-api-keystringRequired

### Query parameters
limitintegerOptionalDefaults to `100`
last_docstring or nullOptional

### Response
Successful Response
batch_callslist of objects
Show 12 properties
next_docstring or null
The next document, used to paginate through the batch calls
has_moreboolean or nullDefaults to `false`
Whether there are more batch calls to paginate through

### Errors
422
Unprocessable Entity Error
```

----------------------------------------

TITLE: Search User Group in ElevenLabs Workspace with TypeScript
DESCRIPTION: This snippet demonstrates how to search for user groups within the ElevenLabs workspace using the official TypeScript client library. It requires an API key for authentication and takes the group name as a parameter. The client library simplifies API calls to the ElevenLabs platform.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/search-user-groups

LANGUAGE: TypeScript
CODE:
```
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient({ apiKey: "YOUR_API_KEY" });
await client.workspace.groups.search({
  name: "name"
});
```

----------------------------------------

TITLE: ElevenLabs API: Get History Item Endpoint Documentation
DESCRIPTION: Comprehensive API documentation for the 'Get history item' endpoint. This section details the HTTP method, URL structure, required path parameters, necessary headers, and the full schema of the successful JSON response, including all fields related to the history item's metadata.

SOURCE: https://elevenlabs.io/docs/api-reference/history/get

LANGUAGE: APIDOC
CODE:
```
GET https://api.elevenlabs.io/v1/history/:history_item_id

Path parameters:
  history_item_id: string (Required)
    ID of the history item to be used. You can use the Get generated items endpoint to retrieve a list of history items.

Headers:
  xi-api-key: string (Required)

Response (200 Retrieved):
  history_item_id: string
    The ID of the history item.
  date_unix: integer
    Unix timestamp of when the item was created.
  character_count_change_from: integer
    The character count change from.
  character_count_change_to: integer
    The character count change to.
  content_type: string
    The content type of the generated item.
  state: any
  request_id: string or null
    The ID of the request.
  voice_id: string or null
    The ID of the voice used.
  model_id: string or null
    The ID of the model.
  voice_name: string or null
    The name of the voice.
  voice_category: enum or null
    The category of the voice. Either 'premade', 'cloned', 'generated' or 'professional'.
    Allowed values: premade, cloned, generated, professional
  text: string or null
    The text used to generate the audio item.
  settings: object or null
    The settings of the history item.
  feedback: object or null
    Feedback associated with the generated item. Returns null if no feedback has been provided.
  share_link_id: string or null
    The ID of the share link.
  source: enum or null
    The source of the history item. Either TTS (text to speech), STS (speech to text), AN (audio native), Projects, Dubbing, PlayAPI, PD (pronunciation dictionary) or ConvAI (conversational AI).
  alignments: object or null
    The alignments of the history item.
  dialogue: list of objects or null
    The dialogue (voice and text pairs) used to generate the audio item. If this is set then the top level `text` and `voice_id` fields will be empty.

Example Response Body:
{
  "history_item_id": "ja9xsmfGhxYcymxGcOGB",
  "date_unix": 1714650306,
  "character_count_change_from": 17189,
  "character_count_change_to": 17231,
  "content_type": "audio/mpeg",
  "state": null,
  "request_id": "BF0BZg4IwLGBlaVjv9Im",
  "voice_id": "21m00Tcm4TlvDq8ikWAM",
  "model_id": "eleven_multilingual_v2",
  "voice_name": "Rachel",
  "voice_category": "premade",
  "text": "Hello, world!",
  "settings": {
    "similarity_boost": 0.5,
    "stability": 0.71,
    "style": 0,
    "use_speaker_boost": true
  },
  "source": "TTS"
}
```

----------------------------------------

TITLE: Example Response: List Similar Voices API
DESCRIPTION: Provides a sample JSON response structure for a successful call to the 'List similar voices' API. It details the `voices` array with individual voice properties such as `voice_id`, `name`, `gender`, `language`, and `preview_url`, along with a `has_more` flag indicating pagination status.

SOURCE: https://elevenlabs.io/docs/api-reference/voices/get-similar-library-voices

LANGUAGE: JSON
CODE:
```
{
  "voices": [
    {
      "public_owner_id": "63e84100a6bf7874ba37a1bab9a31828a379ec94b891b401653b655c5110880f",
      "voice_id": "sB1b5zUrxQVAFl2PhZFp",
      "date_unix": 1714423232,
      "name": "Alita",
      "accent": "american",
      "gender": "Female",
      "age": "young",
      "descriptive": "calm",
      "use_case": "characters_animation",
      "category": "professional",
      "usage_character_count_1y": 12852,
      "usage_character_count_7d": 12852,
      "play_api_usage_character_count_1y": 12852,
      "cloned_by_count": 11,
      "free_users_allowed": true,
      "live_moderation_enabled": false,
      "featured": false,
      "language": "en",
      "description": "Perfectly calm, neutral and strong voice. Great for a young female protagonist.",
      "preview_url": "https://storage.googleapis.com/eleven-public-prod/wqkMCd9huxXHX1dy5mLJn4QEQHj1/voices/sB1b5zUrxQVAFl2PhZFp/55e71aac-5cb7-4b3d-8241-429388160509.mp3",
      "rate": 1,
      "verified_languages": [
        {
          "language": "en",
          "model_id": "eleven_multilingual_v2",
          "accent": "american",
          "locale": "en-US",
          "preview_url": "https://storage.googleapis.com/eleven-public-prod/wqkMCd9huxXHX1dy5mLJn4QEQHj1/voices/sB1b5zUrxQVAFl2PhZFp/55e71aac-5cb7-4b3d-8241-429388160509.mp3"
        }
      ]
    }
  ],
  "has_more": false
}
```

----------------------------------------

TITLE: Python Example: Delete MCP Server Tool Approval
DESCRIPTION: This Python code snippet demonstrates how to use the ElevenLabs client library to delete a tool approval for a specific MCP server. It requires an API key and the MCP server ID and tool name.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/mcp/approval-policies/delete

LANGUAGE: Python
CODE:
```
from elevenlabs import ElevenLabs

client = ElevenLabs(
    api_key="YOUR_API_KEY",
)
client.conversational_ai.mcp_servers.tool_approvals.delete(
    mcp_server_id="mcp_server_id",
    tool_name="tool_name",
)
```

----------------------------------------

TITLE: Get Audio Native Project Settings using ElevenLabs TypeScript Client
DESCRIPTION: Demonstrates how to fetch Audio Native project settings using the official ElevenLabs TypeScript client. It initializes the client with an API key and calls the `getSettings` method with a specific project ID.

SOURCE: https://elevenlabs.io/docs/api-reference/audio-native/get-settings

LANGUAGE: TypeScript
CODE:
```
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient({ apiKey: "YOUR_API_KEY" });
await client.audioNative.getSettings("21m00Tcm4TlvDq8ikWAM");
```

----------------------------------------

TITLE: Get Voices List API Endpoint Reference
DESCRIPTION: Detailed API documentation for the ElevenLabs 'Get Voices' endpoint. This section outlines the endpoint's purpose, required headers, all available query parameters with their types, descriptions, and default values, the structure of a successful response, and common error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/voices/search

LANGUAGE: APIDOC
CODE:
```
Endpoint: Gets a list of all available voices for a user with search, filtering and pagination.

Headers:
  xi-api-key: string (Required)

Query parameters:
  next_page_token: string or null (Optional)
    Description: The next page token to use for pagination. Returned from the previous request.
  page_size: integer (Optional, Defaults to 10)
    Description: How many voices to return at maximum. Can not exceed 100, defaults to 10. Page 0 may include more voices due to default voices being included.
  search: string or null (Optional)
    Description: Search term to filter voices by. Searches in name, description, labels, category.
  sort: string or null (Optional)
    Description: Which field to sort by, one of ‘created_at_unix’ or ‘name’. ‘created_at_unix’ may not be available for older voices.
  sort_direction: string or null (Optional)
    Description: Which direction to sort the voices in. 'asc' or 'desc'.
  voice_type: string or null (Optional)
    Description: Type of the voice to filter by. One of ‘personal’, ‘community’, ‘default’, ‘workspace’, ‘non-default’. ‘non-default’ is equal to all but ‘default’.
  category: string or null (Optional)
    Description: Category of the voice to filter by. One of 'premade', 'cloned', 'generated', 'professional'
  fine_tuning_state: string or null (Optional)
    Description: State of the voice’s fine tuning to filter by. Applicable only to professional voices clones. One of ‘draft’, ‘not_verified’, ‘not_started’, ‘queued’, ‘fine_tuning’, ‘fine_tuned’, ‘failed’, ‘delayed’
  collection_id: string or null (Optional)
    Description: Collection ID to filter voices by.
  include_total_count: boolean (Optional, Defaults to true)
    Description: Whether to include the total count of voices found in the response. Incurs a performance cost.

Response:
  Successful Response:
    voices: list of objects
      Description: Show 20 properties (details not provided in snippet)
    has_more: boolean
    total_count: integer
    next_page_token: string or null

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs Speech-to-Speech Conversion API Reference
DESCRIPTION: Detailed documentation for the ElevenLabs speech-to-speech conversion endpoint, including request parameters, their types, descriptions, and expected response.

SOURCE: https://elevenlabs.io/docs/api-reference/speech-to-speech/stream

LANGUAGE: APIDOC
CODE:
```
Endpoint: /v1/speech-to-speech/convert
Method: POST
Content-Type: multipart/form-data

Request Parameters:
  audiofile:
    Type: file
    Required: true
    Description: The audio file which holds the content and emotion that will control the generated speech.

  model_id:
    Type: string
    Optional: true
    Default: eleven_english_sts_v2
    Description: Identifier of the model that will be used, you can query them using GET /v1/models. The model needs to have support for speech to speech, you can check this using the can_do_voice_conversion property.

  voice_settings:
    Type: string or null
    Optional: true
    Description: Voice settings overriding stored settings for the given voice. They are applied only on the given request. Needs to be send as a JSON encoded string.

  seed:
    Type: integer or null
    Optional: true
    Description: If specified, our system will make a best effort to sample deterministically, such that repeated requests with the same seed and parameters should return the same result. Determinism is not guaranteed. Must be integer between 0 and 4294967295.

  remove_background_noise:
    Type: boolean
    Optional: true
    Default: false
    Description: If set, will remove the background noise from your audio input using our audio isolation model. Only applies to Voice Changer.

  file_format:
    Type: enum or null
    Optional: true
    Default: other
    Description: The format of input audio. Options are ‘pcm_s16le_16’ or ‘other’ For pcm_s16le_16, the input audio must be 16-bit PCM at a 16kHz sample rate, single channel (mono), and little-endian byte order. Latency will be lower than with passing an encoded waveform.
    Allowed values:
      - pcm_s16le_16
      - other

Response:
  Type: Streaming audio data

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Example Successful Dubbing Resource Response JSON
DESCRIPTION: Provides a sample JSON structure returned upon a successful retrieval of a dubbing resource. It includes key identifiers, versioning, language information, and detailed properties for input, background, and foreground audio components.

SOURCE: https://elevenlabs.io/docs/api-reference/dubbing/resources/get-resource

LANGUAGE: JSON
CODE:
```
{
  "id": "foo",
  "version": 42,
  "source_language": "foo",
  "target_languages": [
    "foo"
  ],
  "input": {
    "src": "foo",
    "content_type": "foo",
    "bucket_name": "foo",
    "random_path_slug": "foo",
    "duration_secs": 42,
    "is_audio": true,
    "url": "foo"
  },
  "background": {
    "src": "foo",
    "content_type": "foo",
    "bucket_name": "foo",
    "random_path_slug": "foo",
    "duration_secs": 42,
    "is_audio": true,
    "url": "foo"
  },
  "foreground": {
    "src": "foo",
    "content_type": "foo",
    "bucket_name": "foo",
    "random_path_slug": "foo",
    "duration_secs": 42,
    "is_audio": true,
    "url": "foo"
  },
  "speaker_tracks": {},
  "speaker_segments": {},
  "renders": {}
}
```

----------------------------------------

TITLE: ElevenLabs API References from FAQ
DESCRIPTION: Highlights specific API parameters and identifiers mentioned in the Frequently Asked Questions section, such as `voice_id`, `model_id`, and `remove_background_noise`.

SOURCE: https://elevenlabs.io/docs/capabilities/voice-changer

LANGUAGE: APIDOC
CODE:
```
API References from FAQ:
  Custom Voice Usage:
    voice_id: Required for custom voices
    model_id: Required for custom voices
  Noise Reduction:
    remove_background_noise: boolean (set to true to minimize environmental sounds)
  Model IDs:
    eleven_english_sts_v2
    eleven_multilingual_sts_v2 (often outperforms for English material)
```

----------------------------------------

TITLE: ElevenLabs API: Remove Member from User Group Endpoint Reference
DESCRIPTION: This API documentation provides a detailed reference for the 'Remove member from user group' endpoint. It specifies the HTTP method, URL, required path and header parameters, the structure of the request body, and the expected successful response, including the data types and descriptions for each field. It also notes potential error responses.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/groups/members/remove

LANGUAGE: APIDOC
CODE:
```
Endpoint:
  Method: POST
  URL: https://api.elevenlabs.io/v1/workspace/groups/:group_id/members/remove

Path Parameters:
  group_id: string (Required)
    Description: The ID of the target group.

Headers:
  xi-api-key: string (Required)

Request Body:
  Type: object
  Properties:
    email: string (Required)
      Description: The email of the target workspace member.

Responses:
  200 Successful:
    Body:
      Type: object
      Properties:
        status: string
          Description: The status of the workspace group member deletion request. If the request was successful, the status will be 'ok'. Otherwise an error message with status 500 will be returned.
    Example:
      {
        "status": "ok"
      }
  422 Unprocessable Entity Error:
    Description: Indicates issues with the request payload or parameters.
```

----------------------------------------

TITLE: ElevenLabs Studio Project Conversion API Reference
DESCRIPTION: Detailed API documentation for the `POST /v1/studio/projects/:project_id/convert` endpoint, which is used to start the conversion process for an ElevenLabs Studio project and its associated chapters. This section outlines the endpoint's path, required parameters, headers, successful response structure, and potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/convert-project

LANGUAGE: APIDOC
CODE:
```
Endpoint:
  POST /v1/studio/projects/:project_id/convert

Description:
  Starts conversion of a Studio project and all of its chapters.

Path Parameters:
  project_id:
    Type: string
    Required: true
    Description: The ID of the project to be used. You can use the List projects endpoint to list all the available projects.

Headers:
  xi-api-key:
    Type: string
    Required: true

Response (200 Successful):
  status:
    Type: string
    Description: The status of the studio project conversion request. If the request was successful, the status will be 'ok'. Otherwise an error message with status 500 will be returned.

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs API Send Operations
DESCRIPTION: Describes the different operations available for sending data to the ElevenLabs API, such as initializing connections, sending text, and managing contexts, along with their required object types and property counts.

SOURCE: https://elevenlabs.io/docs/api-reference/multi-context-text-to-speech/v-1-text-to-speech-voice-id-multi-stream-input

LANGUAGE: APIDOC
CODE:
```
initializeConnectionMulti: object (Required)
	- Properties: Show 7 properties
OR
initialiseContext: object (Required)
	- Properties: Show 7 properties
OR
sendTextMulti: object (Required)
	- Properties: Show 3 properties
OR
flushContextClient: object (Required)
	- Properties: Show 3 properties
OR
closeContextClient: object (Required)
	- Properties: Show 2 properties
OR
closeSocketClient: object (Required)
	- Properties: Show 1 properties
OR
keepContextAlive: object (Required)
	- Properties: Show 2 properties
```

----------------------------------------

TITLE: Other API Updates: Add Pronunciation Dictionary from File
DESCRIPTION: Updates the 'Add pronunciation dictionary from file' endpoint, making properties nullable.

SOURCE: https://elevenlabs.io/docs/changelog/2025/3/17

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /docs/api-reference/pronunciation-dictionary/add-from-file
Changes:
  - Made nullable: `dictionary_name`, `description`
```

----------------------------------------

TITLE: Retrieve Generated Audio History with ElevenLabs TypeScript Client
DESCRIPTION: This TypeScript code snippet demonstrates how to initialize the ElevenLabs client with an API key and then call the `history.list()` method to fetch a list of previously generated audio items. It's a basic example for integrating with the ElevenLabs API.

SOURCE: https://elevenlabs.io/docs/api-reference/history/get-all

LANGUAGE: TypeScript
CODE:
```
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient({ apiKey: "YOUR_API_KEY" });
await client.history.list();
```

----------------------------------------

TITLE: Updated API Features: Conversational AI Enhancements
DESCRIPTION: Describes several enhancements to the Conversational AI API, including new tool configurations, improved RAG parameters, support for text-only widget mode, and additional fields in batch call responses.

SOURCE: https://elevenlabs.io/docs/changelog/2025/5/26

LANGUAGE: APIDOC
CODE:
```
Conversational AI Updates:
  Agent Configuration:
    - Enhanced system tools with new `skip_turn` tool configuration.
    - Improved RAG configuration with `max_retrieved_rag_chunks_count` parameter.
  Widget Configuration:
    - Added support for text-only mode.
  Batch Calling:
    - Batch call responses now include `phone_provider` field with default value “twilio”.
```

----------------------------------------

TITLE: Updated API Endpoint: Get Studio Project Snapshot
DESCRIPTION: The `Get project snapshot` endpoint has removed the `status` property, simplifying the snapshot metadata.

SOURCE: https://elevenlabs.io/docs/changelog/2025/3/24

LANGUAGE: APIDOC
CODE:
```
API Endpoint: /docs/api-reference/studio/get-project-snapshot
Changes:
- Removed property: `status`
```

----------------------------------------

TITLE: Successful Response Schema for Audio Native Project Settings
DESCRIPTION: Provides an example of a successful 200 HTTP response for retrieving Audio Native project settings. It outlines the JSON structure including `enabled`, `snapshot_id`, and a detailed `settings` object with various project properties and their types.

SOURCE: https://elevenlabs.io/docs/api-reference/audio-native/get-settings

LANGUAGE: APIDOC
CODE:
```
200 Retrieved Response Body:
{
  "enabled": true,
  "snapshot_id": "JBFqnCBsd6RMkjVDRZzb",
  "settings": {
    "title": "My Project",
    "image": "https://example.com/image.jpg",
    "author": "John Doe",
    "small": false,
    "text_color": "#000000",
    "background_color": "#FFFFFF",
    "sessionization": 1,
    "audio_path": "audio/my_project.mp3",
    "audio_url": "https://example.com/audio/my_project.mp3",
    "status": "ready"
  }
}

Response Fields:
  enabled: boolean
    Whether the project is enabled.
  snapshot_id: string or null
    The ID of the latest snapshot of the project.
  settings: object or null
    The settings of the project.
    Properties:
      title: string
      image: string
      author: string
      small: boolean
      text_color: string
      background_color: string
      sessionization: number
      audio_path: string
      audio_url: string
      status: string
```

----------------------------------------

TITLE: ElevenLabs Conversational AI API: Delete Agent Endpoint Reference
DESCRIPTION: Comprehensive API documentation for the DELETE /v1/convai/agents/:agent_id endpoint, detailing the required path parameters, authentication headers, and potential error responses for deleting an agent.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/agents/delete

LANGUAGE: APIDOC
CODE:
```
DELETE /v1/convai/agents/:agent_id

Path parameters:
  agent_id: string (Required)
    The id of an agent. This is returned on agent creation.

Headers:
  xi-api-key: string (Required)

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: cURL Example to List Eleven Labs Studio Projects
DESCRIPTION: Provides a cURL command to demonstrate how to make an authenticated GET request to the Eleven Labs API to retrieve a list of Studio projects. It requires an API key to be passed in the 'xi-api-key' header.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/get-projects

LANGUAGE: cURL
CODE:
```
curl https://api.elevenlabs.io/v1/studio/projects \
-H "xi-api-key: xi-api-key"
```

----------------------------------------

TITLE: API Specification: Get All Conversational AI Workspace Secrets
DESCRIPTION: This section details the REST API endpoint for retrieving all workspace secrets. It specifies the HTTP method, URL, required authentication header, the structure of a successful 200 OK response, and potential error codes like 422 Unprocessable Entity.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/secrets/list

LANGUAGE: APIDOC
CODE:
```
Endpoint: GET /v1/convai/secrets
Full URL: https://api.elevenlabs.io/v1/convai/secrets

Description: Get all workspace secrets for the user.

Headers:
  - xi-api-key (string, Required): Your API key for authentication.

Responses:
  - 200 OK (Successful Response):
    Description: Retrieved successfully.
    Body:
      secrets (list of objects): A list containing workspace secret objects.
        Properties:
          - type (string)
          - secret_id (string)
          - name (string)
          - used_by (object): Details on where the secret is used.
            Properties:
              - tools (list of objects)
              - agents (list of objects)
              - others (list of strings)
              - phone_numbers (list of objects)

Errors:
  - 422 Unprocessable Entity Error
```

----------------------------------------

TITLE: Widget API: Text Input and Multi-Modality Support
DESCRIPTION: Details updates to the widget configuration API, adding support for text input and a text-only mode, enhancing user experience with multi-modality.

SOURCE: https://elevenlabs.io/docs/changelog

LANGUAGE: APIDOC
CODE:
```
Endpoint: /docs/api-reference/widget/get
Method: GET
Description: Retrieve widget configuration.

Response Body Properties:
  widget_config:
    supports_text_only: boolean (Added, indicates support for text input and text-only mode)
```

----------------------------------------

TITLE: Retrieve History Item using ElevenLabs TypeScript SDK
DESCRIPTION: This TypeScript code snippet demonstrates how to initialize the ElevenLabs client with an API key and then use it to retrieve a specific history item by its ID. It showcases a basic usage pattern for interacting with the ElevenLabs API.

SOURCE: https://elevenlabs.io/docs/api-reference/history/get

LANGUAGE: TypeScript
CODE:
```
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient({ apiKey: "YOUR_API_KEY" });
await client.history.get("VW7YKqPnjY4h39yTbx2L");
```

----------------------------------------

TITLE: API Reference for Create Phone Number Endpoint
DESCRIPTION: Detailed API documentation for the POST `/v1/convai/phone-numbers/create` endpoint. It specifies the required `xi-api-key` header, the two possible request body objects (`CreateTwilioPhoneNumberRequest` or `CreateSIPTrunkPhoneNumberRequest`), and the structure of the successful response including the `phone_number_id`.

SOURCE: https://elevenlabs.io/docs/api-reference/phone-numbers/create

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/convai/phone-numbers/create

Headers:
  xi-api-key: string (Required)

Request Body:
  CreateTwilioPhoneNumberRequest: object (Required)
    (Show 5 properties)
  OR
  CreateSIPTrunkPhoneNumberRequest: object (Required)
    (Show 10 properties)

Response:
  200 Successful:
    phone_number_id: string (Phone entity ID)

Errors:
  422 Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference: POST /v1/dubbing/resource/:dubbing_id/transcribe
DESCRIPTION: This section details the `POST` endpoint for transcribing segments within a dubbing project. It explains the endpoint's purpose, required path parameters (`dubbing_id`), necessary headers (`xi-api-key`), the structure of the request body (a list of `segments`), the expected successful response format (an object with a `version` integer), and potential error responses like 422 Unprocessable Entity.

SOURCE: https://elevenlabs.io/docs/api-reference/dubbing/resources/transcribe-segment

LANGUAGE: APIDOC
CODE:
```
POST /v1/dubbing/resource/:dubbing_id/transcribe

Description: Regenerate the transcriptions for the specified segments. Does not automatically regenerate translations or dubs.

Path Parameters:
  dubbing_id: string (Required) - ID of the dubbing project.

Headers:
  xi-api-key: string (Required)

Request Body:
  segments: list of strings (Required) - Transcribe this specific list of segments.

Responses:
  200 Successful:
    {
      "version": 42
    }
    version: integer
  422 Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference: Edit Voice Settings Endpoint
DESCRIPTION: This section provides the comprehensive API documentation for editing voice settings. It details the `POST` request to `/v1/voices/:voice_id/settings/edit`, including required path parameters (`voice_id`), headers (`xi-api-key`), and a detailed breakdown of the request body parameters (e.g., `stability`, `similarity_boost`, `style`, `speed`) with their types and descriptions. It also outlines the expected successful response format and potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/voices/settings/update

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST https://api.elevenlabs.io/v1/voices/:voice_id/settings/edit
Description: Edit your settings for a specific voice. "similarity_boost" corresponds to "Clarity + Similarity Enhancement" in the web app and "stability" corresponds to "Stability" slider in the web app.

Path Parameters:
  voice_id: string (Required)
    ID of the voice to be used. You can use the Get voices endpoint list all the available voices.

Headers:
  xi-api-key: string (Required)

Request Body:
  Object (expects an object)
  Properties:
    stability: double or null (Optional)
      Determines how stable the voice is and the randomness between each generation. Lower values introduce broader emotional range for the voice. Higher values can result in a monotonous voice with limited emotion.
    use_speaker_boost: boolean or null (Optional)
      This setting boosts the similarity to the original speaker. Using this setting requires a slightly higher computational load, which in turn increases latency.
    similarity_boost: double or null (Optional)
      Determines how closely the AI should adhere to the original voice when attempting to replicate it.
    style: double or null (Optional)
      Determines the style exaggeration of the voice. This setting attempts to amplify the style of the original speaker. It does consume additional computational resources and might increase latency if set to anything other than 0.
    speed: double or null (Optional)
      Adjusts the speed of the voice. A value of 1.0 is the default speed, while values less than 1.0 slow down the speech, and values greater than 1.0 speed it up.

Responses:
  200 Successful:
    Body:
      status: string
        The status of the voice settings edit request. If the request was successful, the status will be 'ok'. Otherwise an error message with status 500 will be returned.
    Example:
      {
        "status": "ok"
      }
  422 Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference for Retry Batch Calling Job Endpoint
DESCRIPTION: This section details the API endpoint for retrying a batch calling job. It specifies the HTTP method (POST), the endpoint URL, required path parameters like 'batch_id', and necessary headers such as 'xi-api-key'. It also outlines the structure of a successful 200 response, including various fields like 'id', 'status', and 'phone_provider', and lists possible error responses like 422 Unprocessable Entity.

SOURCE: https://elevenlabs.io/docs/api-reference/batch-calling/retry

LANGUAGE: APIDOC
CODE:
```
API Endpoint:
  Method: POST
  URL: https://api.elevenlabs.io/v1/convai/batch-calling/:batch_id/retry
  Description: Retry a batch call by setting completed recipients back to pending status.

Path Parameters:
  batch_id:
    Type: string
    Required: true

Headers:
  xi-api-key:
    Type: string
    Required: true

Response (200 Successful):
  Example JSON:
    {
      "id": "foo",
      "phone_number_id": "foo",
      "name": "foo",
      "agent_id": "foo",
      "created_at_unix": 42,
      "scheduled_time_unix": 42,
      "total_calls_dispatched": 42,
      "total_calls_scheduled": 42,
      "last_updated_at_unix": 42,
      "status": "pending",
      "agent_name": "foo",
      "phone_provider": "twilio"
    }
  Fields:
    id: string
    phone_number_id: string
    name: string
    agent_id: string
    created_at_unix: integer
    scheduled_time_unix: integer
    total_calls_dispatched: integer
    total_calls_scheduled: integer
    last_updated_at_unix: integer
    status: enum (Allowed values: pending, in_progress, completed, failed, cancelled)
    agent_name: string
    phone_provider: enum or null (Allowed values: twilio, sip_trunk)

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference: Send Conversation Feedback Endpoint
DESCRIPTION: Detailed API documentation for the POST /v1/convai/conversations/:conversation_id/feedback endpoint. This endpoint allows users to submit 'like' or 'dislike' feedback for a given conversation, requiring a conversation ID as a path parameter and an API key in the request headers. The request body specifies the feedback type.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/conversations/create

LANGUAGE: APIDOC
CODE:
```
POST /v1/convai/conversations/:conversation_id/feedback

Path parameters:
  conversation_id:
    type: string
    required: true
    description: The id of the conversation you're taking the action on.

Headers:
  xi-api-key:
    type: string
    required: true

Request Body:
  feedback:
    type: enum
    required: true
    description: Either 'like' or 'dislike' to indicate the feedback for the conversation.
    allowed_values: ['like', 'dislike']

Response:
  Successful Response

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: List Similar Voices API Endpoint and TypeScript Client Example
DESCRIPTION: Documents the API endpoint for finding voices similar to a provided audio sample, detailing the POST method, URL, required headers, optional request parameters (audio_file, similarity_threshold, top_k), and the structure of the successful 200 response including voice properties and pagination flags. A TypeScript client example is provided to demonstrate how to make this API call.

SOURCE: https://elevenlabs.io/docs/api-reference/voices/find-similar-voices

LANGUAGE: TypeScript
CODE:
```
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient({ apiKey: "YOUR_API_KEY" });
await client.voices.findSimilarVoices({});
```

LANGUAGE: APIDOC
CODE:
```
Endpoint: List similar voices
Method: POST
URL: https://api.elevenlabs.io/v1/similar-voices
Description: Returns a list of shared voices similar to the provided audio sample. If neither similarity_threshold nor top_k is provided, we will apply default values.

Headers:
  xi-api-key: string (Required)

Request Body (multipart/form-data):
  audio_file: file (Optional)
  similarity_threshold: double or null (Optional)
    Description: Threshold for voice similarity between provided sample and library voices. Values range from 0 to 2. The smaller the value the more similar voices will be returned.
  top_k: integer or null (Optional)
    Description: Number of most similar voices to return. If similarity_threshold is provided, less than this number of voices may be returned. Values range from 1 to 100.

Response (200 Successful):
  voices: list of objects
    Description: The list of shared voices
    Properties:
      public_owner_id: string
      voice_id: string
      date_unix: integer
      name: string
      accent: string
      gender: string
      age: string
      descriptive: string
      use_case: string
      category: string
      usage_character_count_1y: integer
      usage_character_count_7d: integer
      play_api_usage_character_count_1y: integer
      cloned_by_count: integer
      free_users_allowed: boolean
      live_moderation_enabled: boolean
      featured: boolean
      language: string
      description: string
      preview_url: string
      rate: integer
      verified_languages: list of objects
        Properties:
          language: string
          model_id: string
          accent: string
          locale: string
          preview_url: string
  has_more: boolean
    Description: Whether there are more shared voices in subsequent pages.
  last_sort_id: string or null

Example 200 Successful Response:
{
  "voices": [
    {
      "public_owner_id": "63e84100a6bf7874ba37a1bab9a31828a379ec94b891b401653b655c5110880f",
      "voice_id": "sB1b5zUrxQVAFl2PhZFp",
      "date_unix": 1714423232,
      "name": "Alita",
      "accent": "american",
      "gender": "Female",
      "age": "young",
      "descriptive": "calm",
      "use_case": "characters_animation",
      "category": "professional",
      "usage_character_count_1y": 12852,
      "usage_character_count_7d": 12852,
      "play_api_usage_character_count_1y": 12852,
      "cloned_by_count": 11,
      "free_users_allowed": true,
      "live_moderation_enabled": false,
      "featured": false,
      "language": "en",
      "description": "Perfectly calm, neutral and strong voice. Great for a young female protagonist.",
      "preview_url": "https://storage.googleapis.com/eleven-public-prod/wqkMCd9huxXHX1dy5mLJn4QEQHj1/voices/sB1b5zUrxQVAFl2PhZFp/55e71aac-5cb7-4b3d-8241-429388160509.mp3",
      "rate": 1,
      "verified_languages": [
        {
          "language": "en",
          "model_id": "eleven_multilingual_v2",
          "accent": "american",
          "locale": "en-US",
          "preview_url": "https://storage.googleapis.com/eleven-public-prod/wqkMCd9huxXHX1dy5mLJn4QEQHj1/voices/sB1b5zUrxQVAFl2PhZFp/55e71aac-5cb7-4b3d-8241-429388160509.mp3"
        }
      ]
    }
  ],
  "has_more": false
}
```

----------------------------------------

TITLE: ElevenLabs API Reference: Delete Workspace Member Endpoint
DESCRIPTION: This section provides a comprehensive reference for the `DELETE /v1/workspace/members` API endpoint. It details the endpoint's purpose (deleting a workspace member, restricted to administrators), required `xi-api-key` header, the structure of the request body (requiring an `email` string), the successful response format (`status: ok`), and potential error responses like `422 Unprocessable Entity Error`.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/delete-member

LANGUAGE: APIDOC
CODE:
```
Endpoint: DELETE /v1/workspace/members
Description: Deletes a workspace member. This endpoint may only be called by workspace administrators.

Headers:
  xi-api-key: string (Required)

Request Body:
  email: string (Required)
    Description: Email of the target user.

Response (200 OK):
  status: string
    Description: The status of the workspace member deletion request. If the request was successful, the status will be 'ok'. Otherwise an error message with status 500 will be returned.

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Eleven Labs API: Voice Design Endpoint Reference
DESCRIPTION: Detailed API documentation for the POST /v1/text-to-voice/create-previews endpoint. It outlines the required headers, optional query parameters, the structure and constraints of the request body, and the format of the successful JSON response, including potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/legacy/voices/create-previews

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST https://api.elevenlabs.io/v1/text-to-voice/create-previews

Description: Create a voice from a text prompt.

Headers:
  xi-api-key: string (Required)

Query Parameters:
  output_format: enum (Optional, Defaults to mp3_44100_192)
    Description: The output format of the generated audio.

Request Body:
  voice_description: string (Required, >=20 characters, <=1000 characters)
    Description: Description to use for the created voice.
  text: string or null (Optional, >=100 characters, <=1000 characters)
    Description: Text to generate, text length has to be between 100 and 1000.
  auto_generate_text: boolean (Optional, Defaults to false)
    Description: Whether to automatically generate a text suitable for the voice description.
  loudness: double (Optional, >=-1, <=1, Defaults to 0.5)
    Description: Controls the volume level of the generated voice. -1 is quietest, 1 is loudest, 0 corresponds to roughly -24 LUFS.
  quality: double (Optional, >=-1, <=1, Defaults to 0.9)
    Description: Higher quality results in better voice output but less variety.
  seed: integer or null (Optional, >=0, <=2147483647)
    Description: Random number that controls the voice generation. Same seed with same inputs produces same voice.
  guidance_scale: double (Optional, >=0, <=100, Defaults to 5)
    Description: Controls how closely the AI follows the prompt. Lower numbers give the AI more freedom to be creative, while higher numbers force it to stick more to the prompt. High numbers can cause voice to sound artificial or robotic. We recommend to use longer, more detailed prompts at lower Guidance Scale.

Response (200 Successful):
  previews: list of objects
    audio_base_64: string
    generated_voice_id: string
    media_type: string
    duration_secs: number
  text: string
    Description: The text used to preview the voices.

Response Example (200 Successful):
{
  "previews": [
    {
      "audio_base_64": "foo",
      "generated_voice_id": "foo",
      "media_type": "foo",
      "duration_secs": 42
    }
  ],
  "text": "foo"
}

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference: POST /v1/forced-alignment Endpoint
DESCRIPTION: Detailed API documentation for the ElevenLabs Forced Alignment endpoint, including HTTP method, URL, required headers, request body parameters for multipart form data (file, text, enabled_spooled_file), and the structure of the successful response.

SOURCE: https://elevenlabs.io/docs/api-reference/forced-alignment/create

LANGUAGE: APIDOC
CODE:
```
Method: POST
URL: https://api.elevenlabs.io/v1/forced-alignment

Description: Force align an audio file to text. Use this endpoint to get the timing information for each character and word in an audio file based on a provided text transcript.

Headers:
  xi-api-key: string (Required)

Request Body (multipart/form-data):
  file: file (Required) - The file to align. All major audio formats are supported. The file size must be less than 1GB.
  text: string (Required) - The text to align with the audio. The input text can be in any format, however diarization is not supported at this time.
  enabled_spooled_file: boolean (Optional, Defaults to `false`) - If true, the file will be streamed to the server and processed in chunks. This is useful for large files that cannot be loaded into memory.

Response (200 Successful):
  characters: list of objects - List of characters with their timing information.
  words: list of objects - List of words with their timing information.

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Eleven Labs Dubbing API: Translate Segment Request and cURL Example
DESCRIPTION: This snippet defines the HTTP POST endpoint for translating segments within a specified dubbing project and provides a cURL command example to demonstrate its usage. It shows how to include the API key and the JSON request body with segments and languages.

SOURCE: https://elevenlabs.io/docs/api-reference/dubbing/translate-segments

LANGUAGE: APIDOC
CODE:
```
POST
/v1/dubbing/resource/:dubbing_id/translate
```

LANGUAGE: cURL
CODE:
```
curl -X POST https://api.elevenlabs.io/v1/dubbing/resource/dubbing_id/translate \n-H "xi-api-key: xi-api-key" \n-H "Content-Type: application/json" \n-d '{ \n"segments": [ \n"foo" \n], \n"languages": [ \n"foo" \n] \n}'
```

----------------------------------------

TITLE: API Reference: Simulate Conversation Endpoint
DESCRIPTION: Detailed API documentation for the POST /v1/convai/agents/:agent_id/simulate-conversation endpoint, covering path parameters, request headers, request body schema, and successful response body schema.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/agents/simulate-conversation

LANGUAGE: APIDOC
CODE:
```
POST /v1/convai/agents/:agent_id/simulate-conversation

Path Parameters:
  agent_id: string (Required)
    Description: The id of an agent. This is returned on agent creation.

Headers:
  xi-api-key: string (Required)

Request Body:
  Type: object
  Properties:
    simulation_specification: object (Required)
      Description: A specification detailing how the conversation should be simulated.
      (Note: Contains 4 additional properties not detailed here.)
    extra_evaluation_criteria: list of objects or null (Optional)
      Description: A list of evaluation criteria to test.
      (Note: Contains 5 additional properties not detailed here.)

Response Body (200 Successful):
  Type: object
  Properties:
    simulated_conversation: list of objects
      (Note: Contains 13 additional properties not detailed here.)
    analysis: object
      (Note: Contains 4 additional properties not detailed here.)

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs Knowledge Base API Response Models and Error Codes
DESCRIPTION: Details the various successful response models (GetKnowledgeBaseURLResponseModel, GetKnowledgeBaseFileResponseModel, GetKnowledgeBaseTextResponseModel) and a common error response (422 Unprocessable Entity) for the ElevenLabs Knowledge Base API.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/knowledge-base/get-document

LANGUAGE: APIDOC
CODE:
```
### Response
Successful Response
GetKnowledgeBaseURLResponseModelobject
  Show 8 properties
OR
GetKnowledgeBaseFileResponseModelobject
  Show 7 properties
OR
GetKnowledgeBaseTextResponseModelobject
  Show 7 properties
### Errors
422
Unprocessable Entity Error
```

----------------------------------------

TITLE: Call ElevenLabs Speech-to-Text API with cURL
DESCRIPTION: This cURL command demonstrates how to make a POST request to the ElevenLabs Speech-to-Text API. It includes setting the `xi-api-key` header, `Content-Type` as `multipart/form-data`, and sending a `model_id` along with the audio file.

SOURCE: https://elevenlabs.io/docs/api-reference/speech-to-text/convert

LANGUAGE: cURL
CODE:
```
curl -X POST https://api.elevenlabs.io/v1/speech-to-text \
-H "xi-api-key: xi-api-key" \
-H "Content-Type: multipart/form-data" \
-F model_id="foo" \
-F file=@<file1>
```

----------------------------------------

TITLE: API Reference for Create MCP Server Endpoint
DESCRIPTION: Detailed API documentation for the POST /v1/convai/mcp-servers endpoint. This section outlines the required headers, the structure of the request body, and the properties of the successful 200 OK response, along with potential error codes.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/mcp/create

LANGUAGE: APIDOC
CODE:
```
POST /v1/convai/mcp-servers
Description: Create a new MCP server configuration in the workspace.

Headers:
  xi-api-key: string (Required)

Request Body:
  Type: object (This endpoint expects an object.)
  Properties:
    config: object (Required)
      Description: Configuration details for the MCP Server.
      (Show 8 properties)

Response (200 Successful):
  id: string
  config: object (Show 8 properties)
  metadata: object (The metadata of the MCP Server, Show 2 properties)
  access_info: object or null (The access information of the MCP Server, Show 4 properties)
  dependent_agents: list of objects or null (List of agents that depend on this MCP Server, Show 2 variants)

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference: Update Convai Dashboard Settings (PATCH)
DESCRIPTION: This section details the API endpoint for updating the Conversational AI dashboard settings. It specifies the HTTP method (PATCH), the endpoint path, required headers, the structure of the request body, and the expected successful response. An example JSON response is also provided.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/workspace/dashboard/update

LANGUAGE: APIDOC
CODE:
```
Method: PATCH
Path: /v1/convai/settings/dashboard

Headers:
  xi-api-key: string (Required)

Request Body:
  Type: object
  Properties:
    charts: list of objects (Optional)

Response (200 OK):
  Type: object
  Properties:
    charts: list of objects or null
```

LANGUAGE: json
CODE:
```
{
  "charts": [
    {
      "name": "foo",
      "type": "call_success"
    }
  ]
}
```

----------------------------------------

TITLE: Successful User Invitation API Response (JSON)
DESCRIPTION: This JSON snippet illustrates the expected successful response from the ElevenLabs API after a user invitation request. A `status` value of 'ok' confirms that the invitation email has been successfully processed and sent.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/invite-user

LANGUAGE: JSON
CODE:
```
{
  "status": "ok"
}
```

----------------------------------------

TITLE: ElevenLabs API: Create Speech with Timing Endpoint Reference
DESCRIPTION: This section details the API endpoint for generating speech with character-level timing. It specifies the HTTP method, URL path, required path parameters like `voice_id`, and necessary headers such as `xi-api-key` for authentication.

SOURCE: https://elevenlabs.io/docs/api-reference/text-to-speech/convert-with-timestamps

LANGUAGE: APIDOC
CODE:
```
POST https://api.elevenlabs.io/v1/text-to-speech/:voice_id/with-timestamps

Path parameters:
  voice_id: string (Required)
    Voice ID to be used, you can use https://api.elevenlabs.io/v1/voices to list all the available voices.

Headers:
  xi-api-key: string (Required)
```

----------------------------------------

TITLE: Conversational AI - New MCP Server API Endpoints
DESCRIPTION: Introduces new API endpoints for managing Model Context Protocol (MCP) servers within the Conversational AI system, covering creation, listing, retrieval, and approval policy management for MCP tools.

SOURCE: https://elevenlabs.io/docs/changelog

LANGUAGE: APIDOC
CODE:
```
Create MCP server: Create a new MCP server configuration in the workspace
List MCP servers: Retrieve all MCP server configurations available in the workspace
Get MCP server: Retrieve a specific MCP server configuration from the workspace
Update MCP server approval policy: Update the approval policy configuration for an MCP server
Create MCP server tool approval: Add approval for a specific MCP tool when using per-tool approval mode
Delete MCP server tool approval: Remove approval for a specific MCP tool when using per-tool approval mode
```

----------------------------------------

TITLE: API Reference for Invite Multiple Users Endpoint
DESCRIPTION: This section provides the detailed API specification for the `POST /v1/workspace/invites/add-bulk` endpoint. It outlines the required headers, the structure of the request body including email and optional group IDs, the successful response format, and potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/invite-multiple-users

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/workspace/invites/add-bulk
Description: Sends email invitations to join your workspace to the provided emails. Requires all email addresses to be part of a verified domain. If the users don't have an account they will be prompted to create one. If the users accept these invites they will be added as users to your workspace and your subscription using one of your seats. This endpoint may only be called by workspace administrators.

Headers:
  xi-api-key: string (Required)

Request Body:
  emails: list of strings (Required) - The email of the customer
  group_ids: list of strings or null (Optional) - The group ids of the user

Response (200 Successful):
  status: string - The status of the workspace invite request. If the request was successful, the status will be 'ok'. Otherwise an error message with status 500 will be returned.

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Download History Items using cURL
DESCRIPTION: This cURL command demonstrates how to download one or more history items from the ElevenLabs API by sending a POST request to the /v1/history/download endpoint. It requires an API key and a JSON payload containing a list of history item IDs.

SOURCE: https://elevenlabs.io/docs/api-reference/history/download

LANGUAGE: shell
CODE:
```
curl -X POST https://api.elevenlabs.io/v1/history/download \
-H "xi-api-key: xi-api-key" \
-H "Content-Type: application/json" \
-d '{
"history_item_ids": [
"foo"
]
}'
```

----------------------------------------

TITLE: ElevenLabs API Reference: GET PVC Speaker Separation Status Endpoint
DESCRIPTION: This section provides comprehensive documentation for the `GET /v1/voices/pvc/:voice_id/samples/:sample_id/speakers` API endpoint. It details the required path parameters (`voice_id`, `sample_id`), necessary headers (`xi-api-key`), and the structure of the successful JSON response, including `voice_id`, `sample_id`, `status`, `speakers`, and `selected_speaker_ids`. It also mentions the 422 Unprocessable Entity error.

SOURCE: https://elevenlabs.io/docs/api-reference/voices/pvc/samples/get-speaker-separation-status

LANGUAGE: APIDOC
CODE:
```
Endpoint: GET https://api.elevenlabs.io/v1/voices/pvc/:voice_id/samples/:sample_id/speakers

Path parameters:
  voice_id: string (Required)
    Description: Voice ID to be used, you can use https://api.elevenlabs.io/v1/voices to list all the available voices.
  sample_id: string (Required)
    Description: Sample ID to be used

Headers:
  xi-api-key: string (Required)

Response (200 Retrieved):
  voice_id: string
    Description: The ID of the voice.
  sample_id: string
    Description: The ID of the sample.
  status: enum (Allowed values: not_started, pending, completed, failed)
    Description: The status of the speaker separation.
  speakers: map from strings to objects or null
    Description: The speakers of the sample.
  selected_speaker_ids: list of strings or null
    Description: The IDs of the selected speakers.

Example Response:
{
  "voice_id": "DCwhRBWXzGAHq8TQ4Fs18",
  "sample_id": "DCwhRBWXzGAHq8TQ4Fs18",
  "status": "not_started"
}

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: New ElevenLabs Dubbing Resource Management Endpoints
DESCRIPTION: Introduces a suite of new API endpoints for managing dubbing resources, including adding languages, retrieving resources, and performing CRUD operations on dubbing segments (create, update, delete, dub, transcribe, translate). These endpoints enhance control over the dubbing workflow.

SOURCE: https://elevenlabs.io/docs/changelog/2025/3/3

LANGUAGE: APIDOC
CODE:
```
Dubbing Resource Management Endpoints:
  - Add Language: /docs/api-reference/dubbing/resources/add-language
  - Get Resource: /docs/api-reference/dubbing/resources/get-resource
  - Create Segment: /docs/api-reference/dubbing/resources/create-segment
  - Modify Segment: /docs/api-reference/dubbing/resources/update-segment
  - Remove Segment: /docs/api-reference/dubbing/resources/delete-segment
  - Dub Segment: /docs/api-reference/dubbing/resources/dub-segment
  - Transcribe Segment: /docs/api-reference/dubbing/resources/transcribe-segment
  - Translate Segment: /docs/api-reference/dubbing/resources/translate-segment
```

----------------------------------------

TITLE: New API Endpoint: Get Workspace Resource
DESCRIPTION: Introduces a new API endpoint to retrieve a workspace resource.

SOURCE: https://elevenlabs.io/docs/changelog/2025/3/17

LANGUAGE: APIDOC
CODE:
```
Endpoint: GET /docs/api-reference/workspace/get-resource
Description: Get workspace resource
```

----------------------------------------

TITLE: New API: Get Document RAG Indexes
DESCRIPTION: A new API endpoint has been added to retrieve information about RAG indexes. This endpoint provides details on all RAG indexes associated with a specific knowledge base document.

SOURCE: https://elevenlabs.io/docs/changelog

LANGUAGE: APIDOC
CODE:
```
Endpoint: /docs/api-reference/knowledge-base/get-document-rag-indexes
Method: GET
Description: Retrieves information about all RAG indexes of a knowledge base document.
```

----------------------------------------

TITLE: New Studio Project Management Endpoints
DESCRIPTION: Introduction of new endpoints for managing projects in Studio, replacing deprecated `/v1/projects/*` endpoints. This includes operations for listing, creating, retrieving, and deleting projects.

SOURCE: https://elevenlabs.io/docs/changelog/2025/2/10

LANGUAGE: APIDOC
CODE:
```
GET /v1/studio/projects: List all projects
```

LANGUAGE: APIDOC
CODE:
```
POST /v1/studio/projects: Create a project
```

LANGUAGE: APIDOC
CODE:
```
GET /v1/studio/projects/{project_id}: Get project details
```

LANGUAGE: APIDOC
CODE:
```
DELETE /v1/studio/projects/{project_id}: Delete a project
```

----------------------------------------

TITLE: API Reference: Update PVC Voice Endpoint
DESCRIPTION: This section provides a comprehensive API reference for the `POST /v1/voices/pvc/:voice_id` endpoint, used to update metadata for a Private Voice Clone (PVC) voice. It details the required path parameters, headers, the structure of the request body (including optional fields like name, language, description, and labels), and the expected successful response format, along with potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/voices/pvc/update

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/voices/pvc/:voice_id

Description: Update PVC voice metadata.

Path Parameters:
  voice_id: string (Required)
    Description: Voice ID to be used. Use https://api.elevenlabs.io/v1/voices to list available voices.

Headers:
  xi-api-key: string (Required)
    Description: Your ElevenLabs API key.

Request Body (JSON Object):
  name: string (Optional, Max 100 characters)
    Description: The name that identifies this voice. Displayed in the website dropdown.
  language: string (Optional)
    Description: Language used in the samples.
  description: string or null (Optional, Max 500 characters)
    Description: Description to use for the created voice.
  labels: map from strings to strings or null (Optional)
    Description: Serialized labels dictionary for the voice.

Responses:
  200 OK (Successful):
    Body (JSON Object):
      voice_id: string
        Description: The ID of the updated voice.
    Example:
      ```json
      {
        "voice_id": "b38kUX8pkfFy"
      }
      ```

  422 Unprocessable Entity Error:
    Description: Indicates an error with the request payload.
```

----------------------------------------

TITLE: Conversational AI Customizable Tool Timeouts
DESCRIPTION: This API documentation describes the ability to set specific timeout durations for individual tools within the Conversational AI agent's prompt configuration. This feature provides granular control over how long a tool is allowed to execute before timing out.

SOURCE: https://elevenlabs.io/docs/changelog/2025/5/19

LANGUAGE: APIDOC
CODE:
```
POST /agents/create
Request Body:
  conversation_config:
    agent:
      prompt:
        tools:
          client:
            response_timeout_secs: integer # Timeout duration in seconds for the tool
```

----------------------------------------

TITLE: API Reference: Get RAG Index for Knowledge Base Document
DESCRIPTION: This section provides the API specification for retrieving all RAG indexes associated with a specific document in the knowledge base. It outlines the HTTP method, endpoint path, required path parameters, and necessary headers for authentication.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/knowledge-base/get-document-rag-indexes

LANGUAGE: APIDOC
CODE:
```
GET /v1/convai/knowledge-base/:documentation_id/rag-index
Description: Provides information about all RAG indexes of the specified knowledgebase document.

Path Parameters:
  documentation_id: string (Required)
    Description: The id of a document from the knowledge base. This is returned on document addition.

Headers:
  xi-api-key: string (Required)

Responses:
  200 Retrieved:
    Description: Successful Response
    Body:
      indexes: list of objects
        Description: Show 5 properties
```

----------------------------------------

TITLE: ElevenLabs Studio Snapshot Retrieval Endpoints
DESCRIPTION: Introduces new API endpoints for retrieving snapshots of projects and chapters within the ElevenLabs Studio. These endpoints enable developers to access historical states of their studio content.

SOURCE: https://elevenlabs.io/docs/changelog/2025/3/3

LANGUAGE: APIDOC
CODE:
```
Studio Snapshot Retrieval Endpoints:
  - Get Project Snapshot: /docs/api-reference/studio/get-project-snapshot
  - Get Chapter Snapshot: /docs/api-reference/studio/get-chapter-snapshot
```

----------------------------------------

TITLE: API Reference: Get PVC Voice Sample Audio Endpoint
DESCRIPTION: This section provides comprehensive API documentation for the `GET /v1/voices/pvc/:voice_id/samples/:sample_id/audio` endpoint. It details the HTTP method, URL structure, required path parameters, required headers, optional query parameters, and the structure of a successful JSON response, including `audio_base_64`, `voice_id`, `sample_id`, `media_type`, and `duration_secs`. It also mentions the 422 Unprocessable Entity error.

SOURCE: https://elevenlabs.io/docs/api-reference/voices/pvc/samples/get-audio

LANGUAGE: APIDOC
CODE:
```
API Endpoint: GET /v1/voices/pvc/:voice_id/samples/:sample_id/audio
Description: Retrieve the first 30 seconds of voice sample audio with or without noise removal.

Path Parameters:
  voice_id (string, Required): Voice ID to be used, you can use https://api.elevenlabs.io/v1/voices to list all the available voices.
  sample_id (string, Required): Sample ID to be used

Headers:
  xi-api-key (string, Required)

Query Parameters:
  remove_background_noise (boolean, Optional, Default: false): If set will remove background noise for voice samples using our audio isolation model. If the samples do not include background noise, it can make the quality worse.

Responses:
  200 OK (Retrieved):
    Description: Successful Response
    Body (application/json):
      audio_base_64 (string): The base64 encoded audio.
      voice_id (string): The ID of the voice.
      sample_id (string): The ID of the sample.
      media_type (string): The media type of the audio.
      duration_secs (double or null): The duration of the audio in seconds.
    Example:
      {
        "audio_base_64": "audio_base_64",
        "voice_id": "DCwhRBWXzGAHq8TQ4Fs18",
        "sample_id": "DCwhRBWXzGAHq8TQ4Fs18",
        "media_type": "audio/mpeg",
        "duration_secs": 5
      }

  422 Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference: Get Dependent Agents for Knowledge Base Document
DESCRIPTION: This section provides the comprehensive API documentation for the `GET /v1/convai/knowledge-base/:documentation_id/dependent-agents` endpoint. It details the HTTP method, path parameters, headers, query parameters, successful response structure, and potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/knowledge-base/get-agents

LANGUAGE: APIDOC
CODE:
```
Endpoint: GET /v1/convai/knowledge-base/:documentation_id/dependent-agents

Path Parameters:
  documentation_id: string (Required)
    Description: The id of a document from the knowledge base. This is returned on document addition.

Headers:
  xi-api-key: string (Required)

Query Parameters:
  cursor: string or null (Optional)
    Description: Used for fetching next page. Cursor is returned in the response.
  page_size: integer (Optional)
    Description: How many documents to return at maximum. Can not exceed 100, defaults to 30.
    Constraints: >=1, <=100
    Default: 30

Responses:
  200 OK (Retrieved):
    Description: Successful Response
    Body:
      agents: list of objects
      has_more: boolean
      next_cursor: string or null
    Example:
      {
        "agents": [
          {
            "type": "unknown"
          }
        ],
        "has_more": true,
        "next_cursor": "foo"
      }
  422 Unprocessable Entity Error:
    Description: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs Dubbing Resource API Endpoint Specification
DESCRIPTION: This section provides the detailed specification for the GET /v1/dubbing/resource/:dubbing_id API endpoint. It outlines the HTTP method, the full URL, required path parameters, and necessary request headers for accessing a dubbing resource.

SOURCE: https://elevenlabs.io/docs/api-reference/dubbing/get-dubbing-resource

LANGUAGE: APIDOC
CODE:
```
Method: GET
URL: https://api.elevenlabs.io/v1/dubbing/resource/:dubbing_id

Path Parameters:
  dubbing_id: string (Required)
    Description: ID of the dubbing project.

Headers:
  xi-api-key: string (Required)
```

----------------------------------------

TITLE: Retrieve ElevenLabs Project Snapshot using TypeScript Client
DESCRIPTION: This TypeScript code snippet demonstrates how to use the official `@elevenlabs/elevenlabs-js` client library to fetch a specific project snapshot. It requires an API key for authentication and the unique identifiers for both the project and the snapshot.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/get-project-snapshot

LANGUAGE: TypeScript
CODE:
```
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient({ apiKey: "YOUR_API_KEY" });
await client.studio.projects.snapshots.get("21m00Tcm4TlvDq8ikWAM", "21m00Tcm4TlvDq8ikWAM");
```

----------------------------------------

TITLE: ElevenLabs Studio API: List Chapters JSON Response Schema
DESCRIPTION: This JSON snippet illustrates the expected successful response structure when calling the ElevenLabs Studio API to list project chapters. It details the `chapters` array, including properties like `chapter_id`, `name`, `state`, and conversion statistics.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/get-chapters

LANGUAGE: APIDOC
CODE:
```
{
"chapters": [
{
"chapter_id": "foo",
"name": "foo",
"can_be_downloaded": true,
"state": "default",
"last_conversion_date_unix": 42,
"conversion_progress": 42,
"statistics": {
"characters_unconverted": 42,
"characters_converted": 42,
"paragraphs_converted": 42,
"paragraphs_unconverted": 42
},
"last_conversion_error": "foo"
}
]
}
```

----------------------------------------

TITLE: ElevenLabs Agents API Query Parameters and Response
DESCRIPTION: Detailed documentation for querying agents, including available parameters, successful response structure, and common error codes. This covers pagination, search functionality, and the format of the returned agent list.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/agents/list

LANGUAGE: APIDOC
CODE:
```
Query parameters:
  cursor:
    type: string or null
    optional: true
    description: Used for fetching next page. Cursor is returned in the response.
  page_size:
    type: integer
    optional: true
    constraints: ">=1", "<=100"
    default: 30
    description: How many Agents to return at maximum. Can not exceed 100, defaults to 30.
  search:
    type: string or null
    optional: true
    description: Search by agents name.

Response:
  Successful Response:
    agents:
      type: list of objects
      description: A list of agents and their metadata
      properties: 5
    has_more:
      type: boolean
      description: Whether there are more agents to paginate through
    next_cursor:
      type: string or null
      description: The next cursor to paginate through the agents

Errors:
  422:
    description: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs Conversational AI Knowledge Base RAG Indexing Endpoint
DESCRIPTION: Adds a new API endpoint for computing RAG (Retrieval Augmented Generation) indexes for Knowledge Bases within the Conversational AI feature. This allows for programmatic management of knowledge base indexing.

SOURCE: https://elevenlabs.io/docs/changelog/2025/3/3

LANGUAGE: APIDOC
CODE:
```
Knowledge Base RAG Indexing Endpoint:
  - Compute RAG Index: /docs/conversational-ai/api-reference/knowledge-base/compute-rag-index
```

----------------------------------------

TITLE: Updated ElevenLabs Conversational AI API Endpoints
DESCRIPTION: Details changes to existing Conversational AI API endpoints, including the deprecation of a snake_case path in favor of a kebab-case equivalent, and significant response schema updates for phone number details to distinguish between Twilio and SIPTrunk providers.

SOURCE: https://elevenlabs.io/docs/changelog

LANGUAGE: APIDOC
CODE:
```
Updated Endpoints - Conversational AI:
- Agents & Conversations:
  - Deprecated: GET /v1/convai/conversation/get_signed_url (snake_case path)
  - New: GET /v1/convai/conversation/get-signed-url (kebab-case path)
- Phone Numbers:
  - Get Phone Number Details: GET /v1/convai/phone-numbers/{phone_number_id}
    Response Schema Update: Distinct Twilio and SIPTrunk provider details.
  - Update Phone Number: PATCH /v1/convai/phone-numbers/{phone_number_id}
    Response Schema Update: Similar for Twilio and SIPTrunk.
  - List Phone Numbers: GET /v1/convai/phone-numbers/
    Response Schema Update: List items updated for Twilio and SIPTrunk providers.
```

----------------------------------------

TITLE: ElevenLabs Shared Voices API Reference
DESCRIPTION: Detailed documentation for querying shared voices, including available query parameters, successful response structure, and common error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/voice-library/get-shared

LANGUAGE: APIDOC
CODE:
```
Query Parameters:
  page_size:
    Type: integer
    Optional: true
    Default: 30
    Description: How many shared voices to return at maximum. Can not exceed 100, defaults to 30.
  category:
    Type: enum
    Optional: true
    Allowed values: professional, famous, high_quality
    Description: Voice category used for filtering
  gender:
    Type: string or null
    Optional: true
    Description: Gender used for filtering
  age:
    Type: string or null
    Optional: true
    Description: Age used for filtering
  accent:
    Type: string or null
    Optional: true
    Description: Accent used for filtering
  language:
    Type: string or null
    Optional: true
    Description: Language used for filtering
  locale:
    Type: string or null
    Optional: true
    Description: Locale used for filtering
  search:
    Type: string or null
    Optional: true
    Description: Search term used for filtering
  use_cases:
    Type: list of strings or null
    Optional: true
    Description: Use-case used for filtering
  descriptives:
    Type: list of strings or null
    Optional: true
    Description: Search term used for filtering
  featured:
    Type: boolean
    Optional: true
    Default: false
    Description: Filter featured voices
  min_notice_period_days:
    Type: integer or null
    Optional: true
    Description: Filter voices with a minimum notice period of the given number of days.
  include_custom_rates:
    Type: boolean or null
    Optional: true
    Description: Include/exclude voices with custom rates
  include_live_moderated:
    Type: boolean or null
    Optional: true
    Description: Include/exclude voices that are live moderated
  reader_app_enabled:
    Type: boolean
    Optional: true
    Default: false
    Description: Filter voices that are enabled for the reader app
  owner_id:
    Type: string or null
    Optional: true
    Description: Filter voices by public owner ID
  sort:
    Type: string or null
    Optional: true
    Description: Sort criteria
  page:
    Type: integer
    Optional: true
    Default: 0

Response:
  Successful Response:
    voices:
      Type: list of objects
      Description: The list of shared voices (Note: 31 properties not detailed here)
    has_more:
      Type: boolean
      Description: Whether there are more shared voices in subsequent pages.
    last_sort_id:
      Type: string or null

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: List Workspace Secrets using ElevenLabs Python SDK
DESCRIPTION: This Python snippet demonstrates how to initialize the ElevenLabs client with an API key and then call the `conversational_ai.secrets.list()` method to retrieve all workspace secrets associated with the user's account.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/secrets/list

LANGUAGE: Python
CODE:
```
from elevenlabs import ElevenLabs

client = ElevenLabs(
    api_key="YOUR_API_KEY",
)
client.conversational_ai.secrets.list()
```

----------------------------------------

TITLE: Eleven Labs API: Delete Dubbing Endpoint Reference
DESCRIPTION: Comprehensive API documentation for the 'Delete dubbing' endpoint. It outlines the HTTP method, URL structure, required path parameters, necessary headers for authentication, and the expected successful response schema, including potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/dubbing/delete

LANGUAGE: APIDOC
CODE:
```
DELETE /v1/dubbing/:dubbing_id

Description: Deletes a dubbing project.

Path parameters:
  dubbing_id: string (Required)
    Description: ID of the dubbing project.

Headers:
  xi-api-key: string (Required)

Response (200 OK):
  Body:
    {
      "status": "ok"
    }
  Properties:
    status: string
      Description: The status of the dubbing project. If the request was successful, the status will be 'ok'. Otherwise an error message with status 500 will be returned.

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Update Project Management API: Get Project
DESCRIPTION: Updates the 'Get project' endpoint, making `last_modified_at`, `created_at`, and `project_name` nullable.

SOURCE: https://elevenlabs.io/docs/changelog/2025/3/17

LANGUAGE: APIDOC
CODE:
```
Endpoint: GET /docs/api-reference/studio/get-project
Changes:
  - Made nullable: `last_modified_at`, `created_at`, `project_name`
```

----------------------------------------

TITLE: ElevenLabs Dubbing Resource API Success Response JSON Example
DESCRIPTION: This JSON object provides an example of the data structure returned upon a successful retrieval of a dubbing resource from the ElevenLabs API. It illustrates the typical fields and nested objects, including `id`, `version`, language details, and various media asset references.

SOURCE: https://elevenlabs.io/docs/api-reference/dubbing/get-dubbing-resource

LANGUAGE: JSON
CODE:
```
{
  "id": "foo",
  "version": 42,
  "source_language": "foo",
  "target_languages": [
    "foo"
  ],
  "input": {
    "src": "foo",
    "content_type": "foo",
    "bucket_name": "foo",
    "random_path_slug": "foo",
    "duration_secs": 42,
    "is_audio": true,
    "url": "foo"
  },
  "background": {
    "src": "foo",
    "content_type": "foo",
    "bucket_name": "foo",
    "random_path_slug": "foo",
    "duration_secs": 42,
    "is_audio": true,
    "url": "foo"
  },
  "foreground": {
    "src": "foo",
    "content_type": "foo",
    "bucket_name": "foo",
    "random_path_slug": "foo",
    "duration_secs": 42,
    "is_audio": true,
    "url": "foo"
  },
  "speaker_tracks": {},
  "speaker_segments": {},
  "renders": {}
}
```

----------------------------------------

TITLE: Update ElevenLabs Audio Native Project using TypeScript Client
DESCRIPTION: This code snippet demonstrates how to update an Audio Native project using the ElevenLabs TypeScript client library. It initializes the client with an API key and then calls the `audioNative.update` method with the project ID and an empty object for the content, indicating that the content might be provided via multipart form data.

SOURCE: https://elevenlabs.io/docs/api-reference/audio-native/update

LANGUAGE: TypeScript
CODE:
```
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient({ apiKey: "YOUR_API_KEY" });
await client.audioNative.update("21m00Tcm4TlvDq8ikWAM", {});
```

----------------------------------------

TITLE: Create Knowledge Base Document from URL using ElevenLabs API
DESCRIPTION: This snippet details the API endpoint and parameters for creating a knowledge base document by scraping a given URL. It includes required headers, request body structure, and the expected successful response, along with a cURL example for demonstration.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/knowledge-base/create-from-url

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/convai/knowledge-base/url

Headers:
  xi-api-key: string (Required)

Request Body:
  url: string (Required) - URL to a page of documentation that the agent will have access to in order to interact with users.
  name: string or null (Optional) - A custom, human-readable name for the document.

Response (200 Successful):
  id: string
  name: string
```

LANGUAGE: cURL
CODE:
```
curl -X POST https://api.elevenlabs.io/v1/convai/knowledge-base/url \n-H "xi-api-key: xi-api-key" \n-H "Content-Type: application/json" \n-d '{\n"url": "foo"\n}'
```

----------------------------------------

TITLE: Workspace - New Webhook Management API Endpoint
DESCRIPTION: Documents the new API endpoint for retrieving all webhook configurations for the workspace, providing administrators with visibility into integration settings and optional usage information.

SOURCE: https://elevenlabs.io/docs/changelog

LANGUAGE: APIDOC
CODE:
```
Get workspace webhooks: Retrieve all webhook configurations for the workspace with optional usage information
```

----------------------------------------

TITLE: Python Client: List ElevenLabs Batch Calling Jobs
DESCRIPTION: Demonstrates how to use the ElevenLabs Python client library to programmatically list all batch calling jobs. It shows client initialization with an API key and the method call to fetch the jobs.

SOURCE: https://elevenlabs.io/docs/api-reference/batch-calling/list

LANGUAGE: Python
CODE:
```
from elevenlabs import ElevenLabs

client = ElevenLabs(
    api_key="YOUR_API_KEY",
)
client.conversational_ai.batch_calls.list()
```

----------------------------------------

TITLE: API Reference: Create Widget Avatar Endpoint
DESCRIPTION: Comprehensive API documentation for the POST /v1/convai/agents/:agent_id/avatar endpoint. This endpoint allows setting an avatar for an agent displayed in the widget, detailing required path parameters, headers, request body format, and expected successful and error responses.

SOURCE: https://elevenlabs.io/docs/api-reference/widget/create

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/convai/agents/:agent_id/avatar
Description: Sets the avatar for an agent displayed in the widget.

Path Parameters:
  agent_id: string (Required)
    Description: The id of an agent. This is returned on agent creation.

Headers:
  xi-api-key: string (Required)

Request Body (multipart/form-data):
  avatar_file: file (Required)
    Description: An image file to be used as the agent's avatar.

Responses:
  200 Successful:
    agent_id: string
    avatar_url: string or null
  422 Unprocessable Entity Error
```

----------------------------------------

TITLE: Sample JSON Response for Listing Eleven Labs Studio Projects
DESCRIPTION: Illustrates the expected JSON structure returned by the 'List Studio Projects' API endpoint. It shows an array of project objects, each containing various metadata fields such as project ID, name, creation date, and content details.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/get-projects

LANGUAGE: JSON
CODE:
```
{
"projects": [
{
"project_id": "aw1NgEzBg83R7vgmiJt6",
"name": "My Project",
"create_date_unix": 1714204800,
"default_title_voice_id": "JBFqnCBsd6RMkjVDRZzb",
"default_paragraph_voice_id": "JBFqnCBsd6RMkjVDRZzb",
"default_model_id": "eleven_multilingual_v2",
"can_be_downloaded": true,
"volume_normalization": true,
"state": "default",
"access_level": "viewer",
"quality_check_on": false,
"quality_check_on_when_bulk_convert": false,
"last_conversion_date_unix": 1714204800,
"title": "My Project",
"author": "John Doe",
"description": "This is a description of my project.",
"genres": [
"Novel",
"Short Story"
],
"cover_image_url": "https://example.com/cover.jpg",
"target_audience": "young adult",
"language": "en",
"content_type": "Novel",
"original_publication_date": "2025-01-01",
"mature_content": false,
"isbn_number": "978-90-274-3964-2",
"fiction": "fiction",
"creation_meta": {
"creation_progress": 0.5,
"status": "pending",
"type": "blank"
}
}
]
}
```

----------------------------------------

TITLE: API Reference: Create Workspace Secret Endpoint
DESCRIPTION: Detailed API documentation for the `POST /v1/convai/secrets` endpoint, which allows creating a new secret within an ElevenLabs workspace. It outlines the required headers, the structure of the request payload, the expected successful response, and potential error codes.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/workspace/secrets/create

LANGUAGE: APIDOC
CODE:
```
POST /v1/convai/secrets:
  Description: Create a new secret for the workspace.

  Headers:
    xi-api-key: string (Required)

  Request Body:
    type: string (Required)
    name: string (Required)
    value: string (Required)
    Example:
      {
        "type": "foo",
        "name": "foo",
        "value": "foo"
      }

  Response (200 Successful):
    type: string
    secret_id: string
    name: string
    Example:
      {
        "type": "foo",
        "secret_id": "foo",
        "name": "foo"
      }

  Errors:
    422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference for Start Speaker Separation Endpoint
DESCRIPTION: Detailed API documentation for the `POST /v1/voices/pvc/:voice_id/samples/:sample_id/separate-speakers` endpoint. This section outlines the required path parameters, headers, and the structure of the successful response, including potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/voices/pvc/samples/separate-speakers

LANGUAGE: APIDOC
CODE:
```
POST /v1/voices/pvc/:voice_id/samples/:sample_id/separate-speakers

Path parameters:
  voice_id: string (Required)
    Description: Voice ID to be used, you can use https://api.elevenlabs.io/v1/voices to list all the available voices.
  sample_id: string (Required)
    Description: Sample ID to be used

Headers:
  xi-api-key: string (Required)

Response (200 Successful):
  {
    "status": "ok"
  }
  status: string
    Description: The status of the start speaker seperation request. If the request was successful, the status will be 'ok'. Otherwise an error message with status 500 will be returned.

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API: Update Conversational AI Components for Agent Transfer
DESCRIPTION: Updates various components to support the new agent-agent transfer tool, enabling more complex conversational flows within the Conversational AI system.

SOURCE: https://elevenlabs.io/docs/changelog/2025/4/14

LANGUAGE: APIDOC
CODE:
```
Affected Area: Conversational AI Components
Change: Support for agent-agent transfer tool.
```

----------------------------------------

TITLE: New ElevenLabs API Endpoints
DESCRIPTION: Documentation for newly added API endpoints, including functionality to retrieve agent knowledge base size and calculate LLM token usage for agents and general models.

SOURCE: https://elevenlabs.io/docs/changelog

LANGUAGE: APIDOC
CODE:
```
Endpoint: GET /v1/agents/knowledge-base/size
  Description: Returns the number of pages in the agent’s knowledge base.

Endpoint: POST /v1/agents/llm-usage/calculate
  Description: Calculates expected number of LLM tokens needed for the specified agent.

Endpoint: POST /v1/llm-usage/calculate
  Description: Returns a list of LLM models and the expected cost for using them based on the provided values.
```

----------------------------------------

TITLE: Python Example: Retrieve Conversation Details
DESCRIPTION: Demonstrates how to use the ElevenLabs Python client library to fetch details for a specific conversation using its ID. This snippet initializes the client with an API key and then calls the `get` method on the `conversations` object within the `conversational_ai` module.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/conversations/get-conversation

LANGUAGE: Python
CODE:
```
from elevenlabs import ElevenLabs

client = ElevenLabs(
    api_key="YOUR_API_KEY",
)
client.conversational_ai.conversations.get(
    conversation_id="123",
)
```

----------------------------------------

TITLE: Install ElevenLabs Node.js Library
DESCRIPTION: This command installs the official Node.js library for the ElevenLabs API using npm, the Node.js package manager. It should be run in your Node.js project directory to add the library as a dependency.

SOURCE: https://elevenlabs.io/docs/api-reference

LANGUAGE: JavaScript
CODE:
```
npm install @elevenlabs/elevenlabs-js
```

----------------------------------------

TITLE: TypeScript: Get Knowledge Base Document Content Example
DESCRIPTION: Illustrates how to programmatically retrieve the content of a knowledge base document using the ElevenLabs JavaScript client library in TypeScript. It demonstrates client initialization with an API key and calling the specific method.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/knowledge-base/get-content

LANGUAGE: TypeScript
CODE:
```
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient({ apiKey: "YOUR_API_KEY" });
await client.conversationalAi.knowledgeBase.documents.getContent("21m00Tcm4TlvDq8ikWAM");
```

----------------------------------------

TITLE: Python Client: Get Signed URL for ElevenLabs Conversational AI
DESCRIPTION: Example Python code demonstrating how to use the ElevenLabs Python client library to programmatically retrieve a signed URL. This snippet shows the necessary imports, client initialization with an API key, and the method call with the required agent ID.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/conversations/get-signed-url

LANGUAGE: Python
CODE:
```
from elevenlabs import ElevenLabs

client = ElevenLabs(
    api_key="YOUR_API_KEY",
)
client.conversational_ai.conversations.get_signed_url(
    agent_id="21m00Tcm4TlvDq8ikWAM",
)
```

----------------------------------------

TITLE: ElevenLabs Conversational AI API Schema Changes
DESCRIPTION: Outlines significant schema additions for conversational AI, including detailed LLM usage and pricing information, `tool_latency_secs` in tool results, and `access_info` in agent details.

SOURCE: https://elevenlabs.io/docs/changelog/2025/4/28

LANGUAGE: APIDOC
CODE:
```
Schema Change: Conversational AI - Charging and History Models
Path: response.body.metadata.charging
Details: Added detailed LLM usage and pricing information.

Schema Change: Tool Result Schemas
Path: response.body.transcript.tool_results
Details: Added `tool_latency_secs`.

Schema Change: GET /v1/convai/agents/{agent_id} Response
Path: response.body
Details: Added `access_info`.
```

----------------------------------------

TITLE: ElevenLabs API: Get Dependent Agents Response Fields
DESCRIPTION: Describes the fields returned in a successful response from the 'Get Dependent Agents' endpoint, including the list of agents, a flag for more results, and a cursor for pagination.

SOURCE: https://elevenlabs.io/docs/api-reference/tools/get-dependent-agents

LANGUAGE: APIDOC
CODE:
```
### Response
Successful Response
agentslist of objects
Show 2 variants
has_moreboolean
next_cursorstring or null
```

----------------------------------------

TITLE: ElevenLabs Transcription API Synchronous Response
DESCRIPTION: Describes the structure of the synchronous response returned by the ElevenLabs transcription endpoint, including detected language, confidence, and transcribed text.

SOURCE: https://elevenlabs.io/docs/api-reference/speech-to-text/convert

LANGUAGE: APIDOC
CODE:
```
language_code: string
  Description: The detected language code (e.g. ‘eng’ for English).
language_probability: double
  Description: The confidence score of the language detection (0 to 1).
text: string
  Description: The raw text of the transcription.
words: list of objects
  Description: List of words with their timing information.
additional_formats: list of nullable objects or null
  Description: Requested additional formats of the transcript.
```

----------------------------------------

TITLE: Eleven Labs Conversational AI: Simulate Conversation API Reference
DESCRIPTION: Comprehensive API documentation for the `POST /v1/convai/agents/:agent_id/simulate-conversation` endpoint. It details path parameters, required headers, the structure of the request body, and the expected successful response body, including nested object properties and their types.

SOURCE: https://elevenlabs.io/docs/api-reference/agents/simulate-conversation

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/convai/agents/:agent_id/simulate-conversation

Path Parameters:
  agent_id:
    Type: string
    Required: true
    Description: The id of an agent. This is returned on agent creation.

Headers:
  xi-api-key:
    Type: string
    Required: true

Request Body:
  simulation_specification:
    Type: object
    Required: true
    Description: A specification detailing how the conversation should be simulated (Show 4 properties)
  extra_evaluation_criteria:
    Type: list of objects or null
    Optional: true
    Description: A list of evaluation criteria to test (Show 5 properties)

Response (200 Successful):
  simulated_conversation:
    Type: list of objects
    Description: (Show 13 properties)
  analysis:
    Type: object
    Description: (Show 4 properties)
```

----------------------------------------

TITLE: Example JSON Response for Get Dubbing Project
DESCRIPTION: This JSON snippet provides an example of the data structure returned by the ElevenLabs API when successfully retrieving metadata for a dubbing project. It illustrates typical fields such as `dubbing_id`, `name`, `status`, `target_languages`, and `media_metadata`.

SOURCE: https://elevenlabs.io/docs/api-reference/dubbing/get

LANGUAGE: JSON
CODE:
```
{
  "dubbing_id": "21m00Tcm4TlvDq8ikWAM",
  "name": "My Dubbing Project",
  "status": "dubbed",
  "target_languages": [
    "es",
    "fr",
    "de"
  ],
  "media_metadata": {
    "content_type": "video/mp4",
    "duration": 127.5
  }
}
```

----------------------------------------

TITLE: ElevenLabs Update Studio Project API Parameters
DESCRIPTION: Details the required parameters for the 'Update Studio Project' API endpoint. This includes the `project_id` as a path parameter and `xi-api-key` as a header, both essential for authentication and identifying the target project.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/edit-project

LANGUAGE: APIDOC
CODE:
```
Path parameters:
  project_id: string (Required)
    The ID of the project to be used. You can use the [List projects](/docs/api-reference/studio/get-projects) endpoint to list all the available projects.

Headers:
  xi-api-key: string (Required)
```

----------------------------------------

TITLE: Knowledge Base API: Force Delete and Usage Control
DESCRIPTION: Describes updates to the Knowledge Base API, including a new `force` parameter for document deletion and a change from `prompt_injectable` to `supported_usages` for better control over document usage modes. Also notes enhanced response for RAG index creation.

SOURCE: https://elevenlabs.io/docs/changelog

LANGUAGE: APIDOC
CODE:
```
Endpoint: /docs/api-reference/knowledge-base/delete
Method: DELETE
Description: Delete a knowledge base document.

Query Parameters:
  force: boolean (Added, allows deletion regardless of agent dependencies)

General Knowledge Base Document Changes:
  Property Change: 'prompt_injectable' replaced by 'supported_usages' for usage mode control.
  RAG Index Creation: Enhanced response model now includes usage information.
```

----------------------------------------

TITLE: Updated ElevenLabs API: Conversational AI Batch Calling
DESCRIPTION: Documentation for updated batch call responses, now including the `phone_provider` field.

SOURCE: https://elevenlabs.io/docs/changelog

LANGUAGE: APIDOC
CODE:
```
Batch Calling Response Fields:
  phone_provider: string
    Description: The phone provider used for the batch call.
    Default: "twilio"
```

----------------------------------------

TITLE: List Conversations API Endpoint and Usage
DESCRIPTION: This snippet provides comprehensive documentation for the Eleven Labs Conversational AI API endpoint to list conversations. It includes the API definition, a cURL example for making the request, and the expected JSON response structure.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/conversations/list

LANGUAGE: APIDOC
CODE:
```
Endpoint: GET /v1/convai/conversations
Full URL: https://api.elevenlabs.io/v1/convai/conversations
Description: Get all conversations of agents that user owns. With option to restrict to a specific agent.

Headers:
  xi-api-key: string (Required)
```

LANGUAGE: cURL
CODE:
```
curl https://api.elevenlabs.io/v1/convai/conversations \
-H "xi-api-key: xi-api-key"
```

LANGUAGE: APIDOC
CODE:
```
Response (200 Retrieved):
  conversations: array of objects
    agent_id: string
    conversation_id: string
    start_time_unix_secs: integer
    call_duration_secs: integer
    message_count: integer
    status: string (e.g., "initiated")
    call_successful: string (e.g., "success")
    agent_name: string
  has_more: boolean
  next_cursor: string
```

----------------------------------------

TITLE: API Reference for Updating Knowledge Base Document Endpoint
DESCRIPTION: Comprehensive API documentation for the PATCH endpoint used to update a knowledge base document. This section details the endpoint path, required path parameters, header authentication, request body schema, and possible successful and error responses.

SOURCE: https://elevenlabs.io/docs/api-reference/knowledge-base/update-knowledge-base-document

LANGUAGE: APIDOC
CODE:
```
Endpoint:
  PATCH /v1/convai/knowledge-base/:documentation_id
  Description: Update the name of a document.

Path Parameters:
  documentation_id: string (Required)
    Description: The id of a document from the knowledge base. This is returned on document addition.

Headers:
  xi-api-key: string (Required)

Request Body:
  name: string (Required)
    Constraints: >=1 character
    Description: A custom, human-readable name for the document.

Responses:
  200 OK:
    Description: Updated
    Models: GetKnowledgeBaseURLResponseModel (object, 8 properties)
            GetKnowledgeBaseFileResponseModel (object, 7 properties)
            GetKnowledgeBaseTextResponseModel (object, 7 properties)
  422 Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs Conversational AI Agent Share Link API Reference
DESCRIPTION: Comprehensive API documentation for the `GET /v1/convai/agents/:agent_id/link` endpoint. This endpoint allows retrieval of the current share link used to share an agent with others, detailing path parameters, required headers, successful response structure, and potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/agents/get-link

LANGUAGE: APIDOC
CODE:
```
Endpoint: GET /v1/convai/agents/:agent_id/link
Description: Get the current link used to share the agent with others.

Path Parameters:
  agent_id: string (Required)
    Description: The ID of an agent. This is returned on agent creation.

Headers:
  xi-api-key: string (Required)

Responses:
  200 OK (Successful Response):
    agent_id: string
      Description: The ID of the agent.
    token: object or null
      Description: The token data for the agent. (Show 5 properties)
  422 Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference: Unshare Workspace Resource Endpoint
DESCRIPTION: Detailed API documentation for the POST /v1/workspace/resources/:resource_id/unshare endpoint. This section outlines the endpoint's purpose, path parameters, required headers, the structure of the request body, and possible responses, including error codes. It specifies how to target different entities like users, groups, or API keys for unsharing.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/resources/unshare

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/workspace/resources/:resource_id/unshare
Description: Removes any existing role on a workspace resource from a user, service account, group or workspace api key. To target a user or service account, pass only the user email. The user must be in your workspace. To target a group, pass only the group id. To target a workspace api key, pass the api key id. The resource will be unshared from the service account associated with the api key. You must have admin access to the resource to unshare it. You cannot remove permissions from the user who created the resource.

Path Parameters:
  resource_id:
    Type: string
    Required: true
    Description: The ID of the target resource.

Headers:
  xi-api-key:
    Type: string
    Required: true

Request Body:
  Type: object
  Properties:
    resource_type:
      Type: enum
      Required: true
      Description: Resource type of the target resource. (Show 15 enum values)
    user_email:
      Type: string or null
      Optional: true
      Description: The email of the user or service account.
    group_id:
      Type: string or null
      Optional: true
      Description: The ID of the target group. To target the permissions principals have by default on this resource, use the value 'default'.
    workspace_api_key_id:
      Type: string or null
      Optional: true
      Description: The ID of the target workspace API key. This isn't the same as the key itself that would you pass in the header for authentication. Workspace admins can find this in the workspace settings UI.

Responses:
  200: Successful Response
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference: Create Knowledge Base Document from File
DESCRIPTION: Detailed API specification for creating a knowledge base document by uploading a file. This POST endpoint requires a multipart form with the file content and optionally a custom name. It also specifies required headers and the structure of a successful response.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/knowledge-base/create-from-file

LANGUAGE: APIDOC
CODE:
```
Method: POST
URL: https://api.elevenlabs.io/v1/convai/knowledge-base/file

Headers:
  xi-api-key: string (Required)

Request Body (multipart/form-data):
  file: file (Required)
    Description: Documentation that the agent will have access to in order to interact with users.
  name: string or null (Optional)
    Constraints: >=1 character
    Description: A custom, human-readable name for the document.

Response (200 Successful):
  id: string
  name: string

Response Example (200 OK):
{
  "id": "foo",
  "name": "foo"
}
```

----------------------------------------

TITLE: API Reference: Update Speaker Endpoint for Dubbing Resources
DESCRIPTION: This section provides the detailed API specification for updating speaker metadata within a dubbing project. It outlines the PATCH method, required path parameters, headers, and the structure of the request body for modifying voice and language settings. It also describes the expected successful response and potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/dubbing/resources/update-speaker

LANGUAGE: APIDOC
CODE:
```
PATCH /v1/dubbing/resource/:dubbing_id/speaker/:speaker_id

Description: Amend the metadata associated with a speaker, such as their voice. Both voice cloning and using voices from the ElevenLabs library are supported.

Path Parameters:
  dubbing_id: string (Required) - ID of the dubbing project.
  speaker_id: string (Required) - ID of the speaker.

Headers:
  xi-api-key: string (Required)

Request Body (application/json):
  voice_id: string or null (Optional) - Either the identifier of a voice from the ElevenLabs voice library, or one of ['track-clone', 'clip-clone'].
  languages: list of strings or null (Optional) - Languages to apply these changes to. If empty, will apply to all languages.

Responses:
  200 OK:
    Description: Updated
    Body:
      version: integer
  422 Unprocessable Entity Error
```

----------------------------------------

TITLE: Update Studio Project Endpoints
DESCRIPTION: Details changes to ElevenLabs Studio project API endpoints, including the addition of a new `source_type` property and the deprecation of `quality_check_on` and `quality_check_on_when_bulk_convert` properties. These updates affect project retrieval, creation, and content management.

SOURCE: https://elevenlabs.io/docs/changelog/2025/3/10

LANGUAGE: APIDOC
CODE:
```
Studio Project Endpoints:
  - GET /docs/api-reference/studio/get-projects
  - GET /docs/api-reference/studio/get-project
  - POST /docs/api-reference/studio/add-project
  - PUT /docs/api-reference/studio/update-content
  - POST /docs/api-reference/studio/create-podcast
Changes:
  - Added property: `source_type`
  - Deprecated properties: `quality_check_on`, `quality_check_on_when_bulk_convert`
```

----------------------------------------

TITLE: Example JSON Response for Listing Workspace Secrets
DESCRIPTION: This JSON example illustrates the expected data structure returned by the 'Get secrets' API endpoint upon a successful request. It shows an array of secret objects, each containing type, ID, name, and a detailed 'used_by' object indicating where the secret is utilized within the ElevenLabs platform.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/secrets/list

LANGUAGE: JSON
CODE:
```
{
  "secrets": [
    {
      "type": "foo",
      "secret_id": "foo",
      "name": "foo",
      "used_by": {
        "tools": [
          {
            "type": "unknown"
          }
        ],
        "agents": [
          {
            "type": "unknown"
          }
        ],
        "others": [
          "conversation_initiation_webhook"
        ],
        "phone_numbers": [
          {
            "phone_number_id": "foo",
            "phone_number": "foo",
            "label": "foo",
            "provider": "twilio"
          }
        ]
      }
    }
  ]
}
```

----------------------------------------

TITLE: ElevenLabs Conversational AI Agent WebSocket API Reference: Query Parameters
DESCRIPTION: Defines the query parameters that can be used when establishing the WebSocket connection.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/conversational-ai/websocket

LANGUAGE: APIDOC
CODE:
```
agent_id: any (Required)
  Description: The unique identifier for the voice to use in the TTS process.
```

----------------------------------------

TITLE: ElevenLabs Studio API: Callback Message Structures
DESCRIPTION: Details the JSON payload structures for the `callback_url` parameter, indicating project or chapter conversion status (success or error).

SOURCE: https://elevenlabs.io/docs/api-reference/studio/create-podcast

LANGUAGE: APIDOC
CODE:
```
1. When project was converted successfully:
   {
     "type": "project_conversion_status",
     "event_timestamp": 1234567890,
     "data": {
       "request_id": "1234567890",
       "project_id": "21m00Tcm4TlvDq8ikWAM",
       "conversion_status": "success",
       "project_snapshot_id": "22m00Tcm4TlvDq8ikMAT",
       "error_details": null
     }
   }
2. When project conversion failed:
   {
     "type": "project_conversion_status",
     "event_timestamp": 1234567890,
     "data": {
       "request_id": "1234567890",
       "project_id": "21m00Tcm4TlvDq8ikWAM",
       "conversion_status": "error",
       "project_snapshot_id": null,
       "error_details": "Error details if conversion failed"
     }
   }
3. When chapter was converted successfully:
   {
     "type": "chapter_conversion_status",
     "event_timestamp": 1234567890,
     "data": {
       "request_id": "1234567890",
       "project_id": "21m00Tcm4TlvDq8ikWAM",
       "chapter_id": "22m00Tcm4TlvDq8ikMAT",
       "conversion_status": "success",
       "chapter_snapshot_id": "23m00Tcm4TlvDq8ikMAV",
       "error_details": null
     }
   }
4. When chapter conversion failed:
   {
     "type": "chapter_conversion_status",
     "event_timestamp": 1234567890,
     "data": {
       "request_id": "1234567890",
       "project_id": "21m00Tcm4TlvDq8ikWAM",
       "chapter_id": "22m00Tcm4TlvDq8ikMAT",
       "conversion_status": "error",
       "chapter_snapshot_id": null,
       "error_details": "Error details if conversion failed"
     }
   }
```

----------------------------------------

TITLE: Update Conversational AI API: Add to Knowledge Base
DESCRIPTION: Updates the 'Add to knowledge base' endpoint, making `document_name` nullable.

SOURCE: https://elevenlabs.io/docs/changelog/2025/3/17

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /docs/api-reference/knowledge-base/create-from-url
Changes:
  - Made nullable: `document_name`
```

----------------------------------------

TITLE: API Reference: Delete Studio Chapter Endpoint Details
DESCRIPTION: Comprehensive API documentation for the 'Delete Chapter' endpoint, detailing path parameters (`project_id`, `chapter_id`), required headers (`xi-api-key`), and the structure of the successful response, including the `status` field. It also mentions the 422 error.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/delete-chapter

LANGUAGE: APIDOC
CODE:
```
Path parameters:
  project_id: string (Required)
    Description: The ID of the project to be used. You can use the [List projects] endpoint to list all the available projects.
  chapter_id: string (Required)
    Description: The ID of the chapter to be used. You can use the [List project chapters] endpoint to list all the available chapters.

Headers:
  xi-api-key: string (Required)

Response:
  Successful Response:
    status: string
      Description: The status of the studio chapter deletion request. If the request was successful, the status will be 'ok'. Otherwise an error message with status 500 will be returned.

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: New API: Get RAG Index Overview
DESCRIPTION: A new API endpoint provides an overview of RAG indexes used by knowledge base documents. This endpoint returns the total size and other relevant information about the RAG indexes.

SOURCE: https://elevenlabs.io/docs/changelog

LANGUAGE: APIDOC
CODE:
```
Endpoint: /docs/api-reference/knowledge-base/rag-index-overview
Method: GET
Description: Retrieves total size and information of RAG indexes used by knowledge base documents.
```

----------------------------------------

TITLE: API: Add Render Dub Endpoint
DESCRIPTION: Introduces a new API endpoint to regenerate audio or video renders for specific languages within a dubbing project, automatically handling missing transcriptions or translations. This enhances flexibility for dubbing projects.

SOURCE: https://elevenlabs.io/docs/changelog/2025/4/14

LANGUAGE: APIDOC
CODE:
```
New Endpoint: /docs/api-reference/dubbing/render-dub
Description: Regenerate dubs for a specific language.
```

----------------------------------------

TITLE: General Product Feature Enhancements
DESCRIPTION: Summarizes significant new features and capabilities introduced across different product areas, such as dynamic variables in simulated conversations, MCP server integration, burst pricing, Studio project initialization with JSON, and workspace-level webhook management.

SOURCE: https://elevenlabs.io/docs/changelog

LANGUAGE: APIDOC
CODE:
```
Conversational AI - Dynamic variables in simulated conversations: Added support for dynamic variable population in simulated conversations, enabling more flexible and context-aware conversation testing scenarios.
Conversational AI - MCP server integration: Introduced comprehensive support for Model Context Protocol (MCP) servers, allowing agents to connect to external tools and services through standardized protocols with configurable approval policies.
Conversational AI - Burst pricing for extra concurrency: Added bursting capability for workspace call limits, automatically allowing up to 3x the configured concurrency limit during peak usage for overflow capacity.
Studio - JSON content initialization: Added support for initializing Studio projects with structured JSON content through the `from_content_json` parameter, enabling programmatic project creation with predefined chapters, blocks, and voice configurations.
Workspaces - Webhook management: Introduced workspace-level webhook management capabilities, allowing administrators to view, configure, and monitor webhook integrations across the entire workspace with detailed usage tracking and failure diagnostics.
```

----------------------------------------

TITLE: TypeScript: List ElevenLabs Studio Project Snapshots using SDK
DESCRIPTION: This code snippet demonstrates how to use the ElevenLabs JavaScript/TypeScript SDK to programmatically retrieve a list of snapshots for a specified Studio project. It requires an API key for authentication and the project ID as an input.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/get-snapshots

LANGUAGE: TypeScript
CODE:
```
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient({ apiKey: "YOUR_API_KEY" });
await client.studio.projects.snapshots.list("21m00Tcm4TlvDq8ikWAM");
```

----------------------------------------

TITLE: ElevenLabs API Reference: Design a Voice Endpoint
DESCRIPTION: Comprehensive API documentation for the POST /v1/text-to-voice/design endpoint. It details the request method, full URL, required headers, optional query parameters with their types and descriptions, and the structure of a successful 200 OK JSON response, including voice preview details.

SOURCE: https://elevenlabs.io/docs/api-reference/text-to-voice

LANGUAGE: APIDOC
CODE:
```
Endpoint: Design a voice
Method: POST
URL: https://api.elevenlabs.io/v1/text-to-voice/design

Headers:
  xi-api-key: string (Required)

Query parameters:
  output_format: enum (Optional)
    Defaults to `mp3_44100_192`
    Description: Output format of the generated audio. Formatted as codec_sample_rate_bitrate. So an mp3 with 22.05kHz sample rate at 32kbs is represented as mp3_22050_32. MP3 with 192kbps bitrate requires you to be subscribed to Creator tier or above. PCM with 44.1kHz sample rate requires you to be subscribed to Pro tier or above. Note that the μ-law format (sometimes written mu-law, often approximated as u-law) is commonly used for Twilio audio inputs.

Responses:
  200 Successful:
    {
      "previews": [
        {
          "audio_base_64": "foo",
          "generated_voice_id": "foo",
          "media_type": "foo",
          "duration_secs": 42
        }
      ],
      "text": "foo"
    }
```

----------------------------------------

TITLE: Update Usage Metrics Endpoint with Aggregation and Breakdowns
DESCRIPTION: The `Get Usage Metrics` endpoint (`GET /v1/usage/character-stats`) has been enhanced with new optional query parameters. `aggregation_interval` allows controlling the aggregation period for character usage, while `metric` enables selecting various metric breakdowns like `minutes_used`, `request_count`, `ttfb_avg`, and `ttfb_p95`. Additionally, filtering and breakdown by `request_queue` is now supported.

SOURCE: https://elevenlabs.io/docs/changelog

LANGUAGE: APIDOC
CODE:
```
Endpoint: GET /v1/usage/character-stats
Description: Updated usage metrics endpoint with new query parameters.
Parameters:
  - aggregation_interval (optional): Controls interval for character usage aggregation (hour, day, week, month, cumulative).
  - metric (optional): Selectable metric breakdowns (minutes_used, request_count, ttfb_avg, ttfb_p95).
  - request_queue (optional): Breakdown and filter by request_queue.
```

----------------------------------------

TITLE: ElevenLabs API Reference: Create Pronunciation Dictionary from File
DESCRIPTION: This API documentation details the POST endpoint for creating a new pronunciation dictionary from a lexicon .PLS file. It specifies the endpoint URL, required headers, multipart form request parameters (name, file, description, workspace_access), and the structure of a successful JSON response, including dictionary ID, name, creation time, and version details. It also mentions a 422 Unprocessable Entity error.

SOURCE: https://elevenlabs.io/docs/api-reference/pronunciation-dictionary/add-from-file

LANGUAGE: APIDOC
CODE:
```
POST /v1/pronunciation-dictionaries/add-from-file

Headers:
  xi-api-key: string (Required)

Request (multipart/form-data):
  name: string (Required) - The name of the pronunciation dictionary, used for identification only.
  file: file (Optional) - A lexicon .pls file which we will use to initialize the project with.
  description: string or null (Optional) - A description of the pronunciation dictionary, used for identification only.
  workspace_access: enum or null (Optional) - Should be one of 'admin', 'editor' or 'viewer'. If not provided, defaults to no access.
    Allowed values: 'admin', 'editor', 'viewer'

Response (200 Successful):
  id: string - The ID of the created pronunciation dictionary.
  name: string - The name of the created pronunciation dictionary.
  created_by: string - The user ID of the creator of the pronunciation dictionary.
  creation_time_unix: integer - The creation time of the pronunciation dictionary in Unix timestamp.
  version_id: string - The ID of the created pronunciation dictionary version.
  version_rules_num: integer - The number of rules in the version of the pronunciation dictionary.
  permission_on_resource: enum or null - The permission on the resource of the pronunciation dictionary.
    Allowed values: 'admin', 'editor', 'viewer'
  description: string or null - The description of the pronunciation dictionary.

  Example Response Body:
  {
    "id": "5xM3yVvZQKV0EfqQpLrJ",
    "name": "My Dictionary",
    "created_by": "ar6633Es2kUjFXBdR1iVc9ztsXl1",
    "creation_time_unix": 1714156800,
    "version_id": "5xM3yVvZQKV0EfqQpLrJ",
    "version_rules_num": 5,
    "permission_on_resource": "admin",
    "description": "This is a test dictionary"
  }

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs Conversational AI Get Phone Number API Response Schema
DESCRIPTION: This JSON schema illustrates the expected successful response structure when retrieving phone number details via the API. It shows the properties returned for a phone number object.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/phone-numbers/get

LANGUAGE: APIDOC
CODE:
```
{
  "phone_number": "foo",
  "label": "foo",
  "phone_number_id": "foo",
  "assigned_agent": {
    "agent_id": "foo",
    "agent_name": "foo"
  },
  "provider": "twilio"
}
```

----------------------------------------

TITLE: API Reference for Updating ElevenLabs Audio Native Project Content
DESCRIPTION: This section provides comprehensive API documentation for the `POST /v1/audio-native/:project_id/content` endpoint, used to update content for a specific AudioNative Project. It details the required path parameters, headers, request body fields (including file upload and conversion options), and the structure of the successful response, along with potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/audio-native/update-content

LANGUAGE: APIDOC
CODE:
```
Endpoint:
  POST https://api.elevenlabs.io/v1/audio-native/:project_id/content

Path Parameters:
  project_id: string (Required)
    The ID of the project to be used. You can use the [List projects] endpoint to list all the available projects.

Headers:
  xi-api-key: string (Required)

Request Body (multipart/form-data):
  file: file (Optional)
    Either txt or HTML input file containing the article content. HTML should be formatted as follows ‘<html><body><div><p>Your content</p><h5>More of your content</h5><p>Some more of your content</p></div></body></html>’
  auto_convert: boolean (Optional, Defaults to false)
    Whether to auto convert the project to audio or not.
  auto_publish: boolean (Optional, Defaults to false)
    Whether to auto publish the new project snapshot after it's converted.

Response (200 Successful):
  project_id: string
    The ID of the project.
  converting: boolean
    Whether the project is currently being converted.
  publishing: boolean
    Whether the project is currently being published.
  html_snippet: string
    The HTML snippet to embed the Audio Native player.

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference: Get Agent Widget Configuration Parameters and Response
DESCRIPTION: Detailed API documentation for the 'Get widget' endpoint, outlining required path parameters, authentication headers, optional query parameters, and the structure of the successful response, including the `agent_id` and `widget_config` object, as well as potential error responses.

SOURCE: https://elevenlabs.io/docs/api-reference/widget/get

LANGUAGE: APIDOC
CODE:
```
Endpoint: GET /v1/convai/agents/:agent_id/widget

Path Parameters:
  agent_id (string, Required): The id of an agent. This is returned on agent creation.

Headers:
  xi-api-key (string, Required)

Query Parameters:
  conversation_signature (string or null, Optional): An expiring token that enables a websocket conversation to start. These can be generated for an agent using the /v1/convai/conversation/get-signed-url endpoint

Responses:
  200 OK (Successful Response):
    agent_id (string)
    widget_config (object) - Show 38 properties
  422 Unprocessable Entity Error
```

----------------------------------------

TITLE: Conversational AI Endpoint Updates
DESCRIPTION: Details on modifications to existing Conversational AI endpoints, including updates to agent configuration and tool management parameters.

SOURCE: https://elevenlabs.io/docs/changelog/2025/2/10

LANGUAGE: APIDOC
CODE:
```
GET /v1/convai/agents/{agent_id} - Updated conversation configuration and agent properties
```

LANGUAGE: APIDOC
CODE:
```
PATCH /v1/convai/agents/{agent_id} - Added `use_tool_ids` parameter for tool management
```

LANGUAGE: APIDOC
CODE:
```
POST /v1/convai/agents/create - Added tool integration via `use_tool_ids`
```

----------------------------------------

TITLE: Pronunciation Dictionary API Endpoint Changes
DESCRIPTION: This section outlines the recent modifications to the ElevenLabs Pronunciation Dictionary API, detailing new query parameters for retrieval and additional response properties for tracking rule versions across various dictionary management operations.

SOURCE: https://elevenlabs.io/docs/changelog/2025/3/24

LANGUAGE: APIDOC
CODE:
```
Pronunciation Dictionary API Updates:
- Get all pronunciation dictionaries:
  - Added query parameters: `sort`, `sort_direction`
  - Added response properties: `latest_version_rules_num`, `integer`
- Get pronunciation dictionary:
  - Added response properties: `latest_version_rules_num`, `integer`
- Add from file:
  - Added response property: `version_rules_num` (for tracking rules quantity)
- Add rules:
  - Added response property: `version_rules_num` (for rules tracking)
- Remove rules:
  - Added response property: `version_rules_num` (for rules tracking)
```

----------------------------------------

TITLE: Update Project Management API: Create Podcast
DESCRIPTION: Updates the 'Create podcast' endpoint, making `title`, `description`, and `author` nullable.

SOURCE: https://elevenlabs.io/docs/changelog/2025/3/17

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /docs/api-reference/studio/create-podcast
Changes:
  - Made nullable: `title`, `description`, `author`
```

----------------------------------------

TITLE: Registering a Python Client Tool and Initializing Conversation
DESCRIPTION: This snippet demonstrates how to define a Python function (`get_customer_details`) that acts as a client tool. It shows the process of registering this function with the `ClientTools` instance and then initializing an `ElevenLabs Conversation` object, passing the registered client tools. The agent will execute `get_customer_details` on the client and use its return value in the conversation context.

SOURCE: https://elevenlabs.io/docs/conversational-ai/customization/tools/client-tools

LANGUAGE: Python
CODE:
```
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

----------------------------------------

TITLE: API Reference: Add Member to Workspace Group
DESCRIPTION: Detailed API documentation for the endpoint that adds a member to a specified user group within an Eleven Labs workspace. It outlines the HTTP method, URL structure, required path parameters, headers, request body schema, successful response format, and potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/groups/members/add

LANGUAGE: APIDOC
CODE:
```
POST /v1/workspace/groups/:group_id/members

Description: Adds a member of your workspace to the specified group. This endpoint may only be called by workspace administrators.

Path Parameters:
  group_id: string (Required)
    Description: The ID of the target group.

Headers:
  xi-api-key: string (Required)

Request Body:
  Type: object
  Properties:
    email: string (Required)
      Description: The email of the target workspace member.

Response (200 Successful):
  Type: object
  Properties:
    status: string
      Description: The status of the workspace group member addition request. If the request was successful, the status will be 'ok'. Otherwise an error message with status 500 will be returned.

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs API Reference: Create Speech Endpoint
DESCRIPTION: This section details the 'Create speech' API endpoint, which converts text into audio. It outlines the HTTP method, URL, required path and header parameters, and optional query parameters, including their types, descriptions, and default values.

SOURCE: https://elevenlabs.io/docs/api-reference/text-to-speech

LANGUAGE: APIDOC
CODE:
```
Endpoint: Create speech
Method: POST
URL: https://api.elevenlabs.io/v1/text-to-speech/:voice_id

Path Parameters:
  voice_id:
    Type: string
    Required: Yes
    Description: ID of the voice to be used. Use the Get voices endpoint list all the available voices.

Headers:
  xi-api-key:
    Type: string
    Required: Yes

Query Parameters:
  enable_logging:
    Type: boolean
    Optional: Yes
    Default: true
    Description: When enable_logging is set to false zero retention mode will be used for the request. This will mean history features are unavailable for this request, including request stitching. Zero retention mode may only be used by enterprise customers.
  optimize_streaming_latency:
    Type: integer or null
    Optional: Yes
    Deprecated: Yes
    Default: None
    Description: You can turn on latency optimizations at some cost of quality. The best possible final latency varies by model. Possible values: 0 - default mode (no latency optimizations), 1 - normal latency optimizations (about 50% of possible latency improvement of option 3), 2 - strong latency optimizations (about 75% of possible latency improvement of option 3), 3 - max latency optimizations, 4 - max latency optimizations, but also with text normalizer turned off for even more latency savings (best latency, but can mispronounce eg numbers and dates).
  output_format:
    Type: enum
    Optional: Yes
    Default: mp3_44100_128
    Description: Output format of the generated audio. Formatted as codec_sample_rate_bitrate. So an mp3 with 22.05kHz sample rate at 32kbs is represented as mp3_22050_32. MP3 with 192kbps bitrate requires you to be subscribed to Creator tier or above. PCM with 44.1kHz sample rate requires you to be subscribed to Pro tier or above. Note that the μ-law format (sometimes written mu-law, often approximated as u-law) is commonly used for Twilio audio inputs.
```

----------------------------------------

TITLE: Regenerate Dub Segments using cURL
DESCRIPTION: This cURL command demonstrates how to make a POST request to the ElevenLabs API's 'Dub segment' endpoint. It shows how to specify the API key in the header and provide segments and languages in the JSON request body to regenerate dubs for a given dubbing resource.

SOURCE: https://elevenlabs.io/docs/api-reference/dubbing/resources/dub-segment

LANGUAGE: cURL
CODE:
```
curl -X POST https://api.elevenlabs.io/v1/dubbing/resource/dubbing_id/dub \n-H "xi-api-key: xi-api-key" \n-H "Content-Type: application/json" \n-d '{\n"segments": [\n"foo"\n],\n"languages": [\n"foo"\n]\n}'
```

----------------------------------------

TITLE: API Reference: Update Knowledge Base Document (PATCH)
DESCRIPTION: Comprehensive API documentation for the `PATCH /v1/convai/knowledge-base/:documentation_id` endpoint, used to update the name of a document within an ElevenLabs knowledge base. It outlines the required path and header parameters, the request body schema, successful response structures, and potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/knowledge-base/update

LANGUAGE: APIDOC
CODE:
```
Endpoint: PATCH /v1/convai/knowledge-base/:documentation_id
Description: Update the name of a document

Path Parameters:
  documentation_id: string (Required)
    Description: The id of a document from the knowledge base. This is returned on document addition.

Headers:
  xi-api-key: string (Required)

Request Body:
  Type: object
  Properties:
    name: string (Required)
      Description: A custom, human-readable name for the document.
      Constraints: >=1 character

Responses:
  200 OK:
    Description: Updated successfully.
    Body:
      Type: object (one of the following models)
      - GetKnowledgeBaseURLResponseModel (Show 8 properties)
      - GetKnowledgeBaseFileResponseModel (Show 7 properties)
      - GetKnowledgeBaseTextResponseModel (Show 7 properties)
    Example:
      {
        "id": "foo",
        "name": "foo",
        "metadata": {
          "created_at_unix_secs": 42,
          "last_updated_at_unix_secs": 42,
          "size_bytes": 42
        },
        "supported_usages": [
          "prompt"
        ],
        "access_info": {
          "is_creator": true,
          "creator_name": "foo",
          "creator_email": "foo",
          "role": "admin"
        },
        "extracted_inner_html": "foo",
        "type": "foo",
        "url": "foo"
      }

  422 Unprocessable Entity Error:
    Description: The request was well-formed but could not be processed.
```

----------------------------------------

TITLE: Conversational AI Schema Enhancements
DESCRIPTION: Several schema updates have been made for Conversational AI. Detailed LLM usage and pricing information is now included in conversation charging and history models. `tool_latency_secs` has been added to tool result schemas, and `access_info` is now part of the response for `GET /v1/convai/agents/{agent_id}`.

SOURCE: https://elevenlabs.io/docs/changelog

LANGUAGE: APIDOC
CODE:
```
Schema Changes:
  - LLM usage and pricing information added to conversation charging and history models (metadata.charging).
  - tool_latency_secs added to tool result schemas (transcript.tool_results.tool_latency_secs).
  - access_info added to GET /v1/convai/agents/{agent_id} response body.
```

----------------------------------------

TITLE: Manage Conversational AI Dashboard Settings via API
DESCRIPTION: Introduces new API endpoints to retrieve and update custom chart configurations for the Conversational AI Dashboard, allowing for extended visualization of evaluation criteria over time.

SOURCE: https://elevenlabs.io/docs/changelog/2025/4/28

LANGUAGE: APIDOC
CODE:
```
API Endpoints for Conversational AI Dashboard Settings:

GET /docs/api-reference/workspace/dashboard/get
  Description: Retrieves custom chart configurations for the ConvAI dashboard.

PATCH /docs/api-reference/workspace/dashboard/update
  Description: Updates custom chart configurations for the ConvAI dashboard.
```

----------------------------------------

TITLE: Deprecated ElevenLabs Studio API Endpoints
DESCRIPTION: Documents the deprecation of all `/v1/projects/*` endpoints, including operations on projects, chapters, snapshots, and content, in favor of new `/v1/studio/projects/*` endpoints.

SOURCE: https://elevenlabs.io/docs/changelog/2025/2/10

LANGUAGE: APIDOC
CODE:
```
Studio (formerly Projects)
  All /v1/projects/* endpoints have been deprecated in favor of the new /v1/studio/projects/* endpoints.
  The following endpoints are now deprecated:
  - All operations on /v1/projects/
  - All operations related to chapters, snapshots, and content under /v1/projects/*
```

----------------------------------------

TITLE: ElevenLabs Conversational AI: SIP Trunk Outbound Call API Reference
DESCRIPTION: Comprehensive API documentation for the POST /v1/convai/sip-trunk/outbound-call endpoint. This section details the endpoint URL, HTTP method, required headers, request body parameters, and the structure of a successful response for initiating an outbound call.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/sip-trunk/outbound-call

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST https://api.elevenlabs.io/v1/convai/sip-trunk/outbound-call

Headers:
  xi-api-key: string (Required)

Request Body:
  Type: object
  Properties:
    agent_id: string (Required)
    agent_phone_number_id: string (Required)
    to_number: string (Required)
    conversation_initiation_client_data: object or null (Optional)

Response (200 Successful):
  Type: object
  Properties:
    success: boolean
    message: string
    conversation_id: string or null
    sip_call_id: string or null
```

----------------------------------------

TITLE: List Phone Numbers using ElevenLabs Python SDK
DESCRIPTION: Illustrates how to programmatically retrieve a list of phone numbers using the official ElevenLabs Python SDK. This example demonstrates initializing the ElevenLabs client with an API key and calling the `list()` method on the `conversational_ai.phone_numbers` object to fetch the data.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/phone-numbers/list

LANGUAGE: Python
CODE:
```
from elevenlabs import ElevenLabs

client = ElevenLabs(
    api_key="YOUR_API_KEY",
)
client.conversational_ai.phone_numbers.list()
```

----------------------------------------

TITLE: API Endpoint: List Knowledge Base Documents
DESCRIPTION: Detailed API documentation for the GET /v1/convai/knowledge-base endpoint. This section outlines the request method, URL, required headers, optional query parameters with their types, constraints, and descriptions, and the structure of successful and error responses.

SOURCE: https://elevenlabs.io/docs/api-reference/knowledge-base

LANGUAGE: APIDOC
CODE:
```
GET /v1/convai/knowledge-base
  Description: Get a list of available knowledge base documents
  Headers:
    xi-api-key: string (Required)
  Query Parameters:
    cursor: string | null (Optional)
      Description: Used for fetching next page. Cursor is returned in the response.
    page_size: integer (Optional)
      Constraints: >=1, <=100
      Default: 30
      Description: How many documents to return at maximum. Can not exceed 100, defaults to 30.
    search: string | null (Optional)
      Description: If specified, the endpoint returns only such knowledge base documents whose names start with this string.
    show_only_owned_documents: boolean (Optional)
      Default: false
      Description: If set to true, the endpoint will return only documents owned by you (and not shared from somebody else).
    types: list of enums | null (Optional)
      Allowed values: file, url, text
      Description: If present, the endpoint will return only documents of the given types.
    use_typesense: boolean (Optional)
      Default: false
      Description: If set to true, the endpoint will use typesense DB to search for the documents).
  Responses:
    200 (Successful Response):
      documents: list of objects
      has_more: boolean
      next_cursor: string | null
    422 (Unprocessable Entity Error)
```

----------------------------------------

TITLE: Eleven Labs Audio Isolation API Endpoint Reference
DESCRIPTION: Detailed API documentation for the Audio Isolation endpoint. It outlines the HTTP method, endpoint path, required headers, and the structure of the multipart form data request body, including parameters for the audio file and its format. It also lists possible error responses.

SOURCE: https://elevenlabs.io/docs/api-reference/audio-isolation/audio-isolation

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/audio-isolation
Description: Removes background noise from audio.

Headers:
  xi-api-key:
    type: string
    required: true

Request:
  Content-Type: multipart/form-data
  Parameters:
    audio:
      type: file
      required: true
      description: The audio file from which vocals/speech will be isolated from.
    file_format:
      type: enum or null
      optional: true
      default: other
      description: The format of input audio. Options are ‘pcm_s16le_16’ or ‘other’. For `pcm_s16le_16`, the input audio must be 16-bit PCM at a 16kHz sample rate, single channel (mono), and little-endian byte order. Latency will be lower than with passing an encoded waveform.
      allowed_values:
        - pcm_s16le_16
        - other

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Simulate Conversation Endpoint Request Body Specification
DESCRIPTION: Defines the structure of the JSON object expected by the 'simulate conversation' API endpoint. It includes details on the required simulation specification and optional evaluation criteria.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/agents/simulate-conversation-stream

LANGUAGE: APIDOC
CODE:
```
Request Body:
  simulation_specification: object (Required)
    Description: A specification detailing how the conversation should be simulated
    Properties: (4 properties, details not provided in source)
  extra_evaluation_criteria: list of objects or null (Optional)
    Description: A list of evaluation criteria to test
    Properties: (5 properties, details not provided in source)

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs API: Get RAG Index Overview Endpoint
DESCRIPTION: This section defines the API endpoint for retrieving an overview of RAG indexes. It specifies the HTTP method (GET) and the full URL path, providing the foundational information for making the API call.

SOURCE: https://elevenlabs.io/docs/api-reference/knowledge-base/rag-index-overview

LANGUAGE: HTTP
CODE:
```
GET
https://api.elevenlabs.io/v1/convai/knowledge-base/rag-index

GET
/v1/convai/knowledge-base/rag-index
```

----------------------------------------

TITLE: Fix Language Detection in Conversational AI System Tool
DESCRIPTION: Addresses and resolves an issue in the language detection system tool where it would incorrectly trigger when a user replied 'yes' in a non-English language.

SOURCE: https://elevenlabs.io/docs/changelog/2025/4/28

LANGUAGE: APIDOC
CODE:
```
Conversational AI System Tools:
  Feature: Language detection
  Fix: Resolved an issue where the tool incorrectly triggered on non-English 'yes' responses.
  Documentation: /docs/conversational-ai/customization/tools/system-tools/language-detection
```

----------------------------------------

TITLE: Example JSON Response for Listing Workspace Webhooks
DESCRIPTION: This JSON example illustrates the successful response structure when listing workspace webhooks. It shows an array of webhook objects, each containing details such as name, ID, URL, status, creation timestamp, authentication type, usage, and recent failure information.

SOURCE: https://elevenlabs.io/docs/api-reference/webhooks/list

LANGUAGE: JSON
CODE:
```
{
  "webhooks": [
    {
      "name": "My Webhook",
      "webhook_id": "123",
      "webhook_url": "https://elevenlabs.io/example-callback-url",
      "is_disabled": false,
      "is_auto_disabled": false,
      "created_at_unix": 123456789,
      "auth_type": "hmac",
      "usage": [
        {
          "usage_type": "ConvAI Settings"
        }
      ],
      "most_recent_failure_error_code": 404,
      "most_recent_failure_timestamp": 123456799
    }
  ]
}
```

----------------------------------------

TITLE: Update Project Management API: Add Project
DESCRIPTION: Updates the 'Add project' endpoint, making several properties nullable.

SOURCE: https://elevenlabs.io/docs/changelog/2025/3/17

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /docs/api-reference/studio/add-project
Changes:
  - Made nullable: `metadata`, `project_name`, `description`
```

----------------------------------------

TITLE: List Pronunciation Dictionaries using ElevenLabs TypeScript Client
DESCRIPTION: This snippet demonstrates how to use the official ElevenLabs TypeScript client to fetch a list of pronunciation dictionaries. It requires an API key for authentication and initializes the client to make the API call.

SOURCE: https://elevenlabs.io/docs/api-reference/pronunciation-dictionaries/list

LANGUAGE: TypeScript
CODE:
```
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient({ apiKey: "YOUR_API_KEY" });
await client.pronunciationDictionaries.list();
```

----------------------------------------

TITLE: Example JSON Response for List Phone Numbers API
DESCRIPTION: Provides a sample JSON array representing a successful response from the 'List Phone Numbers' API endpoint. Each object in the array details a phone number, including its unique ID, a user-defined label, the assigned conversational agent, and the telephony provider (e.g., Twilio).

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/phone-numbers/list

LANGUAGE: JSON
CODE:
```
[
  {
    "phone_number": "foo",
    "label": "foo",
    "phone_number_id": "foo",
    "assigned_agent": {
      "agent_id": "foo",
      "agent_name": "foo"
    },
    "provider": "twilio"
  }
]
```

----------------------------------------

TITLE: API Reference for Update Dubbing Segment Endpoint
DESCRIPTION: Comprehensive API documentation for the 'Update a segment' endpoint, detailing path parameters, required headers, optional request body fields, and the structure of a successful response, along with potential error codes. This endpoint modifies a single segment's text and/or start/end times for a specific language without regenerating the dub.

SOURCE: https://elevenlabs.io/docs/api-reference/dubbing/update-segment-language

LANGUAGE: APIDOC
CODE:
```
Modifies a single segment with new text and/or start/end times. Will update the values for only a specific language of a segment. Does not automatically regenerate the dub.

### Path parameters
dubbing_idstringRequired
  ID of the dubbing project.
segment_idstringRequired
  ID of the segment
languagestringRequired
  ID of the language.

### Headers
xi-api-keystringRequired

### Request
This endpoint expects an object.
start_timedouble or nullOptional
end_timedouble or nullOptional
textstring or nullOptional

### Response
Successful Response
versioninteger

### Errors
422
Unprocessable Entity Error
```

----------------------------------------

TITLE: API Specification: Get Conversation Details Endpoint
DESCRIPTION: Detailed API documentation for the 'Get conversation details' endpoint, including the HTTP method, URL path, required path parameters, necessary headers for authentication, and the comprehensive schema for a successful 200 OK response. It also lists potential error responses.

SOURCE: https://elevenlabs.io/docs/api-reference/conversations/get-conversation

LANGUAGE: APIDOC
CODE:
```
Endpoint:
  GET https://api.elevenlabs.io/v1/convai/conversations/:conversation_id

Path Parameters:
  conversation_id: string (Required)
    Description: The id of the conversation you're taking the action on.

Headers:
  xi-api-key: string (Required)

Response (200 Retrieved):
  agent_id: string
  conversation_id: string
  status: enum
    Allowed values: initiated, in-progress, processing, done, failed
  transcript: list of objects
  metadata: object
  has_audio: boolean
  has_user_audio: boolean
  has_response_audio: boolean
  analysis: object or null
  conversation_initiation_client_data: object or null

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs SDK Updates and Enhancements
DESCRIPTION: Outlines recent updates to ElevenLabs SDKs, including expanded cross-runtime compatibility, regeneration to align with the latest API specification, and a fix for dynamic variable handling.

SOURCE: https://elevenlabs.io/docs/changelog/2025/1/27

LANGUAGE: APIDOC
CODE:
```
SDK Updates:
- Cross-Runtime Support: Compatible with Bun 1.1.45+ and Deno 2.1.7+
- Regenerated SDKs: Updated to latest API spec (Python SDK release 1.50.5, JS SDK release v1.50.4)
- Dynamic Variables: Fixed an issue where dynamic variables were not being handled correctly in all SDKs
```

----------------------------------------

TITLE: ElevenLabs Voice Changer API Endpoint Reference
DESCRIPTION: This section details the `POST /v1/speech-to-speech/:voice_id` API endpoint for transforming audio. It outlines required path parameters, headers, and optional query parameters like `enable_logging`, `optimize_streaming_latency`, and `output_format`, along with their types, descriptions, and default values.

SOURCE: https://elevenlabs.io/docs/api-reference/speech-to-speech/convert

LANGUAGE: APIDOC
CODE:
```
POST /v1/speech-to-speech/:voice_id

Path Parameters:
  voice_id: string (Required)
    Description: ID of the voice to be used. Use the Get voices endpoint to list all the available voices.

Headers:
  xi-api-key: string (Required)

Query Parameters:
  enable_logging: boolean (Optional)
    Default: true
    Description: When enable_logging is set to false zero retention mode will be used for the request. This will mean history features are unavailable for this request, including request stitching. Zero retention mode may only be used by enterprise customers.
  optimize_streaming_latency: integer or null (Optional, Deprecated)
    Default: None
    Description: You can turn on latency optimizations at some cost of quality. The best possible final latency varies by model. Possible values: 0 - default mode (no latency optimizations), 1 - normal latency optimizations (about 50% of possible latency improvement of option 3), 2 - strong latency optimizations (about 75% of possible latency improvement of option 3), 3 - max latency optimizations, 4 - max latency optimizations, but also with text normalizer turned off for even more latency savings (best latency, but can mispronounce eg numbers and dates).
  output_format: enum (Optional)
    Default: mp3_44100_128
    Description: Output format of the generated audio. Formatted as codec_sample_rate_bitrate. So an mp3 with 22.05kHz sample rate at 32kbs is represented as mp3_22050_32. MP3 with 192kbps bitrate requires you to be subscribed to Creator tier or above. PCM with 44.1kHz sample rate requires you to be subscribed to Pro tier or above. Note that the µ-law format (sometimes written mu-law, often approximated as u-law) is commonly used for Twilio audio inputs.
```

----------------------------------------

TITLE: Example cURL Request for Get Chapter Snapshot
DESCRIPTION: Provides a command-line example using cURL to demonstrate how to call the 'Get Chapter Snapshot' API endpoint. This example includes the full URL with placeholder IDs and the necessary `xi-api-key` header for authentication.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/get-chapter-snapshot

LANGUAGE: cURL
CODE:
```
curl https://api.elevenlabs.io/v1/studio/projects/project_id/chapters/chapter_id/snapshots/chapter_snapshot_id \
-H "xi-api-key: xi-api-key"
```

----------------------------------------

TITLE: Example JSON Response for Convai Dashboard Settings Update
DESCRIPTION: Provides an example of a successful JSON response body returned after updating the Convai dashboard settings, demonstrating the structure of the 'charts' array.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/dashboard/update

LANGUAGE: JSON
CODE:
```
{
  "charts": [
    {
      "name": "foo",
      "type": "call_success"
    }
  ]
}
```

----------------------------------------

TITLE: Example JSON Response for Speech-to-Text API
DESCRIPTION: This JSON object represents a successful response from the ElevenLabs Speech-to-Text API. It provides the detected `language_code`, `language_probability`, the full `text` transcript, and a detailed `words` array including `text`, `type`, `logprob`, `start`, `end` timestamps, and `speaker_id` for each word.

SOURCE: https://elevenlabs.io/docs/api-reference/speech-to-text/convert

LANGUAGE: JSON
CODE:
```
{
  "language_code": "en",
  "language_probability": 0.98,
  "text": "Hello world!",
  "words": [
    {
      "text": "Hello",
      "type": "word",
      "logprob": -0.124,
      "start": 0,
      "end": 0.5,
      "speaker_id": "speaker_1"
    },
    {
      "text": " ",
      "type": "spacing",
      "logprob": 0,
      "start": 0.5,
      "end": 0.5,
      "speaker_id": "speaker_1"
    },
    {
      "text": "world!",
      "type": "word",
      "logprob": -0.089,
      "start": 0.5,
      "end": 1.2,
      "speaker_id": "speaker_1"
    }
  ]
}
```

----------------------------------------

TITLE: Eleven Labs API: Get Dubbed Audio Endpoint Reference
DESCRIPTION: This section details the API endpoint for retrieving dubbed audio. It specifies the HTTP GET method, the full URL path with required parameters, and the necessary authentication header. It also describes the path parameters `dubbing_id` and `language_code`, the `xi-api-key` header, along with the expected response and potential errors.

SOURCE: https://elevenlabs.io/docs/api-reference/dubbing/audio/get

LANGUAGE: APIDOC
CODE:
```
Endpoint: GET /v1/dubbing/:dubbing_id/audio/:language_code
Full URL: https://api.elevenlabs.io/v1/dubbing/:dubbing_id/audio/:language_code
Description: Returns dub as a streamed MP3 or MP4 file. If this dub has been edited using Dubbing Studio you need to use the resource render endpoint as this endpoint only returns the original automatic dub result.

Path Parameters:
  dubbing_id: string (Required)
    Description: ID of the dubbing project.
  language_code: string (Required)
    Description: ID of the language.

Headers:
  xi-api-key: string (Required)
    Description: Your API key for authentication.

Response:
  Type: Audio/Video file (streamed MP3 or MP4)
  Description: The dubbed audio or video file.

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Specify Pronunciation Dictionaries via cURL
DESCRIPTION: Demonstrates how to pass multiple pronunciation dictionary locators as JSON strings using `curl --form` for project creation, especially when using formData instead of a JSON body. This example shows the `--form` arguments.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/add-project

LANGUAGE: Shell
CODE:
```
\u2014form \u2018pronunciation_dictionary_locators=\"{\"pronunciation_dictionary_id\":\"Vmd4Zor6fplcA7WrINey\",\"version_id\":\"hRPaxjlTdR7wFMhV4w0b\"}\"\u2019 \u2014form \u2018pronunciation_dictionary_locators=\"{\"pronunciation_dictionary_id\":\"JzWtcGQMJ6bnlWwyMo7e\",\"version_id\":\"lbmwxiLu4q6txYxgdZqn\"}\"\u2019
```

----------------------------------------

TITLE: GET RAG Index Overview API Endpoint
DESCRIPTION: This API documentation describes the GET endpoint for retrieving an overview of RAG indexes within the ElevenLabs Conversational AI knowledge base. It provides details on the request method, path, required headers, and the structure of the successful response.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/knowledge-base/rag-index-overview

LANGUAGE: APIDOC
CODE:
```
GET
/v1/convai/knowledge-base/rag-index

### Headers
xi-api-keystringRequired

### Response
Successful Response
total_used_bytesinteger
total_max_bytesinteger
modelslist of objects
Show 2 properties
```

----------------------------------------

TITLE: API Reference: Delete Knowledge Base Document
DESCRIPTION: This section details the API endpoint for deleting a document from the ElevenLabs conversational AI knowledge base. It specifies the HTTP method, endpoint URL, required path parameters, headers, optional query parameters, and expected responses, including error codes.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/knowledge-base/delete

LANGUAGE: APIDOC
CODE:
```
Endpoint: DELETE /v1/convai/knowledge-base/:documentation_id
Description: Delete a document from the knowledge base.

Path Parameters:
  documentation_id:
    Type: string
    Required: true
    Description: The id of a document from the knowledge base. This is returned on document addition.

Headers:
  xi-api-key:
    Type: string
    Required: true

Query Parameters:
  force:
    Type: boolean
    Optional: true
    Default: false
    Description: If set to true, the document will be deleted regardless of whether it is used by any agents and it will be deleted from the dependent agents.

Responses:
  Successful Response:
    Description: The document was successfully deleted.
  Errors:
    422 Unprocessable Entity Error:
      Description: Indicates that the server understands the content type of the request entity, and the syntax of the request entity is correct, but it was unable to process the contained instructions.
```

----------------------------------------

TITLE: Get Resource API Parameters and Response Schema
DESCRIPTION: Detailed API documentation for the 'Get Resource' endpoint, outlining required path parameters, headers, query parameters, and the comprehensive structure of the successful response. This section also notes potential error responses.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/resources/get

LANGUAGE: APIDOC
CODE:
```
Path parameters:
  resource_id: string (Required)
    Description: The ID of the target resource.

Headers:
  xi-api-key: string (Required)

Query parameters:
  resource_type: enum (Required)
    Description: Resource type of the target resource. (Show 15 enum values)

Response (Successful Response - 200 Retrieved):
  resource_id: string
    Description: The ID of the resource.
  resource_type: enum
    Description: The type of the resource. (Show 15 enum values)
  creator_user_id: string or null
    Description: The ID of the user who created the resource.
  role_to_group_ids: map from strings to lists of strings
    Description: A mapping of roles to group IDs. When the resource is shared with a user, the group id is the user's id.
  share_options: list of objects
    Description: List of options for sharing the resource further in the workspace. These are users who don't have access to the resource yet. (Show 3 properties)

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference: Create Conversational AI Agent Endpoint
DESCRIPTION: This section provides the detailed API specification for the `POST /v1/convai/agents/create` endpoint. It outlines the required headers, the structure of the request body including `conversation_config`, `platform_settings`, `name`, and `tags`, and the expected successful response format containing the `agent_id`. It also notes potential error responses.

SOURCE: https://elevenlabs.io/docs/api-reference/agents

LANGUAGE: APIDOC
CODE:
```
POST /v1/convai/agents/create

Headers:
  xi-api-key: string (Required) - Your ElevenLabs API key.

Request Body:
  conversation_config: object (Required) - Conversation configuration for an agent.
  platform_settings: object or null (Optional) - Platform settings for the agent.
  name: string or null (Optional) - A name to make the agent easier to find.
  tags: list of strings or null (Optional) - Tags to help classify and filter the agent.

Response (200 Successful):
  {
    "agent_id": "string" - ID of the created agent.
  }

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Updated ElevenLabs API: Conversational AI Widget Configuration
DESCRIPTION: Documentation for enhanced widget configuration, adding support for text-only mode.

SOURCE: https://elevenlabs.io/docs/changelog

LANGUAGE: APIDOC
CODE:
```
Widget Configuration Parameters:
  text_only: boolean
    Description: Enables text-only mode for the widget.
```

----------------------------------------

TITLE: API Reference: Get Knowledge Base Document Content Endpoint
DESCRIPTION: Detailed API documentation for the GET /v1/convai/knowledge-base/:documentation_id/content endpoint. This section specifies the HTTP method, full URL, required path parameters, authentication headers, and potential error responses for retrieving knowledge base document content.

SOURCE: https://elevenlabs.io/docs/api-reference/knowledge-base/get-content

LANGUAGE: APIDOC
CODE:
```
Endpoint:
  GET https://api.elevenlabs.io/v1/convai/knowledge-base/:documentation_id/content

Description:
  Get the entire content of a document from the knowledge base

Path Parameters:
  documentation_id:
    type: string
    required: true
    description: The id of a document from the knowledge base. This is returned on document addition.

Headers:
  xi-api-key:
    type: string
    required: true

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference for Get Default Voice Settings Endpoint
DESCRIPTION: This section details the API endpoint for retrieving the default voice settings. It specifies the HTTP method, the full endpoint URL, required headers, and the structure of the successful 200 OK response, along with descriptions for each parameter.

SOURCE: https://elevenlabs.io/docs/api-reference/voices/settings/get-default

LANGUAGE: APIDOC
CODE:
```
Method: GET
Path: /v1/voices/settings/default
Full URL: https://api.elevenlabs.io/v1/voices/settings/default

Headers:
  xi-api-key: string (Required)

Response (200 Retrieved):
  stability: double or null
    Description: Determines how stable the voice is and the randomness between each generation. Lower values introduce broader emotional range for the voice. Higher values can result in a monotonous voice with limited emotion.
  use_speaker_boost: boolean or null
    Description: This setting boosts the similarity to the original speaker. Using this setting requires a slightly higher computational load, which in turn increases latency.
  similarity_boost: double or null
    Description: Determines how closely the AI should adhere to the original voice when attempting to replicate it.
  style: double or null
    Description: Determines the style exaggeration of the voice. This setting attempts to amplify the style of the original speaker. It does consume additional computational resources and might increase latency if set to anything other than 0.
  speed: double or null
    Description: Adjusts the speed of the voice. A value of 1.0 is the default speed, while values less than 1.0 slow down the speech, and values greater than 1.0 speed it up.
```

----------------------------------------

TITLE: Breaking Changes in ElevenLabs Conversational AI API
DESCRIPTION: Details breaking changes for Conversational AI API endpoints, including a change in response type for `DELETE /v1/convai/agents/{agent_id}` and a change in response type for `GET /v1/convai/tools`.

SOURCE: https://elevenlabs.io/docs/changelog/2025/2/10

LANGUAGE: APIDOC
CODE:
```
Breaking Changes
  - DELETE /v1/convai/agents/{agent_id} - Response type is no longer an object
  - GET /v1/convai/tools - Response type changed from array to object with a tools property
```

----------------------------------------

TITLE: API Reference: Get Knowledge Base Document Endpoint
DESCRIPTION: This documentation outlines the `GET` endpoint for retrieving a specific document from an agent's knowledge base. It includes the request path, required parameters, headers, and the structure of the successful JSON response.

SOURCE: https://elevenlabs.io/docs/api-reference/knowledge-base/get

LANGUAGE: APIDOC
CODE:
```
GET /v1/convai/knowledge-base/:documentation_id

Path parameters:
  documentation_id: string (Required)
    The id of a document from the knowledge base. This is returned on document addition.

Headers:
  xi-api-key: string (Required)

Query parameters:
  agent_id: string (Optional)

Response (200 Retrieved):
  GetKnowledgeBaseURLResponseModel: object
  OR
  GetKnowledgeBaseFileResponseModel: object
  OR
  GetKnowledgeBaseTextResponseModel: object

Example JSON Response:
{
  "id": "foo",
  "name": "foo",
  "metadata": {
    "created_at_unix_secs": 42,
    "last_updated_at_unix_secs": 42,
    "size_bytes": 42
  },
  "supported_usages": [
    "prompt"
  ],
  "access_info": {
    "is_creator": true,
    "creator_name": "foo",
    "creator_email": "foo",
    "role": "admin"
  },
  "extracted_inner_html": "foo",
  "type": "foo",
  "url": "foo"
}
```

----------------------------------------

TITLE: Update Convai Dashboard Settings API Endpoint Specification
DESCRIPTION: Documents the PATCH endpoint for updating Convai dashboard settings, including its full path, required headers, request body structure, and expected response and error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/dashboard/update

LANGUAGE: APIDOC
CODE:
```
Method: PATCH
Path: /v1/convai/settings/dashboard
Full URL: https://api.elevenlabs.io/v1/convai/settings/dashboard

Description: Update Convai dashboard settings for the workspace

Headers:
  - xi-api-key: string (Required)

Request Body:
  Type: object
  Properties:
    - charts: list of objects (Optional)

Response (200 Updated):
  Type: object
  Properties:
    - charts: list of objects or null

Errors:
  - 422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference: Eleven Labs Audio Isolation Stream Endpoint
DESCRIPTION: Comprehensive API documentation for the Eleven Labs Audio Isolation Stream endpoint. It details the POST request method, URL, required headers, multipart form data parameters (audio file, optional file format), and potential error responses.

SOURCE: https://elevenlabs.io/docs/api-reference/audio-isolation-stream

LANGUAGE: APIDOC
CODE:
```
POST https://api.elevenlabs.io/v1/audio-isolation/stream

Headers:
  xi-api-key: string (Required) - Your Eleven Labs API key.

Request Body (multipart/form-data):
  audio: file (Required) - The audio file from which vocals/speech will be isolated from.
  file_format: enum or null (Optional) - Defaults to 'other'. The format of input audio.
    Allowed values:
      - pcm_s16le_16: 16-bit PCM at a 16kHz sample rate, single channel (mono), and little-endian byte order. Latency will be lower than with passing an encoded waveform.
      - other: Encoded waveform.

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Reference: Create PVC Voice Endpoint
DESCRIPTION: Detailed API documentation for the POST /v1/voices/pvc endpoint, which facilitates the creation of a new PVC voice. This section outlines the required headers, the structure and types of the request body parameters, the successful response format, and potential error responses.

SOURCE: https://elevenlabs.io/docs/api-reference/voices/pvc/create

LANGUAGE: APIDOC
CODE:
```
Endpoint:
  POST /v1/voices/pvc
  Base URL: https://api.elevenlabs.io

Description:
  Creates a new PVC voice with metadata but no samples.

Headers:
  xi-api-key: string (Required)

Request Body (application/json):
  name: string (Required)
    Constraints: <=100 characters
    Description: The name that identifies this voice. This will be displayed in the dropdown of the website.
  language: string (Required)
    Description: Language used in the samples.
  description: string or null (Optional)
    Constraints: <=500 characters
    Description: Description to use for the created voice.
  labels: map<string, string> or null (Optional)
    Description: Serialized labels dictionary for the voice.

Responses:
  200 OK: Successful Response
    Body:
      voice_id: string
        Description: The ID of the voice.
    Example Body:
      {
        "voice_id": "b38kUX8pkfYO2kHyqfFy"
      }

  422 Unprocessable Entity: Error
    Description: Unprocessable Entity Error
```

----------------------------------------

TITLE: Delete Voice using ElevenLabs TypeScript SDK
DESCRIPTION: Demonstrates how to delete a voice programmatically using the ElevenLabs TypeScript SDK, requiring an API key for authentication and specifying the voice ID.

SOURCE: https://elevenlabs.io/docs/api-reference/voices/delete

LANGUAGE: TypeScript
CODE:
```
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient({ apiKey: "YOUR_API_KEY" });
await client.voices.delete("21m00Tcm4TlvDq8ikWAM");
```

----------------------------------------

TITLE: GenFM Endpoint Updates
DESCRIPTION: Update to the GenFM project creation endpoint to support multiple input sources.

SOURCE: https://elevenlabs.io/docs/changelog/2025/2/10

LANGUAGE: APIDOC
CODE:
```
POST /v1/projects/podcast/create - Added support for multiple input sources
```

----------------------------------------

TITLE: Example JSON Response for Get Agent API
DESCRIPTION: Presents a sample JSON structure returned upon a successful (HTTP 200) 'Get Agent' API call. This schema details the extensive configuration of an agent, including ASR, TTS, conversation settings, prompt parameters, and integrated tools.

SOURCE: https://elevenlabs.io/docs/api-reference/agents/get

LANGUAGE: APIDOC
CODE:
```
{
"agent_id": "J3Pbu5gP6NNKBscdCdwB",
"name": "My Agent",
"conversation_config": {
"asr": {
"quality": "high",
"provider": "elevenlabs",
"user_input_audio_format": "pcm_8000",
"keywords": [
"foo"
]
},
"turn": {
"turn_timeout": 7,
"silence_end_call_timeout": -1,
"mode": "silence"
},
"tts": {
"model_id": "eleven_turbo_v2",
"voice_id": "cjVigY5qzO86Huf0OWal",
"supported_voices": [
{
"label": "foo",
"voice_id": "foo",
"description": "foo",
"language": "foo",
"model_family": "turbo",
"optimize_streaming_latency": 0,
"stability": 42,
"speed": 42,
"similarity_boost": 42
}
],
"agent_output_audio_format": "pcm_8000",
"optimize_streaming_latency": 0,
"stability": 0.5,
"speed": 1,
"similarity_boost": 0.8,
"pronunciation_dictionary_locators": [
{
"pronunciation_dictionary_id": "foo",
"version_id": "foo"
}
]
},
"conversation": {
"text_only": false,
"max_duration_seconds": 600,
"client_events": [
"conversation_initiation_metadata"
]
},
"language_presets": {},
"agent": {
"first_message": "",
"language": "en",
"dynamic_variables": {
"dynamic_variable_placeholders": {}
},
"prompt": {
"prompt": "",
"llm": "gpt-4o-mini",
"temperature": 0,
"max_tokens": -1,
"tool_ids": [
"foo"
],
"built_in_tools": {
"end_call": {
"name": "foo",
"description": "foo",
"params": {
"system_tool_type": "end_call"
},
"response_timeout_secs": 20,
"type": "system"
},
"language_detection": {
"name": "foo",
"description": "foo",
"params": {
"system_tool_type": "end_call"
},
"response_timeout_secs": 20,
"type": "system"
},
"transfer_to_agent": {
"name": "foo",
"description": "foo",
"params": {
"system_tool_type": "end_call"
},
"response_timeout_secs": 20,
"type": "system"
},
"transfer_to_number": {
"name": "foo",
"description": "foo",
"params": {
"system_tool_type": "end_call"
},
"response_timeout_secs": 20,
"type": "system"
},
"skip_turn": {
"name": "foo",
"description": "foo",
"params": {
"system_tool_type": "end_call"
},
"response_timeout_secs": 20,
"type": "system"
},
"play_keypad_touch_tone": {
"name": "foo",
"description": "foo",
"params": {
"system_tool_type": "end_call"
},
"response_timeout_secs": 20,
"type": "system"
}
},
"mcp_server_ids": [
"foo"
],
"native_mcp_server_ids": [
"foo"
],
"knowledge_base": [
{
"type": "file",
"name": "foo",
"id": "foo",
"usage_mode": "prompt"
}
],
"custom_llm": {
"url": "foo",
"model_id": "foo",
"api_key": {
"secret_id": "foo"
},
"request_headers": {}
},
"ignore_default_personality": true,
"rag": {
"enabled": false,
"embedding_model": "e5_mistral_7b_instruct",
"max_vector_distance": 0.6,
"max_documents_length": 50000,
"max_retrieved_rag_chunks_count": 20
},
"tools": [
{
"name": "foo",
"description": "foo",
"response_timeout_secs": 20,
"type": "webhook",
"api_schema": {
"url": "foo",
"method": "GET",
"path_params_schema": {},
"query_params_schema": {
"properties": {},
"required": [
"foo"
]
},
"request_body_schema": {
"type": "object",
"required": [
"foo"

```

----------------------------------------

TITLE: API Reference: Get User Subscription Endpoint
DESCRIPTION: Detailed API documentation for the GET /v1/user/subscription endpoint. This endpoint retrieves extended information about the user's current subscription plan, including character limits, voice slots, and billing details. It specifies the HTTP method, path, and required authentication headers.

SOURCE: https://elevenlabs.io/docs/api-reference/user/subscription/get

LANGUAGE: APIDOC
CODE:
```
GET /v1/user/subscription
Description: Gets extended information about the users subscription
Headers:
  xi-api-key: string (Required)
```

----------------------------------------

TITLE: Example JSON Response for Listing Pronunciation Dictionaries
DESCRIPTION: This JSON object represents a successful response from the 'List pronunciation dictionaries' API endpoint. It contains an array of `pronunciation_dictionaries` objects, each with metadata such as ID, name, creation time, and permissions. It also includes `has_more` for pagination and `next_cursor` for fetching subsequent pages.

SOURCE: https://elevenlabs.io/docs/api-reference/pronunciation-dictionary/get-all

LANGUAGE: JSON
CODE:
```
{
  "pronunciation_dictionaries": [
    {
      "id": "5xM3yVvZQKV0EfqQpLrJ",
      "latest_version_id": "5xM3yVvZQKV0EfqQpLr2",
      "latest_version_rules_num": 2,
      "name": "My Dictionary",
      "permission_on_resource": "admin",
      "created_by": "ar6633Es2kUjFXBdR1iVc9ztsXl1",
      "creation_time_unix": 1714156800,
      "description": "This is a test dictionary"
    }
  ],
  "has_more": false,
  "next_cursor": "5xM3yVvZQKV0EfqQpLr2"
}
```

----------------------------------------

TITLE: Batch Calling API Endpoints
DESCRIPTION: Documentation for managing batch calls, including cancellation and retry operations.

SOURCE: https://elevenlabs.io/docs/changelog/2025/6/8

LANGUAGE: APIDOC
CODE:
```
Batch Calling:
  Cancel batch call: Cancel a running batch call and set all recipients to cancelled status
  Retry batch call: Retry a batch call by setting completed recipients back to pending status
```

----------------------------------------

TITLE: List Phone Numbers using cURL
DESCRIPTION: This cURL command demonstrates how to retrieve a list of all configured phone numbers associated with your ElevenLabs account. It requires an 'xi-api-key' for authentication, which should be replaced with your actual API key.

SOURCE: https://elevenlabs.io/docs/api-reference/phone-numbers/list

LANGUAGE: cURL
CODE:
```
curl https://api.elevenlabs.io/v1/convai/phone-numbers \
  -H "xi-api-key: xi-api-key"
```

----------------------------------------

TITLE: New API Endpoint: Unshare Workspace Resource
DESCRIPTION: Introduces a new API endpoint to unshare a workspace resource.

SOURCE: https://elevenlabs.io/docs/changelog/2025/3/17

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /docs/api-reference/workspace/unshare-workspace-resource
Description: Unshare workspace resource
```

----------------------------------------

TITLE: Retrieve Dubbing Resource using ElevenLabs TypeScript SDK
DESCRIPTION: This TypeScript code snippet demonstrates how to programmatically fetch a dubbing resource using the official ElevenLabs JavaScript/TypeScript SDK. It shows client initialization with an API key and the method call to retrieve a specific dubbing resource by its ID.

SOURCE: https://elevenlabs.io/docs/api-reference/dubbing/get-dubbing-resource

LANGUAGE: TypeScript
CODE:
```
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient({ apiKey: "YOUR_API_KEY" });
await client.dubbing.resource.get("dubbing_id");
```

----------------------------------------

TITLE: API Endpoint: Create Pronunciation Dictionary from File
DESCRIPTION: This section defines the API endpoint for creating a new pronunciation dictionary by uploading a lexicon .PLS file. It specifies the HTTP method (POST) and the full API path for this operation.

SOURCE: https://elevenlabs.io/docs/api-reference/pronunciation-dictionaries/create-from-file

LANGUAGE: APIDOC
CODE:
```
POST
https://api.elevenlabs.io/v1/pronunciation-dictionaries/add-from-file
POST
/v1/pronunciation-dictionaries/add-from-file
```

----------------------------------------

TITLE: API Reference for Creating Knowledge Base Document from Text
DESCRIPTION: This section provides the full API specification for creating a knowledge base document from text. It includes the HTTP method (POST), the endpoint URL, required headers (xi-api-key), request body parameters (text, optional name), the structure of a successful 200 OK response, and details on potential 422 Unprocessable Entity errors.

SOURCE: https://elevenlabs.io/docs/api-reference/knowledge-base/create-from-text

LANGUAGE: APIDOC
CODE:
```
POST /v1/convai/knowledge-base/text

Headers:
  xi-api-key: string (Required)

Request Body:
  text: string (Required) - Text content to be added to the knowledge base.
  name: string or null (Optional) - A custom, human-readable name for the document. (>=1 character)

Response (200 Successful):
  Example:
    {
      "id": "foo",
      "name": "foo"
    }
  Schema:
    id: string
    name: string

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Transcribe Dubbing Segment using ElevenLabs Python SDK
DESCRIPTION: This Python code snippet demonstrates how to use the ElevenLabs Python SDK to regenerate transcriptions for specific segments of a dubbing project. It initializes the client with an API key and calls the `transcribe` method on the `dubbing.resource` object, passing the `dubbing_id` and a list of `segments`.

SOURCE: https://elevenlabs.io/docs/api-reference/dubbing/resources/transcribe-segment

LANGUAGE: Python
CODE:
```
from elevenlabs import ElevenLabs

client = ElevenLabs(
    api_key="YOUR_API_KEY",
)
client.dubbing.resource.transcribe(
    dubbing_id="dubbing_id",
    segments=["segments"],
)
```

----------------------------------------

TITLE: ElevenLabs Speech to Speech API Endpoint Reference
DESCRIPTION: This section details the request parameters, expected response, and possible error conditions for the ElevenLabs Speech to Speech API endpoint. It covers input file requirements, model selection, voice settings, and audio processing options for generating speech from an audio input.

SOURCE: https://elevenlabs.io/docs/api-reference/speech-to-speech

LANGUAGE: APIDOC
CODE:
```
Endpoint: Speech to Speech

Request:
  Method: POST (multipart form)
  Parameters:
    audiofile:
      Type: file
      Required: true
      Description: The audio file which holds the content and emotion that will control the generated speech.
    model_id:
      Type: string
      Optional: true
      Default: "eleven_english_sts_v2"
      Description: Identifier of the model that will be used. You can query them using GET /v1/models. The model needs to have support for speech to speech (check 'can_do_voice_conversion' property).
    voice_settings:
      Type: string or null
      Optional: true
      Description: Voice settings overriding stored settings for the given voice. They are applied only on the given request. Needs to be sent as a JSON encoded string.
    seed:
      Type: integer or null
      Optional: true
      Description: If specified, our system will make a best effort to sample deterministically, such that repeated requests with the same seed and parameters should return the same result. Determinism is not guaranteed. Must be integer between 0 and 4294967295.
    remove_background_noise:
      Type: boolean
      Optional: true
      Default: false
      Description: If set, will remove the background noise from your audio input using our audio isolation model. Only applies to Voice Changer.
    file_format:
      Type: enum or null
      Optional: true
      Default: "other"
      Description: The format of input audio.
      Allowed values:
        - "pcm_s16le_16": For this format, the input audio must be 16-bit PCM at a 16kHz sample rate, single channel (mono), and little-endian byte order. Latency will be lower than with passing an encoded waveform.
        - "other": Standard encoded waveform.

Response:
  Type: audio file
  Description: The generated audio file.

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Get Dubbing Resource API Endpoint and Client Usage
DESCRIPTION: This section provides a comprehensive overview of the ElevenLabs API endpoint for retrieving a dubbing resource. It includes the HTTP method and path, required parameters, expected headers, and a detailed structure of the successful response. Additionally, it demonstrates how to interact with this endpoint using the ElevenLabs JavaScript client library.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/get-resource

LANGUAGE: APIDOC
CODE:
```
GET /v1/dubbing/resource/:dubbing_id

Path parameters:
  dubbing_id: string (Required)
    ID of the dubbing project.

Headers:
  xi-api-key: string (Required)

Response (200 - Retrieved):
  id: string
  version: integer
  source_language: string
  target_languages: list of strings
  input: object
  background: object
  foreground: object
  speaker_tracks: map from strings to objects
  speaker_segments: map from strings to objects
  renders: map from strings to objects

Errors:
  422: Unprocessable Entity Error
```

LANGUAGE: TypeScript
CODE:
```
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient({ apiKey: "YOUR_API_KEY" });
await client.dubbing.resource.get("dubbing_id");
```

LANGUAGE: JSON
CODE:
```
{
  "id": "foo",
  "version": 42,
  "source_language": "foo",
  "target_languages": [
    "foo"
  ],
  "input": {
    "src": "foo",
    "content_type": "foo",
    "bucket_name": "foo",
    "random_path_slug": "foo",
    "duration_secs": 42,
    "is_audio": true,
    "url": "foo"
  },
  "background": {
    "src": "foo",
    "content_type": "foo",
    "bucket_name": "foo",
    "random_path_slug": "foo",
    "duration_secs": 42,
    "is_audio": true,
    "url": "foo"
  },
  "foreground": {
    "src": "foo",
    "content_type": "foo",
    "bucket_name": "foo",
    "random_path_slug": "foo",
    "duration_secs": 42,
    "is_audio": true,
    "url": "foo"
  },
  "speaker_tracks": {},
  "speaker_segments": {},
  "renders": {}
}
```

----------------------------------------

TITLE: Conversational AI - MCP Servers API Endpoints
DESCRIPTION: Documentation for new API endpoints related to managing Model Context Protocol (MCP) servers within the Eleven Labs Conversational AI suite. These endpoints allow for creation, listing, retrieval, and management of approval policies for MCP server configurations and tools.

SOURCE: https://elevenlabs.io/docs/changelog/2025/6/17

LANGUAGE: APIDOC
CODE:
```
Conversational AI - MCP Servers:
  - Create MCP server: Create a new MCP server configuration in the workspace
  - List MCP servers: Retrieve all MCP server configurations available in the workspace
  - Get MCP server: Retrieve a specific MCP server configuration from the workspace
  - Update MCP server approval policy: Update the approval policy configuration for an MCP server
  - Create MCP server tool approval: Add approval for a specific MCP tool when using per-tool approval mode
  - Delete MCP server tool approval: Remove approval for a specific MCP tool when using per-tool approval mode
```

----------------------------------------

TITLE: Example Successful Response for Translate Segment API
DESCRIPTION: An example of the JSON payload returned upon a successful call to the 'Translate segment' API endpoint, showing the 'version' field.

SOURCE: https://elevenlabs.io/docs/api-reference/dubbing/translate-segments

LANGUAGE: JSON
CODE:
```
{
  "version": 42
}
```

----------------------------------------

TITLE: TypeScript: Update Studio Project Content using Client Library
DESCRIPTION: An example demonstrating how to update Studio project content using the official ElevenLabs JavaScript/TypeScript client library. It shows client initialization with an API key and calling the update method with a project ID.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/update-content

LANGUAGE: TypeScript
CODE:
```
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient({ apiKey: "YOUR_API_KEY" });
await client.studio.projects.content.update("21m00Tcm4TlvDq8ikWAM", {});
```

----------------------------------------

TITLE: New Endpoints: Knowledge Base Document Creation
DESCRIPTION: Dedicated endpoints have been added for creating knowledge base documents from specific sources: text, files, and URLs. These specialized endpoints replace a previously general document creation endpoint, offering more granular control.

SOURCE: https://elevenlabs.io/docs/changelog/2025/4/7

LANGUAGE: APIDOC
CODE:
```
Endpoints:
  - /docs/api-reference/knowledge-base/create-from-text: Create text document
  - /docs/api-reference/knowledge-base/create-from-file: Create file document
  - /docs/api-reference/knowledge-base/create-from-url: Create URL document
```

----------------------------------------

TITLE: cURL Example to Retrieve Conversation Audio
DESCRIPTION: A cURL command example demonstrating how to make a request to the 'Get conversation audio' API endpoint. It shows the full URL with a placeholder for `conversation_id` and how to include the `xi-api-key` in the request header.

SOURCE: https://elevenlabs.io/docs/api-reference/conversations/get-audio

LANGUAGE: cURL
CODE:
```
curl https://api.elevenlabs.io/v1/convai/conversations/conversation_id/audio \
-H "xi-api-key: xi-api-key"
```

----------------------------------------

TITLE: ElevenLabs API Endpoint and Parameter Updates
DESCRIPTION: Details recent modifications to ElevenLabs API endpoints and request parameters, including new features, deprecations, and enhancements across various services like Studio, AudioNative, Agents, and User management.

SOURCE: https://elevenlabs.io/docs/changelog/2025/1/27

LANGUAGE: APIDOC
CODE:
```
API Changes:
- Added Update Project endpoint (for project editing)
- Added Update Content endpoint (for AudioNative content management)
- Deprecated quality_check_on parameter in project operations (now enabled for all users at no extra cost)
- Added apply_text_normalization parameter to project creation (modes: 'auto', 'on', 'apply_english', 'off')
- Added alpha feature auto_assign_voices in project creation
- Added auto_convert flag to project creation (to automatically convert projects to audio)
- Added support for creating Conversational AI agents with dynamic variables
- Added voice_slots_used to Subscription model (track custom voices used in workspace)
- Added user_id field to User endpoint
- Marked legacy AudioNative creation parameters (image, small, sessionization) as deprecated
- Agents platform now supports call_limits (agent_concurrency_limit, daily_limit)
- Added support for language_presets in conversation_config
```

----------------------------------------

TITLE: Eleven Labs API: Get Voice Settings Endpoint Reference
DESCRIPTION: Comprehensive API documentation for the `/v1/voices/:voice_id/settings` endpoint. It details the HTTP method (GET), URL structure, required path parameters (`voice_id`), authentication headers (`xi-api-key`), and the structure of the successful 200 OK response, including descriptions for each setting parameter. It also lists the 422 Unprocessable Entity error.

SOURCE: https://elevenlabs.io/docs/api-reference/voices/settings/get

LANGUAGE: APIDOC
CODE:
```
GET /v1/voices/:voice_id/settings

Path Parameters:
  voice_id: string (Required)
    Description: Voice ID to be used, you can use https://api.elevenlabs.io/v1/voices to list all the available voices.

Headers:
  xi-api-key: string (Required)

Response (200 Retrieved):
  stability: double or null
    Description: Determines how stable the voice is and the randomness between each generation. Lower values introduce broader emotional range for the voice. Higher values can result in a monotonous voice with limited emotion.
  use_speaker_boost: boolean or null
    Description: This setting boosts the similarity to the original speaker. Using this setting requires a slightly higher computational load, which in turn increases latency.
  similarity_boost: double or null
    Description: Determines how closely the AI should adhere to the original voice when attempting to replicate it.
  style: double or null
    Description: Determines the style exaggeration of the voice. This setting attempts to amplify the style of the original speaker. It does consume additional computational resources and might increase latency if set to anything other than 0.
  speed: double or null
    Description: Adjusts the speed of the voice. A value of 1.0 is the default speed, while values less than 1.0 slow down the speech, and values greater than 1.0 speed it up.

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: API Endpoint: Get Conversation Details
DESCRIPTION: Documents the REST API endpoint for retrieving details of a specific conversational AI conversation, including its HTTP method, URL path, required path parameters, and authentication headers.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/conversations/get

LANGUAGE: APIDOC
CODE:
```
GET /v1/convai/conversations/:conversation_id

Path Parameters:
  conversation_id (string, Required): The ID of the conversation to retrieve.

Headers:
  xi-api-key (string, Required): Your ElevenLabs API key for authentication.
```

----------------------------------------

TITLE: API Reference: Update PVC Voice Sample Endpoint
DESCRIPTION: This section provides comprehensive API documentation for the `POST /v1/voices/pvc/:voice_id/samples/:sample_id` endpoint. It details the path parameters, required headers, request body schema including optional parameters like `remove_background_noise` and `selected_speaker_ids`, and the structure of the successful response.

SOURCE: https://elevenlabs.io/docs/api-reference/voices/pvc/samples/update

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST https://api.elevenlabs.io/v1/voices/pvc/:voice_id/samples/:sample_id

Description: Update a PVC voice sample - apply noise removal, or select speaker.

Path Parameters:
  voice_id: string (Required)
    Description: Voice ID to be used, you can use https://api.elevenlabs.io/v1/voices to list all the available voices.
  sample_id: string (Required)
    Description: Sample ID to be used

Headers:
  xi-api-key: string (Required)

Request Body (object):
  remove_background_noise: boolean (Optional, Defaults to `false`)
    Description: If set will remove background noise for voice samples using our audio isolation model. If the samples do not include background noise, it can make the quality worse.
  selected_speaker_ids: list of strings or null (Optional)
    Description: Speaker IDs to be used for PVC training. Make sure you send all the speaker IDs you want to use for PVC training in one request because the last request will override the previous ones.
  trim_start_time: integer or null (Optional)
    Description: The start time of the audio to be used for PVC training. Time should be in milliseconds
  trim_end_time: integer or null (Optional)
    Description: The end time of the audio to be used for PVC training. Time should be in milliseconds

Response (200 Successful):
  voice_id: string
    Description: The ID of the voice.

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Retrieve Phone Number Details using ElevenLabs Python SDK
DESCRIPTION: This Python code demonstrates how to use the ElevenLabs SDK to fetch details for a specific phone number by its ID. It requires an API key for authentication.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/phone-numbers/get

LANGUAGE: Python
CODE:
```
from elevenlabs import ElevenLabs

client = ElevenLabs(
    api_key="YOUR_API_KEY",
)
client.conversational_ai.phone_numbers.get(
    phone_number_id="TeaqRRdTcIfIu2i7BYfT",
)
```

----------------------------------------

TITLE: New API Endpoint: List Voices (v2)
DESCRIPTION: Introduces an enhanced voice search capability with additional filtering options. This new version of the voice listing API provides more granular control over search results.

SOURCE: https://elevenlabs.io/docs/changelog/2025/3/24

LANGUAGE: APIDOC
CODE:
```
API Endpoint: /docs/api-reference/voices/search
Description: Enhanced voice search capabilities with additional filtering options
```

----------------------------------------

TITLE: Example Successful Response for ElevenLabs History List API
DESCRIPTION: This JSON object illustrates the structure of a successful response from the `GET /v1/history` endpoint. It includes an array of `history` items, each containing metadata about a generated audio, along with `has_more` and `last_history_item_id` for pagination.

SOURCE: https://elevenlabs.io/docs/api-reference/history/get-all

LANGUAGE: JSON
CODE:
```
{
"history": [
    {
    "history_item_id": "ja9xsmfGhxYcymxGcOGB",
    "date_unix": 1714650306,
    "character_count_change_from": 17189,
    "character_count_change_to": 17231,
    "content_type": "audio/mpeg",
    "state": null,
    "request_id": "BF0BZg4IwLGBlaVjv9Im",
    "voice_id": "21m00Tcm4TlvDq8ikWAM",
    "model_id": "eleven_multilingual_v2",
    "voice_name": "Rachel",
    "voice_category": "premade",
    "text": "Hello, world!",
    "settings": {
        "similarity_boost": 0.5,
        "stability": 0.71,
        "style": 0,
        "use_speaker_boost": true
    },
    "source": "TTS"
    }
],
"has_more": true,
"last_history_item_id": "ja9xsmfGhxYcymxGcOGB"
}
```

----------------------------------------

TITLE: API Reference: Create Pronunciation Dictionary from Rules
DESCRIPTION: Detailed API documentation for the POST /v1/pronunciation-dictionaries/add-from-rules endpoint. It specifies required headers, the structure of the request body (rules, name, description, workspace_access), and the fields returned in a successful response (id, name, created_by, creation_time_unix, version_id, version_rules_num, permission_on_resource, description). It also mentions the 422 Unprocessable Entity Error.

SOURCE: https://elevenlabs.io/docs/api-reference/pronunciation-dictionaries/create-from-rules

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/pronunciation-dictionaries/add-from-rules
Description: Creates a new pronunciation dictionary from provided rules.

Headers:
  xi-api-key: string (Required)

Request Body:
  Type: object
  Properties:
    rules: list of objects (Required)
      Description: List of pronunciation rules. Rule can be either: an alias rule: {'string_to_replace': 'a', 'type': 'alias', 'alias': 'b', } or a phoneme rule: {'string_to_replace': 'a', 'type': 'phoneme', 'phoneme': 'b', 'alphabet': 'ipa' }
    name: string (Required)
      Description: The name of the pronunciation dictionary, used for identification only.
    description: string or null (Optional)
      Description: A description of the pronunciation dictionary, used for identification only.
    workspace_access: enum (Optional)
      Allowed values: 'admin', 'editor', 'viewer'
      Description: Should be one of 'admin', 'editor' or 'viewer'. If not provided, defaults to no access.

Response (200 Successful):
  Type: object
  Properties:
    id: string
      Description: The ID of the created pronunciation dictionary.
    name: string
      Description: The name of the created pronunciation dictionary.
    created_by: string
      Description: The user ID of the creator of the pronunciation dictionary.
    creation_time_unix: integer
      Description: The creation time of the pronunciation dictionary in Unix timestamp.
    version_id: string
      Description: The ID of the created pronunciation dictionary version.
    version_rules_num: integer
      Description: The number of rules in the version of the pronunciation dictionary.
    permission_on_resource: enum or null
      Allowed values: 'admin', 'editor', 'viewer'
      Description: The permission on the resource of the pronunciation dictionary.
    description: string or null
      Description: The description of the pronunciation dictionary.

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Get Pronunciation Dictionary using cURL
DESCRIPTION: This cURL command demonstrates how to make a GET request to the Eleven Labs API to retrieve details of a specific pronunciation dictionary. It requires the `pronunciation_dictionary_id` as part of the URL path and an `xi-api-key` in the header for authentication.

SOURCE: https://elevenlabs.io/docs/api-reference/pronunciation-dictionaries/get

LANGUAGE: cURL
CODE:
```
curl https://api.elevenlabs.io/v1/pronunciation-dictionaries/pronunciation_dictionary_id \
-H "xi-api-key: xi-api-key"
```

----------------------------------------

TITLE: Access New Metric Breakdowns in Usage Analytics
DESCRIPTION: Expands the Usage Analytics section with additional metric breakdowns, including `minutes_used`, `request_count`, `ttfb_avg`, and `ttfb_p95`, selectable via the `metric` parameter, and introduces filtering by `request_queue`.

SOURCE: https://elevenlabs.io/docs/changelog/2025/4/28

LANGUAGE: APIDOC
CODE:
```
API Endpoint: Get Usage Metrics

GET /docs/api-reference/usage/get

Query Parameters:
  metric (string, optional): Selects the metric breakdown for usage analytics.
    New values: minutes_used, request_count, ttfb_avg, ttfb_p95.
  request_queue (string, optional): Filter usage metrics by request queue.
```

----------------------------------------

TITLE: Simulate Conversation API Successful Response JSON
DESCRIPTION: This JSON object represents a successful response (HTTP 200) from the 'Simulate conversation' API. It contains a `simulated_conversation` array detailing the turns of the conversation, including user messages, tool calls, and feedback, and an `analysis` object providing a summary of the call.

SOURCE: https://elevenlabs.io/docs/api-reference/agents/simulate-conversation

LANGUAGE: JSON
CODE:
```
{
"simulated_conversation": [
{
"role": "user",
"time_in_call_secs": 42,
"message": "foo",
"tool_calls": [
{
"request_id": "foo",
"tool_name": "foo",
"params_as_json": "foo",
"tool_has_been_called": true,
"type": "foo",
"tool_details": {
"type": "webhook",
"method": "foo",
"url": "foo",
"headers": {},
"path_params": {},
"query_params": {},
"body": "foo"
}
}
],
"tool_results": [
{
"request_id": "foo",
"tool_name": "foo",
"result_value": "foo",
"is_error": true,
"tool_has_been_called": true,
"type": "foo",
"tool_latency_secs": 0
}
],
"feedback": {
"score": "like",
"time_in_call_secs": 42
},
"llm_override": "foo",
"conversation_turn_metrics": {
"metrics": {}
},
"rag_retrieval_info": {
"chunks": [
{
"document_id": "foo",
"chunk_id": "foo",
"vector_distance": 42
}
],
"embedding_model": "e5_mistral_7b_instruct",
"retrieval_query": "foo",
"rag_latency_secs": 42
},
"llm_usage": {
"model_usage": {}
},
"interrupted": false,
"original_message": "foo",
"source_medium": "audio"
}
],
"analysis": {
"call_successful": "success",
"transcript_summary": "foo",
"evaluation_criteria_results": {},
"data_collection_results": {}
}
}
```

----------------------------------------

TITLE: Deprecated API Endpoints
DESCRIPTION: Legacy Knowledge Base endpoints have been deprecated and should no longer be used.

SOURCE: https://elevenlabs.io/docs/changelog/2025/2/4

LANGUAGE: APIDOC
CODE:
```
Deprecated Knowledge Base legacy endpoints:
  POST /v1/convai/agents/{agent_id}/add-to-knowledge-base
  GET /v1/convai/agents/{agent_id}/knowledge-base/{documentation_id}
```

----------------------------------------

TITLE: API Reference: Retry Conversational AI Batch Calling Job
DESCRIPTION: This section documents the API endpoint for retrying a batch calling job within ElevenLabs' Conversational AI. It details the HTTP method, endpoint URL, required path parameters, headers, and the structure of a successful 200 OK response, including an example JSON body.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/batch-calling/retry

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/convai/batch-calling/:batch_id/retry
Description: Retry a batch call by setting completed recipients back to pending status.

Path Parameters:
  batch_id:
    Type: string
    Required: true
    Description: The ID of the batch calling job to retry.

Headers:
  xi-api-key:
    Type: string
    Required: true
    Description: Your ElevenLabs API key.

Responses:
  200 Successful:
    Description: Batch calling job successfully retried.
    Body:
      id: string
      phone_number_id: string
      name: string
      agent_id: string
      created_at_unix: number
      scheduled_time_unix: number
      total_calls_dispatched: number
      total_calls_scheduled: number
      last_updated_at_unix: number
      status: string
      agent_name: string
      phone_provider: string
```

LANGUAGE: JSON
CODE:
```
{
  "id": "foo",
  "phone_number_id": "foo",
  "name": "foo",
  "agent_id": "foo",
  "created_at_unix": 42,
  "scheduled_time_unix": 42,
  "total_calls_dispatched": 42,
  "total_calls_scheduled": 42,
  "last_updated_at_unix": 42,
  "status": "pending",
  "agent_name": "foo",
  "phone_provider": "twilio"
}
```

----------------------------------------

TITLE: Added API Parameters, Properties, and Fields
DESCRIPTION: New parameters, properties, and fields added to existing API endpoints and response objects to enhance functionality, access control, data retention, and usage metrics.

SOURCE: https://elevenlabs.io/docs/changelog/2025/2/4

LANGUAGE: APIDOC
CODE:
```
Workspace Invite endpoint:
  Parameter: group_ids
  Description: For group-based access control.
Chapter response objects:
  Property: content (structured)
Agent creation:
  Parameters: retention_days, delete_transcript_and_pii
  Description: Data retention parameters.
AudioNative content response:
  Property: project_id (structured)
User endpoint:
  Metric: convai_chars_per_minute
  Description: Usage metric.
Dubbing response objects:
  Field: media_metadata
Conversation responses:
  Setting: deletion_settings (GDPR-compliant)
  Path: metadata.deletion_settings
```

----------------------------------------

TITLE: New ElevenLabs API Endpoints
DESCRIPTION: This section documents the newly added API endpoints for managing workspace members and comprehensive operations related to Private Voice Cloning (PVC) voices. These operations include creation, editing, sample management, verification, and training processes.

SOURCE: https://elevenlabs.io/docs/changelog

LANGUAGE: APIDOC
CODE:
```
- Delete Member: Allows deleting workspace members.
- Create PVC Voice: Creates a new PVC voice.
- Edit PVC Voice: Edits PVC voice metadata.
- Add Samples To PVC Voice: Adds audio samples to a PVC voice.
- Update PVC Voice Sample: Updates a PVC voice sample (noise removal, speaker selection, trimming).
- Delete PVC Voice Sample: Deletes a sample from a PVC voice.
- Retrieve Voice Sample Audio: Retrieves audio for a PVC voice sample.
- Retrieve Voice Sample Visual Waveform: Retrieves the visual waveform for a PVC voice sample.
- Retrieve Speaker Separation Status: Gets the status of speaker separation for a sample.
- Start Speaker Separation: Initiates speaker separation for a sample.
- Retrieve Separated Speaker Audio: Retrieves audio for a specific separated speaker.
- Get PVC Voice Captcha: Gets the captcha for PVC voice verification.
- Verify PVC Voice Captcha: Submits captcha verification for a PVC voice.
- Run PVC Training: Starts the training process for a PVC voice.
- Request Manual Verification: Requests manual verification for a PVC voice.
```

----------------------------------------

TITLE: Agent Transfer Tool API Definition and JSON Call Example
DESCRIPTION: Defines the API for the `transfer_to_agent` function, used to transfer conversations between specialized AI agents based on user needs. It specifies trigger conditions, required and optional parameters, and provides a JSON example of how to invoke this function.

SOURCE: https://elevenlabs.io/docs/conversational-ai/customization/llm/custom-llm

LANGUAGE: APIDOC
CODE:
```
Function: transfer_to_agent
Purpose: Transfer conversations between specialized AI agents based on user needs.
Trigger conditions:
  - User request requires specialized knowledge or different agent capabilities
  - Current agent cannot adequately handle the query
  - Conversation flow indicates need for different agent type
Parameters:
  - reason (string, optional): The reason for the agent transfer
  - agent_number (integer, required): Zero-indexed number of the agent to transfer to (based on configured transfer rules)
```

LANGUAGE: JSON
CODE:
```
{
"type": "function",
"function": {
"name": "transfer_to_agent",
"arguments": "{\"reason\": \"User needs billing support\", \"agent_number\": 0}"
}
}
```

----------------------------------------

TITLE: New Endpoint to Delete Workspace Members
DESCRIPTION: A new API endpoint has been introduced to allow administrators to delete members from a workspace. This enhances administrative control over workspace user management.

SOURCE: https://elevenlabs.io/docs/changelog

LANGUAGE: APIDOC
CODE:
```
New Endpoint: DELETE /docs/api-reference/workspace/delete-member
Description: Allows administrators to delete workspace members.
```

----------------------------------------

TITLE: New API Endpoint: Share Workspace Resource
DESCRIPTION: Introduces a new API endpoint to share a workspace resource.

SOURCE: https://elevenlabs.io/docs/changelog/2025/3/17

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /docs/api-reference/workspace/share-workspace-resource
Description: Share workspace resource
```

----------------------------------------

TITLE: Retrieve Knowledge Base Document with cURL
DESCRIPTION: This cURL command demonstrates how to fetch details of a specific document within an agent's knowledge base using its unique ID. It requires an API key passed in the 'xi-api-key' header for authentication.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/knowledge-base/get-document

LANGUAGE: cURL
CODE:
```
curl https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id \
-H "xi-api-key: xi-api-key"
```

----------------------------------------

TITLE: ElevenLabs Dubbing Transcript API Endpoint Reference
DESCRIPTION: This section provides the full API documentation for retrieving dubbed transcripts. It specifies the HTTP method, endpoint path, required path parameters, headers, optional query parameters for format selection, and the expected successful response format, along with potential error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/dubbing/transcript/get-transcript-for-dub

LANGUAGE: APIDOC
CODE:
```
GET /v1/dubbing/:dubbing_id/transcript/:language_code

Path parameters:
  dubbing_id: string (Required)
    ID of the dubbing project.
  language_code: string (Required)
    ID of the language.

Headers:
  xi-api-key: string (Required)

Query parameters:
  format_type: enum (Optional, Defaults to `srt`)
    Format to use for the subtitle file, either 'srt' or 'webvtt'
    Allowed values: srt, webvtt

Response: 200 Retrieved
  Returns transcript for the dub as an SRT or WEBVTT file.

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Initiate Outbound Call via SIP Trunk
DESCRIPTION: This snippet provides the API reference and code examples for initiating an outbound call using ElevenLabs' conversational AI via a SIP trunk. It includes the Python SDK usage, the full API endpoint specification, and an example of a successful JSON response.

SOURCE: https://elevenlabs.io/docs/api-reference/sip-trunk/outbound-call

LANGUAGE: Python
CODE:
```
from elevenlabs import ElevenLabs

client = ElevenLabs(
    api_key="YOUR_API_KEY",
)
client.conversational_ai.sip_trunk.outbound_call(
    agent_id="agent_id",
    agent_phone_number_id="agent_phone_number_id",
    to_number="to_number",
)
```

LANGUAGE: APIDOC
CODE:
```
# Outbound call via SIP trunk

## Endpoint
POST /v1/convai/sip-trunk/outbound-call
Full URL: https://api.elevenlabs.io/v1/convai/sip-trunk/outbound-call

## Headers
- xi-api-key: string (Required)

## Request Body
This endpoint expects an object with the following properties:
- agent_id: string (Required)
- agent_phone_number_id: string (Required)
- to_number: string (Required)
- conversation_initiation_client_data: object or null (Optional)

## Response (200 Successful)
Object with the following properties:
- success: boolean
- message: string
- conversation_id: string or null
- sip_call_id: string or null

## Errors
- 422 Unprocessable Entity Error
```

LANGUAGE: JSON
CODE:
```
{
  "success": true,
  "message": "foo",
  "conversation_id": "foo",
  "sip_call_id": "foo"
}
```

----------------------------------------

TITLE: Invite User to ElevenLabs Workspace (TypeScript)
DESCRIPTION: This TypeScript code snippet demonstrates how to programmatically invite a new user to an ElevenLabs workspace using the official `@elevenlabs/elevenlabs-js` client library. It requires an API key for authentication and sends an invitation email to the specified address.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/invite-user

LANGUAGE: TypeScript
CODE:
```
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient({ apiKey: "YOUR_API_KEY" });
await client.workspace.invites.create({
  email: "john.doe@testmail.com"
});
```

----------------------------------------

TITLE: Example JSON Response for Get Document Chunk
DESCRIPTION: This JSON snippet illustrates the structure of a successful response when retrieving a document chunk from the ElevenLabs knowledge base API. It includes the chunk's ID, name, and content.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/knowledge-base/get-chunk

LANGUAGE: JSON
CODE:
```
{
  "id": "foo",
  "name": "foo",
  "content": "foo"
}
```

----------------------------------------

TITLE: ElevenLabs Transcription API Request Parameters
DESCRIPTION: Defines the parameters accepted by the ElevenLabs transcription endpoint for audio and video file processing. It supports various options for model selection, language, speaker diarization, and output formats.

SOURCE: https://elevenlabs.io/docs/api-reference/speech-to-text/convert

LANGUAGE: APIDOC
CODE:
```
model_id: string (Required)
  Description: The ID of the model to use for transcription, currently only ‘scribe_v1’ and ‘scribe_v1_experimental’ are available.
file: file (Optional)
  Description: The file to transcribe. All major audio and video formats are supported. Exactly one of the file or cloud_storage_url parameters must be provided. The file size must be less than 1GB.
language_code: string or null (Optional)
  Description: An ISO-639-1 or ISO-639-3 language_code corresponding to the language of the audio file. Can sometimes improve transcription performance if known beforehand. Defaults to null, in this case the language is predicted automatically.
tag_audio_events: boolean (Optional, Defaults to true)
  Description: Whether to tag audio events like (laughter), (footsteps), etc. in the transcription.
num_speakers: integer or null (Optional, >=1, <=32)
  Description: The maximum amount of speakers talking in the uploaded file. Can help with predicting who speaks when. The maximum amount of speakers that can be predicted is 32. Defaults to null, in this case the amount of speakers is set to the maximum value the model supports.
timestamps_granularity: enum (Optional, Defaults to word)
  Allowed values: none, word, character
  Description: The granularity of the timestamps in the transcription. ‘word’ provides word-level timestamps and ‘character’ provides character-level timestamps per word.
diarize: boolean (Optional, Defaults to false)
  Description: Whether to annotate which speaker is currently talking in the uploaded file.
additional_formats: list of objects (Optional)
  Description: A list of additional formats to export the transcript to.
file_format: enum (Optional, Defaults to other)
  Allowed values: pcm_s16le_16, other
  Description: The format of input audio. Options are ‘pcm_s16le_16’ or ‘other’ For pcm_s16le_16, the input audio must be 16-bit PCM at a 16kHz sample rate, single channel (mono), and little-endian byte order. Latency will be lower than with passing an encoded waveform.
cloud_storage_url: string or null (Optional)
  Description: The valid AWS S3, Cloudflare R2 or Google Cloud Storage URL of the file to transcribe. Exactly one of the file or cloud_storage_url parameters must be provided. The file must be a valid publicly accessible cloud storage URL. The file size must be less than 2GB. URL can be pre-signed.
webhook: boolean (Optional, Defaults to false)
  Description: Whether to send the transcription result to configured speech-to-text webhooks. If set the request will return early without the transcription, which will be delivered later via webhook.
temperature: double or null (Optional, >=0, <=2)
  Description: Controls the randomness of the transcription output. Accepts values between 0.0 and 2.0, where higher values result in more diverse and less deterministic results. If omitted, we will use a temperature based on the model you selected which is usually 0.
```

----------------------------------------

TITLE: ElevenLabs Studio API: Create Project Error Responses
DESCRIPTION: Lists possible error codes returned by the Create Project endpoint.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/create-podcast

LANGUAGE: APIDOC
CODE:
```
422: Unprocessable Entity Error
```

----------------------------------------

TITLE: List Available ElevenLabs AI Models
DESCRIPTION: This snippet documents the ElevenLabs API endpoint for retrieving a list of all available AI models. It includes the HTTP method, endpoint path, a TypeScript client example for making the request, and a detailed schema of the expected successful response, including model properties and error handling.

SOURCE: https://elevenlabs.io/docs/api-reference/models/list

LANGUAGE: APIDOC
CODE:
```
GET /v1/models
https://api.elevenlabs.io/v1/models

Headers:
  xi-api-key: string (Required)
```

LANGUAGE: TypeScript
CODE:
```
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient({ apiKey: "YOUR_API_KEY" });
await client.models.list();
```

LANGUAGE: JSON
CODE:
```
[
  {
    "model_id": "foo",
    "name": "foo",
    "can_be_finetuned": true,
    "can_do_text_to_speech": true,
    "can_do_voice_conversion": true,
    "can_use_style": true,
    "can_use_speaker_boost": true,
    "serves_pro_voices": true,
    "token_cost_factor": 42,
    "description": "foo",
    "requires_alpha_access": true,
    "max_characters_request_free_user": 42,
    "max_characters_request_subscribed_user": 42,
    "maximum_text_length_per_request": 42,
    "languages": [
      {
        "language_id": "foo",
        "name": "foo"
      }
    ],
    "model_rates": {
      "character_cost_multiplier": 42
    },
    "concurrency_group": "standard"
  }
]
```

LANGUAGE: APIDOC
CODE:
```
Response:
  model_id: string (The unique identifier of the model.)
  name: string or null (The name of the model.)
  can_be_finetuned: boolean or null (Whether the model can be finetuned.)
  can_do_text_to_speech: boolean or null (Whether the model can do text-to-speech.)
  can_do_voice_conversion: boolean or null (Whether the model can do voice conversion.)
  can_use_style: boolean or null (Whether the model can use style.)
  can_use_speaker_boost: boolean or null (Whether the model can use speaker boost.)
  serves_pro_voices: boolean or null (Whether the model serves pro voices.)
  token_cost_factor: double or null (The cost factor for the model.)
  description: string or null (The description of the model.)
  requires_alpha_access: boolean or null (Whether the model requires alpha access.)
  max_characters_request_free_user: integer or null (The maximum number of characters that can be requested by a free user.)
  max_characters_request_subscribed_user: integer or null (The maximum number of characters that can be requested by a subscribed user.)
  maximum_text_length_per_request: integer or null (The maximum length of text that can be requested for this model.)
  languages: list of objects or null (The languages supported by the model.)
    language_id: string
    name: string
  model_rates: object or null (The rates for the model.)
    character_cost_multiplier: number
  concurrency_group: enum or null (The concurrency group for the model.)
    Allowed values: standard, turbo

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Invite User to ElevenLabs Workspace with TypeScript SDK
DESCRIPTION: This snippet demonstrates how to use the ElevenLabs TypeScript SDK (`@elevenlabs/elevenlabs-js`) to send an email invitation to a user to join your workspace. It requires an API key for authentication and the recipient's email address. The `create` method of the `client.workspace.invites` object is used for this operation.

SOURCE: https://elevenlabs.io/docs/api-reference/workspace/invites/create

LANGUAGE: TypeScript
CODE:
```
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient({ apiKey: "YOUR_API_KEY" });
await client.workspace.invites.create({
  email: "john.doe@testmail.com"
});
```

----------------------------------------

TITLE: Download Pronunciation Dictionary Version using cURL
DESCRIPTION: This cURL command demonstrates how to download a specific version of a pronunciation dictionary from the ElevenLabs API. It requires replacing placeholders for `dictionary_id`, `version_id`, and `xi-api-key` with actual values. The command uses an `xi-api-key` header for authentication.

SOURCE: https://elevenlabs.io/docs/api-reference/pronunciation-dictionaries/download

LANGUAGE: cURL
CODE:
```
curl https://api.elevenlabs.io/v1/pronunciation-dictionaries/dictionary_id/version_id/download \\
-H "xi-api-key: xi-api-key"
```

----------------------------------------

TITLE: New API Endpoint: Add Pronunciation Dictionary from Rules
DESCRIPTION: Enables the creation of pronunciation dictionaries directly from defined rules, eliminating the need for file uploads. This simplifies the process of customizing pronunciation.

SOURCE: https://elevenlabs.io/docs/changelog/2025/3/24

LANGUAGE: APIDOC
CODE:
```
API Endpoint: /docs/api-reference/pronunciation-dictionary/add-rules
Description: Create pronunciation dictionaries directly from rules without file upload
```

----------------------------------------

TITLE: New Conversational AI API Endpoints
DESCRIPTION: Introduces six new API endpoints for Conversational AI, covering functionalities like getting signed URLs for conversations, simulating agent-user interactions (both standard and streaming), updating workspace secrets, and managing batch call requests.

SOURCE: https://elevenlabs.io/docs/changelog/2025/5/19

LANGUAGE: APIDOC
CODE:
```
GET /docs/conversational-ai/api-reference/conversations/get-signed-url - Get a signed URL to start a conversation with an agent that requires authorization.
POST /docs/conversational-ai/api-reference/agents/simulate-conversation - Run a conversation between an agent and a simulated user.
POST /docs/conversational-ai/api-reference/agents/simulate-conversation-stream - Run and stream a conversation simulation between an agent and a simulated user.
PATCH /docs/conversational-ai/api-reference/workspace/secrets/update-secret - Update an existing secret for the Convai workspace.
POST /docs/conversational-ai/api-reference/batch-calling/create - Submit a batch call request to schedule calls for multiple recipients.
GET /docs/conversational-ai/api-reference/batch-calling/list - Retrieve all batch calls for the current workspace.
```

----------------------------------------

TITLE: Python: List Workspace Batch Calling Jobs
DESCRIPTION: Demonstrates how to programmatically list all batch calling jobs for the current workspace using the ElevenLabs Python client library. This example initializes the client with an API key and then calls the `list()` method on the `conversational_ai.batch_calls` object.

SOURCE: https://elevenlabs.io/docs/conversational-ai/api-reference/batch-calling/list

LANGUAGE: Python
CODE:
```
from elevenlabs import ElevenLabs

client = ElevenLabs(
    api_key="YOUR_API_KEY",
)
client.conversational_ai.batch_calls.list()
```

----------------------------------------

TITLE: ElevenLabs Usage Analytics API Update
DESCRIPTION: Describes the updated `GET /v1/usage/character-stats` endpoint, which now includes optional `aggregation_interval` and `metric` query parameters for more flexible usage data retrieval.

SOURCE: https://elevenlabs.io/docs/changelog/2025/4/28

LANGUAGE: APIDOC
CODE:
```
Endpoint: GET /v1/usage/character-stats
Description: Get Usage Metrics
Update: Added optional query parameters `aggregation_interval` and `metric`.
```

----------------------------------------

TITLE: ElevenLabs Text-to-Speech API Reference: Create Speech
DESCRIPTION: This section details the `POST /v1/text-to-speech/:voice_id` API endpoint, which converts text into speech using a specified voice. It outlines the required path and header parameters, along with optional query parameters like `enable_logging`, `optimize_streaming_latency`, and `output_format`, explaining their purpose and possible values.

SOURCE: https://elevenlabs.io/docs/api-reference/text-to-speech/convert

LANGUAGE: APIDOC
CODE:
```
POST /v1/text-to-speech/:voice_id

Converts text into speech using a voice of your choice and returns audio.

Path parameters:
  voice_id: string (Required)
    ID of the voice to be used. Use the Get voices endpoint list all the available voices.

Headers:
  xi-api-key: string (Required)

Query parameters:
  enable_logging: boolean (Optional, Defaults to true)
    When enable_logging is set to false zero retention mode will be used for the request. This will mean history features are unavailable for this request, including request stitching. Zero retention mode may only be used by enterprise customers.
  optimize_streaming_latency: integer or null (Optional, Deprecated)
    You can turn on latency optimizations at some cost of quality. The best possible final latency varies by model. Possible values:
    0 - default mode (no latency optimizations)
    1 - normal latency optimizations (about 50% of possible latency improvement of option 3)
    2 - strong latency optimizations (about 75% of possible latency improvement of option 3)
    3 - max latency optimizations
    4 - max latency optimizations, but also with text normalizer turned off for even more latency savings (best latency, but can mispronounce eg numbers and dates).
    Defaults to None.
  output_format: enum (Optional, Defaults to mp3_44100_128)
    Output format of the generated audio. Formatted as codec_sample_rate_bitrate. So an mp3 with 22.05kHz sample rate at 32kbs is represented as mp3_22050_32. MP3 with 192kbps bitrate requires you to be subscribed to Creator tier or above. PCM with 44.1kHz sample rate requires you to be subscribed to Pro tier or above.
    Note that the μ-law format (sometimes written mu-law, often approximated as u-law) is commonly used for Twilio audio inputs.
```

----------------------------------------

TITLE: Eleven Labs API: Audio Isolation Stream Endpoint Reference
DESCRIPTION: Detailed API documentation for the Eleven Labs audio isolation stream endpoint, outlining the HTTP method, URL, required headers, request body parameters, and possible error responses. This endpoint is used to remove background noise from audio files.

SOURCE: https://elevenlabs.io/docs/api-reference/audio-isolation/stream

LANGUAGE: APIDOC
CODE:
```
Endpoint:
  Method: POST
  URL: https://api.elevenlabs.io/v1/audio-isolation/stream

Headers:
  xi-api-key: string (Required)

Request Body (multipart/form-data):
  audio: file (Required)
    Description: The audio file from which vocals/speech will be isolated from.
  file_format: enum or null (Optional)
    Description: The format of input audio. Defaults to `other`. For `pcm_s16le_16`, the input audio must be 16-bit PCM at a 16kHz sample rate, single channel (mono), and little-endian byte order. Latency will be lower than with passing an encoded waveform.
    Allowed values: pcm_s16le_16, other

Errors:
  422: Unprocessable Entity Error
```

----------------------------------------

TITLE: Create Studio Project from JSON Content
DESCRIPTION: Adds `from_content_json` parameter to the 'Create Studio project' endpoint, facilitating JSON-based project setup.

SOURCE: https://elevenlabs.io/docs/changelog/2025/6/17

LANGUAGE: APIDOC
CODE:
```
POST /studio/add-project
Path: request.body.from_content_json
Parameter Added: from_content_json (object)
  Description: Used for JSON-based project setup.
```

----------------------------------------

TITLE: ElevenLabs API: Delete RAG Index Endpoint Reference
DESCRIPTION: This section details the ElevenLabs API endpoint for deleting a RAG index. It specifies the HTTP method (DELETE), the full URL path with required parameters, expected headers, and the structure of a successful response, including possible error codes.

SOURCE: https://elevenlabs.io/docs/api-reference/knowledge-base/delete-document-rag-index

LANGUAGE: APIDOC
CODE:
```
DELETE https://api.elevenlabs.io/v1/convai/knowledge-base/:documentation_id/rag-index/:rag_index_id

Path Parameters:
  documentation_id: string (Required)
    Description: The id of a document from the knowledge base. This is returned on document addition.
  rag_index_id: string (Required)
    Description: The id of RAG index of document from the knowledge base.

Headers:
  xi-api-key: string (Required)

Responses:
  200 OK:
    Description: Deleted
    Example Body:
      {
        "id": "foo",
        "model": "e5_mistral_7b_instruct",
        "status": "created",
        "progress_percentage": 42,
        "document_model_index_usage": {
          "used_bytes": 42
        }
      }
    Schema:
      id: string
      model: enum (Allowed values: e5_mistral_7b_instruct, multilingual_e5_large_instruct, ...)
      status: enum (Show 6 enum values)
      progress_percentage: double
      document_model_index_usage: object
        Properties:
          used_bytes: integer
  422 Unprocessable Entity Error
```

----------------------------------------

TITLE: API Endpoint: Update Studio Project Content
DESCRIPTION: Defines the HTTP POST endpoint for updating content within an Eleven Labs Studio project. It specifies the URL path, required path parameters, and necessary headers for authentication.

SOURCE: https://elevenlabs.io/docs/api-reference/studio/update-content

LANGUAGE: APIDOC
CODE:
```
POST https://api.elevenlabs.io/v1/studio/projects/:project_id/content

Path parameters:
  project_id: string (Required)
    Description: The ID of the project to be used. You can use the [List projects](/docs/api-reference/studio/get-projects) endpoint to list all the available projects.

Headers:
  xi-api-key: string (Required)
    Description: Your Eleven Labs API key.
```

----------------------------------------

TITLE: Eleven Labs API: Audio Isolation Stream Endpoint Reference
DESCRIPTION: This comprehensive API documentation details the Eleven Labs audio isolation stream endpoint. It specifies the POST method, full URL, required headers, multipart form data parameters for audio input and format, and potential error responses.

SOURCE: https://elevenlabs.io/docs/api-reference/audio-isolation/audio-isolation-stream

LANGUAGE: APIDOC
CODE:
```
Endpoint: POST /v1/audio-isolation/stream
Full URL: https://api.elevenlabs.io/v1/audio-isolation/stream

Headers:
  xi-api-key: string (Required)

Request Body (multipart/form-data):
  audio: file (Required)
    Description: The audio file from which vocals/speech will be isolated from.
  file_format: enum or null (Optional, Defaults to 'other')
    Description: The format of input audio. Options are 'pcm_s16le_16' or 'other'. For 'pcm_s16le_16', the input audio must be 16-bit PCM at a 16kHz sample rate, single channel (mono), and little-endian byte order. Latency will be lower than with passing an encoded waveform.
    Allowed values: pcm_s16le_16, other

Errors:
  422: Unprocessable Entity Error - Unprocessable Entity Error
```

----------------------------------------

TITLE: ElevenLabs Forced Alignment API Endpoint Specification
DESCRIPTION: This section provides the full API specification for the `POST /v1/forced-alignment` endpoint. It details the HTTP method, URL, required `xi-api-key` header, multipart form data parameters (`file`, `text`, `enabled_spooled_file`), the structure of the successful 200 OK response including `characters` and `words` arrays, and potential error codes like 422.

SOURCE: https://elevenlabs.io/docs/api-reference/forced-alignment

LANGUAGE: APIDOC
CODE:
```
POST /v1/forced-alignment
https://api.elevenlabs.io/v1/forced-alignment

Headers:
  xi-api-key: string (Required)

Request Body (multipart/form-data):
  file: file (Required)
    Description: The file to align. All major audio formats are supported. The file size must be less than 1GB.
  text: string (Required)
    Description: The text to align with the audio. The input text can be in any format, however diarization is not supported at this time.
  enabled_spooled_file: boolean (Optional, Defaults to `false`)
    Description: If true, the file will be streamed to the server and processed in chunks. This is useful for large files that cannot be loaded into memory.

Response (200 Successful):
  Content-Type: application/json
  Body:
    {
      "characters": [
        {
          "text": "foo",
          "start": 42,
          "end": 42
        }
      ],
      "words": [
        {
          "text": "foo",
          "start": 42,
          "end": 42
        }
      ]
    }
  Properties:
    characters: list of objects
      Description: List of characters with their timing information.
      Properties: text (string), start (number), end (number)
    words: list of objects
      Description: List of words with their timing information.
      Properties: text (string), start (number), end (number)

Errors:
  422: Unprocessable Entity Error
```