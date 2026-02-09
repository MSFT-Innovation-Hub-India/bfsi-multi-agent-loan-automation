// Bank Loan Workflow JavaScript - Based on Wireframe
// Complete rewrite following the exact wireframe structure

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

class BankLoanWorkflow {
    constructor() {
        this.currentStep = 0;
        this.completedSteps = new Set();
        this.branchStepsCompleted = new Set();
        this.workflowContainer = null;
        this.progressIndicator = null;
        this.autoProcessing = false;
        this.autoProcessInterval = null;
        this.currentAutoStep = 0;
        
        // Auto process sequence
        this.autoSequence = [
            'customer-service',
            'document-verification', 
            'credit-qualification',
            'credit-assessment',
            'asset-valuation',
            'underwriting',
            'offer-generation',
            'customer-communication',
            'audit'
        ];
        
        // Indian customer database
        this.customerDatabase = {
            'CUST0001': {
                name: 'राजेश कुमार शर्मा (Rajesh Kumar Sharma)',
                mobile: '+91 98765 43210',
                email: 'rajesh.sharma@email.com',
                aadhar: '1234 5678 9012',
                pan: 'ABCDE1234F',
                address: '123, Sector 62, Noida, Uttar Pradesh - 201309',
                loanAmount: '₹25,00,000',
                purpose: 'Home Purchase',
                income: '₹8,50,000 per annum',
                employer: 'Infosys Limited',
                cibil: '750',
                property: '3BHK Apartment in Sector 62, Noida',
                propertyValue: '₹45,00,000',
                incompleteDocuments: true,
                missingDocument: 'Payslip June 2025'
            },
            'CUST0002': {
                name: 'प्रिया पटेल (Priya Patel)',
                mobile: '+91 87654 32109',
                email: 'priya.patel@email.com',
                aadhar: '9876 5432 1098',
                pan: 'FGHIJ5678K',
                address: '456, Bandra West, Mumbai, Maharashtra - 400050',
                loanAmount: '₹5,00,000',
                purpose: 'Personal Loan',
                income: '₹6,50,000 per annum',
                employer: 'TCS Limited',
                cibil: '720',
                property: 'N/A',
                propertyValue: 'N/A'
            },
            'CUST0003': {
                name: 'अमित सिंह (Amit Singh)',
                mobile: '+91 76543 21098',
                email: 'amit.singh@email.com',
                aadhar: '5678 9012 3456',
                pan: 'KLMNO9876P',
                address: '789, Koramangala, Bangalore, Karnataka - 560034',
                loanAmount: '₹8,00,000',
                purpose: 'Car Loan',
                income: '₹7,50,000 per annum',
                employer: 'Wipro Technologies',
                cibil: '680',
                property: 'N/A',
                propertyValue: 'N/A'
            },
            
            'CUST0005': {
                name: 'विक्रम अग्रवाल (Vikram Agarwal)',
                mobile: '+91 88776 65544',
                email: 'vikram.agarwal@email.com',
                aadhar: '3456 7890 1234',
                pan: 'VIKAG5678V',
                address: '202, Connaught Place, New Delhi, Delhi - 110001',
                loanAmount: '₹3,00,000',
                purpose: 'Personal Loan',
                income: '₹5,80,000 per annum',
                employer: 'HCL Technologies',
                cibil: '700',
                property: 'N/A',
                propertyValue: 'N/A',
                suspiciousUnderwriting: true,
                suspiciousReasons: [
                    'Recent job change (3 months ago) - employment stability concern',
                    'High debt-to-income ratio (45%) - above acceptable threshold',
                    'Multiple credit inquiries (8) in last 6 months',
                    'Irregular income deposits in bank statements',
                    'Previous loan default 2 years ago (settled but flagged)'
                ],
                underwritingDecision: null
            },
            'CUST0241': {
                name: 'कला दिवान (Kala Divan)',
                mobile: '+91 87123 45678',
                email: 'kala.divan@email.com',
                aadhar: 'XXXX XXXX 4534',
                pan: 'CHQXJ4150W',
                address: 'House No. XX, Pandya Zilla, Udupi, Karnataka - 576101',
                loanAmount: '₹4,50,000',
                purpose: 'Home Loan',
                income: '₹2,35,000 per annum',
                employer: 'Other',
                cibil: '735',
                property: 'Residential Property in Udupi',
                propertyValue: '₹6,50,000'
            }
        };
        
        // Current customer data (will be set based on customer ID)
        this.customerData = null;
        
        // Workflow steps based on wireframe
        this.workflowSteps = [
            {
                id: 'customer-service',
                title: 'Customer Service Agent',
                description: 'Assists customers with form completion and provides information',
                icon: '🎧',
                type: 'single'
            },
            {
                id: 'document-verification',
                title: 'Document Verification Agent',
                description: 'Verifies customer KYC documents and ensures completeness',
                icon: '📋',
                type: 'single'
            },
            {
                id: 'credit-qualification',
                title: 'Credit Qualification Agent',
                description: 'Reviews initial credit requirements and eligibility',
                icon: '📊',
                type: 'single'
            },
            {
                id: 'branching-section',
                title: 'Parallel Processing',
                description: 'Two agents work simultaneously',
                type: 'branch',
                branches: [
                    {
                        id: 'credit-assessment',
                        title: 'Credit Assessment Agent',
                        description: 'Performs detailed credit analysis and risk evaluation',
                        icon: '💳'
                    },
                    {
                        id: 'asset-valuation',
                        title: 'Asset Valuation Agent',
                        description: 'Evaluates collateral and asset worth for loan security',
                        icon: '🏠'
                    }
                ]
            },
            {
                id: 'underwriting',
                title: 'Underwriting Agent',
                description: 'Makes final loan approval decisions based on all assessments',
                icon: '✍️',
                type: 'single'
            },
            {
                id: 'horizontal-section',
                title: 'Final Processing',
                description: 'Final steps in horizontal layout',
                type: 'horizontal',
                steps: [
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
                ]
            }
        ];
        
        this.init();
    }
    
