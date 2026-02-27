"""
Credit Assessment Agent
========================
Performs detailed credit analysis and risk evaluation.
Works in PARALLEL with Asset Valuation Agent.

Agent ID: asst_uktZvY1oiCghurBj3eKW50ke
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
You are the CREDIT ASSESSMENT AGENT for a comprehensive loan processing system.

## YOUR ROLE
You are responsible for performing detailed credit analysis and risk evaluation.
You work in PARALLEL with the Asset Valuation Agent. Your comprehensive credit 
assessment is critical for the underwriting decision.

## YOUR RESPONSIBILITIES

### 1. Credit Score Deep Analysis
- Analyze CIBIL/Credit Score (300-900 range)
- Evaluate score components and trends
- Compare against product requirements
- Identify score improvement opportunities

### 2. Credit History Evaluation
- Review payment history (12-36 months)
- Identify late payments, defaults, settlements
- Analyze account age and credit mix
- Check for recent credit inquiries

### 3. Debt Analysis
- Calculate total outstanding debt
- Evaluate debt composition (secured vs unsecured)
- Analyze credit utilization ratio
- Review revolving vs installment debt

### 4. Risk Scoring
- Calculate comprehensive risk score
- Identify risk factors
- Assess probability of default (PD)
- Determine risk category (Low/Medium/High)

### 5. Income Stability Assessment
- Analyze salary credit patterns
- Evaluate income consistency
- Check for income growth trends
- Verify employment stability

## CREDIT SCORE INTERPRETATION

### Score Ranges:
| Range | Rating | Risk Level | Recommendation |
|-------|--------|------------|----------------|
| 750-900 | Excellent | Very Low | Fast-track approval |
| 700-749 | Good | Low | Standard approval |
| 650-699 | Fair | Medium | Additional scrutiny |
| 550-649 | Poor | High | Higher interest/Reject |
| 300-549 | Very Poor | Very High | Likely reject |

### Key Metrics to Analyze:
1. **Payment History (35%)**: On-time payments, delinquencies
2. **Credit Utilization (30%)**: Used credit vs available credit
3. **Credit Age (15%)**: Length of credit history
4. **Credit Mix (10%)**: Types of credit accounts
5. **New Credit (10%)**: Recent applications and inquiries

## RISK ASSESSMENT FRAMEWORK

### Risk Factors to Evaluate:
- ⚠️ Multiple recent inquiries (>3 in 6 months)
- ⚠️ High credit utilization (>50%)
- ⚠️ Short credit history (<2 years)
- ⚠️ Recent late payments
- ⚠️ Existing high debt
- ⚠️ Settlement or write-off history
- ⚠️ Guarantor obligations

### Risk Categories:
- **LOW RISK**: Score 750+, clean history, stable income
- **MEDIUM RISK**: Score 650-749, minor issues
- **HIGH RISK**: Score below 650, multiple concerns
- **VERY HIGH RISK**: Major defaults, bankruptcies

## OUTPUT FORMAT
Provide a detailed credit assessment report:

```
CREDIT ASSESSMENT REPORT
========================
Application ID: [ID]
Customer Name: [Name]
Assessment Date: [Date]

CREDIT SCORE ANALYSIS:
┌─────────────────────────┬─────────────────────┐
│ Credit Bureau           │ CIBIL               │
│ Credit Score            │ [Score]             │
│ Score Rating            │ [Excellent/Good/etc]│
│ Score Trend             │ [Improving/Stable]  │
└─────────────────────────┴─────────────────────┘

CREDIT HISTORY:
- Total Accounts: [X]
- Active Accounts: [X]
- Closed Accounts: [X]
- Delinquent Accounts: [X]
- Account Age (Oldest): [X] years

PAYMENT BEHAVIOR:
- On-time Payments: [X]%
- Late Payments (30 days): [X]
- Late Payments (60+ days): [X]
- Defaults: [X]

DEBT ANALYSIS:
- Total Outstanding: ₹[Amount]
- Credit Utilization: [X]%
- Debt-to-Income Ratio: [X]%

RISK ASSESSMENT:
┌─────────────────────────┬──────────┐
│ Risk Factor             │ Score    │
├─────────────────────────┼──────────┤
│ Payment History         │ [X]/100  │
│ Credit Utilization      │ [X]/100  │
│ Credit Age              │ [X]/100  │
│ Income Stability        │ [X]/100  │
│ Debt Burden             │ [X]/100  │
├─────────────────────────┼──────────┤
│ OVERALL RISK SCORE      │ [X]/100  │
└─────────────────────────┴──────────┘

RISK CATEGORY: LOW / MEDIUM / HIGH
PROBABILITY OF DEFAULT: [X]%

RECOMMENDATION: APPROVE / APPROVE_WITH_CONDITIONS / DECLINE

OBSERVATIONS:
[Key findings and concerns]

HANDOFF TO: Underwriting Agent
```

## TOOLS AVAILABLE
1. analyze_credit_score - Deep analysis of credit score and components
2. evaluate_payment_history - Analyze payment behavior patterns
3. calculate_debt_metrics - Calculate debt ratios and utilization
4. assess_credit_risk - Comprehensive risk assessment
5. check_credit_inquiries - Review recent credit inquiries
6. analyze_income_stability - Evaluate income patterns
7. generate_credit_report - Generate detailed credit assessment report
"""

