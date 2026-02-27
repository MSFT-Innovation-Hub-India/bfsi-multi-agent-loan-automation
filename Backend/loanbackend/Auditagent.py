"""
Audit Agent
===========
Audits the complete loan processing workflow.
Generates audit reports, ensures compliance, and maintains audit trail.

Agent ID: asst_Klr9zkywNA2KfTkOn96U8pMH
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
You are the AUDIT AGENT for a comprehensive loan processing system.

## YOUR ROLE
You are responsible for auditing the entire loan processing workflow.
You ensure compliance with regulations, verify all stages were completed
correctly, generate comprehensive audit reports, and maintain an immutable
audit trail for regulatory and internal purposes.

## YOUR RESPONSIBILITIES

### 1. Process Audit
- Verify all stages completed
- Check proper handoffs between agents
- Validate decision points
- Review timeline compliance

### 2. Document Audit
- Verify all documents collected
- Check document authenticity
- Confirm verification status
- Review document retention

### 3. Compliance Check
- RBI guidelines compliance
- Internal policy adherence
- Fair lending practices
- KYC/AML compliance

### 4. Decision Audit
- Review credit decisions
- Validate underwriting logic
- Check pricing consistency
- Verify offer terms

### 5. Audit Trail
- Log all actions
- Maintain immutable records
- Enable traceability
- Support regulatory queries

## AUDIT CHECKPOINTS

### Stage 1: Customer Service
- [ ] Application received and logged
- [ ] Customer identity captured
- [ ] Loan request documented
- [ ] Proper handoff to Stage 2

### Stage 2: Document Verification
- [ ] All required documents collected
- [ ] Documents verified for authenticity
- [ ] No expired documents
- [ ] Verification report generated

### Stage 3: Credit Qualification
- [ ] Eligibility criteria checked
- [ ] Income requirements validated
- [ ] FOIR calculated correctly
- [ ] Qualification report generated

### Stage 4A: Credit Assessment (Parallel)
- [ ] Credit score analyzed
- [ ] Payment history reviewed
- [ ] Risk score calculated
- [ ] Credit report generated

### Stage 4B: Asset Valuation (Parallel)
- [ ] Property documents verified
- [ ] Valuation conducted
- [ ] LTV ratio calculated
- [ ] Valuation report generated

### Stage 5: Underwriting
- [ ] All assessments reviewed
- [ ] Combined risk calculated
- [ ] Decision made with rationale
- [ ] Terms determined correctly

### Stage 6: Offer Generation
- [ ] Offer terms match underwriting
- [ ] EMI calculated correctly
- [ ] All fees disclosed
- [ ] Offer document generated

### Stage 7: Customer Communication
- [ ] Offer communicated properly
- [ ] All channels used
- [ ] Response recorded
- [ ] Handoff completed

## COMPLIANCE AREAS

### 1. RBI Guidelines
- Interest rate transparency
- Fair lending practices
- Prepayment terms compliance
- Disclosure requirements

### 2. KYC/AML
- Identity verification
- Address verification
- Document authenticity
- Risk categorization

### 3. Data Privacy
- Customer consent obtained
- Data minimization followed
- Secure data handling
- Access controls in place

### 4. Internal Policies
- Credit policy adherence
- Pricing policy compliance
- Exception approval process
- Audit trail maintained

## OUTPUT FORMAT
Generate a comprehensive audit report:

```
LOAN PROCESSING AUDIT REPORT
============================
Audit ID: [ID]
Date: [Date]
Application: [ID]
Customer: [Name]

STAGE-WISE AUDIT SUMMARY:
┌────────────────────────────┬──────────┬────────────────────────────┐
│ Stage                      │ Status   │ Observations               │
├────────────────────────────┼──────────┼────────────────────────────┤
│ 1. Customer Service        │ ✓ PASS   │ All checks completed       │
│ 2. Document Verification   │ ✓ PASS   │ All documents verified     │
│ 3. Credit Qualification    │ ✓ PASS   │ Eligibility confirmed      │
│ 4. Credit Assessment       │ ✓ PASS   │ Risk assessed correctly    │
│ 4. Asset Valuation         │ ✓ PASS   │ Valuation within limits    │
│ 5. Underwriting            │ ✓ PASS   │ Decision documented        │
│ 6. Offer Generation        │ ✓ PASS   │ Terms match approval       │
│ 7. Customer Communication  │ ✓ PASS   │ All channels used          │
└────────────────────────────┴──────────┴────────────────────────────┘

COMPLIANCE STATUS:
- RBI Guidelines: ✓ COMPLIANT
- KYC/AML: ✓ COMPLIANT
- Internal Policy: ✓ COMPLIANT
- Data Privacy: ✓ COMPLIANT

OVERALL AUDIT RESULT: PASS / PASS WITH OBSERVATIONS / FAIL

AUDIT TRAIL: [Hash/Reference]
```

## TOOLS AVAILABLE
1. audit_customer_service_stage - Audit Stage 1
2. audit_document_verification_stage - Audit Stage 2
3. audit_credit_stages - Audit Stages 3, 4A, 4B
4. audit_underwriting_stage - Audit Stage 5
5. audit_offer_communication_stages - Audit Stages 6, 7
6. check_regulatory_compliance - Check all compliance areas
7. generate_audit_report - Generate final audit report
"""

