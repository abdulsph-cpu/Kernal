using System.Threading.Channels;

namespace KernalTelemetryApp.Services;

public sealed record TelemetrySummary(
    double AverageTemperatureC,
    double AveragePowerW,
    double PeakThroughputMbps,
    double AverageErrorRate,
    int SampleCount);

public sealed class TelemetryProcessorService
{
    private readonly Channel<TelemetrySample> _queue = Channel.CreateUnbounded<TelemetrySample>(
        new UnboundedChannelOptions { SingleReader = true, SingleWriter = false });

    private TelemetrySummary _latestSummary = new(0, 0, 0, 0, 0);

    public ValueTask EnqueueAsync(TelemetrySample sample, CancellationToken cancellationToken = default)
        => _queue.Writer.WriteAsync(sample, cancellationToken);

    public async Task<TelemetrySummary> GetLatestSummaryAsync(CancellationToken cancellationToken = default)
    {
        var batch = new List<TelemetrySample>();

        while (_queue.Reader.TryRead(out var item))
        {
            batch.Add(item);
        }

        if (batch.Count == 0)
        {
            return _latestSummary;
        }

        var averageTemperature = batch.Average(x => x.TemperatureC);
        var totalPower = batch.Sum(x => x.VoltageV * x.ThroughputMbps / 1000.0);
        var peakThroughput = batch.Max(x => x.ThroughputMbps);
        var averageErrorRate = batch.Average(x => x.ErrorRate);

        _latestSummary = new TelemetrySummary(
            averageTemperature,
            totalPower / batch.Count,
            peakThroughput,
            averageErrorRate,
            batch.Count);

        return _latestSummary;
    }
}
