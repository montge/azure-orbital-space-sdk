# GitHub Actions Workflows

This directory contains the comprehensive CI/CD pipeline for the Azure Orbital Space SDK.

## Status Badges

Add these badges to your main README.md:

```markdown
[![CI](https://github.com/microsoft/azure-orbital-space-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/microsoft/azure-orbital-space-sdk/actions/workflows/ci.yml)
[![Container Build](https://github.com/microsoft/azure-orbital-space-sdk/actions/workflows/container-build.yml/badge.svg)](https://github.com/microsoft/azure-orbital-space-sdk/actions/workflows/container-build.yml)
[![Security](https://github.com/microsoft/azure-orbital-space-sdk/actions/workflows/security-scan.yml/badge.svg)](https://github.com/microsoft/azure-orbital-space-sdk/actions/workflows/security-scan.yml)
[![Documentation](https://github.com/microsoft/azure-orbital-space-sdk/actions/workflows/docs.yml/badge.svg)](https://github.com/microsoft/azure-orbital-space-sdk/actions/workflows/docs.yml)
[![CodeQL](https://github.com/microsoft/azure-orbital-space-sdk/actions/workflows/codeql.yml/badge.svg)](https://github.com/microsoft/azure-orbital-space-sdk/actions/workflows/codeql.yml)
```

## Workflows Overview

### 1. CI Pipeline (`ci.yml`)

**Purpose:** Main continuous integration pipeline for building and testing code changes.

**Triggers:**
- Push to `main`, `develop`, feature branches
- Pull requests to `main`, `develop`
- Manual workflow dispatch

**Jobs:**
- **Python Tests** - Run pytest across Python 3.8-3.11
- **Python Linting** - Black, isort, Flake8
- **.NET Tests** - Build and test .NET 6.0 and 8.0 projects
- **.NET Formatting** - Code formatting validation
- **Sample Validation** - Validate sample application structure
- **Script Validation** - Shellcheck for bash scripts
- **CI Summary** - Overall status and PR comments

**Key Features:**
- Multi-version testing (Python 3.8-3.11, .NET 6.0/8.0)
- Dependency caching for faster builds
- Test coverage reporting
- Type checking with mypy
- PR status comments

**Duration:** ~15-30 minutes

---

### 2. Container Build Pipeline (`container-build.yml`)

**Purpose:** Build multi-architecture container images for sample applications.

**Triggers:**
- Push to `main`, `develop` with container changes
- Pull requests affecting Dockerfiles
- Version tags (`v*.*.*`)
- Manual workflow dispatch

**Jobs:**
- **Detect Apps** - Scan for applications with Dockerfiles
- **Build Containers** - Multi-arch builds (amd64, arm64)
- **Test Containers** - Smoke tests for built images
- **Build Summary** - Status reporting

**Key Features:**
- Multi-architecture support (linux/amd64, linux/arm64)
- QEMU emulation for cross-platform builds
- GitHub Container Registry (ghcr.io) publishing
- Trivy vulnerability scanning
- SBOM (Software Bill of Materials) generation
- Layer caching for performance
- Docker metadata tagging

**Container Images Published:**
- `ghcr.io/microsoft/spacefx-<app-name>:<tag>`

**Duration:** ~30-60 minutes

---

### 3. Security Scanning Pipeline (`security-scan.yml`)

**Purpose:** Comprehensive security scanning beyond CodeQL.

**Triggers:**
- Push to `main`, `develop`
- Pull requests
- Daily schedule (02:00 UTC)
- Manual workflow dispatch

**Jobs:**
- **Python Security** - Safety, Bandit scanning
- **.NET Security** - Vulnerable package detection
- **Secret Scanning** - TruffleHog secret detection
- **Container Scanning** - Trivy Dockerfile analysis
- **License Compliance** - License checking
- **Supply Chain** - Dependency confusion checks
- **Security Summary** - Consolidated reporting

**Key Features:**
- Python: Safety + Bandit for vulnerability and security issues
- .NET: Native vulnerability detection
- Secret scanning with TruffleHog
- Container misconfiguration detection
- License compliance validation
- Automated issue creation for critical findings
- SARIF report upload to GitHub Security

**Duration:** ~20-30 minutes

---

### 4. Release Pipeline (`release.yml`)

**Purpose:** Automated release management with semantic versioning.

**Triggers:**
- Version tags (`v*.*.*`, including alpha/beta/rc)
- Manual workflow dispatch with version input

