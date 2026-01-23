# Azure Container Apps Setup Guide

This guide walks you through deploying the Strategic Value Report to Azure Container Apps with automated GitHub Actions deployment.

## Prerequisites

- Azure subscription
- GitHub Personal Access Token with `read:packages` scope
- Entra ID App Registration (Client ID, Client Secret, Tenant ID)

---

## Step 1: Create Azure Container Apps Environment

### Via Azure Portal

1. Go to [Azure Portal](https://portal.azure.com)
2. Search for **Container Apps** → **Create**
3. **Basics:**
   - Resource Group: Create new → `strategic-value-report-rg`
   - Container Apps Environment name: `strategic-value-env`
   - Region: Choose closest (e.g., East US)
   - Zone redundancy: **Disabled** (saves cost)
4. Click **Review + Create**

---

## Step 2: Create Container App

1. In the environment you just created → **Create new container app**
2. **Basics:**
   - Name: `strategic-value-report` (or choose your own)
   - Deployment source: **Container image**

3. **Container:**
   - Image source: **Other registry**
   - Image type: **Public** or **Private** (use Private with GHCR credentials)
   - Registry login server: `ghcr.io`
   - Image and tag: `doomhound188/strategic_value_report:latest`
   - Username: Your GitHub username
   - Password: GitHub PAT with `read:packages` scope

4. **Ingress:**
   - Ingress: **Enabled**
   - Accepting traffic from: **Anywhere**
   - Ingress type: **HTTP**
   - Target port: `5000`

5. **Scaling:**
   - Min replicas: `0` (enable scale-to-zero)
   - Max replicas: `3`

---

## Step 3: Configure Secrets

1. Go to your Container App → **Secrets**
2. Add the following secrets:
   - `cw-private-key`: Your ConnectWise private key
   - `azure-client-secret`: Entra ID client secret
   - `google-api-key`: Google Gemini API key
   - `flask-secret-key`: Random string (e.g., use `openssl rand -hex 32`)

---

## Step 4: Configure Environment Variables

1. Go to **Environment variables** tab
2. Add all variables:

```
CW_COMPANY_ID=<your-company-id>
CW_SITE_URL=api-na.myconnectwise.net
CW_PUBLIC_KEY=<your-public-key>
CW_PRIVATE_KEY=secretref:cw-private-key
CW_CLIENT_ID=<your-client-id>

GOOGLE_API_KEY=secretref:google-api-key

AZURE_CLIENT_ID=<entra-app-client-id>
AZURE_CLIENT_SECRET=secretref:azure-client-secret
AZURE_TENANT_ID=<your-tenant-id>
FLASK_SECRET_KEY=secretref:flask-secret-key
```

3. Click **Save**

---

## Step 5: Update Entra ID Redirect URI

1. Get your Container App URL from Azure Portal (under **Application Url**)
   - Example: `https://strategic-value-report.proudriver-a1b2c3d4.eastus.azurecontainerapps.io`
2. Go to **Azure Portal** → **Entra ID** → **App registrations**
3. Select your app → **Authentication**
4. Add redirect URI: `https://<your-app-url>/auth/callback`
5. Click **Save**

---

## Step 6: Set Up GitHub Actions Deployment

### Create Azure Service Principal

```bash
az ad sp create-for-rbac \
  --name "GitHub-Actions-Strategic-Value-Report" \
  --role contributor \
  --scopes /subscriptions/<YOUR_SUBSCRIPTION_ID>/resourceGroups/strategic-value-report-rg \
  --sdk-auth
```

Copy the entire JSON output.

### Add GitHub Secrets

1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Add the following secrets:
   - `AZURE_CREDENTIALS`: Paste the JSON from above
   - `AZURE_CONTAINER_APP_NAME`: `strategic-value-report` (or your app name)
   - `AZURE_RESOURCE_GROUP`: `strategic-value-report-rg`

---

## Step 7: Test Deployment

1. Push a commit to the `main` branch
2. Go to **GitHub Actions** tab
3. Watch the workflows:
   - "Build and Scan Docker Image" should complete first
   - "Deploy to Azure Container Apps" should run automatically after
4. Once complete, visit your Container App URL
5. You should be redirected to Microsoft login

---

## Verification Checklist

- [ ] App URL loads
- [ ] Microsoft login works
- [ ] Can generate a report
- [ ] App scales to zero after 5 min idle (check Azure Portal metrics)
- [ ] Cold start works (access after scale-to-zero)

---

## Troubleshooting

**Container won't start:**
- Check **Log stream** in Azure Portal for errors
- Verify all environment variables are set correctly

**Authentication fails:**
- Verify redirect URI matches exactly (include `/auth/callback`)
- Check Entra ID client secret hasn't expired

**Scale-to-zero not working:**
- Ensure min replicas is set to `0`
- Check scaling rules configuration
