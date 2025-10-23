# .NET 8.0 Migration Guide

## Executive Summary

The Azure Orbital Space SDK has migrated from .NET 6.0 to .NET 8.0 as the primary target framework. This upgrade provides significant performance improvements, new language features, and ensures continued support with .NET 8.0's Long-Term Support (LTS) lifecycle.

**Key Dates:**
- **.NET 6.0 End of Life (EOL):** November 12, 2024
- **.NET 8.0 LTS Support:** November 2023 - November 2026 (3 years)

## Why We Migrated

### End of Support for .NET 6.0

.NET 6.0 reached its end of support on November 12, 2024. After this date:
- No security patches or bug fixes are provided
- No technical support from Microsoft
- Potential security vulnerabilities remain unpatched
- Increased risk for production deployments

### Benefits of .NET 8.0

#### 1. Long-Term Support (LTS)
- Supported until **November 2026**
- 3 years of security patches and bug fixes
- Production-ready with Microsoft backing

#### 2. Performance Improvements

.NET 8.0 delivers significant performance gains over .NET 6.0:

- **20-40% faster JSON serialization/deserialization** - Critical for message processing in SpaceFX
- **15-25% reduction in memory allocation** - Important for resource-constrained satellite environments
- **Improved garbage collection** - Reduces pause times and improves application responsiveness
- **Native AOT compilation support** - Smaller container images and faster startup times
- **SIMD improvements** - Better performance for data processing workloads

#### 3. C# 12 Language Features

New language capabilities available with .NET 8.0:

- **Primary constructors** - Cleaner dependency injection patterns
- **Collection expressions** - More concise collection initialization
- **Ref readonly parameters** - Better performance with large structs
- **Default lambda parameters** - More flexible lambda expressions
- **Alias any type** - Improved type aliasing capabilities

#### 4. Container Optimizations

- **Smaller base images** - Reduced container size (10-15% smaller)
- **Faster cold starts** - Improved startup performance
- **Better multi-architecture support** - Enhanced ARM64 performance

#### 5. ASP.NET Core Improvements

- **Native AOT for minimal APIs** - Dramatically faster startup
- **Improved HTTP/3 support** - Better network performance
- **Enhanced rate limiting** - Built-in API protection
- **Better OpenAPI/Swagger integration** - Improved API documentation

## What Changed

### CI/CD Workflows

#### `.github/workflows/ci.yml`
- **Before:** Tested against both .NET 6.0 and 8.0
  ```yaml
  matrix:
    dotnet-version: ['6.0.x', '8.0.x']
  ```
- **After:** Tests only .NET 8.0
  ```yaml
  matrix:
    dotnet-version: ['8.0.x']
  ```

#### `.github/workflows/release.yml`
- **Before:** Setup both .NET 6.0 and 8.0
  ```yaml
  dotnet-version: |
    6.0.x
    8.0.x
  ```
- **After:** Setup only .NET 8.0
  ```yaml
  dotnet-version: '8.0.x'
  ```

### Project Files

All .csproj files targeting `net6.0` should be updated to `net8.0`:

```xml
<!-- Before -->
<TargetFramework>net6.0</TargetFramework>

<!-- After -->
<TargetFramework>net8.0</TargetFramework>
```

### Container Base Images

Dockerfiles using .NET 6.0 runtime images should be updated:

```dockerfile
# Before
FROM mcr.microsoft.com/dotnet/runtime:6.0-alpine

# After
FROM mcr.microsoft.com/dotnet/runtime:8.0-alpine
```

For SDK images used in builds:

```dockerfile
# Before
FROM mcr.microsoft.com/dotnet/sdk:6.0-alpine AS build

# After
FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build
```

## How to Build and Test with .NET 8.0

### Prerequisites

Install the .NET 8.0 SDK:

```bash
# Ubuntu/Debian
wget https://dot.net/v1/dotnet-install.sh
chmod +x dotnet-install.sh
./dotnet-install.sh --channel 8.0

# Windows (PowerShell)
winget install Microsoft.DotNet.SDK.8

# macOS (Homebrew)
brew install dotnet@8
```

Verify installation:

```bash
dotnet --list-sdks
# Should show: 8.0.xxx [/path/to/sdk]
```

### Building Applications

