# GitHub Packages Setup for Azure Orbital Space SDK Fork

This guide explains how to configure GitHub Packages for the `montge` fork of the Azure Orbital Space SDK, enabling package distribution and consumption for both Python and .NET projects.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Authentication Setup](#authentication-setup)
- [Python Package Configuration](#python-package-configuration)
- [.NET NuGet Package Configuration](#net-nuget-package-configuration)
- [Publishing Packages](#publishing-packages)
- [Consuming Packages in Development](#consuming-packages-in-development)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)

## Overview

The montge fork publishes SDK packages to GitHub Packages:

- **Python**: `microsoftazurespacefx` wheel package
- **.NET**: `Microsoft.Azure.SpaceSDK.*` NuGet packages

GitHub Packages serves as the distribution mechanism for the SDK in the fork environment, replacing the local `.wheel/` files and `/spacefx-dev/config/spacefx_version` dependencies used in the devcontainer environment.

### Package Registry URLs

- **Python (PyPI)**: `https://pypi.pkg.github.com/montge/simple`
- **.NET (NuGet)**: `https://nuget.pkg.github.com/montge/index.json`
- **Container Images**: `ghcr.io/montge/spacefx-*`

## Prerequisites

Before you begin, ensure you have:

1. **GitHub Account**: With access to the `montge` organization
2. **GitHub Personal Access Token (PAT)**: With appropriate scopes
3. **Development Tools**:
   - Python 3.8-3.11 with Poetry 1.3.2+
   - .NET 8.0 SDK
   - Docker (for container images)
   - Git

## Authentication Setup

### Creating a GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Configure the token:
   - **Name**: `Azure-Orbital-SDK-Packages` (or your preferred name)
   - **Expiration**: Choose appropriate duration (90 days recommended)
   - **Scopes**:
     - `read:packages` - Download packages from GitHub Packages
     - `write:packages` - Upload packages to GitHub Packages (for maintainers)
     - `repo` - Full repository access (if working with private repos)
     - `delete:packages` - Delete package versions (optional, for maintainers)

4. Generate and **save your token securely** - you won't see it again!

### Storing Your Token Securely

#### For Linux/macOS:

```bash
# Store in environment variable (add to ~/.bashrc or ~/.zshrc)
export GITHUB_TOKEN="ghp_your_token_here"

# Or use a credential manager
# Ubuntu/Debian:
sudo apt-get install gnome-keyring
secret-tool store --label='GitHub Token' service github token personal-access-token
```

#### For Windows:

```powershell
# PowerShell - set environment variable
[System.Environment]::SetEnvironmentVariable('GITHUB_TOKEN', 'ghp_your_token_here', 'User')

# Or use Windows Credential Manager
cmdkey /generic:github.com /user:montge /pass:ghp_your_token_here
```

## Python Package Configuration

### Method 1: Using Poetry Config (Recommended for Local Development)

```bash
# Configure Poetry to use GitHub Packages with authentication
poetry config http-basic.github-montge montge ghp_your_token_here

# Verify configuration
poetry config --list | grep github-montge
```

### Method 2: Using Environment Variables (Recommended for CI/CD)

```bash
# Set environment variables
export POETRY_HTTP_BASIC_GITHUB_MONTGE_USERNAME=montge
export POETRY_HTTP_BASIC_GITHUB_MONTGE_PASSWORD=ghp_your_token_here

# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
echo 'export POETRY_HTTP_BASIC_GITHUB_MONTGE_USERNAME=montge' >> ~/.bashrc
echo 'export POETRY_HTTP_BASIC_GITHUB_MONTGE_PASSWORD=ghp_your_token_here' >> ~/.bashrc
```

### Method 3: Using .netrc File (Alternative)

Create or edit `~/.netrc`:

```netrc
machine pypi.pkg.github.com
login montge
password ghp_your_token_here
```

Set appropriate permissions:

```bash
chmod 600 ~/.netrc
```

### Installing Python SDK Package

Once authentication is configured:

```bash
cd samples/payloadapps/python/shipdetector-onnx

# Install dependencies (including SDK from GitHub Packages)
poetry install

# Or install SDK package directly
poetry add microsoftazurespacefx --source github-montge
```

### Verifying Python Installation

```bash
# Check installed packages
poetry show microsoftazurespacefx

# Test import in Python
poetry run python -c "import microsoftazurespacefx; print(microsoftazurespacefx.__version__)"
```

## .NET NuGet Package Configuration

### Method 1: Using NuGet.config Files (Recommended)

NuGet.config files have been created in the repository:

- Root: `/NuGet.config`
- Sample apps: `samples/payloadapps/dotnet/*/NuGet.config`
- Plugins: `samples/plugins/**/NuGet.config`

These files reference GitHub Packages and use the `GITHUB_TOKEN` environment variable for authentication.

**Set your token as an environment variable:**

```bash
# Linux/macOS
export GITHUB_TOKEN="ghp_your_token_here"

# Windows PowerShell
$env:GITHUB_TOKEN = "ghp_your_token_here"

# Windows CMD
set GITHUB_TOKEN=ghp_your_token_here
```

### Method 2: Using dotnet CLI (Alternative)

```bash
# Add GitHub Packages source
dotnet nuget add source \
  --name github-montge \
  --username montge \
  --password ghp_your_token_here \
  --store-password-in-clear-text \
  "https://nuget.pkg.github.com/montge/index.json"

# List configured sources
dotnet nuget list source
```

### Method 3: Using NuGet.config with Direct Credentials (Not Recommended)

Edit `NuGet.config` to include credentials directly:

```xml
<packageSourceCredentials>
  <github-montge>
    <add key="Username" value="montge" />
    <add key="ClearTextPassword" value="ghp_your_token_here" />
  </github-montge>
</packageSourceCredentials>
```

⚠️ **Warning**: This stores credentials in plain text. Use only for testing.

### Building .NET Projects

```bash
cd samples/payloadapps/dotnet/starter-app

# Restore packages from GitHub Packages
dotnet restore

# Build the project
dotnet build

# Run tests
dotnet test
```

### Verifying .NET Installation

```bash
# List installed packages
dotnet list package

# Check for specific SDK packages
dotnet list package | grep Microsoft.Azure.SpaceSDK
```

## Publishing Packages

### Publishing Python Packages

The workflow `.github/workflows/publish-packages.yml` handles package publishing.

**Manual trigger:**

```bash
# Using GitHub CLI
gh workflow run publish-packages.yml \
  --field version=0.11.0 \
  --field force_publish=true

# Or via GitHub UI: Actions → Publish Packages → Run workflow
```

**Automatic trigger:**

- Push to `main` branch
- Push version tag (e.g., `v0.11.0`)

**Verify published package:**

```bash
# Check GitHub Packages UI
# https://github.com/orgs/montge/packages

# Or try installing
pip install microsoftazurespacefx \
  --index-url https://pypi.pkg.github.com/montge/simple \
  --extra-index-url https://pypi.org/simple
```

### Publishing .NET Packages

**Build NuGet packages:**

```bash
# From SDK source repository (e.g., azure-orbital-space-sdk-core)
dotnet pack -c Release -o ./nupkg

# Push to GitHub Packages
dotnet nuget push "./nupkg/*.nupkg" \
  --source "https://nuget.pkg.github.com/montge/index.json" \
  --api-key ghp_your_token_here
```

**Verify published package:**

```bash
# List available versions
dotnet package search Microsoft.Azure.SpaceSDK.Core \
  --source "https://nuget.pkg.github.com/montge/index.json"

# Or check GitHub Packages UI
# https://github.com/orgs/montge/packages
```

## Consuming Packages in Development

### Python Development Workflow

1. **Clone the repository:**
   ```bash
   git clone git@github.com:montge/azure-orbital-space-sdk.git
   cd azure-orbital-space-sdk
   ```

2. **Configure Poetry authentication:**
   ```bash
   poetry config http-basic.github-montge montge $GITHUB_TOKEN
   ```

3. **Navigate to a Python app:**
   ```bash
   cd samples/payloadapps/python/shipdetector-onnx
   ```

4. **Install dependencies:**
   ```bash
   poetry install
   ```

5. **Run the application:**
   ```bash
   poetry run python src/app/main.py
   ```

### .NET Development Workflow

1. **Clone the repository:**
   ```bash
   git clone git@github.com:montge/azure-orbital-space-sdk.git
   cd azure-orbital-space-sdk
   ```

2. **Set GITHUB_TOKEN environment variable:**
   ```bash
   export GITHUB_TOKEN="ghp_your_token_here"
   ```

3. **Create spacefx_version file (for local development):**
   ```bash
   sudo mkdir -p /spacefx-dev/config
   echo "0.11.0" | sudo tee /spacefx-dev/config/spacefx_version
   ```

4. **Navigate to a .NET app:**
   ```bash
   cd samples/payloadapps/dotnet/starter-app
   ```

5. **Restore and build:**
   ```bash
   dotnet restore
   dotnet build
   ```

6. **Run the application:**
   ```bash
   dotnet run --project src/starter-app.csproj
   ```

## CI/CD Integration

### GitHub Actions

The workflows have been updated to use GitHub Packages:

**Python jobs:**

```yaml
- name: Configure Poetry for GitHub Packages
  run: |
    poetry config http-basic.github-montge montge ${{ secrets.GITHUB_TOKEN }}

- name: Install dependencies
  run: poetry install
```

**. NET jobs:**

```yaml
- name: Create spacefx_version file
  run: |
    sudo mkdir -p /spacefx-dev/config
    echo "0.11.0" | sudo tee /spacefx-dev/config/spacefx_version

- name: Configure NuGet for GitHub Packages
  run: |
    dotnet nuget add source \
      --name github-montge \
      --username montge \
      --password ${{ secrets.GITHUB_TOKEN }} \
      --store-password-in-clear-text \
      "https://nuget.pkg.github.com/montge/index.json"

- name: Restore packages
  run: dotnet restore
```

### Other CI Systems

**Jenkins:**

```groovy
environment {
    GITHUB_TOKEN = credentials('github-token')
}

stages {
    stage('Python Setup') {
        steps {
            sh 'poetry config http-basic.github-montge montge $GITHUB_TOKEN'
        }
    }
}
```

**GitLab CI:**

```yaml
variables:
  POETRY_HTTP_BASIC_GITHUB_MONTGE_USERNAME: montge
  POETRY_HTTP_BASIC_GITHUB_MONTGE_PASSWORD: $GITHUB_TOKEN

before_script:
  - dotnet nuget add source "https://nuget.pkg.github.com/montge/index.json" \
      -n github-montge -u montge -p $GITHUB_TOKEN --store-password-in-clear-text
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Authentication Failed (401 Unauthorized)

**Problem:**
```
HTTP Error 401: Unauthorized
Could not authenticate to GitHub Packages
```

**Solutions:**

- Verify your GitHub PAT is valid and not expired
- Ensure PAT has `read:packages` scope
- Check username is correct (`montge`)
- For Poetry, verify config: `poetry config --list | grep github-montge`
- For NuGet, check: `dotnet nuget list source`

**Test authentication:**

```bash
# Test Python auth
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user

# Test NuGet auth
dotnet nuget list source
```

#### 2. Package Not Found (404)

**Problem:**
```
Package 'microsoftazurespacefx' not found
Package 'Microsoft.Azure.SpaceSDK.Core' not found
```

**Solutions:**

- Verify the package has been published: https://github.com/orgs/montge/packages
- Run the publish-packages workflow to publish SDK packages
- Check package name spelling (case-sensitive)
- Ensure you're authenticated (401 vs 404 can be confusing)

**Check package existence:**

```bash
# Python
pip index versions microsoftazurespacefx \
  --index-url https://pypi.pkg.github.com/montge/simple

# .NET
nuget list Microsoft.Azure.SpaceSDK.Core \
  -Source https://nuget.pkg.github.com/montge/index.json
```

#### 3. Version Conflicts

**Problem:**
```
The package 'Microsoft.Azure.SpaceSDK.Core' requires version '0.11.0' but found '0.10.0'
```

**Solutions:**

- Update `/spacefx-dev/config/spacefx_version` file to match published version
- Publish the correct version to GitHub Packages
- Clear NuGet cache: `dotnet nuget locals all --clear`
- Clear Poetry cache: `poetry cache clear --all github-montge`

#### 4. SSL Certificate Errors

**Problem:**
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Solutions:**

```bash
# Python - update certificates
pip install --upgrade certifi

# Python - bypass SSL (not recommended for production)
poetry config certificates.github-montge.cert false

# .NET - clear NuGet cache
dotnet nuget locals http-cache --clear
```

#### 5. Missing spacefx_version File

**Problem:**
```
Error reading file '/spacefx-dev/config/spacefx_version'
```

**Solutions:**

```bash
# Create the file with correct version
sudo mkdir -p /spacefx-dev/config
echo "0.11.0" | sudo tee /spacefx-dev/config/spacefx_version

# Or update .csproj to use a fallback version
# Replace: $([System.IO.File]::ReadAllText('/spacefx-dev/config/spacefx_version'))
# With: 0.11.0
```

#### 6. Poetry Lock File Out of Sync

**Problem:**
```
The lock file is not compatible with the current version of Poetry
```

**Solutions:**

```bash
# Update lock file
poetry lock --no-update

# Or regenerate completely
rm poetry.lock
poetry install
```

#### 7. NuGet Package Source Already Exists

**Problem:**
```
error: Package source with Name: github-montge already exists
```

**Solutions:**

```bash
# Remove existing source
dotnet nuget remove source github-montge

# Then re-add with correct credentials
dotnet nuget add source \
  --name github-montge \
  --username montge \
  --password $GITHUB_TOKEN \
  --store-password-in-clear-text \
  "https://nuget.pkg.github.com/montge/index.json"
```

### Getting Help

If you encounter issues not covered here:

1. **Check workflow logs**: https://github.com/montge/azure-orbital-space-sdk/actions
2. **Review package status**: https://github.com/orgs/montge/packages
3. **Check GitHub Status**: https://www.githubstatus.com/
4. **File an issue**: https://github.com/montge/azure-orbital-space-sdk/issues

### Debugging Commands

**Python diagnostics:**

```bash
# Show Poetry config
poetry config --list

# Show installed packages
poetry show

# Verbose install
poetry install -vvv

# Export requirements
poetry export -f requirements.txt
```

**.NET diagnostics:**

```bash
# List NuGet sources
dotnet nuget list source

# Show package references
dotnet list package --include-transitive

# Verbose restore
dotnet restore --verbosity detailed

# Check SDK version
dotnet --info
```

## Additional Resources

- **GitHub Packages Documentation**: https://docs.github.com/packages
- **Poetry Documentation**: https://python-poetry.org/docs/
- **NuGet Documentation**: https://learn.microsoft.com/nuget/
- **Azure Orbital Space SDK**: https://github.com/montge/azure-orbital-space-sdk

## Summary

This guide covers:

✅ GitHub Personal Access Token creation
✅ Python package authentication (3 methods)
✅ .NET NuGet package authentication (3 methods)
✅ Publishing packages to GitHub Packages
✅ Consuming packages in development
✅ CI/CD integration examples
✅ Comprehensive troubleshooting

For questions or issues, please file an issue in the main SDK repository.
