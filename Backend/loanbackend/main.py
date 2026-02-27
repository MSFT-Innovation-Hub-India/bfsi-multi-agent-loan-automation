"""
FastAPI Backend for Loan Processing Multi-Agent Orchestrator.
Provides loan application processing with Azure AI Foundry agents.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from datetime import datetime
from typing import List, Optional, Dict
import logging
import os
from dotenv import load_dotenv
import uvicorn
from pathlib import Path
import json
import shutil
import tempfile

# Initialize logging
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import orchestrator
try:
    from simple_orchestrator import SimpleLoanOrchestrator
    ORCHESTRATOR_AVAILABLE = True
    logger.info("✅ Successfully imported orchestrator module")
except ImportError as e:
    logger.warning(f"⚠️ Orchestrator module not available: {e}")
    ORCHESTRATOR_AVAILABLE = False
    
    # Fallback for when orchestrator is not available
    class SimpleLoanOrchestrator:
        def __init__(self):
            pass
        
        def run(self, customer_name, loan_amount, loan_purpose, tenure_years):
            logger.info("🎯 Orchestrator simulated (module not available)")
            return {
                "customer_service": "Simulation mode",
                "document_verification": "Simulation mode",
                "credit_qualification": "Simulation mode",
                "credit_assessment": "Simulation mode",
                "asset_valuation": "Simulation mode",
                "underwriting": "Simulation mode - APPROVED",
                "offer_generation": "Simulation mode",
                "customer_communication": "Simulation mode",
                "audit": "Simulation mode"
            }

# --- Configuration ---
DOCUMENTS_FOLDER = Path(__file__).parent / "Documents"
DOCUMENTS_FOLDER.mkdir(exist_ok=True)

RESULTS_FOLDER = Path(__file__).parent / "results"
RESULTS_FOLDER.mkdir(exist_ok=True)

# Get root_path from environment variable
root_path = os.getenv("ROOT_PATH", "")

# --- FastAPI Application ---
app = FastAPI(
    title="Loan Processing Multi-Agent API",
    description="REST API for loan application processing using Azure AI Foundry agents. Handles customer service, document verification, credit assessment, and more.",
    version="1.0.0",
    root_path=root_path,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "root",
            "description": "Root endpoint operations"
        },
        {
            "name": "health",
            "description": "Health check operations"
        },
        {
            "name": "LoanProcessing",
            "description": "Loan application processing operations"
        },
        {
            "name": "Documents",
            "description": "Document upload and management"
        },
        {
            "name": "Results",
            "description": "Analysis results and reports"
        }
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for your frontend domains in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT"],
    allow_headers=["*"]
)

# --- API Endpoints ---

@app.get("/",
         tags=["root"])
async def read_root():
    """
    Welcome endpoint for the Loan Processing API.
    
    Returns:
    - Dict: Welcome message and service information
    """
    return {
        "message": "Welcome to Loan Processing Multi-Agent API",
        "description": "Azure AI Foundry agents for comprehensive loan processing",
        "version": "1.0.0",
        "service": "running",
        "orchestrator_available": ORCHESTRATOR_AVAILABLE,
        "agents": [
            "Customer Service",
            "Document Verification",
            "Credit Qualification",
            "Credit Assessment",
            "Asset Valuation",
            "Underwriting",
            "Offer Generation",
            "Customer Communication",
            "Audit"
        ],
        "endpoints": {
            "process_loan": "/api/loan/process",
            "upload_documents": "/api/documents/upload",
            "list_documents": "/api/documents",
            "delete_document": "/api/documents/{filename}",
            "get_results": "/api/results",
            "download_result": "/api/results/{filename}",
            "health_check": "/health",
            "api_docs": "/docs"
        }
    }


@app.get("/health",
         tags=["health"])
async def health_check():
    """
    Health check endpoint that verifies system status.
    
    Returns:
    - Dict: Health status and system information
    """
    try:
        # Check documents folder
        documents_exist = DOCUMENTS_FOLDER.exists()
        document_count = len(list(DOCUMENTS_FOLDER.glob("*.*"))) if documents_exist else 0
        
        # Check orchestrator
        orchestrator_status = "available" if ORCHESTRATOR_AVAILABLE else "unavailable"
        
        # Check Azure connection string
        connection_string = os.getenv("PROJECT_CONNECTION_STRING")
        azure_configured = connection_string is not None and len(connection_string) > 0
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "orchestrator": orchestrator_status,
            "azure_configured": azure_configured,
            "documents_folder": str(DOCUMENTS_FOLDER),
            "stats": {
                "total_documents": document_count,
                "results_available": len(list(RESULTS_FOLDER.glob("*.json")))
            },
            "details": {
                "api_version": "1.0.0",
                "environment": os.getenv("ENVIRONMENT", "development"),
                "port": os.getenv("PORT", "8000"),
                "model": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "details": {
                "api_version": "1.0.0"
            }
        }


@app.post("/api/loan/process",
          tags=["LoanProcessing"])
async def process_loan_application(
    customer_name: str = Form(default="Kala Divan", description="Customer name", example="Kala Divan"),
    loan_amount: float = Form(default=4000000, description="Loan amount in rupees", example=4000000),
    loan_purpose: str = Form(default="Home Loan", description="Purpose of loan (e.g., Home Loan)", example="Home Loan"),
    loan_tenure: int = Form(default=20, description="Loan tenure in years", example=20),
    contact_number: Optional[str] = Form(default="+91-9876543210", description="Customer contact number", example="+91-9876543210"),
    email: Optional[str] = Form(default="kala.divan@example.com", description="Customer email", example="kala.divan@example.com")
):
    """
    Process a loan application through the multi-agent orchestrator.
    
    This endpoint:
    1. Validates application data
    2. Executes all 9 agents in sequence
    3. Generates comprehensive analysis
    4. Returns processing results
    
    Parameters:
    - customer_name: Applicant's full name
    - loan_amount: Requested loan amount
    - loan_purpose: Purpose of the loan
    - loan_tenure: Loan repayment period in years
    - contact_number: Optional contact number
    - email: Optional email address
    
    Returns:
    - Dict: Complete loan processing results
    """
    try:
        if not ORCHESTRATOR_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="Orchestrator module not available. Please ensure all agent files are present."
            )
        
        # Generate application ID
        application_id = f"LOAN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Count available documents
        document_count = len(list(DOCUMENTS_FOLDER.glob("*.*")))
        
        # Prepare application data
        application_data = {
            "application_id": application_id,
            "customer_name": customer_name,
            "loan_amount": loan_amount,
            "loan_purpose": loan_purpose,
            "loan_tenure": loan_tenure,
            "contact_number": contact_number,
            "email": email,
            "document_count": document_count,
            "submission_date": datetime.now().isoformat()
        }
        
        logger.info(f"🚀 Starting loan processing for {application_id}")
        logger.info(f"📋 Customer: {customer_name}, Amount: ₹{loan_amount:,.2f}")
        
        # Initialize orchestrator
        from simple_orchestrator import SimpleLoanOrchestrator
        orchestrator = SimpleLoanOrchestrator()
        
        # Process loan application
        logger.info("🔄 Running multi-agent orchestrator...")
        stage_results = orchestrator.run(
            customer_name=customer_name,
            loan_amount=loan_amount,
            loan_purpose=loan_purpose,
            tenure_years=loan_tenure
        )
        
        # Determine final decision from underwriting response
        uw_response_lower = stage_results.get("underwriting", "").lower()
        if "approved" in uw_response_lower or "approve" in uw_response_lower:
            final_decision = "APPROVED"
        elif "rejected" in uw_response_lower or "reject" in uw_response_lower or "denied" in uw_response_lower:
            final_decision = "REJECTED"
        elif "refer" in uw_response_lower or "review" in uw_response_lower:
            final_decision = "REFERRED"
        else:
            final_decision = "PENDING"
        
        # Save results
        result_file = RESULTS_FOLDER / f"{application_id}.json"
        result_data = {
            "application_id": application_id,
            "application_data": application_data,
            "final_decision": final_decision,
            "stages": stage_results,
            "conversation_log": orchestrator.caller.conversation_log,
            "completion_time": datetime.now().isoformat()
        }
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Loan processing completed for {application_id}")
        
        return {
            "status": "completed",
            "application_id": application_id,
            "application_data": application_data,
            "final_decision": final_decision,
            "stages": stage_results,
            "result_file": str(result_file.name),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Loan processing failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Loan processing failed: {str(e)}"
        )


@app.post("/api/documents/upload",
          tags=["Documents"])
async def upload_documents(
    files: List[UploadFile] = File(..., description="Documents to upload (PDF, DOCX, TXT, etc.)")
):
    """
    Upload multiple documents for loan processing.
    Supports PDF, DOCX, TXT, and other document formats.
    
    Parameters:
    - files: List of files to upload
    
    Returns:
    - Dict: Upload confirmation with file details
    """
    try:
        uploaded_files = []
        failed_files = []
        
        # Supported file extensions
        supported_extensions = [
            '.pdf', '.docx', '.doc', '.txt', '.json',
            '.xlsx', '.xls', '.csv', '.png', '.jpg', '.jpeg'
        ]
        
        for file in files:
            try:
                # Get file extension
                file_ext = Path(file.filename).suffix.lower()
                
                # Validate file type
                if file_ext not in supported_extensions:
                    failed_files.append({
                        "filename": file.filename,
                        "error": f"Unsupported file type: {file_ext}"
                    })
                    continue
                
                # Save file
                file_path = DOCUMENTS_FOLDER / file.filename
                with open(file_path, 'wb') as f:
                    content = await file.read()
                    f.write(content)
                
                uploaded_files.append({
                    "filename": file.filename,
                    "size": len(content),
                    "content_type": file.content_type,
                    "path": str(file_path)
                })
                
                logger.info(f"✅ Uploaded {file.filename}")
                
            except Exception as file_error:
                logger.error(f"Failed to upload {file.filename}: {str(file_error)}")
                failed_files.append({
                    "filename": file.filename,
                    "error": str(file_error)
                })
        
        return {
            "message": f"Uploaded {len(uploaded_files)} files successfully",
            "uploaded_files": uploaded_files,
            "failed_files": failed_files,
            "total_documents": len(list(DOCUMENTS_FOLDER.glob("*.*"))),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )


@app.get("/api/documents",
         tags=["Documents"])
async def list_documents():
    """
    List all uploaded documents in the Documents folder.
    
    Returns:
    - Dict: List of documents with metadata
    """
    try:
        documents = []
        
        for file_path in DOCUMENTS_FOLDER.glob("*.*"):
            if file_path.is_file():
                stat = file_path.stat()
                documents.append({
                    "filename": file_path.name,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "extension": file_path.suffix
                })
        
        return {
            "documents": documents,
            "count": len(documents),
            "folder": str(DOCUMENTS_FOLDER),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to list documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list documents: {str(e)}"
        )


@app.delete("/api/documents/{filename}",
            tags=["Documents"])
async def delete_document(filename: str):
    """
    Delete a specific document from the Documents folder.
    
    Parameters:
    - filename: Name of the document to delete
    
    Returns:
    - Dict: Deletion confirmation
    """
    try:
        file_path = DOCUMENTS_FOLDER / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Document not found: {filename}"
            )
        
        file_path.unlink()
        
        return {
            "message": "Document deleted successfully",
            "filename": filename,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {str(e)}"
        )


@app.get("/api/documents/{filename}/download",
         tags=["Documents"])
async def download_document(filename: str):
    """
    Download a specific document from the Documents folder.
    
    Parameters:
    - filename: Name of the document to download
    
    Returns:
    - FileResponse: Document file
    """
    try:
        file_path = DOCUMENTS_FOLDER / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Document not found: {filename}"
            )
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/octet-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download document: {str(e)}"
        )


@app.get("/api/results",
         tags=["Results"])
async def list_results():
    """
    List all loan processing results.
    
    Returns:
    - Dict: List of result files with metadata
    """
    try:
        results = []
        
        for file_path in RESULTS_FOLDER.glob("*.json"):
            if file_path.is_file():
                stat = file_path.stat()
                
                # Read basic info from result file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        application_data = data.get("application_data", {})
                except:
                    application_data = {}
                
                results.append({
                    "filename": file_path.name,
                    "application_id": application_data.get("application_id", "Unknown"),
                    "customer_name": application_data.get("customer_name", "Unknown"),
                    "loan_amount": application_data.get("loan_amount", 0),
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        # Sort by creation time (newest first)
        results.sort(key=lambda x: x["created"], reverse=True)
        
        return {
            "results": results,
            "count": len(results),
            "folder": str(RESULTS_FOLDER),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to list results: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list results: {str(e)}"
        )


@app.get("/api/results/{filename}",
         tags=["Results"])
async def get_result(filename: str):
    """
    Get detailed loan processing result.
    
    Parameters:
    - filename: Name of the result file
    
    Returns:
    - Dict: Complete processing results
    """
    try:
        file_path = RESULTS_FOLDER / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Result not found: {filename}"
            )
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get result: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get result: {str(e)}"
        )


@app.get("/api/results/{filename}/download",
         tags=["Results"])
async def download_result(filename: str):
    """
    Download loan processing result as JSON file.
    
    Parameters:
    - filename: Name of the result file
    
    Returns:
    - FileResponse: Result JSON file
    """
    try:
        file_path = RESULTS_FOLDER / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Result not found: {filename}"
            )
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/json"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download result: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download result: {str(e)}"
        )


@app.delete("/api/results/{filename}",
            tags=["Results"])
async def delete_result(filename: str):
    """
    Delete a specific result file.
    
    Parameters:
    - filename: Name of the result file to delete
    
    Returns:
    - Dict: Deletion confirmation
    """
    try:
        file_path = RESULTS_FOLDER / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Result not found: {filename}"
            )
        
        file_path.unlink()
        
        return {
            "message": "Result deleted successfully",
            "filename": filename,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete result: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete result: {str(e)}"
        )


@app.get("/api/loan/status/{application_id}",
         tags=["LoanProcessing"])
async def get_loan_status(application_id: str):
    """
    Get status of a specific loan application.
    
    Parameters:
    - application_id: Loan application ID
    
    Returns:
    - Dict: Application status and results
    """
    try:
        # Look for result file
        result_file = RESULTS_FOLDER / f"{application_id}.json"
        
        if not result_file.exists():
            return {
                "application_id": application_id,
                "status": "not_found",
                "message": "No processing results found for this application ID"
            }
        
        # Read result file
        with open(result_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return {
            "application_id": application_id,
            "status": "completed",
            "application_data": data.get("application_data", {}),
            "processing_results": data.get("processing_results", {}),
            "completion_time": data.get("completion_time"),
            "result_file": result_file.name
        }
        
    except Exception as e:
        logger.error(f"Failed to get loan status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get loan status: {str(e)}"
        )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("ENV", "dev") == "dev"
    
    logger.info(f"🚀 Starting Loan Processing API on port {port}")
    logger.info(f"📁 Documents folder: {DOCUMENTS_FOLDER}")
    logger.info(f"📊 Results folder: {RESULTS_FOLDER}")
    logger.info(f"🔧 Orchestrator available: {ORCHESTRATOR_AVAILABLE}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=reload
    )