Standard build commands remain unchanged:

```bash
# Restore dependencies
dotnet restore

# Build project
dotnet build

# Build in Release mode
dotnet build --configuration Release

# Publish application
dotnet publish --configuration Release
```

### Running Tests

No changes to test commands:

```bash
# Run all tests
dotnet test

# Run with verbose output
dotnet test --verbosity normal

# Run with code coverage
dotnet test --collect:"XPlat Code Coverage"
```

### Local Development in Devcontainers

The devcontainer configuration will automatically use .NET 8.0 once the `spacefx-dev` feature is updated. No changes required to your local workflow.

### Updating Existing Projects

For each .NET project in the SDK:

1. **Update the target framework** in the `.csproj` file:
   ```xml
   <TargetFramework>net8.0</TargetFramework>
   ```

2. **Restore packages** to update dependencies:
   ```bash
   dotnet restore
   ```

3. **Build the project** to verify compatibility:
   ```bash
   dotnet build
   ```

4. **Run tests** to ensure functionality:
   ```bash
   dotnet test
   ```

5. **Update Dockerfile** if the project has container builds:
   ```dockerfile
   FROM mcr.microsoft.com/dotnet/runtime:8.0-alpine
   ```

## Breaking Changes to Watch For

### Minimal Breaking Changes from .NET 6.0 to 8.0

.NET 8.0 maintains excellent backward compatibility with .NET 6.0. Most applications will migrate without code changes.

### Known Breaking Changes

1. **System.Text.Json Changes**
   - More strict null handling by default
   - **Impact:** May affect message deserialization
   - **Fix:** Review JSON serialization options and add explicit null handling

2. **Regular Expression Timeout**
   - Default timeout added to prevent ReDoS attacks
   - **Impact:** Long-running regex operations may timeout
   - **Fix:** Increase timeout explicitly if needed: `new Regex(pattern, options, timeout)`

3. **Host Builder Configuration**
   - Slight changes to configuration order
   - **Impact:** Rare; only if using complex configuration scenarios
   - **Fix:** Review configuration loading order if issues arise

4. **Entity Framework Core 8.0**
   - If using EF Core, update to version 8.0
   - **Impact:** Query translation improvements may affect complex queries
   - **Fix:** Review and test database queries after upgrade

### Testing Recommendations

After migration, thoroughly test:

1. **Message serialization/deserialization** - Core to SpaceFX communication
2. **File I/O operations** - Critical for inbox/outbox processing
3. **External API calls** - Verify HTTP client behavior
4. **Database operations** - If using EF Core or ADO.NET
5. **Plugin loading** - Ensure plugin interfaces remain compatible

## Performance Optimization Opportunities

### Take Advantage of New Features

1. **Use Source Generators**
   - System.Text.Json source generation for faster serialization
   - Regular expression source generation for better performance

2. **Consider Native AOT**
   - For applications with strict startup time requirements
   - Results in smaller container images (50-70% reduction)
   - Note: Some reflection-based features may not work

3. **Leverage SIMD Improvements**
   - Use `System.Numerics.Vector` for data processing
   - Automatic vectorization in more scenarios

4. **Update to Minimal APIs** (if applicable)
   - Better performance than controller-based APIs
   - Supports Native AOT compilation

## Rollback Procedure

If critical issues are discovered after migration:

### Option 1: Rollback Individual Projects

1. **Revert .csproj changes:**
   ```xml
   <TargetFramework>net6.0</TargetFramework>
   ```

2. **Update Dockerfile:**
   ```dockerfile
   FROM mcr.microsoft.com/dotnet/runtime:6.0-alpine
   ```

3. **Rebuild and redeploy:**
   ```bash
   dotnet build
   docker build -t app:rollback .
   ```

### Option 2: Use Git to Revert Workflow Changes

```bash
# Find the commit before migration
git log --oneline --grep="NET8"

# Create a revert branch
git checkout -b revert-net8-migration

# Revert specific commits
git revert <commit-hash>

# Push and create PR
git push origin revert-net8-migration
```

### Option 3: Emergency Hotfix

For production issues:

1. **Keep .NET 6.0 containers available** in the registry with specific tags
2. **Modify deployment manifests** to reference the .NET 6.0 image:
   ```yaml
   image: registry.spacefx.local:5000/app:net6.0-latest
   ```
