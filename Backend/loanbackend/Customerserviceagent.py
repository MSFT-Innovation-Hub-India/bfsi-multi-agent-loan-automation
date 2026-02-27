"""
Customer Service Agent
======================
First point of contact for loan applications.
Assists customers with form completion and provides information.

Agent ID: asst_Se1fgOvqYaeTSESaRpWpdhsD
"""

# pip install azure-ai-projects==1.0.0b10
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    FilePurpose,
    FileSearchToolDefinition,
    ToolResources,
    FileSearchToolResource,
    MessageRole
)
from azure.identity import DefaultAzureCredential

# Load environment variables
load_dotenv()

# ============================================================================
# AGENT CONFIGURATION
# ============================================================================

PROJECT_CONNECTION_STRING = os.getenv("PROJECT_CONNECTION_STRING")
MODEL_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
DOCUMENTS_PATH = os.path.join(os.path.dirname(__file__), "Documents")

# ============================================================================
# AGENT INSTRUCTIONS
# ============================================================================

AGENT_INSTRUCTIONS = """
You are the CUSTOMER SERVICE AGENT for a comprehensive loan processing system.

## YOUR ROLE
You are the first point of contact for all loan applications. Your primary responsibility 
is to assist customers with the loan application process, gather their requirements, 
and ensure they have all necessary information to proceed.

## YOUR RESPONSIBILITIES

### 1. Customer Greeting & Intake
- Welcome customers warmly and professionally
- Collect basic personal information (name, contact details)
- Understand the customer's loan requirements

### 2. Loan Requirements Gathering
- Loan amount requested
- Purpose of the loan (Home, Personal, Business, Vehicle, Education)
- Preferred loan tenure (in years/months)
- Any specific requirements or preferences

### 3. Document Guidance
- Explain required documents for loan application:
  * Identity Proof: Aadhaar Card, PAN Card, Passport
  * Address Proof: Aadhaar, Passport, Utility Bills
  * Income Proof: Form 16, Salary Slips (last 3-6 months), ITR
  * Bank Statements: Last 6-12 months
  * Property Documents: For secured loans
  * CIBIL/Credit Report: For credit assessment

### 4. Eligibility Information
- Provide basic eligibility criteria:
  * Age: 21-65 years
  * Employment: Minimum 2 years experience
  * Income: As per loan product requirements
  * Credit Score: Minimum 650+ preferred

### 5. Process Explanation
- Explain the loan processing stages
- Set expectations for timeline
- Provide contact information for queries

## COMMUNICATION GUIDELINES
- Be professional, friendly, and empathetic
- Use clear, simple language
- Confirm understanding at each step
- Address concerns proactively
- Never promise approval - only explain the process

## OUTPUT FORMAT
After gathering information, provide a structured summary:

```
CUSTOMER SERVICE SUMMARY
========================
Application Date: [Date]
Customer Name: [Name]
Contact: [Phone/Email]

LOAN REQUIREMENTS:
- Amount Requested: ₹[Amount]
- Loan Purpose: [Purpose]
- Preferred Tenure: [Years] years

DOCUMENTS CHECKLIST:
✓ Available: [List documents customer has]
✗ Required: [List documents still needed]

ELIGIBILITY NOTES:
[Any preliminary observations]

NEXT STEPS:
[What customer needs to do next]

HANDOFF TO: Document Verification Agent
STATUS: Ready for document verification
```

## TOOLS AVAILABLE
1. get_customer_documents - Retrieve list of available documents for a customer
2. get_loan_products - Get available loan products and their requirements
3. calculate_basic_eligibility - Perform basic eligibility check
4. create_application_record - Create initial application record
"""

# ============================================================================
# TOOLS / FUNCTIONS
# ============================================================================