    init() {
        this.createWorkflowStructure();
        this.createProgressIndicator();
        this.startWorkflow();
    }
    
    createWorkflowStructure() {
        const container = document.getElementById('workflow-grid');
        if (!container) {
            console.error('Workflow container not found');
            return;
        }
        
        this.workflowContainer = container;
        container.innerHTML = '';
        
        this.workflowSteps.forEach((step, index) => {
            if (step.type === 'single') {
                this.createSingleAgent(step);
                if (index < this.workflowSteps.length - 1) {
                    this.createVerticalArrow(`arrow-${index}`);
                }
            } else if (step.type === 'branch') {
                this.createBranchingSection(step);
            } else if (step.type === 'horizontal') {
                this.createHorizontalSection(step);
            }
        });
    }
    
    createSingleAgent(step) {
        const agentCard = this.createAgentCard(step);
        this.workflowContainer.appendChild(agentCard);
    }
    
    createAgentCard(agent) {
        const card = document.createElement('div');
        card.className = 'agent-card';
        card.setAttribute('data-agent', agent.id);
        
        card.innerHTML = `
            <div class="agent-icon">${agent.icon}</div>
            <h3>${agent.title}</h3>
            <div class="agent-status">✓ Completed</div>
            <div class="agent-actions">
                <button class="btn btn-secondary details-btn" id="details-${agent.id}" onclick="workflowInstance.showAgentDetails('${agent.id}')" disabled title="Process the agent first to see details">
                    ℹ️ Details
                </button>
                <button class="btn btn-success process-btn" id="process-${agent.id}" onclick="workflowInstance.processAgent('${agent.id}')">
                    ▶️ Process
                </button>
            </div>
        `;
        
        return card;
    }
    
    createVerticalArrow(id) {
        const arrow = document.createElement('div');
        arrow.className = 'flow-arrow';
        arrow.id = id;
        this.workflowContainer.appendChild(arrow);
        return arrow;
    }
    
    createBranchingSection(step) {
        // Create branching arrows
        const branchingArrows = document.createElement('div');
        branchingArrows.className = 'branching-arrows';
        branchingArrows.id = 'branching-arrows';
        branchingArrows.innerHTML = `
            <div class="branch-arrow-left"></div>
            <div class="branch-arrow-right"></div>
        `;
        this.workflowContainer.appendChild(branchingArrows);
        
        // Create branching section container
        const branchingContainer = document.createElement('div');
        branchingContainer.className = 'branching-section';
        branchingContainer.id = 'branching-section';
        
        // Add branch agents
        step.branches.forEach(branch => {
            const branchCard = this.createAgentCard(branch);
            branchingContainer.appendChild(branchCard);
        });
        
        this.workflowContainer.appendChild(branchingContainer);
        
        // Create convergence arrows
        const convergenceArrows = document.createElement('div');
        convergenceArrows.className = 'convergence-arrows';
        convergenceArrows.id = 'convergence-arrows';
        convergenceArrows.innerHTML = `
            <div class="converge-arrow-left"></div>
            <div class="converge-arrow-right"></div>
        `;
        this.workflowContainer.appendChild(convergenceArrows);
    }
    
    createHorizontalSection(step) {
        const horizontalContainer = document.createElement('div');
        horizontalContainer.className = 'horizontal-flow';
        horizontalContainer.id = 'horizontal-section';
        
        step.steps.forEach((horizontalStep, index) => {
            const stepCard = this.createAgentCard(horizontalStep);
            horizontalContainer.appendChild(stepCard);
            
            // Add horizontal arrow between steps (except after last step)
            if (index < step.steps.length - 1) {
                const horizontalArrow = document.createElement('div');
                horizontalArrow.className = 'horizontal-arrow';
                horizontalArrow.id = `horizontal-arrow-${index}`;
                horizontalContainer.appendChild(horizontalArrow);
            }
        });
        
        this.workflowContainer.appendChild(horizontalContainer);
    }
    
    createProgressIndicator() {
        const progressDiv = document.createElement('div');
        progressDiv.className = 'progress-indicator';
        progressDiv.innerHTML = `
            <h4>Workflow Progress</h4>
            <div class="progress-step" data-step="customer-service">Customer Service</div>
            <div class="progress-step" data-step="document-verification">Document Verification</div>
            <div class="progress-step" data-step="credit-qualification">Credit Qualification</div>
            <div class="progress-step" data-step="credit-assessment">Credit Assessment</div>
            <div class="progress-step" data-step="asset-valuation">Asset Valuation</div>
            <div class="progress-step" data-step="underwriting">Underwriting</div>
            <div class="progress-step" data-step="offer-generation">Offer Generation</div>
            <div class="progress-step" data-step="customer-communication">Customer Communication</div>
            <div class="progress-step" data-step="audit">Audit</div>
        `;
        
        document.body.appendChild(progressDiv);
        this.progressIndicator = progressDiv;
    }
    
    startWorkflow() {
        // Don't auto-start workflow, wait for customer ID input
        console.log('Workflow initialized, waiting for customer ID...');
    }

