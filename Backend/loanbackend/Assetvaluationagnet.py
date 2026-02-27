"""
Asset Valuation Agent
======================
Evaluates collateral and asset worth for loan security.
Works in PARALLEL with Credit Assessment Agent.

Agent ID: asst_0rfLXApRmIav9jA1fcj3SbMD
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
You are the ASSET VALUATION AGENT for a comprehensive loan processing system.

## YOUR ROLE
You are responsible for evaluating collateral and asset worth for loan security.
You work in PARALLEL with the Credit Assessment Agent. Your valuation determines
the maximum loan amount based on collateral value and Loan-to-Value (LTV) ratio.

## YOUR RESPONSIBILITIES

### 1. Property Document Verification
- Verify property ownership documents
- Check title deed authenticity
- Verify encumbrance certificate
- Confirm property tax payments
- Check for any legal disputes

### 2. Property Valuation
- Assess current market value
- Evaluate property location and accessibility
- Analyze construction quality and age
- Compare with market transactions
- Consider future appreciation potential

### 3. LTV Ratio Calculation
- Calculate Loan-to-Value ratio
- Apply product-specific LTV limits
- Determine maximum loan based on value
- Factor in property type adjustments

### 4. Collateral Risk Assessment
- Evaluate marketability of property
- Assess liquidation timeframe
- Check for encumbrances or liens
- Review insurance requirements
- Identify property risks

### 5. Other Asset Evaluation
- Fixed deposits and investments
- Insurance policies with surrender value
- Other real estate holdings
- Vehicle and equipment values

## LTV GUIDELINES BY PROPERTY TYPE

| Property Type | Max LTV | Remarks |
|---------------|---------|---------|
| Residential - Ready | 80% | Standard |
| Residential - Under Construction | 75% | Builder approved |
| Commercial | 70% | Higher risk |
| Plot/Land | 60% | Non-constructed |
| Mixed Use | 65% | Case by case |

## VALUATION METHODOLOGY

### 1. Market Comparison Approach
- Compare similar properties sold recently
- Adjust for location, size, amenities
- Consider time value adjustments

### 2. Income Approach (for rental properties)
- Estimate rental income potential
- Apply capitalization rate
- Calculate net operating income

### 3. Cost Approach
- Estimate land value
- Calculate construction cost
- Deduct depreciation

## OUTPUT FORMAT
Provide a detailed valuation report:

```
ASSET VALUATION REPORT
======================
Application ID: [ID]
Customer Name: [Name]
Valuation Date: [Date]

PROPERTY DETAILS:
┌─────────────────────┬─────────────────────────┐
│ Property Type       │ [Type]                  │
│ Location            │ [Address]               │
│ Built-up Area       │ [X] sq.ft               │
│ Property Age        │ [X] years               │
│ Ownership Type      │ [Freehold/Leasehold]    │
└─────────────────────┴─────────────────────────┘

DOCUMENT VERIFICATION:
✓ Title Deed: VERIFIED
✓ Encumbrance Certificate: CLEAR
✓ Property Tax: PAID
✓ Approved Plan: VERIFIED
✓ Occupancy Certificate: VERIFIED

VALUATION:
┌─────────────────────────┬─────────────────────┐
│ Market Value            │ ₹[Amount]           │
│ Forced Sale Value       │ ₹[Amount]           │
│ Valuation Method        │ [Method]            │
│ Confidence Level        │ [High/Medium/Low]   │
└─────────────────────────┴─────────────────────┘

LTV CALCULATION:
- Property Value: ₹[Amount]
- Max LTV Allowed: [X]%
- Maximum Loan Amount: ₹[Amount]
- Requested Loan Amount: ₹[Amount]
- LTV for Requested Amount: [X]%
- LTV Status: WITHIN LIMITS / EXCEEDS LIMIT

COLLATERAL ASSESSMENT:
- Marketability: HIGH / MEDIUM / LOW
- Liquidation Timeframe: [X] months
- Risk Category: LOW / MEDIUM / HIGH

RECOMMENDATION: ADEQUATE / INADEQUATE / CONDITIONAL

HANDOFF TO: Underwriting Agent
```

## TOOLS AVAILABLE
1. verify_property_documents - Verify property ownership and legal documents
2. calculate_property_value - Calculate market value of property
3. calculate_ltv_ratio - Calculate Loan-to-Value ratio
4. assess_collateral_risk - Assess risk associated with collateral
5. evaluate_other_assets - Evaluate additional assets and securities
6. check_encumbrance - Check for existing liens or encumbrances
7. generate_valuation_report - Generate comprehensive valuation report
"""

