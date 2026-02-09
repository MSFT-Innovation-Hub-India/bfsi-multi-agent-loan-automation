// Sample application data - Indian Customers
const applicationsData = {
    pending: [
        {
            id: 'CUST0241',
            customerName: 'Kala Divan',
            loanType: 'Home Loan',
            amount: 450000,
            submittedDate: '2025-09-25',
            priority: 'high',
            status: 'pending',
            email: 'kala.divan@email.com',
            phone: '+91 8712345678',
            creditScore: 735,
            income: 235000,
            employmentType: 'Other',
            requestedTerm: 300,
            panNumber: 'FHXXX1234X',
            aadharNumber: '4534-XXXX-XXXX',
            city: 'Udupi, KA',
            isCosmosData: true
        },
        {
            id: 'CUST0001',
            customerName: 'Rajesh Kumar Sharma',
            loanType: 'Home Loan',
            amount: 2500000,
            submittedDate: '2025-09-20',
            priority: 'high',
            status: 'pending',
            email: 'rajesh.sharma@email.com',
            phone: '+91 9876543210',
            creditScore: 750,
            income: 850000,
            employmentType: 'Full-time',
            requestedTerm: 240,
            panNumber: 'ABCDE1234F',
            aadharNumber: '1234-5678-9012',
            city: 'Noida, UP'
        },
        {
            id: 'CUST0002',
            customerName: 'Priya Patel',
            loanType: 'Personal Loan',
            amount: 500000,
            submittedDate: '2025-09-21',
            priority: 'medium',
            status: 'pending',
            email: 'priya.patel@email.com',
            phone: '+91 8765432109',
            creditScore: 720,
            income: 650000,
            employmentType: 'Full-time',
            requestedTerm: 36,
            panNumber: 'FGHIJ5678K',
            aadharNumber: '9876-5432-1098',
            city: 'Mumbai, MH',
            isCosmosData: true
        },
        
        {
            id: 'CUST0003',
            customerName: 'Amit Singh',
            loanType: 'Car Loan',
            amount: 800000,
            submittedDate: '2025-09-22',
            priority: 'low',
            status: 'pending',
            email: 'amit.singh@email.com',
            phone: '+91 7654321098',
            creditScore: 680,
            income: 750000,
            employmentType: 'Contract',
            requestedTerm: 60,
            panNumber: 'KLMNO9876P',
            aadharNumber: '5678-9012-3456',
            city: 'Bangalore, KA',
            isCosmosData: true
        },
        {
            id: 'CUST0005',
            customerName: 'Vikram Agarwal',
            loanType: 'Personal Loan',
            amount: 300000,
            submittedDate: '2025-09-23',
            priority: 'medium',
            status: 'pending',
            email: 'vikram.agarwal@email.com',
            phone: '+91 8877665544',
            creditScore: 700,
            income: 580000,
            employmentType: 'Full-time',
            requestedTerm: 48,
            panNumber: 'VIKAG5678V',
            aadharNumber: '3456-7890-1234',
            city: 'Delhi, DL'
        }
    ],
    reviewed: [
        {
            id: 'CUST0006',
            customerName: 'Anita Sharma',
            loanType: 'Home Loan',
            amount: 2800000,
            submittedDate: '2025-09-18',
            reviewedDate: '2025-09-19',
            priority: 'high',
            status: 'approved',
            email: 'anita.sharma@email.com',
            phone: '+91 9123456789',
            creditScore: 760,
            income: 950000,
            employmentType: 'Full-time',
            requestedTerm: 300,
            panNumber: 'ANSHA7890A',
            aadharNumber: '4567-8901-2345',
            city: 'Pune, MH'
        },
        {
            id: 'CUST0007',
            customerName: 'Rahul Gupta',
            loanType: 'Car Loan',
            amount: 650000,
            submittedDate: '2025-09-17',
            reviewedDate: '2025-09-18',
            priority: 'medium',
            status: 'rejected',
            email: 'rahul.gupta@email.com',
            phone: '+91 8234567890',
            creditScore: 620,
            income: 450000,
            employmentType: 'Part-time',
            requestedTerm: 60,
            panNumber: 'RAHGU4567R',
            aadharNumber: '6789-0123-4567',
            city: 'Gurgaon, HR'
        },
        {
            id: 'CUST0008',
            customerName: 'Kavita Joshi',
            loanType: 'Personal Loan',
            amount: 200000,
            submittedDate: '2025-09-16',
            reviewedDate: '2025-09-17',
            priority: 'low',
            status: 'approved',
            email: 'kavita.joshi@email.com',
            phone: '+91 7345678901',
            creditScore: 740,
            income: 620000,
            employmentType: 'Full-time',
            requestedTerm: 24,
            panNumber: 'KAVJO2345K',
            aadharNumber: '7890-1234-5678',
            city: 'Chennai, TN'
        }
    ]
};

