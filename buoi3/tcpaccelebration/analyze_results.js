const fs = require('fs');

// Read the results
const results = JSON.parse(fs.readFileSync('results/results.json', 'utf8'));

console.log('=== TCP Lab Results Analysis ===\n');

// Analyze Nagle experiment
console.log('1. NAGLE\'S ALGORITHM ANALYSIS');
console.log('==============================');

const nagleRuns = results.exp_nagle.runs;
const nagleOn = nagleRuns.find(r => r.mode === 'nagle_on');
const nagleOff = nagleRuns.find(r => r.mode === 'tcp_nodelay_on');

if (nagleOn && nagleOff) {
    const nagleAvg = nagleOn.rtts_ms.reduce((a, b) => a + b) / nagleOn.rtts_ms.length;
    const nodelayAvg = nagleOff.rtts_ms.reduce((a, b) => a + b) / nagleOff.rtts_ms.length;
    
    console.log(`Average RTT with Nagle enabled:  ${nagleAvg.toFixed(3)} ms`);
    console.log(`Average RTT with TCP_NODELAY:    ${nodelayAvg.toFixed(3)} ms`);
    console.log(`Latency improvement:             ${((nagleAvg - nodelayAvg) / nagleAvg * 100).toFixed(1)}%`);
    
    const nagleMax = Math.max(...nagleOn.rtts_ms);
    const nodelayMax = Math.max(...nagleOff.rtts_ms);
    console.log(`Max RTT with Nagle:              ${nagleMax.toFixed(3)} ms`);
    console.log(`Max RTT with TCP_NODELAY:        ${nodelayMax.toFixed(3)} ms`);
}

console.log('\n2. BUFFER SIZE ANALYSIS');
console.log('========================');

const bufferRuns = results.exp_buffers.runs;

// Find best performing configuration
const bestConfig = bufferRuns.reduce((best, current) => 
    current.throughput_mbps > best.throughput_mbps ? current : best
);

console.log(`Best throughput configuration:`);
console.log(`  Send Buffer: ${bestConfig.sndbuf} bytes`);
console.log(`  Recv Buffer: ${bestConfig.rcvbuf} bytes`);
console.log(`  Throughput:  ${bestConfig.throughput_mbps.toFixed(1)} Mbps`);

// Analyze by send buffer size
const bySendBuf = {};
bufferRuns.forEach(run => {
    if (!bySendBuf[run.sndbuf]) bySendBuf[run.sndbuf] = [];
    bySendBuf[run.sndbuf].push(run.throughput_mbps);
});

console.log('\nThroughput by Send Buffer Size:');
Object.keys(bySendBuf).sort((a, b) => parseInt(a) - parseInt(b)).forEach(sndbuf => {
    const avg = bySendBuf[sndbuf].reduce((a, b) => a + b) / bySendBuf[sndbuf].length;
    console.log(`  ${sndbuf.padStart(6)} bytes: ${avg.toFixed(1)} Mbps (avg)`);
});

// Analyze by receive buffer size
const byRecvBuf = {};
bufferRuns.forEach(run => {
    if (!byRecvBuf[run.rcvbuf]) byRecvBuf[run.rcvbuf] = [];
    byRecvBuf[run.rcvbuf].push(run.throughput_mbps);
});

console.log('\nThroughput by Receive Buffer Size:');
Object.keys(byRecvBuf).sort((a, b) => parseInt(a) - parseInt(b)).forEach(rcvbuf => {
    const avg = byRecvBuf[rcvbuf].reduce((a, b) => a + b) / byRecvBuf[rcvbuf].length;
    console.log(`  ${rcvbuf.padStart(6)} bytes: ${avg.toFixed(1)} Mbps (avg)`);
});

console.log('\n3. KEEP-ALIVE CONFIGURATION');
console.log('============================');

const keepalive = results.exp_keepalive;
console.log(`Idle time before probes:  ${keepalive.params.idle} seconds`);
console.log(`Probe interval:           ${keepalive.params.intvl} seconds`);
console.log(`Probe count:              ${keepalive.params.cnt} probes`);
console.log(`Total detection time:     ~${keepalive.params.idle + (keepalive.params.intvl * keepalive.params.cnt)} seconds max`);

console.log('\n4. KEY INSIGHTS');
console.log('================');
console.log('• TCP_NODELAY reduces latency by avoiding Nagle\'s algorithm delays');
console.log('• Larger socket buffers don\'t always mean better throughput');
console.log('• System and network conditions significantly affect performance');
console.log('• TCP Keep-Alive helps detect broken connections automatically');
console.log('• Small packets benefit more from TCP_NODELAY than large transfers');

console.log('\n=== Analysis Complete ===');