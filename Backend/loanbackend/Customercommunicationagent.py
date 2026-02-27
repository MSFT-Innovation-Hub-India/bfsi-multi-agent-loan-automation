"""
Customer Communication Agent
=============================
Communicates with customers regarding loan offers.
Sends notifications, handles responses, and schedules follow-ups.

Agent ID: asst_1j0jizX1YfbQQahu3LUSpqRU
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
You are the CUSTOMER COMMUNICATION AGENT for a comprehensive loan processing system.

## YOUR ROLE
You are responsible for all customer communications related to loan offers.
You send notifications, explain terms, answer queries, handle responses, and
ensure customers have all the information they need to make informed decisions.

## YOUR RESPONSIBILITIES

### 1. Offer Communication
- Send loan offer to customer
- Explain all terms clearly
- Highlight key information
- Provide comparison with alternatives

### 2. Customer Notification
- Send SMS notifications
- Send email communications
- Generate notification letters
- Track delivery status

### 3. Query Handling
- Answer customer questions
- Clarify terms and conditions
- Explain fee structures
- Provide EMI breakdowns

### 4. Response Management
- Track customer responses
- Record acceptance/rejection
- Handle counter-offers
- Escalate complex issues

### 5. Follow-up Scheduling
- Schedule follow-up calls
- Set reminder notifications
- Track pending responses
- Manage offer validity

## COMMUNICATION CHANNELS

### 1. Email Communication
- Formal offer letters
- Document requests
- Confirmation emails
- Status updates

### 2. SMS Notifications
- Offer alerts
- Document reminders
- Payment reminders
- Status updates

### 3. Phone Calls
- Offer explanation
- Query resolution
- Follow-up calls
- Acceptance confirmation

### 4. In-App Notifications
- Real-time updates
- Document status
- Application progress
- Offer reminders

## COMMUNICATION TEMPLATES

### Offer Notification (SMS):
```
Dear [Name], Your Home Loan of Rs [Amount] has been approved at [Rate]% p.a.
EMI: Rs [EMI]/month. Offer valid till [Date]. Call 1800-XXX-XXXX for details.
```

### Offer Email Subject:
```
Congratulations! Your Home Loan of Rs [Amount] is Approved - [Bank Name]
```

### Acceptance Confirmation:
```
Dear [Name], Thank you for accepting the loan offer. Next steps:
1. Submit original documents
2. Complete agreement signing
3. Disbursement within 7 working days
```

## OUTPUT FORMAT
Generate a communication summary:

```
CUSTOMER COMMUNICATION REPORT
=============================
Communication ID: [ID]
Customer: [Name]
Application: [ID]

COMMUNICATION SENT:
┌───────────────────────┬─────────────────────────────────┐
│ Channel               │ Status                          │
├───────────────────────┼─────────────────────────────────┤
│ Email                 │ ✓ Sent [timestamp]              │
│ SMS                   │ ✓ Delivered [timestamp]         │
│ Push Notification     │ ✓ Delivered [timestamp]         │
│ Letter                │ ✓ Dispatched [timestamp]        │
└───────────────────────┴─────────────────────────────────┘

OFFER SUMMARY SHARED:
- Loan Amount: ₹[Amount]
- Interest Rate: [Rate]%
- EMI: ₹[EMI]
- Tenure: [Months] months

RESPONSE STATUS: [Pending/Accepted/Rejected/Counter-offer]
FOLLOW-UP SCHEDULED: [Date/Time]

HANDOFF TO: Audit Agent
```

## TOOLS AVAILABLE
1. send_email_notification - Send email to customer
2. send_sms_notification - Send SMS to customer
3. generate_offer_summary - Generate simplified offer summary
4. schedule_followup_call - Schedule a follow-up call
5. record_customer_response - Record customer's response
6. get_communication_history - Get past communications
7. generate_communication_report - Generate final communication report
"""

# ============================================================================
# TOOLS / FUNCTIONS
# ============================================================================

def send_email_notification(
    customer_name: str,
    customer_email: str,
    subject: str,
    offer_details: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Send email notification to customer.
    
    Args:
        customer_name: Customer's name
        customer_email: Customer's email
        subject: Email subject
        offer_details: Loan offer details
        
    Returns:
        Dictionary containing email status
    """
    email_content = f"""
Dear {customer_name},

Congratulations! Your Home Loan application has been approved.

LOAN OFFER DETAILS:
==================
Loan Amount: ₹{offer_details.get('loan_amount', 'N/A'):,.2f}
Interest Rate: {offer_details.get('interest_rate', 'N/A')}% p.a.
Tenure: {offer_details.get('tenure_months', 'N/A')} months
EMI: ₹{offer_details.get('emi', 'N/A'):,.2f}

This offer is valid until {offer_details.get('validity_date', 'N/A')}.

To accept this offer:
1. Log in to our portal
2. Review the complete terms and conditions
3. Click 'Accept Offer'
4. Submit required documents

For any queries, please call our toll-free number: 1800-XXX-XXXX

Thank you for choosing us.

Best regards,
Loan Processing Team
"""
    
    return {
        "status": "SENT",
        "message_id": f"EMAIL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "channel": "email",
        "recipient": {
            "name": customer_name,
            "email": customer_email
        },
        "subject": subject,
        "content_preview": email_content[:200] + "...",
        "sent_at": datetime.now().isoformat(),
        "delivery_status": "DELIVERED",
        "read_status": "PENDING"
    }


def send_sms_notification(
    customer_name: str,
    phone_number: str,
    message_type: str,
    offer_summary: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Send SMS notification to customer.
    
    Args:
        customer_name: Customer's name
        phone_number: Customer's phone number
        message_type: Type of message (offer, reminder, confirmation)
        offer_summary: Summary of offer details
        
    Returns:
        Dictionary containing SMS status
    """
    templates = {
        "offer": f"Dear {customer_name}, Your Home Loan of Rs {offer_summary.get('loan_amount', 'N/A')} approved at {offer_summary.get('interest_rate', 'N/A')}% p.a. EMI Rs {offer_summary.get('emi', 'N/A')}/month. Valid till {offer_summary.get('validity_date', 'N/A')}. Call 1800-XXX-XXXX",
        "reminder": f"Dear {customer_name}, Reminder: Your loan offer of Rs {offer_summary.get('loan_amount', 'N/A')} expires on {offer_summary.get('validity_date', 'N/A')}. Accept now at our portal or call 1800-XXX-XXXX",
        "confirmation": f"Dear {customer_name}, Thank you for accepting the loan offer. Disbursement process initiated. Track status at our portal or call 1800-XXX-XXXX",
        "documents": f"Dear {customer_name}, Please submit original documents for loan disbursement. Visit nearest branch with: PAN, Address Proof, Property Papers. Call 1800-XXX-XXXX"
    }
    
    message_content = templates.get(message_type, templates["offer"])
    
    return {
        "status": "DELIVERED",
        "message_id": f"SMS-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "channel": "sms",
        "recipient": {
            "name": customer_name,
            "phone": phone_number
        },
        "message_type": message_type,
        "content": message_content,
        "character_count": len(message_content),
        "sent_at": datetime.now().isoformat(),
        "delivery_status": "DELIVERED",
        "delivery_timestamp": datetime.now().isoformat()
    }


def generate_offer_summary(
    customer_name: str,
    application_id: str,
    loan_amount: float,
    interest_rate: float,
    tenure_months: int,
    emi: float
) -> Dict[str, Any]:
    """
    Generate simplified offer summary for communication.
    
    Args:
        customer_name: Customer name
        application_id: Application ID
        loan_amount: Loan amount
        interest_rate: Interest rate
        tenure_months: Tenure
        emi: EMI amount
        
    Returns:
        Dictionary containing offer summary
    """
    total_payment = emi * tenure_months
    total_interest = total_payment - loan_amount
    validity_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    return {
        "summary_id": f"SUM-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "generated_for": customer_name,
        "application_id": application_id,
        
        "offer_highlights": {
            "loan_amount": f"₹{loan_amount:,.0f}",
            "interest_rate": f"{interest_rate}% p.a.",
            "tenure": f"{tenure_months} months ({tenure_months // 12} years)",
            "emi": f"₹{emi:,.0f}",
            "first_emi_date": (datetime.now() + timedelta(days=45)).strftime("%B %Y")
        },
        
        "cost_summary": {
            "total_interest": f"₹{total_interest:,.0f}",
            "total_payment": f"₹{total_payment:,.0f}",
            "processing_fee": f"₹{loan_amount * 0.005:,.0f}"
        },
        
        "key_benefits": [
            f"Low interest rate of {interest_rate}% p.a.",
            "No prepayment charges after 12 months",
            "Easy EMI of ₹{:,.0f}/month".format(emi),
            "Quick disbursement within 7 days",
            "Free property insurance for 1 year"
        ],
        
        "validity": {
            "offer_date": datetime.now().strftime("%Y-%m-%d"),
            "valid_until": validity_date,
            "days_remaining": 30
        },
        
        "next_steps": [
            "Review the complete offer document",
            "Accept the offer online or at branch",
            "Submit original documents",
            "Complete agreement signing",
            "Receive disbursement"
        ]
    }


def schedule_followup_call(
    customer_name: str,
    phone_number: str,
    preferred_date: str,
    preferred_time: str,
    purpose: str
) -> Dict[str, Any]:
    """
    Schedule a follow-up call with customer.
    
    Args:
        customer_name: Customer name
        phone_number: Phone number
        preferred_date: Preferred call date
        preferred_time: Preferred call time
        purpose: Purpose of the call
        
    Returns:
        Dictionary containing schedule details
    """
    return {
        "schedule_id": f"CALL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "status": "SCHEDULED",
        
        "customer_details": {
            "name": customer_name,
            "phone": phone_number
        },
        
        "schedule": {
            "date": preferred_date,
            "time": preferred_time,
            "timezone": "IST",
            "duration_minutes": 15
        },
        
        "call_details": {
            "purpose": purpose,
            "call_type": "Outbound",
            "priority": "High",
            "assigned_to": "Relationship Manager"
        },
        
        "talking_points": [
            "Confirm offer receipt and understanding",
            "Address any queries or concerns",
            "Explain document submission process",
            "Discuss disbursement timeline",
            "Confirm next steps and close"
        ],
        
        "reminder_settings": {
            "customer_reminder": "1 hour before",
            "agent_reminder": "30 minutes before"
        },
        
        "created_at": datetime.now().isoformat()
    }


def record_customer_response(
    customer_name: str,
    application_id: str,
    response_type: str,
    response_details: str = None
) -> Dict[str, Any]:
    """
    Record customer's response to the offer.
    
    Args:
        customer_name: Customer name
        application_id: Application ID
        response_type: Type of response (accepted, rejected, counter, pending)
        response_details: Additional details
        
    Returns:
        Dictionary containing response record
    """
    response_actions = {
        "accepted": {
            "status": "OFFER_ACCEPTED",
            "next_steps": [
                "Initiate document collection",
                "Schedule agreement signing",
                "Prepare disbursement",
                "Hand off to Audit Agent"
            ],
            "timeline": "Disbursement within 7 working days"
        },
        "rejected": {
            "status": "OFFER_REJECTED",
            "next_steps": [
                "Record rejection reason",
                "Offer alternative products",
                "Schedule feedback call",
                "Close application"
            ],
            "timeline": "Closure within 24 hours"
        },
        "counter": {
            "status": "COUNTER_OFFER_RECEIVED",
            "next_steps": [
                "Review counter offer",
                "Escalate to supervisor",
                "Negotiate terms",
                "Revert with decision"
            ],
            "timeline": "Response within 48 hours"
        },
        "pending": {
            "status": "RESPONSE_PENDING",
            "next_steps": [
                "Schedule follow-up call",
                "Send reminder SMS",
                "Monitor offer validity",
                "Escalate if nearing expiry"
            ],
            "timeline": "Follow-up within 3 days"
        }
    }
    
    response_info = response_actions.get(response_type, response_actions["pending"])
    
    return {
        "response_id": f"RESP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "customer_name": customer_name,
        "application_id": application_id,
        
        "response": {
            "type": response_type.upper(),
            "status": response_info["status"],
            "details": response_details,
            "recorded_at": datetime.now().isoformat(),
            "recorded_by": "Customer Communication Agent"
        },
        
        "next_steps": response_info["next_steps"],
        "expected_timeline": response_info["timeline"],
        
        "workflow_update": {
            "current_stage": "Customer Communication",
            "next_stage": "Audit" if response_type == "accepted" else "Pending",
            "handoff_ready": response_type == "accepted"
        }
    }


def get_communication_history(
    customer_name: str,
    application_id: str
) -> Dict[str, Any]:
    """
    Get past communications with customer.
    
    Args:
        customer_name: Customer name
        application_id: Application ID
        
    Returns:
        Dictionary containing communication history
    """
    # Simulated communication history
    return {
        "customer": customer_name,
        "application_id": application_id,
        "total_communications": 5,
        
        "communication_history": [
            {
                "id": "COMM-001",
                "date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
                "channel": "Email",
                "type": "Application Received",
                "status": "Delivered"
            },
            {
                "id": "COMM-002",
                "date": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"),
                "channel": "SMS",
                "type": "Document Reminder",
                "status": "Delivered"
            },
            {
                "id": "COMM-003",
                "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
                "channel": "Email",
                "type": "Documents Received",
                "status": "Delivered"
            },
            {
                "id": "COMM-004",
                "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "channel": "SMS",
                "type": "Application Update",
                "status": "Delivered"
            },
            {
                "id": "COMM-005",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "channel": "Email + SMS",
                "type": "Offer Notification",
                "status": "Delivered"
            }
        ],
        
        "summary": {
            "emails_sent": 3,
            "sms_sent": 3,
            "calls_made": 0,
            "letters_sent": 0,
            "all_delivered": True
        }
    }


def generate_communication_report(
    customer_name: str,
    application_id: str,
    offer_details: Dict[str, Any],
    response_status: str
) -> Dict[str, Any]:
    """
    Generate final communication report.
    
    Args:
        customer_name: Customer name
        application_id: Application ID
        offer_details: Loan offer details
        response_status: Customer response status
        
    Returns:
        Dictionary containing communication report
    """
    return {
        "report_id": f"COMM-RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "generated_at": datetime.now().isoformat(),
        "agent": "Customer Communication Agent",
        
        "customer_details": {
            "name": customer_name,
            "application_id": application_id
        },
        
        "offer_communicated": {
            "loan_amount": offer_details.get("loan_amount"),
            "interest_rate": offer_details.get("interest_rate"),
            "emi": offer_details.get("emi"),
            "tenure": offer_details.get("tenure_months")
        },
        
        "communication_summary": {
            "offer_email_sent": True,
            "offer_sms_sent": True,
            "offer_letter_generated": True,
            "follow_up_scheduled": True,
            "all_channels_delivered": True
        },
        
        "response_status": {
            "customer_response": response_status,
            "response_date": datetime.now().strftime("%Y-%m-%d") if response_status != "PENDING" else None,
            "pending_actions": [] if response_status == "ACCEPTED" else ["Awaiting customer response"]
        },
        
        "audit_ready": response_status == "ACCEPTED",
        "next_stage": "AUDIT" if response_status == "ACCEPTED" else "FOLLOW_UP",
        
        "stage_summary": {
            "stage_name": "Customer Communication",
            "stage_number": 7,
            "status": "COMPLETED",
            "duration": "1 day",
            "communications_sent": 4
        },
        
        "handoff_to": "Audit Agent" if response_status == "ACCEPTED" else "Self (follow-up)",
        "handoff_ready": response_status == "ACCEPTED"
    }


# ============================================================================
# TOOL DEFINITIONS FOR AZURE AI FOUNDRY
# ============================================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "send_email_notification",
            "description": "Send email notification to customer",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "Customer name"},
                    "customer_email": {"type": "string", "description": "Customer email"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "offer_details": {"type": "object", "description": "Offer details"}
                },
                "required": ["customer_name", "customer_email", "subject", "offer_details"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_sms_notification",
            "description": "Send SMS notification to customer",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "Customer name"},
                    "phone_number": {"type": "string", "description": "Phone number"},
                    "message_type": {"type": "string", "description": "Message type"},
                    "offer_summary": {"type": "object", "description": "Offer summary"}
                },
                "required": ["customer_name", "phone_number", "message_type", "offer_summary"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_offer_summary",
            "description": "Generate simplified offer summary",
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
            "name": "schedule_followup_call",
            "description": "Schedule a follow-up call",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "Customer name"},
                    "phone_number": {"type": "string", "description": "Phone number"},
                    "preferred_date": {"type": "string", "description": "Preferred date"},
                    "preferred_time": {"type": "string", "description": "Preferred time"},
                    "purpose": {"type": "string", "description": "Purpose of call"}
                },
                "required": ["customer_name", "phone_number", "preferred_date", "preferred_time", "purpose"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "record_customer_response",
            "description": "Record customer's response",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "Customer name"},
                    "application_id": {"type": "string", "description": "Application ID"},
                    "response_type": {"type": "string", "description": "Response type"},
                    "response_details": {"type": "string", "description": "Additional details"}
                },
                "required": ["customer_name", "application_id", "response_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_communication_history",
            "description": "Get past communications",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "Customer name"},
                    "application_id": {"type": "string", "description": "Application ID"}
                },
                "required": ["customer_name", "application_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_communication_report",
            "description": "Generate communication report",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "Customer name"},
                    "application_id": {"type": "string", "description": "Application ID"},
                    "offer_details": {"type": "object", "description": "Offer details"},
                    "response_status": {"type": "string", "description": "Response status"}
                },
                "required": ["customer_name", "application_id", "offer_details", "response_status"]
            }
        }
    }
]