let selectedApplication = null;

// Utility functions for masking sensitive data
function maskPAN(panNumber) {
    if (!panNumber || panNumber.length < 5) return panNumber;
    return panNumber.substring(0, 2) + 'XXX' + panNumber.substring(panNumber.length - 1);
}

function maskAadhar(aadharNumber) {
    if (!aadharNumber) return aadharNumber;
    return 'XXXX-XXXX-' + aadharNumber.substring(aadharNumber.length - 4);
}

function maskPhone(phoneNumber) {
    if (!phoneNumber) return phoneNumber;
    // For +91 XXXXXXXXXX format, show +91 XXXXX and last 4 digits
    const cleanNumber = phoneNumber.replace(/\s+/g, '');
    if (cleanNumber.startsWith('+91')) {
        return '+91 XXXXX' + cleanNumber.substring(cleanNumber.length - 4);
    }
    return phoneNumber.substring(0, 3) + 'XXXXX' + phoneNumber.substring(phoneNumber.length - 4);
}

function maskEmail(email) {
    if (!email || !email.includes('@')) return email;
    const [username, domain] = email.split('@');
    if (username.length <= 2) return email;
    return username.substring(0, 2) + 'XXXX@' + domain;
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    loadApplications();
});

// Load applications into the columns
function loadApplications() {
    loadPendingApplications();
    loadReviewedApplications();
    updateCountBadges();
}

// Load pending applications
function loadPendingApplications() {
    const container = document.getElementById('pendingApplications');
    container.innerHTML = '';

    if (applicationsData.pending.length === 0) {
        container.innerHTML = '<div class="loading"><i class="fas fa-info-circle"></i> No pending applications</div>';
        return;
    }

    applicationsData.pending.forEach(app => {
        const cardElement = createApplicationCard(app);
        container.appendChild(cardElement);
    });
}

// Load reviewed applications
function loadReviewedApplications() {
    const container = document.getElementById('reviewedApplications');
    container.innerHTML = '';

    if (applicationsData.reviewed.length === 0) {
        container.innerHTML = '<div class="loading"><i class="fas fa-info-circle"></i> No reviewed applications</div>';
        return;
    }

    applicationsData.reviewed.forEach(app => {
        const cardElement = createApplicationCard(app);
        container.appendChild(cardElement);
    });
}

// Create application card element
function createApplicationCard(app) {
    const card = document.createElement('div');
    card.className = 'application-card';
    card.onclick = () => openApplicationModal(app);

    const priorityClass = `priority-${app.priority}`;
    const statusClass = `status-${app.status}`;

    card.innerHTML = `
        <div class="card-header">
            <div class="application-id">${app.id}</div>
            <div class="application-status ${statusClass}">${app.status}</div>
        </div>
        <div class="card-info">
            <div class="info-item">
                <i class="fas fa-user"></i>
                <span>${app.customerName}</span>
            </div>
            <div class="info-item">
                <i class="fas fa-money-bill-wave"></i>
                <span>₹${app.amount.toLocaleString('en-IN')}</span>
            </div>
            <div class="info-item">
                <i class="fas fa-tag"></i>
                <span>${app.loanType}</span>
            </div>
            <div class="info-item">
                <i class="fas fa-chart-line"></i>
                <span>Score: ${app.creditScore}</span>
            </div>
        </div>
        <div class="card-footer">
            <div class="submitted-date">
                <i class="fas fa-calendar-alt"></i>
                Submitted: ${formatDate(app.submittedDate)}
            </div>
            <div class="${priorityClass}">
                <i class="fas fa-flag"></i>
                ${app.priority.toUpperCase()}
            </div>
        </div>
    `;

    return card;
}

