"""
Credit Qualification Agent
===========================
Reviews initial credit requirements and eligibility.
Performs preliminary screening before detailed assessment.

Agent ID: asst_J2e5SYsTlj46O8L14hjQYOcl
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
from azure.ai.projects.models import MessageRole
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
You are the CREDIT QUALIFICATION AGENT for a comprehensive loan processing system.

## YOUR ROLE
You are responsible for reviewing initial credit requirements and determining 
basic eligibility before the application proceeds to detailed credit assessment 
and asset valuation. You act as a gatekeeper to ensure only qualified applications 
move forward, saving time and resources.

## YOUR RESPONSIBILITIES

### 1. Eligibility Screening
- Verify minimum age requirements (21-65 years)
- Check employment status and stability
- Validate minimum income thresholds
- Assess existing debt obligations

### 2. Credit History Review
- Verify CIBIL/credit report availability
- Check for major defaults or bankruptcies
- Review payment history patterns
- Identify any credit red flags

### 3. Income Assessment
- Validate income documentation
- Calculate gross and net income
- Assess income stability
- Verify income-to-loan ratio

### 4. Debt-to-Income Analysis
- Calculate existing EMI obligations
- Compute Fixed Obligation to Income Ratio (FOIR)
- Determine borrowing capacity
- Check against product-specific limits

### 5. Product Eligibility
- Match customer profile with loan products
- Check product-specific criteria
- Identify best-fit loan options
- Flag any product restrictions

## QUALIFICATION CRITERIA

### Minimum Requirements:
| Criteria | Home Loan | Personal Loan | Business Loan |
|----------|-----------|---------------|---------------|
| Age | 21-65 | 21-60 | 25-65 |
| Min Income | ₹25,000/month | ₹15,000/month | ₹50,000/month |
| Employment | 2 years | 1 year | 3 years business |
| CIBIL Score | 650+ | 700+ | 650+ |
| FOIR Max | 60% | 50% | 55% |

### Qualification Statuses:
- **QUALIFIED**: Meets all criteria, proceed to assessment
- **CONDITIONALLY_QUALIFIED**: Meets most criteria, needs review
- **NOT_QUALIFIED**: Does not meet minimum criteria
- **REFERRED**: Needs senior/special approval

## OUTPUT FORMAT
Provide a detailed qualification report:

```
CREDIT QUALIFICATION REPORT
===========================
Application ID: [ID]
Customer Name: [Name]
Qualification Date: [Date]

ELIGIBILITY CHECKS:
┌─────────────────────────┬──────────┬─────────────┐
│ Criteria                │ Status   │ Details     │
├─────────────────────────┼──────────┼─────────────┤
│ Age Requirement         │ ✓ PASS   │ Age: 35     │
│ Income Threshold        │ ✓ PASS   │ ₹75,000/m   │
│ Employment Stability    │ ✓ PASS   │ 5 years     │
│ Credit History          │ ✓ PASS   │ CIBIL: 750  │
│ Existing Obligations    │ ✓ PASS   │ FOIR: 25%   │
│ Product Eligibility     │ ✓ PASS   │ Home Loan   │
└─────────────────────────┴──────────┴─────────────┘

QUALIFICATION SUMMARY:
- Total Checks: 6
- Passed: 6
- Failed: 0
- Warnings: 0

BORROWING CAPACITY:
- Maximum Eligible Amount: ₹[Amount]
- Recommended Amount: ₹[Amount]
- Maximum Tenure: [Years] years

QUALIFICATION STATUS: QUALIFIED / NOT_QUALIFIED / CONDITIONAL

OBSERVATIONS:
[Any notable points]

RECOMMENDATION:
[Proceed / Hold / Reject with reasons]

HANDOFF TO: Credit Assessment Agent & Asset Valuation Agent (Parallel)
```

## TOOLS AVAILABLE
1. check_age_eligibility - Verify age requirements for loan products
2. validate_income_requirements - Check if income meets product thresholds
3. calculate_foir - Calculate Fixed Obligation to Income Ratio
4. check_credit_history_status - Verify credit report availability and basic status
5. determine_borrowing_capacity - Calculate maximum borrowing amount
6. match_loan_products - Match customer profile with eligible products
7. generate_qualification_report - Generate comprehensive qualification report
"""

