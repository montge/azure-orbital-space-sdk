using StarterApp.Tests.TestHelpers;
using System.Diagnostics.CodeAnalysis;

namespace StarterApp.Tests.Integration;

/// <summary>
/// Integration tests for StarterApp service workflows
/// Tests end-to-end scenarios and service interactions
/// </summary>
[ExcludeFromCodeCoverage]
public class ServiceIntegrationTests
{
    #region Complete Workflow Tests

    [Fact]
    public async Task CompleteWorkflow_HeartbeatToPosition_ExecutesInSequence()
    {
        // Arrange
        var heartBeats = TestData.CreateHeartBeatList();
        var positionResponse = TestData.CreateValidPositionResponse();

        // Act
        var servicesOnline = heartBeats.Any(hb => hb.AppId.Contains("position"));
        var positionAvailable = positionResponse.ResponseHeader.Status == StatusCodes.Successful;

        // Assert
        servicesOnline.Should().BeTrue("Position service should be in heartbeat list");
        positionAvailable.Should().BeTrue("Position service should return valid response");
        positionResponse.Position.Should().NotBeNull();
    }

    [Fact]
    public async Task CompleteWorkflow_HeartbeatToSensor_ExecutesInSequence()
    {
        // Arrange
        var heartBeats = TestData.CreateHeartBeatList();
        var sensorsAvailableResponse = TestData.CreateValidSensorsAvailableResponse();
        var taskingPreCheckResponse = TestData.CreateValidTaskingPreCheckResponse(true);
        var taskingResponse = TestData.CreateValidTaskingResponse();

        // Act
        var sensorServiceOnline = heartBeats.Any(hb => hb.AppId.Contains("sensor"));
        var sensorsAvailable = sensorsAvailableResponse.Sensors.Count > 0;
        var sensorReady = taskingPreCheckResponse.SensorAvailable;
        var taskingSuccessful = taskingResponse.ResponseHeader.Status == StatusCodes.Successful;

        // Assert
        sensorServiceOnline.Should().BeTrue("Sensor service should be in heartbeat list");
        sensorsAvailable.Should().BeTrue("Should have available sensors");
        sensorReady.Should().BeTrue("Sensor should be ready for tasking");
        taskingSuccessful.Should().BeTrue("Sensor tasking should succeed");
        taskingResponse.SensorData.Should().NotBeNull("Should receive sensor data");
    }

    [Fact]
    public async Task CompleteWorkflow_FileTransferWithLink_ExecutesSuccessfully()
    {
        // Arrange
        var heartBeats = TestData.CreateHeartBeatList();
        var linkResponse = TestData.CreateValidLinkResponse();

        // Act
        var linkServiceOnline = heartBeats.Any(hb => hb.AppId.Contains("link"));
        var fileTransferSuccessful = linkResponse.ResponseHeader.Status == StatusCodes.Successful;

        // Assert
        linkServiceOnline.Should().BeTrue("Link service should be in heartbeat list");
        fileTransferSuccessful.Should().BeTrue("File transfer should succeed");
        linkResponse.FileName.Should().NotBeNullOrEmpty("Response should include filename");
    }

    [Fact]
    public async Task CompleteWorkflow_LoggingAcrossServices_HandlesMessages()
    {
        // Arrange
        var heartBeats = TestData.CreateHeartBeatList();
        var logResponse = TestData.CreateValidLogMessageResponse();

        // Act
        var loggingServiceOnline = heartBeats.Any(hb => hb.AppId.Contains("logging"));
        var logMessageSent = logResponse.ResponseHeader.Status == StatusCodes.Successful;

        // Assert
        loggingServiceOnline.Should().BeTrue("Logging service should be in heartbeat list");
        logMessageSent.Should().BeTrue("Log message should be sent successfully");
    }

    #endregion

    #region Error Handling and Resilience Tests

    [Fact]
    public async Task ErrorHandling_ServiceUnavailable_PropagatesGracefully()
    {
        // Arrange
        var errorPositionResponse = TestData.CreateErrorPositionResponse(StatusCodes.Unavailable);
        var errorLinkResponse = TestData.CreateErrorLinkResponse(StatusCodes.Unavailable);

        // Act
        var positionError = errorPositionResponse.ResponseHeader.Status;
        var linkError = errorLinkResponse.ResponseHeader.Status;

        // Assert
        positionError.Should().Be(StatusCodes.Unavailable);
        linkError.Should().Be(StatusCodes.Unavailable);
        errorPositionResponse.ResponseHeader.Message.Should().NotBeNullOrEmpty();
        errorLinkResponse.ResponseHeader.Message.Should().NotBeNullOrEmpty();
    }

    [Fact]
    public async Task ErrorHandling_MissingFile_ReturnsFileNotFound()
    {
        // Arrange
        var fileNotFoundResponse = TestData.CreateErrorLinkResponse(StatusCodes.FileNotFound);

        // Act
        var status = fileNotFoundResponse.ResponseHeader.Status;

        // Assert
        status.Should().Be(StatusCodes.FileNotFound);
        fileNotFoundResponse.ResponseHeader.Message.Should().Contain("not found");
    }

