# CI SDK Package Solution

## Problem

The CI pipeline was failing because it expected the `microsoftazurespacefx` Python package (version 0.11.0) to be available from GitHub Packages at `https://pypi.pkg.github.com/montge/simple`. However, **GitHub Packages does not support the PyPI simple repository format**, making it impossible to publish and consume Python packages via the standard PyPI protocol.

## Root Cause

- GitHub discontinued support for PyPI-compatible package repositories
- The package registry format GitHub uses is incompatible with Poetry/pip's simple repository protocol
- The fork (montge/azure-orbital-space-sdk) cannot use the original Microsoft GitHub Packages registry
- Publishing to public PyPI requires additional authentication and namespace ownership

## Solution Implemented

Instead of attempting to publish to GitHub Packages, the CI workflow now **builds the SDK package from source during each CI run**. This approach:

1. **Clones the SDK client repository** (`azure-orbital-space-sdk-client`)
2. **Builds the wheel locally** using Poetry
3. **Installs the wheel** before running tests
4. **Eliminates dependency** on any external package registry

## Changes Made

### 1. CI Workflow (.github/workflows/ci.yml)

Added a new step to build the SDK package:

```yaml
- name: Clone and build microsoftazurespacefx SDK
  run: |
    # Clone the SDK client repository
    git clone --depth 1 https://github.com/microsoft/azure-orbital-space-sdk-client.git /tmp/sdk-client

    cd /tmp/sdk-client

    # Create minimal protos directory structure
    mkdir -p spacefx/protos
    touch spacefx/protos/__init__.py

    # Temporarily allow Python 3.12 for building
    sed -i 's/python = ">=3.8,<3.12"/python = ">=3.8,<3.13"/' pyproject.toml

    # Build the SDK wheel
    poetry build

    # Copy wheel to a known location
    mkdir -p ${{ github.workspace }}/.sdk-wheels
    cp dist/*.whl ${{ github.workspace }}/.sdk-wheels/
```

Modified the test step to install the local wheel:

```yaml
# Install the locally built SDK wheel first
if [ -f "${{ github.workspace }}/.sdk-wheels/microsoftazurespacefx-0.11.0-py3-none-any.whl" ]; then
  echo "Installing microsoftazurespacefx from local wheel..."
  poetry run pip install "${{ github.workspace }}/.sdk-wheels/microsoftazurespacefx-0.11.0-py3-none-any.whl"
fi
```

### 2. pyproject.toml (shipdetector-onnx)

Removed the GitHub Packages source configuration:

**Before:**
```toml
microsoftazurespacefx = { version = "0.11.0", source = "github-montge" }

[[tool.poetry.source]]
name = "github-montge"
url = "https://pypi.pkg.github.com/montge/simple"
```

**After:**
```toml
microsoftazurespacefx = "0.11.0"

# Note: microsoftazurespacefx is installed from a locally built wheel in CI
# GitHub Packages does not support PyPI simple repository format, so the
# package is built from source (azure-orbital-space-sdk-client) during CI runs
```

## How It Works

1. **CI Trigger**: Push or PR to main/develop branches
2. **Setup**: Install Python, Poetry
3. **Build SDK**: Clone sdk-client repo → Build wheel → Cache in `.sdk-wheels/`
4. **Test Apps**: For each Python app:
   - Install the locally built SDK wheel via `poetry run pip install`
   - Install remaining dependencies via `poetry install`
   - Run tests with pytest

## Advantages

- ✅ **No external dependencies**: Works entirely within CI environment
- ✅ **Always uses latest**: Builds from the main branch of sdk-client
- ✅ **Fork-friendly**: No need for package registry access or authentication
- ✅ **Transparent**: Build process is visible in CI logs
- ✅ **Simple**: No complex package publishing setup required

## Disadvantages

- ⚠️ Slightly longer CI runs (adds ~30-60 seconds for SDK build)
- ⚠️ No version pinning beyond the pyproject.toml version constraint
- ⚠️ Requires network access to clone sdk-client repo

## Local Development

For local development, you have two options:

### Option 1: Build and install locally

```bash
# Clone and build the SDK
cd /tmp
git clone https://github.com/microsoft/azure-orbital-space-sdk-client.git
cd azure-orbital-space-sdk-client

# Create protos directory
mkdir -p spacefx/protos
touch spacefx/protos/__init__.py

# Build
poetry build

# Install in your project
cd /path/to/your/project
poetry run pip install /tmp/azure-orbital-space-sdk-client/dist/microsoftazurespacefx-0.11.0-py3-none-any.whl
```

### Option 2: Use development containers

The SDK provides devcontainers with the SDK pre-installed. See `.devcontainer/` directories for examples.

## Alternative Solutions Considered

### 1. Publish to PyPI.org
- ❌ Requires PyPI account and namespace ownership
- ❌ Fork would conflict with official package name
- ❌ Ongoing maintenance burden

### 2. Use GitHub Releases
- ❌ Requires manual upload for each version
- ❌ Still requires custom Poetry configuration
- ❌ Not automated

### 3. Private PyPI server
- ❌ Infrastructure overhead
- ❌ Hosting costs
- ❌ Maintenance complexity

### 4. Git dependencies in Poetry
- ❌ Poetry doesn't support subdirectory Git dependencies well
- ❌ Requires SSH keys or tokens in CI
- ❌ Less reliable than wheel installation

## Version Management

The SDK version is controlled by:
- `/home/e/Development/azure-orbital-space/azure-orbital-space-sdk-client/pyproject.toml` (version = "0.11.0")
- The CI workflow assumes this version when copying the wheel
- If the version changes, update the wheel filename in `.github/workflows/ci.yml`

## Testing

To verify the solution works:

1. Push changes to the repository
2. Check the "Python Tests" job in GitHub Actions
3. Look for the "Clone and build microsoftazurespacefx SDK" step
4. Verify wheel is built successfully
5. Confirm tests pass for Python applications

## Future Improvements

1. **Cache the built wheel** across CI runs using GitHub Actions cache
2. **Extract version dynamically** from pyproject.toml instead of hardcoding
3. **Add wheel verification** (checksums, signature validation)
4. **Parallel builds** if multiple SDK versions are needed
5. **Artifact upload** to save wheels for debugging

## Related Files

- `/home/e/Development/azure-orbital-space/azure-orbital-space-sdk/.github/workflows/ci.yml`
- `/home/e/Development/azure-orbital-space/azure-orbital-space-sdk/samples/payloadapps/python/shipdetector-onnx/pyproject.toml`
- `/home/e/Development/azure-orbital-space/azure-orbital-space-sdk-client/pyproject.toml`

## References

- [GitHub Packages Python documentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-python-registry)
- [Poetry documentation](https://python-poetry.org/docs/)
- [Python wheel format](https://packaging.python.org/en/latest/specifications/binary-distribution-format/)