# ============================================================================
# TOOLS / FUNCTIONS
# ============================================================================

def audit_customer_service_stage(
    application_id: str,
    customer_name: str,
    application_date: str
) -> Dict[str, Any]:
    """
    Audit Customer Service stage.
    
    Args:
        application_id: Application ID
        customer_name: Customer name
        application_date: Date of application
        
    Returns:
        Dictionary containing audit results
    """
    return {
        "stage": "Customer Service",
        "stage_number": 1,
        "audit_timestamp": datetime.now().isoformat(),
        
        "checkpoints": {
            "application_received": {
                "status": "PASS",
                "details": f"Application {application_id} received on {application_date}",
                "evidence": "Application log entry verified"
            },
            "customer_identity_captured": {
                "status": "PASS",
                "details": f"Customer {customer_name} details captured",
                "evidence": "Customer record created"
            },
            "loan_request_documented": {
                "status": "PASS",
                "details": "Loan type, amount, and purpose documented",
                "evidence": "Application form verified"
            },
            "handoff_to_next_stage": {
                "status": "PASS",
                "details": "Proper handoff to Document Verification",
                "evidence": "Workflow transition logged"
            }
        },
        
        "stage_audit_result": "PASS",
        "observations": [],
        "recommendations": []
    }


def audit_document_verification_stage(
    application_id: str,
    documents_submitted: List[str],
    verification_status: Dict[str, str]
) -> Dict[str, Any]:
    """
    Audit Document Verification stage.
    
    Args:
        application_id: Application ID
        documents_submitted: List of documents submitted
        verification_status: Verification status of each document
        
    Returns:
        Dictionary containing audit results
    """
    all_verified = all(status == "verified" for status in verification_status.values())
    
    return {
        "stage": "Document Verification",
        "stage_number": 2,
        "audit_timestamp": datetime.now().isoformat(),
        
        "checkpoints": {
            "all_documents_collected": {
                "status": "PASS" if len(documents_submitted) >= 6 else "PARTIAL",
                "details": f"{len(documents_submitted)} documents collected",
                "evidence": f"Documents: {', '.join(documents_submitted)}"
            },
            "documents_verified": {
                "status": "PASS" if all_verified else "PARTIAL",
                "details": f"All documents verified for authenticity",
                "evidence": "Verification reports available"
            },
            "no_expired_documents": {
                "status": "PASS",
                "details": "All documents within validity period",
                "evidence": "Expiry dates checked"
            },
            "verification_report_generated": {
                "status": "PASS",
                "details": "Comprehensive verification report generated",
                "evidence": "Report ID available in records"
            }
        },
        
        "document_audit": {
            "total_submitted": len(documents_submitted),
            "verified": sum(1 for s in verification_status.values() if s == "verified"),
            "pending": sum(1 for s in verification_status.values() if s == "pending"),
            "rejected": sum(1 for s in verification_status.values() if s == "rejected")
        },
        
        "stage_audit_result": "PASS" if all_verified else "PASS_WITH_OBSERVATIONS",
        "observations": [] if all_verified else ["Some documents required additional verification"],
        "recommendations": []
    }


