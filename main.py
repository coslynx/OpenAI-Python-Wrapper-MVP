from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import openai
import requests
import jwt
import os
from dotenv import load_dotenv
from cachetools import TTLCache, cached
from marshmallow import Schema, fields

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE")

openai.api_key = OPENAI_API_KEY

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

origins = [
    "http://localhost:8000",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Caching Configuration
CACHE_TTL = 300  # Cache expiration time in seconds
cache = TTLCache(maxsize=100, ttl=CACHE_TTL)

# Authentication Configuration
SECRET_KEY = os.getenv("SECRET_KEY")  # Replace with a strong, secure key
ALGORITHM = "HS256"

# Database Model
class RequestLog(Base):
    __tablename__ = "request_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    timestamp = Column(DateTime)
    request_data = Column(Text)
    response_data = Column(Text)

# Database Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication Functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.exceptions.InvalidTokenError:
        raise credentials_exception

async def get_current_user(token: str = Depends(verify_token)):
    user_id = token.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user_id

# API Endpoints
@app.post("/api/v1/completions")
async def create_completion(
    request_data: CompletionRequest,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    try:
        response = await create_completion_service(
            prompt=request_data.prompt,
            model=request_data.model,
            max_tokens=request_data.max_tokens,
            temperature=request_data.temperature
        )
        # Log the request
        log_request(db, current_user, request_data, response)
        return JSONResponse(content=response, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/api/v1/translations")
async def translate_text(
    request_data: TranslationRequest,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    try:
        response = await translate_text_service(
            text=request_data.text,
            target_language=request_data.target_language
        )
        # Log the request
        log_request(db, current_user, request_data, response)
        return JSONResponse(content=response, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/api/v1/summaries")
async def summarize_text(
    request_data: SummarizationRequest,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    try:
        response = await summarize_text_service(
            text=request_data.text,
            max_tokens=request_data.max_tokens
        )
        # Log the request
        log_request(db, current_user, request_data, response)
        return JSONResponse(content=response, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Service Functions
@cached(cache)
async def create_completion_service(
    prompt: str,
    model: str = "text-davinci-003",
    max_tokens: int = 100,
    temperature: float = 0.7
):
    try:
        response = openai.Completion.create(
            engine=model,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].text
    except openai.error.APIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API Error: {e}")

@cached(cache)
async def translate_text_service(
    text: str,
    target_language: str
):
    try:
        response = openai.Translation.create(
            model="gpt-3.5-turbo",
            from_language="auto",
            to_language=target_language,
            text=text
        )
        return response.text
    except openai.error.APIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API Error: {e}")

@cached(cache)
async def summarize_text_service(
    text: str,
    max_tokens: int = 100
):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Summarize this text: {text}",
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].text
    except openai.error.APIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API Error: {e}")

# Database Logging
def log_request(db: Session, user_id: str, request_data: dict, response_data: str):
    db_request = RequestLog(
        user_id=user_id,
        timestamp=datetime.utcnow(),
        request_data=json.dumps(request_data),
        response_data=response_data
    )
    db.add(db_request)
    db.commit()

# Data Models for Request Validation
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

# Run the Application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)