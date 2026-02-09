# Bank Workflow System - Flask Application

## Overview
This is a Flask-based banking workflow system that integrates with Azure Cosmos DB for real-time data processing. The application provides a comprehensive loan processing portal with applications dashboard and workflow management.

## Features
- **Applications Dashboard**: View and manage loan applications
- **Workflow System**: Process loans through various agents and stages
- **Cosmos DB Integration**: Real-time data fetching for specific customers
- **Indian Banking Context**: Tailored for Indian customers with INR currency, PAN, Aadhar support
- **Responsive Design**: Modern UI with Font Awesome icons and professional styling

## Technology Stack
- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: Azure Cosmos DB
- **Authentication**: Azure Managed Identity
- **Styling**: Custom CSS with Font Awesome icons

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Azure Cosmos DB account
- Azure Managed Identity (for production)

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Setup
Ensure your Azure Cosmos DB credentials are properly configured in the `Cosmos-api/app/cosmos_client.py` file.

### 3. Run the Application
```bash
python app.py
```

The application will be available at: `http://localhost:5000`

## Application Structure

```
bank-workflow/
├── app.py                     # Main Flask application
├── requirements.txt           # Python dependencies
├── templates/                 # Flask templates
│   ├── applications.html      # Applications dashboard
│   └── workflow-new.html      # Workflow page
├── static/                    # Static assets
│   ├── css/
│   │   ├── applications.css   # Applications styling
│   │   └── workflow-new.css   # Workflow styling
│   └── js/
│       ├── applications.js    # Applications logic
│       └── workflow-new.js    # Workflow logic
├── Cosmos-api/                # Cosmos DB integration (unchanged)
│   └── app/
│       └── cosmos_client.py   # Cosmos DB client
└── package.json              # Project metadata
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
   - Verify Azure credentials and managed identity configuration
   - Check network connectivity to Cosmos DB endpoint
   - Application will fallback to mock data automatically

2. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Port Already in Use**
   - Change the port in `app.py`: `app.run(debug=True, host='0.0.0.0', port=5001)`

## License
ISC License - Banking Team

## Support
For technical support and questions, please contact the Banking Team.