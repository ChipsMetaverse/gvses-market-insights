const WebSocket = require('ws');

console.log('Testing WebSocket proxy...');

const proxyUrl = 'ws://localhost:8000/ws/elevenlabs-proxy?agent_id=agent_4901k2tkkq54f4mvgpndm3pgzm7g';
console.log('Connecting to:', proxyUrl);

const ws = new WebSocket(proxyUrl);

ws.on('open', () => {
    console.log('✅ Connected to proxy!');
    
    const init = {
        type: 'conversation_initiation_client_data',
        custom_llm_extra_body: {}
    };
    console.log('Sending init:', JSON.stringify(init));
    ws.send(JSON.stringify(init));
});

ws.on('message', (data) => {
    try {
        const parsed = JSON.parse(data.toString());
        console.log('📥 Message type:', parsed.type);
        
        if (parsed.type === 'conversation_initiation_metadata') {
            console.log('🎉 SUCCESS! Proxy works!');
            console.log('Conversation ID:', parsed.conversation_initiation_metadata_event?.conversation_id);
            
            // Close after success
            setTimeout(() => {
                console.log('Closing...');
                ws.close();
                process.exit(0);
            }, 1000);
        }
    } catch (e) {
        console.log('Non-JSON message');
    }
});

ws.on('error', (error) => {
    console.error('❌ Error:', error.message);
    process.exit(1);
});

ws.on('close', (code, reason) => {
    console.log('Connection closed:', code, reason.toString());
});

setTimeout(() => {
    console.log('Timeout after 10 seconds');
    ws.close();
    process.exit(1);
}, 10000);