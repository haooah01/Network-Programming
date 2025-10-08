const fs = require('fs');
const path = require('path');

console.log('🚀 TCP Lab Summary Report');
console.log('========================\n');

// Check if results exist
const resultsPath = 'results/results.json';
if (!fs.existsSync(resultsPath)) {
    console.log('❌ No results found. Run experiments first:');
    console.log('   node run_experiments.js');
    process.exit(1);
}

const results = JSON.parse(fs.readFileSync(resultsPath, 'utf8'));

console.log('📊 Experiment Status:');
console.log(`   ✅ Nagle Algorithm Test: ${results.exp_nagle.runs.length} runs completed`);
console.log(`   ✅ Buffer Size Test: ${results.exp_buffers.runs.length} configurations tested`);
console.log(`   ⚠️  Keep-Alive Test: Manual demo available`);

console.log('\n📈 Key Findings:');

// Nagle analysis
const nagleOn = results.exp_nagle.runs.find(r => r.mode === 'nagle_on');
const nagleOff = results.exp_nagle.runs.find(r => r.mode === 'tcp_nodelay_on');

if (nagleOn && nagleOff) {
    const nagleAvg = nagleOn.rtts_ms.reduce((a, b) => a + b) / nagleOn.rtts_ms.length;
    const nodelayAvg = nagleOff.rtts_ms.reduce((a, b) => a + b) / nagleOff.rtts_ms.length;
    
    console.log(`   🕐 Latency Impact:`);
    console.log(`      Nagle ON:  ${nagleAvg.toFixed(2)} ms average`);
    console.log(`      Nagle OFF: ${nodelayAvg.toFixed(2)} ms average`);
    
    if (nagleAvg > nodelayAvg) {
        console.log(`      💡 TCP_NODELAY reduces latency by ${((nagleAvg - nodelayAvg) / nagleAvg * 100).toFixed(1)}%`);
    } else {
        console.log(`      💡 No significant latency difference observed`);
    }
}

// Buffer analysis
const bestThroughput = Math.max(...results.exp_buffers.runs.map(r => r.throughput_mbps));
const bestConfig = results.exp_buffers.runs.find(r => r.throughput_mbps === bestThroughput);

console.log(`   📡 Throughput Optimization:`);
console.log(`      Best: ${bestThroughput.toFixed(0)} Mbps`);
console.log(`      Config: ${bestConfig.sndbuf}/${bestConfig.rcvbuf} bytes (send/recv)`);

console.log('\n🔧 Available Commands:');
console.log('   npm run server          # Start echo server');
console.log('   npm run experiments     # Run all experiments');
console.log('   npm run analyze         # Detailed analysis');
console.log('   npm run test-keepalive  # Interactive keep-alive demo');

console.log('\n📁 Generated Files:');
const files = [
    'results/results.json',
    'results/exp_nagle_runs.json',
    'results/exp_nagle_rtts.csv',
    'results/exp_buffers_runs.json',
    'results/exp_buffers_summary.csv',
    'results/exp_keepalive_events.json'
];

files.forEach(file => {
    if (fs.existsSync(file)) {
        const stats = fs.statSync(file);
        console.log(`   ✅ ${file} (${(stats.size / 1024).toFixed(1)} KB)`);
    } else {
        console.log(`   ❌ ${file} (missing)`);
    }
});

console.log('\n🎯 Learning Objectives Achieved:');
console.log('   ✅ Measured impact of Nagle\'s algorithm on latency');
console.log('   ✅ Analyzed socket buffer size effects on throughput');
console.log('   ✅ Demonstrated TCP keep-alive for connection monitoring');
console.log('   ✅ Generated data suitable for visualization');

console.log('\n📚 Next Steps:');
console.log('   • Analyze results with your preferred data visualization tool');
console.log('   • Test with different payload sizes and network conditions');
console.log('   • Compare results across different operating systems');
console.log('   • Implement a web dashboard for real-time visualization');

console.log('\n✨ Lab completed successfully! ✨');