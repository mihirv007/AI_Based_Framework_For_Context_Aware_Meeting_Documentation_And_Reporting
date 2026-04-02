# AI Based Framework for Context-Aware Meeting Documentation and Reporting

This project implements an **AI-powered pipeline** that converts meeting audio into structured documentation and reports.  
The system combines **speech recognition and large language models** to automatically generate meeting minutes including key discussions, decisions, and action items.

The pipeline processes audio recordings, transcribes them into text, analyzes the transcript using AI agents, and produces structured meeting summaries for documentation purposes.

---

# System Architecture Overview

The framework consists of multiple components that work together to transform raw meeting audio into organized reports.

---

# 1. Dependencies

The system requires several Python libraries for audio processing, AI orchestration, and environment configuration.

Key dependencies include:

- **Python 3.10+**
- Whisper for speech-to-text transcription
- CrewAI for multi-agent orchestration
- Gemini LLM for intelligent summarization
- dotenv for environment variable management

These dependencies enable the pipeline to handle transcription, reasoning, and report generation efficiently.

---

# 2. Library Imports

The framework imports several libraries required for system functionality.

Main libraries used in the project include:

- `os` – environment and file management  
- `warnings` – suppress unnecessary warnings  
- `datetime` – timestamp generation for outputs  
- `whisper` – speech recognition model  
- `crewai` – AI agent framework  
- `dotenv` – loading environment variables  

These libraries collectively support transcription, AI processing, and pipeline execution.

---

# 3. API Configuration

The system uses an **LLM API key** to enable AI-based summarization.

The API key is stored securely inside a `.env` file and loaded using the `dotenv` library.

This ensures:
- Secure credential management
- Easy configuration across environments
- Separation of sensitive data from source code

Example environment variable:

