# CI/CD Pipeline Quick Start Guide

This guide will help you quickly get started with the Azure Orbital Space SDK CI/CD pipeline.

## Prerequisites

- Git repository with workflows committed
- GitHub Actions enabled on repository
- Permissions: Write access to repository, packages, and security

## 5-Minute Setup

### 1. Enable Workflows (First Time)

```bash
cd /home/e/Development/azure-orbital-space/azure-orbital-space-sdk

# Add all workflow files
git add .github/workflows/
git add .github/CICD_SUMMARY.md
git add .github/QUICKSTART.md

# Commit
git commit -m "feat: Add comprehensive CI/CD pipeline

- Multi-language build and test (Python, .NET)
- Multi-arch container builds (amd64, arm64)
- Comprehensive security scanning
- Automated release management
- Documentation validation

Includes 6 workflows:
- ci.yml: Main build and test pipeline
- container-build.yml: Multi-arch container images
- security-scan.yml: Security scanning suite
- release.yml: Automated release workflow
- docs.yml: Documentation validation
- codeql.yml: Advanced code analysis"

# Push to main branch
git push origin main
```

### 2. Verify Workflows

1. Go to GitHub repository
2. Click **Actions** tab
3. You should see workflows running:
   - ✅ CI - Build and Test
   - ✅ CodeQL Security Scanning
   - ✅ Documentation

### 3. Add Status Badges (Optional)

Add to your `README.md`:

```markdown
## Status

[![CI](https://github.com/microsoft/azure-orbital-space-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/microsoft/azure-orbital-space-sdk/actions/workflows/ci.yml)
[![Container Build](https://github.com/microsoft/azure-orbital-space-sdk/actions/workflows/container-build.yml/badge.svg)](https://github.com/microsoft/azure-orbital-space-sdk/actions/workflows/container-build.yml)
[![Security](https://github.com/microsoft/azure-orbital-space-sdk/actions/workflows/security-scan.yml/badge.svg)](https://github.com/microsoft/azure-orbital-space-sdk/actions/workflows/security-scan.yml)
[![Documentation](https://github.com/microsoft/azure-orbital-space-sdk/actions/workflows/docs.yml/badge.svg)](https://github.com/microsoft/azure-orbital-space-sdk/actions/workflows/docs.yml)
```

## Common Tasks

### Making a Code Change (with CI)

```bash
# Create feature branch
git checkout -b feature/my-new-feature

# Make changes to code
vim samples/payloadapps/python/my-app/src/main.py

# Commit
git commit -am "feat: Add awesome new feature"

# Push
git push origin feature/my-new-feature

# Create pull request on GitHub
# CI will automatically run and comment on PR with results
```

**What Happens:**
- ✅ Python tests run (all versions)
- ✅ .NET tests run (if applicable)
- ✅ Linting and formatting checks
- ✅ Sample validation
- ✅ CodeQL security scan
- ✅ Documentation checks (if docs changed)
- ✅ PR receives automated status comment

### Creating a Release

**Option 1: Tag-based (Recommended)**

```bash
# Ensure you're on main with latest changes
git checkout main
git pull origin main

# Create version tag (semantic versioning)
git tag v1.2.3

# Push tag
git push origin v1.2.3

# Release workflow automatically:
# 1. Runs full test suite
# 2. Builds multi-arch container images
# 3. Packages all artifacts
# 4. Creates GitHub release
# 5. Posts announcement issue
```

**Option 2: Manual Workflow Dispatch**

1. Go to **Actions** > **Release**
2. Click **Run workflow**
3. Enter version: `v1.2.3`
4. Select options:
   - Pre-release: No (for stable releases)
   - Draft: No (publish immediately)
5. Click **Run workflow**

**Pre-release Example:**

```bash
# For beta/rc releases
git tag v1.3.0-beta.1
git push origin v1.3.0-beta.1
# Automatically marked as pre-release
```

### Running Security Scans Manually

```bash
# Security scans run daily at 02:00 UTC automatically
# To run immediately:
```

1. Go to **Actions** > **Security Scanning**
2. Click **Run workflow**
3. Select branch: `main`
4. Click **Run workflow**

**View Results:**
- Go to **Security** tab > **Code scanning alerts**
- Filter by tool (CodeQL, Trivy, Bandit)

