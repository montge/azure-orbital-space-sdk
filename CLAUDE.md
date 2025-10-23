# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repository contains the Azure Orbital Space SDK - a software development kit, runtime framework, and virtualization platform for developing and deploying applications to space. The SDK is built on Kubernetes (k3s), Dapr, and a microservices architecture.

**Key Architectural Components:**
- **Core Services** (core namespace): Fileserver, Registry, Switchboard
- **Host Services** (hostsvc namespace): Link, Logging, Position, Sensor
- **Platform Services** (platformsvc namespace): Deployment, Message Translation Service (MTS)
- **Payload Applications**: User-developed apps in isolated namespaces
- **Virtual Test Harness (VTH)**: Ground-based testing environment

This repository is part of a distributed system spanning multiple GitHub repositories. The `/spacefx-dev` devcontainer feature coordinates dependencies across repos.

## Development Environment

All development is done through devcontainers. There are 13 pre-configured devcontainers for different sample apps and plugins.

**Host Requirements:**
- 8 CPU cores, 8GB RAM (for development)
- Docker v24.0.7+
- DevContainer v0.338.1+

**Common Devcontainer Pattern:**
Each devcontainer uses the `ghcr.io/microsoft/azure-orbital-space-sdk/spacefx-dev:0.11.0` feature which:
- Downloads proto files, plugins, and data generators
- Sets up SDK dependencies and tools
- Configures workspace paths

## Common Commands

### Creating New Apps/Plugins

Create a new payload app or plugin from starter templates:

```bash
bash ./scripts/create-app.sh \
  --output-dir <target-directory> \
  --app-name <app-name> \
  --language [python|dotnet] \
  [--overwrite]
```

### Python Applications

**Setup dependencies:**
```bash
poetry install
```

**Run tests:**
```bash
poetry run pytest
```

**Type checking:**
```bash
poetry run mypy src/
```

**Debug locally (via VS Code tasks):**
- Use the "Debug Client" launch configuration in VS Code
- This uses the `deploy-debugshim-client` task which:
  - Copies config/models to `/var/spacedev/xfer/<app-name>/inbox`
  - Deploys the debug shim
  - Attaches debugger on port 5678

### .NET Applications

**Build:**
```bash
dotnet build
```

**Run tests:**
```bash
dotnet test
```

**Restore packages:**
```bash
dotnet restore
```

### Building and Deploying to Production Cluster

**Build container image:**
```bash
/var/spacedev/build/build_containerImage.sh \
  --dockerfile ${PWD}/path/to/Dockerfile.prod \
  --app-name <app-name> \
  --image-tag <version> \
  --architecture [amd64|arm64] \
  --repo-dir ${PWD}/path/to/app \
  --build-arg APP_DIRECTORY=/workspace/<app-name> \
  --devcontainer-json .devcontainer/<app-name>/devcontainer.json \
  --annotation-config azure-orbital-space-sdk.yaml \
  --no-push
```

**Tag and push to cluster registry:**
```bash
docker tag <app-name>:<version> registry.spacefx.local:5000/<app-name>:<version>
docker push registry.spacefx.local:5000/<app-name>:<version>
```

**Deploy via Platform Deployment service:**
```bash
# Copy artifacts to deployment inbox
sudo cp ./model/* /var/spacedev/xfer/platform-deployment/inbox/schedule/
sudo cp ./schedules/prod/* /var/spacedev/xfer/platform-deployment/inbox/schedule/
```

**Monitor app execution:**
```bash
watch -n 2 tree /var/spacedev/xfer/<app-name>
```

### Virtual Test Harness Setup

**Stage cluster with VTH and data generators:**
```bash
/var/spacedev/scripts/stage_spacefx.sh --vth \
  --container <datagenerator-name>:<version> \
  --artifact <proto-file>.proto \
  --artifact <datagenerator-config>.yaml \
  --artifact <plugin-dll>.dll \
  --artifact <plugin-manifest>.json.spacefx_plugin
```

**Deploy the cluster:**
```bash
/var/spacedev/scripts/deploy/deploy_spacefx.sh
```

### Debug Shim Commands

**Deploy debug shim (Python):**
```bash
/spacefx-dev/debugShim-deploy.sh \
  --debug_shim <app-name> \
  --python_file <path-to-main.py> \
  --port 5678
```

**Reset debug shim:**
```bash
/spacefx-dev/debugShim-reset.sh \
  --debug_shim <app-name> \
  [--skip-pod-wait]
```

## Code Architecture

### Directory Structure

