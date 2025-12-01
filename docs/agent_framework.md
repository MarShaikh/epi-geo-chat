# Microsoft Agent Framework

### Why Microsoft Agent Framework?
- **Next-gen orchestration** - Evolution beyond Semantic Kernel, built for multi-agent systems
- **Graph-based workflows** - Native support for complex agent pipelines with streaming and checkpointing
- **Built-in observability** - OpenTelemetry integration for distributed tracing
- **Azure integration** - Native support for Azure OpenAI and Azure services
- **DevUI included** - Interactive developer interface for testing and debugging
- **Python-first** - Modern Python implementation with async support
- **Production-ready** - Used in Microsoft's latest AI agent solutions


### How to create agents

Read more on building a Azure OpenAI Responses Agent [here](https://learn.microsoft.com/en-us/agent-framework/user-guide/agents/agent-types/azure-openai-responses-agent?pivots=programming-language-python).

```python
# Example Agent to write haikus

import os
import asyncio
from dotenv import load_dotenv
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import AzureCliCredential

load_dotenv() # save the env vars in a `.env` file

async def main(string: str = "Write a haiku about the Microsoft Agent Framework."):
    agent = AzureOpenAIResponsesClient(
        # endpoint = os.environ["AZURE_OPENAI_ENDPOINT"],
        # deployment_name = os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
        # api_version = os.environ["AZURE_OPENAI_API_VERSION"],
        # api_key = os.environ.get("AZURE_OPENAI_API_KEY"),
        # credential=AzureCliCredential(); if not using the API key
    ).create_agent( # use this to create an agent
        name = "HaikuBot",
        instruction = "You are a poet that composes beautiful haikus.",
    )

    print(await agent.run(string))
    

asyncio.run(main(string = "Write a haiku about the ISS"))
```
> **Note**: The responses API is not available in every region. Check [here](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/responses?view=foundry-classic&tabs=python-key#region-availability) to make sure that the responses API is available in the region where you have set up your Azure OpenAI account.  