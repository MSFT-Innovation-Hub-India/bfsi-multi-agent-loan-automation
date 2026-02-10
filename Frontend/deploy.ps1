# =============================================================
#  deploy.ps1 — Deploy Loan Workflow to Azure Container Apps
# =============================================================
#  Usage:
#    .\deploy.ps1                     (first-time full deploy)
#    .\deploy.ps1 -UpdateOnly         (re-build & push image only)
#
#  Prerequisites:
#    - Azure CLI installed  (az --version)
#    - Logged into Azure    (az login)
#  
#  Uses EXISTING ACR: loanprocessingapi.azurecr.io
# =============================================================

param(
    [switch]$UpdateOnly   # skip resource creation, just rebuild & push
)

# ---------- Configuration ----------
$RESOURCE_GROUP   = "fsi-demos"
$LOCATION         = "eastus2"

# Existing ACR details
$ACR_NAME         = "loanprocessingapi"
$ACR_SERVER       = "loanprocessingapi.azurecr.io"
$ACR_USERNAME     = "loanprocessingapi"
$ACR_PASSWORD     = "7qpH2YSkzi4kOLGoGdhIYzmhYtQr8AOMxQNxYfMj5OM3GKSBYE7KJQQJ99CAACHYHv6Eqg7NAAACAZCRQtqD"

# Container App settings
$ENVIRONMENT_NAME = "loan-workflow-env"
$APP_NAME         = "loan-workflow-app"
$IMAGE_NAME       = "loan-workflow"
$IMAGE_TAG        = "latest"

# Environment variables for the container
$COSMOS_API_BASE_URL = "https://cosmosdb-api-h3f2fnbth2dccaed.eastus2-01.azurewebsites.net"
# --------------------------------------------------

$ErrorActionPreference = "Stop"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Loan Workflow — Azure Container Apps" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 1. Check prerequisites
Write-Host "[1/7] Checking prerequisites..." -ForegroundColor Yellow
try { az --version | Out-Null } catch { Write-Error "Azure CLI not found. Install from https://aka.ms/installazurecli"; exit 1 }

# Make sure we're logged in
$account = az account show 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  → Not logged in. Running 'az login'..." -ForegroundColor Gray
    az login
}
$subName = (az account show --query name -o tsv)
Write-Host "  ✅ Using subscription: $subName" -ForegroundColor Green

if (-not $UpdateOnly) {
    # 2. Create Resource Group
    Write-Host "`n[2/7] Creating Resource Group '$RESOURCE_GROUP'..." -ForegroundColor Yellow
    az group create --name $RESOURCE_GROUP --location $LOCATION --output none
    Write-Host "  ✅ Resource group ready" -ForegroundColor Green

    # 3. Skip ACR creation — using existing ACR
    Write-Host "`n[3/7] Using existing ACR '$ACR_NAME' ($ACR_SERVER)..." -ForegroundColor Yellow
    Write-Host "  ✅ ACR ready (pre-existing)" -ForegroundColor Green

    # 4. Create Container Apps Environment
    Write-Host "`n[4/7] Creating Container Apps Environment '$ENVIRONMENT_NAME'..." -ForegroundColor Yellow
    az containerapp env create `
        --name $ENVIRONMENT_NAME `
        --resource-group $RESOURCE_GROUP `
        --location $LOCATION `
        --output none
    Write-Host "  ✅ Environment ready" -ForegroundColor Green
} else {
    Write-Host "`n[2-4] Skipping resource creation (--UpdateOnly)" -ForegroundColor Gray
}

# 5. Build & push image using ACR Build (no local Docker needed)
Write-Host "`n[5/7] Building image in ACR (cloud build)..." -ForegroundColor Yellow
$FULL_IMAGE = "${ACR_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}"
az acr build `
    --registry $ACR_NAME `
    --image "${IMAGE_NAME}:${IMAGE_TAG}" `
    --file Dockerfile `
    .
Write-Host "  ✅ Image built & pushed: $FULL_IMAGE" -ForegroundColor Green

if (-not $UpdateOnly) {
    # 6. Create Container App
    Write-Host "`n[6/7] Creating Container App '$APP_NAME'..." -ForegroundColor Yellow
    az containerapp create `
        --name $APP_NAME `
        --resource-group $RESOURCE_GROUP `
        --environment $ENVIRONMENT_NAME `
        --image $FULL_IMAGE `
        --registry-server $ACR_SERVER `
        --registry-username $ACR_USERNAME `
        --registry-password $ACR_PASSWORD `
        --target-port 8000 `
        --ingress external `
        --min-replicas 1 `
        --max-replicas 3 `
        --cpu 0.5 `
        --memory 1.0Gi `
        --env-vars `
            COSMOS_API_BASE_URL="$COSMOS_API_BASE_URL" `
            PORT="8000" `
        --output none
    Write-Host "  ✅ Container App created" -ForegroundColor Green
} else {
    # 6. Update existing Container App with new image
    Write-Host "`n[6/7] Updating Container App '$APP_NAME' with new image..." -ForegroundColor Yellow
    az containerapp update `
        --name $APP_NAME `
        --resource-group $RESOURCE_GROUP `
        --image $FULL_IMAGE `
        --output none
    Write-Host "  ✅ Container App updated" -ForegroundColor Green
}

# 7. Get the app URL
Write-Host "`n[7/7] Fetching app URL..." -ForegroundColor Yellow
$APP_URL = (az containerapp show `
    --name $APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --query "properties.configuration.ingress.fqdn" `
    -o tsv)

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  ✅ DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`n  🌐 App URL:  https://$APP_URL" -ForegroundColor Cyan
Write-Host "  🏥 Health:   https://$APP_URL/health" -ForegroundColor Cyan
Write-Host "`n  To redeploy after code changes:" -ForegroundColor Gray
Write-Host "    .\deploy.ps1 -UpdateOnly" -ForegroundColor Gray
Write-Host ""
