// =============================================================================
// COMPREHENSIVE TCP EXPERIMENT RUNNER
// Script để chạy và so sánh tất cả các kịch bản khác nhau
// =============================================================================

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

class TCPExperimentRunner {
    constructor() {
        this.results = {};
        this.serverProcess = null;
    }

    // Utility function to run command and capture output
    async runCommand(command, args = [], options = {}) {
        return new Promise((resolve, reject) => {
            console.log(`🔧 Executing: ${command} ${args.join(' ')}`);
            
            const proc = spawn(command, args, {
                stdio: ['pipe', 'pipe', 'pipe'],
                shell: true,
                ...options
            });
            
            let stdout = '';
            let stderr = '';
            
            proc.stdout.on('data', (data) => {
                stdout += data.toString();
            });
            
            proc.stderr.on('data', (data) => {
                stderr += data.toString();
            });
            
            proc.on('close', (code) => {
                resolve({ code, stdout, stderr });
            });
            
            proc.on('error', reject);
        });
    }

    // Start server and wait for it to be ready
    async startServer() {
        console.log('🚀 Starting detailed server...');
        
        this.serverProcess = spawn('node', ['server_detailed.js'], {
            stdio: ['pipe', 'pipe', 'pipe']
        });
        
        return new Promise((resolve) => {
            this.serverProcess.stdout.on('data', (data) => {
                const output = data.toString();
                console.log(`[SERVER] ${output.trim()}`);
                if (output.includes('Echo server đang chạy')) {
                    resolve();
                }
            });
            
            this.serverProcess.stderr.on('data', (data) => {
                console.log(`[SERVER ERROR] ${data.toString().trim()}`);
            });
        });
    }

    // Stop server
    stopServer() {
        if (this.serverProcess) {
            console.log('🛑 Stopping server...');
            this.serverProcess.kill();
            this.serverProcess = null;
        }
    }