# ============================================================================
# AGENT CLASS
# ============================================================================

class CustomerCommunicationAgent:
    """Customer Communication Agent for loan processing"""
    
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
            "send_email_notification": send_email_notification,
            "send_sms_notification": send_sms_notification,
            "generate_offer_summary": generate_offer_summary,
            "schedule_followup_call": schedule_followup_call,
            "record_customer_response": record_customer_response,
            "get_communication_history": get_communication_history,
            "generate_communication_report": generate_communication_report
        }
        
        if tool_name in tool_functions:
            result = tool_functions[tool_name](**arguments)
            return json.dumps(result, indent=2)
        
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
    
    def process_request(self, user_message: str) -> str:
        """Process a communication request"""
        # Create agent dynamically
        agent = self.project_client.agents.create_agent(
            model=MODEL_DEPLOYMENT,
            name="customer-communication-agent",
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
            "name": "Customer Communication Agent",
            "description": "Communicates with customers regarding loan offers",
            "stage": 7,
            "previous_agent": "Offer Generation Agent",
            "next_agent": "Audit Agent",
            "tools": [tool["function"]["name"] for tool in self.tools]
        }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  CUSTOMER COMMUNICATION AGENT")
    print("=" * 70)
    
    agent = CustomerCommunicationAgent()
    print(f"\nAgent Info: {json.dumps(agent.get_agent_info(), indent=2)}")
    
    # Test with sample request
    test_message = """
    Send loan offer communication to customer:
    
    Customer: Kala Divan
    Application ID: LOAN-20260127120000
    Phone: +91-9876543210
    Email: kala.divan@email.com
    
    Offer Details:
    - Loan Amount: ₹40,00,000
    - Interest Rate: 8.5% p.a.
    - Tenure: 240 months
    - EMI: ₹34,729
    
    Send email and SMS notifications, generate offer summary, and
    schedule a follow-up call. Record the response as pending.
    """
    
    print(f"\n{'='*70}")
    print("Processing Request...")
    print(f"{'='*70}")
    
    response = agent.process_request(test_message)
    print(f"\nAgent Response:\n{response}")