3. **Redeploy using Platform Deployment service**

## Timeline and Support

### Migration Schedule

- **Phase 1:** CI/CD workflows updated (Completed)
- **Phase 2:** Documentation and migration guide (Completed)
- **Phase 3:** Sample applications and plugins (In Progress)
- **Phase 4:** Runtime services update (Coordinated across repositories)

### Support Window

- **.NET 6.0:** Unsupported as of November 12, 2024
- **.NET 8.0:** Supported until November 2026
- **.NET 9.0:** Available (not LTS, supported for 18 months)
- **Next LTS:** .NET 10 (expected November 2025)

## Additional Resources

### Official Documentation

- [.NET 8.0 Release Notes](https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-8)
- [C# 12 What's New](https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-12)
- [Breaking Changes in .NET 8](https://learn.microsoft.com/en-us/dotnet/core/compatibility/8.0)
- [Migration Guide from .NET 6 to 8](https://learn.microsoft.com/en-us/dotnet/core/migration/60-to-80)

### Performance Resources

- [.NET 8 Performance Improvements](https://devblogs.microsoft.com/dotnet/performance-improvements-in-net-8/)
- [ASP.NET Core 8 Performance](https://devblogs.microsoft.com/dotnet/asp-net-core-updates-in-dotnet-8/)

### Azure Orbital Space SDK Documentation

- [Architecture Overview](../architecture/architecture.md)
- [System Requirements](../overview/requirements.md)
- [Getting Started Guide](../getting-started.md)
- [CLAUDE.md - Development Guide](../../CLAUDE.md)

## FAQ

### Q: Do I need to update all projects at once?

**A:** No. You can migrate incrementally. .NET 8.0 applications can reference .NET 6.0 libraries. However, for consistency and to avoid confusion, we recommend migrating all projects together.

### Q: Will my existing .NET 6.0 containers still work?

**A:** Yes, existing containers will continue to function. However, they should be rebuilt with .NET 8.0 for security updates and performance improvements.

### Q: What about my local development environment?

**A:** The devcontainer will be updated to use .NET 8.0 automatically. You may want to install .NET 8.0 SDK locally for better IDE support.

### Q: Are there any license changes?

**A:** No. .NET 8.0 uses the same MIT license as .NET 6.0.

### Q: How does this affect satellite deployments?

**A:** Minimal impact. The runtime framework size is similar. You'll benefit from better performance and reduced memory usage, which is valuable in resource-constrained satellite environments.

### Q: What about ARM64 support?

**A:** .NET 8.0 has improved ARM64 support with better performance and smaller images. This is beneficial for edge computing scenarios.

### Q: Can I still use .NET 6.0 for local development?

**A:** Not recommended. While technically possible, you should develop with the same runtime that will be used in production to avoid compatibility issues.

## Getting Help

If you encounter issues during migration:

1. **Review this guide** for common scenarios
2. **Check the [Breaking Changes documentation](https://learn.microsoft.com/en-us/dotnet/core/compatibility/8.0)**
3. **Search existing issues** on the GitHub repository
4. **Create a new issue** with:
   - Description of the problem
   - Error messages and stack traces
   - Steps to reproduce
   - Environment details (.NET version, OS, etc.)

## Checklist

Use this checklist to track your migration progress:

- [ ] Read and understand this migration guide
- [ ] Install .NET 8.0 SDK locally
- [ ] Update .csproj files to target `net8.0`
- [ ] Update Dockerfiles to use .NET 8.0 base images
- [ ] Run `dotnet restore` to update dependencies
- [ ] Build all projects successfully
- [ ] Run all tests and verify they pass
- [ ] Test message serialization/deserialization
- [ ] Test file I/O operations
- [ ] Update CI/CD pipelines (if not already done)
- [ ] Update documentation references to .NET version
- [ ] Rebuild and test container images
- [ ] Deploy to test environment
- [ ] Perform integration testing
- [ ] Review performance metrics
- [ ] Deploy to production
- [ ] Monitor for issues

---

**Document Version:** 1.0
**Last Updated:** 2025-10-23
**Applies to:** Azure Orbital Space SDK 0.11.0+