# ============================================================================
# TOOLS / FUNCTIONS
# ============================================================================

def check_age_eligibility(customer_age: int, loan_type: str = "Home Loan") -> Dict[str, Any]:
    """
    Verify age requirements for loan products.
    
    Args:
        customer_age: Age of the customer in years
        loan_type: Type of loan being applied for
        
    Returns:
        Dictionary containing age eligibility results
    """
    age_limits = {
        "Home Loan": {"min": 21, "max": 65, "max_at_maturity": 70},
        "Personal Loan": {"min": 21, "max": 60, "max_at_maturity": 65},
        "Business Loan": {"min": 25, "max": 65, "max_at_maturity": 70},
        "Vehicle Loan": {"min": 21, "max": 65, "max_at_maturity": 70}
    }
    
    limits = age_limits.get(loan_type, age_limits["Home Loan"])
    
    is_eligible = limits["min"] <= customer_age <= limits["max"]
    
    return {
        "customer_age": customer_age,
        "loan_type": loan_type,
        "age_limits": limits,
        "is_eligible": is_eligible,
        "status": "PASS" if is_eligible else "FAIL",
        "years_to_max_age": limits["max"] - customer_age if is_eligible else 0,
        "max_tenure_by_age": limits["max_at_maturity"] - customer_age if is_eligible else 0,
        "remarks": f"Eligible for up to {limits['max_at_maturity'] - customer_age} years tenure" if is_eligible else f"Age must be between {limits['min']} and {limits['max']}"
    }


def validate_income_requirements(
    monthly_income: float,
    loan_type: str = "Home Loan",
    loan_amount: float = 0
) -> Dict[str, Any]:
    """
    Check if income meets product thresholds.
    
    Args:
        monthly_income: Monthly income in INR
        loan_type: Type of loan being applied for
        loan_amount: Requested loan amount (optional)
        
    Returns:
        Dictionary containing income validation results
    """
    income_requirements = {
        "Home Loan": {"min_income": 25000, "income_multiplier": 60},
        "Personal Loan": {"min_income": 15000, "income_multiplier": 20},
        "Business Loan": {"min_income": 50000, "income_multiplier": 48},
        "Vehicle Loan": {"min_income": 20000, "income_multiplier": 36}
    }
    
    req = income_requirements.get(loan_type, income_requirements["Home Loan"])
    
    meets_minimum = monthly_income >= req["min_income"]
    max_eligible_amount = monthly_income * req["income_multiplier"]
    
    if loan_amount > 0:
        amount_eligible = loan_amount <= max_eligible_amount
    else:
        amount_eligible = True
    
    return {
        "monthly_income": monthly_income,
        "annual_income": monthly_income * 12,
        "loan_type": loan_type,
        "minimum_required": req["min_income"],
        "meets_minimum_income": meets_minimum,
        "max_eligible_loan_amount": max_eligible_amount,
        "requested_amount": loan_amount if loan_amount > 0 else "Not specified",
        "amount_eligible": amount_eligible,
        "status": "PASS" if (meets_minimum and amount_eligible) else "FAIL",
        "income_category": "HIGH" if monthly_income >= 100000 else "MEDIUM" if monthly_income >= 50000 else "STANDARD",
        "remarks": "Income meets requirements" if meets_minimum else f"Minimum income of ₹{req['min_income']:,} required"
    }