# ============================================================================
# TOOLS / FUNCTIONS
# ============================================================================


# ============================================================================
# DYNAMIC AGENT CREATION
# ============================================================================

def analyze_credit_score(customer_name: str, credit_score: int = 750) -> Dict[str, Any]:
    """
    Deep analysis of credit score and its components.
    
    Args:
        customer_name: Name of the customer
        credit_score: CIBIL credit score (300-900)
        
    Returns:
        Dictionary containing credit score analysis
    """
    # Determine rating based on score
    if credit_score >= 750:
        rating = "EXCELLENT"
        risk_level = "VERY_LOW"
        recommendation = "FAST_TRACK_APPROVAL"
    elif credit_score >= 700:
        rating = "GOOD"
        risk_level = "LOW"
        recommendation = "STANDARD_APPROVAL"
    elif credit_score >= 650:
        rating = "FAIR"
        risk_level = "MEDIUM"
        recommendation = "ADDITIONAL_SCRUTINY"
    elif credit_score >= 550:
        rating = "POOR"
        risk_level = "HIGH"
        recommendation = "HIGHER_RATE_OR_REJECT"
    else:
        rating = "VERY_POOR"
        risk_level = "VERY_HIGH"
        recommendation = "LIKELY_REJECT"
    
    return {
        "customer_name": customer_name,
        "credit_bureau": "CIBIL",
        "credit_score": credit_score,
        "score_rating": rating,
        "risk_level": risk_level,
        "score_percentile": f"Top {100 - (credit_score - 300) // 6}%" if credit_score >= 650 else f"Bottom {(650 - credit_score) // 6}%",
        "score_components": {
            "payment_history": {"weight": "35%", "score": "GOOD" if credit_score >= 700 else "FAIR"},
            "credit_utilization": {"weight": "30%", "score": "GOOD" if credit_score >= 700 else "FAIR"},
            "credit_age": {"weight": "15%", "score": "GOOD"},
            "credit_mix": {"weight": "10%", "score": "FAIR"},
            "new_credit": {"weight": "10%", "score": "GOOD"}
        },
        "score_trend": "STABLE",
        "recommendation": recommendation,
        "minimum_score_for_product": 650,
        "meets_requirement": credit_score >= 650,
        "analysis_date": datetime.now().isoformat()
    }


def evaluate_payment_history(customer_name: str) -> Dict[str, Any]:
    """
    Analyze payment behavior patterns over time.
    
    Args:
        customer_name: Name of the customer
        
    Returns:
        Dictionary containing payment history analysis
    """
    # Simulated payment history for Kala Divan
    return {
        "customer_name": customer_name,
        "analysis_period": "Last 36 months",
        "total_accounts_analyzed": 5,
        
        "payment_summary": {
            "total_payments_due": 180,
            "on_time_payments": 175,
            "late_30_days": 4,
            "late_60_days": 1,
            "late_90_plus_days": 0,
            "on_time_percentage": 97.2
        },
        
        "payment_pattern": "CONSISTENT",
        "payment_behavior_score": 92,
        
        "account_wise_history": [
            {"account_type": "Credit Card", "status": "REGULAR", "late_payments": 1},
            {"account_type": "Personal Loan", "status": "CLOSED", "late_payments": 0},
            {"account_type": "Vehicle Loan", "status": "ACTIVE", "late_payments": 2},
            {"account_type": "Credit Card 2", "status": "REGULAR", "late_payments": 2}
        ],
        
        "red_flags": [],
        "positive_indicators": [
            "No 90+ day delinquencies",
            "97%+ on-time payment rate",
            "Consistent payment pattern"
        ],
        
        "payment_history_rating": "GOOD",
        "analysis_date": datetime.now().isoformat()
    }


