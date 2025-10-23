# Testing Checklist: GitHub Packages Implementation

This checklist helps verify the GitHub Packages implementation is working correctly.

## Pre-Testing Setup

- [ ] Create GitHub Personal Access Token with `read:packages` and `write:packages` scopes
- [ ] Save PAT securely: `ghp_xxxxxxxxxxxxx`
- [ ] Set environment variable: `export GITHUB_TOKEN="ghp_xxxxxxxxxxxxx"`

## Phase 1: Package Publishing

### Test Publish Workflow

- [ ] Go to: https://github.com/montge/azure-orbital-space-sdk/actions
- [ ] Select "Publish Packages to GitHub Packages"
- [ ] Click "Run workflow"
- [ ] Set version: `0.11.0`
- [ ] Set force_publish: `true`
- [ ] Run workflow
- [ ] Wait for completion (should take ~5-10 minutes)

### Verify Published Packages

- [ ] Go to: https://github.com/orgs/montge/packages
- [ ] Check for `microsoftazurespacefx` package (Python)
- [ ] Check for `Microsoft.Azure.SpaceSDK.*` packages (.NET)
- [ ] Download artifacts from workflow run

**Expected**: Workflow completes successfully, artifacts are available

## Phase 2: Python Package Testing

### Local Development

```bash
# Navigate to Python sample
cd samples/payloadapps/python/shipdetector-onnx

# Configure Poetry authentication
poetry config http-basic.github-montge montge $GITHUB_TOKEN

# Clear cache (fresh start)
poetry cache clear --all github-montge

# Install dependencies
poetry install

# Verify SDK package
poetry show microsoftazurespacefx

# Test import
poetry run python -c "import microsoftazurespacefx; print('✅ Import successful')"
```

**Checklist**:
- [ ] Poetry config command succeeds
- [ ] `poetry install` completes without errors
- [ ] SDK package version is 0.11.0
- [ ] Python import works

### Troubleshooting (if needed)

If `poetry install` fails:
- [ ] Check authentication: `poetry config --list | grep github-montge`
- [ ] Verify token is valid: `curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user`
- [ ] Run with verbose output: `poetry install -vvv`
- [ ] Check if package exists at: https://github.com/orgs/montge/packages

## Phase 3: .NET Package Testing

### Local Development

```bash
# Create spacefx_version file
sudo mkdir -p /spacefx-dev/config
echo "0.11.0" | sudo tee /spacefx-dev/config/spacefx_version

# Verify file
cat /spacefx-dev/config/spacefx_version

# Navigate to .NET sample
cd samples/payloadapps/dotnet/starter-app

# Verify NuGet.config exists
cat NuGet.config

# Clear cache (fresh start)
dotnet nuget locals all --clear

# Restore packages
dotnet restore

# List installed packages
dotnet list package

# Build project
dotnet build

# Run tests (if any)
dotnet test
```

**Checklist**:
- [ ] spacefx_version file created successfully
- [ ] NuGet.config exists in project directory
- [ ] `dotnet restore` completes without errors
- [ ] SDK packages are listed: `Microsoft.Azure.SpaceSDK.Core`, `Microsoft.Azure.SpaceSDK.Client`
- [ ] Build succeeds
- [ ] No package version mismatches

### Troubleshooting (if needed)

If `dotnet restore` fails:
- [ ] Check NuGet sources: `dotnet nuget list source`
- [ ] Verify token: `echo $GITHUB_TOKEN`
- [ ] Add source manually: `dotnet nuget add source --name github-montge --username montge --password $GITHUB_TOKEN --store-password-in-clear-text "https://nuget.pkg.github.com/montge/index.json"`
- [ ] Restore with verbose output: `dotnet restore --verbosity detailed`

## Phase 4: CI/CD Workflow Testing

### Test ci.yml Workflow

```bash
# Make a small change to trigger workflow
echo "# Test change" >> README.md

# Commit and push
git add README.md
git commit -m "Test: Trigger CI workflow"
git push origin main
```

**Checklist**:
- [ ] Go to: https://github.com/montge/azure-orbital-space-sdk/actions
- [ ] Find "CI - Build and Test" workflow run
- [ ] Wait for completion (15-30 minutes)

**Check these jobs pass**:
- [ ] ✅ Python 3.8 Tests
- [ ] ✅ Python 3.9 Tests
- [ ] ✅ Python 3.10 Tests
- [ ] ✅ Python 3.11 Tests
- [ ] ✅ Python Linting
- [ ] ✅ .NET 8.0 Tests
- [ ] ✅ .NET Code Formatting
- [ ] ✅ Validate Sample Applications
- [ ] ✅ Validate Scripts
- [ ] ✅ CI Summary

### Test codeql.yml Workflow

**Checklist**:
- [ ] Go to workflow runs: https://github.com/montge/azure-orbital-space-sdk/actions/workflows/codeql.yml
- [ ] Check latest run status
- [ ] Verify both Python and C# analysis complete
- [ ] Check Security tab: https://github.com/montge/azure-orbital-space-sdk/security/code-scanning

**Expected**: Both language analyses complete successfully

### Test security-scan.yml Workflow

**Checklist**:
- [ ] Go to workflow runs: https://github.com/montge/azure-orbital-space-sdk/actions/workflows/security-scan.yml
- [ ] Check all security scan jobs complete
- [ ] Review security findings (if any)

**Jobs to verify**:
- [ ] ✅ Python Security Scan
- [ ] ✅ .NET Security Scan
- [ ] ✅ Secret Scanning
- [ ] ✅ Container Image Scan
- [ ] ✅ License Compliance
- [ ] ✅ Supply Chain Security

