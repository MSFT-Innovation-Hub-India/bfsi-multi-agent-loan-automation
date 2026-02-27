"""
Loan Processing Multi-Agent Orchestrator (Simplified)
=====================================================
Uses Azure AI Foundry agents with dynamic creation.

Flow: Customer Service -> Document Verification -> Credit Qualification -> 
      Credit Assessment & Asset Valuation (parallel) -> Underwriting -> 
      Offer Generation -> Customer Communication -> Audit
"""

import os
import json
from datetime import datetime
from typing import Dict, Any

# Import all agent classes
from Customerserviceagent import CustomerServiceAgent
from Documentverificationagent import DocumentVerificationAgent
from Creditqualificationagent import CreditQualificationAgent
from Creditassessmentagent import CreditAssessmentAgent
from Assetvaluationagnet import AssetValuationAgent
from Underwritingagent import UnderwritingAgent
from Offergenerationagent import OfferGenerationAgent
from Customercommunicationagent import CustomerCommunicationAgent
from Auditagent import AuditAgent

DOCUMENTS_PATH = os.path.join(os.path.dirname(__file__), "Documents")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_header(text: str, char: str = "="):
    """Print formatted header"""
    width = 70
    print(f"\n{char * width}")
    print(f"  {text}")
    print(f"{char * width}")


def print_agent_communication(from_agent: str, to_agent: str, message_preview: str):
    """Print agent-to-agent communication"""
    print(f"\n📤 [{from_agent}] → [{to_agent}]")
    print(f"   Message: {message_preview[:100]}..." if len(message_preview) > 100 else f"   Message: {message_preview}")


def print_agent_response(agent_name: str, response: str):
    """Print agent response"""
    print(f"\n📥 [{agent_name}] Response:")
    print("-" * 50)
    # Print first 500 chars of response
    if len(response) > 500:
        print(response[:500] + "...")
    else:
        print(response)
    print("-" * 50)


def get_available_documents() -> Dict[str, Any]:
    """Get list of available documents"""
    if os.path.exists(DOCUMENTS_PATH):
        documents = os.listdir(DOCUMENTS_PATH)
        return {
            "documents": documents,
            "count": len(documents),
            "path": DOCUMENTS_PATH
        }
    return {"documents": [], "count": 0, "path": DOCUMENTS_PATH}


# ============================================================================
# FOUNDRY AGENT CALLER
# ============================================================================

class FoundryAgentCaller:
    """Calls agent classes and tracks communication"""
    
    def __init__(self):
        print("🔌 Initializing agents...")
        # Instantiate all agents
        self.agents = {
            "customer_service": CustomerServiceAgent(),
            "document_verification": DocumentVerificationAgent(),
            "credit_qualification": CreditQualificationAgent(),
            "credit_assessment": CreditAssessmentAgent(),
            "asset_valuation": AssetValuationAgent(),
            "underwriting": UnderwritingAgent(),
            "offer_generation": OfferGenerationAgent(),
            "customer_communication": CustomerCommunicationAgent(),
            "audit": AuditAgent()
        }
        
        self.agent_names = {
            "customer_service": "Customer Service Agent",
            "document_verification": "Document Verification Agent",
            "credit_qualification": "Credit Qualification Agent",
            "credit_assessment": "Credit Assessment Agent",
            "asset_valuation": "Asset Valuation Agent",
            "underwriting": "Underwriting Agent",
            "offer_generation": "Offer Generation Agent",
            "customer_communication": "Customer Communication Agent",
            "audit": "Audit Agent"
        }
        
        print("✅ All agents initialized!\n")
        self.conversation_log = []
    
    def call_agent(self, agent_key: str, message: str, previous_agent: str = None) -> str:
        """Call an agent and return response"""
        agent = self.agents.get(agent_key)
        agent_name = self.agent_names.get(agent_key, agent_key)
        
        if not agent:
            return f"Error: Agent {agent_key} not found"
        
        # Log communication
        if previous_agent:
            print_agent_communication(previous_agent, agent_name, message)
        else:
            print(f"\n📨 Sending to [{agent_name}]")
        
        try:
            # Process request using agent's process_request method
            print(f"   ⏳ Processing...")
            response = agent.process_request(message)
            
            if response and response != "No response from agent":
                # Log and print response
                self.conversation_log.append({
                    "agent": agent_name,
                    "message": message[:200],
                    "response": response[:500],
                    "timestamp": datetime.now().isoformat()
                })
                
                print_agent_response(agent_name, response)
                return response
            else:
                print(f"   ⚠️ No response from agent")
                return "No response from agent"
            
        except Exception as e:
            error_msg = f"Error calling {agent_name}: {str(e)}"
            print(f"   ❌ {error_msg}")
            return error_msg


# ============================================================================
# ORCHESTRATOR
# ============================================================================

class SimpleLoanOrchestrator:
    """Simple orchestrator that shows agent-to-agent communication"""
    
    def __init__(self):
        self.caller = FoundryAgentCaller()
        self.results = {}
    
    def run(self, customer_name: str, loan_amount: float, loan_purpose: str, tenure_years: int):
        """Run the complete loan processing workflow"""
        
        application_id = f"LOAN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        docs = get_available_documents()
        
        print_header("LOAN PROCESSING ORCHESTRATOR", "═")
        print(f"""
📋 APPLICATION DETAILS:
   Application ID: {application_id}
   Customer: {customer_name}
   Loan Amount: ₹{loan_amount:,.0f}
   Purpose: {loan_purpose}
   Tenure: {tenure_years} years
   Documents Available: {docs['count']}
""")
        
        # =====================================================================
        # STAGE 1: Customer Service
        # =====================================================================
        print_header("STAGE 1: CUSTOMER SERVICE AGENT")
        
        cs_message = f"""
New loan application received:

Customer Name: {customer_name}
Loan Amount: ₹{loan_amount:,.0f}
Purpose: {loan_purpose}
Tenure: {tenure_years} years

Available Documents: {', '.join(docs['documents'])}

Please process the initial application, gather customer information,
and prepare handoff summary for Document Verification Agent.
"""
        
        cs_response = self.caller.call_agent("customer_service", cs_message)
        self.results["customer_service"] = cs_response
        
        # =====================================================================
        # STAGE 2: Document Verification
        # =====================================================================
        print_header("STAGE 2: DOCUMENT VERIFICATION AGENT")
        
        dv_message = f"""
HANDOFF FROM: Customer Service Agent
Application ID: {application_id}
Customer: {customer_name}

PREVIOUS STAGE SUMMARY:
{cs_response[:500] if len(cs_response) > 500 else cs_response}

DOCUMENTS TO VERIFY:
{', '.join(docs['documents'])}

Please verify all KYC and income documents, check for authenticity,
and prepare handoff summary for Credit Qualification Agent.
"""
        
        dv_response = self.caller.call_agent(
            "document_verification", 
            dv_message, 
            "Customer Service Agent"
        )
        self.results["document_verification"] = dv_response
        
        # =====================================================================
        # STAGE 3: Credit Qualification
        # =====================================================================
        print_header("STAGE 3: CREDIT QUALIFICATION AGENT")
        
        cq_message = f"""
HANDOFF FROM: Document Verification Agent
Application ID: {application_id}
Customer: {customer_name}
Loan Amount: ₹{loan_amount:,.0f}

PREVIOUS STAGE SUMMARY:
{dv_response[:500] if len(dv_response) > 500 else dv_response}

Please check credit eligibility, calculate FOIR, and determine if customer
qualifies for the loan. Prepare handoff for parallel Credit Assessment
and Asset Valuation.
"""
        
        cq_response = self.caller.call_agent(
            "credit_qualification",
            cq_message,
            "Document Verification Agent"
        )
        self.results["credit_qualification"] = cq_response
        
        # =====================================================================
        # STAGE 4A & 4B: Credit Assessment & Asset Valuation (PARALLEL)
        # =====================================================================
        print_header("STAGE 4: PARALLEL EXECUTION", "▓")
        print("   Running Credit Assessment and Asset Valuation in parallel...")
        
        # Stage 4A: Credit Assessment
        print_header("STAGE 4A: CREDIT ASSESSMENT AGENT", "-")
        
        ca_message = f"""
HANDOFF FROM: Credit Qualification Agent (PARALLEL BRANCH A)
Application ID: {application_id}
Customer: {customer_name}

PREVIOUS STAGE SUMMARY:
{cq_response[:400] if len(cq_response) > 400 else cq_response}

CIBIL Report available in documents.
Please analyze credit score, payment history, calculate risk score,
and prepare credit assessment report for Underwriting Agent.
"""
        
        ca_response = self.caller.call_agent(
            "credit_assessment",
            ca_message,
            "Credit Qualification Agent"
        )
        self.results["credit_assessment"] = ca_response
        
        # Stage 4B: Asset Valuation
        print_header("STAGE 4B: ASSET VALUATION AGENT", "-")
        
        av_message = f"""
HANDOFF FROM: Credit Qualification Agent (PARALLEL BRANCH B)
Application ID: {application_id}
Customer: {customer_name}
Loan Amount Requested: ₹{loan_amount:,.0f}

PREVIOUS STAGE SUMMARY:
{cq_response[:400] if len(cq_response) > 400 else cq_response}

Property Document available.
Please verify property documents, calculate property value, LTV ratio,
and prepare asset valuation report for Underwriting Agent.
"""
        
        av_response = self.caller.call_agent(
            "asset_valuation",
            av_message,
            "Credit Qualification Agent"
        )
        self.results["asset_valuation"] = av_response
        
        print_header("PARALLEL EXECUTION COMPLETE", "▓")
        
        # =====================================================================
        # STAGE 5: Underwriting
        # =====================================================================
        print_header("STAGE 5: UNDERWRITING AGENT")
        
        uw_message = f"""
HANDOFF FROM: Credit Assessment Agent & Asset Valuation Agent
Application ID: {application_id}
Customer: {customer_name}
Loan Amount Requested: ₹{loan_amount:,.0f}

CREDIT ASSESSMENT SUMMARY:
{ca_response[:400] if len(ca_response) > 400 else ca_response}

ASSET VALUATION SUMMARY:
{av_response[:400] if len(av_response) > 400 else av_response}

Please review all assessments, calculate combined risk, make underwriting
decision (APPROVE/REJECT/REFER), and set loan terms if approved.
Prepare handoff for Offer Generation Agent.
"""
        
        uw_response = self.caller.call_agent(
            "underwriting",
            uw_message,
            "Credit Assessment + Asset Valuation Agents"
        )
        self.results["underwriting"] = uw_response
        
        # =====================================================================
        # STAGE 6: Offer Generation
        # =====================================================================
        print_header("STAGE 6: OFFER GENERATION AGENT")
        
        og_message = f"""
HANDOFF FROM: Underwriting Agent
Application ID: {application_id}
Customer: {customer_name}

UNDERWRITING DECISION SUMMARY:
{uw_response[:500] if len(uw_response) > 500 else uw_response}

If approved, please calculate EMI, generate amortization schedule,
create formal offer letter with all terms and conditions.
Prepare handoff for Customer Communication Agent.
"""
        
        og_response = self.caller.call_agent(
            "offer_generation",
            og_message,
            "Underwriting Agent"
        )
        self.results["offer_generation"] = og_response
        
        # =====================================================================
        # STAGE 7: Customer Communication
        # =====================================================================
        print_header("STAGE 7: CUSTOMER COMMUNICATION AGENT")
        
        cc_message = f"""
HANDOFF FROM: Offer Generation Agent
Application ID: {application_id}
Customer: {customer_name}

OFFER DETAILS:
{og_response[:500] if len(og_response) > 500 else og_response}

Please send loan offer to customer via email and SMS,
explain terms, record customer response, and schedule follow-up if needed.
Prepare handoff for Audit Agent.
"""
        
        cc_response = self.caller.call_agent(
            "customer_communication",
            cc_message,
            "Offer Generation Agent"
        )
        self.results["customer_communication"] = cc_response
        
        # =====================================================================
        # STAGE 8: Audit
        # =====================================================================
        print_header("STAGE 8: AUDIT AGENT")
        
        audit_message = f"""
HANDOFF FROM: Customer Communication Agent
Application ID: {application_id}
Customer: {customer_name}

COMPLETE WORKFLOW SUMMARY:

1. CUSTOMER SERVICE: Application received and processed
2. DOCUMENT VERIFICATION: Documents verified
3. CREDIT QUALIFICATION: Eligibility checked
4. CREDIT ASSESSMENT: Risk assessed
5. ASSET VALUATION: Property valued
6. UNDERWRITING: Decision made
7. CUSTOMER COMMUNICATION: Customer notified

Please audit the entire loan processing workflow, check compliance,
and generate final audit report with certification.
"""
        
        audit_response = self.caller.call_agent(
            "audit",
            audit_message,
            "Customer Communication Agent"
        )
        self.results["audit"] = audit_response
        
        # =====================================================================
        # FINAL SUMMARY
        # =====================================================================
        print_header("WORKFLOW COMPLETE", "═")
        
        # Determine final decision from underwriting response
        uw_response_lower = self.results.get("underwriting", "").lower()
        if "approved" in uw_response_lower or "approve" in uw_response_lower:
            final_decision = "✅ APPROVED"
            decision_color = "🟢"
        elif "rejected" in uw_response_lower or "reject" in uw_response_lower or "denied" in uw_response_lower:
            final_decision = "❌ REJECTED"
            decision_color = "🔴"
        elif "refer" in uw_response_lower or "review" in uw_response_lower:
            final_decision = "🔄 REFERRED FOR REVIEW"
            decision_color = "🟡"
        else:
            final_decision = "⏳ PENDING DECISION"
            decision_color = "🟡"
        
        # Format values for display
        loan_amount_str = f"₹{loan_amount:,.0f}"
        
        # Save results to loan_result.json
        result_data = {
            "application_id": application_id,
            "customer_name": customer_name,
            "loan_amount": loan_amount,
            "loan_purpose": loan_purpose,
            "tenure_years": tenure_years,
            "timestamp": datetime.now().isoformat(),
            "final_decision": final_decision,
            "stages": self.results,
            "conversation_log": self.caller.conversation_log
        }
        
        result_file = os.path.join(os.path.dirname(__file__), "loan_result.json")
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {result_file}")
        
        print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║                      FINAL LOAN DECISION                             ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║   Application ID: {application_id}
║   Customer: {customer_name}
║   Loan Amount: {loan_amount_str}
║   Tenure: {tenure_years} years
║                                                                      ║
║   {decision_color} DECISION: {final_decision}
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

📊 STAGE COMPLETION SUMMARY:
   ✓ Stage 1: Customer Service      - Completed
   ✓ Stage 2: Document Verification - Completed
   ✓ Stage 3: Credit Qualification  - Completed
   ✓ Stage 4A: Credit Assessment    - Completed
   ✓ Stage 4B: Asset Valuation      - Completed
   ✓ Stage 5: Underwriting          - Completed
   ✓ Stage 6: Offer Generation      - Completed
   ✓ Stage 7: Customer Communication- Completed
   ✓ Stage 8: Audit                 - Completed
""")
        
        return self.results


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║           LOAN PROCESSING MULTI-AGENT ORCHESTRATOR                   ║
║                  Azure AI Foundry Edition                            ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    orchestrator = SimpleLoanOrchestrator()
    
    result = orchestrator.run(
        customer_name="Kala Divan",
        loan_amount=4000000,  # ₹40 Lakhs
        loan_purpose="Home Loan",
        tenure_years=20
    )
