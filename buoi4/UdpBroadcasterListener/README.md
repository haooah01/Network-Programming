
# UdpBroadcasterListener

**Version:** 1.0.0  
**Owner:** networking-team  
**Language:** C# (.NET 8 LTS)

## Overview
UdpBroadcasterListener is a cross-platform UDP broadcaster and listener service designed for production use. It supports IPv4/IPv6, broadcast and multicast, structured logging, metrics, and robust configuration.

## Features
- Send UDP datagrams to broadcast or multicast targets
- Listen on configurable ports/adapters (IPv4/IPv6, dual mode)
- Handles packet loss, duplication, and reordering
- CLI, environment, and appsettings.json configuration
- Structured JSON logging (Serilog or built-in)
- Prometheus metrics and health endpoints
- Graceful shutdown and safe parallelism

## Quick Start
### Build
```sh
cd buoi4/UdpBroadcasterListener
dotnet build
```

### Run as Listener
```sh
dotnet run -- --mode listener --listen.port 11000
```

### Run as Broadcaster
```sh
dotnet run -- --mode broadcaster --tx.target 192.168.1.255 --tx.port 11000 --payload "hello"
```

## Configuration
- CLI options: see `Program.cs` or run with `--help`
- Environment variables: prefix `UDPAPP_`
- appsettings.json: see below

### Example appsettings.json
```json
{
  "mode": "listener",
  "listen": { "port": 11000, "ip": "0.0.0.0", "dualMode": true },
  "rx": { "parallelism": 4, "channelCapacity": 1024 },
  "obs": { "metrics": { "enabled": true }, "http": { "port": 8090 } },
  "logging": { "level": "Information" }
}
```

## Health & Metrics
- Health: `GET /healthz`, `GET /ready` (port 8090)
- Metrics: `GET /metrics` (Prometheus format)

## Architecture
- Clean Architecture, single process, async I/O
- Modules: AppHost, Config, Tx (sender), Rx (listener), Codec, Observability, Diagnostics

## Troubleshooting
- No packets received: check OS firewall and broadcast/multicast permissions
- IPv6 only: enable DualMode or use multicast ff02::1
- Duplicate messages: enable dedupe window or use msgId
- Out of order: use seq in payload and reorder in consumer

## License
MIT
