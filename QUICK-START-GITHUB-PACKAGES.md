# Quick Start: GitHub Packages for montge Fork

This is a quick reference guide for getting started with GitHub Packages in the montge fork of Azure Orbital Space SDK.

## Prerequisites

1. GitHub account with access to `montge` organization
2. GitHub Personal Access Token (PAT) with `read:packages` scope

## Create GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens
2. "Generate new token (classic)"
3. Scopes: ✅ `read:packages`, ✅ `write:packages` (for publishing)
4. Save your token: `ghp_xxxxxxxxxxxxx`

## Setup Authentication

### For Python Projects

```bash
# Configure Poetry with GitHub Packages
poetry config http-basic.github-montge montge ghp_your_token_here
```

### For .NET Projects

```bash
# Set environment variable
export GITHUB_TOKEN="ghp_your_token_here"

# Create spacefx_version file (for local development)
sudo mkdir -p /spacefx-dev/config
echo "0.11.0" | sudo tee /spacefx-dev/config/spacefx_version
```

## Quick Commands

### Python Development

```bash
# Clone repository
git clone git@github.com:montge/azure-orbital-space-sdk.git
cd azure-orbital-space-sdk/samples/payloadapps/python/shipdetector-onnx

# Configure Poetry
poetry config http-basic.github-montge montge $GITHUB_TOKEN

# Install dependencies
poetry install

# Run application
poetry run python src/app/main.py
```

### .NET Development

```bash
# Clone repository
git clone git@github.com:montge/azure-orbital-space-sdk.git
cd azure-orbital-space-sdk/samples/payloadapps/dotnet/starter-app

# Ensure GITHUB_TOKEN is set
export GITHUB_TOKEN="ghp_your_token_here"

# Restore and build
dotnet restore
dotnet build
dotnet run --project src/starter-app.csproj
```

## Publish Packages

### Via GitHub UI

1. Go to: https://github.com/montge/azure-orbital-space-sdk/actions
2. Select "Publish Packages to GitHub Packages"
3. "Run workflow" → Set version (e.g., 0.11.0)
4. Run

### Via GitHub CLI

```bash
gh workflow run publish-packages.yml --field version=0.11.0
```

## Troubleshooting

### 401 Unauthorized

```bash
# Check your token
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user

# Reconfigure Poetry
poetry config http-basic.github-montge montge $GITHUB_TOKEN

# Check NuGet sources
dotnet nuget list source
```

### Package Not Found

```bash
# Verify package exists
# Go to: https://github.com/orgs/montge/packages

# Run publish workflow to create packages
gh workflow run publish-packages.yml
```

### Clear Cache

```bash
# Python
poetry cache clear --all github-montge

# .NET
dotnet nuget locals all --clear
```

## Key Files

- **Documentation**: `/docs/development/GITHUB-PACKAGES-SETUP.md`
- **Full Report**: `/GITHUB-PACKAGES-IMPLEMENTATION-REPORT.md`
- **Python Config**: `samples/payloadapps/python/README-GITHUB-PACKAGES.md`
- **NuGet Config**: `NuGet.config` (root and in sample directories)

## Package URLs

- **Python**: https://pypi.pkg.github.com/montge/simple
- **.NET**: https://nuget.pkg.github.com/montge/index.json
- **Containers**: ghcr.io/montge/spacefx-*
- **Browse**: https://github.com/orgs/montge/packages

## CI/CD

Workflows are pre-configured. Just push to `main` or create PR:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

Check status: https://github.com/montge/azure-orbital-space-sdk/actions

## Support

- **Issues**: https://github.com/montge/azure-orbital-space-sdk/issues
- **Full docs**: See `/docs/development/GITHUB-PACKAGES-SETUP.md`

---

**Remember**: Always use `GITHUB_TOKEN` environment variable or Poetry config for authentication!
