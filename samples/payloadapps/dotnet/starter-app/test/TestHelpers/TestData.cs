using Google.Protobuf.WellKnownTypes;

namespace StarterApp.Tests.TestHelpers;

/// <summary>
/// Factory for creating test data objects with valid default values
/// </summary>
public static class TestData
{
    /// <summary>
    /// Creates a valid HeartBeatPulse for testing service discovery
    /// </summary>
    public static HeartBeatPulse CreateValidHeartBeat(string appId = "test-service")
    {
        return new HeartBeatPulse
        {
            AppId = appId,
            PulseDatetime = Timestamp.FromDateTime(DateTime.UtcNow)
        };
    }

    /// <summary>
    /// Creates a list of HeartBeatPulses simulating multiple services
    /// </summary>
    public static List<HeartBeatPulse> CreateHeartBeatList()
    {
        return new List<HeartBeatPulse>
        {
            CreateValidHeartBeat("hostsvc-position"),
            CreateValidHeartBeat("hostsvc-sensor"),
            CreateValidHeartBeat("hostsvc-link"),
            CreateValidHeartBeat("hostsvc-logging"),
            CreateValidHeartBeat("platformsvc-deployment")
        };
    }

    /// <summary>
    /// Creates a valid PositionResponse with sample coordinates
    /// </summary>
    public static PositionResponse CreateValidPositionResponse()
    {
        return new PositionResponse
        {
            ResponseHeader = CreateSuccessResponseHeader(),
            Position = new Position
            {
                PositionTime = Timestamp.FromDateTime(DateTime.UtcNow),
                Point = new Point
                {
                    X = 6378137.0,  // Earth radius at equator (meters)
                    Y = 0.0,
                    Z = 0.0
                }
            }
        };
    }

    /// <summary>
    /// Creates a PositionResponse with error status
    /// </summary>
    public static PositionResponse CreateErrorPositionResponse(StatusCodes statusCode = StatusCodes.Unavailable)
    {
        return new PositionResponse
        {
            ResponseHeader = CreateErrorResponseHeader(statusCode, "Position service unavailable")
        };
    }

    /// <summary>
    /// Creates a valid SensorData response
    /// </summary>
    public static SensorData CreateValidSensorData(string sensorId = "test-sensor")
    {
        return new SensorData
        {
            SensorID = sensorId,
            GeneratedTime = Timestamp.FromDateTime(DateTime.UtcNow),
            ExpirationTime = Timestamp.FromDateTime(DateTime.UtcNow.AddMinutes(10)),
            Data = Google.Protobuf.ByteString.CopyFromUtf8("test-sensor-data")
        };
    }

    /// <summary>
    /// Creates a valid SensorsAvailableResponse
    /// </summary>
    public static SensorsAvailableResponse CreateValidSensorsAvailableResponse()
    {
        var response = new SensorsAvailableResponse
        {
            ResponseHeader = CreateSuccessResponseHeader()
        };

        response.Sensors.Add(new SensorType
        {
            SensorID = "camera-1",
            SensorDescription = "Optical Camera"
        });

        response.Sensors.Add(new SensorType
        {
            SensorID = "thermal-1",
            SensorDescription = "Thermal Sensor"
        });

        return response;
    }

    /// <summary>
    /// Creates an empty SensorsAvailableResponse
    /// </summary>
    public static SensorsAvailableResponse CreateEmptySensorsAvailableResponse()
    {
        return new SensorsAvailableResponse
        {
            ResponseHeader = CreateSuccessResponseHeader()
        };
    }

    /// <summary>
    /// Creates a valid TaskingPreCheckResponse
    /// </summary>
    public static TaskingPreCheckResponse CreateValidTaskingPreCheckResponse(bool isAvailable = true)
    {
        return new TaskingPreCheckResponse
        {
            ResponseHeader = CreateSuccessResponseHeader(),
            SensorAvailable = isAvailable
        };
    }

    /// <summary>
    /// Creates a valid TaskingResponse
    /// </summary>
    public static TaskingResponse CreateValidTaskingResponse()
    {
        return new TaskingResponse
        {
            ResponseHeader = CreateSuccessResponseHeader(),
            SensorID = "test-sensor",
            SensorData = CreateValidSensorData()
        };
    }

    /// <summary>
    /// Creates a valid LinkResponse for file transfer operations
    /// </summary>
    public static LinkResponse CreateValidLinkResponse()
    {
        return new LinkResponse
        {
            ResponseHeader = CreateSuccessResponseHeader(),
            FileName = "/test/file.txt"
        };
    }

    /// <summary>
    /// Creates a LinkResponse with error status
    /// </summary>
    public static LinkResponse CreateErrorLinkResponse(StatusCodes statusCode = StatusCodes.FileNotFound)
    {
        return new LinkResponse
        {
            ResponseHeader = CreateErrorResponseHeader(statusCode, "File not found"),
            FileName = "/test/missing.txt"
        };
    }

    /// <summary>
    /// Creates a valid LogMessageResponse
    /// </summary>
    public static LogMessageResponse CreateValidLogMessageResponse()
    {
        return new LogMessageResponse
        {
            ResponseHeader = CreateSuccessResponseHeader()
        };
    }

    /// <summary>
    /// Creates a success ResponseHeader
    /// </summary>
    public static ResponseHeader CreateSuccessResponseHeader()
    {
        return new ResponseHeader
        {
            TrackingId = Guid.NewGuid().ToString(),
            CorrelationId = Guid.NewGuid().ToString(),
            Status = StatusCodes.Successful,
            Message = "Success"
        };
    }

    /// <summary>
    /// Creates an error ResponseHeader
    /// </summary>
    public static ResponseHeader CreateErrorResponseHeader(StatusCodes statusCode, string message)
    {
        return new ResponseHeader
        {
            TrackingId = Guid.NewGuid().ToString(),
            CorrelationId = Guid.NewGuid().ToString(),
            Status = statusCode,
            Message = message
        };
    }

    /// <summary>
    /// Creates a DirectToApp message envelope
    /// </summary>
    public static DirectToApp CreateDirectToAppMessage(string destinationAppId = "starter-app")
    {
        return new DirectToApp
        {
            DestinationAppId = destinationAppId,
            MessageName = "TestMessage",
            TrackingId = Guid.NewGuid().ToString(),
            CorrelationId = Guid.NewGuid().ToString()
        };
    }
}