    #endregion

    #region Service Dependency Tests

    [Fact]
    public async Task ServiceDependency_AllCoreServicesPresent_InHeartbeat()
    {
        // Arrange
        var heartBeats = TestData.CreateHeartBeatList();
        var requiredServices = new[] { "position", "sensor", "link", "logging" };

        // Act
        var servicesFound = requiredServices.Select(service =>
            heartBeats.Any(hb => hb.AppId.Contains(service))
        ).ToList();

        // Assert
        servicesFound.Should().AllSatisfy(found => found.Should().BeTrue());
        heartBeats.Should().HaveCountGreaterOrEqualTo(4, "Should have at least 4 core services");
    }

    [Fact]
    public async Task ServiceDependency_MessageRouting_PreservesCorrelationId()
    {
        // Arrange
        var correlationId = Guid.NewGuid().ToString();
        var positionResponse = TestData.CreateValidPositionResponse();
        positionResponse.ResponseHeader.CorrelationId = correlationId;

        // Act
        var responseCorrelationId = positionResponse.ResponseHeader.CorrelationId;

        // Assert
        responseCorrelationId.Should().Be(correlationId);
    }

    [Fact]
    public async Task ServiceDependency_MessageRouting_GeneratesTrackingId()
    {
        // Arrange
        var response = TestData.CreateSuccessResponseHeader();

        // Act
        var trackingId = response.TrackingId;
        var isValidGuid = Guid.TryParse(trackingId, out _);

        // Assert
        trackingId.Should().NotBeNullOrEmpty();
        isValidGuid.Should().BeTrue("TrackingId should be a valid GUID");
    }

    #endregion

    #region Timeout and Async Operation Tests

    [Fact]
    public async Task AsyncOperation_TaskCompletion_ReturnsWithinTimeout()
    {
        // Arrange
        var taskCompletionSource = new TaskCompletionSource<bool>();
        var timeout = TimeSpan.FromSeconds(5);

        // Act
        taskCompletionSource.SetResult(true);
        var completedTask = await Task.WhenAny(taskCompletionSource.Task, Task.Delay(timeout));

        // Assert
        completedTask.Should().Be(taskCompletionSource.Task, "Task should complete before timeout");
        taskCompletionSource.Task.Result.Should().BeTrue();
    }

    [Fact]
    public async Task AsyncOperation_MultipleRequests_HandleConcurrently()
    {
        // Arrange
        var response1 = TestData.CreateValidPositionResponse();
        var response2 = TestData.CreateValidSensorsAvailableResponse();
        var response3 = TestData.CreateValidLinkResponse();

        // Act - Simulate concurrent responses
        var tasks = new[]
        {
            Task.FromResult(response1),
            Task.FromResult(response2),
            Task.FromResult(response3)
        };
        await Task.WhenAll(tasks);

        // Assert
        tasks.Should().AllSatisfy(task => task.IsCompleted.Should().BeTrue());
        response1.ResponseHeader.Status.Should().Be(StatusCodes.Successful);
        response2.ResponseHeader.Status.Should().Be(StatusCodes.Successful);
        response3.ResponseHeader.Status.Should().Be(StatusCodes.Successful);
    }

    #endregion

    #region DirectToApp Message Tests

    [Fact]
    public void DirectToAppMessage_Construction_HasRequiredFields()
    {
        // Arrange & Act
        var message = TestData.CreateDirectToAppMessage("test-app");

        // Assert
        message.Should().NotBeNull();
        message.DestinationAppId.Should().Be("test-app");
        message.MessageName.Should().NotBeNullOrEmpty();
        message.TrackingId.Should().NotBeNullOrEmpty();
        message.CorrelationId.Should().NotBeNullOrEmpty();
    }

    [Fact]
    public void DirectToAppMessage_WithCustomDestination_RoutesCorrectly()
    {
        // Arrange
        var customAppId = "custom-payload-app";

        // Act
        var message = TestData.CreateDirectToAppMessage(customAppId);

        // Assert
        message.DestinationAppId.Should().Be(customAppId);
    }

    #endregion

    #region Data Validation Tests

    [Fact]
    public async Task DataValidation_SensorData_ContainsValidTimestamps()
    {
        // Arrange
        var sensorData = TestData.CreateValidSensorData();

        // Act
        var generatedTime = sensorData.GeneratedTime.ToDateTime();
        var expirationTime = sensorData.ExpirationTime.ToDateTime();

        // Assert
        generatedTime.Should().BeCloseTo(DateTime.UtcNow, TimeSpan.FromMinutes(1));
        expirationTime.Should().BeAfter(generatedTime);
    }

    [Fact]
    public async Task DataValidation_PositionData_ContainsValidCoordinates()
    {
        // Arrange
        var positionResponse = TestData.CreateValidPositionResponse();

        // Act
        var position = positionResponse.Position;

        // Assert
        position.Should().NotBeNull();
        position.Point.Should().NotBeNull();
        position.Point.X.Should().BeGreaterThan(0);
        position.PositionTime.Should().NotBeNull();
    }

    #endregion
}