# ============================================================================
# TOOLS / FUNCTIONS
# ============================================================================

def verify_property_documents(customer_name: str) -> Dict[str, Any]:
    """
    Verify property ownership and legal documents.
    
    Args:
        customer_name: Name of the customer
        
    Returns:
        Dictionary containing document verification results
    """
    docs_path = os.path.join(os.path.dirname(__file__), "Documents")
    documents = os.listdir(docs_path) if os.path.exists(docs_path) else []
    
    property_doc_found = any('property' in doc.lower() for doc in documents)
    
    return {
        "customer_name": customer_name,
        "verification_date": datetime.now().isoformat(),
        
        "document_checklist": {
            "title_deed": {
                "status": "VERIFIED" if property_doc_found else "NOT_FOUND",
                "remarks": "Clear title in customer name" if property_doc_found else "Document not submitted"
            },
            "encumbrance_certificate": {
                "status": "VERIFIED" if property_doc_found else "PENDING",
                "period_covered": "Last 13 years",
                "encumbrances_found": "NONE",
                "remarks": "Property is free from encumbrances"
            },
            "property_tax_receipts": {
                "status": "VERIFIED" if property_doc_found else "PENDING",
                "paid_till": "2025-26",
                "outstanding": 0,
                "remarks": "All taxes paid up to date"
            },
            "approved_building_plan": {
                "status": "VERIFIED" if property_doc_found else "PENDING",
                "sanctioning_authority": "Municipal Corporation",
                "remarks": "Plan approved and construction as per plan"
            },
            "occupancy_certificate": {
                "status": "VERIFIED" if property_doc_found else "PENDING",
                "issue_date": "2020-06-15",
                "remarks": "Valid OC obtained"
            },
            "sale_deed": {
                "status": "VERIFIED" if property_doc_found else "NOT_FOUND",
                "registration_date": "2020-05-10",
                "registration_number": "DOC/2020/12345"
            }
        },
        
        "legal_opinion": {
            "title_clear": True if property_doc_found else False,
            "marketable": True if property_doc_found else False,
            "legal_heir_issues": "NONE",
            "pending_litigation": "NONE"
        },
        
        "overall_status": "VERIFIED" if property_doc_found else "INCOMPLETE",
        "documents_found_in_folder": [doc for doc in documents if 'property' in doc.lower()]
    }


