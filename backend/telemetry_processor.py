import asyncio
import json
import statistics
from collections import deque
from dataclasses import dataclass
from typing import Deque


@dataclass(frozen=True)
class TelemetrySample:
    timestamp_ms: int
    core_id: int
    frequency_mhz: float
    voltage_v: float
    temperature_c: float
    throughput_mbps: float
    error_rate: float


class TelemetryProcessor:
    def __init__(self, window_size: int = 512):
        self._queue: asyncio.Queue[TelemetrySample] = asyncio.Queue(maxsize=10000)
        self._window: Deque[TelemetrySample] = deque(maxlen=window_size)

    async def ingest(self, sample: TelemetrySample) -> None:
        await self._queue.put(sample)

    async def run(self) -> None:
        while True:
            sample = await self._queue.get()
            self._window.append(sample)
            self._queue.task_done()

    def snapshot(self) -> dict:
        if not self._window:
            return {"sample_count": 0, "temperature_c": 0.0, "error_rate": 0.0}

        temperatures = [sample.temperature_c for sample in self._window]
        throughput = [sample.throughput_mbps for sample in self._window]
        error_rates = [sample.error_rate for sample in self._window]

        return {
            "sample_count": len(self._window),
            "temperature_c": round(statistics.fmean(temperatures), 2),
            "throughput_mbps": round(max(throughput), 2),
            "error_rate": round(statistics.fmean(error_rates), 6),
        }


async def generate_sample_stream(processor: TelemetryProcessor) -> None:
    import random

    while True:
        sample = TelemetrySample(
            timestamp_ms=int(asyncio.get_running_loop().time() * 1000),
            core_id=random.randint(1, 8),
            frequency_mhz=950 + random.random() * 450,
            voltage_v=0.82 + random.random() * 0.18,
            temperature_c=38 + random.random() * 30,
            throughput_mbps=1800 + random.random() * 2000,
            error_rate=random.random() * 0.05,
        )

        await processor.ingest(sample)
        await asyncio.sleep(0.1)


async def main() -> None:
    processor = TelemetryProcessor()
    worker = asyncio.create_task(processor.run())
    generator = asyncio.create_task(generate_sample_stream(processor))

    try:
        while True:
            await asyncio.sleep(1)
            print(json.dumps(processor.snapshot(), separators=(",", ":")))
    except KeyboardInterrupt:
        generator.cancel()
        worker.cancel()
        await asyncio.gather(generator, worker, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main())