def calculate_foir(
    monthly_income: float,
    existing_emis: float,
    proposed_emi: float = 0,
    other_obligations: float = 0
) -> Dict[str, Any]:
    """
    Calculate Fixed Obligation to Income Ratio (FOIR).
    
    Args:
        monthly_income: Monthly income in INR
        existing_emis: Total existing EMI obligations
        proposed_emi: Proposed EMI for new loan (optional)
        other_obligations: Other fixed monthly obligations
        
    Returns:
        Dictionary containing FOIR calculation
    """
    total_obligations = existing_emis + proposed_emi + other_obligations
    current_foir = (existing_emis + other_obligations) / monthly_income * 100 if monthly_income > 0 else 0
    proposed_foir = total_obligations / monthly_income * 100 if monthly_income > 0 else 0
    
    # Maximum FOIR thresholds
    max_foir = 60  # Generally 50-60% depending on product
    
    available_for_emi = monthly_income * (max_foir / 100) - existing_emis - other_obligations
    
    foir_status = "PASS" if proposed_foir <= max_foir else "FAIL"
    
    return {
        "monthly_income": monthly_income,
        "existing_emis": existing_emis,
        "proposed_emi": proposed_emi,
        "other_obligations": other_obligations,
        "total_obligations": total_obligations,
        "current_foir_percentage": round(current_foir, 2),
        "proposed_foir_percentage": round(proposed_foir, 2),
        "max_allowed_foir": max_foir,
        "available_for_new_emi": round(available_for_emi, 2),
        "status": foir_status,
        "foir_health": "HEALTHY" if current_foir <= 30 else "MODERATE" if current_foir <= 50 else "HIGH",
        "remarks": f"FOIR at {proposed_foir:.1f}% is within limits" if foir_status == "PASS" else f"FOIR at {proposed_foir:.1f}% exceeds {max_foir}% limit"
    }


def check_credit_history_status(customer_name: str) -> Dict[str, Any]:
    """
    Verify credit report availability and basic status.
    
    Args:
        customer_name: Name of the customer
        
    Returns:
        Dictionary containing credit history status
    """
    docs_path = os.path.join(os.path.dirname(__file__), "Documents")
    documents = os.listdir(docs_path) if os.path.exists(docs_path) else []
    
    cibil_available = any('cibil' in doc.lower() for doc in documents)
    
    # Simulated credit history check
    if cibil_available:
        return {
            "customer_name": customer_name,
            "credit_report_available": True,
            "credit_bureau": "CIBIL",
            "report_status": "AVAILABLE",
            "credit_score_range": "700-800 (Estimated)",
            "score_category": "GOOD",
            "major_defaults": False,
            "bankruptcy_flag": False,
            "settlement_flag": False,
            "writeoff_flag": False,
            "active_accounts": 5,
            "closed_accounts": 3,
            "enquiries_last_6_months": 2,
            "status": "PASS",
            "remarks": "Credit history looks healthy for loan processing"
        }
    else:
        return {
            "customer_name": customer_name,
            "credit_report_available": False,
            "credit_bureau": "CIBIL",
            "report_status": "NOT_AVAILABLE",
            "status": "PENDING",
            "remarks": "CIBIL report not found. Please upload credit report."
        }


def determine_borrowing_capacity(
    monthly_income: float,
    existing_emis: float,
    customer_age: int,
    loan_type: str = "Home Loan",
    interest_rate: float = 8.5
) -> Dict[str, Any]:
    """
    Calculate maximum borrowing amount based on income and obligations.
    
    Args:
        monthly_income: Monthly income in INR
        existing_emis: Existing EMI obligations
        customer_age: Age of customer
        loan_type: Type of loan
        interest_rate: Expected interest rate (annual %)
        
    Returns:
        Dictionary containing borrowing capacity
    """
    # Calculate available EMI capacity (50% of income minus existing EMIs)
    max_foir = 0.50
    available_emi = (monthly_income * max_foir) - existing_emis
    
    if available_emi <= 0:
        return {
            "status": "FAIL",
            "message": "No borrowing capacity due to existing obligations",
            "available_emi_capacity": 0,
            "max_loan_amount": 0
        }
    
    # Calculate max tenure based on age
    max_age_at_maturity = 70 if loan_type == "Home Loan" else 65
    max_tenure_years = min(30, max_age_at_maturity - customer_age)
    max_tenure_months = max_tenure_years * 12
    
    # Calculate max loan using EMI formula (reverse)
    # EMI = P × r × (1 + r)^n / ((1 + r)^n - 1)
    # P = EMI × ((1 + r)^n - 1) / (r × (1 + r)^n)
    
    monthly_rate = interest_rate / 100 / 12
    
    if monthly_rate > 0:
        factor = ((1 + monthly_rate) ** max_tenure_months - 1) / (monthly_rate * (1 + monthly_rate) ** max_tenure_months)
        max_loan = available_emi * factor
    else:
        max_loan = available_emi * max_tenure_months
    
    return {
        "monthly_income": monthly_income,
        "existing_emis": existing_emis,
        "customer_age": customer_age,
        "loan_type": loan_type,
        "interest_rate": f"{interest_rate}%",
        "max_tenure_years": max_tenure_years,
        "available_emi_capacity": round(available_emi, 2),
        "max_loan_amount": round(max_loan, 0),
        "recommended_loan_amount": round(max_loan * 0.8, 0),  # 80% of max
        "status": "PASS",
        "remarks": f"Eligible for loan up to ₹{max_loan:,.0f} with EMI of ₹{available_emi:,.0f}"
    }


