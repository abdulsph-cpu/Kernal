# Kernal
For Freedom

## Silicon telemetry dashboard

This repository contains a Blazor WebAssembly client and a Python telemetry automation layer for low-overhead silicon data processing.

### Architecture
- Browser UI: Blazor WebAssembly
- Memory model: .NET runtime garbage collector manages allocations inside the web client
- Sandbox boundary: browser isolates execution and UI state from native system access
- Telemetry processing: Python automation layer handles high-frequency stream ingestion and summarization
- Thread safety: channel-based queueing and bounded processing patterns reduce contention during concurrent updates

### Project structure
- `src/KernalTelemetryApp/` — Blazor WebAssembly application
- `backend/` — Python automation service
- `.gitignore` — standard ignore rules for .NET and Python builds

### Run locally

.NET client
```bash
dotnet restore src/KernalTelemetryApp/KernalTelemetryApp.csproj
dotnet build src/KernalTelemetryApp/KernalTelemetryApp.csproj
dotnet run --project src/KernalTelemetryApp/KernalTelemetryApp.csproj
```

Python backend
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python backend/telemetry_processor.py
```