**Jobs:**
- **Validate Release** - Version format and prerequisite checks
- **Pre-Release Tests** - Full CI suite
- **Generate Changelog** - Automated changelog from git history
- **Build Artifacts** - Package samples, plugins, scripts, docs
- **Build Containers** - Multi-arch container images
- **Create Release** - GitHub release with all artifacts
- **Post-Release** - Announcements and notifications

**Key Features:**
- Semantic versioning validation
- Pre-release support (alpha, beta, rc)
- Automated changelog generation
- Artifact packaging with checksums
- Container image tagging
- GitHub release creation
- Release announcement issues
- Draft release support

**Release Artifacts:**
- Sample application archives
- Plugin templates
- Build scripts
- Documentation
- Container images
- SHA256 checksums

**Duration:** ~45-90 minutes

---

### 5. Documentation Pipeline (`docs.yml`)

**Purpose:** Validate and maintain documentation quality.

**Triggers:**
- Push/PR affecting docs or markdown files
- Weekly schedule (Sunday 00:00 UTC)
- Manual workflow dispatch

**Jobs:**
- **Markdown Linting** - markdownlint-cli2
- **Spell Check** - codespell with custom dictionary
- **Link Validation** - markdown-link-check
- **Structure Validation** - Required files and organization
- **Code Documentation** - Docstring coverage
- **Generate Report** - Summary and recommendations

**Key Features:**
- Markdown style enforcement
- Spell checking with technical term dictionary
- Internal and external link validation
- Documentation structure requirements
- Python docstring coverage analysis
- PR documentation feedback
- Automated issue creation for broken links

**Duration:** ~10-20 minutes

---

### 6. CodeQL Security Scanning (`codeql.yml`)

**Purpose:** Advanced semantic code analysis for security vulnerabilities.

**Triggers:**
- Push to `main` with code changes
- Pull requests to `main`
- Weekly schedule (Sunday 00:00 UTC)
- Manual workflow dispatch

