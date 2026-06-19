# HackerRank Orchestrate: Multi-Modal AI Claims Intelligence

Welcome to the **HackerRank Orchestrate** hackathon repository. This project implements a production-ready, highly robust **Automated Visual Evidence Adjudication** system. 

The goal of this system is to analyze damage claims across three object types (**cars**, **laptops**, and **packages**) by intelligently cross-referencing user chat transcripts, historical user risk data, and multi-modal image evidence.

---

## 🏗️ 1. Core Architecture & Pipeline

To solve this complex adjudication problem, we built a **Multi-Agent Pipeline** using Python. The system delegates distinct analytical tasks to specialized AI "Agents" to ensure high accuracy and modularity. We used the `instructor` library combined with `pydantic` to force the Large Language Model (`gpt-4o-mini`) to output strictly validated JSON that perfectly matches the hackathon's required Enums.

The pipeline (`code/pipeline.py`) flows sequentially through four distinct agents:

### A. The Claim Extractor (`code/agents/extractor.py`)
- **Inputs:** The user's chat transcript.
- **Role:** Extracts exactly *what* the user is claiming is damaged. 
- **Detail:** Instead of throwing the whole transcript at the visual model, this agent distills the transcript into a focused "Verification Target". For example, if a user rants about a car crash, the extractor pulls out specifically: *"Verify if there is a dent on the front bumper."*

### B. The Visual Inspector (`code/agents/inspector.py`)
- **Inputs:** Base64-encoded images and the `evidence_requirements.csv`.
- **Role:** The primary "eyes" of the system. It examines the images to identify the `issue_type` (e.g., `scratch`, `crack`) and the `object_part` (e.g., `windshield`, `screen`).
- **Detail:** It dynamically handles single images or multiple semicolon-separated images. It checks the images against the strict evidence requirements. If an image is blurry, shows the wrong object, or is heavily cropped, it safely flags `valid_image = false` rather than guessing.

### C. The Verdict Judge (`code/agents/judge.py`)
- **Inputs:** The extracted claim (from Agent A) and the visual findings (from Agent B).
- **Role:** Acts as the logical arbitrator. 
- **Detail:** If the user claimed a cracked screen, but the Visual Inspector only found a scratched body, the Judge marks the claim as `contradicted`. If the images perfectly align, it marks it as `supported`. If the Visual Inspector couldn't see the image clearly, it safely returns `not_enough_information`.

### D. The Risk Assessor (`code/agents/risk_assessor.py`)
- **Inputs:** The Judge's verdict and the user's historical profile (`user_history.csv`).
- **Role:** Finalizes the `severity` and appends `risk_flags`.
- **Detail:** If a user has a history of 50 rejected claims in the last 90 days, the Risk Assessor will append the `user_history_risk` flag and potentially elevate the severity of the claim for manual review, fulfilling the complex risk-context requirements of the hackathon.

---

## 🛡️ 2. Fault Tolerance & API Error Handling

In real-world data processing (and hackathons), APIs fail and datasets contain corrupted files. Our solution is built to **never crash**.

1. **API Limit Handling (HTTP 402):** If the OpenRouter API runs out of credits midway through processing the 45-row dataset, the script catches the `402 Payment Required` error. 
2. **Corrupted Images (HTTP 400):** If an image is an unsupported format, it catches the `400 Bad Request` error.
3. **Graceful Degradation:** Instead of crashing and destroying the `output.csv`, the pipeline gracefully defaults failed rows to `claim_status: not_enough_information` with a matching `Justification`. This ensures the final `output.csv` has exactly 45 rows and perfectly adheres to the evaluation script constraints.

---

## 📊 3. The Interactive Dashboard (`dashboard.html`)

To provide visual proof of the system's accuracy, we built a **zero-dependency interactive dashboard** using HTML, CSS (Glassmorphism design), and Vanilla JavaScript.

- **Real-Time Data Parsing:** The dashboard automatically reads the generated `output.csv` using JavaScript's `fetch` API.
- **Dynamic Metrics:** It instantly calculates total claims, supported claims, contradicted claims, and errors, displaying them in premium UI cards.
- **Deep-Dive Modals:** By clicking on any row in the dashboard table, an interactive modal pops up showing the **actual image** from the dataset alongside the AI's exact justification for *why* it made its decision. 

---

## 🚀 4. How to Run the Project

### Environment Setup
1. Ensure Python 3.9+ is installed.
2. Install the required dependencies:
   ```bash
   pip install pydantic instructor httpx python-dotenv pandas
   ```
3. Set your API key inside `code/utils/llm_client.py` using an environment variable (`os.getenv("OPENROUTER_API_KEY")`) or a `.env` file.

### Running the Data Pipeline
Run the main script from the root directory to ingest `dataset/claims.csv` and generate `output.csv`.
```bash
python code/main.py
```

### Viewing the Dashboard
Because the dashboard fetches a local CSV file, it must be run over a local web server to bypass CORS restrictions.
1. Start the server from the root directory:
   ```bash
   python -m http.server 8000
   ```
2. Open your browser and navigate to: `http://localhost:8000/dashboard.html`

---

## 📈 5. Operational Evaluation

An evaluation report (`code/evaluation/evaluation_report.md`) is included in the project, detailing the token costs, latency, API rate limits, and processing efficiency of the pipeline against the sample and test datasets.

---
*Created for the HackerRank Orchestrate Hackathon.*
