# Hackathon Orchestrate: Multi-Modal Evidence Review

## Architecture Overview
This solution utilizes a modular, multi-agent pipeline leveraging `gpt-4o-mini` (via OpenRouter) and the `instructor` library to ensure robust, schema-constrained outputs.

The pipeline (`pipeline.py`) consists of 4 specialized agents:
1. **ClaimExtractor**: Decomposes the user transcript into verification questions.
2. **VisualInspector**: Analyzes provided image(s) against `evidence_requirements.csv` rules to extract condition, object part, and flag visual issues.
3. **VerdictJudge**: Synthesizes visual evidence to arrive at a final determination (`supported`, `contradicted`, `not_enough_information`).
4. **RiskAssessor**: Ingests historical data (`user_history.csv`) and assigns an overall severity flag.

## How to Run

### Setup Environment
1. Ensure Python 3.9+ is installed.
2. Install dependencies:
   ```bash
   pip install pydantic instructor httpx python-dotenv pandas
   ```
3. Set your OpenRouter API key in a `.env` file or environment variable:
   ```bash
   OPENROUTER_API_KEY=sk-or-v1-...
   ```

### Running the Pipeline
Run the main script from the root of the project to process the dataset and generate `output.csv`.
```bash
python code/main.py
```

### Evaluation
An evaluation script is provided to run against the `sample_claims.csv` for fast iteration and debugging.
```bash
python code/evaluation/main.py
```

## Features
- **Pydantic Enum Validation:** Guarantees all LLM outputs strictly map to the required hackathon Enums (no hallucinations).
- **Graceful Error Handling:** If the LLM throws a 400 (Invalid Image Format) or 402 (Insufficient Credits), the system catches the error and generates a valid `not_enough_information` row to ensure the grading script does not crash on a malformed `output.csv`.
- **Intelligent Pathing:** Dynamically handles semicolon-separated image paths and absolute/relative path mixing seamlessly.
