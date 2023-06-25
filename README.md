# HelpGPT

A question-answer tool for your documents, powered by Pinecore, LangChain, and OpenAI.

## Start Server

### Requirements: Python 3.8 or later

Copy `.env_example` to a new `.env` file, and fill out the required settings:

```
DOCUMENT_DIRECTORY=source_documents
DOCUMENT_DIRECTORY_INDEXED=source_documents_indexed
OPENAI_API_KEY=...
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=...
PINECONE_INDEX=...
```

Start a terminal and run the following commands to start the backend server:

```bash
% cd server
% python3 -m venv myenv
% source myenv/bin/activate
% pip install -r requirements.txt
% python helpgpt.py
```

On macOS, you may need to install some required drivers as well:

```bash
% brew install poppler
% brew install tesseract
% brew install pkg-config
```

## Start Web Frontend

* Requirements: Node.js v18.12.1 or later

Start another terminal and run the following commands to start the frontend web server:

```bash
% cd client
% npm install
% npm run dev
```

## Use the Web Application

Open http://localhost:3000 and upload any of your documents, then ask questions about the content in these documents.
