# 🏦 Global Trust Bank - Loan Processing Workflow System

<p align="center">
  <img src="https://img.shields.io/badge/Flask-2.3.3-green?style=for-the-badge&logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Azure-Cosmos%20DB-0089D6?style=for-the-badge&logo=microsoft-azure" alt="Azure Cosmos DB">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License">
</p>

<p align="center">
  <b>An AI-driven, enterprise-grade loan processing portal built for the Indian banking sector</b>
</p>

<p align="center">
  🌐 <b>Live Demo:</b> <a href="https://bank-workflow-hxbxhyd8f7bvdwc4.eastus2-01.azurewebsites.net/">https://bank-workflow-hxbxhyd8f7bvdwc4.eastus2-01.azurewebsites.net/</a>
</p>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [API Reference](#-api-reference)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Deployment](#-deployment)


---

## 🎯 Overview

**Global Trust Bank Loan Workflow System** is an AI-driven loan automation platform powered by **Azure AI Foundry**. This intelligent system leverages cutting-edge AI agents to streamline end-to-end loan processing—from application intake and document verification to risk assessment and final decisioning. Built with Flask and integrated with Azure Cosmos DB, it empowers bank officers with an intelligent dashboard that automates repetitive tasks, reduces processing time, and delivers smarter lending decisions through AI-powered insights.


## ✨ Features

### 📁 Applications Dashboard
- **Dual-Column View**: Separate pending and reviewed applications for quick navigation
- **Priority Indicators**: High, medium, and low priority tagging
- **Quick Search**: Filter applications by customer name, ID, or loan type
- **Detailed Modals**: View complete customer information with one click

### 🔄 Intelligent Workflow System
- **Multi-Agent Processing**: Automated agents for different verification stages
  - `ApplicationAssist Agent` - Captures and validates customer details
  - `DocumentChecker Agent` - Verifies KYC and financial documents
  - `Audit Agent` - Maintains complete processing trail
- **Auto-Process Mode**: Batch process multiple applications automatically
- **Real-time Status Updates**: Live notifications as each stage completes

### 📄 Document Management
- **Categorized Documents**: Organized into KYC, Financial, and Property sections
- **Visual Document Viewer**: In-app preview for images and PDFs
- **Verification Status**: Track document verification status (Verified/Pending)
- **Supported Formats**: PNG, JPG, PDF documents

### 📊 Analysis & Reporting
- **Final Verdict Display**: Clear approve/reject recommendations
- **Agent Reports**: Detailed logs from each processing agent
- **Risk Assessment**: Comprehensive credit and income analysis
- **Audit Trail**: Complete history of all actions taken

### 🔗 Cosmos DB Integration
- **REST API Integration**: Seamless connection to Azure Cosmos DB
- **Graceful Fallback**: Mock data support when external APIs are unavailable
- **Real-time Data Sync**: Instant access to customer interaction history

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT BROWSER                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ Applications│  │  Workflow   │  │  Process Application    │ │
│  │  Dashboard  │  │    View     │  │  (Docs/Workflow/Analysis│ │
│  └──────┬──────┘  └──────┬──────┘  └────────────┬────────────┘ │
└─────────┼────────────────┼──────────────────────┼───────────────┘
          │                │                      │
          ▼                ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FLASK APPLICATION                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                     app.py (Routes)                        │ │
│  │  • GET /                  → Applications Dashboard         │ │
│  │  • GET /workflow          → Workflow View                  │ │
│  │  • GET /process-application → Document Processing          │ │
│  │  • GET /api/applications  → Fetch All Applications         │ │
│  │  • GET /api/cosmos-data   → Fetch Cosmos DB Data           │ │
│  │  • POST /api/applications/<id>/process → Process Loan      │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
          │                                        ▲
          │  REST API Request                      │  Agent Logs & Results
          ▼                                        │
┌─────────────────────────────────────────────────────────────────┐
│                    AZURE COSMOS DB API                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  External REST API for Customer Logs & Agent Interactions  │ │
│  │  Endpoint: cosmosdb-api-*.azurewebsites.net               │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
          ▲                 ▲                     ▲
          │    Read/Write   │    Read/Write       │   Read/Write
          ▼                 ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                 🤖 AI AGENTS (Azure AI Foundry)                 │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Application  │  │  Document    │  │       Audit          │  │
│  │ Assist Agent │  │Checker Agent │  │       Agent          │  │
│  │              │  │              │  │                      │  │
│  │ • Capture    │  │ • Verify KYC │  │ • Log all actions    │  │
│  │   details    │  │ • Check docs │  │ • Track processing   │  │
│  │ • Validate   │  │ • Assess risk│  │ • Generate audit     │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Credit     │  │    Risk      │  │    Underwriting      │  │
│  │ Score Agent  │  │Evaluator Agent│  │       Agent          │  │
│  │              │  │              │  │                      │  │
│  │ • CIBIL check│  │ • Risk score │  │ • Final decision     │  │
│  │ • Score calc │  │ • Flag issues│  │ • Loan terms         │  │
│  │ • Eligibility│  │ • Compliance │  │ • Approval/Reject    │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---
## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** installed on your machine
- **pip** package manager
- (Optional) Azure Cosmos DB account for production use

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/loan-workflow.git
   cd loan-workflow
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   ```
   http://localhost:5000
   ```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `COSMOS_API_BASE_URL` | Base URL for Cosmos DB REST API | `https://cosmosdb-api-*.azurewebsites.net` |
| `PORT` | Port for production deployment | `8000` |

---

## 📚 API Reference

### Applications Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Applications dashboard (HTML) |
| `GET` | `/workflow` | Workflow processing page (HTML) |
| `GET` | `/process-application` | Document review page (HTML) |
| `GET` | `/api/applications` | Fetch all applications (JSON) |
| `GET` | `/api/applications/<id>` | Fetch single application (JSON) |
| `POST` | `/api/applications/<id>/process` | Approve/Reject application |

### Data Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/cosmos-data/<customer_id>` | Fetch customer logs from Cosmos DB |
| `GET` | `/api/documents` | List all uploaded documents |
| `GET` | `/Documents/<filename>` | Serve a specific document file |

### Example Response - Get Applications

```json
{
  "pending": [
    {
      "id": "CUST0001",
      "customerName": "Rajesh Kumar Sharma",
      "loanType": "Home Loan",
      "amount": 2500000,
      "creditScore": 750,
      "priority": "high",
      "status": "pending"
    }
  ],
  "reviewed": [...]
}
```

---

## 📂 Project Structure

```
Loan-workflow/
├── 📄 app.py                    # Main Flask application & API routes
├── 📄 startup.py                # Azure Web App startup script
├── 📄 requirements.txt          # Python dependencies
├── 📄 web.config                # IIS configuration for Azure
├── 📄 README.md                 # This file
│
├── 📁 Documents/                # Customer uploaded documents
│   ├── Adhaar.png
│   ├── Pan.png
│   ├── Passport.png
│   ├── Cibil.png
│   ├── Pay Slip.pdf
│   ├── Bank transactions.pdf
│   ├── Form 16.png
│   └── Property Document.pdf
│
├── 📁 templates/                # Jinja2 HTML templates
│   ├── applications.html        # Main dashboard view
│   ├── workflow-new.html        # Workflow processing view
│   └── process-application.html # Document review & analysis
│
└── 📁 static/                   # Static assets
    ├── 📁 css/
    │   ├── applications.css
    │   ├── workflow-new.css
    │   └── process-application.css
    └── 📁 js/
        ├── applications.js
        ├── workflow-new.js
        └── process-application.js
```

---

## ⚙️ Configuration

### Cosmos DB Setup

The application connects to an external Cosmos DB REST API. Configure the endpoint:

```python
# In app.py or via environment variable
COSMOS_API_BASE_URL = os.environ.get(
    'COSMOS_API_BASE_URL', 
    'https://cosmosdb-api-*.azurewebsites.net'
)
```

### Application Data

Sample loan application data is defined in `app.py`. Modify the `applications_data` dictionary to customize:

- Customer information (name, contact, employment)
- Loan details (type, amount, term)
- Credit information (score, income)
- Identity documents (PAN, Aadhaar)

---

## 🚢 Deployment

### Azure Web App Deployment

1. **Create Azure Web App** (Python 3.8+)

2. **Configure startup command**
   ```
   gunicorn --bind=0.0.0.0 --timeout 600 app:app
   ```

3. **Set environment variables** in Azure Portal:
   - `COSMOS_API_BASE_URL` → Your Cosmos DB API endpoint
   - `WEBSITE_PORT` → `8000`

4. **Deploy via Git** or Azure CLI
   ```bash
   az webapp up --name your-app-name --resource-group your-rg
   ```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["gunicorn", "--bind=0.0.0.0:8000", "app:app"]
```

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Flask 2.3.3, Python 3.8+ |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Database** | Azure Cosmos DB (REST API) |
| **Icons** | Font Awesome 6.x |
| **Server** | Gunicorn (Production) |
| **Hosting** | Azure Web Apps |

---

## 🧪 Testing

### Manual Testing

1. Navigate to `http://localhost:5000`
2. Click on any pending application
3. Use "Process Application" to start workflow
4. Test with different Customer IDs: `CUST0001`, `CUST0002`, `CUST0003`, `CUST0241`

### API Testing

```bash
# Get all applications
curl http://localhost:5000/api/applications

# Get specific application
curl http://localhost:5000/api/applications/CUST0001

# Fetch Cosmos data
curl http://localhost:5000/api/cosmos-data/CUST0002

# Process an application
curl -X POST http://localhost:5000/api/applications/CUST0001/process \
  -H "Content-Type: application/json" \
  -d '{"decision": "approved"}'
```

---