def match_loan_products(
    customer_age: int,
    monthly_income: float,
    loan_amount: float,
    loan_purpose: str,
    employment_type: str = "Salaried"
) -> Dict[str, Any]:
    """
    Match customer profile with eligible loan products.
    
    Args:
        customer_age: Age of customer
        monthly_income: Monthly income
        loan_amount: Requested loan amount
        loan_purpose: Purpose of loan
        employment_type: Salaried/Self-Employed/Business
        
    Returns:
        Dictionary containing matched products
    """
    products = []
    
    # Home Loan
    if loan_purpose.lower() in ["home", "house", "property", "home loan"]:
        if customer_age >= 21 and customer_age <= 65 and monthly_income >= 25000:
            products.append({
                "product_name": "Home Loan",
                "eligibility": "ELIGIBLE",
                "max_amount": monthly_income * 60,
                "interest_rate_range": "8.5% - 10.5%",
                "max_tenure": min(30, 70 - customer_age),
                "match_score": 95
            })
    
    # Personal Loan
    if monthly_income >= 15000 and customer_age <= 60:
        products.append({
            "product_name": "Personal Loan",
            "eligibility": "ELIGIBLE",
            "max_amount": min(2500000, monthly_income * 20),
            "interest_rate_range": "10.5% - 18%",
            "max_tenure": min(7, 65 - customer_age),
            "match_score": 70
        })
    
    # Top-up Loan (if existing customer - simulated)
    if loan_amount <= monthly_income * 24:
        products.append({
            "product_name": "Top-up Loan",
            "eligibility": "MAY_BE_ELIGIBLE",
            "max_amount": monthly_income * 24,
            "interest_rate_range": "9% - 12%",
            "max_tenure": 10,
            "match_score": 60,
            "condition": "Subject to existing loan relationship"
        })
    
    # Sort by match score
    products.sort(key=lambda x: x["match_score"], reverse=True)
    
    return {
        "customer_profile": {
            "age": customer_age,
            "monthly_income": monthly_income,
            "requested_amount": loan_amount,
            "purpose": loan_purpose,
            "employment": employment_type
        },
        "matched_products": products,
        "best_match": products[0] if products else None,
        "total_options": len(products),
        "status": "PRODUCTS_FOUND" if products else "NO_MATCHING_PRODUCTS"
    }