def calculate_property_value(
    property_type: str = "Residential",
    location: str = "Metro City",
    built_up_area_sqft: int = 1500,
    property_age_years: int = 5,
    construction_quality: str = "Good"
) -> Dict[str, Any]:
    """
    Calculate market value of property.
    
    Args:
        property_type: Type of property
        location: Location/city of property
        built_up_area_sqft: Built-up area in square feet
        property_age_years: Age of property in years
        construction_quality: Quality of construction
        
    Returns:
        Dictionary containing property valuation
    """
    # Base rates per sqft by location
    location_rates = {
        "Metro City": 8000,
        "Tier 1 City": 6000,
        "Tier 2 City": 4000,
        "Tier 3 City": 2500
    }
    
    # Property type adjustments
    type_multipliers = {
        "Residential": 1.0,
        "Commercial": 1.2,
        "Industrial": 0.8,
        "Plot": 0.7,
        "Mixed Use": 1.1
    }
    
    # Quality adjustments
    quality_multipliers = {
        "Excellent": 1.2,
        "Good": 1.0,
        "Average": 0.85,
        "Below Average": 0.7
    }
    
    # Calculate base value
    base_rate = location_rates.get(location, 5000)
    type_mult = type_multipliers.get(property_type, 1.0)
    quality_mult = quality_multipliers.get(construction_quality, 1.0)
    
    # Age depreciation (1% per year, max 15%)
    depreciation = min(0.15, property_age_years * 0.01)
    
    # Calculate values
    base_value = built_up_area_sqft * base_rate * type_mult * quality_mult
    depreciated_value = base_value * (1 - depreciation)
    market_value = round(depreciated_value, -3)  # Round to nearest 1000
    forced_sale_value = round(market_value * 0.75, -3)  # 75% of market value
    
    return {
        "valuation_date": datetime.now().isoformat(),
        
        "property_details": {
            "type": property_type,
            "location": location,
            "built_up_area_sqft": built_up_area_sqft,
            "property_age_years": property_age_years,
            "construction_quality": construction_quality
        },
        
        "valuation_inputs": {
            "base_rate_per_sqft": base_rate,
            "type_multiplier": type_mult,
            "quality_multiplier": quality_mult,
            "depreciation_applied": f"{depreciation*100:.1f}%"
        },
        
        "valuation_results": {
            "calculated_base_value": round(base_value, 0),
            "market_value": market_value,
            "forced_sale_value": forced_sale_value,
            "per_sqft_value": round(market_value / built_up_area_sqft, 0)
        },
        
        "valuation_method": "Market Comparison with Adjustments",
        "confidence_level": "HIGH" if quality_mult >= 1.0 else "MEDIUM",
        "valuation_valid_for_days": 90
    }


def calculate_ltv_ratio(
    property_value: float,
    loan_amount: float,
    property_type: str = "Residential"
) -> Dict[str, Any]:
    """
    Calculate Loan-to-Value ratio.
    
    Args:
        property_value: Market value of property
        loan_amount: Requested loan amount
        property_type: Type of property
        
    Returns:
        Dictionary containing LTV calculation
    """
    # Max LTV by property type
    max_ltv_limits = {
        "Residential": 80,
        "Residential - Under Construction": 75,
        "Commercial": 70,
        "Plot": 60,
        "Industrial": 65,
        "Mixed Use": 65
    }
    
    max_ltv = max_ltv_limits.get(property_type, 75)
    actual_ltv = (loan_amount / property_value) * 100 if property_value > 0 else 0
    max_loan_amount = property_value * (max_ltv / 100)
    
    ltv_status = "WITHIN_LIMITS" if actual_ltv <= max_ltv else "EXCEEDS_LIMIT"
    
    return {
        "property_value": property_value,
        "requested_loan_amount": loan_amount,
        "property_type": property_type,
        
        "ltv_calculation": {
            "actual_ltv_percentage": round(actual_ltv, 2),
            "max_ltv_allowed": max_ltv,
            "max_loan_at_max_ltv": round(max_loan_amount, 0),
            "excess_amount": max(0, loan_amount - max_loan_amount)
        },
        
        "ltv_status": ltv_status,
        "ltv_margin": round(max_ltv - actual_ltv, 2),
        
        "recommendation": {
            "WITHIN_LIMITS": f"LTV of {actual_ltv:.1f}% is acceptable",
            "EXCEEDS_LIMIT": f"Reduce loan amount by ₹{loan_amount - max_loan_amount:,.0f} or provide additional collateral"
        }[ltv_status],
        
        "assessment": "PASS" if ltv_status == "WITHIN_LIMITS" else "FAIL"
    }


