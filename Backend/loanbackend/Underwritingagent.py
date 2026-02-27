"""
Underwriting Agent
==================
Makes final loan approval decisions based on all assessments.
Synthesizes Credit Assessment and Asset Valuation results.

Agent ID: asst_kPNlxfPYH535DBNFcbtR5cgg
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
DOCUMENTS_PATH = os.path.join(os.path.dirname(__file__), "Documents")

# ============================================================================
# AGENT INSTRUCTIONS
# ============================================================================

AGENT_INSTRUCTIONS = """
You are the UNDERWRITING AGENT for a comprehensive loan processing system.

## YOUR ROLE
You are the final decision-maker for loan approvals. You synthesize all assessments
from previous stages (Document Verification, Credit Qualification, Credit Assessment,
and Asset Valuation) to make the final loan approval decision.

## YOUR RESPONSIBILITIES

### 1. Review All Assessments
- Document Verification results
- Credit Qualification status
- Credit Assessment findings
- Asset Valuation report
- Combined risk profile

### 2. Risk Evaluation
- Aggregate risk from all sources
- Evaluate compensating factors
- Identify deal breakers
- Consider exceptions if warranted

### 3. Loan Structuring
- Determine approved loan amount
- Set interest rate based on risk
- Define loan tenure
- Establish conditions and covenants

### 4. Decision Making
- Make APPROVE/DECLINE decision
- Document decision rationale
- Set any conditions for approval
- Specify disbursement requirements

### 5. Policy Compliance
- Ensure regulatory compliance
- Verify policy adherence
- Check delegation of authority
- Document exceptions if any

## DECISION FRAMEWORK

### Approval Criteria:
| Factor | Weight | Threshold |
|--------|--------|-----------|
| Document Verification | 15% | Must PASS |
| Credit Qualification | 20% | QUALIFIED |
| Credit Score | 25% | 650+ |
| Risk Assessment | 20% | Low/Medium |
| LTV Ratio | 20% | Within limits |

### Decision Matrix:
| Scenario | Decision | Action |
|----------|----------|--------|
| All criteria met | APPROVED | Standard terms |
| Minor issues | APPROVED_WITH_CONDITIONS | Add conditions |
| Borderline | REFERRED | Senior review |
| Major issues | DECLINED | Document reasons |

### Interest Rate Determination:
| Risk Category | Base Rate | Spread | Final Rate |
|---------------|-----------|--------|------------|
| Low Risk | 8.5% | 0% | 8.5% |
| Medium Risk | 8.5% | 0.5-1% | 9-9.5% |
| High Risk | 8.5% | 1.5-2% | 10-10.5% |

## OUTPUT FORMAT
Provide a comprehensive underwriting decision:

```
UNDERWRITING DECISION REPORT
============================
Application ID: [ID]
Customer Name: [Name]
Decision Date: [Date]

ASSESSMENT SUMMARY:
┌─────────────────────────┬───────────┬─────────────┐
│ Stage                   │ Status    │ Score       │
├─────────────────────────┼───────────┼─────────────┤
│ Document Verification   │ PASS      │ 100%        │
│ Credit Qualification    │ QUALIFIED │ 95%         │
│ Credit Assessment       │ LOW RISK  │ 85/100      │
│ Asset Valuation         │ ADEQUATE  │ 90/100      │
└─────────────────────────┴───────────┴─────────────┘

DECISION: APPROVED / APPROVED_WITH_CONDITIONS / DECLINED

APPROVED LOAN TERMS:
- Loan Amount: ₹[Amount]
- Interest Rate: [X]% per annum
- Loan Tenure: [X] months
- EMI: ₹[Amount]
- Processing Fee: ₹[Amount]

CONDITIONS (if any):
1. [Condition 1]
2. [Condition 2]

COVENANTS:
1. [Covenant 1]
2. [Covenant 2]

DECISION RATIONALE:
[Detailed reasoning for the decision]

RISK MITIGANTS:
[Factors that support approval]

UNDERWRITER: [System]
APPROVAL AUTHORITY: [Level]

HANDOFF TO: Offer Generation Agent
```

