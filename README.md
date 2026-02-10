# 🏦 BFSI Multi-Agent Loan Automation

An end-to-end loan processing automation system for the Banking, Financial Services, and Insurance (BFSI) sector. Built with a **multi-agent AI architecture** powered by **Azure AI Foundry** and **GPT-4o**, it automates the entire loan application lifecycle — from customer intake through document verification, credit assessment, underwriting, offer generation, customer communication, and final audit.

> Tailored for the **Indian banking context** with support for INR currency, PAN/Aadhaar identification, CIBIL credit scoring, and FOIR (Fixed Obligation to Income Ratio) calculations. Simulates a fictional bank called **"Global Trust Bank"**.

---

## 📑 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Agent Pipeline](#agent-pipeline)
- [Tech Stack](#tech-stack)
- [Azure Services](#azure-services)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Environment Variables](#environment-variables)
- [Getting Started](#getting-started)
  - [Backend](#backend)
  - [Frontend](#frontend)
  - [Docker](#docker)
- [API Reference](#api-reference)
  - [Backend API](#backend-api)
  - [Frontend Routes](#frontend-routes)
- [Frontend Features](#frontend-features)
- [Workflow & Data Flow](#workflow--data-flow)
- [Deployment](#deployment)
- [License](#license)

---

## Architecture Overview

The system follows a **two-tier architecture**:

| Layer | Framework | Purpose |
|-------|-----------|---------|
| **Backend** | FastAPI | Multi-agent orchestrator and AI agent pipeline |
| **Frontend** | Flask | Bank-officer portal for managing and reviewing loan applications |

```
┌──────────────────────────────────────────────────────────────────────┐
│                        Frontend (Flask)                               │
│   Applications Dashboard  ·  Workflow Visualizer  ·  Analysis View   │
└──────────────────────┬───────────────────────────────────────────────┘
                       │  REST API
┌──────────────────────▼───────────────────────────────────────────────┐
│                       Backend (FastAPI)                               │
│                  Simple Orchestrator Pipeline                         │
│                                                                      │
│  Customer    Document     Credit       ┌─ Credit Assessment ─┐       │
│  Service  →  Verification → Qualification →                    →     │
│                                        └─ Asset Valuation ───┘       │
│     → Underwriting → Offer Generation → Communication → Audit        │
└──────────────────────────────────────────────────────────────────────┘
                       │
         Azure AI Foundry (GPT-4o Agents)
```

---

## Agent Pipeline

The orchestrator runs **9 specialized agents** sequentially, with two executing in **parallel**:

| # | Agent | Responsibility |
|---|-------|---------------|
| 1 | **Customer Service** | Greets the customer, collects personal information, gathers loan requirements (amount, purpose, tenure), explains required documents, and prepares a handoff summary. |
| 2 | **Document Verification** | Verifies KYC documents (Aadhaar, PAN, Passport, Form 16, salary slips, bank statements, CIBIL report, property docs). Checks authenticity, validity, name consistency, and expiration using **File Search** to read uploaded PDFs. |
| 3 | **Credit Qualification** | Gatekeeper for eligibility — checks age (21–65), employment stability (2+ years), income thresholds, CIBIL score (≥650), and calculates FOIR (max 60%). |
| 4a | **Credit Assessment** ⚡ | Deep credit analysis: CIBIL score analysis (300–900), payment history, debt analysis, credit utilization, risk scoring (probability of default), and income stability assessment. |
| 4b | **Asset Valuation** ⚡ | Property document verification, market value assessment (comparison/income/cost approaches), LTV ratio calculation (max 80% for residential), collateral risk assessment, and marketability evaluation. |
| 5 | **Underwriting** | Final decision-maker. Synthesizes all assessments using weighted criteria (Doc Verification 15%, Credit Qualification 20%, Credit Score 25%, Risk 20%, LTV 20%). Makes **APPROVE / DECLINE / REFERRED** decision and sets interest rate (8.5%–10.5%). |
| 6 | **Offer Generation** | Creates the formal loan offer — calculates EMI, generates amortization schedule, computes total cost/interest, and produces a fee structure (processing, documentation, legal, valuation, stamp duty, MODT). |
| 7 | **Customer Communication** | Sends email notifications, SMS alerts, and push notifications. Explains terms, handles queries, records customer responses, and schedules follow-ups. |
| 8 | **Audit** | Audits the entire workflow, verifies compliance with RBI guidelines, KYC/AML, internal policy, and data privacy. Generates a comprehensive audit report with an immutable audit trail. |

> ⚡ Credit Assessment and Asset Valuation run **in parallel** for faster processing.

---

## Tech Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11 | Runtime |
| FastAPI | ≥ 0.109.0 | REST API framework |
| Uvicorn | ≥ 0.27.0 | ASGI server |
| Azure AI Projects SDK | latest | Azure AI Foundry agent creation |
| Azure Identity | ≥ 1.15.0 | `DefaultAzureCredential` |
| OpenAI | ≥ 1.0.0 | Model interaction |
| aiohttp | ≥ 3.9.0 | Async HTTP |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| Flask | 2.3.3 | Web framework |
| Gunicorn | 21.2.0 | Production WSGI server |
| Jinja2 | 3.1.2 | HTML templating |
| HTML5 / CSS3 / JavaScript | — | UI (vanilla, no frameworks) |
| Font Awesome | 6.x | Icons |

---

## Azure Services

| Service | Purpose |
|---------|---------|
| **Azure AI Foundry** | Hosts AI agents, runs GPT-4o model, provides agent runtime with tool calling |
| **Azure OpenAI Service** | GPT-4o model deployment for all agents |
| **Azure Cosmos DB** | Stores agent processing logs/records (REST API) |
| **Azure Container Apps** | Serverless container hosting (0.5 vCPU, 1 Gi RAM, 1–3 replicas) |
| **Azure Container Registry** | Docker image storage |
| **Azure Identity** | `DefaultAzureCredential` authentication across services |

---

## Project Structure

```
bfsi-multi-agent-loan-automation/
├── Backend/
│   ├── Documents/                        # Uploaded customer documents
│   ├── results/                          # Processed loan results
│   └── loanbackend/
│       ├── main.py                       # FastAPI app & API endpoints
│       ├── simple_orchestrator.py        # Agent pipeline orchestrator
│       ├── Customerserviceagent.py        # Agent 1 – Customer intake
│       ├── Documentverificationagent.py   # Agent 2 – KYC verification
│       ├── Creditqualificationagent.py    # Agent 3 – Eligibility check
│       ├── Creditassessmentagent.py       # Agent 4a – Credit analysis
│       ├── Assetvaluationagnet.py         # Agent 4b – Property valuation
│       ├── Underwritingagent.py           # Agent 5 – Final decision
│       ├── Offergenerationagent.py        # Agent 6 – Loan offer creation
│       ├── Customercommunicationagent.py  # Agent 7 – Notifications
│       ├── Auditagent.py                  # Agent 8 – Compliance audit
│       ├── requirements.txt
│       ├── Dockerfile
│       └── Documents/                    # Agent-accessible documents
│
├── Frontend/
│   ├── app.py                            # Flask application
│   ├── startup.py                        # Azure Web App startup
│   ├── deploy.ps1                        # Azure Container Apps deployment
│   ├── web.config                        # IIS configuration
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── Documents/                        # Frontend document assets
│   ├── templates/
│   │   ├── applications.html             # Applications dashboard
│   │   ├── workflow-new.html             # Workflow visualizer
│   │   └── process-application.html      # Application processing view
│   └── static/
│       ├── css/                          # Stylesheets
│       └── js/                           # Client-side JavaScript
│
└── README.md
```

---

## Prerequisites

- **Python 3.11+**
- **Azure Subscription** with the following resources provisioned:
  - Azure AI Foundry project with a GPT-4o deployment
  - Azure Cosmos DB instance (optional — for frontend agent logs)
  - Azure Container Registry (for Docker deployments)
- **Azure CLI** (`az`) — for deployment
- **Docker** (optional) — for containerized runs
- **Azure authentication** via one of:
  - Azure CLI login (`az login`)
  - Environment variables (`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`)
  - Managed Identity
  - VS Code Azure extension

---

## Environment Variables

### Backend

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PROJECT_CONNECTION_STRING` | ✅ Yes | — | Azure AI Foundry project connection string |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | No | `gpt-4o` | Model deployment name |
| `PORT` | No | `8000` | Server port |
| `ROOT_PATH` | No | `""` | FastAPI root path prefix |
| `ENVIRONMENT` | No | `development` | Runtime environment |
| `ENV` | No | `dev` | Controls uvicorn hot-reload |

### Frontend

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `COSMOS_API_BASE_URL` | No | *(hardcoded fallback)* | Cosmos DB REST API endpoint |
| `PORT` | No | `8000` | Server port |

Create a `.env` file in each service directory for local development.

---

## Getting Started

### Backend

```bash
cd Backend/loanbackend

# Install dependencies
pip install -r requirements.txt

# Set required environment variable
export PROJECT_CONNECTION_STRING="<your-azure-ai-foundry-connection-string>"

# Start the server
python main.py
```

The API will be available at **http://localhost:8000**. Interactive docs at **http://localhost:8000/docs** (Swagger UI).

### Frontend

```bash
cd Frontend

# Install dependencies
pip install -r requirements.txt

# (Optional) Set Cosmos DB URL
export COSMOS_API_BASE_URL="<your-cosmos-api-url>"

# Start the server
python app.py
```

The web portal will be available at **http://localhost:8000**.

### Docker

**Backend:**

```bash
cd Backend/loanbackend
docker build -t loan-backend .
docker run -p 8000:8000 \
  -e PROJECT_CONNECTION_STRING="<your-connection-string>" \
  loan-backend
```

**Frontend:**

```bash
cd Frontend
docker build -t loan-frontend .
docker run -p 8000:8000 \
  -e COSMOS_API_BASE_URL="<your-cosmos-api-url>" \
  loan-frontend
```

---

## API Reference

### Backend API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Welcome message with available agents and endpoints |
| `GET` | `/health` | System health, orchestrator status, Azure config |
| `POST` | `/api/loan/process` | **Process a loan application** through all 9 agents. Form params: `customer_name`, `loan_amount`, `loan_purpose`, `loan_tenure`, `contact_number`, `email` |
| `GET` | `/api/loan/status/{application_id}` | Get loan application status |
| `POST` | `/api/documents/upload` | Upload documents (PDF, DOCX, TXT, JSON, XLSX, CSV, images) |
| `GET` | `/api/documents` | List all uploaded documents with metadata |
| `GET` | `/api/documents/{filename}` | Download a specific document |
| `DELETE` | `/api/documents/{filename}` | Delete a document |
| `GET` | `/api/results` | List all processing results (sorted newest first) |
| `GET` | `/api/results/{result_id}` | Get detailed result JSON |
| `GET` | `/api/results/{result_id}/download` | Download result as JSON file |
| `DELETE` | `/api/results/{result_id}` | Delete a result |

### Frontend Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Applications dashboard |
| `GET` | `/workflow` | Workflow visualizer |
| `GET` | `/process-application` | Application processing view |
| `GET` | `/health` | Health check |
| `GET` | `/api/applications` | Get all application data (pending + reviewed) |
| `GET` | `/api/applications/<id>` | Get specific application |
| `POST` | `/api/applications/<id>/process` | Process an application |
| `GET` | `/api/agent-records/<customer_id>` | Fetch agent data from Cosmos DB |
| `GET` | `/api/documents` | List documents by category |

---

## Frontend Features

### 📋 Applications Dashboard
- Two-column Kanban board: **"Yet to be Reviewed"** (pending) and **"Reviewed"** (approved / rejected)
- Application cards with customer name, loan type, amount, date, and priority badges
- **Sensitive data masking** — PAN, Aadhaar, phone, and email are masked by default
- Click-through to process individual applications

### 🔄 Workflow Visualizer
- Visual flow diagram of the entire agent pipeline
- **Auto-process** ("Process All") button to run through all agents sequentially
- Visual branching for parallel Credit Assessment + Asset Valuation
- Real-time progress indicator sidebar
- 6 pre-configured Indian customers for demo
- Agent processing modals with detailed output

### 📊 Process Application View
- **Documents Tab** — uploaded documents organized by category (Application, KYC, Financial, Property)
- **Workflow Tab** — embedded agent workflow grid
- **Analysis Tab** — final verdict (Approved / Rejected), individual agent report cards, and full audit trail

---

## Workflow & Data Flow

```
1. Upload Documents (Aadhaar, PAN, Passport, Form 16, Pay Slip,
   Bank Statements, CIBIL Report, Property Document)
                        │
2. Submit Loan Application (POST /api/loan/process)
                        │
3. Orchestrator initializes all 9 agents
                        │
4. Sequential processing with handoffs:
   ┌────────────────────┴─────────────────────┐
   │  Customer Service                         │
   │       ↓                                   │
   │  Document Verification (File Search)      │
   │       ↓                                   │
   │  Credit Qualification                     │
   │       ↓                                   │
   │  ┌─ Credit Assessment ──┐  (parallel)     │
   │  └─ Asset Valuation ────┘                 │
   │       ↓                                   │
   │  Underwriting → Decision                  │
   │       ↓                                   │
   │  Offer Generation → EMI / Fees            │
   │       ↓                                   │
   │  Customer Communication → Notifications   │
   │       ↓                                   │
   │  Audit → Compliance Report                │
   └───────────────────────────────────────────┘
                        │
5. Result saved as JSON (results/LOAN-{timestamp}.json)
                        │
6. Frontend displays results via Analysis tab
```

---

## Deployment

### Azure Container Apps (Frontend)

A PowerShell deployment script is provided at `Frontend/deploy.ps1`:

```powershell
# Full deployment (first time)
.\deploy.ps1

# Redeployment (image update only)
.\deploy.ps1 -UpdateOnly
```

This script:
1. Creates a resource group and Container Apps environment
2. Builds the Docker image in Azure Container Registry (no local Docker needed)
3. Deploys to Azure Container Apps with external HTTPS ingress

### Cloud Build (without local Docker)

```bash
az acr build --registry <your-acr-name> --image loan-backend:latest --file Dockerfile .
```

### Configuration
- **CPU:** 0.5 vCPU
- **Memory:** 1.0 Gi
- **Replicas:** 1–3 (auto-scaling)
- **Ingress:** External HTTPS on port 8000

---

## License

This project is provided as-is for demonstration and educational purposes.