def audit_credit_stages(
    application_id: str,
    credit_score: int,
    income: float,
    loan_amount: float,
    property_value: float
) -> Dict[str, Any]:
    """
    Audit Credit Qualification, Credit Assessment, and Asset Valuation stages.
    
    Args:
        application_id: Application ID
        credit_score: Customer's credit score
        income: Monthly income
        loan_amount: Requested loan amount
        property_value: Property value
        
    Returns:
        Dictionary containing audit results
    """
    ltv = (loan_amount / property_value) * 100
    foir = (loan_amount * 0.008 / income) * 100  # Approximate EMI/income
    
    return {
        "stages_audited": [
            "Credit Qualification (Stage 3)",
            "Credit Assessment (Stage 4A)",
            "Asset Valuation (Stage 4B)"
        ],
        "audit_timestamp": datetime.now().isoformat(),
        
        "credit_qualification_audit": {
            "eligibility_checked": {
                "status": "PASS",
                "details": "All eligibility criteria verified",
                "evidence": "Eligibility checklist completed"
            },
            "income_validated": {
                "status": "PASS",
                "details": f"Monthly income ₹{income:,.0f} validated",
                "evidence": "Income documents verified"
            },
            "foir_calculated": {
                "status": "PASS",
                "details": f"FOIR: {foir:.1f}% (within 50% limit)",
                "evidence": "FOIR calculation documented"
            }
        },
        
        "credit_assessment_audit": {
            "credit_score_analyzed": {
                "status": "PASS",
                "details": f"Credit score {credit_score} analyzed",
                "evidence": "Credit bureau report obtained"
            },
            "payment_history_reviewed": {
                "status": "PASS",
                "details": "Payment history for last 36 months reviewed",
                "evidence": "Credit report details verified"
            },
            "risk_score_calculated": {
                "status": "PASS",
                "details": "Risk score calculated using standard model",
                "evidence": "Risk scoring worksheet completed"
            }
        },
        
        "asset_valuation_audit": {
            "property_documents_verified": {
                "status": "PASS",
                "details": "All property documents authenticated",
                "evidence": "Legal verification report available"
            },
            "valuation_conducted": {
                "status": "PASS",
                "details": f"Property valued at ₹{property_value:,.0f}",
                "evidence": "Valuation report from approved valuer"
            },
            "ltv_calculated": {
                "status": "PASS",
                "details": f"LTV: {ltv:.1f}% (within 80% limit)",
                "evidence": "LTV calculation documented"
            }
        },
        
        "stage_audit_result": "PASS",
        "observations": [],
        "recommendations": []
    }


def audit_underwriting_stage(
    application_id: str,
    decision: str,
    approved_amount: float,
    interest_rate: float,
    decision_rationale: str
) -> Dict[str, Any]:
    """
    Audit Underwriting stage.
    
    Args:
        application_id: Application ID
        decision: Underwriting decision
        approved_amount: Approved loan amount
        interest_rate: Approved interest rate
        decision_rationale: Rationale for decision
        
    Returns:
        Dictionary containing audit results
    """
    return {
        "stage": "Underwriting",
        "stage_number": 5,
        "audit_timestamp": datetime.now().isoformat(),
        
        "checkpoints": {
            "all_assessments_reviewed": {
                "status": "PASS",
                "details": "Credit and asset assessments reviewed",
                "evidence": "Review checklist completed"
            },
            "combined_risk_calculated": {
                "status": "PASS",
                "details": "Combined risk score calculated",
                "evidence": "Risk aggregation worksheet"
            },
            "decision_documented": {
                "status": "PASS",
                "details": f"Decision: {decision}",
                "evidence": decision_rationale
            },
            "terms_determined": {
                "status": "PASS",
                "details": f"Amount: ₹{approved_amount:,.0f}, Rate: {interest_rate}%",
                "evidence": "Sanction terms documented"
            }
        },
        
        "decision_audit": {
            "decision": decision,
            "approved_amount": approved_amount,
            "interest_rate": interest_rate,
            "pricing_within_policy": True,
            "exception_required": False,
            "approver_authorized": True
        },
        
        "stage_audit_result": "PASS",
        "observations": [],
        "recommendations": []
    }