### Test container-build.yml Workflow

**Checklist**:
- [ ] Go to workflow runs: https://github.com/montge/azure-orbital-space-sdk/actions/workflows/container-build.yml
- [ ] Verify container builds for detected apps
- [ ] Check images published to: https://github.com/orgs/montge/packages?repo_name=azure-orbital-space-sdk

**Expected**: Container images with tag format `ghcr.io/montge/spacefx-*`

## Phase 5: Integration Testing

### Test Full Development Cycle

**Python App Development**:
```bash
# 1. Clone fresh repository
cd /tmp
git clone git@github.com:montge/azure-orbital-space-sdk.git
cd azure-orbital-space-sdk

# 2. Configure Poetry
poetry config http-basic.github-montge montge $GITHUB_TOKEN

# 3. Build Python app
cd samples/payloadapps/python/shipdetector-onnx
poetry install
poetry run pytest

# 4. Verify success
echo "✅ Python development cycle complete"
```

**.NET App Development**:
```bash
# 1. Use same cloned repository
cd /tmp/azure-orbital-space-sdk

# 2. Set up .NET environment
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxx"
sudo mkdir -p /spacefx-dev/config
echo "0.11.0" | sudo tee /spacefx-dev/config/spacefx_version

# 3. Build .NET app
cd samples/payloadapps/dotnet/starter-app
dotnet restore
dotnet build
dotnet run --project src/starter-app.csproj

# 4. Verify success
echo "✅ .NET development cycle complete"
```

**Checklist**:
- [ ] Fresh clone works
- [ ] Authentication configures correctly
- [ ] All dependencies install
- [ ] Projects build successfully
- [ ] Tests run (if applicable)

## Phase 6: Documentation Verification

### Review Documentation

- [ ] Read `/docs/development/GITHUB-PACKAGES-SETUP.md`
- [ ] Read `/samples/payloadapps/python/README-GITHUB-PACKAGES.md`
- [ ] Read `/GITHUB-PACKAGES-IMPLEMENTATION-REPORT.md`
- [ ] Read `/QUICK-START-GITHUB-PACKAGES.md`

**Checklist**:
- [ ] Documentation is clear and accurate
- [ ] All commands work as documented
- [ ] Troubleshooting section is helpful
- [ ] Examples are correct

### Test Documentation Examples

Pick 3 random commands from documentation and test them:

**Example 1**: _______________________
- [ ] Command works as documented
- [ ] Output matches expected result

**Example 2**: _______________________
- [ ] Command works as documented
- [ ] Output matches expected result

**Example 3**: _______________________
- [ ] Command works as documented
- [ ] Output matches expected result

## Phase 7: Error Handling

### Test Common Failure Scenarios

**Scenario 1: Invalid Token**
```bash
# Set invalid token
poetry config http-basic.github-montge montge invalid_token_xxx

# Try to install
poetry install
```
- [ ] Appropriate error message shown (401 Unauthorized)
- [ ] Error message is helpful

**Scenario 2: Missing spacefx_version**
```bash
# Remove spacefx_version file
sudo rm -rf /spacefx-dev/config

# Try to build .NET
dotnet restore samples/payloadapps/dotnet/starter-app/src/starter-app.csproj
```
- [ ] Appropriate error message shown
- [ ] Troubleshooting guide helps resolve issue

**Scenario 3: Package Not Found**
```bash
# Try to install non-existent package version
poetry add microsoftazurespacefx==99.99.99 --source github-montge
```
- [ ] Appropriate error message shown (404 Not Found)
- [ ] Clear what the problem is

## Sign-Off

### Developer Sign-Off

**Tested by**: _______________________
**Date**: _______________________
**Environment**: _______________________

**Overall Status**:
- [ ] ✅ All critical tests passed
- [ ] ⚠️ Some tests passed with warnings (document below)
- [ ] ❌ Tests failed (document below)

**Issues Found**:

1. _______________________
2. _______________________
3. _______________________

**Recommended Actions**:

1. _______________________
2. _______________________
3. _______________________

### Deployment Approval

- [ ] Code reviewed
- [ ] Testing complete
- [ ] Documentation verified
- [ ] CI/CD workflows passing
- [ ] Security scan clean
- [ ] Ready for team use

**Approved by**: _______________________
**Date**: _______________________

---

## Troubleshooting Reference

### Quick Fixes

**401 Unauthorized**:
```bash
# Reconfigure authentication
poetry config http-basic.github-montge montge $GITHUB_TOKEN
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxx"
```

**Package Not Found**:
```bash
# Check package exists
# Go to: https://github.com/orgs/montge/packages

# Run publish workflow
gh workflow run publish-packages.yml
```

**Version Mismatch**:
```bash
# Update spacefx_version
echo "0.11.0" | sudo tee /spacefx-dev/config/spacefx_version

# Clear cache
poetry cache clear --all github-montge
dotnet nuget locals all --clear
```

### Support Resources

- **Documentation**: `/docs/development/GITHUB-PACKAGES-SETUP.md`
- **Quick Start**: `/QUICK-START-GITHUB-PACKAGES.md`
- **Full Report**: `/GITHUB-PACKAGES-IMPLEMENTATION-REPORT.md`
- **Issues**: https://github.com/montge/azure-orbital-space-sdk/issues
- **Packages**: https://github.com/orgs/montge/packages

---

**Last Updated**: 2025-10-23