### Building Container Images Only

```bash
# Container builds run automatically on Dockerfile changes
# To force rebuild:
```

1. Go to **Actions** > **Container Build - Multi-Architecture**
2. Click **Run workflow**
3. Options:
   - Push images: Yes
   - Architectures: `linux/amd64,linux/arm64`
4. Click **Run workflow**

**Access Images:**

```bash
# Pull from GitHub Container Registry
docker pull ghcr.io/microsoft/spacefx-<app-name>:latest

# View all packages
# Go to repository main page > Packages
```

### Validating Documentation

```bash
# Runs automatically on doc changes
# To run manually:
```

1. Go to **Actions** > **Documentation**
2. Click **Run workflow**
3. Select branch
4. Click **Run workflow**

**Common Issues:**
- Broken links: Update or remove dead URLs
- Spelling: Check `.codespell-ignore` for tech terms
- Markdown lint: Run `markdownlint docs/` locally

## Troubleshooting

### "CI Failed" - What to Check

1. **Click on failed workflow run**
2. **Identify failed job** (red X)
3. **Expand failed step**
4. **Common issues:**

**Python Tests Failed:**
```bash
# Run locally to debug
cd samples/payloadapps/python/my-app
poetry install
poetry run pytest -v
```

**.NET Build Failed:**
```bash
# Run locally
cd samples/payloadapps/dotnet/my-app
dotnet restore
dotnet build
```

**Linting Failed:**
```bash
# Fix Python formatting
black samples/payloadapps/python/my-app/
isort samples/payloadapps/python/my-app/

# Fix .NET formatting
dotnet format samples/payloadapps/dotnet/my-app/
```

### "Container Build Failed"

**Check:**
1. Dockerfile.prod exists in `docker/` directory
2. Build context is correct
3. All COPY paths are valid

**Test locally:**
```bash
cd samples/payloadapps/python/my-app
docker build -f docker/Dockerfile.prod -t test:local .
```

### "Security Scan Warnings"

**Not Blocking:**
- Security scans use `continue-on-error: true`
- Review findings but they won't fail builds
- Address critical/high severity issues

**Review:**
1. Go to **Security** tab
2. Click **Code scanning alerts**
3. Review and dismiss false positives
4. Fix real issues

### "Release Failed"

**Common causes:**
1. **Pre-release tests failed** - Fix CI issues first
2. **Invalid version format** - Use `vX.Y.Z` format
3. **Release already exists** - Use different version

**Recovery:**
```bash
# Delete bad tag
git tag -d v1.2.3
git push origin :refs/tags/v1.2.3

# Fix issues, create new tag
git tag v1.2.4
git push origin v1.2.4
```

## Configuration

### Branch Protection

**Recommended settings for `main` branch:**

1. Go to **Settings** > **Branches** > **Add rule**
2. Branch name pattern: `main`
3. Enable:
   - ✅ Require pull request reviews (1 reviewer)
   - ✅ Require status checks to pass:
     - `CI Summary`
     - `Analyze (python)`
     - `Analyze (csharp)`
     - `Markdown Linting`
   - ✅ Require conversation resolution
   - ✅ Require linear history
   - ✅ Include administrators

### Repository Secrets

**Required for full functionality:**

1. **GITHUB_TOKEN** - Automatically provided
2. **Additional secrets (if needed):**
   - `PYPI_TOKEN` - For PyPI publishing (future)
   - `NUGET_TOKEN` - For NuGet publishing (future)

Add secrets:
1. **Settings** > **Secrets and variables** > **Actions**
2. Click **New repository secret**

### Container Registry

**GitHub Container Registry (GHCR) is pre-configured:**

- Images: `ghcr.io/microsoft/spacefx-*`
- Visibility: Inherits from repository
- No additional setup needed

**Make packages public:**
1. Go to repository **Packages** tab
2. Click on package
3. **Package settings** > **Change visibility** > Public

## Best Practices

### Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/awesome-feature

# 2. Make changes, commit frequently
git commit -am "feat: Add feature X"

# 3. Run local tests before pushing
poetry run pytest  # Python
dotnet test       # .NET

# 4. Push and create PR
git push origin feature/awesome-feature

# 5. Address CI feedback in PR

