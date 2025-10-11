
"""
OpenAI Agent Builder Implementation Pattern
Based on the workflow concepts from the video
"""

import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

class OutputFormat(Enum):
    TEXT = "text"
    JSON = "json" 
    WIDGET = "widget"

@dataclass
class WorkflowNode:
    """Represents a node in the agent workflow"""
    id: str
    type: str  # 'agent', 'condition', 'tool'
    config: Dict[str, Any]
    next_nodes: List[str] = None

class AgentWorkflow:
    """
    Implementation of OpenAI Agent Builder workflow pattern
    """
    
    def __init__(self, name: str):
        self.name = name
        self.nodes = {}
        self.start_node = None
        self.tools = {}
        
    def add_agent_node(self, node_id: str, instructions: str, tools: List[str] = None, output_format: OutputFormat = OutputFormat.TEXT):
        """Add an agent node to the workflow"""
        node = WorkflowNode(
            id=node_id,
            type="agent",
            config={
                "instructions": instructions,
                "tools": tools or [],
                "output_format": output_format.value
            }
        )
        self.nodes[node_id] = node
        return node
        
    def add_condition_node(self, node_id: str, condition: str, true_branch: str, false_branch: str):
        """Add a conditional branching node"""
        node = WorkflowNode(
            id=node_id,
            type="condition",
            config={
                "condition": condition,
                "true_branch": true_branch,
                "false_branch": false_branch
            }
        )
        self.nodes[node_id] = node
        return node
        
    def add_tool(self, tool_name: str, tool_config: Dict[str, Any]):
        """Register a tool for use in agents"""
        self.tools[tool_name] = tool_config
        
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the workflow with given input"""
        current_node_id = self.start_node
        context = {"input": input_data, "outputs": {}}
        
        while current_node_id:
            node = self.nodes.get(current_node_id)
            if not node:
                break
                
            if node.type == "agent":
                # Execute agent logic
                result = self._execute_agent(node, context)
                context["outputs"][node.id] = result
                current_node_id = node.next_nodes[0] if node.next_nodes else None
                
            elif node.type == "condition":
                # Evaluate condition
                if self._evaluate_condition(node.config["condition"], context):
                    current_node_id = node.config["true_branch"]
                else:
                    current_node_id = node.config["false_branch"]
                    
        return context["outputs"]
        
    def _execute_agent(self, node: WorkflowNode, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an agent node"""
        # Simulate agent execution
        return {
            "text": f"Agent {node.id} executed with instructions: {node.config['instructions'][:50]}...",
            "format": node.config["output_format"]
        }
        
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a condition string"""
        # Simple evaluation - in practice would use safe eval
        try:
            # Example: "input.type == 'weather'"
            if "==" in condition:
                parts = condition.split("==")
                left = parts[0].strip()
                right = parts[1].strip().strip("'").strip('"')
                
                # Navigate context
                value = context
                for key in left.split('.'):
                    value = value.get(key, {})
                    
                return str(value) == right
        except:
            pass
        return False

# Example workflow creation matching the video pattern
def create_example_workflow():
    """Create an example workflow similar to the video demonstration"""
    
    workflow = AgentWorkflow("Multi-Agent Assistant")
    
    # Add tools
    workflow.add_tool("web_search", {
        "description": "Search the internet for information",
        "endpoint": "/api/search"
    })
    
    workflow.add_tool("code_interpreter", {
        "description": "Execute Python code",
        "endpoint": "/api/execute"
    })
    
    # Add nodes
    router = workflow.add_condition_node(
        "router",
        "input.query_type == 'web'",
        "web_agent",
        "general_agent"
    )
    
    web_agent = workflow.add_agent_node(
        "web_agent",
        "You are a web search specialist. Search for: {input.query}",
        tools=["web_search"],
        output_format=OutputFormat.JSON
    )
    
    general_agent = workflow.add_agent_node(
        "general_agent", 
        "You are a helpful assistant. Answer: {input.query}",
        output_format=OutputFormat.TEXT
    )
    
    # Set flow
    workflow.start_node = "router"
    router.next_nodes = None  # Handled by condition
    web_agent.next_nodes = None
    general_agent.next_nodes = None
    
    return workflow

if __name__ == "__main__":
    # Create and test workflow
    workflow = create_example_workflow()
    
    # Test with web query
    result = workflow.execute({
        "query_type": "web",
        "query": "Latest AI news"
    })
    print("Web Query Result:", json.dumps(result, indent=2))
    
    # Test with general query
    result = workflow.execute({
        "query_type": "general",
        "query": "Tell me a joke"
    })
    print("\nGeneral Query Result:", json.dumps(result, indent=2))