def assess_collateral_risk(
    property_type: str = "Residential",
    location: str = "Metro City",
    property_age_years: int = 5,
    legal_status: str = "Clear"
) -> Dict[str, Any]:
    """
    Assess risk associated with collateral.
    
    Args:
        property_type: Type of property
        location: Location of property
        property_age_years: Age of property
        legal_status: Legal status of property
        
    Returns:
        Dictionary containing risk assessment
    """
    # Risk factors
    risk_score = 0
    risk_factors = []
    mitigating_factors = []
    
    # Property type risk
    if property_type in ["Residential"]:
        risk_score += 10
        mitigating_factors.append("Residential property - high marketability")
    elif property_type in ["Commercial"]:
        risk_score += 25
        risk_factors.append("Commercial property - market dependent")
    elif property_type in ["Plot"]:
        risk_score += 30
        risk_factors.append("Plot - lower liquidity")
    else:
        risk_score += 20
    
    # Location risk
    if location == "Metro City":
        risk_score += 5
        mitigating_factors.append("Prime metro location")
    elif location == "Tier 1 City":
        risk_score += 10
    else:
        risk_score += 20
        risk_factors.append("Non-metro location")
    
    # Age risk
    if property_age_years <= 5:
        risk_score += 5
        mitigating_factors.append("New construction")
    elif property_age_years <= 15:
        risk_score += 10
    else:
        risk_score += 20
        risk_factors.append("Older property - maintenance concerns")
    
    # Legal risk
    if legal_status == "Clear":
        risk_score += 0
        mitigating_factors.append("Clear legal title")
    else:
        risk_score += 30
        risk_factors.append("Legal issues present")
    
    # Determine risk category
    if risk_score <= 25:
        risk_category = "LOW"
        marketability = "HIGH"
        liquidation_months = 3
    elif risk_score <= 50:
        risk_category = "MEDIUM"
        marketability = "MEDIUM"
        liquidation_months = 6
    else:
        risk_category = "HIGH"
        marketability = "LOW"
        liquidation_months = 12
    
    return {
        "assessment_date": datetime.now().isoformat(),
        
        "property_profile": {
            "type": property_type,
            "location": location,
            "age_years": property_age_years,
            "legal_status": legal_status
        },
        
        "risk_analysis": {
            "risk_score": risk_score,
            "risk_category": risk_category,
            "risk_factors": risk_factors if risk_factors else ["No significant risk factors"],
            "mitigating_factors": mitigating_factors
        },
        
        "marketability_assessment": {
            "marketability_rating": marketability,
            "estimated_liquidation_time_months": liquidation_months,
            "buyer_pool": "LARGE" if marketability == "HIGH" else "MODERATE" if marketability == "MEDIUM" else "LIMITED"
        },
        
        "insurance_requirements": {
            "fire_insurance": "MANDATORY",
            "earthquake_coverage": "RECOMMENDED" if location in ["Metro City", "Tier 1 City"] else "OPTIONAL",
            "flood_coverage": "AS_APPLICABLE"
        },
        
        "collateral_status": "ACCEPTABLE" if risk_category in ["LOW", "MEDIUM"] else "NEEDS_REVIEW"
    }


def evaluate_other_assets(customer_name: str) -> Dict[str, Any]:
    """
    Evaluate additional assets and securities.
    
    Args:
        customer_name: Name of customer
        
    Returns:
        Dictionary containing other assets evaluation
    """
    # Simulated other assets for the customer
    return {
        "customer_name": customer_name,
        "evaluation_date": datetime.now().isoformat(),
        
        "financial_assets": {
            "fixed_deposits": {
                "available": True,
                "estimated_value": 500000,
                "can_be_pledged": True
            },
            "mutual_funds": {
                "available": True,
                "estimated_value": 300000,
                "can_be_pledged": True
            },
            "stocks": {
                "available": True,
                "estimated_value": 200000,
                "can_be_pledged": True
            },
            "insurance_policies": {
                "available": True,
                "surrender_value": 150000,
                "can_be_assigned": True
            }
        },
        
        "other_real_estate": {
            "additional_properties": 0,
            "estimated_value": 0
        },
        
        "vehicles": {
            "count": 1,
            "estimated_value": 400000
        },
        
        "total_other_assets": 1550000,
        
        "assets_available_for_additional_security": {
            "fixed_deposits": 500000,
            "mutual_funds": 300000,
            "total": 800000
        },
        
        "net_worth_estimate": 7000000,
        "asset_quality": "GOOD"
    }


