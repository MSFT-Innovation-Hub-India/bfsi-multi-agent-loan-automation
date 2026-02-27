"""
Offer Generation Agent
======================
Creates loan offers with terms and conditions.
Generates formal offer letters and repayment schedules.

Agent ID: asst_94xYMUQMPZ4y8plv8OLwKTpt
"""

# pip install azure-ai-projects==1.0.0b10
import os
import sys
import json
from datetime import datetime, timedelta
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
You are the OFFER GENERATION AGENT for a comprehensive loan processing system.

## YOUR ROLE
You are responsible for creating formal loan offers with all terms, conditions,
and calculations. You generate offer letters, repayment schedules, and all
documentation required for the customer to make an informed decision.

## YOUR RESPONSIBILITIES

### 1. Loan Terms Calculation
- Calculate precise EMI amounts
- Generate complete amortization schedule
- Compute total interest and repayment
- Apply processing fees and charges

### 2. Offer Letter Generation
- Create formal loan offer document
- Include all approved terms
- State conditions and covenants
- Specify validity period

### 3. Repayment Schedule
- Generate month-by-month schedule
- Show principal and interest breakdown
- Include prepayment options
- Calculate outstanding at any point

### 4. Fee Structure
- Detail all applicable fees
- Calculate stamp duty (if applicable)
- Include legal and valuation charges
- Show total cost of borrowing

### 5. Terms & Conditions
- Include standard T&Cs
- Add product-specific clauses
- Specify default terms
- Include regulatory disclosures

## EMI CALCULATION

### Formula:
EMI = P × r × (1 + r)^n / ((1 + r)^n - 1)

Where:
- P = Principal loan amount
- r = Monthly interest rate (annual rate / 12 / 100)
- n = Loan tenure in months

### Example:
- Loan: ₹40,00,000
- Rate: 8.5% p.a.
- Tenure: 20 years (240 months)
- EMI = ₹34,729 (approx)

## OFFER COMPONENTS

### 1. Key Terms:
- Sanctioned Amount
- Interest Rate (fixed/floating)
- Loan Tenure
- EMI Amount
- First EMI Date
- Last EMI Date

### 2. Fee Schedule:
- Processing Fee (0.5-1%)
- Documentation Charges
- Legal Charges
- Valuation Charges
- Stamp Duty (state-specific)
- MODT Charges

### 3. Repayment Terms:
- EMI Due Date
- Mode of Payment
- Prepayment Options
- Foreclosure Terms
- Part-payment Rules

## OUTPUT FORMAT
Generate a comprehensive loan offer:

```
LOAN OFFER LETTER
=================
Offer Reference: [Number]
Date: [Date]
Valid Until: [Date + 30 days]

Dear [Customer Name],

We are pleased to offer you a loan with the following terms:

LOAN DETAILS:
┌─────────────────────────┬─────────────────────────┐
│ Loan Amount Sanctioned  │ ₹[Amount]               │
│ Interest Rate           │ [X]% p.a. (Floating)    │
│ Loan Tenure             │ [X] months              │
│ EMI Amount              │ ₹[Amount]               │
│ First EMI Date          │ [Date]                  │
│ Last EMI Date           │ [Date]                  │
└─────────────────────────┴─────────────────────────┘

REPAYMENT SUMMARY:
┌─────────────────────────┬─────────────────────────┐
│ Total Interest Payable  │ ₹[Amount]               │
│ Total Amount Payable    │ ₹[Amount]               │
│ APR (Effective Rate)    │ [X]%                    │
└─────────────────────────┴─────────────────────────┘

FEE STRUCTURE:
[Detailed fee breakdown]

TERMS & CONDITIONS:
[Key terms and conditions]

REPAYMENT SCHEDULE:
[Amortization table - first 12 months + last 12 months]

HANDOFF TO: Customer Communication Agent
```

