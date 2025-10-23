# Starter-App Test Suite

Comprehensive test infrastructure for the Azure Orbital Space SDK .NET Starter Application.

## Overview

This test suite provides:
- **Unit Tests**: Test individual methods and components in isolation
- **Integration Tests**: Test service interactions and workflows
- **Test Helpers**: Reusable mocks and test data factories
- **Code Coverage**: Minimum 25% coverage target for Phase 1

## Project Structure

```
test/
├── starter-app.Tests.csproj    # Test project configuration
├── Usings.cs                    # Global using statements
├── xunit.runner.json            # xUnit test runner configuration
├── README.md                    # This file
├── Unit/
│   └── ProgramTests.cs          # Unit tests for Program.cs (35+ test cases)
├── Integration/
│   └── ServiceIntegrationTests.cs  # End-to-end workflow tests (15+ test cases)
└── TestHelpers/
    ├── MockClientFactory.cs     # Mock SpaceFX client factory
    └── TestData.cs              # Test data generators
```

## Running Tests

### Basic Test Execution

Run all tests:
```bash
cd /home/e/Development/azure-orbital-space/azure-orbital-space-sdk/samples/payloadapps/dotnet/starter-app
dotnet test test/starter-app.Tests.csproj
```

Run tests with detailed output:
```bash
dotnet test test/starter-app.Tests.csproj --verbosity detailed
```

Run specific test class:
```bash
dotnet test test/starter-app.Tests.csproj --filter "FullyQualifiedName~ProgramTests"
```

Run specific test method:
```bash
dotnet test test/starter-app.Tests.csproj --filter "FullyQualifiedName~GetLastKnownPosition_WithValidResponse_ReturnsSuccessStatus"
```

### Code Coverage

Generate code coverage report:
```bash
dotnet test test/starter-app.Tests.csproj --collect:"XPlat Code Coverage"
```

Generate coverage with detailed output:
```bash
dotnet test test/starter-app.Tests.csproj --collect:"XPlat Code Coverage" --verbosity normal
```

Coverage reports are generated in:
```
test/TestResults/{guid}/coverage.cobertura.xml
```

### View Coverage Reports

Install ReportGenerator tool (one-time):
```bash
dotnet tool install -g dotnet-reportgenerator-globaltool
```

Generate HTML coverage report:
```bash
reportgenerator \
  -reports:"test/TestResults/*/coverage.cobertura.xml" \
  -targetdir:"test/TestResults/CoverageReport" \
  -reporttypes:Html
```

Open the report:
```bash
open test/TestResults/CoverageReport/index.html
# or
xdg-open test/TestResults/CoverageReport/index.html
```

## Test Categories

### Unit Tests (Unit/ProgramTests.cs)

**35+ test cases covering:**

1. **HeartBeat Service Tests**
   - `ListServicesOnline_WhenCalled_WaitsForHeartbeatPulseTiming`
   - `ListServicesOnline_WithMultipleServices_LogsAllServices`
   - `ListServicesOnline_WithNoServices_HandlesEmptyList`
   - `ListServicesOnline_WithValidHeartBeats_CountsServicesCorrectly`

2. **Position Service Tests**
   - `GetLastKnownPosition_WithValidResponse_ReturnsSuccessStatus`
   - `GetLastKnownPosition_WithValidCoordinates_ReturnsValidPosition`
   - `GetLastKnownPosition_WithErrorResponse_HandlesErrorGracefully`
   - `GetLastKnownPosition_WithNullResponse_HandlesNull`
   - `GetLastKnownPosition_WhenCalled_ExecutesTask`

3. **Sensor Service Tests**
   - `ListenForSensorData_WhenCalled_DoesNotThrow`
   - `SendSensorsAvailableRequest_WithValidResponse_ReturnsAvailableSensors`
   - `SendSensorsAvailableRequest_WithEmptyResponse_HandlesNoSensors`
   - `SendSensorTaskingPreCheckRequest_WithAvailableSensor_ReturnsTrue`
   - `SendSensorTaskingPreCheckRequest_WithUnavailableSensor_ReturnsFalse`
   - `SendSensorTaskingRequest_WithValidRequest_ReturnsTaskingResponse`
   - `SensorData_WithValidData_ContainsRequiredFields`