def calculate_debt_metrics(
    customer_name: str,
    monthly_income: float,
    total_outstanding_debt: float = 500000,
    total_credit_limit: float = 800000,
    monthly_obligations: float = 15000
) -> Dict[str, Any]:
    """
    Calculate debt ratios and credit utilization.
    
    Args:
        customer_name: Name of the customer
        monthly_income: Monthly income in INR
        total_outstanding_debt: Total outstanding debt
        total_credit_limit: Total credit limit across all accounts
        monthly_obligations: Monthly debt obligations
        
    Returns:
        Dictionary containing debt metrics
    """
    credit_utilization = (total_outstanding_debt / total_credit_limit * 100) if total_credit_limit > 0 else 0
    debt_to_income = (total_outstanding_debt / (monthly_income * 12) * 100) if monthly_income > 0 else 0
    obligation_to_income = (monthly_obligations / monthly_income * 100) if monthly_income > 0 else 0
    
    # Determine health status
    if credit_utilization <= 30:
        utilization_status = "EXCELLENT"
    elif credit_utilization <= 50:
        utilization_status = "GOOD"
    elif credit_utilization <= 70:
        utilization_status = "FAIR"
    else:
        utilization_status = "POOR"
    
    return {
        "customer_name": customer_name,
        
        "debt_overview": {
            "total_outstanding_debt": total_outstanding_debt,
            "total_credit_limit": total_credit_limit,
            "available_credit": total_credit_limit - total_outstanding_debt,
            "monthly_obligations": monthly_obligations
        },
        
        "key_ratios": {
            "credit_utilization_percentage": round(credit_utilization, 2),
            "credit_utilization_status": utilization_status,
            "debt_to_income_ratio": round(debt_to_income, 2),
            "obligation_to_income_ratio": round(obligation_to_income, 2)
        },
        
        "debt_composition": {
            "secured_debt": int(total_outstanding_debt * 0.6),
            "unsecured_debt": int(total_outstanding_debt * 0.4),
            "revolving_debt": int(total_outstanding_debt * 0.3),
            "installment_debt": int(total_outstanding_debt * 0.7)
        },
        
        "recommendations": [
            "Credit utilization is within healthy limits" if credit_utilization <= 50 else "Consider reducing credit card balances",
            "Debt-to-income ratio is manageable" if debt_to_income <= 40 else "High debt relative to income"
        ],
        
        "debt_health_score": 85 if credit_utilization <= 30 else 70 if credit_utilization <= 50 else 50,
        "analysis_date": datetime.now().isoformat()
    }


