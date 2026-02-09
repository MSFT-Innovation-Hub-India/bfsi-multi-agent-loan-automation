// Process Application JavaScript - Global Trust Bank
// Handles Documents, Workflow, and Analysis tabs

// Application data passed from applications page
let applicationData = null;
let workflowStarted = false;
let workflowCompleted = false;
let autoProcessing = false;
let currentStep = 0;
let agentResults = {};
let cosmosAgentData = null; // Real agent data from Cosmos DB

// Workflow steps configuration
const workflowSteps = [
    {
        id: 'customer-service',
        title: 'Customer Service Agent',
        description: 'Assists customers with form completion and provides information',
        icon: '🎧'
    },
    {
        id: 'document-verification',
        title: 'Document Verification Agent',
        description: 'Verifies customer KYC documents and ensures completeness',
        icon: '📋'
    },
    {
        id: 'credit-qualification',
        title: 'Credit Qualification Agent',
        description: 'Reviews initial credit requirements and eligibility',
        icon: '📊'
    },
    {
        id: 'credit-assessment',
        title: 'Credit Assessment Agent',
        description: 'Performs detailed credit analysis and risk evaluation',
        icon: '💳',
        parallel: true
    },
    {
        id: 'asset-valuation',
        title: 'Asset Valuation Agent',
        description: 'Evaluates collateral and asset worth for loan security',
        icon: '🏠',
        parallel: true
    },
    {
        id: 'underwriting',
        title: 'Underwriting Agent',
        description: 'Makes final loan approval decisions based on all assessments',
        icon: '✍️'
    },
    {
        id: 'offer-generation',
        title: 'Offer Generation Agent',
        description: 'Creates loan offers with terms and conditions',
        icon: '📄'
    },
    {
        id: 'customer-communication',
        title: 'Customer Communication Agent',
        description: 'Communicates offers and manages customer interactions',
        icon: '📞'
    },
    {
        id: 'audit',
        title: 'Audit Agent',
        description: 'Reviews and audits the complete loan process',
        icon: '🔍'
    }
];

// Document file mappings with categories and official names
const documentsMapping = {
    'adhaar male-3.png': { 
        name: 'Aadhaar Card', 
        type: 'image', 
        category: 'kyc'
    },
    'cibil.png': { 
        name: 'CIBIL Score Report', 
        type: 'image', 
        category: 'financial'
    },
    'CUST0001 - Pan.png': { 
        name: 'PAN Card', 
        type: 'image', 
        category: 'kyc'
    },
    'CUST0001 - Pay Slip.pdf': { 
        name: 'Salary Pay Slip', 
        type: 'pdf', 
        category: 'financial'
    },
    'CUST0006 - bank transactions.pdf': { 
        name: 'Bank Account Statement', 
        type: 'pdf', 
        category: 'financial'
    },
    'passport - CUST0001.png': { 
        name: 'Passport', 
        type: 'image', 
        category: 'kyc'
    },
    'Property Document.pdf': {
        name: 'Property Registration Document',
        type: 'pdf',
        category: 'property'
    }
};

// Track if workflow has been visited
let workflowVisited = false;

// Categorization helper - maps keywords to categories
function getCategoryFromFilename(filename) {
    const lower = filename.toLowerCase();
    
    // Financial documents keywords
    if (lower.includes('cibil') || lower.includes('pay') || lower.includes('slip') || 
        lower.includes('bank') || lower.includes('transaction') || lower.includes('salary')) {
        return 'financial';
    }
    
    // Property documents keywords
    if (lower.includes('property') || lower.includes('collateral')) {
        return 'property';
    }
    
    // Default to KYC
    return 'kyc';
}

// Get document verification status based on workflow state
function getDocumentStatus() {
    // Check if workflow has been visited in this session
    return workflowVisited ? 'verified' : 'pending';
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    loadApplicationData();
    loadDocuments();
    initializeWorkflow();
    // Pre-fetch cosmos data for analysis tab (after applicationData is loaded)
    setTimeout(() => fetchCosmosAgentData(), 100);
});

// Load application data from URL parameters or session storage
function loadApplicationData() {
    const urlParams = new URLSearchParams(window.location.search);
    const appId = urlParams.get('id');
    
    // Try to get from session storage first
    const storedData = sessionStorage.getItem('selectedApplication');
    if (storedData) {
        applicationData = JSON.parse(storedData);
    } else if (appId) {
        // Fallback to sample data if not in session storage
        applicationData = {
            id: appId,
            customerName: 'Customer',
            loanType: 'Loan',
            amount: 0
        };
    }
    
    // Update header display
    if (applicationData) {
        document.getElementById('applicationIdDisplay').textContent = applicationData.id;
        document.getElementById('applicantNameDisplay').textContent = applicationData.customerName;
        document.getElementById('loanTypeDisplay').textContent = applicationData.loanType;
    }
}