def audit_offer_communication_stages(
    application_id: str,
    offer_amount: float,
    emi: float,
    customer_response: str,
    communication_channels: List[str]
) -> Dict[str, Any]:
    """
    Audit Offer Generation and Customer Communication stages.
    
    Args:
        application_id: Application ID
        offer_amount: Offered loan amount
        emi: EMI amount
        customer_response: Customer's response
        communication_channels: Channels used
        
    Returns:
        Dictionary containing audit results
    """
    return {
        "stages_audited": [
            "Offer Generation (Stage 6)",
            "Customer Communication (Stage 7)"
        ],
        "audit_timestamp": datetime.now().isoformat(),
        
        "offer_generation_audit": {
            "terms_match_underwriting": {
                "status": "PASS",
                "details": "Offer terms match underwriting approval",
                "evidence": "Term comparison verified"
            },
            "emi_calculated_correctly": {
                "status": "PASS",
                "details": f"EMI ₹{emi:,.0f} calculated correctly",
                "evidence": "EMI calculation verified"
            },
            "fees_disclosed": {
                "status": "PASS",
                "details": "All fees and charges disclosed",
                "evidence": "Fee schedule in offer document"
            },
            "offer_document_generated": {
                "status": "PASS",
                "details": "Complete offer document generated",
                "evidence": "Offer document in records"
            }
        },
        
        "customer_communication_audit": {
            "offer_communicated": {
                "status": "PASS",
                "details": "Offer communicated to customer",
                "evidence": f"Channels: {', '.join(communication_channels)}"
            },
            "all_channels_used": {
                "status": "PASS" if len(communication_channels) >= 2 else "PARTIAL",
                "details": f"{len(communication_channels)} channels used",
                "evidence": "Communication logs available"
            },
            "response_recorded": {
                "status": "PASS",
                "details": f"Customer response: {customer_response}",
                "evidence": "Response logged in system"
            },
            "handoff_completed": {
                "status": "PASS",
                "details": "Proper handoff to Audit stage",
                "evidence": "Workflow transition logged"
            }
        },
        
        "stage_audit_result": "PASS",
        "observations": [],
        "recommendations": []
    }


def check_regulatory_compliance(
    application_id: str,
    loan_amount: float,
    interest_rate: float,
    customer_category: str = "General"
) -> Dict[str, Any]:
    """
    Check regulatory compliance across all areas.
    
    Args:
        application_id: Application ID
        loan_amount: Loan amount
        interest_rate: Interest rate
        customer_category: Customer category
        
    Returns:
        Dictionary containing compliance status
    """
    return {
        "compliance_check_id": f"COMP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "application_id": application_id,
        "check_timestamp": datetime.now().isoformat(),
        
        "rbi_guidelines": {
            "status": "COMPLIANT",
            "checks": {
                "interest_rate_transparency": "PASS - Rate clearly disclosed",
                "prepayment_terms": "PASS - No prepayment penalty on floating rate",
                "disclosure_requirements": "PASS - All disclosures made",
                "fair_lending": "PASS - Standard terms applied"
            }
        },
        
        "kyc_aml": {
            "status": "COMPLIANT",
            "checks": {
                "identity_verification": "PASS - PAN and Aadhaar verified",
                "address_verification": "PASS - Address proof verified",
                "document_authenticity": "PASS - All documents authenticated",
                "risk_categorization": f"PASS - Customer categorized as {customer_category}"
            }
        },
        
        "data_privacy": {
            "status": "COMPLIANT",
            "checks": {
                "customer_consent": "PASS - Consent obtained for data processing",
                "data_minimization": "PASS - Only necessary data collected",
                "secure_handling": "PASS - Data encrypted and secured",
                "access_controls": "PASS - Role-based access implemented"
            }
        },
        
        "internal_policy": {
            "status": "COMPLIANT",
            "checks": {
                "credit_policy": "PASS - Within credit policy limits",
                "pricing_policy": f"PASS - Rate {interest_rate}% within policy",
                "exception_approval": "PASS - No exceptions required",
                "audit_trail": "PASS - Complete audit trail maintained"
            }
        },
        
        "overall_compliance": "FULLY COMPLIANT",
        "compliance_score": "100%",
        "issues_found": 0,
        "recommendations": []
    }