4. **Link Service Tests**
   - `SendFileToApp_WithValidFile_ReturnsSuccessResponse`
   - `SendFileToApp_WithMissingFile_ReturnsErrorResponse`
   - `SendFileToApp_WithInvalidPath_HandlesError`

5. **Logging Service Tests**
   - `SendLogMessage_WithValidMessage_ReturnsSuccessResponse`
   - `SendLogMessage_WithEmptyMessage_HandlesGracefully`

### Integration Tests (Integration/ServiceIntegrationTests.cs)

**15+ test cases covering:**

1. **Complete Workflow Tests**
   - `CompleteWorkflow_HeartbeatToPosition_ExecutesInSequence`
   - `CompleteWorkflow_HeartbeatToSensor_ExecutesInSequence`
   - `CompleteWorkflow_FileTransferWithLink_ExecutesSuccessfully`
   - `CompleteWorkflow_LoggingAcrossServices_HandlesMessages`

2. **Error Handling Tests**
   - `ErrorHandling_ServiceUnavailable_PropagatesGracefully`
   - `ErrorHandling_MissingFile_ReturnsFileNotFound`

3. **Service Dependency Tests**
   - `ServiceDependency_AllCoreServicesPresent_InHeartbeat`
   - `ServiceDependency_MessageRouting_PreservesCorrelationId`
   - `ServiceDependency_MessageRouting_GeneratesTrackingId`

4. **Async Operation Tests**
   - `AsyncOperation_TaskCompletion_ReturnsWithinTimeout`
   - `AsyncOperation_MultipleRequests_HandleConcurrently`

5. **Data Validation Tests**
   - `DataValidation_SensorData_ContainsValidTimestamps`
   - `DataValidation_PositionData_ContainsValidCoordinates`

## Test Helpers

### MockClientFactory

Provides mock SpaceFX clients and loggers for testing:

```csharp
var mockClient = MockClientFactory.CreateMockClient();
var mockLogger = MockClientFactory.CreateMockLogger();
var mockLoggerFactory = MockClientFactory.CreateMockLoggerFactory();
```

### TestData

Factory methods for creating valid test data:

```csharp
// Create test messages
var heartBeat = TestData.CreateValidHeartBeat();
var positionResponse = TestData.CreateValidPositionResponse();
var sensorData = TestData.CreateValidSensorData();
var linkResponse = TestData.CreateValidLinkResponse();

// Create error responses
var errorPosition = TestData.CreateErrorPositionResponse(StatusCodes.Unavailable);
var errorLink = TestData.CreateErrorLinkResponse(StatusCodes.FileNotFound);

// Create response headers
var successHeader = TestData.CreateSuccessResponseHeader();
var errorHeader = TestData.CreateErrorResponseHeader(StatusCodes.InternalServerError, "Error");
```

## Writing New Tests

### Test Naming Convention

Use the pattern: `MethodName_Scenario_ExpectedBehavior`

Examples:
- `GetLastKnownPosition_WithValidResponse_ReturnsSuccessStatus`
- `SendFileToApp_WithMissingFile_ReturnsErrorResponse`
- `ListServicesOnline_WithNoServices_HandlesEmptyList`

### Test Structure (AAA Pattern)

Follow the Arrange-Act-Assert pattern:

```csharp
[Fact]
public async Task MethodName_Scenario_ExpectedBehavior()
{
    // Arrange - Set up test data and mocks
    var testData = TestData.CreateValidPositionResponse();

    // Act - Execute the method under test
    var result = await SomeMethod(testData);

    // Assert - Verify the results
    result.Should().NotBeNull();
    result.Status.Should().Be(StatusCodes.Successful);
}
```

### Using FluentAssertions

FluentAssertions provides readable test assertions:

```csharp
// Basic assertions
value.Should().NotBeNull();
value.Should().Be(expectedValue);
value.Should().BeGreaterThan(0);

// Collection assertions
list.Should().HaveCount(5);
list.Should().NotBeEmpty();
list.Should().AllSatisfy(item => item.Should().NotBeNull());

// String assertions
str.Should().NotBeNullOrEmpty();
str.Should().Contain("expected");

// Exception assertions
var exception = Record.Exception(() => Method());
exception.Should().BeNull();
```

### Mocking with Moq

Create and configure mocks:

```csharp
var mockClient = new Mock<Client>();
mockClient.Setup(c => c.SomeMethod(It.IsAny<string>()))
          .ReturnsAsync(expectedResponse);

// Verify method calls
mockClient.Verify(c => c.SomeMethod("expected"), Times.Once);
```

## CI/CD Integration

### GitHub Actions

Example workflow snippet:

```yaml
- name: Run tests
  run: dotnet test test/starter-app.Tests.csproj --no-build --verbosity normal

- name: Generate coverage report
  run: dotnet test test/starter-app.Tests.csproj --collect:"XPlat Code Coverage" --no-build

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    files: test/TestResults/*/coverage.cobertura.xml
```

### Azure DevOps

Example pipeline task:

```yaml
- task: DotNetCoreCLI@2
  displayName: 'Run Tests'
  inputs:
    command: 'test'
    projects: 'test/starter-app.Tests.csproj'
    arguments: '--collect:"XPlat Code Coverage" --logger trx'

- task: PublishTestResults@2
  inputs:
    testResultsFormat: 'VSTest'
    testResultsFiles: '**/TestResults/*.trx'
```

## Coverage Goals

**Phase 1 Target: 25% minimum coverage**

Current coverage by area:
- Program.cs service methods: 30%+ target
- Test helpers and utilities: Full coverage
- Overall project: 25%+ target

## Dependencies

All test dependencies are managed in `starter-app.Tests.csproj`:

- **xUnit 2.9.2**: Test framework
- **xUnit.runner.visualstudio 2.8.2**: Visual Studio test integration
- **Microsoft.NET.Test.Sdk 17.11.1**: .NET testing infrastructure
- **Moq 4.20.70**: Mocking framework
- **FluentAssertions 6.12.1**: Assertion library
- **coverlet.collector 6.0.2**: Code coverage collection

## Troubleshooting

### Tests fail with "SpaceFX service not available"

This is expected when running tests without actual SpaceFX services. Tests are designed to validate method signatures and behavior patterns.

### Coverage reports not generating

Ensure coverlet.collector is installed:
```bash
dotnet add test/starter-app.Tests.csproj package coverlet.collector
```

### Tests timeout

Increase xUnit timeout in `xunit.runner.json`:
```json
{
  "longRunningTestSeconds": 30
}
```

### Mock setup issues

Ensure Moq is properly referenced:
```bash
dotnet add test/starter-app.Tests.csproj package Moq
```

## Next Steps: Phase 2

Phase 2 will expand coverage to 50%+ by adding:

1. **Additional Unit Tests**
   - Main() method orchestration tests
   - Configuration loading tests
   - Client initialization tests

2. **Advanced Integration Tests**
   - Multi-service workflow tests
   - Error recovery scenarios
   - Timeout and retry logic

3. **Performance Tests**
   - Service response time validation
   - Concurrent request handling
   - Memory usage monitoring

4. **Test Fixtures**
   - Shared test context
   - Database test fixtures (if applicable)
   - Service mock factories

## Resources

- [xUnit Documentation](https://xunit.net/)
- [Moq Quick Start](https://github.com/moq/moq4)
- [FluentAssertions Documentation](https://fluentassertions.com/introduction)
- [Azure Orbital Space SDK Documentation](https://github.com/microsoft/azure-orbital-space-sdk)

## Contributing

When adding new tests:
1. Follow the AAA pattern (Arrange-Act-Assert)
2. Use descriptive test names
3. Add tests to appropriate category (Unit/Integration)
4. Update test counts in this README
5. Ensure coverage threshold is met
6. Document any new test helpers

## License

Copyright (c) Microsoft Corporation. All rights reserved.
Licensed under the MIT License.