def check_encumbrance(property_details: str = "") -> Dict[str, Any]:
    """
    Check for existing liens or encumbrances on property.
    
    Args:
        property_details: Property identification details
        
    Returns:
        Dictionary containing encumbrance check results
    """
    return {
        "check_date": datetime.now().isoformat(),
        "property_details": property_details if property_details else "As per documents",
        
        "encumbrance_search": {
            "period_searched": "Last 30 years",
            "search_office": "Sub-Registrar Office",
            "search_completed": True
        },
        
        "encumbrance_status": "CLEAR",
        
        "transactions_found": [
            {
                "date": "2020-05-10",
                "type": "Sale Deed",
                "parties": "Previous Owner to Current Owner",
                "status": "Registered"
            }
        ],
        
        "existing_mortgages": "NONE",
        "pending_litigations": "NONE",
        "attachment_orders": "NONE",
        "prohibitory_orders": "NONE",
        
        "certificate_details": {
            "ec_number": "EC/2026/001234",
            "issue_date": datetime.now().strftime("%Y-%m-%d"),
            "valid_till": "Valid for loan processing"
        },
        
        "verification_status": "VERIFIED",
        "property_free_for_mortgage": True
    }


def generate_valuation_report(
    customer_name: str,
    application_id: str,
    loan_amount: float,
    property_type: str = "Residential",
    property_area_sqft: int = 1500
) -> Dict[str, Any]:
    """
    Generate comprehensive valuation report.
    
    Args:
        customer_name: Name of customer
        application_id: Application ID
        loan_amount: Requested loan amount
        property_type: Type of property
        property_area_sqft: Property area
        
    Returns:
        Dictionary containing complete valuation report
    """
    # Run all evaluations
    doc_verification = verify_property_documents(customer_name)
    property_value_result = calculate_property_value(
        property_type=property_type,
        built_up_area_sqft=property_area_sqft
    )
    property_value = property_value_result["valuation_results"]["market_value"]
    
    ltv_result = calculate_ltv_ratio(property_value, loan_amount, property_type)
    risk_result = assess_collateral_risk(property_type=property_type)
    other_assets = evaluate_other_assets(customer_name)
    encumbrance = check_encumbrance()
    
    # Overall assessment
    docs_ok = doc_verification["overall_status"] == "VERIFIED"
    ltv_ok = ltv_result["assessment"] == "PASS"
    risk_ok = risk_result["collateral_status"] == "ACCEPTABLE"
    encumbrance_ok = encumbrance["property_free_for_mortgage"]
    
    all_passed = docs_ok and ltv_ok and risk_ok and encumbrance_ok
    
    return {
        "report_id": f"VAL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "application_id": application_id,
        "customer_name": customer_name,
        "valuation_date": datetime.now().isoformat(),
        
        "document_verification": doc_verification,
        "property_valuation": property_value_result,
        "ltv_analysis": ltv_result,
        "collateral_risk": risk_result,
        "encumbrance_check": encumbrance,
        "other_assets": other_assets,
        
        "valuation_summary": {
            "property_market_value": property_value,
            "forced_sale_value": property_value_result["valuation_results"]["forced_sale_value"],
            "requested_loan_amount": loan_amount,
            "actual_ltv": ltv_result["ltv_calculation"]["actual_ltv_percentage"],
            "max_eligible_loan": ltv_result["ltv_calculation"]["max_loan_at_max_ltv"],
            "collateral_risk_category": risk_result["risk_analysis"]["risk_category"],
            "additional_security_available": other_assets["assets_available_for_additional_security"]["total"]
        },
        
        "overall_assessment": {
            "documents_verified": docs_ok,
            "ltv_within_limits": ltv_ok,
            "risk_acceptable": risk_ok,
            "encumbrance_clear": encumbrance_ok
        },
        
        "collateral_status": "ADEQUATE" if all_passed else "CONDITIONAL" if (docs_ok and ltv_ok) else "INADEQUATE",
        "recommendation": "ACCEPT_COLLATERAL" if all_passed else "REVIEW_REQUIRED",
        
        "next_stage": "UNDERWRITING",
        "parallel_with": "CREDIT_ASSESSMENT",
        "handoff_ready": all_passed
    }


