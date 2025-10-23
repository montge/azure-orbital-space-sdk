# Using GitHub Packages with Python Applications

This directory contains Python applications that depend on the `microsoftazurespacefx` package from GitHub Packages.

## Setup Authentication

Before you can install dependencies, you need to configure Poetry to authenticate with GitHub Packages:

### Option 1: Using Environment Variable (Recommended for CI/CD)

```bash
export POETRY_HTTP_BASIC_GITHUB_MONTGE_USERNAME=montge
export POETRY_HTTP_BASIC_GITHUB_MONTGE_PASSWORD=<your-github-pat>
```

### Option 2: Using Poetry Config (Recommended for Local Development)

```bash
# Configure credentials for github-montge source
poetry config http-basic.github-montge montge <your-github-pat>
```

### Option 3: Using .netrc File

Create or edit `~/.netrc`:

```
machine pypi.pkg.github.com
login montge
password <your-github-pat>
```

## Creating a GitHub Personal Access Token

1. Go to GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "Poetry GitHub Packages")
4. Select scopes:
   - `read:packages` - Download packages from GitHub Package Registry
   - `write:packages` - Upload packages to GitHub Package Registry (if publishing)
5. Generate and save your token securely

## Installing Dependencies

Once authentication is configured:

```bash
cd samples/payloadapps/python/shipdetector-onnx
poetry install
```

## Troubleshooting

### Authentication Errors

If you get 401 Unauthorized errors:

```
HTTP Error 401: Unauthorized
```

Make sure:
1. Your GitHub PAT is valid and not expired
2. Your PAT has `read:packages` scope
3. The package exists in the montge organization
4. You're using the correct authentication method

### Package Not Found

If Poetry can't find the package:

```
Package microsoftazurespacefx not found
```

This means:
1. The package hasn't been published to GitHub Packages yet
2. Run the publish-packages workflow to build and publish the SDK packages

### Fallback to Local Wheel (Temporary)

If GitHub Packages is not available, you can temporarily use a local wheel file:

```toml
[tool.poetry.dependencies]
microsoftazurespacefx = { path = ".wheel/microsoftazurespacefx-0.11.0-py3-none-any.whl" }
```

## CI/CD Configuration

In GitHub Actions workflows, use:

```yaml
- name: Configure Poetry
  run: |
    poetry config http-basic.github-montge montge ${{ secrets.GITHUB_TOKEN }}

- name: Install dependencies
  run: poetry install
```

The `GITHUB_TOKEN` secret is automatically available in GitHub Actions.
