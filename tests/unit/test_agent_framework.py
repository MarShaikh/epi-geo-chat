from unittest.mock import patch, MagicMock
from src.agents.agent_config import create_agent_client
from tests.fixtures.env import mock_env_vars


@patch("src.agents.agent_config.AzureOpenAIResponsesClient")
def test_create_agent_client_with_api_key(mock_client_class, mock_env_vars):
    """Test client creation with API key authentication"""
    env_with_key = {**mock_env_vars, "AZURE_OPENAI_API_KEY": "test-key"}

    with patch.dict("os.environ", env_with_key, clear=True):
        client = create_agent_client()

        mock_client_class.assert_called_once_with(
            endpoint=env_with_key["AZURE_OPENAI_ENDPOINT"],
            deployment_name=env_with_key["AZURE_OPENAI_DEPLOYMENT_NAME"],
            api_version=env_with_key["AZURE_OPENAI_API_VERSION"],
            api_key=env_with_key["AZURE_OPENAI_API_KEY"],
        )


@patch("src.agents.agent_config.AzureCliCredential")
@patch("src.agents.agent_config.AzureOpenAIResponsesClient")
def test_create_agent_client_with_azure_cli(
    mock_client_class, mock_credential_class, mock_env_vars
):
    """Test client creation with Azure CLI credential"""
    mock_credential = MagicMock()
    mock_credential_class.return_value = mock_credential

    with patch.dict("os.environ", mock_env_vars, clear=True):
        client = create_agent_client()

        mock_credential_class.assert_called_once()
        mock_client_class.assert_called_once_with(
            endpoint=mock_env_vars["AZURE_OPENAI_ENDPOINT"],
            deployment_name=mock_env_vars["AZURE_OPENAI_DEPLOYMENT_NAME"],
            api_version=mock_env_vars["AZURE_OPENAI_API_VERSION"],
            credential=mock_credential,
        )


@patch("src.agents.agent_config.AzureOpenAIResponsesClient")
def test_agent_creation(mock_client_class, mock_env_vars):
    """Test creating an agent with the configured client"""
    mock_client = MagicMock()
    mock_agent = MagicMock()
    mock_agent.name = "TestAgent"
    mock_client.create_agent.return_value = mock_agent
    mock_client_class.return_value = mock_client

    env_with_key = {**mock_env_vars, "AZURE_OPENAI_API_KEY": "test-key"}

    with patch.dict("os.environ", env_with_key, clear=True):
        client = create_agent_client()
        agent = client.create_agent(
            name="TestAgent", instructions="You are a helpful assistant..."
        )

        mock_client.create_agent.assert_called_once_with(
            name="TestAgent", instructions="You are a helpful assistant..."
        )
        assert agent.name == "TestAgent"