    // Get customer data by ID
    getCustomerData(customerId) {
        const customer = this.customerDatabase[customerId];
        if (customer) {
            return { ...customer, customerId: customerId };
        }
        
        // Return default customer data if ID not found
        return {
            customerId: customerId,
            name: 'ग्राहक (Customer)',
            mobile: '+91 XXXXX XXXXX',
            email: 'customer@email.com',
            aadhar: 'XXXX XXXX XXXX',
            pan: 'XXXXX XXXXX',
            address: 'Customer Address',
            loanAmount: '₹X,XX,XXX',
            purpose: 'Loan Purpose',
            income: '₹X,XX,XXX per annum',
            employer: 'Employer Name',
            cibil: 'XXX',
            property: 'Property Details',
            propertyValue: '₹X,XX,XXX'
        };
    }

    startWorkflowWithCustomerId() {
        const customerIdInput = document.getElementById('customerIdInput');
        const customerId = customerIdInput.value.trim().toUpperCase();
        
        if (!customerId) {
            this.showNotification('warning', 'Customer ID Required', 'Please enter a Customer ID to start the workflow.');
            customerIdInput.focus();
            return;
        }
        
        if (customerId.length < 6) {
            this.showNotification('error', 'Invalid Customer ID', 'Customer ID should be at least 6 characters long (e.g., CUST0001).');
            customerIdInput.focus();
            return;
        }
        
        // Load customer data based on the entered ID
        this.customerData = this.getCustomerData(customerId);
        
        // Hide the input section and show auto-process controls
        document.querySelector('.customer-input-section').style.display = 'none';
        document.getElementById('autoProcessControls').style.display = 'flex';
        
        // Show only the first agent initially with realistic timing
        setTimeout(() => {
            this.showAgent('customer-service');
            this.updateProgress('customer-service', 'active');
        }, 1500);
        
        // Show success notification
        setTimeout(() => {
            this.showNotification('success', 'Workflow Started Successfully! 🚀', 
                `Loan processing initiated for <strong>Customer ID: ${customerId}</strong><br>
                Customer: <strong>${this.customerData.name}</strong><br>
                Loan Amount: <strong>${this.customerData.loanAmount}</strong>`);
        }, 500);
    }
    
    showAgent(agentId) {
        const agent = document.querySelector(`[data-agent="${agentId}"]`);
        if (agent) {
            setTimeout(() => {
                agent.classList.add('visible', 'animate-slide-up');
                console.log(`Agent shown: ${agentId}`);
            }, 300);
        }
    }
    
    hideAllAgentsExcept(exceptIds = []) {
        const allAgents = document.querySelectorAll('.agent-card');
        allAgents.forEach(agent => {
            const agentId = agent.getAttribute('data-agent');
            if (!exceptIds.includes(agentId)) {
                agent.classList.remove('visible');
            }
        });
    }
    
    processAgent(agentId) {
        console.log(`Processing agent: ${agentId}`);
        
        // Show processing state
        const agent = document.querySelector(`[data-agent="${agentId}"]`);
        if (agent) {
            const processBtn = agent.querySelector('.btn-success');
            if (processBtn) {
                processBtn.innerHTML = '⏳ Processing...';
                processBtn.disabled = true;
            }
        }
        
        // Check for CUST0005 suspicious underwriting case
        if (agentId === 'underwriting' && this.customerData.customerId === 'CUST0005' && this.customerData.suspiciousUnderwriting) {
            setTimeout(() => {
                // Mark agent as suspicious
                this.markAgentSuspicious(agentId);
                this.updateProgress(agentId, 'suspicious');
                
                // Stop workflow progression here until manual decision
                this.showNotification('warning', 'Underwriting Review Required', 
                    `Suspicious activity detected for ${this.customerData.name}. Manual review and approval required.`);
            }, 2500);
            return;
        }
        
        // Normal processing for other agents
        if (agentId === 'document-verification' && this.customerData.customerId === 'CUST0001' && this.customerData.incompleteDocuments) {
            setTimeout(() => {
                // Mark agent as incomplete
                this.markAgentIncomplete(agentId);
                this.updateProgress(agentId, 'incomplete');
                
                // Stop workflow progression here
                this.showNotification('warning', 'Document Verification Incomplete', 
                    `Missing document detected for ${this.customerData.name}. Please review and request missing documents.`);
            }, 2500);
            return;
        }
        
        // Normal processing for other agents
        setTimeout(() => {
            // Mark agent as completed
            this.markAgentCompleted(agentId);
            this.completedSteps.add(agentId);
            this.updateProgress(agentId, 'completed');
            
            // Show next step after completion
            setTimeout(() => {
                this.showNextStep(agentId);
            }, 1500);
        }, 2500);
    }
    
    markAgentCompleted(agentId) {
        const agent = document.querySelector(`[data-agent="${agentId}"]`);
        if (agent) {
            const status = agent.querySelector('.agent-status');
            if (status) {
                status.classList.add('completed');
            }
            
            // Change process button to completed
            const processBtn = agent.querySelector('.btn-success');
            if (processBtn) {
                processBtn.innerHTML = '✅ Completed';
                processBtn.disabled = true;
                processBtn.style.opacity = '0.7';
            }
            
            // Enable the Details button now that processing is complete
            const detailsBtn = agent.querySelector('.details-btn');
            if (detailsBtn) {
                detailsBtn.disabled = false;
                detailsBtn.classList.remove('btn-secondary');
                detailsBtn.classList.add('btn-primary');
                detailsBtn.title = 'View processing details';
            }
        }
    }
    
