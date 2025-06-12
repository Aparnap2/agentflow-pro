#!/usr/bin/env python3
"""Test the agent API endpoints."""
import asyncio
import httpx
import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.core.config import settings

# API client configuration
BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {"Content-Type": "application/json"}

async def test_create_agent() -> Dict[str, Any]:
    """Test creating a new agent."""
    url = f"{BASE_URL}/agents"
    payload = {
        "name": "Test Agent",
        "description": "A test agent created via API",
        "agent_type": "general",
        "tools": [
            {
                "name": "test_tool",
                "description": "A test tool",
                "parameters": {"param1": "value1"},
                "enabled": True
            }
        ],
        "llm_config": {
            "model": "deepseek-chat",
            "temperature": 0.7,
            "max_tokens": 2000
        },
        "metadata": {"test": "value"},
        "tags": ["test", "api"]
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=HEADERS)
        response.raise_for_status()
        return response.json()

async def test_list_agents() -> Dict[str, Any]:
    """Test listing all agents."""
    url = f"{BASE_URL}/agents"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()

async def test_get_agent(agent_id: str) -> Dict[str, Any]:
    """Test getting a single agent by ID."""
    url = f"{BASE_URL}/agents/{agent_id}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()

async def test_process_task(agent_id: str) -> Dict[str, Any]:
    """Test processing a task with an agent."""
    url = f"{BASE_URL}/agents/{agent_id}/process"
    payload = {
        "task": "Tell me a joke about AI",
        "context": {"user_id": "test_user_123"},
        "stream": False
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=HEADERS)
        response.raise_for_status()
        return response.json()

async def run_tests():
    """Run all API tests."""
    print("Starting API tests...\n")
    
    try:
        # Test 1: Create a new agent
        print("1. Testing agent creation...")
        created_agent = await test_create_agent()
        agent_id = created_agent["id"]
        print(f"✅ Created agent with ID: {agent_id}")
        print(json.dumps(created_agent, indent=2))
        
        # Test 2: List all agents
        print("\n2. Testing agent listing...")
        agents = await test_list_agents()
        print(f"✅ Found {agents['total']} agents")
        
        # Test 3: Get the created agent
        print(f"\n3. Testing get agent (ID: {agent_id})...")
        agent = await test_get_agent(agent_id)
        print(f"✅ Retrieved agent: {agent['name']}")
        
        # Test 4: Process a task with the agent
        print("\n4. Testing task processing...")
        task_result = await test_process_task(agent_id)
        print("✅ Task processed successfully")
        print(f"Task ID: {task_result['task_id']}")
        print(f"Status: {task_result['status']}")
        print(f"Result: {task_result.get('result', {}).get('output', 'No output')}")
        
        print("\n✅ All tests passed!")
        
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP error: {e}")
        if e.response.content:
            print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_tests())