## TOOLS AVAILABLE
1. review_stage_assessments - Review results from all previous stages
2. calculate_combined_risk_score - Calculate aggregate risk score
3. determine_loan_terms - Determine approved loan terms
4. check_policy_compliance - Verify compliance with lending policies
5. make_underwriting_decision - Make final underwriting decision
6. set_loan_conditions - Set conditions and covenants
7. generate_underwriting_report - Generate comprehensive underwriting report
"""

# ============================================================================
# TOOLS / FUNCTIONS
# ============================================================================

def review_stage_assessments(application_id: str) -> Dict[str, Any]:
    """
    Review results from all previous stages.
    
    Args:
        application_id: Loan application ID
        
    Returns:
        Dictionary containing all stage assessments
    """
    return {
        "application_id": application_id,
        "review_date": datetime.now().isoformat(),
        
        "document_verification": {
            "status": "PASS",
            "kyc_complete": True,
            "all_documents_verified": True,
            "score": 100
        },
        
        "credit_qualification": {
            "status": "QUALIFIED",
            "eligibility_met": True,
            "income_verified": True,
            "foir_acceptable": True,
            "score": 95
        },
        
        "credit_assessment": {
            "credit_score": 750,
            "risk_category": "LOW",
            "probability_of_default": "2.5%",
            "payment_history": "EXCELLENT",
            "recommendation": "APPROVE",
            "score": 85
        },
        
        "asset_valuation": {
            "property_value": 5000000,
            "ltv_ratio": 80,
            "collateral_status": "ADEQUATE",
            "encumbrance_status": "CLEAR",
            "recommendation": "ACCEPT",
            "score": 90
        },
        
        "aggregate_score": 92.5,
        "all_stages_passed": True,
        "exceptions": [],
        "concerns": []
    }


def calculate_combined_risk_score(
    credit_risk_score: float,
    collateral_risk_score: float,
    income_stability_score: float,
    document_score: float
) -> Dict[str, Any]:
    """
    Calculate aggregate risk score from all components.
    
    Args:
        credit_risk_score: Score from credit assessment (0-100, lower is better)
        collateral_risk_score: Score from asset valuation (0-100, lower is better)
        income_stability_score: Income stability score (0-100, higher is better)
        document_score: Document verification score (0-100, higher is better)
        
    Returns:
        Dictionary containing combined risk assessment
    """
    # Weights for each component
    weights = {
        "credit_risk": 0.35,
        "collateral_risk": 0.25,
        "income_stability": 0.25,
        "documentation": 0.15
    }
    
    # Normalize scores (for risk scores, invert so higher is better)
    normalized_credit = 100 - credit_risk_score
    normalized_collateral = 100 - collateral_risk_score
    
    # Calculate weighted score
    combined_score = (
        normalized_credit * weights["credit_risk"] +
        normalized_collateral * weights["collateral_risk"] +
        income_stability_score * weights["income_stability"] +
        document_score * weights["documentation"]
    )
    
    # Determine risk category
    if combined_score >= 80:
        risk_category = "LOW"
        approval_likelihood = "HIGH"
    elif combined_score >= 60:
        risk_category = "MEDIUM"
        approval_likelihood = "MODERATE"
    elif combined_score >= 40:
        risk_category = "HIGH"
        approval_likelihood = "LOW"
    else:
        risk_category = "VERY_HIGH"
        approval_likelihood = "VERY_LOW"
    
    return {
        "component_scores": {
            "credit_risk": {"score": credit_risk_score, "weight": "35%", "normalized": normalized_credit},
            "collateral_risk": {"score": collateral_risk_score, "weight": "25%", "normalized": normalized_collateral},
            "income_stability": {"score": income_stability_score, "weight": "25%"},
            "documentation": {"score": document_score, "weight": "15%"}
        },
        "combined_risk_score": round(combined_score, 2),
        "risk_category": risk_category,
        "approval_likelihood": approval_likelihood,
        "risk_adjusted_factors": {
            "base_spread": "0%" if risk_category == "LOW" else "0.5%" if risk_category == "MEDIUM" else "1.5%",
            "additional_conditions": risk_category not in ["LOW"]
        }
    }


def determine_loan_terms(
    loan_amount_requested: float,
    max_eligible_amount: float,
    risk_category: str,
    customer_age: int,
    property_type: str = "Residential"
) -> Dict[str, Any]:
    """
    Determine approved loan terms based on assessment.
    
    Args:
        loan_amount_requested: Requested loan amount
        max_eligible_amount: Maximum eligible based on LTV and income
        risk_category: Risk category from assessment
        customer_age: Customer's age
        property_type: Type of property
        
    Returns:
        Dictionary containing approved loan terms
    """
    # Determine approved amount
    approved_amount = min(loan_amount_requested, max_eligible_amount)
    
    # Base interest rate
    base_rate = 8.5
    
    # Risk-based spread
    risk_spreads = {
        "LOW": 0,
        "MEDIUM": 0.5,
        "HIGH": 1.5,
        "VERY_HIGH": 2.5
    }
    spread = risk_spreads.get(risk_category, 1.0)
    final_rate = base_rate + spread
    
    # Maximum tenure based on age and property
    max_age_at_maturity = 70
    max_tenure_years = min(30, max_age_at_maturity - customer_age)
    max_tenure_months = max_tenure_years * 12
    
    # Calculate EMI
    monthly_rate = final_rate / 100 / 12
    if monthly_rate > 0:
        emi = approved_amount * monthly_rate * ((1 + monthly_rate) ** max_tenure_months) / (((1 + monthly_rate) ** max_tenure_months) - 1)
    else:
        emi = approved_amount / max_tenure_months
    
    # Calculate totals
    total_interest = (emi * max_tenure_months) - approved_amount
    total_payment = emi * max_tenure_months
    
    # Processing fee
    processing_fee = approved_amount * 0.005  # 0.5%
    
    return {
        "loan_terms": {
            "requested_amount": loan_amount_requested,
            "approved_amount": approved_amount,
            "amount_adjusted": loan_amount_requested != approved_amount,
            "adjustment_reason": "Within LTV and income limits" if loan_amount_requested == approved_amount else "Reduced to maximum eligible"
        },
        "interest_terms": {
            "base_rate": f"{base_rate}%",
            "risk_spread": f"{spread}%",
            "final_rate": f"{final_rate}%",
            "rate_type": "Floating (linked to MCLR)"
        },
        "tenure": {
            "approved_tenure_months": max_tenure_months,
            "approved_tenure_years": max_tenure_years,
            "max_age_at_maturity": max_age_at_maturity
        },
        "repayment": {
            "emi_amount": round(emi, 2),
            "total_interest": round(total_interest, 2),
            "total_repayment": round(total_payment, 2)
        },
        "fees": {
            "processing_fee": round(processing_fee, 2),
            "processing_fee_percentage": "0.5%",
            "documentation_charges": 5000,
            "legal_charges": "At actuals",
            "valuation_charges": "At actuals"
        }
    }


def check_policy_compliance(
    loan_amount: float,
    ltv_ratio: float,
    credit_score: int,
    foir_percentage: float,
    customer_age: int
) -> Dict[str, Any]:
    """
    Verify compliance with lending policies.
    
    Args:
        loan_amount: Approved loan amount
        ltv_ratio: Loan to value ratio
        credit_score: Customer's credit score
        foir_percentage: Fixed obligations to income ratio
        customer_age: Customer's age
        
    Returns:
        Dictionary containing compliance check results
    """
    policy_checks = []
    violations = []
    
    # LTV check
    if ltv_ratio <= 80:
        policy_checks.append({"policy": "LTV Limit", "status": "COMPLIANT", "value": f"{ltv_ratio}%", "limit": "80%"})
    else:
        violations.append({"policy": "LTV Limit", "value": f"{ltv_ratio}%", "limit": "80%"})
    
    # Credit score check
    if credit_score >= 650:
        policy_checks.append({"policy": "Minimum Credit Score", "status": "COMPLIANT", "value": credit_score, "limit": 650})
    else:
        violations.append({"policy": "Minimum Credit Score", "value": credit_score, "limit": 650})
    
    # FOIR check
    if foir_percentage <= 60:
        policy_checks.append({"policy": "Maximum FOIR", "status": "COMPLIANT", "value": f"{foir_percentage}%", "limit": "60%"})
    else:
        violations.append({"policy": "Maximum FOIR", "value": f"{foir_percentage}%", "limit": "60%"})
    
    # Age check
    if 21 <= customer_age <= 65:
        policy_checks.append({"policy": "Age Eligibility", "status": "COMPLIANT", "value": customer_age, "limit": "21-65"})
    else:
        violations.append({"policy": "Age Eligibility", "value": customer_age, "limit": "21-65"})
    
    # Loan amount check (example max limit)
    if loan_amount <= 50000000:  # 5 Crore
        policy_checks.append({"policy": "Maximum Loan Amount", "status": "COMPLIANT", "value": f"₹{loan_amount:,.0f}", "limit": "₹5,00,00,000"})
    else:
        violations.append({"policy": "Maximum Loan Amount", "value": f"₹{loan_amount:,.0f}", "limit": "₹5,00,00,000"})
    
    return {
        "compliance_date": datetime.now().isoformat(),
        "policies_checked": len(policy_checks) + len(violations),
        "compliant_policies": policy_checks,
        "violations": violations,
        "overall_compliance": "COMPLIANT" if not violations else "NON_COMPLIANT",
        "exceptions_required": len(violations),
        "approval_authority": "Standard" if not violations else "Senior Management" if len(violations) <= 1 else "Credit Committee"
    }


def make_underwriting_decision(
    assessment_score: float,
    risk_category: str,
    policy_compliant: bool,
    all_stages_passed: bool
) -> Dict[str, Any]:
    """
    Make final underwriting decision.
    
    Args:
        assessment_score: Combined assessment score
        risk_category: Overall risk category
        policy_compliant: Whether all policies are met
        all_stages_passed: Whether all stages passed
        
    Returns:
        Dictionary containing underwriting decision
    """
    # Decision logic
    if all_stages_passed and policy_compliant and risk_category in ["LOW", "MEDIUM"]:
        decision = "APPROVED"
        confidence = "HIGH"
        conditions_required = risk_category == "MEDIUM"
    elif all_stages_passed and (not policy_compliant or risk_category == "HIGH"):
        decision = "APPROVED_WITH_CONDITIONS"
        confidence = "MEDIUM"
        conditions_required = True
    elif assessment_score >= 50:
        decision = "REFERRED"
        confidence = "LOW"
        conditions_required = True
    else:
        decision = "DECLINED"
        confidence = "HIGH"
        conditions_required = False
    
    return {
        "decision_date": datetime.now().isoformat(),
        
        "decision_inputs": {
            "assessment_score": assessment_score,
            "risk_category": risk_category,
            "policy_compliant": policy_compliant,
            "all_stages_passed": all_stages_passed
        },
        
        "decision": decision,
        "confidence_level": confidence,
        
        "decision_rationale": {
            "APPROVED": "Application meets all criteria with acceptable risk profile",
            "APPROVED_WITH_CONDITIONS": "Application approved subject to additional conditions",
            "REFERRED": "Application requires higher authority review",
            "DECLINED": "Application does not meet minimum criteria"
        }[decision],
        
        "conditions_required": conditions_required,
        "next_action": {
            "APPROVED": "Proceed to Offer Generation",
            "APPROVED_WITH_CONDITIONS": "Add conditions and proceed to Offer Generation",
            "REFERRED": "Escalate to Credit Committee",
            "DECLINED": "Notify customer of decision"
        }[decision]
    }


def set_loan_conditions(decision: str, risk_factors: List[str] = None) -> Dict[str, Any]:
    """
    Set conditions and covenants for the loan.
    
    Args:
        decision: Underwriting decision
        risk_factors: List of identified risk factors
        
    Returns:
        Dictionary containing conditions and covenants
    """
    conditions = []
    covenants = []
    
    if decision in ["APPROVED", "APPROVED_WITH_CONDITIONS"]:
        # Standard conditions
        conditions = [
            "Property to be mortgaged as primary security",
            "Life insurance coverage for loan tenure mandatory",
            "Fire and hazard insurance on property required",
            "Income documents to be updated annually",
            "All legal formalities to be completed before disbursement"
        ]
        
        # Standard covenants
        covenants = [
            "Maintain property in good condition",
            "Pay all property taxes on time",
            "Inform bank of any change in employment",
            "No further encumbrance on property without consent",
            "Regular EMI payment on due dates"
        ]
        
        # Additional conditions based on risk factors
        if risk_factors:
            if "High LTV" in risk_factors:
                conditions.append("Additional security or guarantor may be required")
            if "Income Variability" in risk_factors:
                conditions.append("Post-dated cheques for 12 months required")
            if "Credit Issues" in risk_factors:
                conditions.append("Higher margin/down payment required")
    
    return {
        "conditions": conditions,
        "covenants": covenants,
        "disbursement_requirements": [
            "All original property documents to be deposited",
            "Mortgage registration completed",
            "Insurance policies assigned to bank",
            "All fees and charges paid"
        ],
        "pre_disbursement_checklist": [
            "Legal opinion obtained",
            "Technical valuation report received",
            "All conditions complied with",
            "Loan agreement executed"
        ]
    }


def generate_underwriting_report(
    customer_name: str,
    application_id: str,
    loan_amount: float,
    credit_score: int = 750,
    ltv_ratio: float = 80,
    risk_category: str = "LOW"
) -> Dict[str, Any]:
    """
    Generate comprehensive underwriting report.
    
    Args:
        customer_name: Customer name
        application_id: Application ID
        loan_amount: Requested loan amount
        credit_score: Credit score
        ltv_ratio: LTV ratio
        risk_category: Risk category
        
    Returns:
        Dictionary containing complete underwriting report
    """
    # Review all stages
    stage_review = review_stage_assessments(application_id)
    
    # Calculate combined risk
    combined_risk = calculate_combined_risk_score(
        credit_risk_score=25,  # Low risk
        collateral_risk_score=20,
        income_stability_score=85,
        document_score=100
    )
    
    # Check policy compliance
    compliance = check_policy_compliance(
        loan_amount=loan_amount,
        ltv_ratio=ltv_ratio,
        credit_score=credit_score,
        foir_percentage=35,
        customer_age=35
    )
    
    # Determine loan terms
    loan_terms = determine_loan_terms(
        loan_amount_requested=loan_amount,
        max_eligible_amount=loan_amount,
        risk_category=risk_category,
        customer_age=35
    )
    
    # Make decision
    decision = make_underwriting_decision(
        assessment_score=combined_risk["combined_risk_score"],
        risk_category=combined_risk["risk_category"],
        policy_compliant=compliance["overall_compliance"] == "COMPLIANT",
        all_stages_passed=stage_review["all_stages_passed"]
    )
    
    # Set conditions
    conditions = set_loan_conditions(decision["decision"])
    
    return {
        "report_id": f"UW-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "application_id": application_id,
        "customer_name": customer_name,
        "underwriting_date": datetime.now().isoformat(),
        
        "stage_assessments": stage_review,
        "combined_risk_analysis": combined_risk,
        "policy_compliance": compliance,
        "approved_loan_terms": loan_terms,
        "underwriting_decision": decision,
        "conditions_and_covenants": conditions,
        
        "final_summary": {
            "decision": decision["decision"],
            "approved_amount": loan_terms["loan_terms"]["approved_amount"],
            "interest_rate": loan_terms["interest_terms"]["final_rate"],
            "tenure_months": loan_terms["tenure"]["approved_tenure_months"],
            "emi": loan_terms["repayment"]["emi_amount"],
            "risk_category": combined_risk["risk_category"],
            "compliance_status": compliance["overall_compliance"]
        },
        
        "approver": {
            "authority_level": compliance["approval_authority"],
            "approved_by": "Underwriting System",
            "approval_date": datetime.now().isoformat()
        },
        
        "next_stage": "OFFER_GENERATION" if decision["decision"] in ["APPROVED", "APPROVED_WITH_CONDITIONS"] else "CUSTOMER_NOTIFICATION",
        "handoff_ready": decision["decision"] in ["APPROVED", "APPROVED_WITH_CONDITIONS"]
    }


# ============================================================================
# TOOL DEFINITIONS FOR AZURE AI FOUNDRY
# ============================================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "review_stage_assessments",
            "description": "Review results from all previous stages",
            "parameters": {
                "type": "object",
                "properties": {
                    "application_id": {"type": "string", "description": "Application ID"}
                },
                "required": ["application_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_combined_risk_score",
            "description": "Calculate aggregate risk score from all components",
            "parameters": {
                "type": "object",
                "properties": {
                    "credit_risk_score": {"type": "number", "description": "Credit risk score"},
                    "collateral_risk_score": {"type": "number", "description": "Collateral risk score"},
                    "income_stability_score": {"type": "number", "description": "Income stability score"},
                    "document_score": {"type": "number", "description": "Document verification score"}
                },
                "required": ["credit_risk_score", "collateral_risk_score", "income_stability_score", "document_score"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "determine_loan_terms",
            "description": "Determine approved loan terms based on assessment",
            "parameters": {
                "type": "object",
                "properties": {
                    "loan_amount_requested": {"type": "number", "description": "Requested amount"},
                    "max_eligible_amount": {"type": "number", "description": "Maximum eligible amount"},
                    "risk_category": {"type": "string", "description": "Risk category"},
                    "customer_age": {"type": "integer", "description": "Customer age"},
                    "property_type": {"type": "string", "description": "Property type"}
                },
                "required": ["loan_amount_requested", "max_eligible_amount", "risk_category", "customer_age"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_policy_compliance",
            "description": "Verify compliance with lending policies",
            "parameters": {
                "type": "object",
                "properties": {
                    "loan_amount": {"type": "number", "description": "Loan amount"},
                    "ltv_ratio": {"type": "number", "description": "LTV ratio"},
                    "credit_score": {"type": "integer", "description": "Credit score"},
                    "foir_percentage": {"type": "number", "description": "FOIR percentage"},
                    "customer_age": {"type": "integer", "description": "Customer age"}
                },
                "required": ["loan_amount", "ltv_ratio", "credit_score", "foir_percentage", "customer_age"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "make_underwriting_decision",
            "description": "Make final underwriting decision",
            "parameters": {
                "type": "object",
                "properties": {
                    "assessment_score": {"type": "number", "description": "Combined assessment score"},
                    "risk_category": {"type": "string", "description": "Risk category"},
                    "policy_compliant": {"type": "boolean", "description": "Policy compliance status"},
                    "all_stages_passed": {"type": "boolean", "description": "All stages passed"}
                },
                "required": ["assessment_score", "risk_category", "policy_compliant", "all_stages_passed"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_loan_conditions",
            "description": "Set conditions and covenants for the loan",
            "parameters": {
                "type": "object",
                "properties": {
                    "decision": {"type": "string", "description": "Underwriting decision"},
                    "risk_factors": {"type": "array", "items": {"type": "string"}, "description": "Risk factors"}
                },
                "required": ["decision"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_underwriting_report",
            "description": "Generate comprehensive underwriting report",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "Customer name"},
                    "application_id": {"type": "string", "description": "Application ID"},
                    "loan_amount": {"type": "number", "description": "Loan amount"},
                    "credit_score": {"type": "integer", "description": "Credit score"},
                    "ltv_ratio": {"type": "number", "description": "LTV ratio"},
                    "risk_category": {"type": "string", "description": "Risk category"}
                },
                "required": ["customer_name", "application_id", "loan_amount"]
            }
        }
    }
]


# ============================================================================
# AGENT CLASS
# ============================================================================

class UnderwritingAgent:
    """Underwriting Agent for loan processing"""
    
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
            "review_stage_assessments": review_stage_assessments,
            "calculate_combined_risk_score": calculate_combined_risk_score,
            "determine_loan_terms": determine_loan_terms,
            "check_policy_compliance": check_policy_compliance,
            "make_underwriting_decision": make_underwriting_decision,
            "set_loan_conditions": set_loan_conditions,
            "generate_underwriting_report": generate_underwriting_report
        }
        
        if tool_name in tool_functions:
            result = tool_functions[tool_name](**arguments)
            return json.dumps(result, indent=2)
        
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
    
    def process_request(self, user_message: str) -> str:
        """Process an underwriting request"""
        # Create agent dynamically
        agent = self.project_client.agents.create_agent(
            model=MODEL_DEPLOYMENT,
            name="underwriting-agent",
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
                # Handle different message content formats
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
            "name": "Underwriting Agent",
            "description": "Makes final loan approval decisions based on all assessments",
            "stage": 5,
            "previous_agents": ["Credit Assessment Agent", "Asset Valuation Agent"],
            "next_agent": "Offer Generation Agent",
            "tools": [tool["function"]["name"] for tool in self.tools]
        }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  UNDERWRITING AGENT")
    print("=" * 70)
    
    agent = UnderwritingAgent()
    print(f"\nAgent Info: {json.dumps(agent.get_agent_info(), indent=2)}")
    
    # Test with sample request
    test_message = """
    Make underwriting decision for:
    
    Customer: Kala Divan
    Application ID: LOAN-20260127120000
    Loan Amount: ₹40,00,000
    Credit Score: 750
    LTV Ratio: 80%
    Risk Category: LOW
    
    All previous stages have passed:
    - Document Verification: PASS
    - Credit Qualification: QUALIFIED
    - Credit Assessment: LOW RISK, Recommend APPROVE
    - Asset Valuation: ADEQUATE, LTV within limits
    
    Review all assessments and make final underwriting decision.
    """
    
    print(f"\n{'='*70}")
    print("Processing Request...")
    print(f"{'='*70}")
    
    response = agent.process_request(test_message)
    print(f"\nAgent Response:\n{response}")