    markAgentIncomplete(agentId) {
        const agent = document.querySelector(`[data-agent="${agentId}"]`);
        if (agent) {
            const status = agent.querySelector('.agent-status');
            if (status) {
                status.classList.add('incomplete');
                status.textContent = '❌ Incomplete';
            }
            
            // Change process button to incomplete
            const processBtn = agent.querySelector('.btn-success');
            if (processBtn) {
                processBtn.innerHTML = '❌ Incomplete';
                processBtn.disabled = true;
                processBtn.classList.add('btn-incomplete');
            }
            
            // Enable the Details button to see what went wrong
            const detailsBtn = agent.querySelector('.details-btn');
            if (detailsBtn) {
                detailsBtn.disabled = false;
                detailsBtn.classList.remove('btn-secondary');
                detailsBtn.classList.add('btn-warning');
                detailsBtn.title = 'View incomplete processing details';
            }
        }
    }
    
    markAgentSuspicious(agentId) {
        const agent = document.querySelector(`[data-agent="${agentId}"]`);
        if (agent) {
            const status = agent.querySelector('.agent-status');
            if (status) {
                status.classList.add('suspicious');
                status.textContent = '⚠️ Suspicious';
            }
            
            // Change process button to suspicious
            const processBtn = agent.querySelector('.btn-success');
            if (processBtn) {
                processBtn.innerHTML = '⚠️ Requires Review';
                processBtn.disabled = true;
                processBtn.classList.add('btn-suspicious');
            }
            
            // Enable the Details button to see suspicious activity details
            const detailsBtn = agent.querySelector('.details-btn');
            if (detailsBtn) {
                detailsBtn.disabled = false;
                detailsBtn.classList.remove('btn-secondary');
                detailsBtn.classList.add('btn-danger');
                detailsBtn.title = 'View suspicious activity details';
            }
        }
    }
    
    showNextStep(currentAgentId) {
        // Check if current customer has incomplete documents at document verification
        if (currentAgentId === 'document-verification' && 
            this.customerData.customerId === 'CUST0001' && 
            this.customerData.incompleteDocuments) {
            // Stop workflow progression - do not show any further steps
            console.log('Workflow stopped due to incomplete document verification for CUST0001');
            return;
        }
        
        // Check if current customer has suspicious underwriting that was rejected
        if (currentAgentId === 'underwriting' && 
            this.customerData.customerId === 'CUST0005' && 
            this.customerData.suspiciousUnderwriting &&
            this.customerData.underwritingDecision === 'rejected') {
            // Stop workflow progression - application rejected
            console.log('Workflow stopped due to rejected underwriting for CUST0005');
            return;
        }
        
        // Check if current customer has suspicious underwriting pending decision
        if (currentAgentId === 'underwriting' && 
            this.customerData.customerId === 'CUST0005' && 
            this.customerData.suspiciousUnderwriting &&
            !this.customerData.underwritingDecision) {
            // Stop workflow progression - waiting for manual decision
            console.log('Workflow stopped - waiting for manual underwriting decision for CUST0005');
            return;
        }
        
        switch (currentAgentId) {
            case 'customer-service':
                this.showArrowAndAgent('arrow-0', 'document-verification');
                break;
                
            case 'document-verification':
                this.showArrowAndAgent('arrow-1', 'credit-qualification');
                break;
                
            case 'credit-qualification':
                this.showBranchingFlow();
                break;
                
            case 'credit-assessment':
            case 'asset-valuation':
                this.branchStepsCompleted.add(currentAgentId);
                if (this.branchStepsCompleted.size === 2) {
                    this.showConvergenceFlow();
                }
                break;
                
            case 'underwriting':
                this.showHorizontalFlow();
                break;
                
            case 'offer-generation':
                this.showHorizontalArrowAndAgent('horizontal-arrow-0', 'customer-communication');
                break;
                
            case 'customer-communication':
                this.showHorizontalArrowAndAgent('horizontal-arrow-1', 'audit');
                break;
                
            case 'audit':
                this.completeWorkflow();
                break;
        }
    }
    
    showArrowAndAgent(arrowId, agentId) {
        // Show arrow first with delay
        const arrow = document.getElementById(arrowId);
        if (arrow) {
            setTimeout(() => {
                arrow.classList.add('visible', 'animate-fade-in');
            }, 1000);
        }
        
        // Show agent after arrow animation completes
        setTimeout(() => {
            this.showAgent(agentId);
            this.updateProgress(agentId, 'active');
        }, 2500);
    }
    
    showBranchingFlow() {
        // Show branching arrows with delay
        setTimeout(() => {
            const branchingArrows = document.getElementById('branching-arrows');
            if (branchingArrows) {
                branchingArrows.classList.add('visible', 'animate-fade-in');
            }
        }, 1000);
        
        // Show both branch agents sequentially
        setTimeout(() => {
            this.showAgent('credit-assessment');
            this.updateProgress('credit-assessment', 'active');
        }, 2500);
        
        setTimeout(() => {
            this.showAgent('asset-valuation');
            this.updateProgress('asset-valuation', 'active');
        }, 3500);
    }
    
    showConvergenceFlow() {
        // Show convergence arrows with delay
        setTimeout(() => {
            const convergenceArrows = document.getElementById('convergence-arrows');
            if (convergenceArrows) {
                convergenceArrows.classList.add('visible', 'animate-fade-in');
            }
        }, 1500);
        
        // Show underwriting agent after convergence
        setTimeout(() => {
            this.showAgent('underwriting');
            this.updateProgress('underwriting', 'active');
        }, 3000);
    }
    
    showHorizontalFlow() {
        // Show first horizontal agent with delay
        setTimeout(() => {
            this.showAgent('offer-generation');
            this.updateProgress('offer-generation', 'active');
        }, 1500);
    }
    
