// Test script to verify the provider system works independently
// Run with: node test_provider_system.js

async function testProviderSystem() {
    console.log('=== Testing Provider System ===\n');
    
    // Test 1: Backend endpoint
    console.log('1. Testing backend endpoint...');
    try {
        const response = await fetch('http://localhost:8000/elevenlabs/signed-url');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('✅ Backend returned signed URL:', data.signed_url.substring(0, 100) + '...\n');
    } catch (error) {
        console.error('❌ Backend test failed:', error.message);
        console.log('Make sure backend is running on port 8000\n');
        return;
    }
    
    // Test 2: ElevenLabs API Key
    console.log('2. Checking environment variables...');
    const envVars = {
        ELEVENLABS_API_KEY: process.env.ELEVENLABS_API_KEY,
        ELEVENLABS_AGENT_ID: process.env.ELEVENLABS_AGENT_ID || 'agent_4901k2tkkq54f4mvgpndm3pgzm7g'
    };
    
    if (!envVars.ELEVENLABS_API_KEY) {
        console.log('⚠️  ELEVENLABS_API_KEY not set in environment');
    } else {
        console.log('✅ ELEVENLABS_API_KEY is set');
    }
    console.log('✅ Agent ID:', envVars.ELEVENLABS_AGENT_ID, '\n');
    
    // Test 3: Direct WebSocket connection
    console.log('3. Testing direct WebSocket connection to ElevenLabs...');
    try {
        const response = await fetch('http://localhost:8000/elevenlabs/signed-url');
        const { signed_url } = await response.json();
        
        // Note: This won't work in Node.js directly without ws package
        console.log('📝 To test WebSocket, open test_voice_connection.html in browser');
        console.log('   or install ws package: npm install ws\n');
    } catch (error) {
        console.error('❌ WebSocket test preparation failed:', error.message);
    }
    
    // Test 4: Check frontend configuration
    console.log('4. Checking frontend configuration...');
    console.log('📁 Frontend should have:');
    console.log('   - VITE_API_URL=http://localhost:8000 in .env');
    console.log('   - Provider system initialized with ElevenLabs');
    console.log('   - Voice button connected to provider.connect()\n');
    
    console.log('=== Test Complete ===');
    console.log('\nNext steps:');
    console.log('1. Open test_voice_connection.html in browser');
    console.log('2. Click buttons in order to test each component');
    console.log('3. Check browser console for detailed logs');
    console.log('4. Check Network tab for WebSocket connection');
}

// Run the test
testProviderSystem().catch(console.error);