def generate_qualification_report(
    customer_name: str,
    application_id: str,
    customer_age: int,
    monthly_income: float,
    loan_amount: float,
    loan_type: str,
    existing_emis: float = 0
) -> Dict[str, Any]:
    """
    Generate comprehensive qualification report.
    
    Args:
        customer_name: Name of customer
        application_id: Application ID
        customer_age: Age of customer
        monthly_income: Monthly income
        loan_amount: Requested loan amount
        loan_type: Type of loan
        existing_emis: Existing EMI obligations
        
    Returns:
        Dictionary containing qualification report
    """
    # Run all checks
    age_check = check_age_eligibility(customer_age, loan_type)
    income_check = validate_income_requirements(monthly_income, loan_type, loan_amount)
    foir_check = calculate_foir(monthly_income, existing_emis)
    credit_check = check_credit_history_status(customer_name)
    capacity_check = determine_borrowing_capacity(monthly_income, existing_emis, customer_age, loan_type)
    
    # Calculate overall status
    checks_passed = sum([
        age_check["status"] == "PASS",
        income_check["status"] == "PASS",
        foir_check["status"] == "PASS",
        credit_check["status"] == "PASS",
        capacity_check["status"] == "PASS"
    ])
    
    total_checks = 5
    
    if checks_passed == total_checks:
        overall_status = "QUALIFIED"
    elif checks_passed >= 3:
        overall_status = "CONDITIONALLY_QUALIFIED"
    else:
        overall_status = "NOT_QUALIFIED"
    
    return {
        "report_id": f"QUAL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "application_id": application_id,
        "customer_name": customer_name,
        "qualification_date": datetime.now().isoformat(),
        
        "eligibility_checks": {
            "age_eligibility": age_check,
            "income_validation": income_check,
            "foir_analysis": foir_check,
            "credit_history": credit_check,
            "borrowing_capacity": capacity_check
        },
        
        "summary": {
            "total_checks": total_checks,
            "checks_passed": checks_passed,
            "checks_failed": total_checks - checks_passed
        },
        
        "borrowing_details": {
            "requested_amount": loan_amount,
            "max_eligible_amount": capacity_check.get("max_loan_amount", 0),
            "recommended_amount": capacity_check.get("recommended_loan_amount", 0),
            "available_emi_capacity": capacity_check.get("available_emi_capacity", 0)
        },
        
        "qualification_status": overall_status,
        
        "recommendation": {
            "QUALIFIED": "Proceed to Credit Assessment and Asset Valuation (parallel processing)",
            "CONDITIONALLY_QUALIFIED": "Review flagged items before proceeding",
            "NOT_QUALIFIED": "Application does not meet minimum criteria"
        }[overall_status],
        
        "next_stage": "CREDIT_ASSESSMENT_AND_ASSET_VALUATION",
        "parallel_processing": True,
        "handoff_ready": overall_status in ["QUALIFIED", "CONDITIONALLY_QUALIFIED"]
    }


# ============================================================================
# TOOL DEFINITIONS FOR AZURE AI FOUNDRY
# ============================================================================


# ============================================================================
# DYNAMIC AGENT CREATION
# ============================================================================

def create_credit_qualification_agent():
    """Create Credit Qualification Agent"""
    
    try:
        project_client = AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=PROJECT_CONNECTION_STRING
        )
        
        agent = project_client.agents.create_agent(
            model=MODEL_DEPLOYMENT,
            name="credit-qualification-agent",
            instructions=AGENT_INSTRUCTIONS
        )
        
        thread = project_client.agents.create_thread()
        
        return {
            "project_client": project_client,
            "agent": agent,
            "thread": thread,
            "vector_store": None,
            "uploaded_files": []
        }
    
    except Exception as e:
        print(f"Error creating credit qualification agent: {e}")
        raise