def get_customer_documents(customer_name: str) -> Dict[str, Any]:
    """
    Retrieve list of available documents for a customer.
    
    Args:
        customer_name: Name of the customer
        
    Returns:
        Dictionary containing available documents and their status
    """
    docs_path = os.path.join(os.path.dirname(__file__), "Documents")
    
    if os.path.exists(docs_path):
        documents = os.listdir(docs_path)
        
        # Categorize documents
        identity_docs = []
        income_docs = []
        bank_docs = []
        property_docs = []
        credit_docs = []
        
        for doc in documents:
            doc_lower = doc.lower()
            if any(x in doc_lower for x in ['adhaar', 'aadhaar', 'pan', 'passport']):
                identity_docs.append(doc)
            elif any(x in doc_lower for x in ['form 16', 'pay slip', 'salary']):
                income_docs.append(doc)
            elif 'bank' in doc_lower:
                bank_docs.append(doc)
            elif 'property' in doc_lower:
                property_docs.append(doc)
            elif 'cibil' in doc_lower:
                credit_docs.append(doc)
        
        return {
            "customer_name": customer_name,
            "documents_path": docs_path,
            "total_documents": len(documents),
            "all_documents": documents,
            "categorized": {
                "identity_proof": identity_docs,
                "income_proof": income_docs,
                "bank_statements": bank_docs,
                "property_documents": property_docs,
                "credit_reports": credit_docs
            },
            "status": "retrieved",
            "retrieved_at": datetime.now().isoformat()
        }
    
    return {
        "customer_name": customer_name,
        "error": "Documents folder not found",
        "status": "error"
    }


def get_loan_products() -> Dict[str, Any]:
    """
    Get available loan products and their requirements.
    
    Returns:
        Dictionary containing loan products information
    """
    return {
        "loan_products": [
            {
                "product_name": "Home Loan",
                "min_amount": 500000,
                "max_amount": 50000000,
                "interest_rate_range": "8.5% - 10.5%",
                "max_tenure_years": 30,
                "min_age": 21,
                "max_age": 65,
                "required_documents": [
                    "Identity Proof (Aadhaar/PAN/Passport)",
                    "Income Proof (Form 16/Salary Slips)",
                    "Bank Statements (6 months)",
                    "Property Documents",
                    "CIBIL Report"
                ]
            },
            {
                "product_name": "Personal Loan",
                "min_amount": 50000,
                "max_amount": 2500000,
                "interest_rate_range": "10.5% - 18%",
                "max_tenure_years": 7,
                "min_age": 21,
                "max_age": 60,
                "required_documents": [
                    "Identity Proof (Aadhaar/PAN)",
                    "Income Proof (Form 16/Salary Slips)",
                    "Bank Statements (3 months)"
                ]
            },
            {
                "product_name": "Business Loan",
                "min_amount": 100000,
                "max_amount": 10000000,
                "interest_rate_range": "12% - 20%",
                "max_tenure_years": 10,
                "min_age": 25,
                "max_age": 65,
                "required_documents": [
                    "Identity Proof",
                    "Business Registration",
                    "ITR (3 years)",
                    "Bank Statements (12 months)",
                    "Business Financials"
                ]
            }
        ],
        "retrieved_at": datetime.now().isoformat()
    }


def calculate_basic_eligibility(
    customer_age: int,
    monthly_income: float,
    loan_amount: float,
    loan_tenure_years: int,
    existing_emis: float = 0
) -> Dict[str, Any]:
    """
    Perform basic eligibility check for loan.
    
    Args:
        customer_age: Age of customer in years
        monthly_income: Monthly income in INR
        loan_amount: Requested loan amount in INR
        loan_tenure_years: Requested tenure in years
        existing_emis: Existing monthly EMI obligations
        
    Returns:
        Dictionary containing eligibility assessment
    """
    issues = []
    
    # Age check
    age_eligible = 21 <= customer_age <= 65
    if not age_eligible:
        issues.append(f"Age {customer_age} is outside eligible range (21-65)")
    
    # Income check (rough EMI should be < 50% of income)
    estimated_emi = loan_amount / (loan_tenure_years * 12) * 1.1  # Rough estimate with interest
    available_income = monthly_income - existing_emis
    income_ratio = estimated_emi / available_income if available_income > 0 else float('inf')
    income_eligible = income_ratio < 0.5
    
    if not income_eligible:
        issues.append(f"EMI to income ratio ({income_ratio:.1%}) exceeds 50% threshold")
    
    # Tenure check
    max_age_at_maturity = customer_age + loan_tenure_years
    tenure_eligible = max_age_at_maturity <= 70
    
    if not tenure_eligible:
        issues.append(f"Age at maturity ({max_age_at_maturity}) exceeds 70 years")
    
    overall_eligible = age_eligible and income_eligible and tenure_eligible
    
    return {
        "eligibility_status": "ELIGIBLE" if overall_eligible else "NOT_ELIGIBLE",
        "checks": {
            "age_eligible": age_eligible,
            "income_eligible": income_eligible,
            "tenure_eligible": tenure_eligible
        },
        "details": {
            "customer_age": customer_age,
            "age_at_maturity": max_age_at_maturity,
            "monthly_income": monthly_income,
            "estimated_emi": round(estimated_emi, 2),
            "emi_to_income_ratio": f"{income_ratio:.1%}",
            "available_income_after_emi": round(available_income - estimated_emi, 2)
        },
        "issues": issues,
        "recommendation": "Proceed to document verification" if overall_eligible else "Review and address issues",
        "assessed_at": datetime.now().isoformat()
    }