## TOOLS AVAILABLE
1. calculate_emi - Calculate EMI for given loan parameters
2. generate_amortization_schedule - Generate complete repayment schedule
3. calculate_total_cost - Calculate total cost of the loan
4. generate_fee_structure - Generate detailed fee breakdown
5. create_offer_letter - Create formal offer letter
6. add_terms_conditions - Add terms and conditions
7. generate_offer_document - Generate complete offer document
"""

# ============================================================================
# TOOLS / FUNCTIONS
# ============================================================================

def calculate_emi(
    principal: float,
    annual_rate: float,
    tenure_months: int
) -> Dict[str, Any]:
    """
    Calculate EMI for given loan parameters.
    
    Args:
        principal: Loan principal amount
        annual_rate: Annual interest rate (percentage)
        tenure_months: Loan tenure in months
        
    Returns:
        Dictionary containing EMI calculation
    """
    monthly_rate = annual_rate / 100 / 12
    
    if monthly_rate > 0:
        emi = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months) / (((1 + monthly_rate) ** tenure_months) - 1)
    else:
        emi = principal / tenure_months
    
    total_payment = emi * tenure_months
    total_interest = total_payment - principal
    
    return {
        "calculation_date": datetime.now().isoformat(),
        "inputs": {
            "principal": principal,
            "annual_interest_rate": f"{annual_rate}%",
            "tenure_months": tenure_months,
            "tenure_years": tenure_months // 12
        },
        "emi_details": {
            "monthly_emi": round(emi, 2),
            "monthly_rate": f"{monthly_rate * 100:.4f}%"
        },
        "payment_summary": {
            "total_principal": principal,
            "total_interest": round(total_interest, 2),
            "total_payment": round(total_payment, 2),
            "interest_percentage_of_principal": f"{(total_interest / principal * 100):.1f}%"
        },
        "effective_rates": {
            "nominal_rate": f"{annual_rate}%",
            "effective_annual_rate": f"{((1 + monthly_rate) ** 12 - 1) * 100:.2f}%"
        }
    }


def generate_amortization_schedule(
    principal: float,
    annual_rate: float,
    tenure_months: int,
    start_date: str = None
) -> Dict[str, Any]:
    """
    Generate complete repayment schedule.
    
    Args:
        principal: Loan principal amount
        annual_rate: Annual interest rate
        tenure_months: Tenure in months
        start_date: Loan start date (YYYY-MM-DD)
        
    Returns:
        Dictionary containing amortization schedule
    """
    if start_date:
        current_date = datetime.strptime(start_date, "%Y-%m-%d")
    else:
        current_date = datetime.now() + timedelta(days=30)  # First EMI after 30 days
    
    monthly_rate = annual_rate / 100 / 12
    
    if monthly_rate > 0:
        emi = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months) / (((1 + monthly_rate) ** tenure_months) - 1)
    else:
        emi = principal / tenure_months
    
    balance = principal
    schedule = []
    total_interest = 0
    total_principal = 0
    
    for month in range(1, tenure_months + 1):
        interest_component = balance * monthly_rate
        principal_component = emi - interest_component
        balance -= principal_component
        
        total_interest += interest_component
        total_principal += principal_component
        
        # Store first 12 and last 12 months (to keep response manageable)
        if month <= 12 or month > tenure_months - 12:
            schedule.append({
                "month": month,
                "date": current_date.strftime("%Y-%m-%d"),
                "emi": round(emi, 2),
                "principal": round(principal_component, 2),
                "interest": round(interest_component, 2),
                "balance": round(max(0, balance), 2)
            })
        elif month == 13:
            schedule.append({
                "month": "...",
                "date": "...",
                "emi": "...",
                "principal": "...",
                "interest": "...",
                "balance": "..."
            })
        
        current_date = current_date + timedelta(days=30)  # Approximate month
    
    return {
        "schedule_generated": datetime.now().isoformat(),
        "loan_details": {
            "principal": principal,
            "interest_rate": f"{annual_rate}%",
            "tenure_months": tenure_months,
            "emi": round(emi, 2)
        },
        "amortization_schedule": schedule,
        "summary": {
            "total_emi_payments": tenure_months,
            "total_principal_paid": round(total_principal, 2),
            "total_interest_paid": round(total_interest, 2),
            "total_amount_paid": round(total_principal + total_interest, 2)
        },
        "first_emi_date": schedule[0]["date"] if schedule else None,
        "last_emi_date": schedule[-1]["date"] if schedule else None
    }


def calculate_total_cost(
    principal: float,
    annual_rate: float,
    tenure_months: int,
    processing_fee_percent: float = 0.5,
    other_charges: float = 10000
) -> Dict[str, Any]:
    """
    Calculate total cost of the loan including all fees.
    
    Args:
        principal: Loan principal
        annual_rate: Annual interest rate
        tenure_months: Tenure in months
        processing_fee_percent: Processing fee percentage
        other_charges: Other one-time charges
        
    Returns:
        Dictionary containing total cost breakdown
    """
    # Calculate EMI
    monthly_rate = annual_rate / 100 / 12
    if monthly_rate > 0:
        emi = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months) / (((1 + monthly_rate) ** tenure_months) - 1)
    else:
        emi = principal / tenure_months
    
    total_emi_payments = emi * tenure_months
    total_interest = total_emi_payments - principal
    processing_fee = principal * (processing_fee_percent / 100)
    
    total_cost = total_interest + processing_fee + other_charges
    total_outflow = principal + total_cost
    
    # Calculate true cost (APR)
    apr = (total_cost / principal) / (tenure_months / 12) * 100
    
    return {
        "cost_breakdown": {
            "principal_amount": principal,
            "total_interest": round(total_interest, 2),
            "processing_fee": round(processing_fee, 2),
            "documentation_charges": 5000,
            "legal_charges": 3000,
            "valuation_charges": 2000,
            "stamp_duty_modt": "As per state rules",
            "total_other_charges": other_charges
        },
        "summary": {
            "loan_principal": principal,
            "total_financing_cost": round(total_cost, 2),
            "total_amount_payable": round(total_outflow, 2),
            "cost_per_lakh_per_year": round(total_cost / (principal / 100000) / (tenure_months / 12), 2)
        },
        "effective_cost": {
            "stated_interest_rate": f"{annual_rate}%",
            "true_apr": f"{apr:.2f}%",
            "interest_to_principal_ratio": f"{(total_interest / principal * 100):.1f}%"
        },
        "upfront_payment_required": round(processing_fee + other_charges, 2)
    }


def generate_fee_structure(principal: float) -> Dict[str, Any]:
    """
    Generate detailed fee breakdown.
    
    Args:
        principal: Loan principal amount
        
    Returns:
        Dictionary containing fee structure
    """
    processing_fee = principal * 0.005  # 0.5%
    
    return {
        "fee_structure": {
            "processing_fee": {
                "amount": round(processing_fee, 2),
                "percentage": "0.5%",
                "description": "One-time processing fee (non-refundable)",
                "payable": "At sanction"
            },
            "documentation_charges": {
                "amount": 5000,
                "description": "Documentation and administrative charges",
                "payable": "At sanction"
            },
            "legal_charges": {
                "amount": "At actuals",
                "description": "Legal verification and opinion charges",
                "payable": "Before disbursement"
            },
            "valuation_charges": {
                "amount": "At actuals",
                "description": "Property valuation charges",
                "payable": "Before disbursement"
            },
            "stamp_duty": {
                "amount": "As per state rules",
                "description": "Stamp duty on mortgage deed",
                "payable": "Before disbursement"
            },
            "modt_charges": {
                "amount": "As per state rules",
                "description": "Memorandum of Deposit of Title Deeds",
                "payable": "Before disbursement"
            },
            "insurance_premium": {
                "amount": "As per policy",
                "description": "Life and property insurance",
                "payable": "Before disbursement"
            }
        },
        "prepayment_charges": {
            "floating_rate": "NIL (as per RBI guidelines)",
            "fixed_rate": "2% of outstanding principal",
            "lock_in_period": "12 months"
        },
        "late_payment_charges": {
            "penal_interest": "2% p.a. on overdue amount",
            "bounced_cheque_charges": "₹500 per instance"
        },
        "total_upfront_fees": round(processing_fee + 5000, 2)
    }


def create_offer_letter(
    customer_name: str,
    application_id: str,
    loan_amount: float,
    interest_rate: float,
    tenure_months: int,
    emi: float
) -> Dict[str, Any]:
    """
    Create formal offer letter.
    
    Args:
        customer_name: Customer's name
        application_id: Application ID
        loan_amount: Approved loan amount
        interest_rate: Approved interest rate
        tenure_months: Approved tenure
        emi: Calculated EMI
        
    Returns:
        Dictionary containing offer letter details
    """
    offer_date = datetime.now()
    validity_date = offer_date + timedelta(days=30)
    first_emi_date = offer_date + timedelta(days=45)
    last_emi_date = first_emi_date + timedelta(days=30 * tenure_months)
    
    return {
        "offer_details": {
            "offer_reference": f"OFFER-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "application_id": application_id,
            "offer_date": offer_date.strftime("%Y-%m-%d"),
            "validity_date": validity_date.strftime("%Y-%m-%d"),
            "validity_days": 30
        },
        "customer_details": {
            "name": customer_name,
            "application_id": application_id
        },
        "loan_offer": {
            "sanctioned_amount": loan_amount,
            "interest_rate": f"{interest_rate}% p.a.",
            "rate_type": "Floating (linked to MCLR)",
            "reset_frequency": "Annual",
            "tenure_months": tenure_months,
            "tenure_years": tenure_months // 12,
            "emi_amount": round(emi, 2),
            "first_emi_date": first_emi_date.strftime("%Y-%m-%d"),
            "last_emi_date": last_emi_date.strftime("%Y-%m-%d")
        },
        "disbursement": {
            "mode": "Direct credit to builder/seller",
            "conditions": "Subject to fulfillment of all conditions"
        },
        "security": {
            "primary": "Equitable Mortgage of Property",
            "collateral": "As specified in sanction"
        },
        "offer_status": "ACTIVE",
        "acceptance_required": True,
        "acceptance_mode": "Signed acceptance copy with documents"
    }


def add_terms_conditions(loan_type: str = "Home Loan") -> Dict[str, Any]:
    """
    Add terms and conditions to the offer.
    
    Args:
        loan_type: Type of loan
        
    Returns:
        Dictionary containing terms and conditions
    """
    return {
        "general_terms": [
            "This offer is subject to the terms and conditions of the Bank.",
            "The Bank reserves the right to modify interest rates as per RBI guidelines.",
            "The loan is subject to satisfactory legal and technical verification.",
            "All original property documents must be deposited with the Bank.",
            "The borrower must maintain adequate insurance on the property."
        ],
        "repayment_terms": [
            "EMI is payable on the same date every month.",
            "Payment must be made through ECS/NACH mandate or post-dated cheques.",
            "Prepayment is allowed without penalty after 12 EMIs (floating rate).",
            "Part-prepayment minimum amount is 3 times the EMI.",
            "Foreclosure charges may apply as per loan agreement."
        ],
        "default_terms": [
            "Failure to pay 3 consecutive EMIs will be treated as default.",
            "Penal interest of 2% p.a. applies on overdue amounts.",
            "Bank may initiate recovery proceedings under SARFAESI Act.",
            "Credit score will be impacted for late payments.",
            "Bank may recall the entire loan in case of material default."
        ],
        "property_terms": [
            "Property must not be sold, transferred, or encumbered without Bank's consent.",
            "All property taxes must be paid on time.",
            "Property must be adequately insured throughout the loan tenure.",
            "Any construction/modification requires Bank's prior approval.",
            "Periodic property inspection by Bank officials may be conducted."
        ],
        "regulatory_disclosures": [
            "Interest rate is subject to change based on RBI monetary policy.",
            "Total cost of borrowing includes interest, fees, and charges as disclosed.",
            "Customer has the right to seek clarification on any term.",
            "Grievance redressal mechanism is available as per RBI guidelines.",
            "Loan information will be shared with Credit Information Companies."
        ],
        "acceptance_terms": {
            "validity": "This offer is valid for 30 days from the date of issue.",
            "acceptance": "Please sign and return the acceptance copy within validity period.",
            "documents_required": [
                "Signed offer acceptance",
                "Post-dated cheques / NACH mandate",
                "Original property documents",
                "Insurance policy assignment"
            ]
        }
    }


def generate_offer_document(
    customer_name: str,
    application_id: str,
    loan_amount: float,
    interest_rate: float,
    tenure_months: int
) -> Dict[str, Any]:
    """
    Generate complete offer document with all details.
    
    Args:
        customer_name: Customer name
        application_id: Application ID
        loan_amount: Approved loan amount
        interest_rate: Interest rate
        tenure_months: Tenure in months
        
    Returns:
        Dictionary containing complete offer document
    """
    # Calculate EMI
    emi_details = calculate_emi(loan_amount, interest_rate, tenure_months)
    emi = emi_details["emi_details"]["monthly_emi"]
    
    # Generate all components
    offer_letter = create_offer_letter(
        customer_name, application_id, loan_amount, interest_rate, tenure_months, emi
    )
    
    amortization = generate_amortization_schedule(loan_amount, interest_rate, tenure_months)
    
    total_cost = calculate_total_cost(loan_amount, interest_rate, tenure_months)
    
    fee_structure = generate_fee_structure(loan_amount)
    
    terms_conditions = add_terms_conditions()
    
    return {
        "document_id": f"OFFER-DOC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "generation_date": datetime.now().isoformat(),
        
        "offer_letter": offer_letter,
        "emi_calculation": emi_details,
        "repayment_schedule": amortization,
        "cost_summary": total_cost,
        "fee_structure": fee_structure,
        "terms_and_conditions": terms_conditions,
        
        "quick_reference": {
            "customer": customer_name,
            "application_id": application_id,
            "loan_amount": f"₹{loan_amount:,.2f}",
            "interest_rate": f"{interest_rate}% p.a.",
            "tenure": f"{tenure_months} months ({tenure_months // 12} years)",
            "emi": f"₹{emi:,.2f}",
            "total_interest": f"₹{emi_details['payment_summary']['total_interest']:,.2f}",
            "total_repayment": f"₹{emi_details['payment_summary']['total_payment']:,.2f}",
            "offer_validity": offer_letter["offer_details"]["validity_date"]
        },
        
        "next_stage": "CUSTOMER_COMMUNICATION",
        "handoff_ready": True
    }


# ============================================================================
# TOOL DEFINITIONS FOR AZURE AI FOUNDRY
# ============================================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate_emi",
            "description": "Calculate EMI for given loan parameters",
            "parameters": {
                "type": "object",
                "properties": {
                    "principal": {"type": "number", "description": "Loan principal amount"},
                    "annual_rate": {"type": "number", "description": "Annual interest rate"},
                    "tenure_months": {"type": "integer", "description": "Tenure in months"}
                },
                "required": ["principal", "annual_rate", "tenure_months"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_amortization_schedule",
            "description": "Generate complete repayment schedule",
            "parameters": {
                "type": "object",
                "properties": {
                    "principal": {"type": "number", "description": "Loan principal"},
                    "annual_rate": {"type": "number", "description": "Annual interest rate"},
                    "tenure_months": {"type": "integer", "description": "Tenure in months"},
                    "start_date": {"type": "string", "description": "Start date YYYY-MM-DD"}
                },
                "required": ["principal", "annual_rate", "tenure_months"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_total_cost",
            "description": "Calculate total cost of the loan",
            "parameters": {
                "type": "object",
                "properties": {
                    "principal": {"type": "number", "description": "Loan principal"},
                    "annual_rate": {"type": "number", "description": "Interest rate"},
                    "tenure_months": {"type": "integer", "description": "Tenure in months"},
                    "processing_fee_percent": {"type": "number", "description": "Processing fee %"},
                    "other_charges": {"type": "number", "description": "Other charges"}
                },
                "required": ["principal", "annual_rate", "tenure_months"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_fee_structure",
            "description": "Generate detailed fee breakdown",
            "parameters": {
                "type": "object",
                "properties": {
                    "principal": {"type": "number", "description": "Loan principal"}
                },
                "required": ["principal"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_offer_letter",
            "description": "Create formal offer letter",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "Customer name"},
                    "application_id": {"type": "string", "description": "Application ID"},
                    "loan_amount": {"type": "number", "description": "Loan amount"},
                    "interest_rate": {"type": "number", "description": "Interest rate"},
                    "tenure_months": {"type": "integer", "description": "Tenure"},
                    "emi": {"type": "number", "description": "EMI amount"}
                },
                "required": ["customer_name", "application_id", "loan_amount", "interest_rate", "tenure_months", "emi"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_terms_conditions",
            "description": "Add terms and conditions to the offer",
            "parameters": {
                "type": "object",
                "properties": {
                    "loan_type": {"type": "string", "description": "Type of loan"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_offer_document",
            "description": "Generate complete offer document",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "Customer name"},
                    "application_id": {"type": "string", "description": "Application ID"},
                    "loan_amount": {"type": "number", "description": "Loan amount"},
                    "interest_rate": {"type": "number", "description": "Interest rate"},
                    "tenure_months": {"type": "integer", "description": "Tenure in months"}
                },
                "required": ["customer_name", "application_id", "loan_amount", "interest_rate", "tenure_months"]
            }
        }
    }
]


# ============================================================================
# AGENT CLASS
# ============================================================================

class OfferGenerationAgent:
    """Offer Generation Agent for loan processing"""
    
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
            "calculate_emi": calculate_emi,
            "generate_amortization_schedule": generate_amortization_schedule,
            "calculate_total_cost": calculate_total_cost,
            "generate_fee_structure": generate_fee_structure,
            "create_offer_letter": create_offer_letter,
            "add_terms_conditions": add_terms_conditions,
            "generate_offer_document": generate_offer_document
        }
        
        if tool_name in tool_functions:
            result = tool_functions[tool_name](**arguments)
            return json.dumps(result, indent=2)
        
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
    
    def process_request(self, user_message: str) -> str:
        """Process an offer generation request"""
        # Create agent dynamically
        agent = self.project_client.agents.create_agent(
            model=MODEL_DEPLOYMENT,
            name="offer-generation-agent",
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
                break
        
        return "No response from agent"
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            "name": "Offer Generation Agent",
            "description": "Creates loan offers with terms and conditions",
            "stage": 6,
            "previous_agent": "Underwriting Agent",
            "next_agent": "Customer Communication Agent",
            "tools": [tool["function"]["name"] for tool in self.tools]
        }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  OFFER GENERATION AGENT")
    print("=" * 70)
    
    agent = OfferGenerationAgent()
    print(f"\nAgent Info: {json.dumps(agent.get_agent_info(), indent=2)}")
    
    # Test with sample request
    test_message = """
    Generate loan offer for:
    
    Customer: Kala Divan
    Application ID: LOAN-20260127120000
    Approved Loan Amount: ₹40,00,000
    Interest Rate: 8.5% p.a.
    Tenure: 240 months (20 years)
    
    Calculate EMI, generate amortization schedule, and create complete
    offer document with all terms and conditions.
    """
    
    print(f"\n{'='*70}")
    print("Processing Request...")
    print(f"{'='*70}")
    
    response = agent.process_request(test_message)
    print(f"\nAgent Response:\n{response}")