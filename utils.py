import requests
from cachetools import TTLCache, cached
from marshmallow import Schema, fields

CACHE_TTL = 300  # Cache expiration time in seconds
cache = TTLCache(maxsize=100, ttl=CACHE_TTL)

def format_response(response_data: dict) -> dict:
    """Formats the OpenAI API response into a user-friendly structure.

    Args:
        response_data (dict): The raw OpenAI API response.

    Returns:
        dict: A formatted response dictionary.
    """
    formatted_response = {
        "text": response_data.get("choices", [{}])[0].get("text", ""),
        "usage": response_data.get("usage", {}),
    }
    return formatted_response

class CompletionRequestSchema(Schema):
    prompt = fields.String(required=True)
    model = fields.String(required=False, default="text-davinci-003")
    max_tokens = fields.Integer(required=False, default=100)
    temperature = fields.Float(required=False, default=0.7)

def validate_request(request_data: dict) -> dict:
    """Validates the user request data against predefined schema.

    Args:
        request_data (dict): The user's request data.

    Returns:
        dict: The validated request data.
    """
    schema = CompletionRequestSchema()
    errors = schema.validate(request_data)
    if errors:
        raise ValueError(f"Invalid request data: {errors}")
    return schema.load(request_data)

def handle_api_error(error: Exception) -> dict:
    """Handles errors from the OpenAI API.

    Args:
        error (Exception): The OpenAI API error.

    Returns:
        dict: An error response dictionary.
    """
    error_message = str(error)
    return {"error": error_message}

def cache_response(response_data: dict, key: str) -> None:
    """Caches the API response for future retrieval.

    Args:
        response_data (dict): The API response data.
        key (str): The unique key for caching.
    """
    cache[key] = response_data

def get_cached_response(key: str) -> Optional[dict]:
    """Retrieves a cached API response.

    Args:
        key (str): The unique key for the cached response.

    Returns:
        Optional[dict]: The cached response data, or None if not found.
    """
    return cache.get(key)