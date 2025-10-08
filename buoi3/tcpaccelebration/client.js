const net = require('net');
const { performance } = require('perf_hooks');

const args = Object.fromEntries(
    process.argv.slice(2).map(kv => {
        const [k, v] = kv.replace(/^--/, '').split('=');
        return [k, v ?? true];
    })
);

const host = args.host || '127.0.0.1';
const port = parseInt(args.port || '7000', 10);
const nodelay = String(args.nodelay || 'false') === 'true';
const n = parseInt(args.n || '200', 10);
const gap = parseInt(args.ms || '10', 10);
const size = parseInt(args.size || '16', 10);

const payload = Buffer.alloc(size, 0x61);
const rtts = [];

const sock = net.createConnection({ host, port }, () => {
    sock.setNoDelay(nodelay);
    
    let i = 0;
    function sendOne() {
        if (i >= n) {
            console.log(JSON.stringify({
                mode: nodelay ? 'tcp_nodelay_on' : 'nagle_on',
                rtts_ms: rtts
            }, null, 2));
            sock.end();
            return;
        }
        
        const t0 = performance.now();
        sock.once('data', () => {
            const t1 = performance.now();
            rtts.push(t1 - t0);
            setTimeout(sendOne, gap);
        });
        
        sock.write(payload);
        i++;
    }
    
    sendOne();
});