// Open application modal
function openApplicationModal(app) {
    selectedApplication = app;
    const modal = document.getElementById('modalOverlay');
    const modalTitle = document.getElementById('modalTitle');
    const modalContent = document.getElementById('modalContent');
    const processBtn = document.getElementById('processBtn');

    modalTitle.textContent = `Application Details - ${app.id}`;
    modalContent.innerHTML = createApplicationDetails(app);

    // Show/hide process button based on status
    if (app.status === 'pending') {
        processBtn.style.display = 'flex';
        processBtn.innerHTML = '<i class="fas fa-arrow-right"></i> Process Application';
    } else {
        processBtn.style.display = 'none';
    }

    modal.classList.add('active');
}

// Close modal
function closeModal() {
    const modal = document.getElementById('modalOverlay');
    modal.classList.remove('active');
    selectedApplication = null;
}

// Create application details HTML
function createApplicationDetails(app) {
    const reviewedInfo = app.reviewedDate ? `
        <div class="detail-item">
            <div class="detail-label">Reviewed Date</div>
            <div class="detail-value">${formatDate(app.reviewedDate)}</div>
        </div>
    ` : '';

    return `
        <div class="application-details">
            <div class="detail-section">
                <h4><i class="fas fa-user"></i> Customer Information</h4>
                <div class="detail-grid">
                    <div class="detail-item">
                        <div class="detail-label">Customer Name</div>
                        <div class="detail-value">${app.customerName}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Email</div>
                        <div class="detail-value masked-data">${maskEmail(app.email)}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Phone</div>
                        <div class="detail-value masked-data">${maskPhone(app.phone)}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">City</div>
                        <div class="detail-value">${app.city}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">PAN Number</div>
                        <div class="detail-value masked-data">${maskPAN(app.panNumber)}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Aadhar Number</div>
                        <div class="detail-value masked-data">${maskAadhar(app.aadharNumber)}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Employment Type</div>
                        <div class="detail-value">${app.employmentType}</div>
                    </div>
                </div>
            </div>

            <div class="detail-section">
                <h4><i class="fas fa-money-bill-wave"></i> Loan Information</h4>
                <div class="detail-grid">
                    <div class="detail-item">
                        <div class="detail-label">Loan Type</div>
                        <div class="detail-value">${app.loanType}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Loan Amount</div>
                        <div class="detail-value">₹${app.amount.toLocaleString('en-IN')}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Requested Term</div>
                        <div class="detail-value">${app.requestedTerm} months</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Annual Income</div>
                        <div class="detail-value">₹${app.income.toLocaleString('en-IN')}</div>
                    </div>
                </div>
            </div>

            <div class="detail-section">
                <h4><i class="fas fa-chart-line"></i> Assessment Information</h4>
                <div class="detail-grid">
                    <div class="detail-item">
                        <div class="detail-label">Credit Score</div>
                        <div class="detail-value">${app.creditScore}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Priority</div>
                        <div class="detail-value priority-${app.priority}">${app.priority.toUpperCase()}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Status</div>
                        <div class="detail-value status-${app.status}">${app.status.toUpperCase()}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Submitted Date</div>
                        <div class="detail-value">${formatDate(app.submittedDate)}</div>
                    </div>
                    ${reviewedInfo}
                </div>
            </div>
            
            <div class="sensitive-data-note">
                <i class="fas fa-shield-alt"></i>
                <span>Sensitive information (PAN, Aadhar, Email, Phone) has been masked for privacy and security.</span>
            </div>
        </div>
    `;
}