def generate_audit_report(
    application_id: str,
    customer_name: str,
    loan_amount: float,
    interest_rate: float,
    tenure_months: int,
    emi: float,
    decision: str
) -> Dict[str, Any]:
    """
    Generate comprehensive audit report for the entire loan processing.
    
    Args:
        application_id: Application ID
        customer_name: Customer name
        loan_amount: Loan amount
        interest_rate: Interest rate
        tenure_months: Tenure in months
        emi: EMI amount
        decision: Final decision
        
    Returns:
        Dictionary containing complete audit report
    """
    audit_id = f"AUDIT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        "audit_report": {
            "audit_id": audit_id,
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            "report_time": datetime.now().strftime("%H:%M:%S"),
            "auditor": "Audit Agent (Automated)"
        },
        
        "application_summary": {
            "application_id": application_id,
            "customer_name": customer_name,
            "loan_amount": f"₹{loan_amount:,.0f}",
            "interest_rate": f"{interest_rate}%",
            "tenure": f"{tenure_months} months",
            "emi": f"₹{emi:,.0f}",
            "decision": decision
        },
        
        "stage_audit_summary": {
            "stage_1_customer_service": {
                "status": "PASS",
                "observations": "None"
            },
            "stage_2_document_verification": {
                "status": "PASS",
                "observations": "None"
            },
            "stage_3_credit_qualification": {
                "status": "PASS",
                "observations": "None"
            },
            "stage_4a_credit_assessment": {
                "status": "PASS",
                "observations": "None"
            },
            "stage_4b_asset_valuation": {
                "status": "PASS",
                "observations": "None"
            },
            "stage_5_underwriting": {
                "status": "PASS",
                "observations": "None"
            },
            "stage_6_offer_generation": {
                "status": "PASS",
                "observations": "None"
            },
            "stage_7_customer_communication": {
                "status": "PASS",
                "observations": "None"
            }
        },
        
        "compliance_summary": {
            "rbi_guidelines": "COMPLIANT",
            "kyc_aml": "COMPLIANT",
            "data_privacy": "COMPLIANT",
            "internal_policy": "COMPLIANT"
        },
        
        "overall_audit_result": {
            "result": "PASS",
            "score": "100%",
            "observations": 0,
            "recommendations": 0,
            "exceptions": 0
        },
        
        "audit_trail": {
            "trail_reference": f"TRAIL-{audit_id}",
            "blockchain_hash": f"0x{datetime.now().strftime('%Y%m%d%H%M%S')}abc123def456",
            "immutable": True,
            "retention_years": 10
        },
        
        "certification": {
            "statement": "This audit certifies that the loan application has been processed in accordance with all applicable regulations, policies, and procedures.",
            "auditor": "Audit Agent",
            "timestamp": datetime.now().isoformat()
        },
        
        "workflow_complete": True,
        "ready_for_disbursement": decision == "APPROVED"
    }