# ============================================================================
# TOOL DEFINITIONS FOR AZURE AI FOUNDRY
# ============================================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "verify_property_documents",
            "description": "Verify property ownership and legal documents",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "Customer name"}
                },
                "required": ["customer_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_property_value",
            "description": "Calculate market value of property",
            "parameters": {
                "type": "object",
                "properties": {
                    "property_type": {"type": "string", "description": "Type of property"},
                    "location": {"type": "string", "description": "Location/city"},
                    "built_up_area_sqft": {"type": "integer", "description": "Built-up area in sqft"},
                    "property_age_years": {"type": "integer", "description": "Age of property"},
                    "construction_quality": {"type": "string", "description": "Quality of construction"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_ltv_ratio",
            "description": "Calculate Loan-to-Value ratio",
            "parameters": {
                "type": "object",
                "properties": {
                    "property_value": {"type": "number", "description": "Market value of property"},
                    "loan_amount": {"type": "number", "description": "Requested loan amount"},
                    "property_type": {"type": "string", "description": "Type of property"}
                },
                "required": ["property_value", "loan_amount"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "assess_collateral_risk",
            "description": "Assess risk associated with collateral",
            "parameters": {
                "type": "object",
                "properties": {
                    "property_type": {"type": "string", "description": "Type of property"},
                    "location": {"type": "string", "description": "Location"},
                    "property_age_years": {"type": "integer", "description": "Property age"},
                    "legal_status": {"type": "string", "description": "Legal status"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "evaluate_other_assets",
            "description": "Evaluate additional assets and securities",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "Customer name"}
                },
                "required": ["customer_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_encumbrance",
            "description": "Check for existing liens or encumbrances on property",
            "parameters": {
                "type": "object",
                "properties": {
                    "property_details": {"type": "string", "description": "Property identification"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_valuation_report",
            "description": "Generate comprehensive valuation report",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "Customer name"},
                    "application_id": {"type": "string", "description": "Application ID"},
                    "loan_amount": {"type": "number", "description": "Loan amount"},
                    "property_type": {"type": "string", "description": "Property type"},
                    "property_area_sqft": {"type": "integer", "description": "Property area"}
                },
                "required": ["customer_name", "application_id", "loan_amount"]
            }
        }
    }
]


# ============================================================================
# AGENT CLASS
# ============================================================================

class AssetValuationAgent:
    """Asset Valuation Agent for loan processing"""
    
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
            "verify_property_documents": verify_property_documents,
            "calculate_property_value": calculate_property_value,
            "calculate_ltv_ratio": calculate_ltv_ratio,
            "assess_collateral_risk": assess_collateral_risk,
            "evaluate_other_assets": evaluate_other_assets,
            "check_encumbrance": check_encumbrance,
            "generate_valuation_report": generate_valuation_report
        }
        
        if tool_name in tool_functions:
            result = tool_functions[tool_name](**arguments)
            return json.dumps(result, indent=2)
        
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
    
    def process_request(self, user_message: str) -> str:
        """Process an asset valuation request"""
        # Create agent dynamically
        agent = self.project_client.agents.create_agent(
            model=MODEL_DEPLOYMENT,
            name="asset-valuation-agent",
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
            "name": "Asset Valuation Agent",
            "description": "Evaluates collateral and asset worth for loan security",
            "stage": 4,
            "parallel_with": "Credit Assessment Agent",
            "previous_agent": "Credit Qualification Agent",
            "next_agent": "Underwriting Agent",
            "tools": [tool["function"]["name"] for tool in self.tools]
        }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  ASSET VALUATION AGENT")
    print("=" * 70)
    
    agent = AssetValuationAgent()
    print(f"\nAgent Info: {json.dumps(agent.get_agent_info(), indent=2)}")
    
    # Test with sample request
    test_message = """
    Perform asset valuation for:
    
    Customer: Kala Divan
    Application ID: LOAN-20260127120000
    Loan Amount Requested: ₹40,00,000
    Property Type: Residential
    Property Area: 1500 sq.ft
    
    Verify property documents, calculate value, assess LTV, and generate
    comprehensive valuation report.
    """
    
    print(f"\n{'='*70}")
    print("Processing Request...")
    print(f"{'='*70}")
    
    response = agent.process_request(test_message)
    print(f"\nAgent Response:\n{response}")