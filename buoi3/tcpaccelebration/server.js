const net = require('net');
const port = process.env.PORT || 7000;

const server = net.createServer((socket) => {
    socket.on('data', (data) => {
        socket.write(data);
    });
    
    socket.on('error', (error) => {
        console.error('socket error', error.message);
    });
});

server.listen(port, '0.0.0.0', () => {
    console.log('Echo server on', port);
});