# .NET 8.0 Migration Checklist

This checklist provides a comprehensive guide for migrating Azure Orbital Space SDK to .NET 8.0. Use this to track progress and ensure all necessary steps are completed.

## Pre-Migration Steps

### Environment Preparation

- [ ] **Install .NET 8.0 SDK** on development machine
  ```bash
  dotnet --version  # Should show 8.0.x
  ```
- [ ] **Verify Docker** is updated to v24.0.7+
  ```bash
  docker --version
  ```
- [ ] **Review breaking changes** documentation
  - Read [.NET 8.0 Breaking Changes](https://learn.microsoft.com/en-us/dotnet/core/compatibility/8.0)
  - Review [NET8-UPGRADE-GUIDE.md](../docs/migration/NET8-UPGRADE-GUIDE.md)

### Repository Preparation

- [ ] **Create migration branch**
  ```bash
  git checkout -b feature/migrate-to-net8
  ```
- [ ] **Ensure clean working directory**
  ```bash
  git status  # Should show no uncommitted changes
  ```
- [ ] **Pull latest changes** from main branch
  ```bash
  git pull origin main
  ```
- [ ] **Backup current state** (optional but recommended)
  ```bash
  git tag pre-net8-migration
  ```

### Communication and Planning

- [ ] **Notify team** of migration schedule
- [ ] **Schedule testing window** for validation
- [ ] **Identify rollback contacts** if issues arise
- [ ] **Review deployment schedule** to avoid production conflicts

## Migration Steps

### Phase 1: CI/CD Workflows

- [x] **Update `.github/workflows/ci.yml`**
  - [x] Change matrix from `['6.0.x', '8.0.x']` to `['8.0.x']`
  - [x] Update workflow description/comments
  - [x] Update .NET formatting job to use 8.0.x

- [x] **Update `.github/workflows/release.yml`**
  - [x] Change dotnet-version from multi-version to single `8.0.x`
  - [x] Verify artifact build steps

- [ ] **Update `.github/workflows/container-build.yml`** (if needed)
  - [ ] Review base image references
  - [ ] Update build arguments if using .NET version variables

- [ ] **Test CI/CD workflows locally** (if possible)
  ```bash
  # Use act or similar tool to test GitHub Actions locally
  act -j dotnet-test
  ```

### Phase 2: Project Files (.csproj)

#### Sample Applications

- [ ] **Update .NET sample apps** in `samples/payloadapps/dotnet/`
  - [ ] `samples/payloadapps/dotnet/starter-app/src/starter-app.csproj`
    - [ ] Change `<TargetFramework>net6.0</TargetFramework>` to `net8.0`
    - [ ] Run `dotnet restore`
    - [ ] Run `dotnet build`
    - [ ] Run `dotnet test` (if tests exist)

#### Plugin Projects

- [ ] **Update Host Service plugins** in `samples/plugins/hostsvc/`
  - [ ] `hostsvc-link/starter-plugin/src/*.csproj`
  - [ ] `hostsvc-logging/starter-plugin/src/*.csproj`
  - [ ] `hostsvc-position/starter-plugin/src/*.csproj`
  - [ ] `hostsvc-sensor/starter-plugin/src/*.csproj`
  - [ ] For each:
    - [ ] Update `<TargetFramework>` to `net8.0`
    - [ ] Run `dotnet restore`
    - [ ] Run `dotnet build`

- [ ] **Update Platform Service plugins** in `samples/plugins/platform/`
  - [ ] `platform-mts/starter-plugin/src/*.csproj`
  - [ ] `platform-mts/cpp-sample-plugin/src/*.csproj`
  - [ ] `vth/starter-plugin/src/*.csproj`
  - [ ] For each:
    - [ ] Update `<TargetFramework>` to `net8.0`
    - [ ] Run `dotnet restore`
    - [ ] Run `dotnet build`

#### Debug Payload Apps

- [ ] **Update debugPayloadApp projects**
  - [ ] Update all `debugPayloadApp/debugPayloadApp.csproj` files
  - [ ] Verify they build successfully

### Phase 3: Container Images (Dockerfiles)

- [ ] **Update Dockerfile base images**
  - [ ] Search for all `Dockerfile.prod` files
    ```bash
    find . -name "Dockerfile.prod" -type f
    ```
  - [ ] Update runtime images:
    ```dockerfile
    # FROM mcr.microsoft.com/dotnet/runtime:6.0-alpine
    FROM mcr.microsoft.com/dotnet/runtime:8.0-alpine
    ```
  - [ ] Update SDK images:
    ```dockerfile
    # FROM mcr.microsoft.com/dotnet/sdk:6.0-alpine AS build
    FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build
    ```

- [ ] **Update specific Dockerfiles**
  - [ ] `samples/payloadapps/dotnet/*/docker/Dockerfile.prod`
  - [ ] Any plugin Dockerfiles (if they exist)
  - [ ] Base platform Dockerfiles (if applicable)

- [ ] **Test container builds locally**
  ```bash
  docker build -t test-app:net8 -f ./docker/Dockerfile.prod .
  ```

### Phase 4: Documentation Updates

- [x] **Create migration documentation**
  - [x] Create `docs/migration/NET8-UPGRADE-GUIDE.md`
  - [x] Create `.github/NET8-MIGRATION-CHECKLIST.md` (this file)

- [x] **Update CLAUDE.md**
  - [x] Update .NET version references from `net6.0, net8.0` to `net8.0`
  - [x] Add reference to migration guide

- [x] **Update requirements.md**
  - [x] Add .NET 8.0 SDK requirement
  - [x] Note .NET 6.0 EOL date
  - [x] Link to migration guide

- [ ] **Update README files**
  - [ ] Main `README.md` (if it references .NET version)
  - [ ] `samples/payloadapps/dotnet/*/README.md`
  - [ ] `samples/plugins/*/README.md`
  - [ ] Search for .NET 6.0 references:
    ```bash
    grep -r "\.NET 6" --include="*.md" .
    grep -r "net6\.0" --include="*.md" .
    ```

- [ ] **Update workflow documentation**
  - [ ] `.github/workflows/README.md` (if exists)
  - [ ] `.github/CICD_SUMMARY.md` (if exists)

### Phase 5: Configuration Files

- [ ] **Review VS Code configurations**
  - [ ] `.vscode/launch.json` files (check for .NET version-specific settings)
  - [ ] `.vscode/tasks.json` files

- [ ] **Review devcontainer configurations**
  - [ ] `.devcontainer/*/devcontainer.json` files
  - [ ] Check for hardcoded .NET 6.0 references
  - [ ] Note: `spacefx-dev` feature should handle .NET version

- [ ] **Review build scripts**
  - [ ] `scripts/` directory
  - [ ] Check for hardcoded version references
  - [ ] Search for "6.0" in shell scripts:
    ```bash
    grep -r "6\.0" scripts/ --include="*.sh"
    ```

## Testing Steps

### Unit and Integration Testing

- [ ] **Run all .NET tests**
  ```bash
  # From repository root
  for csproj in $(find . -name "*Test*.csproj" -o -name "*Tests*.csproj"); do
    echo "Testing: $csproj"
    dotnet test "$csproj" --verbosity normal
  done
  ```

- [ ] **Verify test results**
  - [ ] All tests pass
  - [ ] No new warnings introduced
  - [ ] Test coverage maintained

### Build Verification

- [ ] **Build all .NET projects**
  ```bash
  # Build all projects
  for csproj in $(find ./samples -name "*.csproj"); do
    echo "Building: $csproj"
    dotnet build "$csproj" --configuration Release
  done
  ```

- [ ] **Build all container images**
  ```bash
  # Test container builds for each sample app
  for dockerfile in $(find ./samples -name "Dockerfile.prod"); do
    app_name=$(basename $(dirname $(dirname "$dockerfile")))
    echo "Building container: $app_name"
    docker build -t "$app_name:net8-test" -f "$dockerfile" $(dirname $(dirname "$dockerfile"))
  done
  ```

- [ ] **Verify container image sizes**
  ```bash
  docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep net8-test
  ```
  - [ ] Images should be 10-15% smaller than .NET 6.0 versions

### Functional Testing

- [ ] **Test in devcontainer environment**
  - [ ] Open project in devcontainer
  - [ ] Verify .NET 8.0 is used: `dotnet --version`
  - [ ] Build projects within devcontainer
  - [ ] Run debug configurations

- [ ] **Test sample applications**
  - [ ] Deploy starter-app to test cluster
  - [ ] Verify message processing works
  - [ ] Check file inbox/outbox operations
  - [ ] Monitor logs for errors

- [ ] **Test plugin loading**
  - [ ] Deploy plugins to appropriate services
  - [ ] Verify plugins load correctly
  - [ ] Test plugin functionality
  - [ ] Check for version compatibility issues

### Performance Testing

- [ ] **Benchmark message processing**
  - [ ] Compare .NET 8.0 vs .NET 6.0 performance
  - [ ] Measure serialization/deserialization speed
  - [ ] Verify 20-40% improvement in JSON operations

- [ ] **Monitor memory usage**
  - [ ] Deploy to test cluster
  - [ ] Run for extended period (24+ hours)
  - [ ] Compare memory allocation vs .NET 6.0
  - [ ] Verify 15-25% reduction in allocations

- [ ] **Measure startup time**
  - [ ] Cold start time for containers
  - [ ] Application initialization time
  - [ ] Verify improvements in pod startup

### Security and Vulnerability Testing

- [ ] **Run Trivy security scan** (CI/CD handles this automatically)
  - [ ] Verify no new critical vulnerabilities
  - [ ] Compare vulnerability count vs .NET 6.0

- [ ] **Review dependency updates**
  - [ ] Check NuGet package versions
  - [ ] Ensure all packages support .NET 8.0
  - [ ] Update packages to latest stable versions

## Validation Steps

### Code Review

- [ ] **Self-review all changes**
  - [ ] Use `git diff` to review modifications
  - [ ] Ensure no unintended changes
  - [ ] Verify consistent formatting

- [ ] **Peer review**
  - [ ] Create pull request
  - [ ] Request reviews from team members
  - [ ] Address feedback and comments

### CI/CD Validation

- [ ] **Verify all CI/CD checks pass**
  - [ ] Python tests: ✅
  - [ ] .NET tests: ✅
  - [ ] Container builds: ✅
  - [ ] Security scans: ✅
  - [ ] Linting and formatting: ✅

- [ ] **Review CI/CD outputs**
  - [ ] Check for new warnings
  - [ ] Verify build times (should be similar or faster)
  - [ ] Confirm artifact sizes

### Documentation Review

- [ ] **Verify documentation accuracy**
  - [ ] All links work correctly
  - [ ] Code examples are accurate
  - [ ] Version numbers are correct

- [ ] **Spelling and grammar check**
  - [ ] Run spell checker on documentation
  - [ ] Review for clarity and consistency

### Deployment Testing

- [ ] **Deploy to development cluster**
  - [ ] Stage cluster with .NET 8.0 runtime
  - [ ] Deploy sample applications
  - [ ] Verify all services start correctly

- [ ] **Deploy to staging cluster** (if available)
  - [ ] Full deployment of all components
  - [ ] Run integration tests
  - [ ] Monitor for 24+ hours

- [ ] **Prepare production deployment plan**
  - [ ] Document deployment steps
  - [ ] Identify rollback procedures
  - [ ] Schedule deployment window

## Post-Migration Steps

### Cleanup

- [ ] **Remove .NET 6.0 artifacts**
  - [ ] Delete old container images tagged with .NET 6.0
    ```bash
    docker images | grep net6 | awk '{print $3}' | xargs docker rmi
    ```
  - [ ] Clean up old build outputs
  - [ ] Remove temporary test branches

- [ ] **Update .gitignore** (if needed)
  - [ ] Ensure build artifacts are excluded
  - [ ] Add any new .NET 8.0 specific patterns

### Communication

- [ ] **Announce migration completion**
  - [ ] Update team on migration status
  - [ ] Share migration guide with users
  - [ ] Highlight key benefits

- [ ] **Update external documentation** (if applicable)
  - [ ] Public-facing documentation
  - [ ] API documentation
  - [ ] Release notes

### Monitoring

- [ ] **Monitor production deployments**
  - [ ] Watch for errors in logs
  - [ ] Monitor resource usage (CPU, memory)
  - [ ] Track application performance metrics
  - [ ] Verify no regression in functionality

- [ ] **Collect feedback**
  - [ ] Gather developer feedback
  - [ ] Note any issues or improvements
  - [ ] Document lessons learned

### Future Planning

- [ ] **Schedule next migration review**
  - [ ] .NET 10 (next LTS) expected November 2025
  - [ ] Begin planning 6-12 months before .NET 8.0 EOL (November 2026)

- [ ] **Update migration process**
  - [ ] Document what went well
  - [ ] Note areas for improvement
  - [ ] Update this checklist for future migrations

## Rollback Plan (If Needed)

### Emergency Rollback

- [ ] **Revert workflow changes**
  ```bash
  git revert <migration-commit-hash>
  git push origin main
  ```

- [ ] **Redeploy .NET 6.0 containers**
  - [ ] Pull .NET 6.0 images from registry
  - [ ] Update deployment manifests
  - [ ] Redeploy to cluster

- [ ] **Notify stakeholders**
  - [ ] Communicate rollback decision
  - [ ] Explain reason for rollback
  - [ ] Provide timeline for retry

### Post-Rollback Analysis

- [ ] **Identify root cause** of issues
- [ ] **Document problems** encountered
- [ ] **Update migration plan** to address issues
- [ ] **Schedule retry** after fixes

## Sign-Off

### Migration Team

- [ ] **Lead Developer** - Reviewed and approved all code changes
- [ ] **DevOps Engineer** - Verified CI/CD and deployment pipelines
- [ ] **QA/Testing** - Validated all testing requirements met
- [ ] **Technical Writer** - Reviewed and approved documentation
- [ ] **Product Owner** - Approved migration for production

### Final Checklist

- [ ] All pre-migration steps completed
- [ ] All migration steps completed
- [ ] All testing steps completed
- [ ] All validation steps completed
- [ ] All post-migration steps completed
- [ ] No blocking issues identified
- [ ] Rollback plan documented and ready
- [ ] Team trained on new version
- [ ] Documentation updated and published
- [ ] Production deployment scheduled

---

## Useful Commands Reference

### .NET Version Checks
```bash
# Check installed .NET SDKs
dotnet --list-sdks

# Check .NET version
dotnet --version

# Check runtime versions
dotnet --list-runtimes
```

### Find All .NET Projects
```bash
# Find all .csproj files
find . -name "*.csproj" -type f

# Find all projects targeting net6.0
grep -r "net6.0" --include="*.csproj" .

# Find all Dockerfiles
find . -name "Dockerfile*" -type f
```

### Build and Test
```bash
# Restore all projects
find . -name "*.csproj" -exec dotnet restore {} \;

# Build all projects
find . -name "*.csproj" -exec dotnet build {} --configuration Release \;

# Run all tests
find . -name "*Test*.csproj" -exec dotnet test {} --verbosity normal \;
```

### Container Operations
```bash
# List all .NET container images
docker images | grep dotnet

# Remove old .NET 6.0 images
docker images | grep "6.0" | awk '{print $3}' | xargs docker rmi -f

# Build multi-architecture image
docker buildx build --platform linux/amd64,linux/arm64 -t app:net8 .
```

### Git Operations
```bash
# Create feature branch
git checkout -b feature/migrate-to-net8

# View changes
git diff --stat

# Commit changes
git add .
git commit -m "Migrate to .NET 8.0"

# Create tag before migration
git tag pre-net8-migration
```

---

**Checklist Version:** 1.0
**Last Updated:** 2025-10-23
**For SDK Version:** 0.11.0+
