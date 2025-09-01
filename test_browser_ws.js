#!/usr/bin/env node
/**
 * Browser-like WebSocket test using Node.js
 * Simulates browser WebSocket connection to ElevenLabs
 */

const WebSocket = require('ws');
const fetch = require('node-fetch');

const BACKEND_URL = 'http://localhost:8000';
const AGENT_ID = 'agent_4901k2tkkq54f4mvgpndm3pgzm7g';

function log(message, type = 'info') {
    const timestamp = new Date().toISOString().substring(11, 23);
    const typeEmoji = {
        'error': '❌',
        'success': '✅',
        'warning': '⚠️',
        'info': 'ℹ️'
    };
    console.log(`[${timestamp}] ${typeEmoji[type] || ''} ${message}`);
}

async function getSignedUrl() {
    log('Fetching signed URL from backend...', 'info');
    try {
        const response = await fetch(`${BACKEND_URL}/elevenlabs/signed-url?agent_id=${AGENT_ID}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        const data = await response.json();
        log(`Got signed URL: ${data.signed_url.substring(0, 100)}...`, 'success');
        return data.signed_url;
    } catch (error) {
        log(`Failed to get signed URL: ${error.message}`, 'error');
        return null;
    }
}

async function testWebSocket() {
    const signedUrl = await getSignedUrl();
    if (!signedUrl) {
        log('Cannot proceed without signed URL', 'error');
        return;
    }

    log('Creating WebSocket connection...', 'info');
    log(`Origin simulation: http://localhost:5174 (Vite frontend)`, 'info');
    
    // Create WebSocket with browser-like headers
    const ws = new WebSocket(signedUrl, {
        headers: {
            'Origin': 'http://localhost:5174',  // Simulate browser origin
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    });

    let connectionTimeout = setTimeout(() => {
        log('Connection timeout after 5 seconds', 'error');
        ws.close();
    }, 5000);

    ws.on('open', () => {
        clearTimeout(connectionTimeout);
        log('WebSocket opened!', 'success');
        log(`  State: ${ws.readyState}`, 'info');
        log(`  URL: ${ws.url.substring(0, 100)}...`, 'info');
        
        // Send initialization message
        const initMessage = {
            type: 'conversation_initiation_client_data',
            custom_llm_extra_body: {}
        };
        log(`Sending init message: ${JSON.stringify(initMessage)}`, 'info');
        ws.send(JSON.stringify(initMessage));
        log('Init message sent', 'success');
    });

    ws.on('message', (data) => {
        try {
            const parsed = JSON.parse(data.toString());
            log(`Message received: ${parsed.type}`, 'success');
            
            if (parsed.type === 'conversation_initiation_metadata') {
                log('🎉 Conversation initialized successfully!', 'success');
                log(`  Conversation ID: ${parsed.conversation_initiation_metadata_event?.conversation_id}`, 'info');
                
                // Success - close after a moment
                setTimeout(() => {
                    log('Test successful, closing connection...', 'success');
                    ws.close();
                }, 1000);
            } else if (parsed.type === 'ping') {
                log('Ping received, sending pong...', 'info');
                const pong = {
                    type: 'pong',
                    event_id: parsed.ping_event?.event_id
                };
                ws.send(JSON.stringify(pong));
                log('Pong sent', 'success');
            }
            
            log(`  Data preview: ${JSON.stringify(parsed).substring(0, 200)}...`, 'info');
        } catch (error) {
            log(`Non-JSON message: ${data}`, 'warning');
        }
    });

    ws.on('error', (error) => {
        log(`WebSocket error: ${error.message}`, 'error');
        log(`  Error code: ${error.code}`, 'error');
        log(`  Error type: ${error.constructor.name}`, 'error');
    });

    ws.on('close', (code, reason) => {
        clearTimeout(connectionTimeout);
        log(`WebSocket closed`, 'warning');
        log(`  Code: ${code}`, 'warning');
        log(`  Reason: ${reason || 'No reason provided'}`, 'warning');
        
        const closeCodeMeanings = {
            1000: 'Normal closure',
            1001: 'Going away',
            1002: 'Protocol error',
            1003: 'Unsupported data',
            1006: 'Abnormal closure (no close frame)',
            1007: 'Invalid frame payload',
            1008: 'Policy violation',
            1009: 'Message too big',
            1010: 'Mandatory extension',
            1011: 'Internal error',
            1015: 'TLS handshake failure'
        };
        
        const meaning = closeCodeMeanings[code] || 'Unknown code';
        log(`  Meaning: ${meaning}`, 'warning');
    });
}

async function main() {
    console.log('='.repeat(60));
    console.log('BROWSER-LIKE WEBSOCKET TEST');
    console.log('='.repeat(60));
    console.log('');
    
    await testWebSocket();
    
    // Keep process alive for a bit to see all messages
    setTimeout(() => {
        console.log('');
        console.log('='.repeat(60));
        console.log('TEST COMPLETE');
        console.log('='.repeat(60));
        process.exit(0);
    }, 10000);
}

main().catch(error => {
    log(`Fatal error: ${error.message}`, 'error');
    process.exit(1);
});