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
    # Support multiple common env var names for the deployment
    deployment_name = (
        os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")
        or os.environ.get("AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME")
        or os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT")
    )
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION")

    if not endpoint:
        raise ValueError(
            "AZURE_OPENAI_ENDPOINT is not set. Please set it in your environment/.env."
        )

    if not deployment_name:
        raise ValueError(
            "Azure OpenAI deployment name is not set. Set one of: "
            "AZURE_OPENAI_DEPLOYMENT_NAME, AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME, or AZURE_OPENAI_CHAT_DEPLOYMENT."
        )

    # use API key is provided otherwise use Azure CLI Credential
    if api_key:
        return AzureOpenAIResponsesClient(
            endpoint=endpoint,
            deployment_name=deployment_name,
            api_version=api_version,
            api_key=api_key,
        )

    else:
        return AzureOpenAIResponsesClient(
            endpoint=endpoint,
            deployment_name=deployment_name,
            api_version=api_version,
            credential=AzureCliCredential(),
        )