    showHorizontalArrowAndAgent(arrowId, agentId) {
        // Show horizontal arrow with delay
        const arrow = document.getElementById(arrowId);
        if (arrow) {
            setTimeout(() => {
                arrow.classList.add('visible', 'animate-fade-in');
            }, 1000);
        }
        
        // Show next horizontal agent after arrow
        setTimeout(() => {
            this.showAgent(agentId);
            this.updateProgress(agentId, 'active');
        }, 2500);
    }
    
    updateProgress(stepId, status) {
        const progressStep = document.querySelector(`[data-step="${stepId}"]`);
        if (progressStep) {
            progressStep.classList.remove('active', 'completed', 'incomplete', 'suspicious', 'rejected');
            progressStep.classList.add(status);
        }
    }
    
    completeWorkflow() {
        setTimeout(() => {
            this.showNotification('success', 'Workflow Complete! 🎉', `All agents have processed the loan application for ${this.customerData.name}. The loan is ready for disbursement.`);
            this.stopAutoProcess();
        }, 1500);
    }
    
    // Professional Notification System
    showNotification(type = 'success', title, message, duration = 5000) {
        const container = document.getElementById('notificationContainer');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        
        notification.innerHTML = `
            <div class="notification-header">
                <span class="notification-icon">${icons[type]}</span>
                <h4 class="notification-title">${title}</h4>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
            <div class="notification-content">${message}</div>
            <div class="notification-progress">
                <div class="notification-progress-bar"></div>
            </div>
        `;
        
        container.appendChild(notification);
        
        // Trigger animation
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        // Auto-hide with progress bar
        const progressBar = notification.querySelector('.notification-progress-bar');
        if (duration > 0) {
            progressBar.style.transition = `width ${duration}ms linear`;
            progressBar.style.width = '100%';
            
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.remove();
                    }
                }, 400);
            }, duration);
        }
    }
    
    // Auto Process Methods
    startAutoProcess() {
        if (this.autoProcessing) return;
        
        this.autoProcessing = true;
        this.currentAutoStep = 0;
        
        const autoBtn = document.getElementById('autoProcessBtn');
        const stopBtn = document.getElementById('stopProcessBtn');
        
        autoBtn.disabled = true;
        stopBtn.disabled = false;
        
        // Start the auto processing
        this.processNextAutoStep();
    }
    
    stopAutoProcess() {
        this.autoProcessing = false;
        
        if (this.autoProcessInterval) {
            clearTimeout(this.autoProcessInterval);
            this.autoProcessInterval = null;
        }
        
        const autoBtn = document.getElementById('autoProcessBtn');
        const stopBtn = document.getElementById('stopProcessBtn');
        
        autoBtn.disabled = false;
        stopBtn.disabled = true;
    }
    
    processNextAutoStep() {
        if (!this.autoProcessing || this.currentAutoStep >= this.autoSequence.length) {
            this.stopAutoProcess();
            return;
        }
        
        const currentAgentId = this.autoSequence[this.currentAutoStep];
        
        // Check if we should stop auto-processing due to incomplete documents
        if (currentAgentId === 'document-verification' && 
            this.customerData.customerId === 'CUST0001' && 
            this.customerData.incompleteDocuments) {
            // Process the document verification (which will show incomplete)
            this.processAgent(currentAgentId);
            // Stop auto-processing here
            this.stopAutoProcess();
            return;
        }
        
        // Process the current agent
        this.processAgent(currentAgentId);
        
        // Move to next step
        this.currentAutoStep++;
        
        // Schedule next processing (wait for current processing to complete)
        // Total time: 2.5s (processing) + 1.5s (completion delay) + 1-2.5s (arrow/agent show) = ~6s per step
        this.autoProcessInterval = setTimeout(() => {
            this.processNextAutoStep();
        }, 6000);
    }
    
    showAgentDetails(agentId) {
        const agent = this.workflowSteps
            .find(step => step.id === agentId) || 
            this.workflowSteps
                .find(step => step.branches?.find(branch => branch.id === agentId))?.branches
                .find(branch => branch.id === agentId) ||
            this.workflowSteps
                .find(step => step.steps?.find(s => s.id === agentId))?.steps
                .find(s => s.id === agentId);
        
        if (agent) {
            const modal = document.getElementById('agentModal');
            const modalTitle = document.getElementById('modalAgentTitle');
            const modalDescription = document.getElementById('modalAgentDescription');
            const modalDetails = document.getElementById('modalAgentDetails');
            
            modalTitle.textContent = agent.title;
            modalDescription.style.display = 'none'; // Hide description
            modalDetails.innerHTML = this.getAgentDetails(agentId);
            
            modal.style.display = 'block';
        }
    }
    
    getAgentDetails(agentId) {
        const customer = this.customerData;
        
        // Check if we have Cosmos DB data for this customer
        // Support CUST0241, CUST0002, and CUST0003
        if (this.cosmosAgentData && ['CUST0241', 'CUST0002', 'CUST0003'].includes(customer.customerId)) {
            const cosmosDetails = this.getCosmosAgentDetails(agentId);
            if (cosmosDetails) {
                return cosmosDetails;
            }
        }
        const details = {
            'customer-service': `
                <h4>Customer Information:</h4>
                <ul>
                    <li><strong>Customer ID:</strong> ${customer.customerId || 'Not assigned'}</li>
                    <li><strong>Name:</strong> ${customer.name}</li>
                    <li><strong>Mobile:</strong> ${maskPhone(customer.mobile)}</li>
                    <li><strong>Email:</strong> ${maskEmail(customer.email)}</li>
                    <li><strong>Loan Amount:</strong> ${customer.loanAmount}</li>
                    <li><strong>Purpose:</strong> ${customer.purpose}</li>
                </ul>
                <h4>Current Status:</h4>
                <p>✅ Initial form completed and submitted</p>
            `,
            'document-verification': customer.customerId === 'CUST0001' && customer.incompleteDocuments ? `
                <h4>Document Verification Status:</h4>
                <ul>
                    <li><strong>Aadhar Card:</strong> ${maskAadhar(customer.aadhar)} ✅</li>
                    <li><strong>PAN Card:</strong> ${maskPAN(customer.pan)} ✅</li>
                    <li><strong>Address Proof:</strong> ${customer.address} ✅</li>
                    <li><strong>Salary Slips:</strong> May 2025, April 2025 ✅</li>
                    <li><strong>Bank Statements:</strong> Last 6 months ✅</li>
                </ul>
                <div class="missing-document-alert">
                    <h4 style="color: #ef4444;">❌ Missing Document:</h4>
                    <p style="color: #ef4444; font-weight: bold;">${customer.missingDocument}</p>
                </div>
                <div class="email-notification-section">
                    <button class="btn btn-email" onclick="workflowInstance.sendEmailNotification('${customer.customerId}', '${customer.missingDocument}')">
                        <i class="fas fa-envelope"></i> Send Email Notification
                    </button>
                </div>
            ` : `
                <h4>Documents Verified:</h4>
                <ul>
                    <li><strong>Aadhar Card:</strong> ${maskAadhar(customer.aadhar)} ✅</li>
                    <li><strong>PAN Card:</strong> ${maskPAN(customer.pan)} ✅</li>
                    <li><strong>Address Proof:</strong> ${customer.address} ✅</li>
                    <li><strong>Salary Slips:</strong> Last 3 months ✅</li>
                    <li><strong>Bank Statements:</strong> Last 6 months ✅</li>
                </ul>
                <h4>Employer Details:</h4>
                <p>${customer.employer}</p>
            `,
            'credit-qualification': `
                <h4>Credit Assessment:</h4>
                <ul>
                    <li><strong>CIBIL Score:</strong> ${customer.cibil} (Excellent)</li>
                    <li><strong>Annual Income:</strong> ${customer.income}</li>
                    <li><strong>Employment:</strong> ${customer.employer}</li>
                    <li><strong>Loan Amount:</strong> ${customer.loanAmount}</li>
                    <li><strong>Eligibility:</strong> ✅ Qualified</li>
                </ul>
                <h4>Risk Category:</h4>
                <p>Low Risk - Approved for detailed assessment</p>
            `,
            'credit-assessment': `
                <h4>Detailed Credit Analysis:</h4>
                <ul>
                    <li><strong>CIBIL Score:</strong> ${customer.cibil}</li>
                    <li><strong>Credit History:</strong> 5 years, No defaults</li>
                    <li><strong>DTI Ratio:</strong> 35% (Healthy)</li>
                    <li><strong>Existing EMIs:</strong> ₹15,000/month</li>
                    <li><strong>Risk Score:</strong> A+ Category</li>
                </ul>
                <h4>Recommendation:</h4>
                <p>✅ Approved for loan processing</p>
            `,
            'asset-valuation': `
                <h4>Property Valuation:</h4>
                <ul>
                    <li><strong>Property:</strong> ${customer.property}</li>
                    <li><strong>Location:</strong> DLF Phase 2, Gurgaon</li>
                    <li><strong>Market Value:</strong> ${customer.propertyValue}</li>
                    <li><strong>Loan Amount:</strong> ${customer.loanAmount}</li>
                    <li><strong>LTV Ratio:</strong> 55.5% (Safe)</li>
                </ul>
                <h4>Valuation Status:</h4>
                <p>✅ Property approved as collateral</p>
            `,
            'underwriting': customer.customerId === 'CUST0005' && customer.suspiciousUnderwriting ? `
                <h4>Underwriting Assessment - SUSPICIOUS ACTIVITY DETECTED</h4>
                <div class="suspicious-alert">
                    <h4 style="color: #f59e0b;">⚠️ Risk Factors Identified:</h4>
                    <ul class="suspicious-reasons">
                        ${customer.suspiciousReasons.map(reason => `<li>${reason}</li>`).join('')}
                    </ul>
                </div>
                <h4>Customer Details:</h4>
                <ul>
                    <li><strong>Customer:</strong> ${customer.name}</li>
                    <li><strong>Loan Amount:</strong> ${customer.loanAmount}</li>
                    <li><strong>CIBIL Score:</strong> ${customer.cibil} (Fair - Below Preferred)</li>
                    <li><strong>Income:</strong> ${customer.income}</li>
                    <li><strong>Risk Level:</strong> HIGH RISK</li>
                </ul>
                <div class="manual-decision-section">
                    <h4>Manual Decision Required:</h4>
                    <div class="decision-buttons">
                        <button class="btn btn-approve" onclick="workflowInstance.approveUnderwriting('${customer.customerId}')">
                            <i class="fas fa-check"></i> Process Application
                        </button>
                        <button class="btn btn-reject" onclick="workflowInstance.rejectUnderwriting('${customer.customerId}')">
                            <i class="fas fa-times"></i> Reject Application
                        </button>
                    </div>
                </div>
            ` : `
                <h4>Final Assessment:</h4>
                <ul>
                    <li><strong>Customer:</strong> ${customer.name}</li>
                    <li><strong>Loan Amount:</strong> ${customer.loanAmount}</li>
                    <li><strong>Interest Rate:</strong> 8.5% p.a.</li>
                    <li><strong>Tenure:</strong> 20 years</li>
                    <li><strong>Monthly EMI:</strong> ₹21,455</li>
                </ul>
                <h4>Decision:</h4>
                <p>✅ LOAN APPROVED</p>
            `,
            'offer-generation': `
                <h4>Loan Offer Details:</h4>
                <ul>
                    <li><strong>Principal:</strong> ${customer.loanAmount}</li>
                    <li><strong>Interest Rate:</strong> 8.5% p.a. (Floating)</li>
                    <li><strong>Tenure:</strong> 20 years (240 months)</li>
                    <li><strong>Monthly EMI:</strong> ₹21,455</li>
                    <li><strong>Processing Fee:</strong> ₹25,000</li>
                </ul>
                <h4>Offer Validity:</h4>
                <p>Valid till: 30 days from generation</p>
            `,
            'customer-communication': customer.customerId === 'CUST0005' && customer.underwritingDecision === 'rejected' ? `
                <h4>Customer Communication - Application Rejected:</h4>
                <ul>
                    <li><strong>Customer:</strong> ${customer.name}</li>
                    <li><strong>Contact:</strong> ${maskPhone(customer.mobile)}</li>
                    <li><strong>Email:</strong> ${maskEmail(customer.email)}</li>
                    <li><strong>Rejection Notice:</strong> ❌ Sent Via Email & SMS</li>
                    <li><strong>Reason:</strong> High Risk Factors Identified</li>
                </ul>
                <div class="rejection-details">
                    <h4 style="color: #ef4444;">Rejection Reasons Communicated:</h4>
                    <ul class="rejection-reasons">
                        <li>Credit assessment indicates elevated risk profile</li>
                        <li>Recent employment changes affecting stability</li>
                        <li>Debt-to-income ratio exceeds acceptable limits</li>
                        <li>Multiple recent credit inquiries flagged</li>
                    </ul>
                </div>
                <h4>Next Steps:</h4>
                <p style="color: #ef4444;">❌ Application closed. Customer advised to reapply after 6 months with improved financial profile.</p>
            ` : `
                <h4>Communication Summary:</h4>
                <ul>
                    <li><strong>Customer:</strong> ${customer.name}</li>
                    <li><strong>Contact:</strong> ${maskPhone(customer.mobile)}</li>
                    <li><strong>Email:</strong> ${maskEmail(customer.email)}</li>
                    <li><strong>Offer Sent:</strong> ✅ Via Email & SMS</li>
                    <li><strong>Customer Response:</strong> ✅ Accepted</li>
                </ul>
                <h4>Next Steps:</h4>
                <p>Documentation and disbursement process initiated</p>
            `,
            'audit': customer.customerId === 'CUST0005' && customer.underwritingDecision === 'rejected' ? `
                <h4>Audit Report - Application Rejected:</h4>
                <div class="rejection-audit">
                    <ul>
                        <li><strong>Document Verification:</strong> ✅ Complete</li>
                        <li><strong>Credit Qualification:</strong> ✅ Passed Initial Screening</li>
                        <li><strong>Credit Assessment:</strong> ✅ Completed</li>
                        <li><strong>Asset Valuation:</strong> ✅ Completed</li>
                        <li><strong>Underwriting:</strong> ❌ <span style="color: #ef4444;">REJECTED - High Risk</span></li>
                        <li><strong>Risk Factors:</strong> ⚠️ Multiple Risk Indicators</li>
                        <li><strong>Compliance:</strong> ✅ RBI Guidelines Followed</li>
                    </ul>
                </div>
                <h4 style="color: #ef4444;">Rejection Summary:</h4>
                <div class="audit-rejection-details">
                    <ul>
                        <li><strong>Primary Reason:</strong> High debt-to-income ratio (45%)</li>
                        <li><strong>Secondary Factors:</strong> Recent job change, multiple credit inquiries</li>
                        <li><strong>Risk Category:</strong> HIGH RISK - Outside acceptable parameters</li>
                        <li><strong>Decision Date:</strong> ${new Date().toLocaleDateString('en-IN')}</li>
                        <li><strong>Review Period:</strong> 6 months minimum before reapplication</li>
                    </ul>
                </div>
                <h4>Final Status:</h4>
                <p style="color: #ef4444; font-weight: bold;">❌ AUDIT COMPLETE - APPLICATION REJECTED</p>
            ` : `
                <h4>Audit Checklist:</h4>
                <ul>
                    <li><strong>Document Verification:</strong> ✅ Complete</li>
                    <li><strong>Credit Assessment:</strong> ✅ Approved</li>
                    <li><strong>Property Valuation:</strong> ✅ Verified</li>
                    <li><strong>Underwriting:</strong> ✅ Approved</li>
                    <li><strong>Compliance:</strong> ✅ RBI Guidelines Met</li>
                </ul>
                <h4>Final Status:</h4>
                <p>✅ AUDIT COMPLETE - Ready for disbursement</p>
            `
        };
        
        return details[agentId] || '<p>Details not available</p>';
    }

    getCosmosAgentDetails(agentId) {
        console.log('getCosmosAgentDetails called with agentId:', agentId);
        console.log('cosmosAgentData:', this.cosmosAgentData);
        
        if (!this.cosmosAgentData) {
            console.log('No cosmos agent data available');
            return null;
        }
        
        // Map workflow agent IDs to Cosmos agent names
        const agentMapping = {
            'customer-service': 'ApplicationAssist Agent',
            'document-verification': 'DocumentChecker Agent', 
            'credit-qualification': 'PreQualification Agent',
            'credit-assessment': 'CreditAssessor Agent',
            'asset-valuation': 'Valuation Agent',
            'underwriting': 'Underwriting Agent',
            'offer-generation': 'OfferGeneration Agent',
            'customer-communication': 'CustomerCommunication Agent',
            'audit': 'Audit Record'
        };
        
        const targetAgentName = agentMapping[agentId];
        console.log('Looking for agent name:', targetAgentName);
        
        if (!targetAgentName) {
            console.log('No agent mapping found for agentId:', agentId);
            return null;
        }
        
        // Find the matching agent data from Cosmos
        const agentData = this.cosmosAgentData.find(agent => {
            console.log('Checking agent:', agent.agent_name, 'against target:', targetAgentName);
            return agent.agent_name === targetAgentName;
        });
        
        console.log('Found agent data:', agentData);
        
        if (!agentData) {
            console.log('No matching agent data found');
            return null;
        }
        
        // Format the agent description as HTML
        const descriptions = Array.isArray(agentData.agent_description) 
            ? agentData.agent_description 
            : [agentData.agent_description];
        
        const formattedDescriptions = descriptions
            .map(desc => `<li>${desc}</li>`)
            .join('');
        
        return `
            <ul class="cosmos-description-list">
                ${formattedDescriptions}
            </ul>
        `;
    }
    
    sendEmailNotification(customerId, missingDocument) {
        // Simulate sending email notification
        const emailBtn = event.target;
        const originalContent = emailBtn.innerHTML;
        
        // Check if already sent
        if (emailBtn.classList.contains('btn-sent')) {
            return;
        }
        
        // Show sending state
        emailBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
        emailBtn.disabled = true;
        
        setTimeout(() => {
            // Show success state permanently
            emailBtn.innerHTML = '<i class="fas fa-check"></i> Email Sent';
            emailBtn.classList.add('btn-sent');
            emailBtn.disabled = true;
            
            // Show success notification
            this.showNotification('success', 'Email Notification Sent', 
                `Email notification sent successfully to customer ${customerId} regarding missing document: ${missingDocument}`);
            
        }, 1500);
    }
    
    approveUnderwriting(customerId) {
        // Update customer decision
        this.customerData.underwritingDecision = 'approved';
        
        // Update agent status to completed
        this.markAgentCompleted('underwriting');
        this.updateProgress('underwriting', 'completed');
        this.completedSteps.add('underwriting');
        
        // Close modal
        closeModal();
        
        // Show success notification
        this.showNotification('success', 'Application Approved', 
            `Loan application for ${this.customerData.name} has been manually approved despite risk factors.`);
        
        // Continue with workflow after a delay
        setTimeout(() => {
            this.showNextStep('underwriting');
        }, 2000);
    }
    
    rejectUnderwriting(customerId) {
        // Update customer decision
        this.customerData.underwritingDecision = 'rejected';
        
        // Mark agent as rejected
        const agent = document.querySelector(`[data-agent="underwriting"]`);
        if (agent) {
            const status = agent.querySelector('.agent-status');
            if (status) {
                status.classList.remove('suspicious');
                status.classList.add('rejected');
                status.textContent = '❌ Rejected';
            }
            
            const processBtn = agent.querySelector('.btn-success');
            if (processBtn) {
                processBtn.innerHTML = '❌ Rejected';
                processBtn.classList.remove('btn-suspicious');
                processBtn.classList.add('btn-rejected');
            }
        }
        
        // Update progress
        this.updateProgress('underwriting', 'rejected');
        
        // Close modal
        closeModal();
        
        // Show rejection notification
        this.showNotification('error', 'Application Rejected', 
            `Loan application for ${this.customerData.name} has been rejected due to high risk factors.`);
        
        // Stop workflow completely
        this.stopAutoProcess();
    }
}