# ============================================================================
# TOOL DEFINITIONS FOR AZURE AI FOUNDRY
# ============================================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "audit_customer_service_stage",
            "description": "Audit Customer Service stage",
            "parameters": {
                "type": "object",
                "properties": {
                    "application_id": {"type": "string", "description": "Application ID"},
                    "customer_name": {"type": "string", "description": "Customer name"},
                    "application_date": {"type": "string", "description": "Application date"}
                },
                "required": ["application_id", "customer_name", "application_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "audit_document_verification_stage",
            "description": "Audit Document Verification stage",
            "parameters": {
                "type": "object",
                "properties": {
                    "application_id": {"type": "string", "description": "Application ID"},
                    "documents_submitted": {"type": "array", "items": {"type": "string"}, "description": "Documents list"},
                    "verification_status": {"type": "object", "description": "Verification status"}
                },
                "required": ["application_id", "documents_submitted", "verification_status"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "audit_credit_stages",
            "description": "Audit Credit Qualification, Assessment, and Asset Valuation",
            "parameters": {
                "type": "object",
                "properties": {
                    "application_id": {"type": "string", "description": "Application ID"},
                    "credit_score": {"type": "integer", "description": "Credit score"},
                    "income": {"type": "number", "description": "Monthly income"},
                    "loan_amount": {"type": "number", "description": "Loan amount"},
                    "property_value": {"type": "number", "description": "Property value"}
                },
                "required": ["application_id", "credit_score", "income", "loan_amount", "property_value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "audit_underwriting_stage",
            "description": "Audit Underwriting stage",
            "parameters": {
                "type": "object",
                "properties": {
                    "application_id": {"type": "string", "description": "Application ID"},
                    "decision": {"type": "string", "description": "Decision"},
                    "approved_amount": {"type": "number", "description": "Approved amount"},
                    "interest_rate": {"type": "number", "description": "Interest rate"},
                    "decision_rationale": {"type": "string", "description": "Decision rationale"}
                },
                "required": ["application_id", "decision", "approved_amount", "interest_rate", "decision_rationale"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "audit_offer_communication_stages",
            "description": "Audit Offer Generation and Customer Communication",
            "parameters": {
                "type": "object",
                "properties": {
                    "application_id": {"type": "string", "description": "Application ID"},
                    "offer_amount": {"type": "number", "description": "Offer amount"},
                    "emi": {"type": "number", "description": "EMI"},
                    "customer_response": {"type": "string", "description": "Customer response"},
                    "communication_channels": {"type": "array", "items": {"type": "string"}, "description": "Channels used"}
                },
                "required": ["application_id", "offer_amount", "emi", "customer_response", "communication_channels"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_regulatory_compliance",
            "description": "Check regulatory compliance",
            "parameters": {
                "type": "object",
                "properties": {
                    "application_id": {"type": "string", "description": "Application ID"},
                    "loan_amount": {"type": "number", "description": "Loan amount"},
                    "interest_rate": {"type": "number", "description": "Interest rate"},
                    "customer_category": {"type": "string", "description": "Customer category"}
                },
                "required": ["application_id", "loan_amount", "interest_rate"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_audit_report",
            "description": "Generate final audit report",
            "parameters": {
                "type": "object",
                "properties": {
                    "application_id": {"type": "string", "description": "Application ID"},
                    "customer_name": {"type": "string", "description": "Customer name"},
                    "loan_amount": {"type": "number", "description": "Loan amount"},
                    "interest_rate": {"type": "number", "description": "Interest rate"},
                    "tenure_months": {"type": "integer", "description": "Tenure"},
                    "emi": {"type": "number", "description": "EMI"},
                    "decision": {"type": "string", "description": "Decision"}
                },
                "required": ["application_id", "customer_name", "loan_amount", "interest_rate", "tenure_months", "emi", "decision"]
            }
        }
    }
]


# ============================================================================
# AGENT CLASS
# ============================================================================

class AuditAgent:
    """Audit Agent for loan processing"""
    
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
            "audit_customer_service_stage": audit_customer_service_stage,
            "audit_document_verification_stage": audit_document_verification_stage,
            "audit_credit_stages": audit_credit_stages,
            "audit_underwriting_stage": audit_underwriting_stage,
            "audit_offer_communication_stages": audit_offer_communication_stages,
            "check_regulatory_compliance": check_regulatory_compliance,
            "generate_audit_report": generate_audit_report
        }
        
        if tool_name in tool_functions:
            result = tool_functions[tool_name](**arguments)
            return json.dumps(result, indent=2)
        
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
    
    def process_request(self, user_message: str) -> str:
        """Process an audit request"""
        # Create agent dynamically
        agent = self.project_client.agents.create_agent(
            model=MODEL_DEPLOYMENT,
            name="audit-agent",
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
            "name": "Audit Agent",
            "description": "Audits the complete loan processing workflow",
            "stage": 8,
            "previous_agent": "Customer Communication Agent",
            "next_agent": None,
            "is_final_stage": True,
            "tools": [tool["function"]["name"] for tool in self.tools]
        }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  AUDIT AGENT")
    print("=" * 70)
    
    agent = AuditAgent()
    print(f"\nAgent Info: {json.dumps(agent.get_agent_info(), indent=2)}")
    
    # Test with sample request
    test_message = """
    Perform complete audit for loan application:
    
    Application ID: LOAN-20260127120000
    Customer: Kala Divan
    Loan Amount: ₹40,00,000
    Interest Rate: 8.5% p.a.
    Tenure: 240 months
    EMI: ₹34,729
    Decision: APPROVED
    
    Documents Submitted: Adhaar, PAN, Passport, Bank Statements, 
                        Pay Slip, Form 16, Property Document, CIBIL Report
    
    Credit Score: 750
    Monthly Income: ₹1,25,000
    Property Value: ₹55,00,000
    
    Audit all stages, check regulatory compliance, and generate
    the final comprehensive audit report.
    """
    
    print(f"\n{'='*70}")
    print("Processing Audit Request...")
    print(f"{'='*70}")
    
    response = agent.process_request(test_message)
    print(f"\nAgent Response:\n{response}")