// Fetch real agent data from Cosmos DB
async function fetchCosmosAgentData() {
    // Get customer ID from application data
    const customerId = applicationData?.customerId || applicationData?.id;
    if (!customerId) {
        console.log('No customer ID available for Cosmos data fetch');
        // Use mock data if no customer ID
        cosmosAgentData = getMockCosmosData('CUST0241');
        return;
    }
    
    try {
        console.log(`🔍 Fetching Cosmos data for customer: ${customerId}`);
        
        // Fetch from API
        const response = await fetch(`/api/cosmos-data/${customerId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        // Only use API data if it has enough agents (at least 5 for a complete workflow)
        if (result.success && result.data && result.data.length >= 5) {
            cosmosAgentData = result.data;
            console.log('✅ Fetched complete Cosmos data from API:', cosmosAgentData.length, 'agents');
        } else {
            // Use mock data if API returns incomplete data
            console.log('⚠️ API data incomplete (only ' + (result.data?.length || 0) + ' agents), using mock data');
            cosmosAgentData = getMockCosmosData(customerId);
            console.log('📦 Using mock Cosmos data:', cosmosAgentData.length, 'agents');
        }
    } catch (error) {
        console.error('Error fetching Cosmos data:', error);
        // Use mock data on error
        cosmosAgentData = getMockCosmosData(customerId);
        console.log('📦 Using mock Cosmos data (fallback):', cosmosAgentData.length, 'agents');
    }
}

// Mock data structure matching the exact Cosmos DB response format
function getMockCosmosData(customerId) {
    // Default CUST0241 data
    if (customerId === 'CUST0241') {
        return [
            {
                "id": "ApplicationAssistAgent-CUST0241 - agent",
                "agent_id": "CUST0241-agent",
                "agent_name": "ApplicationAssist Agent",
                "customer_id": "CUST0241",
                "agent_description": [
                    "Extracted customer details: name (Kala Divan), contact (87XXXX), employment type (Other).",
                    "Guided the customer in completing all mandatory fields in the loan application form.",
                    "Submitted the completed loan application successfully with reference ID (APPXXXX)."
                ]
            },
            {
                "id": "DocumentCheckerAgent-CUST0241 - agent",
                "agent_id": "CUST0241-agent",
                "agent_name": "DocumentChecker Agent",
                "customer_id": "CUST0241",
                "agent_description": [
                    "Initiated KYC verification using Aadhar (XXXX XXXX 4534), PAN (CHQXXXXXX), and DOB (XX/XX/19XX).",
                    "Verified document set: Aadhar, PAN, salary slips, income certificate, land records, CIBIL report, bank statements, Form 16, birth certificate.",
                    "Updated verification status in document tracking system.",
                    "Output: Document verification marked complete."
                ]
            },
            {
                "id": "PreQualificationAgent-CUST0241 - agent",
                "agent_id": "CUST0241-agent",
                "agent_name": "PreQualification Agent",
                "customer_id": "CUST0241",
                "agent_description": [
                    "Analyzed income (₹23XXXX/month) and employment status ('Other').",
                    "Evaluated eligibility.",
                    "Generated prequalification status: Eligible.",
                    "Output: Prequalification pass."
                ]
            },
            {
                "id": "ValuationAgent-CUST0241 - agent",
                "agent_id": "CUST0241-agent",
                "agent_name": "Valuation Agent",
                "customer_id": "CUST0241",
                "agent_description": [
                    "Initiated property valuation for address: House No. XX, Pandya Zilla, Udupi.",
                    "Estimated value: ₹6XXXXX.",
                    "Confirmed property match against submitted ownership documents.",
                    "Output: Property valuation recorded."
                ]
            },
            {
                "id": "CreditAssessorAgent-CUST0241 - agent",
                "agent_id": "CUST0241-agent",
                "agent_name": "CreditAssessor Agent",
                "customer_id": "CUST0241",
                "agent_description": [
                    "Reviewed 6-month bank and credit card statements.",
                    "Checked for payment defaults, cheque bounces, and over-limit usage.",
                    "Evaluated EMI affordability based on income (₹23XXXX) and proposed EMI (₹3XXX).",
                    "Output: Credit assessment summary prepared."
                ]
            },
            {
                "id": "UnderwritingAgent-CUST0241 - agent",
                "agent_id": "CUST0241-agent",
                "agent_name": "Underwriting Agent",
                "customer_id": "CUST0241",
                "agent_description": [
                    "Checked eligibility against policy exceptions and risk flags.",
                    "Approved loan.",
                    "Output: Loan underwriting complete with decision status (Approved)."
                ]
            },
            {
                "id": "OfferGenerationAgent-CUST0241 - agent",
                "agent_id": "CUST0241-agent",
                "agent_name": "OfferGeneration Agent",
                "customer_id": "CUST0241",
                "agent_description": [
                    "Created personalized loan offer (₹4XXXXX, 25 years, 7.25% interest).",
                    "Packaged offer document and offer ID for dispatch.",
                    "Output: Offer generated and sent to communication system."
                ]
            },
            {
                "id": "CustomerCommunicationAgent-CUST0241 - agent",
                "agent_id": "CUST0241-agent",
                "agent_name": "CustomerCommunication Agent",
                "customer_id": "CUST0241",
                "agent_description": [
                    "Sent acknowledgement, requested documents, and confirmed KYC done.",
                    "Shared application number and loan offer.",
                    "All communication recorded with timestamp."
                ]
            },
            {
                "id": "Audit-CUST0241 - agent",
                "agent_id": "CUST0241-audit",
                "agent_name": "Audit Record",
                "customer_id": "CUST0241",
                "agent_description": [
                    "PreQualification Agent: Analyzed income and employment status. Marked customer pre-qualified.",
                    "ApplicationAssist Agent: Extracted customer details and submitted loan application.",
                    "DocumentChecker Agent: Performed KYC and verified all documents. Marked verification complete.",
                    "Valuation Agent: Conducted property valuation with estimated value ₹6XXXXX.",
                    "CreditAssessor Agent: Reviewed statements, checked defaults, evaluated EMI affordability.",
                    "Underwriting Agent: Checked eligibility against policies. Loan approved.",
                    "OfferGeneration Agent: Created personalized loan offer and dispatched.",
                    "CustomerCommunication Agent: Sent all communications with timestamps.",
                    "Final Status: Loan application processed end-to-end, approved, and communicated to customer."
                ]
            }
        ];
    }
    
    // CUST0001 - Incomplete Documents case
    if (customerId === 'CUST0001') {
        return [
            {
                "agent_name": "ApplicationAssist Agent",
                "customer_id": "CUST0001",
                "agent_description": [
                    "Extracted customer details: name (Rajesh Kumar Sharma), contact (98XXXX), employment type (Full-time).",
                    "Guided the customer in completing all mandatory fields in the loan application form.",
                    "Submitted the completed loan application successfully."
                ]
            },
            {
                "agent_name": "DocumentChecker Agent",
                "customer_id": "CUST0001",
                "status": "incomplete",
                "agent_description": [
                    "Initiated KYC verification using Aadhar (XXXX XXXX 9012), PAN (ABCXXXX).",
                    "✅ Verified: Aadhar Card, PAN Card, Address Proof",
                    "✅ Verified: Salary Slips (May 2025, April 2025)",
                    "✅ Verified: Bank Statements (6 months)",
                    "❌ MISSING: Payslip June 2025 - Document not found in submission",
                    "⚠️ Verification Status: INCOMPLETE - Missing required document",
                    "Action Required: Customer notification sent for missing document submission."
                ]
            }
        ];
    }
    
    // CUST0005 - Suspicious Underwriting case
    if (customerId === 'CUST0005') {
        return [
            {
                "agent_name": "ApplicationAssist Agent",
                "customer_id": "CUST0005",
                "agent_description": [
                    "Extracted customer details: name (Vikram Agarwal), contact (88XXXX), employment type (Full-time).",
                    "Guided the customer in completing all mandatory fields.",
                    "Submitted the completed loan application successfully."
                ]
            },
            {
                "agent_name": "DocumentChecker Agent",
                "customer_id": "CUST0005",
                "agent_description": [
                    "Initiated KYC verification using Aadhar (XXXX XXXX 1234), PAN (VIKXXXX).",
                    "Verified all documents: Aadhar, PAN, salary slips, bank statements.",
                    "Output: Document verification marked complete."
                ]
            },
            {
                "agent_name": "PreQualification Agent",
                "customer_id": "CUST0005",
                "agent_description": [
                    "Analyzed income (₹5,80,000/annum) and employment status (Full-time).",
                    "Evaluated eligibility based on income-to-loan ratio.",
                    "Output: Prequalification passed with conditions."
                ]
            },
            {
                "agent_name": "CreditAssessor Agent",
                "customer_id": "CUST0005",
                "agent_description": [
                    "Reviewed 6-month bank statements - irregular deposits flagged.",
                    "CIBIL Score: 700 (Fair - Below preferred threshold of 720).",
                    "Debt-to-income ratio: 45% - Above acceptable 40% threshold.",
                    "Multiple credit inquiries detected: 8 in last 6 months.",
                    "Output: Credit assessment flagged for elevated risk."
                ]
            },
            {
                "agent_name": "Valuation Agent",
                "customer_id": "CUST0005",
                "agent_description": [
                    "Personal loan - no property collateral required.",
                    "Evaluated unsecured loan risk factors.",
                    "Output: Valuation step completed (N/A for personal loan)."
                ]
            },
            {
                "agent_name": "Underwriting Agent",
                "customer_id": "CUST0005",
                "status": "suspicious",
                "agent_description": [
                    "⚠️ SUSPICIOUS ACTIVITY DETECTED - Manual Review Required",
                    "Risk Factor 1: Recent job change (3 months ago) - employment stability concern",
                    "Risk Factor 2: High debt-to-income ratio (45%) - above acceptable 40% threshold",
                    "Risk Factor 3: Multiple credit inquiries (8) in last 6 months - credit seeking behavior",
                    "Risk Factor 4: Irregular income deposits in bank statements",
                    "Risk Factor 5: Previous loan default 2 years ago (settled but flagged)",
                    "Risk Level: HIGH RISK - Outside normal automated approval parameters",
                    "Decision: REQUIRES MANUAL UNDERWRITING REVIEW"
                ]
            }
        ];
    }
    
    // Generic mock data for other customers
    return [
        {
            "agent_name": "ApplicationAssist Agent",
            "customer_id": customerId,
            "agent_description": ["Extracted customer details.", "Guided application completion.", "Submitted application."]
        },
        {
            "agent_name": "DocumentChecker Agent",
            "customer_id": customerId,
            "agent_description": ["Initiated KYC verification.", "Verified all documents.", "Marked verification complete."]
        },
        {
            "agent_name": "PreQualification Agent",
            "customer_id": customerId,
            "agent_description": ["Analyzed income and employment.", "Evaluated eligibility.", "Prequalification passed."]
        },
        {
            "agent_name": "Valuation Agent",
            "customer_id": customerId,
            "agent_description": ["Initiated property valuation.", "Confirmed property documents.", "Valuation recorded."]
        },
        {
            "agent_name": "CreditAssessor Agent",
            "customer_id": customerId,
            "agent_description": ["Reviewed bank statements.", "Checked payment history.", "Credit assessment complete."]
        },
        {
            "agent_name": "Underwriting Agent",
            "customer_id": customerId,
            "agent_description": ["Checked policy exceptions.", "Evaluated risk flags.", "Loan approved."]
        },
        {
            "agent_name": "OfferGeneration Agent",
            "customer_id": customerId,
            "agent_description": ["Created loan offer.", "Packaged offer document.", "Sent to communication system."]
        },
        {
            "agent_name": "CustomerCommunication Agent",
            "customer_id": customerId,
            "agent_description": ["Sent acknowledgement.", "Shared application details.", "All communications logged."]
        },
        {
            "agent_name": "Audit Record",
            "customer_id": customerId,
            "agent_description": ["All agents completed processing.", "Loan application approved.", "Full audit trail recorded."]
        }
    ];
}

// Load documents from the Documents folder
function loadDocuments() {
    // Fetch documents list from server
    fetch('/api/documents')
        .then(response => response.json())
        .then(data => {
            if (data.documents && data.documents.length > 0) {
                categorizeAndDisplayDocuments(data.documents);
            } else {
                showEmptyDocuments();
            }
        })
        .catch(error => {
            console.error('Error loading documents:', error);
            // Show static documents as fallback
            showStaticDocuments();
        });
}

// Categorize and display documents in their respective sections
function categorizeAndDisplayDocuments(documents) {
    const kycDocs = [];
    const financialDocs = [];
    const propertyDocs = [];
    
    documents.forEach(doc => {
        const mapping = documentsMapping[doc.filename];
        
        // Use mapping category, or API category, or determine from filename
        let category = mapping?.category || doc.category || getCategoryFromFilename(doc.filename);
        
        // Status is based on whether workflow has been visited
        const status = getDocumentStatus();
        
        const enrichedDoc = {
            ...doc,
            officialName: mapping?.name || doc.name,
            status: status,
            category: category
        };
        
        switch(category) {
            case 'financial':
                financialDocs.push(enrichedDoc);
                break;
            case 'property':
                propertyDocs.push(enrichedDoc);
                break;
            default:
                kycDocs.push(enrichedDoc);
        }
    });
    
    // Render each category
    renderDocumentCategory('kycDocumentsGrid', kycDocs, 'kycCount');
    renderDocumentCategory('financialDocumentsGrid', financialDocs, 'financialCount');
    renderDocumentCategory('propertyDocumentsGrid', propertyDocs, 'propertyCount');
}

// Render documents in a category grid
function renderDocumentCategory(gridId, documents, countId) {
    const grid = document.getElementById(gridId);
    const countEl = document.getElementById(countId);
    
    if (!grid) return;
    
    grid.innerHTML = '';
    
    if (documents.length === 0) {
        grid.innerHTML = `
            <div class="category-empty">
                <i class="fas fa-folder-open"></i>
                <p>No documents in this category</p>
            </div>
        `;
        countEl.textContent = '0 documents';
        return;
    }
    
    documents.forEach(doc => {
        const card = createDocumentCard(doc);
        grid.appendChild(card);
    });
    
    countEl.textContent = `${documents.length} document${documents.length > 1 ? 's' : ''}`;
}

// Show static documents as fallback
function showStaticDocuments() {
    const documents = Object.entries(documentsMapping).map(([filename, docInfo]) => ({
        filename: filename,
        name: filename,
        type: docInfo.type,
        url: `/Documents/${filename}`,
        officialName: docInfo.name,
        status: docInfo.status,
        category: docInfo.category
    }));
    
    categorizeAndDisplayDocuments(documents);
}

// Show empty state for all categories
function showEmptyDocuments() {
    ['kycDocumentsGrid', 'financialDocumentsGrid', 'propertyDocumentsGrid'].forEach(gridId => {
        const grid = document.getElementById(gridId);
        if (grid) {
            grid.innerHTML = `
                <div class="category-empty">
                    <i class="fas fa-folder-open"></i>
                    <p>No documents uploaded</p>
                </div>
            `;
        }
    });
}

// Create document card element - Professional Bank Style
function createDocumentCard(doc) {
    const card = document.createElement('div');
    card.className = 'document-card';
    
    const isPdf = doc.type === 'pdf';
    const iconClass = isPdf ? 'pdf' : 'image';
    const iconSymbol = isPdf ? 'fa-file-pdf' : 'fa-file-image';
    const fileTypeLabel = isPdf ? 'PDF Document' : 'Image File';
    
    // Get official name from mapping or use provided name
    const officialName = doc.officialName || documentsMapping[doc.filename]?.name || doc.name || doc.filename;
    const status = doc.status || documentsMapping[doc.filename]?.status || 'pending';
    
    // Status configuration
    const statusConfig = {
        verified: { icon: 'fa-check-circle', text: 'Verified', class: 'verified' },
        pending: { icon: 'fa-clock', text: 'Pending Verification', class: 'pending' },
        rejected: { icon: 'fa-times-circle', text: 'Rejected', class: 'rejected' }
    };
    
    const statusInfo = statusConfig[status] || statusConfig.pending;
    
    card.innerHTML = `
        <div class="document-card-header">
            <div class="document-icon ${iconClass}">
                <i class="fas ${iconSymbol}"></i>
            </div>
            <div class="document-info">
                <div class="document-name">${officialName}</div>
                <div class="document-meta-row">
                    <span class="document-meta-item">
                        <span class="label">Type:</span>
                        <span class="value">${fileTypeLabel}</span>
                    </span>
                </div>
                <div class="document-status ${statusInfo.class}">
                    <i class="fas ${statusInfo.icon}"></i>
                    <span>${statusInfo.text}</span>
                </div>
            </div>
        </div>
        <div class="document-actions">
            <button class="doc-action-btn view" onclick="viewDocument('${doc.filename}', '${doc.type}')">
                <i class="fas fa-eye"></i> View Document
            </button>
            <button class="doc-action-btn download" onclick="downloadDocument('${doc.filename}')">
                <i class="fas fa-download"></i> Download ${isPdf ? 'PDF' : 'File'}
            </button>
        </div>
    `;
    
    return card;
}

// View document in modal
function viewDocument(filename, type) {
    const modal = document.getElementById('documentModal');
    const viewer = document.getElementById('documentViewer');
    const title = document.getElementById('documentModalTitle');
    const downloadBtn = document.getElementById('downloadDocBtn');
    
    const docUrl = `/Documents/${filename}`;
    title.textContent = documentsMapping[filename]?.name || filename;
    downloadBtn.href = docUrl;
    downloadBtn.download = filename;
    
    if (type === 'image' || filename.endsWith('.png') || filename.endsWith('.jpg') || filename.endsWith('.jpeg')) {
        viewer.innerHTML = `<img src="${docUrl}" alt="${filename}" onerror="this.parentElement.innerHTML='<div class=\\'no-preview\\'><i class=\\'fas fa-exclamation-triangle\\'></i><p>Unable to load image</p></div>'" />`;
    } else if (type === 'pdf' || filename.endsWith('.pdf')) {
        viewer.innerHTML = `<iframe src="${docUrl}" title="${filename}"></iframe>`;
    } else {
        viewer.innerHTML = `
            <div class="no-preview">
                <i class="fas fa-file"></i>
                <p>Preview not available for this file type</p>
                <p>Please download the file to view it.</p>
            </div>
        `;
    }
    
    modal.classList.add('active');
}

// Close document modal
function closeDocumentModal() {
    const modal = document.getElementById('documentModal');
    modal.classList.remove('active');
}

// Download document
function downloadDocument(filename) {
    const link = document.createElement('a');
    link.href = `/Documents/${filename}`;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Switch tabs
function switchTab(tabId) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabId}-tab`).classList.add('active');
    
    // Handle workflow tab
    if (tabId === 'workflow') {
        // Mark workflow as visited
        workflowVisited = true;
        
        // Auto-start workflow immediately when switching to workflow tab
        if (!workflowStarted) {
            setTimeout(() => {
                startWorkflow();
            }, 300);
        }
    }
    
    // Reload documents when switching back to documents tab (to update status)
    if (tabId === 'documents' && workflowVisited) {
        loadDocuments();
    }
}

// Initialize workflow UI
function initializeWorkflow() {
    const grid = document.getElementById('workflowGrid');
    grid.innerHTML = '';
    
    // Create workflow step cards
    let parallelContainer = null;
    
    workflowSteps.forEach((step, index) => {
        if (step.parallel) {
            if (!parallelContainer) {
                parallelContainer = document.createElement('div');
                parallelContainer.className = 'parallel-steps';
                grid.appendChild(parallelContainer);
            }
            const card = createWorkflowStepCard(step, index);
            parallelContainer.appendChild(card);
        } else {
            parallelContainer = null;
            const card = createWorkflowStepCard(step, index);
            grid.appendChild(card);
        }
    });
}

// Create workflow step card
function createWorkflowStepCard(step, index) {
    const card = document.createElement('div');
    card.className = 'workflow-step';
    card.id = `step-${step.id}`;
    card.setAttribute('data-step', step.id);
    
    card.innerHTML = `
        <div class="step-icon">${step.icon}</div>
        <div class="step-content">
            <h4 class="step-title">${step.title}</h4>
            <p class="step-description">${step.description}</p>
        </div>
        <div class="step-status pending">Pending</div>
    `;
    
    return card;
}

// Start workflow processing
function startWorkflow() {
    if (workflowStarted) return;
    
    workflowStarted = true;
    autoProcessing = true;
    
    showNotification('info', 'Workflow Started', 'AI agents are now processing the loan application.');
    
    // Start processing steps
    processNextStep();
}

// Stop workflow processing
function stopWorkflow() {
    autoProcessing = false;
    showNotification('warning', 'Workflow Paused', 'Workflow processing has been paused.');
}

// Process next workflow step
function processNextStep() {
    if (!autoProcessing || currentStep >= workflowSteps.length) {
        if (currentStep >= workflowSteps.length) {
            completeWorkflow();
        }
        return;
    }
    
    const step = workflowSteps[currentStep];
    
    // Check for parallel steps
    if (step.parallel) {
        // Find all parallel steps
        const parallelSteps = workflowSteps.filter(s => s.parallel);
        
        // Process both parallel steps simultaneously
        parallelSteps.forEach(pStep => {
            processStep(pStep);
        });
        
        // Skip to after parallel steps
        currentStep = workflowSteps.findIndex(s => s.id === 'underwriting');
        
        // Wait for parallel steps to complete
        setTimeout(() => {
            processNextStep();
        }, 4000);
    } else {
        processStep(step);
        currentStep++;
        
        // Schedule next step
        const delay = step.id === 'underwriting' ? 4000 : 3000;
        setTimeout(() => {
            processNextStep();
        }, delay);
    }
}

// Process individual step
function processStep(step) {
    const card = document.getElementById(`step-${step.id}`);
    if (!card) return;
    
    // Set processing state
    card.classList.remove('pending');
    card.classList.add('processing');
    const status = card.querySelector('.step-status');
    status.className = 'step-status processing';
    status.textContent = 'Processing...';
    
    // Check for CUST0001 incomplete documents case
    if (step.id === 'document-verification' && applicationData?.id === 'CUST0001') {
        setTimeout(() => {
            // Mark as incomplete
            card.classList.remove('processing');
            card.classList.add('incomplete');
            status.className = 'step-status incomplete';
            status.textContent = 'Incomplete';
            
            // Store agent result with incomplete status
            agentResults[step.id] = {
                summary: 'Document verification incomplete - missing documents',
                status: 'incomplete',
                details: [
                    { label: 'Aadhaar Status', value: 'Verified ✓' },
                    { label: 'PAN Status', value: 'Verified ✓' },
                    { label: 'Address Proof', value: 'Verified ✓' },
                    { label: 'Salary Slips', value: 'May 2025, April 2025 ✓' },
                    { label: 'Missing Document', value: 'Payslip June 2025 ❌' }
                ]
            };
            
            // Stop workflow progression
            autoProcessing = false;
            
            showNotification('warning', 'Document Verification Incomplete', 
                `Missing document detected for ${applicationData.customerName}. Please review and request missing documents.`);
            
            // Show Analysis tab with incomplete status after a delay
            setTimeout(() => {
                showIncompleteAnalysis('incomplete');
            }, 2000);
        }, 2500);
        return;
    }
    
    // Check for CUST0005 suspicious underwriting case
    if (step.id === 'underwriting' && applicationData?.id === 'CUST0005') {
        setTimeout(() => {
            // Mark as suspicious
            card.classList.remove('processing');
            card.classList.add('suspicious');
            status.className = 'step-status suspicious';
            status.textContent = 'Requires Review';
            
            // Store agent result with suspicious status
            agentResults[step.id] = {
                summary: 'Underwriting flagged for manual review - suspicious activity detected',
                status: 'suspicious',
                suspiciousReasons: [
                    'Recent job change (3 months ago) - employment stability concern',
                    'High debt-to-income ratio (45%) - above acceptable threshold',
                    'Multiple credit inquiries (8) in last 6 months',
                    'Irregular income deposits in bank statements',
                    'Previous loan default 2 years ago (settled but flagged)'
                ],
                details: [
                    { label: 'Risk Assessment', value: 'HIGH RISK ⚠️' },
                    { label: 'Decision', value: 'REQUIRES MANUAL REVIEW' },
                    { label: 'Debt-to-Income', value: '45% (Above 40% threshold)' },
                    { label: 'Employment Stability', value: 'Concern - Recent change' }
                ]
            };
            
            // Stop workflow progression - requires manual decision
            autoProcessing = false;
            
            showNotification('warning', 'Underwriting Review Required', 
                `Suspicious activity detected for ${applicationData.customerName}. Manual review and approval required.`);
            
            // Show Analysis tab with suspicious status after a delay
            setTimeout(() => {
                showIncompleteAnalysis('suspicious');
            }, 2000);
        }, 2500);
        return;
    }
    
    // Normal processing for other steps
    setTimeout(() => {
        // Complete the step
        card.classList.remove('processing');
        card.classList.add('completed');
        status.className = 'step-status completed';
        status.textContent = 'Completed';
        
        // Store agent result
        agentResults[step.id] = generateAgentResult(step);
        
        showNotification('success', `${step.title}`, 'Processing completed successfully.');
    }, 2500);
}

// Generate simulated agent result
function generateAgentResult(step) {
    const results = {
        'customer-service': {
            summary: 'Customer inquiry handled successfully',
            details: [
                { label: 'Query Type', value: 'Loan Application Status' },
                { label: 'Response Time', value: '2.3 seconds' },
                { label: 'Satisfaction Score', value: '95%' },
                { label: 'Issues Identified', value: 'None' }
            ]
        },
        'document-verification': {
            summary: 'All documents verified and validated',
            details: [
                { label: 'Documents Checked', value: '6 documents' },
                { label: 'Aadhaar Status', value: 'Verified ✓' },
                { label: 'PAN Status', value: 'Verified ✓' },
                { label: 'Income Proof', value: 'Verified ✓' }
            ]
        },
        'credit-qualification': {
            summary: 'Applicant meets basic credit requirements',
            details: [
                { label: 'Credit Score', value: applicationData?.creditScore || '720' },
                { label: 'Minimum Required', value: '650' },
                { label: 'Qualification Status', value: 'Qualified ✓' },
                { label: 'Risk Category', value: 'Low Risk' }
            ]
        },
        'credit-assessment': {
            summary: 'Detailed credit analysis completed',
            details: [
                { label: 'Credit History', value: '5+ years' },
                { label: 'Payment History', value: 'Excellent' },
                { label: 'Credit Utilization', value: '28%' },
                { label: 'Debt-to-Income', value: '32%' }
            ]
        },
        'asset-valuation': {
            summary: 'Collateral assessment completed',
            details: [
                { label: 'Property Type', value: 'Residential' },
                { label: 'Market Value', value: '₹45,00,000' },
                { label: 'LTV Ratio', value: '75%' },
                { label: 'Valuation Status', value: 'Approved ✓' }
            ]
        },
        'underwriting': {
            summary: 'Loan application approved by underwriting',
            details: [
                { label: 'Risk Assessment', value: 'Acceptable' },
                { label: 'Terms Offered', value: 'Standard' },
                { label: 'Interest Rate', value: '8.5% p.a.' },
                { label: 'Decision', value: 'APPROVED' }
            ]
        },
        'offer-generation': {
            summary: 'Loan offer generated and ready',
            details: [
                { label: 'Loan Amount', value: `₹${(applicationData?.amount || 2500000).toLocaleString('en-IN')}` },
                { label: 'Tenure', value: '240 months' },
                { label: 'EMI Amount', value: '₹21,850' },
                { label: 'Processing Fee', value: '0.5%' }
            ]
        },
        'customer-communication': {
            summary: 'Customer notified of loan approval',
            details: [
                { label: 'Notification Sent', value: 'Email + SMS' },
                { label: 'Offer Validity', value: '30 days' },
                { label: 'Response Required', value: 'Yes' },
                { label: 'Follow-up Date', value: 'In 7 days' }
            ]
        },
        'audit': {
            summary: 'Complete audit trail generated',
            details: [
                { label: 'Compliance Check', value: 'Passed ✓' },
                { label: 'Documentation', value: 'Complete' },
                { label: 'Process Integrity', value: 'Verified' },
                { label: 'Audit Score', value: '98/100' }
            ]
        }
    };
    
    return results[step.id] || { summary: 'Processing completed', details: [] };
}

// Complete workflow
function completeWorkflow() {
    workflowCompleted = true;
    autoProcessing = false;
    
    // Show analysis tab
    const analysisTabBtn = document.getElementById('analysisTabBtn');
    if (analysisTabBtn) {
        analysisTabBtn.classList.remove('hidden');
    }
    
    // Show completion notification
    showNotification('success', 'Workflow Complete!', 'All agents have completed processing. View the Analysis tab for results.');
    
    // Populate analysis tab
    populateAnalysis();
    
    // Automatically switch to analysis tab
    setTimeout(() => {
        switchTab('analysis');
    }, 1500);
}

// Show analysis for incomplete or suspicious workflow
function showIncompleteAnalysis(status) {
    // Show analysis tab
    const analysisTabBtn = document.getElementById('analysisTabBtn');
    if (analysisTabBtn) {
        analysisTabBtn.classList.remove('hidden');
    }
    
    // Load the appropriate mock data for this customer
    const customerId = applicationData?.id || 'CUST0241';
    cosmosAgentData = getMockCosmosData(customerId);
    
    // Populate analysis tab with partial results
    populateAnalysis(status);
    
    // Automatically switch to analysis tab
    setTimeout(() => {
        switchTab('analysis');
    }, 1000);
}

// Switch analysis sub-tabs
function switchAnalysisSubTab(subtabId) {
    // Update sub-tab buttons
    document.querySelectorAll('.sub-tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-subtab="${subtabId}"]`).classList.add('active');
    
    // Update sub-tab content
    document.querySelectorAll('.analysis-sub-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${subtabId}-subtab`).classList.add('active');
    
    // Populate full output if switching to that tab
    if (subtabId === 'full-output') {
        populateFullOutput();
    }
}

// Populate full output view
function populateFullOutput() {
    const container = document.getElementById('fullOutputContainer');
    container.innerHTML = '';
    
    // Ensure we have cosmos data
    if (!cosmosAgentData || cosmosAgentData.length === 0) {
        const customerId = applicationData?.customerId || applicationData?.id || 'CUST0241';
        cosmosAgentData = getMockCosmosData(customerId);
    }
    
    // Add action buttons
    const actionsHtml = `
        <div class="full-output-actions">
            <button class="output-action-btn" onclick="expandAllAgents()">
                <i class="fas fa-expand-alt"></i> Expand All
            </button>
            <button class="output-action-btn" onclick="collapseAllAgents()">
                <i class="fas fa-compress-alt"></i> Collapse All
            </button>
        </div>
    `;
    container.innerHTML = actionsHtml;
    
    // Create full output section for each agent
    cosmosAgentData.forEach((agent, index) => {
        const agentSection = createFullOutputSection(agent, index === 0);
        container.appendChild(agentSection);
    });
}

// Create full output section for an agent
function createFullOutputSection(agent, expandedByDefault = false) {
    const section = document.createElement('div');
    section.className = `full-output-agent${expandedByDefault ? ' expanded' : ''}`;
    
    const icon = getAgentIcon(agent.agent_name);
    const descriptionCount = agent.agent_description ? agent.agent_description.length : 0;
    
    // Build output items
    let outputItemsHtml = '';
    if (agent.agent_description && agent.agent_description.length > 0) {
        outputItemsHtml = agent.agent_description.map(desc => {
            // Determine if this is a success item
            const descLower = desc.toLowerCase();
            const isSuccess = descLower.includes('verified') || descLower.includes('approved') || 
                              descLower.includes('eligible') || descLower.includes('success') ||
                              descLower.includes('completed') || descLower.includes('submitted') ||
                              descLower.includes('pass');
            
            return `
                <div class="full-output-item${isSuccess ? ' success' : ''}">
                    <p>${desc}</p>
                </div>
            `;
        }).join('');
    }
    
    section.innerHTML = `
        <div class="full-output-header" onclick="toggleAgentOutput(this)">
            <div class="full-output-icon">${icon}</div>
            <div class="full-output-title">
                <h4>${agent.agent_name}</h4>
                <p>${descriptionCount} output${descriptionCount !== 1 ? 's' : ''} recorded</p>
            </div>
            <div class="full-output-toggle">
                <i class="fas fa-chevron-down"></i>
            </div>
        </div>
        <div class="full-output-body">
            ${outputItemsHtml}
        </div>
    `;
    
    return section;
}

// Toggle agent output expansion
function toggleAgentOutput(header) {
    const section = header.parentElement;
    section.classList.toggle('expanded');
}

// Expand all agents
function expandAllAgents() {
    document.querySelectorAll('.full-output-agent').forEach(section => {
        section.classList.add('expanded');
    });
}

// Collapse all agents
function collapseAllAgents() {
    document.querySelectorAll('.full-output-agent').forEach(section => {
        section.classList.remove('expanded');
    });
}

// Populate analysis tab with results
function populateAnalysis(status = 'approved') {
    // Update verdict based on status
    updateVerdict(status);
    
    // Populate agent results grid
    const grid = document.getElementById('analysisGrid');
    grid.innerHTML = '';
    
    // Ensure we have cosmos data (mock or real)
    if (!cosmosAgentData || cosmosAgentData.length === 0) {
        const customerId = applicationData?.customerId || applicationData?.id || 'CUST0241';
        cosmosAgentData = getMockCosmosData(customerId);
        console.log('📦 Loaded mock Cosmos data for analysis:', cosmosAgentData.length, 'agents');
    }
    
    // Use Cosmos data (real or mock)
    console.log('📊 Populating analysis with Cosmos data:', cosmosAgentData.length, 'agents');
    
    // Create cards from Cosmos agent data
    cosmosAgentData.forEach(agent => {
        // Skip audit records for individual cards (we'll handle them separately)
        if (agent.agent_name && !agent.agent_name.toLowerCase().includes('audit')) {
            const card = createCosmosAgentCard(agent, status);
            grid.appendChild(card);
        }
    });
    
    // Add audit card at the end if exists (only for completed workflows)
    if (status === 'approved') {
        const auditAgent = cosmosAgentData.find(a => 
            a.agent_name && a.agent_name.toLowerCase().includes('audit')
        );
        if (auditAgent) {
            const auditCard = createCosmosAgentCard(auditAgent, status);
            grid.appendChild(auditCard);
        }
    }
}

// Create card from real Cosmos agent data
function createCosmosAgentCard(agent, status = 'approved') {
    const card = document.createElement('div');
    
    // Check if this agent has a special status (incomplete or suspicious)
    const hasSpecialStatus = agent.status === 'incomplete' || agent.status === 'suspicious';
    const isIncomplete = agent.status === 'incomplete' || 
        (agent.agent_description && agent.agent_description.some(d => d.includes('❌') || d.includes('MISSING') || d.includes('INCOMPLETE')));
    const isSuspicious = agent.status === 'suspicious' || 
        (agent.agent_description && agent.agent_description.some(d => d.includes('⚠️') || d.includes('SUSPICIOUS') || d.includes('HIGH RISK')));
    
    // Set appropriate class based on status
    if (isIncomplete) {
        card.className = 'agent-analysis-card status-incomplete';
    } else if (isSuspicious) {
        card.className = 'agent-analysis-card status-suspicious';
    } else {
        card.className = 'agent-analysis-card';
    }
    
    // Determine icon based on agent name
    const icon = getAgentIcon(agent.agent_name);
    
    // Format agent description as details with special styling for issues
    let detailsHtml = '';
    if (agent.agent_description && agent.agent_description.length > 0) {
        detailsHtml = agent.agent_description.map((desc) => {
            // Check if this is an error/warning/issue line
            const isError = desc.includes('❌') || desc.includes('MISSING') || desc.includes('INCOMPLETE');
            const isWarning = desc.includes('⚠️') || desc.includes('SUSPICIOUS') || desc.includes('Risk Factor') || desc.includes('HIGH RISK');
            const isSuccess = desc.includes('✅') || desc.includes('Verified') || desc.includes('complete');
            
            let itemClass = 'agent-output-item';
            if (isError) itemClass += ' error-item';
            else if (isWarning) itemClass += ' warning-item';
            else if (isSuccess) itemClass += ' success-item';
            
            return `
                <div class="${itemClass}">
                    <div class="agent-output-value">${desc}</div>
                </div>
            `;
        }).join('');
    }
    
    // Add status badge if special status
    let statusBadge = '';
    if (isIncomplete) {
        statusBadge = '<span class="agent-status-badge incomplete">Incomplete</span>';
    } else if (isSuspicious) {
        statusBadge = '<span class="agent-status-badge suspicious">Requires Review</span>';
    }
    
    card.innerHTML = `
        <div class="agent-card-header">
            <div class="agent-icon">${icon}</div>
            <div class="agent-info">
                <div class="agent-name">${agent.agent_name} ${statusBadge}</div>
                <div class="agent-role">Agent output from processing</div>
            </div>
        </div>
        <div class="agent-card-body">
            <div class="agent-output">
                ${detailsHtml}
            </div>
        </div>
    `;
    
    // Store data for modal
    const agentData = {
        name: agent.agent_name,
        icon: icon,
        descriptions: agent.agent_description || [],
        customerId: agent.customer_id,
        timestamp: agent._ts,
        status: isIncomplete ? 'incomplete' : (isSuspicious ? 'suspicious' : 'completed')
    };
    
    // Add click handler to open modal
    card.onclick = () => openCosmosAgentModal(agentData);
    
    return card;
}

// Get icon based on agent name
function getAgentIcon(agentName) {
    const name = agentName.toLowerCase();
    if (name.includes('application') || name.includes('assist')) return '📝';
    if (name.includes('document') || name.includes('checker')) return '📋';
    if (name.includes('qualification') || name.includes('prequal')) return '📊';
    if (name.includes('credit') || name.includes('assessment')) return '💳';
    if (name.includes('valuation') || name.includes('asset')) return '🏠';
    if (name.includes('underwriting') || name.includes('under')) return '✍️';
    if (name.includes('offer') || name.includes('generation')) return '📄';
    if (name.includes('communication') || name.includes('customer')) return '📞';
    if (name.includes('audit')) return '🔍';
    return '🤖';
}

// Open modal for Cosmos agent data
function openCosmosAgentModal(agentData) {
    const modal = document.getElementById('agentModal');
    const icon = document.getElementById('agentModalIcon');
    const title = document.getElementById('agentModalTitle');
    const subtitle = document.getElementById('agentModalSubtitle');
    const content = document.getElementById('agentModalContent');
    
    icon.textContent = agentData.icon;
    title.textContent = agentData.name;
    subtitle.textContent = `Customer: ${agentData.customerId || 'N/A'}`;
    
    // Build detailed content from agent descriptions
    let detailsHtml = '<div class="agent-detail-grid">';
    
    if (agentData.descriptions && agentData.descriptions.length > 0) {
        detailsHtml += agentData.descriptions.map((desc, index) => {
            // Determine styling based on content
            let valueClass = '';
            const descLower = desc.toLowerCase();
            if (descLower.includes('verified') || descLower.includes('approved') || 
                descLower.includes('eligible') || descLower.includes('success') ||
                descLower.includes('completed') || descLower.includes('submitted')) {
                valueClass = 'success';
            } else if (descLower.includes('pending') || descLower.includes('processing')) {
                valueClass = 'warning';
            } else if (descLower.includes('rejected') || descLower.includes('failed') || 
                       descLower.includes('error')) {
                valueClass = 'error';
            }
            
            return `
                <div class="agent-detail-item" style="grid-column: 1 / -1;">
                    <div class="agent-detail-value ${valueClass}">${desc}</div>
                </div>
            `;
        }).join('');
    }
    
    if (agentData.timestamp) {
        const date = new Date(agentData.timestamp * 1000);
        detailsHtml += `
            <div class="agent-detail-item">
                <div class="agent-detail-label">Processed At</div>
                <div class="agent-detail-value">${date.toLocaleString()}</div>
            </div>
        `;
    }
    
    detailsHtml += '</div>';
    
    content.innerHTML = detailsHtml;
    modal.classList.add('active');
}

// Update verdict section
function updateVerdict(status = 'approved') {
    const verdictCard = document.getElementById('verdictCard');
    const verdictIcon = document.getElementById('verdictIcon');
    const verdictTitle = document.getElementById('verdictTitle');
    const verdictMessage = document.getElementById('verdictMessage');
    
    // Remove any existing action buttons
    const existingActions = verdictCard.querySelector('.verdict-actions');
    if (existingActions) {
        existingActions.remove();
    }
    
    // Handle special statuses for CUST0001 and CUST0005
    if (status === 'incomplete') {
        verdictCard.className = 'verdict-card incomplete';
        verdictIcon.innerHTML = '<i class="fas fa-exclamation-circle"></i>';
        verdictTitle.textContent = 'DOCUMENT VERIFICATION INCOMPLETE';
        verdictMessage.textContent = `The loan application for ${applicationData?.customerName || 'Customer'} requires additional documents. Missing: Payslip June 2025. Please request the customer to submit the missing document.`;
        
        // Add Send Email button for CUST0001
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'verdict-actions';
        actionsDiv.innerHTML = `
            <button class="verdict-btn email-btn" onclick="sendDocumentRequestEmail()">
                <i class="fas fa-envelope"></i> Send Email to Customer
            </button>
        `;
        verdictCard.querySelector('.verdict-content').appendChild(actionsDiv);
        return;
    }
    
    if (status === 'suspicious') {
        verdictCard.className = 'verdict-card suspicious';
        verdictIcon.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
        verdictTitle.textContent = 'MANUAL REVIEW REQUIRED';
        verdictMessage.textContent = `The loan application for ${applicationData?.customerName || 'Customer'} has been flagged for suspicious activity. High-risk factors detected during underwriting. Manual approval or rejection is required.`;
        
        // Add Approve/Reject buttons for CUST0005
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'verdict-actions';
        actionsDiv.innerHTML = `
            <button class="verdict-btn approve-btn" onclick="approveApplication()">
                <i class="fas fa-check"></i> Approve Application
            </button>
            <button class="verdict-btn reject-btn" onclick="rejectApplication()">
                <i class="fas fa-times"></i> Reject Application
            </button>
        `;
        verdictCard.querySelector('.verdict-content').appendChild(actionsDiv);
        return;
    }
    
    // Check for real verdict from Cosmos data (look in audit record)
    let isApproved = true;
    let verdictSource = 'default';
    
    if (cosmosAgentData && cosmosAgentData.length > 0) {
        const auditRecord = cosmosAgentData.find(a => 
            a.agent_name && a.agent_name.toLowerCase().includes('audit')
        );
        
        if (auditRecord && auditRecord.agent_description) {
            // Check the descriptions for approval/rejection keywords
            const allDescriptions = auditRecord.agent_description.join(' ').toLowerCase();
            if (allDescriptions.includes('approved') || allDescriptions.includes('eligible')) {
                isApproved = true;
                verdictSource = 'cosmos';
            } else if (allDescriptions.includes('rejected') || allDescriptions.includes('denied')) {
                isApproved = false;
                verdictSource = 'cosmos';
            }
        }
    }
    
    console.log(`📋 Verdict determined from ${verdictSource}: ${isApproved ? 'APPROVED' : 'REJECTED'}`);
    
    if (isApproved) {
        verdictCard.className = 'verdict-card approved';
        verdictIcon.innerHTML = '<i class="fas fa-check-circle"></i>';
        verdictTitle.textContent = 'LOAN APPROVED';
        verdictMessage.textContent = `Congratulations! The loan application for ${applicationData?.customerName || 'Customer'} has been approved. The customer will receive the offer details shortly.`;
    } else {
        verdictCard.className = 'verdict-card rejected';
        verdictIcon.innerHTML = '<i class="fas fa-times-circle"></i>';
        verdictTitle.textContent = 'LOAN REJECTED';
        verdictMessage.textContent = `Unfortunately, the loan application for ${applicationData?.customerName || 'Customer'} has been rejected based on the evaluation criteria.`;
    }
}

// Create agent analysis card
function createAgentAnalysisCard(step, result) {
    const card = document.createElement('div');
    card.className = 'agent-analysis-card';
    
    let detailsHtml = '';
    if (result.details && result.details.length > 0) {
        detailsHtml = result.details.map(d => `
            <div class="agent-output-item">
                <div class="agent-output-label">${d.label}</div>
                <div class="agent-output-value">${d.value}</div>
            </div>
        `).join('');
    }
    
    card.innerHTML = `
        <div class="agent-card-header">
            <div class="agent-icon">${step.icon}</div>
            <div class="agent-info">
                <div class="agent-name">${step.title}</div>
                <div class="agent-role">${result.summary}</div>
            </div>
        </div>
        <div class="agent-card-body">
            <div class="agent-output">
                ${detailsHtml}
            </div>
        </div>
    `;
    
    // Add click handler to open modal
    card.onclick = () => openAgentModal(step, result);
    
    return card;
}

// Open agent details modal
function openAgentModal(step, result) {
    const modal = document.getElementById('agentModal');
    const icon = document.getElementById('agentModalIcon');
    const title = document.getElementById('agentModalTitle');
    const subtitle = document.getElementById('agentModalSubtitle');
    const content = document.getElementById('agentModalContent');
    
    icon.textContent = step.icon;
    title.textContent = step.title;
    subtitle.textContent = result.summary;
    
    // Build detailed content
    let detailsHtml = '<div class="agent-detail-grid">';
    if (result.details && result.details.length > 0) {
        detailsHtml += result.details.map(d => {
            // Determine value class based on content
            let valueClass = '';
            const valueLower = d.value.toLowerCase();
            if (valueLower.includes('✓') || valueLower.includes('verified') || valueLower.includes('approved') || valueLower.includes('passed') || valueLower.includes('excellent')) {
                valueClass = 'success';
            } else if (valueLower.includes('pending') || valueLower.includes('warning')) {
                valueClass = 'warning';
            } else if (valueLower.includes('rejected') || valueLower.includes('failed') || valueLower.includes('❌')) {
                valueClass = 'error';
            }
            
            return `
                <div class="agent-detail-item">
                    <div class="agent-detail-label">${d.label}</div>
                    <div class="agent-detail-value ${valueClass}">${d.value}</div>
                </div>
            `;
        }).join('');
    }
    detailsHtml += '</div>';
    
    content.innerHTML = detailsHtml;
    modal.classList.add('active');
}

// Close agent modal
function closeAgentModal() {
    const modal = document.getElementById('agentModal');
    modal.classList.remove('active');
}

// Notification system
function showNotification(type, title, message, duration = 4000) {
    const container = document.getElementById('notificationContainer');
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-times-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    notification.innerHTML = `
        <div class="notification-icon">
            <i class="fas ${icons[type]}"></i>
        </div>
        <div class="notification-content">
            <div class="notification-title">${title}</div>
            <div class="notification-message">${message}</div>
        </div>
    `;
    
    container.appendChild(notification);
    
    // Auto-remove after duration
    setTimeout(() => {
        notification.style.animation = 'slideInRight 0.3s ease reverse';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, duration);
}

// Close modal on escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeDocumentModal();
        closeAgentModal();
    }
});

// Close modal on overlay click
document.getElementById('documentModal')?.addEventListener('click', function(e) {
    if (e.target === this) {
        closeDocumentModal();
    }
});

document.getElementById('agentModal')?.addEventListener('click', function(e) {
    if (e.target === this) {
        closeAgentModal();
    }
});

// Send email for missing document (CUST0001)
function sendDocumentRequestEmail() {
    const btn = event.target.closest('.email-btn');
    const originalContent = btn.innerHTML;
    
    // Show sending state
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
    btn.disabled = true;
    
    // Simulate sending email
    setTimeout(() => {
        btn.innerHTML = '<i class="fas fa-check"></i> Email Sent';
        btn.classList.add('sent');
        
        showNotification('success', 'Email Sent', 
            `Document request email sent successfully to ${applicationData?.customerName || 'Customer'} at ${applicationData?.email || 'customer email'}.`);
    }, 1500);
}

// Approve application (CUST0005)
function approveApplication() {
    const actionsDiv = document.querySelector('.verdict-actions');
    
    // Disable both buttons
    actionsDiv.querySelectorAll('button').forEach(btn => btn.disabled = true);
    
    // Show processing
    const approveBtn = actionsDiv.querySelector('.approve-btn');
    approveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    
    setTimeout(() => {
        // Update verdict to approved
        const verdictCard = document.getElementById('verdictCard');
        const verdictIcon = document.getElementById('verdictIcon');
        const verdictTitle = document.getElementById('verdictTitle');
        const verdictMessage = document.getElementById('verdictMessage');
        
        verdictCard.className = 'verdict-card approved';
        verdictIcon.innerHTML = '<i class="fas fa-check-circle"></i>';
        verdictTitle.textContent = 'LOAN APPROVED (MANUAL OVERRIDE)';
        verdictMessage.textContent = `The loan application for ${applicationData?.customerName || 'Customer'} has been manually approved despite risk factors. Proceed with caution.`;
        
        // Update actions to show approved state
        actionsDiv.innerHTML = `
            <div class="verdict-decision approved">
                <i class="fas fa-check-circle"></i> Application Approved by Manual Review
            </div>
        `;
        
        showNotification('success', 'Application Approved', 
            `Loan application for ${applicationData?.customerName || 'Customer'} has been manually approved.`);
    }, 1500);
}

// Reject application (CUST0005)
function rejectApplication() {
    const actionsDiv = document.querySelector('.verdict-actions');
    
    // Disable both buttons
    actionsDiv.querySelectorAll('button').forEach(btn => btn.disabled = true);
    
    // Show processing
    const rejectBtn = actionsDiv.querySelector('.reject-btn');
    rejectBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    
    setTimeout(() => {
        // Update verdict to rejected
        const verdictCard = document.getElementById('verdictCard');
        const verdictIcon = document.getElementById('verdictIcon');
        const verdictTitle = document.getElementById('verdictTitle');
        const verdictMessage = document.getElementById('verdictMessage');
        
        verdictCard.className = 'verdict-card rejected';
        verdictIcon.innerHTML = '<i class="fas fa-times-circle"></i>';
        verdictTitle.textContent = 'LOAN REJECTED';
        verdictMessage.textContent = `The loan application for ${applicationData?.customerName || 'Customer'} has been rejected due to high-risk factors identified during underwriting review.`;
        
        // Update actions to show rejected state
        actionsDiv.innerHTML = `
            <div class="verdict-decision rejected">
                <i class="fas fa-times-circle"></i> Application Rejected - High Risk Factors
            </div>
        `;
        
        showNotification('error', 'Application Rejected', 
            `Loan application for ${applicationData?.customerName || 'Customer'} has been rejected.`);
    }, 1500);
}