if __name__ == "__main__":
    result = create_credit_qualification_agent()
    print(f"✅ Credit Qualification Agent Created: {result['agent'].id}")
    print(f"   Thread ID: {result['thread'].id}")

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_age_eligibility",
            "description": "Verify age requirements for loan products",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_age": {"type": "integer", "description": "Age of customer in years"},
                    "loan_type": {"type": "string", "description": "Type of loan (Home Loan, Personal Loan, etc.)"}
                },
                "required": ["customer_age"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "validate_income_requirements",
            "description": "Check if income meets product thresholds",
            "parameters": {
                "type": "object",
                "properties": {
                    "monthly_income": {"type": "number", "description": "Monthly income in INR"},
                    "loan_type": {"type": "string", "description": "Type of loan"},
                    "loan_amount": {"type": "number", "description": "Requested loan amount"}
                },
                "required": ["monthly_income"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_foir",
            "description": "Calculate Fixed Obligation to Income Ratio",
            "parameters": {
                "type": "object",
                "properties": {
                    "monthly_income": {"type": "number", "description": "Monthly income in INR"},
                    "existing_emis": {"type": "number", "description": "Existing EMI obligations"},
                    "proposed_emi": {"type": "number", "description": "Proposed EMI for new loan"},
                    "other_obligations": {"type": "number", "description": "Other fixed obligations"}
                },
                "required": ["monthly_income", "existing_emis"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_credit_history_status",
            "description": "Verify credit report availability and basic status",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "Name of the customer"}
                },
                "required": ["customer_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "determine_borrowing_capacity",
            "description": "Calculate maximum borrowing amount",
            "parameters": {
                "type": "object",
                "properties": {
                    "monthly_income": {"type": "number", "description": "Monthly income"},
                    "existing_emis": {"type": "number", "description": "Existing EMIs"},
                    "customer_age": {"type": "integer", "description": "Customer age"},
                    "loan_type": {"type": "string", "description": "Type of loan"},
                    "interest_rate": {"type": "number", "description": "Expected interest rate"}
                },
                "required": ["monthly_income", "existing_emis", "customer_age"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "match_loan_products",
            "description": "Match customer profile with eligible loan products",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_age": {"type": "integer", "description": "Age of customer"},
                    "monthly_income": {"type": "number", "description": "Monthly income"},
                    "loan_amount": {"type": "number", "description": "Requested amount"},
                    "loan_purpose": {"type": "string", "description": "Purpose of loan"},
                    "employment_type": {"type": "string", "description": "Employment type"}
                },
                "required": ["customer_age", "monthly_income", "loan_amount", "loan_purpose"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_qualification_report",
            "description": "Generate comprehensive qualification report",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "Customer name"},
                    "application_id": {"type": "string", "description": "Application ID"},
                    "customer_age": {"type": "integer", "description": "Customer age"},
                    "monthly_income": {"type": "number", "description": "Monthly income"},
                    "loan_amount": {"type": "number", "description": "Loan amount"},
                    "loan_type": {"type": "string", "description": "Type of loan"},
                    "existing_emis": {"type": "number", "description": "Existing EMIs"}
                },
                "required": ["customer_name", "application_id", "customer_age", "monthly_income", "loan_amount", "loan_type"]
            }
        }
    }
]


# ============================================================================
# AGENT CLASS
# ============================================================================

class CreditQualificationAgent:
    """Credit Qualification Agent for loan processing"""
    
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
            "check_age_eligibility": check_age_eligibility,
            "validate_income_requirements": validate_income_requirements,
            "calculate_foir": calculate_foir,
            "check_credit_history_status": check_credit_history_status,
            "determine_borrowing_capacity": determine_borrowing_capacity,
            "match_loan_products": match_loan_products,
            "generate_qualification_report": generate_qualification_report
        }
        
        if tool_name in tool_functions:
            result = tool_functions[tool_name](**arguments)
            return json.dumps(result, indent=2)
        
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
    
    def process_request(self, user_message: str) -> str:
        """Process a credit qualification request"""
        # Create agent dynamically
        agent = self.project_client.agents.create_agent(
            model=MODEL_DEPLOYMENT,
            name="credit-qualification-agent",
            instructions=self.instructions
        )
        thread = self.project_client.agents.create_thread()
        
        self.project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=user_message
        )
        
        run = self.project_client.agents.create_and_process_run(
            thread_id=thread.id,
            agent_id=agent.id
        )
        
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
            "name": "Credit Qualification Agent",
            "description": "Reviews initial credit requirements and eligibility",
            "stage": 3,
            "previous_agent": "Document Verification Agent",
            "next_agents": ["Credit Assessment Agent", "Asset Valuation Agent"],
            "parallel_handoff": True,
            "tools": [tool["function"]["name"] for tool in self.tools]
        }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  CREDIT QUALIFICATION AGENT")
    print("=" * 70)
    
    agent = CreditQualificationAgent()
    print(f"\nAgent Info: {json.dumps(agent.get_agent_info(), indent=2)}")
    
    # Test with sample request
    test_message = """
    Please qualify the following loan application:
    
    Customer: Kala Divan
    Application ID: LOAN-20260127120000
    Age: 35 years
    Monthly Income: ₹75,000
    Loan Amount Requested: ₹40,00,000
    Loan Type: Home Loan
    Existing EMIs: ₹10,000
    
    Perform all eligibility checks and generate qualification report.
    """
    
    print(f"\n{'='*70}")
    print("Processing Request...")
    print(f"{'='*70}")
    
    response = agent.process_request(test_message)
    print(f"\nAgent Response:\n{response}")