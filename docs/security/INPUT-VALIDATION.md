# Input Validation Guide

## Overview

The Azure Orbital Space SDK provides comprehensive input validation libraries to prevent injection attacks and ensure data integrity. This guide covers when and how to use each validation method, common pitfalls, and security best practices.

**Key Principles:**
- **Whitelist Approach**: Only explicitly allowed characters are permitted
- **Defense in Depth**: Multiple layers of validation
- **Fail Secure**: Invalid input is rejected, not sanitized into validity
- **Clear Error Messages**: Actionable feedback for debugging

## Table of Contents

1. [Quick Start](#quick-start)
2. [Validation Methods](#validation-methods)
3. [Common Use Cases](#common-use-cases)
4. [Security Best Practices](#security-best-practices)
5. [Common Pitfalls](#common-pitfalls)
6. [Performance Considerations](#performance-considerations)
7. [Integration Examples](#integration-examples)

## Quick Start

### C# / .NET

```csharp
using Microsoft.Azure.SpaceSDK;

// Validate Docker image name
var result = SecurityValidation.ValidateDockerImageName("registry.io/myapp");
if (!result.IsValid)
{
    throw new ArgumentException(result.ErrorMessage);
}

// Or use extension methods
string imageName = userInput;
if (!imageName.IsValidDockerImageName())
{
    throw new ArgumentException("Invalid image name");
}

// Validate and throw in one call
SecurityValidation.ValidateDockerImageName(userInput).ThrowIfInvalid("imageName");
```

### Python

```python
from spacefx.security import validate_docker_image_name, validate_file_path

# Validate Docker image name
if not validate_docker_image_name("registry.io/myapp"):
    raise ValueError("Invalid image name")

# Validate file path
if not validate_file_path(user_path, base_directory):
    raise ValueError("Invalid or unsafe file path")
```

## Validation Methods

### Docker Validation

#### `ValidateDockerImageName` / `validate_docker_image_name`

**Purpose**: Validate Docker image names according to Docker's naming conventions.

**When to Use**:
- Before pulling or pushing Docker images
- When accepting user-provided image names
- In deployment configurations
- In container orchestration scripts

**Valid Format**:
- Lowercase alphanumeric characters
- Separators: `.`, `_`, `-`, `/`
- Maximum 255 characters
- Cannot start or end with separator

**Examples**:
```csharp
// C# Examples
✅ SecurityValidation.ValidateDockerImageName("myapp")
✅ SecurityValidation.ValidateDockerImageName("registry.io/namespace/myapp")
✅ SecurityValidation.ValidateDockerImageName("my-app_v1")
❌ SecurityValidation.ValidateDockerImageName("MYAPP")  // Uppercase
❌ SecurityValidation.ValidateDockerImageName("my..app")  // Double separator
❌ SecurityValidation.ValidateDockerImageName("my|app")  // Invalid character
```

```python
# Python Examples
✅ validate_docker_image_name("myapp")
✅ validate_docker_image_name("registry.io/namespace/myapp")
✅ validate_docker_image_name("my-app_v1")
❌ validate_docker_image_name("MYAPP")  # Uppercase
❌ validate_docker_image_name("my..app")  # Double separator
```

#### `ValidateDockerTag` / `validate_docker_tag`

**Purpose**: Validate Docker tags.

**When to Use**:
- Before tagging images
- When accepting version numbers from users
- In CI/CD pipelines

**Valid Format**:
- Alphanumeric characters
- Separators: `_`, `.`, `-`
- Length: 1-128 characters

**Examples**:
```csharp
✅ SecurityValidation.ValidateDockerTag("latest")
✅ SecurityValidation.ValidateDockerTag("v1.0.0")
✅ SecurityValidation.ValidateDockerTag("sha-abc123")
❌ SecurityValidation.ValidateDockerTag("invalid tag")  // Space
```

### File System Validation

#### `ValidateFilePath` / `validate_file_path`

**Purpose**: Prevent path traversal attacks and ensure files stay within allowed directories.

**When to Use**:
- Before any file system operation
- When accepting file paths from users
- In file upload handlers
- In configuration file processors

**What It Checks**:
1. Path traversal sequences (`..`, `/.`, etc.)
2. Null byte injection
3. URL-encoded traversal attempts
4. Resolves to location within base directory

**Examples**:
```csharp
// C# Example
string baseDir = "/var/spacedev/xfer/myapp";
string userPath = "/var/spacedev/xfer/myapp/data/file.txt";

var result = SecurityValidation.ValidateFilePath(userPath, baseDir);
if (!result.IsValid)
{
    _logger.LogError("Invalid path: {Error}", result.ErrorMessage);
    throw new SecurityException(result.ErrorMessage);
}
```

```python
# Python Example
base_dir = "/var/spacedev/xfer/myapp"
user_path = "/var/spacedev/xfer/myapp/data/file.txt"

if not validate_file_path(user_path, base_dir):
    raise ValueError("Path is outside allowed directory")
```

**Attack Examples (All Rejected)**:
```
❌ "../../../etc/passwd"
❌ "/./../etc/passwd"
❌ "%2e%2e/passwd"  // URL encoded
❌ "file.txt\0.exe"  // Null byte injection
```

#### `ValidateFilename` / `validate_filename`

**Purpose**: Validate file names (without paths) for safe characters.

**When to Use**:
- File upload forms
- Saving user-generated files
- Creating log files with user input in names

**Valid Format**:
- Alphanumeric characters
- Separators: `_`, `.`, `-`
- Maximum 255 characters
- Not a Windows reserved name (CON, PRN, etc.)
- No path separators

**Examples**:
```csharp
✅ SecurityValidation.ValidateFilename("config.json")
✅ SecurityValidation.ValidateFilename("data_file-v1.txt")
❌ SecurityValidation.ValidateFilename("../etc/passwd")
❌ SecurityValidation.ValidateFilename("CON")  // Windows reserved
❌ SecurityValidation.ValidateFilename("file|name.txt")
```

#### `IsPathWithinDirectory` / `is_within_directory`

**Purpose**: Check if a resolved path stays within a base directory.

**When to Use**:
- As a final check before file operations
- To verify symbolic links don't escape boundaries
- In file serving applications

**Example**:
```csharp
string baseDir = "/var/spacedev/xfer/myapp";
string userPath = GetUserInput();

if (!SecurityValidation.IsPathWithinDirectory(userPath, baseDir))
{
    throw new UnauthorizedAccessException("Access denied");
}

// Safe to proceed with file operation
File.ReadAllText(userPath);
```

### Kubernetes Validation

#### `ValidateKubernetesNamespace` / `validate_kubernetes_namespace`

**Purpose**: Validate Kubernetes namespace names.

**When to Use**:
- Before creating namespaces
- In deployment automation
- When accepting namespace names from configuration

**Valid Format**:
- Lowercase alphanumeric or hyphens
- Cannot start or end with hyphen
- Maximum 63 characters

**Examples**:
```csharp
✅ SecurityValidation.ValidateKubernetesNamespace("default")
✅ SecurityValidation.ValidateKubernetesNamespace("my-namespace")
✅ SecurityValidation.ValidateKubernetesNamespace("app123")
❌ SecurityValidation.ValidateKubernetesNamespace("INVALID")
❌ SecurityValidation.ValidateKubernetesNamespace("-invalid")
```

#### `ValidateKubernetesResourceName` / `validate_kubernetes_resource_name`

**Purpose**: Validate Kubernetes resource names (pods, services, etc.).

**When to Use**:
- Creating any Kubernetes resource
- Validating deployment configurations
- In Helm templates

**Valid Format**:
- Lowercase alphanumeric, hyphens, or dots
- Cannot start or end with hyphen or dot
- Maximum 253 characters

### Helm Validation

#### `ValidateHelmParameter` / `validate_helm_parameter`

**Purpose**: Validate Helm parameter names.

**When to Use**:
- Processing Helm values
- Building Helm commands
- Configuration management

**Valid Format**:
- Alphanumeric, dots, underscores, hyphens
- Maximum 255 characters

**Examples**:
```csharp
✅ SecurityValidation.ValidateHelmParameter("app.replicas")
✅ SecurityValidation.ValidateHelmParameter("config_name")
❌ SecurityValidation.ValidateHelmParameter("invalid param")
```

#### `ValidateHelmValue` / `validate_helm_value`

**Purpose**: Validate Helm values.

**Valid Format**:
- Alphanumeric and safe separators: `.`, `_`, `:`, `-`, `/`
- Maximum 1024 characters
- Supports URLs and paths

### Shell Security

#### `ContainsShellMetacharacters` / `contains_shell_metacharacters`

**Purpose**: Detect shell metacharacters that could enable command injection.

**When to Use**:
- **ALWAYS** before passing user input to shell commands
- Before using `Process.Start` with shell execution
- In any context where input might reach a shell

**Detected Characters**:
```
| & ; < > ( ) $ ` \ " ' \n \r \t * ? [ ] { } ! # ~
```

**Example**:
```csharp
string userInput = GetUserInput();

if (SecurityValidation.ContainsShellMetacharacters(userInput))
{
    throw new SecurityException("Input contains dangerous characters");
}

// BETTER: Use parameterized APIs instead of shell
// Instead of: Process.Start("sh", $"-c 'cat {userInput}'")
// Do: File.ReadAllText(userInput)
```

**CRITICAL**: Detection alone is not sufficient. See [Security Best Practices](#security-best-practices).

#### `SanitizeShellArgument` / `sanitize_shell_argument`

**Purpose**: Escape dangerous characters for shell execution.

**When to Use**:
- **ONLY as defense-in-depth** after validation
- When shell execution is unavoidable
- Never as the sole protection

**Example**:
```csharp
// WRONG: Relying only on sanitization
string userFile = GetUserInput();
string command = $"cat {userFile}";  // VULNERABLE!

// BETTER: Validate first, then sanitize
string userFile = GetUserInput();
SecurityValidation.ValidateFilename(userFile).ThrowIfInvalid("filename");
string safeFile = SecurityValidation.SanitizeShellArgument(userFile);
// Still prefer parameterized APIs!

// BEST: Avoid shell entirely
string content = File.ReadAllText(userFile);
```

### General Validation

#### `ValidateIdentifier` / `validate_identifier`

**Purpose**: Validate programming identifiers (variable names, function names).

**When to Use**:
- Code generation
- Dynamic variable creation
- API parameter names

**Valid Format**:
- Starts with letter or underscore
- Contains only letters, numbers, underscores
- Maximum 255 characters

**Examples**:
```csharp
✅ SecurityValidation.ValidateIdentifier("myVariable")
✅ SecurityValidation.ValidateIdentifier("_internal")
✅ SecurityValidation.ValidateIdentifier("value123")
❌ SecurityValidation.ValidateIdentifier("123invalid")
❌ SecurityValidation.ValidateIdentifier("my-var")
```

#### `SanitizeInput` / `sanitize_input`

**Purpose**: Remove all characters not in an allowed set.

**When to Use**:
- Creating safe slugs from user input
- Filtering output for specific contexts
- Generating safe filenames from titles

**Example**:
```csharp
// C#
string title = "My File (Version 2.0)!";
string safeFilename = SecurityValidation.SanitizeInput(
    title,
    ValidationConstants.ALPHANUMERIC_WITH_SEPARATORS
) + ".txt";
// Result: "MyFileVersion2.0.txt"
```

```python
# Python
from spacefx.security import sanitize_input, ALPHANUMERIC_CHARS

title = "My File (Version 2.0)!"
safe_filename = sanitize_input(title, ALPHANUMERIC_CHARS) + ".txt"
# Result: "MyFileVersion20.txt"
```

## Common Use Cases

### Use Case 1: Processing Deployment Configuration

```csharp
public class DeploymentValidator
{
    public void ValidateDeploymentConfig(DeploymentConfig config)
    {
        // Validate image name
        var imageResult = SecurityValidation.ValidateDockerImageName(config.ImageName);
        imageResult.ThrowIfInvalid(nameof(config.ImageName));

        // Validate tag
        var tagResult = SecurityValidation.ValidateDockerTag(config.ImageTag);
        tagResult.ThrowIfInvalid(nameof(config.ImageTag));

        // Validate namespace
        var nsResult = SecurityValidation.ValidateKubernetesNamespace(config.Namespace);
        nsResult.ThrowIfInvalid(nameof(config.Namespace));

        // Validate all Helm parameters
        foreach (var param in config.HelmParameters)
        {
            SecurityValidation.ValidateHelmParameter(param.Key).ThrowIfInvalid("parameter");
            SecurityValidation.ValidateHelmValue(param.Value).ThrowIfInvalid("value");
        }
    }
}
```

### Use Case 2: File Upload Handler

```csharp
public class FileUploadHandler
{
    private readonly string _uploadBasePath = "/var/spacedev/xfer/uploads";

    public async Task<string> HandleUpload(string filename, Stream content)
    {
        // Validate filename
        var filenameResult = SecurityValidation.ValidateFilename(filename);
        if (!filenameResult.IsValid)
        {
            throw new ArgumentException($"Invalid filename: {filenameResult.ErrorMessage}");
        }

        // Construct full path
        string fullPath = Path.Combine(_uploadBasePath, filename);

        // Verify path is within base directory
        if (!SecurityValidation.IsPathWithinDirectory(fullPath, _uploadBasePath))
        {
            throw new SecurityException("Path traversal attempt detected");
        }

        // Additional validation
        var pathResult = SecurityValidation.ValidateFilePath(fullPath, _uploadBasePath);
        pathResult.ThrowIfInvalid(nameof(fullPath));

        // Safe to proceed
        using var fileStream = File.Create(fullPath);
        await content.CopyToAsync(fileStream);

        return fullPath;
    }
}
```

### Use Case 3: Building Container Commands

```python
from spacefx.security import (
    validate_docker_image_name,
    validate_docker_tag,
    contains_shell_metacharacters
)
import subprocess

def pull_docker_image(image_name: str, tag: str) -> None:
    """
    Safely pull a Docker image.

    Args:
        image_name: The image name to pull
        tag: The image tag

    Raises:
        ValueError: If inputs are invalid
    """
    # Validate inputs
    if not validate_docker_image_name(image_name):
        raise ValueError(f"Invalid image name: {image_name}")

    if not validate_docker_tag(tag):
        raise ValueError(f"Invalid tag: {tag}")

    # Additional safety check
    full_image = f"{image_name}:{tag}"
    if contains_shell_metacharacters(full_image):
        raise ValueError("Image reference contains dangerous characters")

    # Use parameterized subprocess (no shell=True)
    subprocess.run(
        ["docker", "pull", full_image],
        check=True,
        capture_output=True
    )
```

### Use Case 4: Extension Method Pattern

```csharp
public class ApplicationService
{
    public void DeployApplication(string imageName, string tag, string namespace)
    {
        // Use extension methods for fluent validation
        if (!imageName.IsValidDockerImageName())
            throw new ArgumentException("Invalid image name", nameof(imageName));

        if (!tag.IsValidDockerTag())
            throw new ArgumentException("Invalid tag", nameof(tag));

        if (!namespace.IsValidKubernetesNamespace())
            throw new ArgumentException("Invalid namespace", nameof(namespace));

        // Check for injection attempts
        if (imageName.ContainsShellMetacharacters() ||
            tag.ContainsShellMetacharacters())
        {
            throw new SecurityException("Input contains dangerous characters");
        }

        // Proceed with deployment
        DeployToCluster(imageName, tag, namespace);
    }
}
```

## Security Best Practices

### 1. Always Validate Before Use

```csharp
// ❌ WRONG: Using user input directly
string imageName = GetUserInput();
Process.Start("docker", $"pull {imageName}");

// ✅ CORRECT: Validate first
string imageName = GetUserInput();
SecurityValidation.ValidateDockerImageName(imageName).ThrowIfInvalid("imageName");
Process.Start("docker", new[] { "pull", imageName });
```

### 2. Prefer Parameterized APIs

```csharp
// ❌ WRONG: Using shell with string concatenation
Process.Start("/bin/sh", $"-c 'docker pull {imageName}'");

// ✅ CORRECT: Direct API call without shell
Process.Start("docker", new[] { "pull", imageName });
```

```python
# ❌ WRONG: shell=True with string formatting
subprocess.run(f"docker pull {image_name}", shell=True)

# ✅ CORRECT: List arguments, no shell
subprocess.run(["docker", "pull", image_name])
```

### 3. Layer Your Defenses

```csharp
public void ProcessFile(string userPath)
{
    // Layer 1: Filename validation
    string filename = Path.GetFileName(userPath);
    SecurityValidation.ValidateFilename(filename).ThrowIfInvalid("filename");

    // Layer 2: Full path validation
    string basePath = "/var/spacedev/xfer";
    SecurityValidation.ValidateFilePath(userPath, basePath).ThrowIfInvalid("path");

    // Layer 3: Directory boundary check
    if (!SecurityValidation.IsPathWithinDirectory(userPath, basePath))
        throw new SecurityException("Path outside allowed directory");

    // Layer 4: File system permissions
    var fileInfo = new FileInfo(userPath);
    if (!fileInfo.Exists)
        throw new FileNotFoundException();

    // Now safe to proceed
    var content = File.ReadAllText(userPath);
}
```

### 4. Validate Configuration at Startup

```csharp
public class AppConfiguration
{
    public string ImageRegistry { get; set; }
    public string Namespace { get; set; }

    public void Validate()
    {
        SecurityValidation.ValidateDockerImageName(ImageRegistry)
            .ThrowIfInvalid(nameof(ImageRegistry));

        SecurityValidation.ValidateKubernetesNamespace(Namespace)
            .ThrowIfInvalid(nameof(Namespace));
    }
}

// At startup
var config = LoadConfiguration();
config.Validate();  // Fail fast if config is invalid
```

### 5. Log Validation Failures

```csharp
public void ValidateInput(string input, string context)
{
    var result = SecurityValidation.ValidateDockerImageName(input);
    if (!result.IsValid)
    {
        _logger.LogWarning(
            "Validation failed for {Context}: {Error}. Input: {Input}",
            context,
            result.ErrorMessage,
            input.Substring(0, Math.Min(50, input.Length))  // Log truncated input
        );
        throw new ArgumentException(result.ErrorMessage);
    }
}
```

### 6. Never Trust, Always Verify

```csharp
// ❌ WRONG: Trusting internal sources
string configFile = internalService.GetConfigPath();
var content = File.ReadAllText(configFile);  // VULNERABLE!

// ✅ CORRECT: Validate all inputs, regardless of source
string configFile = internalService.GetConfigPath();
SecurityValidation.ValidateFilePath(configFile, _basePath).ThrowIfInvalid("configFile");
var content = File.ReadAllText(configFile);
```

## Common Pitfalls

### Pitfall 1: Sanitization as Primary Defense

```csharp
// ❌ WRONG: Only sanitizing
string userInput = GetUserInput();
string sanitized = SecurityValidation.SanitizeShellArgument(userInput);
Process.Start("sh", $"-c 'cat {sanitized}'");

// ✅ CORRECT: Validate, then avoid shell
string userInput = GetUserInput();
SecurityValidation.ValidateFilename(userInput).ThrowIfInvalid("filename");
string content = File.ReadAllText(userInput);
```

**Why**: Sanitization can be bypassed. Always validate against a whitelist first.

### Pitfall 2: Partial Path Validation

```csharp
// ❌ WRONG: Only checking filename
string filename = GetUserInput();
if (SecurityValidation.ValidateFilename(filename).IsValid)
{
    string path = $"/data/{filename}";
    File.ReadAllText(path);  // Still vulnerable!
}

// ✅ CORRECT: Validate full path
string filename = GetUserInput();
string path = Path.Combine("/data", filename);
SecurityValidation.ValidateFilePath(path, "/data").ThrowIfInvalid("path");
File.ReadAllText(path);
```

### Pitfall 3: Validating After Construction

```csharp
// ❌ WRONG: Building path before validation
string userInput = GetUserInput();
string path = $"/data/{userInput}/../../etc/passwd";
SecurityValidation.ValidateFilePath(path, "/data");  // Too late!

// ✅ CORRECT: Validate input, then construct
string userInput = GetUserInput();
SecurityValidation.ValidateFilename(userInput).ThrowIfInvalid("input");
string path = Path.Combine("/data", userInput);
```

### Pitfall 4: Case Sensitivity Issues

```csharp
// ❌ WRONG: Case-insensitive comparison
if (imageName.ToLower() == "myapp")  // VULNERABLE on case-insensitive filesystems

// ✅ CORRECT: Use validation that enforces format
SecurityValidation.ValidateDockerImageName(imageName).ThrowIfInvalid("imageName");
```

### Pitfall 5: Ignoring URL Encoding

```csharp
// ❌ WRONG: Not checking URL-encoded traversal
string path = "%2e%2e/passwd";
if (!path.Contains(".."))  // False sense of security!
{
    AccessFile(path);
}

// ✅ CORRECT: Use comprehensive validation
SecurityValidation.ValidateFilePath(path, baseDir).ThrowIfInvalid("path");
```

### Pitfall 6: Trusting File Extensions

```csharp
// ❌ WRONG: Only checking extension
if (filename.EndsWith(".txt"))
{
    // file.txt\0.exe bypasses this check
}

// ✅ CORRECT: Full filename validation
SecurityValidation.ValidateFilename(filename).ThrowIfInvalid("filename");
```

## Performance Considerations

### Compiled Regex Patterns

The validation library uses compiled regex patterns for optimal performance:

```csharp
// Patterns are compiled once and reused
private static readonly Regex DockerImageNameRegex = new(
    ValidationConstants.DOCKER_IMAGE_NAME_PATTERN,
    RegexOptions.Compiled | RegexOptions.CultureInvariant,
    TimeSpan.FromMilliseconds(100)  // Timeout protection
);
```

### Caching Validation Results

For frequently validated values:

```csharp
// Cache validation results for configuration
private readonly ConcurrentDictionary<string, bool> _validatedImages = new();

public bool IsValidImage(string imageName)
{
    return _validatedImages.GetOrAdd(imageName, name =>
        SecurityValidation.ValidateDockerImageName(name).IsValid
    );
}
```

### Batch Validation

```csharp
public ValidationResult ValidateMultiple(IEnumerable<string> imageNames)
{
    var errors = new List<string>();

    foreach (var imageName in imageNames)
    {
        var result = SecurityValidation.ValidateDockerImageName(imageName);
        if (!result.IsValid)
        {
            errors.Add($"{imageName}: {result.ErrorMessage}");
        }
    }

    return errors.Any()
        ? ValidationResult.Failure(string.Join("; ", errors))
        : ValidationResult.Success();
}
```

### Benchmarks

Typical validation performance (approximate):
- Docker image name: ~10-50 μs
- Docker tag: ~5-20 μs
- File path: ~50-200 μs (includes file system calls)
- Shell metacharacter check: ~5-10 μs
- Identifier: ~10-30 μs

Path validation is slower due to `Path.GetFullPath()` system calls.

## Integration Examples

### ASP.NET Core API Controller

```csharp
[ApiController]
[Route("api/[controller]")]
public class DeploymentController : ControllerBase
{
    [HttpPost]
    public IActionResult Deploy([FromBody] DeploymentRequest request)
    {
        // Validate all inputs
        var validations = new[]
        {
            SecurityValidation.ValidateDockerImageName(request.ImageName),
            SecurityValidation.ValidateDockerTag(request.Tag),
            SecurityValidation.ValidateKubernetesNamespace(request.Namespace)
        };

        var failures = validations.Where(v => !v.IsValid).ToList();
        if (failures.Any())
        {
            return BadRequest(new
            {
                Errors = failures.Select(f => f.ErrorMessage)
            });
        }

        // Proceed with deployment
        return Ok();
    }
}
```

### Python FastAPI

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from spacefx.security import validate_docker_image_name, validate_docker_tag

app = FastAPI()

class DeploymentRequest(BaseModel):
    image_name: str
    tag: str

    @validator('image_name')
    def validate_image(cls, v):
        if not validate_docker_image_name(v):
            raise ValueError('Invalid Docker image name')
        return v

    @validator('tag')
    def validate_tag(cls, v):
        if not validate_docker_tag(v):
            raise ValueError('Invalid Docker tag')
        return v

@app.post("/deploy")
async def deploy(request: DeploymentRequest):
    # Inputs are already validated by Pydantic
    return {"status": "success"}
```

### Helm Template Validation

```csharp
public class HelmValueValidator
{
    public void ValidateValues(Dictionary<string, string> values)
    {
        foreach (var (key, value) in values)
        {
            var keyResult = SecurityValidation.ValidateHelmParameter(key);
            if (!keyResult.IsValid)
            {
                throw new ArgumentException(
                    $"Invalid Helm parameter '{key}': {keyResult.ErrorMessage}"
                );
            }

            var valueResult = SecurityValidation.ValidateHelmValue(value);
            if (!valueResult.IsValid)
            {
                throw new ArgumentException(
                    $"Invalid Helm value for '{key}': {valueResult.ErrorMessage}"
                );
            }
        }
    }
}
```

### File Processing Pipeline

```python
from pathlib import Path
from spacefx.security import validate_file_path, validate_filename

class FileProcessor:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)

    def process_file(self, filename: str) -> dict:
        """
        Process a file with full validation.

        Args:
            filename: Name of file to process

        Returns:
            Processing results

        Raises:
            ValueError: If validation fails
        """
        # Validate filename
        if not validate_filename(filename):
            raise ValueError(f"Invalid filename: {filename}")

        # Construct and validate full path
        full_path = self.base_dir / filename
        if not validate_file_path(str(full_path), str(self.base_dir)):
            raise ValueError(f"Invalid or unsafe path: {full_path}")

        # Safe to proceed
        with open(full_path) as f:
            content = f.read()

        return {"filename": filename, "size": len(content)}
```

## Testing Your Validation

### Unit Test Template

```csharp
[Theory]
[InlineData("valid-input", true)]
[InlineData("invalid input", false)]
[InlineData("'; DROP TABLE users; --", false)]
public void TestValidation(string input, bool expectedValid)
{
    var result = SecurityValidation.ValidateDockerImageName(input);
    Assert.Equal(expectedValid, result.IsValid);
}
```

### Integration Test

```csharp
[Fact]
public void EndToEnd_DeploymentWithInvalidInput_ShouldReject()
{
    // Arrange
    var maliciousInput = "../../etc/passwd";

    // Act & Assert
    var exception = Assert.Throws<ArgumentException>(
        () => deploymentService.Deploy(maliciousInput)
    );

    Assert.Contains("traversal", exception.Message, StringComparison.OrdinalIgnoreCase);
}
```

## Additional Resources

- [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [OWASP Command Injection](https://owasp.org/www-community/attacks/Command_Injection)
- [CWE-22: Path Traversal](https://cwe.mitre.org/data/definitions/22.html)
- [CWE-78: OS Command Injection](https://cwe.mitre.org/data/definitions/78.html)

## Support

For issues or questions about input validation:
1. Check this documentation
2. Review the unit tests for examples
3. Examine the source code comments
4. Open an issue on GitHub

---

**Remember**: Input validation is not optional—it's a critical security control. When in doubt, validate!
