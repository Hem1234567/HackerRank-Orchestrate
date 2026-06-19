# HackerRank Orchestrate: Multi-Modal AI Claims Intelligence

Starter repository for the **HackerRank Orchestrate** 24-hour hackathon. This repository now contains a completed, production-ready solution to the visual evidence adjudication challenge.

## Project Overview

This solution implements a sophisticated multi-agent pipeline designed to verify damage claims for cars, laptops, and packages. It evaluates user transcripts, image evidence, and historical user risk profiles to arrive at highly accurate verdicts constrained strictly by Pydantic Enums.

### Key Features
1. **Multi-Agent Architecture (`pipeline.py`)**:
   - `ClaimExtractor`: Intelligently parses user transcripts to determine exactly what needs to be visually verified.
   - `VisualInspector`: Analyzes images via a Vision-Language Model against `evidence_requirements.csv` rules.
   - `VerdictJudge`: Synthesizes the extracted transcript and visual findings to deliver a final ruling.
   - `RiskAssessor`: Layers in user history to adjust final severity and risk flags.
2. **Interactive Glassmorphism Dashboard (`dashboard.html`)**: A beautiful, dark-mode, zero-dependency dashboard built to visualize the results directly from the `output.csv`. View exact images and the AI's logical reasoning side-by-side!
3. **Graceful Fault Tolerance**: The system intelligently catches API failures (e.g., 402 Insufficient Credits, 400 Invalid Images) and gracefully degrades the claim to a `not_enough_information` state, ensuring the pipeline never crashes and the output CSV formatting remains perfect for grading scripts.

## Repository Contents

- `code/`: Contains the full multi-agent AI pipeline and evaluation logic.
- `code.zip`: The packaged final submission.
- `output.csv`: The final system predictions on the test dataset.
- `dashboard.html`: The interactive UI dashboard to review results.

## Quick Start
To run the full pipeline locally:
```bash
python code/main.py
```
To view the results dashboard:
```bash
python -m http.server 8000
```
Then navigate to `http://localhost:8000/dashboard.html` in your browser.

---
Read [`problem_statement.md`](./problem_statement.md) for the original task spec, input/output schema, and allowed values.
