# 🌐 TCP Latency, Throughput, and Keep-Alive Lab

[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive hands-on laboratory for understanding TCP networking concepts including **Nagle's algorithm**, **socket buffers**, and **TCP keep-alive mechanisms**.

## 🎯 Learning Objectives

- 📊 **Measure latency impact** of Nagle's algorithm vs TCP_NODELAY
- 📈 **Analyze throughput** relationship with socket buffer sizes  
- 🔍 **Demonstrate connection health monitoring** with TCP keep-alive
- 🛠️ **Practice performance engineering** with real-world scenarios

## 📋 Prerequisites

- Node.js >= 18
- Python >= 3.10

## Files Overview

- `server.js` - Simple TCP echo server
- `client.js` - TCP client for latency testing (Nagle vs TCP_NODELAY)
- `buffers.py` - Python client for throughput testing with different buffer sizes
- `keepalive_demo.py` - Demonstration of TCP keep-alive functionality
- `run_experiments.js` - Automated test runner for all experiments

## 🚀 Quick Start

### Option 1: Run All Experiments Automatically
```bash
# Clone and setup
git clone <your-repo-url>
cd tcpaccelebration

# Run comprehensive experiments
node comprehensive_experiments.js

# Analyze results
node analyze_results.js

# Generate final report  
python final_report.py
```

### Option 2: Run Individual Experiments

#### 🧪 Experiment 1: Nagle's Algorithm vs TCP_NODELAY
```bash
# Start server in one terminal
node server_detailed.js

# In another terminal, test with different configurations
node client_detailed.js --nodelay=false --n=50 --ms=10 --size=1   # Small packets, Nagle ON
node client_detailed.js --nodelay=true --n=50 --ms=10 --size=1    # Small packets, Nagle OFF
node client_detailed.js --nodelay=false --n=50 --ms=10 --size=64  # Medium packets, Nagle ON
```

#### 📊 Experiment 2: Buffer Sizes and Throughput
```bash
# Start server
node server_detailed.js

# Test different buffer configurations
python buffers_detailed.py --sndbuf=32768 --rcvbuf=32768 --mb=32
python buffers_detailed.py --sndbuf=131072 --rcvbuf=65536 --mb=32  # Optimal config
python buffers_detailed.py --sndbuf=262144 --rcvbuf=131072 --mb=32
```

#### 🔍 Experiment 3: TCP Keep-Alive
```bash
# Start server
node server_detailed.js

# In another terminal, start keep-alive monitoring
python keepalive_detailed.py 127.0.0.1 7000

# Kill the server after 30-60 seconds to see disconnect detection
```

## 📊 Experiment Results

Our comprehensive testing revealed:

### Nagle Algorithm Impact
- **Small packets (1 byte)**: Minimal difference on localhost (~0.5ms)
- **Larger packets**: Nagle effect diminishes
- **Real-world impact**: More significant on WAN networks

### Buffer Size Optimization  
- **Best configuration**: 131KB send buffer + 65KB receive buffer = **6,180 Mbps**
- **Key insight**: Larger buffers don't always mean better performance
- **Sweet spot**: Depends on system resources and network conditions

### Keep-Alive Configuration
- **Detection time**: ~11 seconds with optimized settings
- **Production recommendation**: 30s idle + 10s interval + 5 probes
- **Platform support**: Varies across operating systems

## 📁 Project Structure

```
tcpaccelebration/
├── 🎯 Core Implementation
│   ├── server.js & server_detailed.js       # TCP echo servers
│   ├── client.js & client_detailed.js       # Latency testing clients  
│   ├── buffers.py & buffers_detailed.py     # Throughput testing
│   └── keepalive_*.py                       # Keep-alive demonstrations
├── 🤖 Automation & Analysis
│   ├── run_experiments.js                   # Original experiment runner
│   ├── comprehensive_experiments.js         # Enhanced test suite
│   ├── analyze_results.js                   # Data analysis
│   └── summary.js                          # Final reporting
├── 📚 Documentation  
│   ├── README.md                           # This file
│   ├── MO_TA_CHI_TIET.txt                 # Vietnamese documentation
│   └── package.json                       # Project configuration
└── 📊 Results
    ├── results.json                        # Combined experimental data
    ├── exp_nagle_*.json/csv               # Nagle algorithm results
    └── exp_buffers_*.json/csv             # Buffer size results
```

## 🎮 Available NPM Scripts

```bash
npm run server          # Start echo server
npm run experiments     # Run all experiments  
npm run analyze         # Detailed analysis
npm run test-keepalive  # Interactive keep-alive demo
```

## 🧪 Lab Goals & Learning Outcomes

### Technical Skills Developed
- **Socket Programming**: Practical experience with Node.js `net` module and Python `socket` library
- **Performance Engineering**: High-resolution timing, benchmarking, and statistical analysis
- **System Administration**: Process management, port handling, cross-platform compatibility
- **Automation**: Test scripting, data collection, and automated reporting

### Networking Concepts Mastered
- **Nagle Algorithm**: Understanding trade-offs between latency and bandwidth efficiency
- **Socket Buffers**: Impact on throughput and optimal configuration strategies  
- **TCP Keep-Alive**: Connection monitoring and failure detection mechanisms
- **Performance Measurement**: Real-world networking performance analysis

## 🔬 Advanced Experiments

### Custom Scenarios
```bash
# Test with different payload patterns
node client_detailed.js --nodelay=true --n=100 --ms=5 --size=1024

# Stress test with high frequency
node client_detailed.js --nodelay=false --n=1000 --ms=1 --size=8

# Large buffer throughput test
python buffers_detailed.py --sndbuf=1048576 --rcvbuf=1048576 --mb=128
```

### Production Simulation
```bash
# Simulate database connection pattern
python keepalive_detailed.py --idle=60 --intvl=30 --cnt=3

# API server latency simulation  
node client_detailed.js --nodelay=true --n=500 --ms=100 --size=512
```

## 💡 Real-World Applications

- **🎮 Game Servers**: TCP_NODELAY for real-time responsiveness
- **💾 Database Connections**: Buffer tuning for bulk operations
- **📱 Chat Applications**: Keep-alive for connection reliability
- **📡 IoT Devices**: Optimized keep-alive for battery life
- **🌐 Load Balancers**: Connection health monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-experiment`)
3. Commit your changes (`git commit -am 'Add amazing experiment'`)
4. Push to the branch (`git push origin feature/amazing-experiment`)
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

Network Programming Laboratory

## 🙏 Acknowledgments

- TCP/IP protocol specifications (RFC 793, RFC 896, RFC 1122)
- Node.js and Python communities for excellent networking APIs
- Performance engineering best practices from industry experts

---

⭐ **Star this repository if it helped you understand TCP networking!** ⭐