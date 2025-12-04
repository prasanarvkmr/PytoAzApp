# Python Flask Calculator - Azure App Service Deployment

A simple Python Flask web application that performs calculator operations, deployed to Azure App Service using Azure Pipelines with JFrog Artifactory integration.

## 📋 Application Structure

```
PytoAzApp/
├── app.py                  # Flask application entry point
├── calculator.py           # Calculator logic module
├── templates/
│   └── index.html         # Web interface
├── requirements.txt        # Python dependencies
├── azure-pipelines.yml    # CI/CD pipeline configuration
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## 🚀 Features

- **Flask Web Application**: Simple calculator with web interface
- **Modular Design**: Separate Python module for calculator logic
- **Responsive UI**: Modern, gradient-styled web interface
- **Azure App Service**: Cloud deployment on Azure
- **JFrog Artifactory**: Artifact management and versioning
- **CI/CD Pipeline**: Automated build and deployment

## 🛠️ Local Development

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Setup and Run

1. **Clone the repository**
   ```powershell
   git clone <your-repo-url>
   cd PytoAzApp
   ```

2. **Create virtual environment**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```powershell
   python app.py
   ```

5. **Access the application**
   Open your browser and navigate to: `http://localhost:8000`

## ☁️ Azure App Service Setup

### 1. Create Azure App Service

```bash
# Login to Azure
az login

# Create resource group
az group create --name rg-calculator-app --location eastus

# Create App Service plan (Linux)
az appservice plan create \
  --name plan-calculator-app \
  --resource-group rg-calculator-app \
  --sku B1 \
  --is-linux

# Create Web App
az webapp create \
  --resource-group rg-calculator-app \
  --plan plan-calculator-app \
  --name your-webapp-name \
  --runtime "PYTHON:3.11"
```

### 2. Configure App Service

```bash
# Set startup command
az webapp config set \
  --resource-group rg-calculator-app \
  --name your-webapp-name \
  --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 app:app"
```

## 🔧 Azure DevOps Pipeline Setup

### 1. Create Service Connections

#### Azure Service Connection
1. Go to Azure DevOps → Project Settings → Service connections
2. Click "New service connection"
3. Select "Azure Resource Manager"
4. Choose "Service principal (automatic)"
5. Select your subscription and resource group
6. Name it: `AzureServiceConnection`

#### JFrog Artifactory Service Connection
1. In Azure DevOps → Project Settings → Service connections
2. Click "New service connection"
3. Select "JFrog Artifactory"
4. Enter your JFrog details:
   - **Server URL**: `https://your-company.jfrog.io/artifactory`
   - **Username**: Your JFrog username
   - **Password/API Key**: Your JFrog API key
5. Name it: `JFrogServiceConnection`

### 2. Install JFrog Extension

Install the JFrog extension in your Azure DevOps organization:
1. Go to Organization Settings → Extensions
2. Browse Marketplace
3. Search for "JFrog Artifactory"
4. Install the extension

### 3. Configure Pipeline Variables

Update the following variables in `azure-pipelines.yml`:

```yaml
variables:
  azureServiceConnection: 'AzureServiceConnection'  # Your Azure service connection name
  webAppName: 'your-webapp-name'                    # Your Azure Web App name
  artifactoryUrl: 'https://your-company.jfrog.io/artifactory'
  artifactoryRepo: 'python-local'                   # Your Artifactory repository
```

### 4. Create Pipeline

1. Go to Azure DevOps → Pipelines → New Pipeline
2. Select your repository
3. Choose "Existing Azure Pipelines YAML file"
4. Select `/azure-pipelines.yml`
5. Save and run

## 📦 JFrog Artifactory Setup

### 1. Create Repository

1. Login to JFrog Artifactory
2. Go to Administration → Repositories → Local
3. Click "New Local Repository"
4. Select "Generic" type
5. Repository Key: `python-local`
6. Click "Create"

### 2. Generate API Key

1. In JFrog, click on your profile (top right)
2. Edit Profile → Generate API Key
3. Copy the key for Azure DevOps service connection

### 3. Set Permissions

Ensure your user has the following permissions:
- Deploy/Cache artifacts
- Read artifacts
- Annotate artifacts

## 🔄 CI/CD Pipeline Workflow

The pipeline consists of two stages:

### Build Stage
1. ✅ Setup Python environment
2. ✅ Install dependencies
3. ✅ Compile Python files
4. ✅ Archive application
5. ✅ Upload to JFrog Artifactory
6. ✅ Publish build info
7. ✅ Publish to Azure Pipelines artifacts

### Deploy Stage
1. ✅ Download artifact from JFrog
2. ✅ Deploy to Azure App Service
3. ✅ Verify deployment

## 🧪 Testing the Application

Once deployed, test the calculator:

1. Navigate to: `https://your-webapp-name.azurewebsites.net`
2. Enter two numbers
3. Click an operation button (Add, Subtract, Multiply, Divide)
4. View the result

### API Endpoint

You can also test the API directly:

```bash
curl -X POST https://your-webapp-name.azurewebsites.net/calculate \
  -H "Content-Type: application/json" \
  -d '{"operation":"add","num1":10,"num2":5}'
```

## 📝 Pipeline Configuration Details

### Build Tasks
- **UsePythonVersion**: Sets up Python 3.11
- **pip install**: Installs dependencies from requirements.txt
- **py_compile**: Validates Python syntax
- **ArchiveFiles**: Creates deployment package
- **ArtifactoryGenericUpload**: Uploads to JFrog
- **PublishBuildArtifacts**: Publishes to Azure Pipelines

### Deploy Tasks
- **ArtifactoryGenericDownload**: Downloads from JFrog
- **AzureWebApp**: Deploys to Azure App Service

## 🔐 Security Best Practices

1. **Never commit secrets** to source control
2. **Use service connections** for authentication
3. **Store API keys** in Azure Key Vault
4. **Enable HTTPS** on Azure App Service
5. **Use managed identities** where possible

## 🐛 Troubleshooting

### Application doesn't start
- Check startup command in App Service configuration
- Review Application logs in Azure Portal
- Verify all dependencies in requirements.txt

### Pipeline fails at JFrog upload
- Verify JFrog service connection credentials
- Check repository permissions
- Ensure repository exists in Artifactory

### Deployment fails
- Verify Azure service connection
- Check App Service name is correct
- Review deployment logs in Azure DevOps

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Azure App Service Documentation](https://docs.microsoft.com/azure/app-service/)
- [JFrog Artifactory Documentation](https://www.jfrog.com/confluence/display/JFROG/JFrog+Artifactory)
- [Azure Pipelines Documentation](https://docs.microsoft.com/azure/devops/pipelines/)

## 📄 License

This project is provided as-is for demonstration purposes.

## 👥 Support

For issues or questions:
1. Check Azure DevOps pipeline logs
2. Review Azure App Service logs
3. Check JFrog Artifactory build info
