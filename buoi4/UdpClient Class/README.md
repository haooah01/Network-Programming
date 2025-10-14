# UdpClient Class Demo

A simple C# .NET 8 console app demonstrating UDP send and receive using `UdpClient`.

## Features
- Send UDP datagrams to any IP/port
- Listen for UDP datagrams on a configurable port
- Interactive CLI for mode selection

## Usage

### Build
```sh
cd buoi4/UdpClient Class
 dotnet build
```

### Run
```sh
cd buoi4/UdpClient Class
 dotnet run
```

Follow the prompts:
- Choose mode: 1=Send, 2=Receive
- Enter target IP/port and message (Send mode)
- Enter listen port (Receive mode)

## Example
**Send:**
```
Choose mode: 1=Send, 2=Receive
1
Target IP: 127.0.0.1
Target Port: 11000
Message: Hello UDP!
Sent 'Hello UDP!' to 127.0.0.1:11000
```

**Receive:**
```
Choose mode: 1=Send, 2=Receive
2
Listen Port: 11000
Listening on UDP port 11000...
Received from 127.0.0.1: Hello UDP!
```

## License
MIT