// Process application - redirect to process application page with tabs
async function processApplication() {
    if (selectedApplication) {
        // Store application data in session storage for the process page
        sessionStorage.setItem('selectedApplication', JSON.stringify(selectedApplication));
        
        // Check if this application needs Cosmos DB data
        if (selectedApplication.isCosmosData) {
            try {
                showLoadingIndicator('Fetching application data...');
                
                // Fetch data from Cosmos DB and store in localStorage
                const cosmosData = await fetchCosmosData(selectedApplication.id);
                localStorage.setItem(`cosmosData_${selectedApplication.id}`, JSON.stringify(cosmosData));
                
                hideLoadingIndicator();
                
                // Redirect to process application page
                window.location.href = `/process-application?id=${selectedApplication.id}&cosmosData=true`;
            } catch (error) {
                console.error('Error fetching Cosmos data:', error);
                hideLoadingIndicator();
                
                // Continue with process page even if Cosmos fails
                window.location.href = `/process-application?id=${selectedApplication.id}`;
            }
        } else {
            // Redirect to process application page
            window.location.href = `/process-application?id=${selectedApplication.id}`;
        }
    }
}

// Refresh applications
function refreshApplications() {
    // Show loading state
    const pendingContainer = document.getElementById('pendingApplications');
    const reviewedContainer = document.getElementById('reviewedApplications');
    
    pendingContainer.innerHTML = '<div class="loading"><i class="fas fa-spinner"></i> Loading applications...</div>';
    reviewedContainer.innerHTML = '<div class="loading"><i class="fas fa-spinner"></i> Loading applications...</div>';

    // Simulate API call delay
    setTimeout(() => {
        loadApplications();
    }, 1000);
}

// Update count badges
function updateCountBadges() {
    document.getElementById('pendingCount').textContent = applicationsData.pending.length;
    document.getElementById('reviewedCount').textContent = applicationsData.reviewed.length;
}

