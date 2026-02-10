# Bank Workflow System - Flask Application

## Overview
This is a Flask-based banking workflow system that integrates with Azure Cosmos DB for real-time data processing. The application provides a comprehensive loan processing portal with applications dashboard and workflow management. It is containerized with Docker and deployed on **Azure Container Apps**.

## Features
- **Applications Dashboard**: View and manage loan applications
- **Workflow System**: Process loans through various agents and stages
- **Cosmos DB Integration**: Real-time data fetching for specific customers
- **Indian Banking Context**: Tailored for Indian customers with INR currency, PAN, Aadhar support
- **Responsive Design**: Modern UI with Font Awesome icons and professional styling
- **Containerized Deployment**: Docker image deployed on Azure Container Apps

## Technology Stack
- **Backend**: Flask (Python 3.11), Gunicorn WSGI server
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: Azure Cosmos DB (REST API)
- **Container Registry**: Azure Container Registry (ACR)
- **Hosting**: Azure Container Apps (serverless containers)
- **Styling**: Custom CSS with Font Awesome icons

---

## Docker Image & Container Registry

| Property | Value |
|---|---|
| **Registry** | `loanprocessingapi.azurecr.io` |
| **Image** | `loanprocessingapi.azurecr.io/loan-workflow:latest` |
| **Base Image** | `python:3.11-slim` (multi-stage build) |
| **Exposed Port** | `8000` |
| **WSGI Server** | Gunicorn (4 workers, 2 threads) |
| **Health Check** | `GET /health` |

### Docker Build (Cloud — no local Docker needed)
```bash
az acr build --registry loanprocessingapi --image loan-workflow:latest --file Dockerfile .
```

### Docker Build (Local)
```bash
docker build -t loan-workflow .
docker run -p 8000:8000 -e COSMOS_API_BASE_URL="https://cosmosdb-api-h3f2fnbth2dccaed.eastus2-01.azurewebsites.net" loan-workflow
```

---

## Azure Container Apps Deployment

| Property | Value |
|---|---|
| **Resource Group** | `fsi-demos` |
| **Location** | `eastus2` |
| **Container App** | `loan-workflow-app` |
| **Environment** | `loan-workflow-env` |
| **CPU / Memory** | 0.5 vCPU / 1.0 Gi |
| **Replicas** | Min: 1, Max: 3 |
| **Ingress** | External (HTTPS) |

### Environment Variables
| Variable | Description |
|---|---|
| `COSMOS_API_BASE_URL` | Cosmos DB REST API endpoint |
| `PORT` | Container port (default: `8000`) |

### First-Time Deployment
```powershell
.\deploy.ps1
```

### Redeploy After Code Changes
```powershell
.\deploy.ps1 -UpdateOnly
```

The `-UpdateOnly` flag skips resource creation and only rebuilds the image and updates the container app.

---

## Local Development

### Prerequisites
- Python 3.8 or higher
- Azure Cosmos DB account (or use mock data fallback)

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Setup
Create a `.env` file (optional):
```env
COSMOS_API_BASE_URL=https://cosmosdb-api-h3f2fnbth2dccaed.eastus2-01.azurewebsites.net
PORT=8000
```

### 3. Run the Application
```bash
python app.py
```

The application will be available at: `http://localhost:8000`

---

## Application Structure

```
Loan-workflow/
├── app.py                          # Main Flask application
├── Dockerfile                      # Multi-stage Docker build
├── .dockerignore                   # Docker build exclusions
├── deploy.ps1                      # Azure Container Apps deployment script
├── requirements.txt                # Python dependencies
├── startup.py                      # Azure Web App startup (legacy)
├── web.config                      # IIS config (legacy)
├── Documents/                      # Loan application documents (PDF/images)
├── templates/                      # Flask HTML templates
│   ├── applications.html           # Applications dashboard
│   ├── process-application.html    # Loan processing page (Documents/Workflow/Analysis)
│   └── workflow-new.html           # Workflow page
├── static/                         # Static assets
│   ├── css/
│   │   ├── applications.css        # Applications styling
│   │   ├── process-application.css # Process application styling
│   │   └── workflow-new.css        # Workflow styling
│   └── js/
│       ├── applications.js         # Applications logic
│       ├── process-application.js  # Process application logic
│       └── workflow-new.js         # Workflow logic
└── README-Flask.md                 # This file
```

## API Endpoints

### Applications API
- `GET /` - Applications dashboard
- `GET /api/applications` - Get all applications
- `GET /api/applications/<id>` - Get specific application
- `POST /api/applications/<id>/process` - Process an application

### Workflow API  
- `GET /workflow` - Workflow page
- `GET /api/cosmos-data/<customer_id>` - Fetch Cosmos DB data

### Health & Documents
- `GET /health` - Health check endpoint (returns `{"status": "healthy"}`)
- `GET /api/documents` - List uploaded documents
- `GET /Documents/<filename>` - Serve a document file

## Key Features

### 1. Applications Dashboard
- View pending and reviewed applications
- Search and filter functionality
- Detailed application modal views
- Real-time application processing

### 2. Cosmos DB Integration
- Seamless integration with existing Cosmos DB
- Fallback to mock data if Cosmos is unavailable
- Real-time agent interaction data
- Risk assessment and timeline tracking

### 3. Workflow System
- Multi-stage loan processing workflow
- Agent-based processing system
- Auto-processing capabilities
- Progress tracking and notifications

## Customer Data Format

The application supports Indian banking context with:
- **Currency**: Indian Rupees (INR)
- **Identification**: PAN and Aadhar numbers
- **Regional**: Indian cities and states
- **Phone**: +91 country code format
- **Banking**: Indian banking terminologies

## Sample Customer IDs
- `CUST0241` - Kala Divan (Cosmos DB integrated)
- `CUST0001` - Rajesh Kumar Sharma
- `CUST0002` - Priya Patel  
- `CUST0003` - Amit Singh
- `CUST0005` - Vikram Agarwal

## Development Notes

### Cosmos DB Integration
- Customer `CUST0241` is specifically configured for Cosmos DB integration
- All other customers use local application data
- Cosmos client handles authentication via Azure Managed Identity
- Fallback mechanisms ensure application works even without Cosmos access

### Security Features
- Sensitive data masking (PAN, Aadhar, Phone, Email)
- Secure API endpoints
- Input validation and sanitization

## Troubleshooting

### Common Issues

1. **Cosmos DB Connection Issues**
   - Verify `COSMOS_API_BASE_URL` environment variable is set correctly
   - Check network connectivity to Cosmos DB endpoint
   - Application will fallback to mock data automatically

2. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Port Already in Use**
   - Change the `PORT` environment variable or run: `PORT=5001 python app.py`

4. **ACR Build Fails**
   - Ensure you're logged in: `az login`
   - Verify subscription: `az account show`
   - Check ACR access: `az acr show --name loanprocessingapi`

5. **Container App Not Responding**
   - Check logs: `az containerapp logs show --name loan-workflow-app --resource-group fsi-demos`
   - Verify health: `curl https://<app-url>/health`
   - Check revision status: `az containerapp revision list --name loan-workflow-app --resource-group fsi-demos -o table`

## License
ISC License - Banking Team

## Support
For technical support and questions, please contact the Banking Team.