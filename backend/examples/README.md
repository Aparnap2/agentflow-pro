# AgentFlow Pro Examples

This directory contains example scripts demonstrating how to use the AgentFlow Pro platform.

## Available Examples

### 1. Workflow Example

**File:** `workflow_example.py`

This example demonstrates how to:
- Initialize the LangGraphOrchestrator
- Create and execute agent workflows
- Process tasks through multiple agents
- Handle workflow results

#### Running the Example

```bash
# From the backend directory
python -m examples.workflow_example
```

#### Expected Output

```
INFO:__main__:Starting workflow example...
INFO:__main__:Initializing services...
INFO:__main__:Creating orchestrator...
INFO:__main__:
Processing task: Review NDA for new client
INFO:__main__:Description: We need to review the NDA for our new client Acme Corp. Please analyze the terms and highlight any potential risks.
...
```

## Customizing Examples

You can modify the example scripts to:
1. Change the sample tasks in `SAMPLE_TASKS`
2. Add more agents to the workflow
3. Customize the workflow logic
4. Integrate with your own services

## Dependencies

Make sure all required dependencies are installed:

```bash
pip install -r ../requirements.txt
```

## Troubleshooting

If you encounter any issues:
1. Check that all services (Redis, Qdrant, etc.) are running
2. Verify your environment variables are set correctly
3. Check the logs for detailed error messages

## Next Steps

After running the examples, you can:
1. Create your own agent implementations
2. Define custom workflows
3. Integrate with your application
4. Deploy the agents as a service