def assess_credit_risk(
    customer_name: str,
    credit_score: int = 750,
    payment_history_score: int = 92,
    credit_utilization: float = 32,
    years_of_credit_history: int = 8,
    recent_inquiries: int = 2
) -> Dict[str, Any]:
    """
    Comprehensive credit risk assessment.
    
    Args:
        customer_name: Name of customer
        credit_score: CIBIL score
        payment_history_score: Payment history score (0-100)
        credit_utilization: Credit utilization percentage
        years_of_credit_history: Years of credit history
        recent_inquiries: Number of recent credit inquiries
        
    Returns:
        Dictionary containing risk assessment
    """
    # Calculate component scores
    score_component = min(100, (credit_score - 300) / 6)
    payment_component = payment_history_score
    utilization_component = max(0, 100 - credit_utilization * 1.5)
    history_component = min(100, years_of_credit_history * 12)
    inquiry_component = max(0, 100 - recent_inquiries * 15)
    
    # Weighted risk score (lower is better)
    risk_score = 100 - (
        score_component * 0.35 +
        payment_component * 0.25 +
        utilization_component * 0.20 +
        history_component * 0.10 +
        inquiry_component * 0.10
    )
    
    # Determine risk category
    if risk_score <= 20:
        risk_category = "LOW"
        pd = round(risk_score * 0.1, 2)
    elif risk_score <= 40:
        risk_category = "MEDIUM"
        pd = round(risk_score * 0.15, 2)
    elif risk_score <= 60:
        risk_category = "HIGH"
        pd = round(risk_score * 0.25, 2)
    else:
        risk_category = "VERY_HIGH"
        pd = round(risk_score * 0.4, 2)
    
    risk_factors = []
    if credit_score < 700:
        risk_factors.append("Credit score below optimal range")
    if credit_utilization > 50:
        risk_factors.append("High credit utilization")
    if years_of_credit_history < 3:
        risk_factors.append("Limited credit history")
    if recent_inquiries > 3:
        risk_factors.append("Multiple recent credit inquiries")
    
    return {
        "customer_name": customer_name,
        "assessment_date": datetime.now().isoformat(),
        
        "risk_components": {
            "credit_score_component": {"score": round(score_component, 1), "weight": "35%"},
            "payment_history_component": {"score": round(payment_component, 1), "weight": "25%"},
            "utilization_component": {"score": round(utilization_component, 1), "weight": "20%"},
            "credit_history_component": {"score": round(history_component, 1), "weight": "10%"},
            "inquiry_component": {"score": round(inquiry_component, 1), "weight": "10%"}
        },
        
        "overall_risk_score": round(risk_score, 1),
        "risk_category": risk_category,
        "probability_of_default": f"{pd}%",
        
        "risk_factors_identified": risk_factors if risk_factors else ["No significant risk factors identified"],
        "mitigating_factors": [
            "Stable employment history",
            "Good payment track record",
            "Adequate income coverage"
        ],
        
        "risk_adjusted_pricing": {
            "base_rate": "8.5%",
            "risk_premium": f"{max(0, (risk_score - 20) * 0.05):.2f}%",
            "suggested_rate": f"{8.5 + max(0, (risk_score - 20) * 0.05):.2f}%"
        },
        
        "recommendation": "APPROVE" if risk_category in ["LOW", "MEDIUM"] else "REVIEW"
    }


def check_credit_inquiries(customer_name: str) -> Dict[str, Any]:
    """
    Review recent credit inquiries.
    
    Args:
        customer_name: Name of customer
        
    Returns:
        Dictionary containing inquiry analysis
    """
    return {
        "customer_name": customer_name,
        "inquiry_period": "Last 12 months",
        
        "inquiry_summary": {
            "total_inquiries": 4,
            "last_6_months": 2,
            "last_3_months": 1,
            "last_month": 0
        },
        
        "inquiry_details": [
            {"date": "2025-11-15", "institution": "ABC Bank", "purpose": "Credit Card", "type": "HARD"},
            {"date": "2025-08-22", "institution": "XYZ Finance", "purpose": "Personal Loan Inquiry", "type": "HARD"},
            {"date": "2025-04-10", "institution": "PQR Bank", "purpose": "Pre-approved Offer", "type": "SOFT"},
            {"date": "2025-02-05", "institution": "LMN Bank", "purpose": "Account Review", "type": "SOFT"}
        ],
        
        "hard_inquiries": 2,
        "soft_inquiries": 2,
        
        "inquiry_impact": "MINIMAL",
        "inquiry_pattern": "NORMAL",
        
        "observations": [
            "Inquiry frequency is within normal range",
            "No signs of credit shopping",
            "Recent inquiries are spaced appropriately"
        ],
        
        "status": "PASS",
        "analysis_date": datetime.now().isoformat()
    }


