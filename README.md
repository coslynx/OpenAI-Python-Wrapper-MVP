<div class="hero-icon" align="center">
<img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-markdown-open.svg" width="100" />
</div>
<h1 align="center"> Python AI Wrapper for OpenAI Requests - MVP </h1> 
<h4 align="center">A user-friendly Python backend service that simplifies interaction with OpenAI's API.</h4>
<h4 align="center">Developed with the software and tools below.</h4>
<div class="badges" align="center">
<img src="https://img.shields.io/badge/Framework-FastAPI-blue" alt="Framework">
<img src="https://img.shields.io/badge/Language-Python-red" alt="Language">
<img src="https://img.shields.io/badge/API-OpenAI-blue" alt="API">
<img src="https://img.shields.io/badge/Database-PostgreSQL-black" alt="Database">
</div>
<div class="badges" align="center">
<img src="https://img.shields.io/github/last-commit/coslynx/OpenAI-Python-Wrapper-MVP?style=flat-square&color=5D6D7E" alt="git-last-commit" />
<img src="https://img.shields.io/github/commit-activity/m/coslynx/OpenAI-Python-Wrapper-MVP?style=flat-square&color=5D6D7E" alt="GitHub commit activity" />
<img src="https://img.shields.io/github/languages/top/coslynx/OpenAI-Python-Wrapper-MVP?style=flat-square&color=5D6D7E" alt="GitHub top language" />
</div>  

## Overview

This repository houses the code for a Python-based Minimum Viable Product (MVP) that acts as a user-friendly wrapper for OpenAI's API.  The MVP streamlines the process of interacting with OpenAI's powerful language models, enabling developers and users to access and leverage AI capabilities with ease. It does so by providing a standardized interface for handling user requests, translating those requests into appropriate OpenAI API calls, processing the responses, and returning the final output in a clear and usable manner.  

## Features

| Feature | Description |
|---|---|
| **Request Handling and Validation:** | The MVP accepts user requests in a standardized format, typically JSON, and performs basic validation to ensure correct structure and data types. This ensures that requests are well-formed and compatible with the OpenAI API. |
| **OpenAI API Integration:** | The MVP seamlessly integrates with OpenAI's API by mapping user requests to the appropriate API endpoints (e.g., `/v1/completions` for text completion, `/v1/translations` for translation) and handling API authentication. This allows users to access OpenAI's language models through a simplified interface. |
| **Response Processing and Formatting:** | The MVP receives responses from OpenAI's API and performs any necessary post-processing, such as formatting the output, filtering irrelevant information, and handling potential errors. This ensures that users receive clear and readily usable responses. |
| **Database Logging (Optional):** | The MVP can optionally log user requests and responses to a database (e.g., PostgreSQL), providing insights into usage patterns and potential performance issues. |
| **Caching (Optional):** | The MVP can implement caching mechanisms to store frequently accessed responses from OpenAI's API, reducing the need for repeated API calls and improving response time. |
| **Security:** | The MVP incorporates security measures to protect user data and sensitive information. This includes using a secure environment variable storage system, enforcing HTTPS communication, and potentially implementing rate limiting to prevent abuse. |

## Structure

```
├── api
│   └── v1
│       └── routes.py
├── main.py
├── models.py
├── utils.py
├── tests
│   └── test_main.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
├── .flake8
├── deploy.py
└── .env.example

```

## Installation

1. **Prerequisites:**
    - Python 3.9+
    - PostgreSQL (optional, if logging to database is desired)
    - Docker (optional, for containerized deployment)

2. **Clone the repository:**
   ```bash
   git clone https://github.com/coslynx/OpenAI-Python-Wrapper-MVP.git
   cd OpenAI-Python-Wrapper-MVP
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   - Create a `.env` file (if not present) based on the `.env.example` file.
   - Set the `OPENAI_API_KEY` to your actual OpenAI API key.
   - If using PostgreSQL:
      - Set `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DATABASE` to your database connection details.

## Usage

1. **Run the application:**
   ```bash
   uvicorn main:app --reload
   ```
   - This will start the FastAPI application, enabling the API endpoints.

2. **Test the API:**
   - You can use tools like `curl` or Postman to send requests to the API endpoints. 
   - For example, to generate text using the `/api/v1/completions` endpoint:
      ```bash
      curl -X POST -H "Content-Type: application/json" -d '{"prompt": "Write a short story about a cat.", "model": "text-davinci-003", "max_tokens": 100, "temperature": 0.7}' http://localhost:8000/api/v1/completions
      ```

## Hosting

1. **Containerization (Optional):**
    - If using Docker, build the image:
      ```bash
      docker build -t openai-wrapper .
      ```
    - Run the container:
      ```bash
      docker run -d -p 8000:8000 openai-wrapper
      ```

2. **Deployment:**
    - You can deploy the application using a platform like Heroku, AWS Lambda, or Google Cloud Functions.
    - Ensure you configure environment variables (e.g., `OPENAI_API_KEY`, database connection details) on your chosen platform.

## API Documentation

### Endpoints

| Endpoint | Description |
|---|---|
| `/api/v1/completions` | Generates text based on a given prompt. |
| `/api/v1/translations` | Translates text from one language to another. |
| `/api/v1/summaries` | Summarizes a given text. |

### Example API Calls

**Text Completion:**

```json
{
  "prompt": "Write a short story about a cat.",
  "model": "text-davinci-003",
  "max_tokens": 100,
  "temperature": 0.7
}
```

**Translation:**

```json
{
  "text": "Hello, how are you?",
  "target_language": "fr"
}
```

**Summarization:**

```json
{
  "text": "The quick brown fox jumps over the lazy dog.",
  "max_tokens": 20
}
```

### Authentication

- The API doesn't currently implement authentication.
- Future iterations may introduce authentication using JWT or similar mechanisms.

## Contribution

- Fork the repository
- Make changes to the code
- Create a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## CosLynx.com

This project was created as a part of the CosLynx.com community initiative.

CosLynx.com is a website dedicated to fostering the development of AI-powered applications, with a focus on:

- **Community Building:** Connecting developers, researchers, and enthusiasts to share knowledge, collaborate, and learn.
- **Resources and Tutorials:** Providing comprehensive resources, tutorials, and guides to help you build AI applications.
- **Open Source Projects:** Showcasing and supporting open-source projects that advance the field of AI.

Visit [CosLynx.com](https://www.coslynx.com) to learn more about the community and its initiatives.