**Jobs:**
- **Analyze (Python)** - Python security analysis
- **Analyze (C#)** - .NET security analysis

**Key Features:**
- Security-extended query suite
- Security and quality analysis
- Python and C#/.NET support
- SARIF result upload
- GitHub Security integration
- Space/embedded system focus

**Duration:** ~30-60 minutes

---

## Workflow Dependencies

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  Developer Push/PR                              │
│                                                 │
└────────────┬────────────────────────────────────┘
             │
             ├──► ci.yml (always runs)
             │
             ├──► codeql.yml (code changes)
             │
             ├──► docs.yml (doc changes)
             │
             ├──► security-scan.yml (scheduled daily)
             │
             └──► container-build.yml (container changes)

┌─────────────────────────────────────────────────┐
│                                                 │
│  Version Tag (v1.2.3)                           │
│                                                 │
└────────────┬────────────────────────────────────┘
             │
             └──► release.yml
                  ├──► Calls: ci.yml (pre-release tests)
                  └──► Calls: container-build.yml (images)
```

## Usage Guide

### Running Workflows Manually

All workflows support manual triggering via `workflow_dispatch`.

**Example: Manual CI Run**
1. Go to Actions tab
2. Select "CI - Build and Test"
3. Click "Run workflow"
4. Select branch
5. Click "Run workflow"

**Example: Manual Release**
1. Go to Actions tab
2. Select "Release"
3. Click "Run workflow"
4. Enter version (e.g., v1.2.3)
5. Select options (prerelease, draft)
6. Click "Run workflow"

### Creating a Release

**Automated via Git Tag:**
```bash
# Create and push a version tag
git tag v1.2.3
git push origin v1.2.3

# Pre-release versions
git tag v1.2.3-beta.1
git push origin v1.2.3-beta.1
```

**Manual via Workflow Dispatch:**
1. Navigate to Actions > Release
2. Click "Run workflow"
3. Enter version: `v1.2.3`
4. Select options as needed
5. Click "Run workflow"

### Viewing Security Findings

Security findings are uploaded to the GitHub Security tab:

1. Navigate to repository Security tab
2. Click "Code scanning alerts"
3. Filter by tool:
   - CodeQL: Semantic analysis
   - Trivy: Container vulnerabilities
   - Bandit: Python security issues

### Debugging Failed Workflows

**Check Job Logs:**
1. Go to Actions tab
2. Click on failed workflow run
3. Click on failed job
4. Expand failed step
5. Review error output

**Common Issues:**

**Python dependency errors:**
- Missing local SDK wheel is expected in CI
- Check if dependencies are in pyproject.toml

**.NET build failures:**
- Verify .NET version in workflow matches project
- Check for missing NuGet package sources

**Container build failures:**
- Verify Dockerfile.prod exists
- Check build context and arguments
- Review multi-arch compatibility

**Link check failures:**
- External links may be temporarily down
- Update or remove dead links
- Check .markdown-link-check.json config

## Caching Strategy

Workflows use GitHub Actions cache to speed up builds:

| Workflow | Cache Key | Cached Items |
|----------|-----------|--------------|
| CI | `poetry-py{version}-{lock-hash}` | Poetry dependencies |
| CI | `nuget-{version}-{csproj-hash}` | NuGet packages |
| Container Build | `gha` | Docker layers |
| Security Scan | `poetry-{lock-hash}` | Python packages |

**Cache Invalidation:**
- Automatic on dependency changes (lock files, .csproj)
- Manual: Delete cache via Actions > Caches

## Resource Usage

**Concurrent Jobs:**
- CI: Up to 4 parallel jobs (matrix builds)
- Container: Parallel builds per application
- Security: Up to 6 parallel scans

**Runner Minutes (approximate):**
- CI: 15-30 minutes
- Container Build: 30-60 minutes
- Security: 20-30 minutes
- Release: 45-90 minutes
- Docs: 10-20 minutes
- CodeQL: 30-60 minutes

**Storage:**
- Artifacts retained: 30-90 days
- Container images: Latest + tagged versions
- SARIF results: Permanent in Security tab

## Workflow Customization

### Modifying Python Test Matrix

Edit `ci.yml`:
```yaml
matrix:
  python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']  # Add 3.12
```

### Changing Container Architectures

Edit `container-build.yml`:
```yaml
env:
  PLATFORMS: 'linux/amd64,linux/arm64,linux/arm/v7'  # Add armv7
```

### Adjusting Security Scan Schedule

Edit `security-scan.yml`:
```yaml
schedule:
  - cron: '0 2 * * *'  # Daily at 02:00 UTC
  # Change to: '0 2 * * 1' for weekly (Mondays)
```

### Adding Custom Linters

Add to `ci.yml` python-lint job:
```yaml
- name: Run custom linter
  run: |
    pip install my-custom-linter
    my-custom-linter samples/
```

## Best Practices

### For Developers

1. **Before Pushing:**
   - Run local tests: `poetry run pytest`
   - Format code: `black .` or `dotnet format`
   - Check types: `mypy src/`

2. **Pull Requests:**
   - Ensure CI passes before requesting review
   - Address security warnings
   - Update documentation for new features

3. **Commits:**
   - Use conventional commit format for changelog generation
   - Prefix: `feat:`, `fix:`, `docs:`, `refactor:`, `perf:`

### For Maintainers

1. **Releases:**
   - Verify all tests pass on main before tagging
   - Use semantic versioning
   - Review generated changelog before publishing

2. **Security:**
   - Review security alerts weekly
   - Update dependencies regularly
   - Address critical findings promptly

3. **Documentation:**
   - Keep CLAUDE.md updated with workflow changes
   - Update README with new badges
   - Document any workflow customizations

## Troubleshooting

### Workflow Not Triggering

**Check:**
- Path filters match changed files
- Branch filters include your branch
- Workflow file syntax is valid (YAML)

**Solution:**
```bash
# Validate workflow syntax locally
cat .github/workflows/ci.yml | python -c "import yaml, sys; yaml.safe_load(sys.stdin)"
```

### Container Build Fails on ARM64

**Issue:** QEMU emulation timeout or OOM

**Solution:**
- Reduce parallel builds
- Increase timeout in workflow
- Build ARM64 on native runner (if available)

### Security Scan False Positives

**Issue:** Known safe patterns flagged

**Solution:**
1. Review finding carefully
2. If false positive, add to ignore list
3. Document reasoning in code comments

### Release Workflow Stuck

**Issue:** Waiting for dependent workflow

**Solution:**
- Check status of ci.yml and container-build.yml
- Fix any failures in dependencies
- Re-run release workflow after fixes

## Support

- **Issues:** [GitHub Issues](https://github.com/microsoft/azure-orbital-space-sdk/issues)
- **Discussions:** [GitHub Discussions](https://github.com/microsoft/azure-orbital-space-sdk/discussions)
- **Security:** See [SECURITY.md](../../SECURITY.md)

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines on:
- Proposing workflow changes
- Testing workflow modifications
- Submitting workflow improvements

---

**Last Updated:** 2025-10-23
**Workflow Version:** 1.0.0
