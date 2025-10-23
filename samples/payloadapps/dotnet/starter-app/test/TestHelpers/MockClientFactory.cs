using Microsoft.Azure.SpaceFx.SDK;

namespace StarterApp.Tests.TestHelpers;

public static class MockClientFactory
{
    /// <summary>
    /// Creates a mock SpaceFX client with default behavior
    /// </summary>
    public static Mock<Client> CreateMockClient()
    {
        var mockClient = new Mock<Client>();
        var mockLogger = CreateMockLogger();

        // Setup default logger behavior
        mockClient.Setup(c => c.Logger).Returns(mockLogger.Object);

        return mockClient;
    }

    /// <summary>
    /// Creates a mock logger with verification support
    /// </summary>
    public static Mock<ILogger> CreateMockLogger()
    {
        var mockLogger = new Mock<ILogger>();

        // Setup default logging behavior to accept any log call
        mockLogger.Setup(x => x.Log(
            It.IsAny<LogLevel>(),
            It.IsAny<EventId>(),
            It.IsAny<It.IsAnyType>(),
            It.IsAny<Exception>(),
            It.IsAny<Func<It.IsAnyType, Exception?, string>>()
        )).Verifiable();

        return mockLogger;
    }

    /// <summary>
    /// Creates a mock logger factory for dependency injection scenarios
    /// </summary>
    public static Mock<ILoggerFactory> CreateMockLoggerFactory()
    {
        var mockLoggerFactory = new Mock<ILoggerFactory>();
        var mockLogger = CreateMockLogger();

        mockLoggerFactory.Setup(f => f.CreateLogger(It.IsAny<string>()))
            .Returns(mockLogger.Object);

        return mockLoggerFactory;
    }
}
