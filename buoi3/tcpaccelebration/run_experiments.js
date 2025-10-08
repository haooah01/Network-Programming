const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { promisify } = require('util');

const mkdir = promisify(fs.mkdir);
const writeFile = promisify(fs.writeFile);

// Helper function to run a command and capture output
function runCommand(command, args = [], options = {}) {
    return new Promise((resolve, reject) => {
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
async function startServer() {
    const serverProc = spawn('node', ['server.js'], {
        stdio: ['pipe', 'pipe', 'pipe']
    });
    
    return new Promise((resolve) => {
        serverProc.stdout.on('data', (data) => {
            const output = data.toString();
            if (output.includes('Echo server on')) {
                resolve(serverProc);
            }
        });
    });
}

// Experiment 1: Nagle's Algorithm Test
async function runNagleExperiment() {
    console.log('Running Nagle experiment...');
    
    const serverProc = await startServer();
    
    // Wait a bit for server to fully start
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const runs = [];
    
    // Run with Nagle enabled
    console.log('  Testing with Nagle enabled...');
    const nagleResult = await runCommand('node', [
        'client.js',
        '--nodelay=false',
        '--n=200',
        '--ms=10',
        '--size=16',
        '--host=127.0.0.1',
        '--port=7000'
    ]);
    
    if (nagleResult.stdout) {
        runs.push(JSON.parse(nagleResult.stdout));
    }
    
    // Run with TCP_NODELAY enabled
    console.log('  Testing with TCP_NODELAY enabled...');
    const nodelayResult = await runCommand('node', [
        'client.js',
        '--nodelay=true',
        '--n=200',
        '--ms=10',
        '--size=16',
        '--host=127.0.0.1',
        '--port=7000'
    ]);
    
    if (nodelayResult.stdout) {
        runs.push(JSON.parse(nodelayResult.stdout));
    }
    
    serverProc.kill();
    
    const results = { runs };
    await writeFile('results/exp_nagle_runs.json', JSON.stringify(results, null, 2));
    
    // Create CSV for RTTs
    const csvData = ['mode,rtt_ms'];
    runs.forEach(run => {
        run.rtts_ms.forEach(rtt => {
            csvData.push(`${run.mode},${rtt}`);
        });
    });
    await writeFile('results/exp_nagle_rtts.csv', csvData.join('\n'));
    
    console.log('  Nagle experiment completed');
    return results;
}

// Experiment 2: Buffer Size Test
async function runBufferExperiment() {
    console.log('Running buffer experiment...');
    
    const serverProc = await startServer();
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const sndbufSizes = [32768, 65536, 131072, 262144, 524288];
    const rcvbufSizes = [32768, 65536, 131072, 262144, 524288];
    const payloadMb = 256;
    
    const runs = [];
    
    for (const sndbuf of sndbufSizes) {
        for (const rcvbuf of rcvbufSizes) {
            console.log(`  Testing sndbuf=${sndbuf}, rcvbuf=${rcvbuf}...`);
            
            const result = await runCommand('python', [
                'buffers.py',
                '--host=127.0.0.1',
                '--port=7000',
                `--sndbuf=${sndbuf}`,
                `--rcvbuf=${rcvbuf}`,
                `--mb=${payloadMb}`
            ]);
            
            if (result.stdout) {
                runs.push(JSON.parse(result.stdout));
            }
        }
    }
    
    serverProc.kill();
    
    const results = { runs };
    await writeFile('results/exp_buffers_runs.json', JSON.stringify(results, null, 2));
    
    // Create CSV summary
    const csvData = ['sndbuf,rcvbuf,throughput_mbps'];
    runs.forEach(run => {
        csvData.push(`${run.sndbuf},${run.rcvbuf},${run.throughput_mbps}`);
    });
    await writeFile('results/exp_buffers_summary.csv', csvData.join('\n'));
    
    console.log('  Buffer experiment completed');
    return results;
}

// Experiment 3: Keep-Alive Test (interactive)
async function runKeepAliveExperiment() {
    console.log('Running keep-alive experiment...');
    console.log('Note: This experiment requires manual interaction.');
    console.log('Start the server manually and then run: python keepalive_demo.py 127.0.0.1 7000');
    console.log('After 30-60 seconds, kill the server to see disconnect detection.');
    
    // Create placeholder results for keep-alive
    const results = {
        params: { idle: 30, intvl: 10, cnt: 5 },
        events: [
            { t: new Date().toISOString(), type: 'keepalive_configured' },
            { t: '...', type: 'disconnect_detected' }
        ]
    };
    
    await writeFile('results/exp_keepalive_events.json', JSON.stringify(results, null, 2));
    return results;
}

// Main function to run all experiments
async function runAllExperiments() {
    try {
        // Ensure results directory exists
        await mkdir('results', { recursive: true });
        
        console.log('Starting TCP Lab Experiments...\n');
        
        // Run experiments
        const expNagle = await runNagleExperiment();
        const expBuffers = await runBufferExperiment();
        const expKeepalive = await runKeepAliveExperiment();
        
        // Combine all results
        const finalResults = {
            meta: {
                author: "Tran The Hao",
                created_utc: new Date().toISOString(),
                description: "TCP latency, throughput, and keep-alive lab results"
            },
            exp_nagle: expNagle,
            exp_buffers: expBuffers,
            exp_keepalive: expKeepalive
        };
        
        await writeFile('results/results.json', JSON.stringify(finalResults, null, 2));
        
        console.log('\nAll experiments completed!');
        console.log('Results saved to results/results.json');
        console.log('\nSummary:');
        console.log(`- Nagle test: ${expNagle.runs.length} runs completed`);
        console.log(`- Buffer test: ${expBuffers.runs.length} configurations tested`);
        console.log('- Keep-alive test: Manual interaction required');
        
    } catch (error) {
        console.error('Error running experiments:', error);
    }
}

// Run if called directly
if (require.main === module) {
    runAllExperiments();
}

module.exports = { runAllExperiments, runNagleExperiment, runBufferExperiment, runKeepAliveExperiment };