def create_application_record(
    customer_name: str,
    contact_phone: str,
    contact_email: str,
    loan_amount: float,
    loan_purpose: str,
    loan_tenure_years: int
) -> Dict[str, Any]:
    """
    Create initial loan application record.
    
    Args:
        customer_name: Full name of customer
        contact_phone: Contact phone number
        contact_email: Contact email address
        loan_amount: Requested loan amount
        loan_purpose: Purpose of the loan
        loan_tenure_years: Requested tenure in years
        
    Returns:
        Dictionary containing application record
    """
    application_id = f"LOAN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        "application_id": application_id,
        "status": "INITIATED",
        "customer_details": {
            "name": customer_name,
            "phone": contact_phone,
            "email": contact_email
        },
        "loan_details": {
            "amount_requested": loan_amount,
            "purpose": loan_purpose,
            "tenure_years": loan_tenure_years
        },
        "created_at": datetime.now().isoformat(),
        "current_stage": "CUSTOMER_SERVICE",
        "next_stage": "DOCUMENT_VERIFICATION",
        "message": f"Application {application_id} created successfully"
    }


# ============================================================================
# TOOL DEFINITIONS FOR AZURE AI FOUNDRY
# ============================================================================


# ============================================================================
# DYNAMIC AGENT CREATION
# ============================================================================

def create_customer_service_agent():
    """Create Customer Service Agent with file search capabilities"""
    
    try:
        project_client = AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=PROJECT_CONNECTION_STRING
        )
        
        # Upload documents if available
        uploaded_files = []
        
        # Supported file types for Azure AI file search (retrieval)
        supported_extensions = ['.c', '.cpp', '.cs', '.css', '.doc', '.docx', '.go', 
                                '.html', '.java', '.js', '.json', '.md', '.pdf', 
                                '.php', '.pptx', '.py', '.rb', '.sh', '.tex', '.ts', '.txt']
        
        if os.path.exists(DOCUMENTS_PATH):
            for filename in os.listdir(DOCUMENTS_PATH):
                file_path = os.path.join(DOCUMENTS_PATH, filename)
                if os.path.isfile(file_path):
                    file_ext = os.path.splitext(filename)[1].lower()
                    if file_ext not in supported_extensions:
                        continue
                    
                    try:
                        file = project_client.agents.upload_file_and_poll(
                            file_path=file_path,
                            purpose=FilePurpose.AGENTS
                        )
                        uploaded_files.append(file)
                    except Exception:
                        continue
        
        # Create agent with or without file search
        if uploaded_files:
            vector_store = project_client.agents.create_vector_store_and_poll(
                file_ids=[file.id for file in uploaded_files],
                name="Customer_Service_Documents"
            )
            
            agent = project_client.agents.create_agent(
                model=MODEL_DEPLOYMENT,
                name="customer-service-agent",
                instructions=AGENT_INSTRUCTIONS,
                tools=[FileSearchToolDefinition()],
                tool_resources=ToolResources(
                    file_search=FileSearchToolResource(vector_store_ids=[vector_store.id])
                )
            )
        else:
            agent = project_client.agents.create_agent(
                model=MODEL_DEPLOYMENT,
                name="customer-service-agent",
                instructions=AGENT_INSTRUCTIONS
            )
            vector_store = None
        
        # Create a thread
        thread = project_client.agents.create_thread()
        
        return {
            "project_client": project_client,
            "agent": agent,
            "thread": thread,
            "vector_store": vector_store,
            "uploaded_files": uploaded_files
        }
    
    except Exception as e:
        print(f"Error creating customer service agent: {e}")
        raise