// Fetch real-time data from Cosmos DB via Flask API
async function fetchCosmosData(customerId) {
    try {
        console.log(`\n🔍 JAVASCRIPT: Starting data fetch for customer: ${customerId}`);
        console.log(`🌐 JAVASCRIPT: Calling Flask API endpoint: /api/cosmos-data/${customerId}`);
        
        // Call Flask API endpoint for Cosmos data
        const response = await fetch(`/api/cosmos-data/${customerId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log(`📡 JAVASCRIPT: Flask API Response:`, result);
        
        if (result.success) {
            if (result.source === 'cosmos') {
                console.log(`✅ JAVASCRIPT: REAL COSMOS API DATA RECEIVED for ${customerId}`);
                console.log(`📊 JAVASCRIPT: ${result.message}`);
                console.log(`🎯 JAVASCRIPT: Data source: EXTERNAL COSMOS DB API`);
            } else {
                console.log(`🔄 JAVASCRIPT: MOCK FALLBACK DATA RECEIVED for ${customerId}`);
                console.log(`📊 JAVASCRIPT: ${result.message}`);
                console.log(`🎯 JAVASCRIPT: Data source: MOCK DATA (External API failed)`);
            }
            console.log(`📋 JAVASCRIPT: Full data:`, result.data);
            return result.data;
        } else {
            throw new Error('Failed to fetch cosmos data');
        }
        
    } catch (error) {
        console.error('🚨 JAVASCRIPT: Error fetching Cosmos data:', error);
        
        // Fallback: Return mock data structure matching Cosmos format
        console.log('🔄 JAVASCRIPT: FALLING BACK TO CLIENT-SIDE MOCK DATA');
        console.log('🎯 JAVASCRIPT: Data source: CLIENT-SIDE MOCK (Network/API error)');
        return getMockCosmosData(customerId);
    }
}

// Mock data structure matching the exact Cosmos DB response format
function getMockCosmosData(customerId) {
    // Return different mock data based on customer ID
    
    if (customerId === 'CUST0002') {
        return [
            {
                "id": "ApplicationAssistAgent-CUST0002 - agent",
                "agent_id": "CUST0002-agent",
                "agent_name": "ApplicationAssist Agent",
                "customer_id": "CUST0002",
                "agent_description": ["Captured details Priya Patel", "Recorded loan ₹5XX,XXX", "Submitted application APP1XX"],
                "_rid": "lyxLAMjqOZoxAQAAAAAAAA==",
                "_self": "dbs/lyxLAA==/colls/lyxLAMjqOZo=/docs/lyxLAMjqOZoxAQAAAAAAAA==/",
                "_etag": "\"e700afc2-0000-0800-0000-68dcb8540000\"",
                "_attachments": "attachments/",
                "_ts": 1759295572
            },
            {
                "id": "DocumentCheckerAgent-CUST0002 - agent",
                "agent_id": "CUST0002-agent",
                "agent_name": "DocumentChecker Agent",
                "customer_id": "CUST0002",
                "agent_description": ["Verified KYC docs", "Checked Aadhar XXXX1098", "Checked PAN FGXXXK"],
                "_rid": "lyxLAMjqOZoyAQAAAAAAAA==",
                "_self": "dbs/lyxLAA==/colls/lyxLAMjqOZo=/docs/lyxLAMjqOZoyAQAAAAAAAA==/",
                "_etag": "\"e700f8c6-0000-0800-0000-68dcb86f0000\"",
                "_attachments": "attachments/",
                "_ts": 1759295599
            },
            {
                "id": "PreQualificationAgent-CUST0002 - agent",
                "agent_id": "CUST0002-agent",
                "agent_name": "PreQualification Agent",
                "customer_id": "CUST0002",
                "agent_description": ["Analyzed income ₹6XX,XXX", "Checked credit 72X", "Marked eligible"],
                "_rid": "lyxLAMjqOZozAQAAAAAAAA==",
                "_self": "dbs/lyxLAA==/colls/lyxLAMjqOZo=/docs/lyxLAMjqOZozAQAAAAAAAA==/",
                "_etag": "\"e70078c8-0000-0800-0000-68dcb87e0000\"",
                "_attachments": "attachments/",
                "_ts": 1759295614
            },
            {
                "id": "Audit-CUST0002 - agent",
                "agent_id": "CUST0002-audit",
                "agent_name": "Audit Record",
                "customer_id": "CUST0002",
                "agent_description": ["ApplicationAssist: Captured details, recorded loan, submitted APP1XX", "DocumentChecker: Verified KYC, checked Aadhar, checked PAN", "PreQualification: Analyzed income, checked credit, marked eligible", "Final Status: Loan approved and communicated"],
                "_rid": "lyxLAMjqOZo5AQAAAAAAAA==",
                "_self": "dbs/lyxLAA==/colls/lyxLAMjqOZo=/docs/lyxLAMjqOZo5AQAAAAAAAA==/",
                "_etag": "\"e70079da-0000-0800-0000-68dcb90d0000\"",
                "_attachments": "attachments/",
                "_ts": 1759295757
            }
        ];
    }
    
    if (customerId === 'CUST0003') {
        return [
            {
                "id": "ApplicationAssistAgent-CUST0003 - agent",
                "agent_id": "CUST0003-agent",
                "agent_name": "ApplicationAssist Agent",
                "customer_id": "CUST0003",
                "agent_description": ["Captured details Amit Singh", "Recorded loan ₹8XX,XXX", "Submitted application APP2XX"],
                "_rid": "lyxLAMjqOZo6AQAAAAAAAA==",
                "_self": "dbs/lyxLAA==/colls/lyxLAMjqOZo=/docs/lyxLAMjqOZo6AQAAAAAAAA==/",
                "_etag": "\"e70064ed-0000-0800-0000-68dcb9950000\"",
                "_attachments": "attachments/",
                "_ts": 1759295893
            },
            {
                "id": "DocumentCheckerAgent-CUST0003 - agent",
                "agent_id": "CUST0003-agent",
                "agent_name": "DocumentChecker Agent",
                "customer_id": "CUST0003",
                "agent_description": ["Verified KYC docs", "Checked Aadhar XXXX3456", "Checked PAN KLXXXP", "Checked all the documents"],
                "_rid": "lyxLAMjqOZo7AQAAAAAAAA==",
                "_self": "dbs/lyxLAA==/colls/lyxLAMjqOZo=/docs/lyxLAMjqOZo7AQAAAAAAAA==/",
                "_etag": "\"e700eff2-0000-0800-0000-68dcb9c40000\"",
                "_attachments": "attachments/",
                "_ts": 1759295940
            },
            {
                "id": "PreQualificationAgent-CUST0003 - agent",
                "agent_id": "CUST0003-agent",
                "agent_name": "PreQualification Agent",
                "customer_id": "CUST0003",
                "agent_description": ["Analyzed income ₹7XX,XXX", "Checked credit 68X", "Marked eligible"],
                "_rid": "lyxLAMjqOZo8AQAAAAAAAA==",
                "_self": "dbs/lyxLAA==/colls/lyxLAMjqOZo=/docs/lyxLAMjqOZo8AQAAAAAAAA==/",
                "_etag": "\"e700adf6-0000-0800-0000-68dcb9d90000\"",
                "_attachments": "attachments/",
                "_ts": 1759295961
            },
            {
                "id": "ValuationAgent-CUST0003 - agent",
                "agent_id": "CUST0003-agent",
                "agent_name": "Valuation Agent",
                "customer_id": "CUST0003",
                "agent_description": ["Initiated car valuation", "Estimated value ₹8XX,XXX", "Confirmed ownership"],
                "_rid": "lyxLAMjqOZo9AQAAAAAAAA==",
                "_self": "dbs/lyxLAA==/colls/lyxLAMjqOZo=/docs/lyxLAMjqOZo9AQAAAAAAAA==/",
                "_etag": "\"e70079f8-0000-0800-0000-68dcb9ea0000\"",
                "_attachments": "attachments/",
                "_ts": 1759295978
            },
            {
                "id": "Audit-CUST0003 - agent",
                "agent_id": "CUST0003-audit",
                "agent_name": "Audit Record",
                "customer_id": "CUST0003",
                "agent_description": ["ApplicationAssist: Captured details, recorded loan, submitted APP2XX", "DocumentChecker: Verified KYC, checked Aadhar, checked PAN", "PreQualification: Analyzed income, checked credit, marked eligible", "Valuation: Initiated car valuation, estimated ₹8XX,XXX, confirmed ownership", "Final Status: Loan approved and communicated"],
                "_rid": "lyxLAMjqOZpCAQAAAAAAAA==",
                "_self": "dbs/lyxLAA==/colls/lyxLAMjqOZo=/docs/lyxLAMjqOZpCAQAAAAAAAA==/",
                "_etag": "\"e8001b04-0000-0800-0000-68dcba440000\"",
                "_attachments": "attachments/",
                "_ts": 1759296068
            }
        ];
    }
    
    // Default CUST0241 data (existing)
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
            ],
            "_rid": "lyxLAMjqOZooAQAAAAAAAA==",
            "_self": "dbs/lyxLAA==/colls/lyxLAMjqOZo=/docs/lyxLAMjqOZooAQAAAAAAAA==/",
            "_etag": "\"1100e575-0000-0800-0000-68d272c10000\"",
            "_attachments": "attachments/",
            "_ts": 1758622401
        },
        {
            "id": "DocumentCheckerAgent-CUST0241 - agent",
            "agent_id": "CUST0241-agent",
            "agent_name": "DocumentChecker Agent",
            "customer_id": "CUST0241",
            "agent_description": [
                "Initiated KYC verification using Aadhar (XXXX XXXX 4534), PAN (CHQXXXXXX), and DOB (XX/XX/19XX).",
                "Verified document set:",
                "Aadhar (XXXX XXXX 4534)",
                "PAN(CHQXXXXXX)",
                "salary slips",
                "income certificate",
                "land records",
                "CIBIL report",
                "bank statements",
                "Form 16",
                "birth certificate.",
                "Updated verification status in document tracking system.",
                "Output: Document verification marked complete ."
            ],
            "_rid": "lyxLAMjqOZopAQAAAAAAAA==",
            "_self": "dbs/lyxLAA==/colls/lyxLAMjqOZo=/docs/lyxLAMjqOZopAQAAAAAAAA==/",
            "_etag": "\"1100f075-0000-0800-0000-68d273000000\"",
            "_attachments": "attachments/",
            "_ts": 1758622464
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
            ],
            "_rid": "lyxLAMjqOZoqAQAAAAAAAA==",
            "_self": "dbs/lyxLAA==/colls/lyxLAMjqOZo=/docs/lyxLAMjqOZoqAQAAAAAAAA==/",
            "_etag": "\"1100f675-0000-0800-0000-68d273090000\"",
            "_attachments": "attachments/",
            "_ts": 1758622473
        },
        {
            "id": "ValuationAgent-CUST0241 - agent",
            "agent_id": "CUST0241-agent",
            "agent_name": "Valuation Agent",
            "customer_id": "CUST0241",
            "agent_description": [
                "Initiated property valuation for address: House No. XX, Pandya Zilla, Udupi.",
                "estimated value: ₹6XXXXX.",
                "Confirmed property match against submitted ownership documents.",
                "Output: Property valuation recorded."
            ],
            "_rid": "lyxLAMjqOZorAQAAAAAAAA==",
            "_self": "dbs/lyxLAA==/colls/lyxLAMjqOZo=/docs/lyxLAMjqOZorAQAAAAAAAA==/",
            "_etag": "\"1100f975-0000-0800-0000-68d273120000\"",
            "_attachments": "attachments/",
            "_ts": 1758622482
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
            ],
            "_rid": "lyxLAMjqOZosAQAAAAAAAA==",
            "_self": "dbs/lyxLAA==/colls/lyxLAMjqOZo=/docs/lyxLAMjqOZosAQAAAAAAAA==/",
            "_etag": "\"1100fa75-0000-0800-0000-68d2731e0000\"",
            "_attachments": "attachments/",
            "_ts": 1758622494
        },
        {
            "id": "UnderwritingAgent-CUST0241 - agent",
            "agent_id": "CUST0241-agent",
            "agent_name": "Underwriting Agent",
            "customer_id": "CUST0241",
            "agent_description": [
                "Checked eligibility against policy exceptions and risk flags.",
                "Approved loan .",
                "Output: Loan underwriting complete with decision status (Approved)."
            ],
            "_rid": "lyxLAMjqOZotAQAAAAAAAA==",
            "_self": "dbs/lyxLAA==/colls/lyxLAMjqOZo=/docs/lyxLAMjqOZotAQAAAAAAAA==/",
            "_etag": "\"1100fc75-0000-0800-0000-68d273260000\"",
            "_attachments": "attachments/",
            "_ts": 1758622502
        },
        {
            "id": "OfferGenerationAgent-CUST0241 - agent",
            "agent_id": "CUST0241-agent",
            "agent_name": "OfferGeneration Agent",
            "customer_id": "CUST0241",
            "agent_description": [
                "Created personalized loan offer.",
                "Packaged offer document and offer ID for dispatch.",
                "Output: Offer generated and sent to communication system."
            ],
            "_rid": "lyxLAMjqOZouAQAAAAAAAA==",
            "_self": "dbs/lyxLAA==/colls/lyxLAMjqOZo=/docs/lyxLAMjqOZouAQAAAAAAAA==/",
            "_etag": "\"1100fd75-0000-0800-0000-68d2732f0000\"",
            "_attachments": "attachments/",
            "_ts": 1758622511
        },
        {
            "id": "CustomerCommunicationAgent-CUST0241 - agent",
            "agent_id": "CUST0241-agent",
            "agent_name": "CustomerCommunication Agent",
            "customer_id": "CUST0241",
            "agent_description": [
                "Sent acknowledgement, requested documents, and confirmed KYC done",
                "Shared application number and loan offer, all communication recorded with timestamp"
            ],
            "_rid": "lyxLAMjqOZovAQAAAAAAAA==",
            "_self": "dbs/lyxLAA==/colls/lyxLAMjqOZo=/docs/lyxLAMjqOZovAQAAAAAAAA==/",
            "_etag": "\"11000876-0000-0800-0000-68d2739e0000\"",
            "_attachments": "attachments/",
            "_ts": 1758622622
        },
        {
            "id": "Audit-CUST0241 - agent",
            "agent_id": "CUST0241-audit",
            "agent_name": "Audit Record",
            "customer_id": "CUST0241",
            "agent_description": [
                "PreQualification Agent: Analyzed income (₹23XXXX/month) and employment status (Other). Marked customer pre-qualified.",
                "ApplicationAssist Agent: Extracted customer details and submitted loan application (APPXXXX).",
                "DocumentChecker Agent: Performed KYC and verified documents including ID proofs, income proofs, land records, and bank statements. Marked verification complete.",
                "Valuation Agent: Conducted property valuation for House No. XX, Pandya Zilla, Udupi with estimated value ₹6XXXXX. Confirmed ownership documents.",
                "CreditAssessor Agent: Reviewed bank and credit card statements, checked defaults, and evaluated EMI affordability (Income: ₹23XXXX vs EMI: ₹3XXX).",
                "Underwriting Agent: Checked eligibility against policies and risk flags. Loan approved.",
                "OfferGeneration Agent: Created personalized loan offer (₹4XXXXX, 25 years, 7.25% interest). Packaged and dispatched offer.",
                "CustomerCommunication Agent: Sent acknowledgement, requested documents, confirmed KYC, and shared application number and loan offer. All communications recorded with timestamps.",
                "Final Status: Loan application processed end-to-end, approved, and communicated to customer."
            ],
            "_rid": "lyxLAMjqOZowAQAAAAAAAA==",
            "_self": "dbs/lyxLAA==/colls/lyxLAMjqOZo=/docs/lyxLAMjqOZowAQAAAAAAAA==/",
            "_etag": "\"11001c76-0000-0800-0000-68d2748e0000\"",
            "_attachments": "attachments/",
            "_ts": 1758622862
        }
    ];
}

// Show loading indicator
function showLoadingIndicator(message = 'Loading...') {
    const overlay = document.getElementById('modalOverlay');
    overlay.innerHTML = `
        <div class="modal loading-modal">
            <div class="loading-content">
                <div class="spinner"></div>
                <p>${message}</p>
            </div>
        </div>
    `;
    overlay.style.display = 'flex';
}

// Hide loading indicator
function hideLoadingIndicator() {
    document.getElementById('modalOverlay').style.display = 'none';
}

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Close modal when clicking outside
document.getElementById('modalOverlay').addEventListener('click', function(e) {
    if (e.target === this) {
        closeModal();
    }
});

// Handle escape key to close modal
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeModal();
    }
});

// Function to get application by ID (for use by workflow page)
function getApplicationById(id) {
    // Search in both pending and reviewed applications
    const allApps = [...applicationsData.pending, ...applicationsData.reviewed];
    return allApps.find(app => app.id === id);
}

// Export function for use in other files
window.getApplicationById = getApplicationById;