```
/samples/
  ├── payloadapps/           # Sample applications
  │   ├── dotnet/            # .NET apps (net8.0)
  │   └── python/            # Python apps (3.9-3.13 LTS)
  ├── plugins/               # Service extension plugins
  │   ├── hostsvc/           # Host service plugins
  │   ├── platform/          # Platform service plugins
  │   └── vth/               # VTH plugins
  ├── datagenerator/         # VTH data generators
  ├── base-host-platform/    # Base platform reference
  └── config/                # Configuration templates

/docs/
  ├── architecture/          # Runtime framework & services docs
  ├── setup/                 # Development environment setup
  ├── personas/              # User role documentation
  ├── tools/                 # Development tools
  ├── walkthroughs/          # Step-by-step guides
  └── quick-starts/          # Getting started tutorials

/.devcontainer/             # 13 pre-configured environments
/scripts/                   # Build and creation utilities
```

### Communication Patterns

**Service-to-Service Communication:**
- Uses Dapr sidecars with MQTT pub/sub (port 4222)
- Payload apps subscribe to topics via `DirectToApp` messages
- Host services are accessed via standardized client libraries

**File Transfer:**
- SMB/CIFS shares via Fileserver service
- Apps have inbox/outbox directories: `/var/spacedev/xfer/<app-name>/`
- Link service coordinates file delivery

**Message Translation:**
- MTS converts between native satellite formats and standardized SDK formats
- Plugins define translation logic for specific subsystems

### Key Configuration Files

**Python apps:**
- `pyproject.toml` - Poetry dependencies and build config
- `app-config.json` - Application runtime configuration
- `.vscode/tasks.json` - VS Code task definitions
- `.vscode/launch.json` - Debug configurations
- `docker/Dockerfile.prod` - Production container definition
- `schedules/debug_image/` - Debug deployment configs
- `schedules/prod/` - Production deployment configs

**.NET apps:**
- `*.csproj` - Project file with NuGet package references
- `appsettings.json` - Runtime settings
- Version is controlled via `/spacefx-dev/config/spacefx_version`

**Plugins:**
- `*.spacefx_plugin` - JSON manifest file
- Plugin DLLs must match service interface contracts

## Client Libraries

### Python

**Import:**
```python
from microsoftazurespacefx import MessageFormats
from microsoftazurespacefx.client import Client
```

**Usage pattern:**
- Create client instance with app configuration
- Use async methods for service requests
- Subscribe to message responses via callbacks

### .NET

**NuGet packages:**
```xml
<PackageReference Include="Microsoft.Azure.SpaceSDK.Core" Version="[spacefx_version]" />
<PackageReference Include="Microsoft.Azure.SpaceSDK.Client" Version="[spacefx_version]" />
```

**Usage pattern:**
- Inherit from `BaseClient` or service-specific base classes
- Override message handlers for different message types
- Use dependency injection for configuration

## Important Patterns

### Namespace Isolation

Payload apps are deployed in isolated Kubernetes namespaces (`payloadapp-<name>`). Apps cannot communicate across namespace boundaries - this is enforced for multi-tenant security on-orbit.

### Plugin Architecture

Services are extended without modifying core code:
1. Implement service-specific interface
2. Compile plugin DLL
3. Create `.spacefx_plugin` manifest
4. Deploy manifest to service's plugin directory

### Deployment Workflow

1. Application built as Docker container
2. Image pushed to `registry.spacefx.local:5000`
3. Deployment YAML + schedule JSON placed in Platform Deployment inbox
4. Deployment service pulls image and creates Kubernetes pods
5. Config files transferred to app inbox via Fileserver
6. App starts and processes inbox contents

### Testing Strategy

**Local Development (Debug Shim):**
- Run app code directly with debugger attached
- Uses same runtime framework as production
- Files manually copied to inbox for testing

**Virtual Test Harness:**
- Full production deployment to local k3s cluster
- Data generators simulate satellite sensors/subsystems
- Tests same container images that deploy on-orbit
- Plugins customize test environment behavior

**Production:**
- VTH components not deployed (no internet access)
- MTS plugins connect to real satellite subsystems
- Apps run in resource-constrained environment (2 CPU, 2GB RAM)

## Version Management

SDK version is controlled by `/spacefx-dev/config/spacefx_version`. All NuGet packages, Docker images, and artifacts reference this version (e.g., `0.11.0`, `0.11.0-nightly`).

## Working with Proto Files

Proto files define gRPC service contracts and are shared across components:
- Located in `/var/spacedev/protos/`
- Copied to workspace via devcontainer `postStartCommand`
- Python: Include in `pyproject.toml` via `[[tool.poetry.include]]`
- .NET: Added to project with `Protobuf` or `ProtoContract` references

## Repository Context

This is the main SDK repository containing samples, documentation, and developer tools. The actual runtime services are in separate repositories:
- azure-orbital-space-sdk-core
- azure-orbital-space-sdk-client
- azure-orbital-space-sdk-setup
- azure-orbital-space-sdk-hostsvc-* (link, logging, position, sensor)
- azure-orbital-space-sdk-platform-* (mts, deployment)
- azure-orbital-space-sdk-vth
- azure-orbital-space-sdk-coresvc-* (fileserver, registry, switchboard)
- azure-orbital-space-sdk-data-generators

When developing, you primarily work in this repository, but the devcontainer feature coordinates dependencies from other repos.
