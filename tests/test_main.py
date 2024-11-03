import pytest
from main import create_completion_service, translate_text_service, summarize_text_service
from fastapi import HTTPException
import openai
import requests

# Mock Data (To avoid hitting actual APIs during testing)
mock_prompt = "Write a short story about a cat."
mock_model = "text-davinci-003"
mock_max_tokens = 100
mock_temperature = 0.7
mock_text = "Hello, how are you?"
mock_target_language = "fr"

# Mock OpenAI API Response (For Text Completion)
mock_completion_response = {
    "choices": [
        {
            "text": "The ginger cat, named Marmalade, was a creature of habit. Every morning, at precisely 7:00 AM, he would ..."
        }
    ],
    "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 70,
        "total_tokens": 80
    }
}

# Mock OpenAI API Response (For Translation)
mock_translation_response = "Bonjour, comment allez-vous?"

# Mock OpenAI API Response (For Summarization)
mock_summarization_response = "A ginger cat named Marmalade had a routine."

@pytest.fixture
def mock_openai(monkeypatch):
    """Mocking the OpenAI API to control responses during testing."""
    def mock_completion_create(*args, **kwargs):
        return mock_completion_response

    def mock_translation_create(*args, **kwargs):
        return {"text": mock_translation_response}

    def mock_completion_create_summary(*args, **kwargs):
        return {"choices": [{"text": mock_summarization_response}]}

    monkeypatch.setattr(openai.Completion, "create", mock_completion_create)
    monkeypatch.setattr(openai.Translation, "create", mock_translation_create)
    monkeypatch.setattr(openai.Completion, "create", mock_completion_create_summary)

async def test_create_completion_service(mock_openai):
    """Test the text completion service function."""
    response = await create_completion_service(
        prompt=mock_prompt, model=mock_model, max_tokens=mock_max_tokens, temperature=mock_temperature
    )
    assert response == mock_completion_response["choices"][0]["text"]

async def test_translate_text_service(mock_openai):
    """Test the text translation service function."""
    response = await translate_text_service(text=mock_text, target_language=mock_target_language)
    assert response == mock_translation_response

async def test_summarize_text_service(mock_openai):
    """Test the text summarization service function."""
    response = await summarize_text_service(text=mock_text, max_tokens=mock_max_tokens)
    assert response == mock_summarization_response

async def test_create_completion_service_api_error(monkeypatch):
    """Test handling OpenAI API errors."""
    def mock_api_error(*args, **kwargs):
        raise openai.error.APIError("Mock API Error") 

    monkeypatch.setattr(openai.Completion, "create", mock_api_error)

    with pytest.raises(HTTPException) as e:
        await create_completion_service(mock_prompt, mock_model, mock_max_tokens, mock_temperature)

    assert e.value.status_code == 500
    assert "OpenAI API Error: Mock API Error" in str(e.value.detail)

async def test_translate_text_service_api_error(monkeypatch):
    """Test handling OpenAI API errors for translation."""
    def mock_api_error(*args, **kwargs):
        raise openai.error.APIError("Mock API Error")

    monkeypatch.setattr(openai.Translation, "create", mock_api_error)

    with pytest.raises(HTTPException) as e:
        await translate_text_service(text=mock_text, target_language=mock_target_language)

    assert e.value.status_code == 500
    assert "OpenAI API Error: Mock API Error" in str(e.value.detail)

async def test_summarize_text_service_api_error(monkeypatch):
    """Test handling OpenAI API errors for summarization."""
    def mock_api_error(*args, **kwargs):
        raise openai.error.APIError("Mock API Error")

    monkeypatch.setattr(openai.Completion, "create", mock_api_error)

    with pytest.raises(HTTPException) as e:
        await summarize_text_service(text=mock_text, max_tokens=mock_max_tokens)

    assert e.value.status_code == 500
    assert "OpenAI API Error: Mock API Error" in str(e.value.detail)