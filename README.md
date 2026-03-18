# MemoryOS - Cognitive Architecture Project

MemoryOS is an advanced, multi-modal AI infrastructure project containing a Next.js frontend, a Python FastAPI backend, a C++ high-performance memory infrastructure service, and a Streamlit-based RAG chat application. It leverages local LLMs via Ollama.

This guide explains how to build, set up, and run all components of the project.

---

## Prerequisites

Before starting, ensure you have the following installed on your system:
- **Node.js** (v18+) & **npm/yarn**
- **Python** (3.10+)
- **CMake** (3.10+) & a C++17 compatible compiler (GCC/Clang)
- **SQLite3** development libraries
- **Ollama** (for local LLMs)

---

## 1. Setup Local LLMs (Ollama)

The RAG Chat App and other subsystems use local models served by Ollama.
1. Start the Ollama server (if not already running as a background service):
   ```bash
   ollama serve
   ```
2. Open a new terminal and pull the required models:
   ```bash
   ollama pull mistral
   ollama pull llama3.1:8b
   ```

---

## 2. Python Backend (FastAPI)

The main MemoryOS backend provides internal and public APIs.
**Location**: Roots directory (`/memory/memory/`)

1. Set up a Python Virtual Environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies (make sure you have `fastapi`, `uvicorn`, `pydantic`, etc.):
   ```bash
   pip install -r requirememnts.txt # Add any other required backend deps
   ```
3. Run the backend server:
   ```bash
   python server.py
   # Or using uvicorn directly: uvicorn server:app --reload
   ```
*The backend will be available at `http://localhost:8000`.*

---

## 3. High-Performance C++ Infrastructure

The C++ module handles lower-level vector, graph, and event queue clustering operations.
**Location**: `backend/infra_cpp/`

1. Navigate to the cpp infrastructure directory:
   ```bash
   cd backend/infra_cpp
   ```
2. Build the project using CMake:
   ```bash
   mkdir build
   cd build
   cmake ..
   make
   ```
3. Run the compiled service:
   ```bash
   ./memory_service
   ```

---

## 4. Next.js Frontend

The main web application/dashboard.
**Location**: Root directory (`/memory/memory/`)

1. Open a new terminal in the root directory.
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
*The frontend will be available at `http://localhost:3000`.*

---

## 5. RAG Chat Application (Streamlit)

A specialized conversational frontend utilizing Retrieval-Augmented Generation (RAG).
**Location**: `rag_chat_app/`

1. Navigate to the RAG chat application directory (ensure your Python virtual environment from step 2 is activated):
   ```bash
   cd rag_chat_app
   ```
2. Install Streamlit and required dependencies:
   ```bash
   pip install streamlit sqlite3 requests # Assuming basic requests to backend and Ollama
   ```
3. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```
*The RAG app will open in your browser, typically at `http://localhost:8501`.*

---

## Quick Start Summary

To run the full stack simultaneously, you need 5 separate terminal tabs:
1. `ollama serve`
2. `cd backend/python server.py`
3. `cd backend/infra_cpp/build && ./memory_service`
4. `npm run dev`
5. `cd rag_chat_app && streamlit run app.py`

Enjoy exploring MemoryOS!
