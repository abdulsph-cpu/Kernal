namespace KernalTelemetryApp.Models;

public sealed record TelemetrySample(
    long TimestampUtcMs,
    int CoreId,
    double FrequencyMhz,
    double VoltageV,
    double TemperatureC,
    double ThroughputMbps,
    double ErrorRate);
