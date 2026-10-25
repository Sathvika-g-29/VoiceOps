---

## VoiceOps Capstone Implementation

This project extends the supplied ZentroMart dataset into a voice-enabled customer-support agent.

### Implemented workflow

1. **Speech-to-text:** Transcribes customer recordings using Gnani STT.
2. **Knowledge retrieval:** Uses Sentence Transformers embeddings to retrieve relevant company-document chunks.
3. **Response generation:** Uses the Gemini API to generate answers grounded in retrieved context.
4. **Order support:** Uses the supplied mock tools for identity-verified order lookup and support-ticket creation.
5. **Text-to-speech:** Uses Gnani TTS to generate spoken replies.
6. **Evaluation:** Compares LLM-only and retrieval-augmented responses against the supplied practice questions.

### Installation

Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
python -m pip install -r requirements.txt
```

If PowerShell blocks virtual-environment activation, use the environment's Python executable directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Create a `.env` file in the project root with your API keys:

```text
GEMINI_API_KEY=your_gemini_api_key_here
GNANI_API_KEY=your_gnani_api_key_here
```

Do not commit `.env` or expose your API keys.

### Run the voice agent

Place customer audio files in `audio_input/`, then run:

```powershell
.\.venv\Scripts\python.exe .\run.py .\audio_input
```

Generated transcripts, replies, reply audio, and retrieved chunks are saved in `outputs/`.

### Run evaluation

```powershell
.\.venv\Scripts\python.exe .\evaluate.py
```

Results are written to `evaluation_results.csv`. API rate limits can prevent all questions from completing in one run, so incomplete evaluations should not be treated as final accuracy measurements.

### Security note

The supplied customer and order data is synthetic. The mock tools demonstrate an identity-verification workflow for this capstone and are not a production authentication system.