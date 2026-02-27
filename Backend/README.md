# 🏦 Backend — Loan Processing Multi-Agent API

The backend service for the **BFSI Multi-Agent Loan Automation** system. Built with **FastAPI** and powered by **Azure AI Foundry** with **GPT-4o**, it orchestrates **9 specialized AI agents** to automate the entire loan application lifecycle.

> Part of the [BFSI Multi-Agent Loan Automation](../README.md) project.

---

## 📑 Table of Contents

- [Architecture](#architecture)
- [Agent Pipeline](#agent-pipeline)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Environment Variables](#environment-variables)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Docker](#docker)
- [Deployment](#deployment)

---

## Architecture

The backend is a **FastAPI** application that exposes REST endpoints for loan processing. A **Simple Orchestrator** manages the sequential (and parallel) execution of 9 AI agents, each created dynamically via the **Azure AI Projects SDK**.

```
                    POST /api/loan/process
                            │
                    ┌───────▼────────┐
                    │   FastAPI App   │
                    │    (main.py)    │
                    └───────┬────────┘
                            │
                ┌───────────▼───────────┐
                │  Simple Orchestrator   │
                │ (simple_orchestrator.py)│
                └───────────┬───────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │           Agent Pipeline              │
        │                                       │
        │  1. Customer Service                  │
        │  2. Document Verification (File Search)│
        │  3. Credit Qualification              │
        │  4a. Credit Assessment  ⚡ (parallel)  │
        │  4b. Asset Valuation    ⚡ (parallel)  │
        │  5. Underwriting → Decision           │
        │  6. Offer Generation → EMI / Fees     │
        │  7. Customer Communication            │
        │  8. Audit → Compliance Report         │
        └───────────────────────────────────────┘
                            │
              Azure AI Foundry (GPT-4o Agents)
```

---

## Agent Pipeline

| # | Agent | File | Responsibility |
|---|-------|------|---------------|
| 1 | **Customer Service** | `Customerserviceagent.py` | Collects personal info, loan requirements, explains required documents, and prepares handoff summary |
| 2 | **Document Verification** | `Documentverificationagent.py` | Verifies KYC documents (Aadhaar, PAN, Passport, Form 16, salary slips, bank statements, CIBIL report, property docs) using **File Search** |
| 3 | **Credit Qualification** | `Creditqualificationagent.py` | Eligibility gatekeeper — checks age (21–65), employment stability (2+ years), income thresholds, CIBIL score (≥650), FOIR (max 60%) |
| 4a | **Credit Assessment** ⚡ | `Creditassessmentagent.py` | Deep credit analysis: CIBIL score (300–900), payment history, debt analysis, credit utilization, risk scoring |
| 4b | **Asset Valuation** ⚡ | `Assetvaluationagnet.py` | Property valuation, market value assessment, LTV ratio calculation (max 80% residential), collateral risk |
| 5 | **Underwriting** | `Underwritingagent.py` | Final decision-maker (APPROVE / DECLINE / REFERRED) using weighted criteria; sets interest rate (8.5%–10.5%) |
| 6 | **Offer Generation** | `Offergenerationagent.py` | Calculates EMI, amortization schedule, total cost/interest, and fee structure |
| 7 | **Customer Communication** | `Customercommunicationagent.py` | Sends email notifications, SMS alerts, push notifications; explains terms and schedules follow-ups |
| 8 | **Audit** | `Auditagent.py` | Audits entire workflow, verifies RBI compliance, KYC/AML, internal policy, and generates audit report |

> ⚡ Credit Assessment and Asset Valuation run **in parallel** for faster processing.

---

## Project Structure

```
Backend/
├── Documents/                          # Uploaded customer documents (shared)
├── results/                            # Processed loan result JSONs
└── loanbackend/
    ├── main.py                         # FastAPI app & API endpoints
    ├── simple_orchestrator.py          # Agent pipeline orchestrator
    ├── Customerserviceagent.py         # Agent 1 – Customer intake
    ├── Documentverificationagent.py    # Agent 2 – KYC verification
    ├── Creditqualificationagent.py     # Agent 3 – Eligibility check
    ├── Creditassessmentagent.py        # Agent 4a – Credit analysis
    ├── Assetvaluationagnet.py          # Agent 4b – Property valuation
    ├── Underwritingagent.py            # Agent 5 – Final decision
    ├── Offergenerationagent.py         # Agent 6 – Loan offer creation
    ├── Customercommunicationagent.py   # Agent 7 – Notifications
    ├── Auditagent.py                   # Agent 8 – Compliance audit
    ├── requirements.txt                # Python dependencies
    ├── Dockerfile                      # Container configuration
    ├── .env                            # Environment variables (not committed)
    ├── .gitignore                      # Git ignore rules
    └── Documents/                      # Agent-accessible documents
```

---

## Prerequisites

- **Python 3.11+**
- **Azure Subscription** with:
  - Azure AI Foundry project with a **GPT-4o** deployment
  - Azure OpenAI Service
- **Azure authentication** via one of:
  - Azure CLI login (`az login`)
  - Environment variables (`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`)
  - Managed Identity
  - VS Code Azure extension

---

## Environment Variables

Create a `.env` file inside `loanbackend/`:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PROJECT_CONNECTION_STRING` | ✅ Yes | — | Azure AI Foundry project connection string |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | No | `gpt-4o` | Model deployment name |
| `PORT` | No | `8000` | Server port |
| `ROOT_PATH` | No | `""` | FastAPI root path prefix |
| `ENVIRONMENT` | No | `development` | Runtime environment |
| `ENV` | No | `dev` | Controls uvicorn hot-reload |

Example `.env`:

```env
PROJECT_CONNECTION_STRING=<your-azure-ai-foundry-connection-string>
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
PORT=8000
```

---

## Getting Started

```bash
# Navigate to the backend
cd Backend/loanbackend

# (Optional) Create a virtual environment
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Set required environment variable (or use .env file)
# Windows PowerShell:
$env:PROJECT_CONNECTION_STRING="<your-azure-ai-foundry-connection-string>"
# Linux/macOS:
# export PROJECT_CONNECTION_STRING="<your-azure-ai-foundry-connection-string>"

# Start the server
python main.py
```

The API will be available at **http://localhost:8000**.

- Swagger UI: **http://localhost:8000/docs**
- ReDoc: **http://localhost:8000/redoc**

---

## API Reference

### Root & Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Welcome message with available agents and endpoints |
| `GET` | `/health` | System health, orchestrator status, Azure configuration |

### Loan Processing

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/loan/process` | Process a loan application through all 9 agents |
| `GET` | `/api/loan/status/{application_id}` | Get loan application status |

**`POST /api/loan/process`** — Form parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `customer_name` | string | `"Kala Divan"` | Applicant's full name |
| `loan_amount` | float | `4000000` | Loan amount in INR |
| `loan_purpose` | string | `"Home Loan"` | Purpose of the loan |
| `loan_tenure` | int | `20` | Tenure in years |
| `contact_number` | string | `"+91-9876543210"` | Contact number |
| `email` | string | `"kala.divan@example.com"` | Email address |

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/documents/upload` | Upload documents (PDF, DOCX, TXT, JSON, XLSX, CSV, images) |
| `GET` | `/api/documents` | List all uploaded documents with metadata |
| `GET` | `/api/documents/{filename}` | Download a specific document |
| `DELETE` | `/api/documents/{filename}` | Delete a document |

### Results

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/results` | List all processing results (sorted newest first) |
| `GET` | `/api/results/{result_id}` | Get detailed result JSON |
| `GET` | `/api/results/{result_id}/download` | Download result as JSON file |
| `DELETE` | `/api/results/{result_id}` | Delete a result |

---

## Docker

### Build

```bash
cd Backend/loanbackend
docker build -t loan-backend .
```

### Run

```bash
docker run -p 8000:8000 \
  -e PROJECT_CONNECTION_STRING="<your-connection-string>" \
  loan-backend
```

The container uses:
- **Python 3.11-slim** base image
- **Uvicorn** ASGI server on port 8000
- Built-in health check at `/health`

---

## Deployment

### Azure Container Apps

```bash
# Build in Azure Container Registry (no local Docker needed)
az acr build --registry <your-acr-name> --image loan-backend:latest --file Dockerfile .
```

Recommended configuration:
- **CPU:** 0.5 vCPU
- **Memory:** 1.0 Gi
- **Replicas:** 1–3 (auto-scaling)
- **Ingress:** External HTTPS on port 8000

---

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11 | Runtime |
| FastAPI | ≥ 0.109.0 | REST API framework |
| Uvicorn | ≥ 0.27.0 | ASGI server |
| Azure AI Projects SDK | 1.0.0b10 | Azure AI Foundry agent creation |
| Azure Identity | ≥ 1.15.0 | `DefaultAzureCredential` |
| OpenAI | ≥ 1.0.0 | Model interaction |
| aiohttp | ≥ 3.9.0 | Async HTTP |
| python-dotenv | ≥ 1.0.0 | Environment variable management |

---

## Related

- [Main README](../README.md) — Full project overview, architecture, and frontend docs
- [Frontend README](../Frontend/README-Flask.md) — Flask web portal documentation