if __name__ == "__main__":
    # Test agent creation
    result = create_customer_service_agent()
    print(f"✅ Customer Service Agent Created: {result['agent'].id}")
    print(f"   Thread ID: {result['thread'].id}")
    print(f"   Documents uploaded: {len(result['uploaded_files'])}")

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_customer_documents",
            "description": "Retrieve list of available documents for a customer from the documents folder",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "The name of the customer"
                    }
                },
                "required": ["customer_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_loan_products",
            "description": "Get available loan products and their requirements, interest rates, and eligibility criteria",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_basic_eligibility",
            "description": "Perform basic eligibility check based on age, income, and loan requirements",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_age": {
                        "type": "integer",
                        "description": "Age of the customer in years"
                    },
                    "monthly_income": {
                        "type": "number",
                        "description": "Monthly income of the customer in INR"
                    },
                    "loan_amount": {
                        "type": "number",
                        "description": "Requested loan amount in INR"
                    },
                    "loan_tenure_years": {
                        "type": "integer",
                        "description": "Requested loan tenure in years"
                    },
                    "existing_emis": {
                        "type": "number",
                        "description": "Existing monthly EMI obligations in INR"
                    }
                },
                "required": ["customer_age", "monthly_income", "loan_amount", "loan_tenure_years"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_application_record",
            "description": "Create initial loan application record with customer and loan details",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "Full name of the customer"
                    },
                    "contact_phone": {
                        "type": "string",
                        "description": "Contact phone number"
                    },
                    "contact_email": {
                        "type": "string",
                        "description": "Contact email address"
                    },
                    "loan_amount": {
                        "type": "number",
                        "description": "Requested loan amount in INR"
                    },
                    "loan_purpose": {
                        "type": "string",
                        "description": "Purpose of the loan (Home, Personal, Business, etc.)"
                    },
                    "loan_tenure_years": {
                        "type": "integer",
                        "description": "Requested loan tenure in years"
                    }
                },
                "required": ["customer_name", "contact_phone", "contact_email", "loan_amount", "loan_purpose", "loan_tenure_years"]
            }
        }
    }
]


# ============================================================================
# AGENT CLASS
# ============================================================================

class CustomerServiceAgent:
    """Customer Service Agent for loan processing"""
    
    def __init__(self):
        self.project_client = AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=PROJECT_CONNECTION_STRING
        )
        self.instructions = AGENT_INSTRUCTIONS
        self.tools = TOOLS
        
    def _handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Handle tool calls from the agent"""
        tool_functions = {
            "get_customer_documents": get_customer_documents,
            "get_loan_products": get_loan_products,
            "calculate_basic_eligibility": calculate_basic_eligibility,
            "create_application_record": create_application_record
        }
        
        if tool_name in tool_functions:
            result = tool_functions[tool_name](**arguments)
            return json.dumps(result, indent=2)
        
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
    
    def process_request(self, user_message: str) -> str:
        """Process a customer service request"""
        # Create agent dynamically
        agent = self.project_client.agents.create_agent(
            model=MODEL_DEPLOYMENT,
            name="customer-service-agent",
            instructions=self.instructions
        )
        thread = self.project_client.agents.create_thread()
        
        # Create user message
        self.project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=user_message
        )
        
        # Run the agent
        run = self.project_client.agents.create_and_process_run(
            thread_id=thread.id,
            agent_id=agent.id
        )
        
        # Get messages
        messages = self.project_client.agents.list_messages(thread_id=thread.id)
        
        # Extract the response text from the latest assistant message
        for message in messages.data:
            # Check role as string to handle both enum and string values
            role_str = str(message.role).upper() if hasattr(message.role, 'value') else str(message.role).upper()
            if 'ASSISTANT' in role_str or message.role == "assistant":
                if hasattr(message, 'content') and message.content:
                    for content_item in message.content:
                        if hasattr(content_item, 'text'):
                            return content_item.text.value
                        elif hasattr(content_item, 'value'):
                            return str(content_item.value)
                break
        
        return "No response from agent"
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            "name": "Customer Service Agent",
            "description": "Assists customers with form completion and provides information",
            "stage": 1,
            "next_agent": "Document Verification Agent",
            "tools": [tool["function"]["name"] for tool in self.tools]
        }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  CUSTOMER SERVICE AGENT")
    print("=" * 70)
    
    # Initialize agent
    agent = CustomerServiceAgent()
    print(f"\nAgent Info: {json.dumps(agent.get_agent_info(), indent=2)}")
    
    # Test with sample request
    test_message = """
    Hello, I am Kala Divan and I want to apply for a home loan.
    I need a loan of 40 lakhs for purchasing a property.
    I want a tenure of 20 years.
    Please help me understand the process and what documents I need.
    """
    
    print(f"\n{'='*70}")
    print("Processing Request...")
    print(f"{'='*70}")
    
    response = agent.process_request(test_message)
    print(f"\nAgent Response:\n{response}")