// Initialize workflow when DOM is loaded
let workflowInstance;

document.addEventListener('DOMContentLoaded', function() {
    workflowInstance = new BankLoanWorkflow();
    
    // Check if applicationId parameter is passed from applications page
    const urlParams = new URLSearchParams(window.location.search);
    const applicationId = urlParams.get('applicationId');
    const cosmosData = urlParams.get('cosmosData');
    
    // Load Cosmos DB data if available
    if (cosmosData === 'true' && applicationId) {
        const storedCosmosData = localStorage.getItem(`cosmosData_${applicationId}`);
        console.log(`Looking for cosmos data with key: cosmosData_${applicationId}`);
        console.log('Stored cosmos data:', storedCosmosData);
        
        if (storedCosmosData) {
            try {
                workflowInstance.cosmosAgentData = JSON.parse(storedCosmosData);
                console.log('Loaded Cosmos DB data for workflow:', workflowInstance.cosmosAgentData);
                console.log('Data type:', typeof workflowInstance.cosmosAgentData);
                console.log('Is array:', Array.isArray(workflowInstance.cosmosAgentData));
            } catch (error) {
                console.error('Error parsing Cosmos data:', error);
            }
        } else {
            console.log('No cosmos data found in localStorage');
        }
    }
    
    // Add Enter key support for customer ID input
    const customerIdInput = document.getElementById('customerIdInput');
    if (customerIdInput) {
        customerIdInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                workflowInstance.startWorkflowWithCustomerId();
            }
        });
        
        // Auto-populate if coming from applications page
        if (applicationId) {
            customerIdInput.value = applicationId;
            // Automatically start workflow after a short delay
            setTimeout(() => {
                workflowInstance.startWorkflowWithCustomerId();
            }, 500);
        } else {
            // Focus on input field when page loads normally
            customerIdInput.focus();
        }
    }
});

// Modal functionality
window.onclick = function(event) {
    const modal = document.getElementById('agentModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}

function closeModal() {
    const modal = document.getElementById('agentModal');
    modal.style.display = 'none';
}