# 6. Merge when CI passes and approved
```

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/) for automatic changelog generation:

```bash
feat: Add new sensor plugin
fix: Resolve memory leak in data processing
docs: Update API documentation
refactor: Improve error handling
perf: Optimize image processing
test: Add integration tests
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `perf:` - Performance improvement
- `test:` - Adding tests
- `chore:` - Maintenance

### Release Cadence

**Recommended:**
- **Patch releases (x.y.Z)**: Weekly/bi-weekly for bug fixes
- **Minor releases (x.Y.0)**: Monthly for new features
- **Major releases (X.0.0)**: Quarterly for breaking changes

**Pre-releases:**
- `v1.2.0-alpha.1` - Early development
- `v1.2.0-beta.1` - Feature complete, testing
- `v1.2.0-rc.1` - Release candidate

### Security

**Weekly routine:**
1. Check **Security** tab for new alerts
2. Review Dependabot PRs
3. Update vulnerable dependencies
4. Run manual security scan if needed

**Critical vulnerabilities:**
1. Review alert details
2. Apply patches immediately
3. Create patch release
4. Notify users if needed

## Advanced Usage

### Custom Workflow Triggers

**Run CI on specific labels:**

Edit `.github/workflows/ci.yml`:
```yaml
on:
  pull_request:
    types: [opened, synchronize, labeled]
    # Add: Only run when 'ready-for-ci' label
```

### Skip CI for Documentation-Only Changes

Add to commit message:
```bash
git commit -m "docs: Update README [skip ci]"
```

Or use path filters (already configured).

### Matrix Build Customization

**Test additional Python version:**

Edit `.github/workflows/ci.yml`:
```yaml
matrix:
  python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']
  # Added 3.12
```

**Test on multiple OS:**
```yaml
matrix:
  os: [ubuntu-latest, windows-latest, macos-latest]
  python-version: ['3.11']
```

## Monitoring

### Workflow Health

**Check regularly:**
1. **Actions** tab > **View workflow runs**
2. Look for patterns:
   - Frequent failures: Fix root cause
   - Long run times: Optimize caching
   - Flaky tests: Improve test stability

### Metrics to Track

**Monthly:**
- Total workflow runs
- Success rate %
- Average duration
- Cache hit rates
- Security findings count

**View insights:**
1. Go to **Insights** tab
2. Click **Actions**
3. Review usage and trends

## Getting Help

### Documentation
- [Workflow README](.github/workflows/README.md)
- [CI/CD Summary](.github/CICD_SUMMARY.md)
- [GitHub Actions Docs](https://docs.github.com/en/actions)

### Support
- **Issues:** [Create issue](../../issues/new) with `ci/cd` label
- **Discussions:** [GitHub Discussions](../../discussions)
- **Email:** See [SUPPORT.md](../../SUPPORT.md)

### Debugging Steps

1. **Enable debug logging:**
   - Repository **Settings** > **Secrets**
   - Add: `ACTIONS_STEP_DEBUG` = `true`
   - Re-run workflow

2. **Review logs:**
   - Download logs from workflow run
   - Search for error messages
   - Check context (before/after error)

3. **Test locally:**
   - Use `act` tool to run workflows locally
   - Install: `brew install act`
   - Run: `act -j python-test`

4. **Ask for help:**
   - Create issue with logs
   - Include workflow run URL
   - Describe expected vs actual behavior

---

## Checklist

**Initial Setup:**
- [ ] Commit workflows to repository
- [ ] Push to main branch
- [ ] Verify workflows run successfully
- [ ] Add status badges to README
- [ ] Configure branch protection
- [ ] Enable GitHub Container Registry

**First PR:**
- [ ] Create feature branch
- [ ] Make changes
- [ ] Push and create PR
- [ ] Verify CI runs on PR
- [ ] Check PR comment from CI
- [ ] Merge when green

**First Release:**
- [ ] Create version tag (v0.1.0)
- [ ] Push tag
- [ ] Verify release workflow runs
- [ ] Check GitHub release created
- [ ] Verify container images published
- [ ] Download and verify artifacts

**Ongoing:**
- [ ] Review security alerts weekly
- [ ] Update dependencies monthly
- [ ] Monitor workflow health
- [ ] Keep documentation current

---

**Last Updated:** 2025-10-23
**Version:** 1.0.0

Happy building! 🚀