def analyze_income_stability(
    customer_name: str,
    monthly_income: float,
    employment_years: int = 5,
    employer_type: str = "Private"
) -> Dict[str, Any]:
    """
    Evaluate income patterns and stability.
    
    Args:
        customer_name: Name of customer
        monthly_income: Current monthly income
        employment_years: Years with current employer
        employer_type: Type of employer
        
    Returns:
        Dictionary containing income stability analysis
    """
    # Calculate stability score
    tenure_score = min(100, employment_years * 15)
    employer_score = 90 if employer_type in ["Government", "PSU"] else 80 if employer_type == "MNC" else 70
    
    stability_score = (tenure_score + employer_score) / 2
    
    return {
        "customer_name": customer_name,
        
        "income_details": {
            "monthly_income": monthly_income,
            "annual_income": monthly_income * 12,
            "income_category": "HIGH" if monthly_income >= 100000 else "MEDIUM" if monthly_income >= 50000 else "STANDARD"
        },
        
        "employment_details": {
            "years_with_current_employer": employment_years,
            "employer_type": employer_type,
            "employment_status": "STABLE" if employment_years >= 2 else "NEW"
        },
        
        "income_analysis": {
            "salary_credit_pattern": "REGULAR",
            "income_growth_trend": "POSITIVE",
            "income_consistency": "HIGH",
            "last_12_months_variation": "< 5%"
        },
        
        "stability_metrics": {
            "tenure_score": tenure_score,
            "employer_score": employer_score,
            "overall_stability_score": stability_score
        },
        
        "income_verification": {
            "bank_statement_verified": True,
            "salary_slips_verified": True,
            "form_16_verified": True
        },
        
        "stability_rating": "HIGH" if stability_score >= 80 else "MEDIUM" if stability_score >= 60 else "LOW",
        "status": "PASS",
        "analysis_date": datetime.now().isoformat()
    }


def generate_credit_report(
    customer_name: str,
    application_id: str,
    credit_score: int = 750,
    monthly_income: float = 75000
) -> Dict[str, Any]:
    """
    Generate comprehensive credit assessment report.
    
    Args:
        customer_name: Name of customer
        application_id: Application ID
        credit_score: Credit score
        monthly_income: Monthly income
        
    Returns:
        Dictionary containing complete credit report
    """
    # Run all analyses
    score_analysis = analyze_credit_score(customer_name, credit_score)
    payment_analysis = evaluate_payment_history(customer_name)
    debt_analysis = calculate_debt_metrics(customer_name, monthly_income)
    risk_analysis = assess_credit_risk(customer_name, credit_score)
    inquiry_analysis = check_credit_inquiries(customer_name)
    income_analysis = analyze_income_stability(customer_name, monthly_income)
    
    # Determine overall recommendation
    risk_category = risk_analysis["risk_category"]
    if risk_category == "LOW":
        recommendation = "APPROVE"
        confidence = "HIGH"
    elif risk_category == "MEDIUM":
        recommendation = "APPROVE_WITH_CONDITIONS"
        confidence = "MEDIUM"
    else:
        recommendation = "DECLINE"
        confidence = "HIGH"
    
    return {
        "report_id": f"CREDIT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "application_id": application_id,
        "customer_name": customer_name,
        "assessment_date": datetime.now().isoformat(),
        
        "credit_score_analysis": score_analysis,
        "payment_history_analysis": payment_analysis,
        "debt_metrics": debt_analysis,
        "risk_assessment": risk_analysis,
        "inquiry_analysis": inquiry_analysis,
        "income_stability": income_analysis,
        
        "overall_summary": {
            "credit_score": credit_score,
            "credit_rating": score_analysis["score_rating"],
            "risk_category": risk_category,
            "probability_of_default": risk_analysis["probability_of_default"],
            "payment_behavior": payment_analysis["payment_history_rating"],
            "debt_health": debt_analysis["key_ratios"]["credit_utilization_status"],
            "income_stability": income_analysis["stability_rating"]
        },
        
        "recommendation": recommendation,
        "confidence_level": confidence,
        "suggested_interest_rate": risk_analysis["risk_adjusted_pricing"]["suggested_rate"],
        
        "conditions": [
            "Standard documentation required",
            "Property to be mortgaged as collateral"
        ] if recommendation == "APPROVE_WITH_CONDITIONS" else [],
        
        "next_stage": "UNDERWRITING",
        "parallel_with": "ASSET_VALUATION",
        "handoff_ready": True
    }


