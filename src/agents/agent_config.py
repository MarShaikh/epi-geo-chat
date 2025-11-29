import os 
from dotenv import load_dotenv

from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import AzureCliCredential

load_dotenv()

def create_agent_client() -> AzureOpenAIResponsesClient:
    """
    Initialize Agent Framework with Azure OpenAI client

    Returns:
       AzureOpenAIResponsesClient: Configured client for agent operations
    """

    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    deployment_name = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION")

    # use API key is provided otherwise use Azure CLI Credential
    if api_key:
        return AzureOpenAIResponsesClient(
            endpoint = endpoint,
            deployment_name = deployment_name,
            api_version = api_version,
            api_key = api_key,
        )

    else:
        return AzureOpenAIResponsesClient(
            endpoint = endpoint,
            deployment_name = deployment_name,
            api_version = api_version,
            credential = AzureCliCredential(),
        )