    // Experiment 1: Nagle Algorithm Impact
    async testNagleImpact() {
        console.log('\n' + '='.repeat(60));
        console.log('🧪 THÍ NGHIỆM 1: NAGLE ALGORITHM vs TCP_NODELAY');
        console.log('='.repeat(60));

        const scenarios = [
            {
                name: 'Nagle Enabled (Small Packets)',
                args: ['--nodelay=false', '--n=10', '--ms=50', '--size=1']
            },
            {
                name: 'TCP_NODELAY Enabled (Small Packets)', 
                args: ['--nodelay=true', '--n=10', '--ms=50', '--size=1']
            },
            {
                name: 'Nagle Enabled (Medium Packets)',
                args: ['--nodelay=false', '--n=10', '--ms=50', '--size=64']
            },
            {
                name: 'TCP_NODELAY Enabled (Medium Packets)',
                args: ['--nodelay=true', '--n=10', '--ms=50', '--size=64']
            }
        ];

        this.results.nagle_tests = [];

        for (const scenario of scenarios) {
            console.log(`\n📊 Testing: ${scenario.name}`);
            
            const result = await this.runCommand('node', ['client_detailed.js', ...scenario.args]);
            
            if (result.code === 0 && result.stdout.includes('"rtts_ms"')) {
                try {
                    // Extract JSON from output
                    const jsonMatch = result.stdout.match(/\{[\s\S]*"rtts_ms"[\s\S]*\}/);
                    if (jsonMatch) {
                        const data = JSON.parse(jsonMatch[0]);
                        this.results.nagle_tests.push({
                            scenario: scenario.name,
                            ...data
                        });
                        console.log(`   ✅ RTT trung bình: ${data.stats.avg.toFixed(3)}ms`);
                    }
                } catch (e) {
                    console.log(`   ❌ Không thể parse JSON: ${e.message}`);
                }
            } else {
                console.log(`   ❌ Test failed: ${result.stderr}`);
            }
            
            // Wait between tests
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
    }

    // Experiment 2: Buffer Size Impact  
    async testBufferImpact() {
        console.log('\n' + '='.repeat(60));
        console.log('🧪 THÍ NGHIỆM 2: SOCKET BUFFER SIZE vs THROUGHPUT');
        console.log('='.repeat(60));

        const bufferConfigs = [
            { sndbuf: 16384, rcvbuf: 16384, name: 'Small Buffers (16KB)' },
            { sndbuf: 65536, rcvbuf: 65536, name: 'Default Buffers (64KB)' },
            { sndbuf: 131072, rcvbuf: 65536, name: 'Large Send Buffer (128KB/64KB)' },
            { sndbuf: 262144, rcvbuf: 131072, name: 'Very Large Buffers (256KB/128KB)' }
        ];

        this.results.buffer_tests = [];

        for (const config of bufferConfigs) {
            console.log(`\n📊 Testing: ${config.name}`);
            
            const args = [
                'buffers_detailed.py',
                `--sndbuf=${config.sndbuf}`,
                `--rcvbuf=${config.rcvbuf}`,
                '--mb=16'  // 16MB untuk test nhanh
            ];
            
            const result = await this.runCommand('python', args);
            
            if (result.code === 0 && result.stdout.includes('throughput_mbps')) {
                try {
                    // Extract JSON from output
                    const jsonMatch = result.stdout.match(/\{[\s\S]*"efficiency_percent"[\s\S]*\}/);
                    if (jsonMatch) {
                        const data = JSON.parse(jsonMatch[0]);
                        this.results.buffer_tests.push({
                            scenario: config.name,
                            ...data
                        });
                        console.log(`   ✅ Throughput: ${data.throughput_mbps.toFixed(1)} Mbps`);
                        console.log(`   📊 Efficiency: ${data.efficiency_percent.toFixed(1)}%`);
                    }
                } catch (e) {
                    console.log(`   ❌ Không thể parse JSON: ${e.message}`);
                }
            } else {
                console.log(`   ❌ Test failed: ${result.stderr}`);
            }
            
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
    }

    // Generate comprehensive report
    generateReport() {
        console.log('\n' + '='.repeat(80));
        console.log('📊 BÁO CÁO TỔNG HỢP KẾT QUẢ THÍ NGHIỆM');
        console.log('='.repeat(80));

        // Nagle Analysis
        if (this.results.nagle_tests && this.results.nagle_tests.length > 0) {
            console.log('\n🔍 PHÂN TÍCH NAGLE ALGORITHM:');
            console.log('-'.repeat(40));
            
            const nagleEnabled = this.results.nagle_tests.filter(t => t.config.nodelay === false);
            const nagleDisabled = this.results.nagle_tests.filter(t => t.config.nodelay === true);
            
            nagleEnabled.forEach(test => {
                console.log(`📈 ${test.scenario}:`);
                console.log(`   RTT: ${test.stats.avg.toFixed(3)}ms ± ${(test.stats.max - test.stats.min).toFixed(3)}ms`);
            });
            
            nagleDisabled.forEach(test => {
                console.log(`📈 ${test.scenario}:`);
                console.log(`   RTT: ${test.stats.avg.toFixed(3)}ms ± ${(test.stats.max - test.stats.min).toFixed(3)}ms`);
            });
            
            // Compare small packet performance
            const smallNagle = nagleEnabled.find(t => t.config.size === 1);
            const smallNodelay = nagleDisabled.find(t => t.config.size === 1);
            
            if (smallNagle && smallNodelay) {
                const improvement = ((smallNagle.stats.avg - smallNodelay.stats.avg) / smallNagle.stats.avg * 100);
                console.log(`\n💡 Với packets 1 byte:`);
                console.log(`   TCP_NODELAY ${improvement > 0 ? 'nhanh hơn' : 'chậm hơn'} ${Math.abs(improvement).toFixed(1)}%`);
            }
        }

        // Buffer Analysis
        if (this.results.buffer_tests && this.results.buffer_tests.length > 0) {
            console.log('\n🔍 PHÂN TÍCH SOCKET BUFFERS:');
            console.log('-'.repeat(40));
            
            let bestThroughput = 0;
            let bestConfig = null;
            
            this.results.buffer_tests.forEach(test => {
                console.log(`📈 ${test.scenario}:`);
                console.log(`   Throughput: ${test.throughput_mbps.toFixed(1)} Mbps`);
                console.log(`   Efficiency: ${test.efficiency_percent.toFixed(1)}%`);
                console.log(`   Buffers: ${test.sndbuf/1024}KB send / ${test.rcvbuf/1024}KB recv`);
                
                if (test.throughput_mbps > bestThroughput) {
                    bestThroughput = test.throughput_mbps;
                    bestConfig = test;
                }
            });
            
            if (bestConfig) {
                console.log(`\n🏆 CẤU HÌNH TỐI ƯU:`);
                console.log(`   ${bestConfig.scenario}`);
                console.log(`   Throughput: ${bestConfig.throughput_mbps.toFixed(1)} Mbps`);
                console.log(`   Send Buffer: ${bestConfig.sndbuf/1024}KB`);
                console.log(`   Recv Buffer: ${bestConfig.rcvbuf/1024}KB`);
            }
        }

        // Key Insights
        console.log('\n💡 NHỮNG HIỂU BIẾT QUAN TRỌNG:');
        console.log('-'.repeat(40));
        console.log('• Nagle algorithm có tác động khác nhau tùy vào kích thước packet');
        console.log('• TCP_NODELAY quan trọng cho real-time applications'); 
        console.log('• Buffer size cần được tuning theo workload cụ thể');
        console.log('• Localhost performance khác với WAN network');
        console.log('• Cần cân bằng giữa latency và throughput');

        // Save detailed results
        const reportFile = 'results/comprehensive_experiment_report.json';
        fs.writeFileSync(reportFile, JSON.stringify({
            timestamp: new Date().toISOString(),
            environment: {
                platform: process.platform,
                nodeVersion: process.version
            },
            results: this.results
        }, null, 2));
        
        console.log(`\n💾 Chi tiết đã được lưu vào: ${reportFile}`);
    }

    // Main experiment runner
    async runAllExperiments() {
        try {
            console.log('🎯 STARTING COMPREHENSIVE TCP EXPERIMENTS');
            console.log('=' .repeat(80));
            
            // Start server
            await this.startServer();
            await new Promise(resolve => setTimeout(resolve, 2000)); // Wait for server to stabilize
            
            // Run experiments
            await this.testNagleImpact();
            await this.testBufferImpact();
            
            // Generate report
            this.generateReport();
            
        } catch (error) {
            console.error('❌ Experiment failed:', error);
        } finally {
            this.stopServer();
        }
    }
}

// Run experiments if called directly
if (require.main === module) {
    const runner = new TCPExperimentRunner();
    runner.runAllExperiments().then(() => {
        console.log('\n✅ All experiments completed!');
        process.exit(0);
    }).catch(error => {
        console.error('❌ Fatal error:', error);
        process.exit(1);
    });
}

module.exports = TCPExperimentRunner;