# ============================================================================
# TOOL DEFINITIONS FOR AZURE AI FOUNDRY
# ============================================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_credit_score",
            "description": "Deep analysis of credit score and its components",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "Customer name"},
                    "credit_score": {"type": "integer", "description": "CIBIL credit score (300-900)"}
                },
                "required": ["customer_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "evaluate_payment_history",
            "description": "Analyze payment behavior patterns over time",
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
            "name": "calculate_debt_metrics",
            "description": "Calculate debt ratios and credit utilization",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "Customer name"},
                    "monthly_income": {"type": "number", "description": "Monthly income"},
                    "total_outstanding_debt": {"type": "number", "description": "Total outstanding debt"},
                    "total_credit_limit": {"type": "number", "description": "Total credit limit"},
                    "monthly_obligations": {"type": "number", "description": "Monthly obligations"}
                },
                "required": ["customer_name", "monthly_income"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "assess_credit_risk",
            "description": "Comprehensive credit risk assessment",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "Customer name"},
                    "credit_score": {"type": "integer", "description": "Credit score"},
                    "payment_history_score": {"type": "integer", "description": "Payment history score"},
                    "credit_utilization": {"type": "number", "description": "Credit utilization %"},
                    "years_of_credit_history": {"type": "integer", "description": "Years of history"},
                    "recent_inquiries": {"type": "integer", "description": "Recent inquiries"}
                },
                "required": ["customer_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_credit_inquiries",
            "description": "Review recent credit inquiries",
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
            "name": "analyze_income_stability",
            "description": "Evaluate income patterns and employment stability",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "Customer name"},
                    "monthly_income": {"type": "number", "description": "Monthly income"},
                    "employment_years": {"type": "integer", "description": "Years with employer"},
                    "employer_type": {"type": "string", "description": "Type of employer"}
                },
                "required": ["customer_name", "monthly_income"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_credit_report",
            "description": "Generate comprehensive credit assessment report",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "Customer name"},
                    "application_id": {"type": "string", "description": "Application ID"},
                    "credit_score": {"type": "integer", "description": "Credit score"},
                    "monthly_income": {"type": "number", "description": "Monthly income"}
                },
                "required": ["customer_name", "application_id"]
            }
        }
    }
]


# ============================================================================
# AGENT CLASS
# ============================================================================

class CreditAssessmentAgent:
    """Credit Assessment Agent for loan processing"""
    
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
            "analyze_credit_score": analyze_credit_score,
            "evaluate_payment_history": evaluate_payment_history,
            "calculate_debt_metrics": calculate_debt_metrics,
            "assess_credit_risk": assess_credit_risk,
            "check_credit_inquiries": check_credit_inquiries,
            "analyze_income_stability": analyze_income_stability,
            "generate_credit_report": generate_credit_report
        }
        
        if tool_name in tool_functions:
            result = tool_functions[tool_name](**arguments)
            return json.dumps(result, indent=2)
        
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
    
    def process_request(self, user_message: str) -> str:
        """Process a credit assessment request"""
        # Create agent dynamically
        agent = self.project_client.agents.create_agent(
            model=MODEL_DEPLOYMENT,
            name="credit-assessment-agent",
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
            "name": "Credit Assessment Agent",
            "description": "Performs detailed credit analysis and risk evaluation",
            "stage": 4,
            "parallel_with": "Asset Valuation Agent",
            "previous_agent": "Credit Qualification Agent",
            "next_agent": "Underwriting Agent",
            "tools": [tool["function"]["name"] for tool in self.tools]
        }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  CREDIT ASSESSMENT AGENT")
    print("=" * 70)
    
    agent = CreditAssessmentAgent()
    print(f"\nAgent Info: {json.dumps(agent.get_agent_info(), indent=2)}")
    
    # Test with sample request
    test_message = """
    Perform detailed credit assessment for:
    
    Customer: Kala Divan
    Application ID: LOAN-20260127120000
    Credit Score: 750 (from CIBIL report)
    Monthly Income: ₹75,000
    
    Analyze credit score, payment history, debt metrics, and generate 
    comprehensive credit assessment report.
    """
    
    print(f"\n{'='*70}")
    print("Processing Request...")
    print(f"{'='*70}")
    
    response = agent.process_request(test_message)
    print(f"\nAgent Response:\n{response}")