from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
import os
from dotenv import load_dotenv
from main import create_completion_service, translate_text_service, summarize_text_service
from utils import format_response

load_dotenv()

app = FastAPI()

@app.post("/api/v1/completions")
async def create_completion(request_data: CompletionRequest):
    """Handles text completion requests."""
    try:
        response = await create_completion_service(
            prompt=request_data.prompt,
            model=request_data.model,
            max_tokens=request_data.max_tokens,
            temperature=request_data.temperature
        )
        return JSONResponse(content=format_response(response), status_code=200)
    except openai.error.APIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API Error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

@app.post("/api/v1/translations")
async def translate_text(request_data: TranslationRequest):
    """Handles text translation requests."""
    try:
        response = await translate_text_service(
            text=request_data.text,
            target_language=request_data.target_language
        )
        return JSONResponse(content=format_response(response), status_code=200)
    except openai.error.APIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API Error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

@app.post("/api/v1/summaries")
async def summarize_text(request_data: SummarizationRequest):
    """Handles text summarization requests."""
    try:
        response = await summarize_text_service(
            text=request_data.text,
            max_tokens=request_data.max_tokens
        )
        return JSONResponse(content=format_response(response), status_code=200)
    except openai.error.APIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API Error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

class CompletionRequest(BaseModel):
    prompt: str = Field(..., description="The text prompt to generate text from.")
    model: Optional[str] = Field("text-davinci-003", description="The OpenAI model to use.")
    max_tokens: Optional[int] = Field(100, description="The maximum number of tokens to generate.")
    temperature: Optional[float] = Field(0.7, description="The temperature parameter controls the creativity of the response.")

class TranslationRequest(BaseModel):
    text: str = Field(..., description="The text to translate.")
    target_language: str = Field(..., description="The target language code (e.g., 'fr' for French).")

class SummarizationRequest(BaseModel):
    text: str = Field(..., description="The text to summarize.")
    max_tokens: Optional[int] = Field(100, description="The maximum number of tokens in the summary.")