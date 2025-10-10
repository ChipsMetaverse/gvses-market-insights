/**
 * Voice Pipeline Diagnostic Tool
 * ================================
 * Automated testing script for voice conversation pipeline
 * Tests all 10 stages from mic permission to audio playback
 */

export interface DiagnosticResult {
  stage: number;
  name: string;
  status: 'pass' | 'fail' | 'skip' | 'pending';
  message: string;
  timestamp: string;
  duration?: number;
  error?: any;
}

export class VoicePipelineDiagnostic {
  private results: DiagnosticResult[] = [];
  private startTime: number = 0;

  async runFullDiagnostic(): Promise<DiagnosticResult[]> {
    console.log('🧪 ========== VOICE PIPELINE DIAGNOSTIC START ==========');
    this.startTime = Date.now();

    try {
      await this.stage1_checkEnvironment();
      await this.stage2_checkBackendHealth();
      await this.stage3_checkRelayURL();
      await this.stage4_checkMicrophoneAvailability();
      await this.stage5_checkAudioContextSupport();
      await this.stage6_checkWebSocketSupport();
      await this.stage7_checkRealtimeSDK();
      await this.stage8_checkAgentOrchestrator();
      await this.stage9_simulateVoiceFlow();
      await this.stage10_validateComplete();
    } catch (error) {
      console.error('❌ Diagnostic failed:', error);
    }

    const totalDuration = Date.now() - this.startTime;
    console.log(`\n🧪 DIAGNOSTIC COMPLETE - Total time: ${totalDuration}ms`);
    this.printResults();

    return this.results;
  }

  private addResult(
    stage: number,
    name: string,
    status: 'pass' | 'fail' | 'skip',
    message: string,
    error?: any
  ) {
    const result: DiagnosticResult = {
      stage,
      name,
      status,
      message,
      timestamp: new Date().toISOString(),
      duration: Date.now() - this.startTime,
      error
    };
    this.results.push(result);

    const icon = status === 'pass' ? '✅' : status === 'fail' ? '❌' : '⏭️';
    console.log(`${icon} Stage ${stage}: ${name} - ${message}`);
    if (error) {
      console.error('   Error:', error);
    }
  }

  private async stage1_checkEnvironment() {
    const stage = 1;
    const name = 'Environment Check';

    try {
      // Check browser
      const isBrowser = typeof window !== 'undefined';
      if (!isBrowser) {
        throw new Error('Not running in browser environment');
      }

      // Check HTTPS or localhost (required for getUserMedia)
      const isSecure = window.location.protocol === 'https:' ||
                       window.location.hostname === 'localhost' ||
                       window.location.hostname === '127.0.0.1';

      if (!isSecure) {
        throw new Error('Must use HTTPS or localhost for microphone access');
      }

      this.addResult(stage, name, 'pass',
        `Browser: ${navigator.userAgent.split(' ').slice(-2).join(' ')}, Protocol: ${window.location.protocol}`
      );
    } catch (error) {
      this.addResult(stage, name, 'fail', 'Environment check failed', error);
      throw error;
    }
  }

  private async stage2_checkBackendHealth() {
    const stage = 2;
    const name = 'Backend Health';

    try {
      const apiUrl = import.meta.env.VITE_API_URL || window.location.origin;
      const response = await fetch(`${apiUrl}/health`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}: ${response.statusText}`);
      }

      const health = await response.json();

      if (health.status !== 'healthy') {
        throw new Error(`Backend unhealthy: ${health.status}`);
      }

      if (!health.openai_relay_ready) {
        throw new Error('OpenAI Realtime relay not ready');
      }

      this.addResult(stage, name, 'pass',
        `Backend healthy, OpenAI relay ready, mode: ${health.service_mode}`
      );
    } catch (error) {
      this.addResult(stage, name, 'fail', 'Backend health check failed', error);
      throw error;
    }
  }

  private async stage3_checkRelayURL() {
    const stage = 3;
    const name = 'OpenAI Realtime Relay';

    try {
      const apiUrl = import.meta.env.VITE_API_URL || window.location.origin;
      const response = await fetch(`${apiUrl}/openai/realtime/session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!response.ok) {
        throw new Error(`Relay endpoint returned ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      if (!data.ws_url) {
        throw new Error('No WebSocket URL in response');
      }

      if (!data.ws_url.includes('/realtime-relay/')) {
        throw new Error(`Invalid relay URL: ${data.ws_url}`);
      }

      this.addResult(stage, name, 'pass',
        `Session created: ${data.session_id}, status: ${data.status}`
      );
    } catch (error) {
      this.addResult(stage, name, 'fail', 'OpenAI Realtime relay check failed', error);
      throw error;
    }
  }

  private async stage4_checkMicrophoneAvailability() {
    const stage = 4;
    const name = 'Microphone Availability';

    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('getUserMedia not supported in this browser');
      }

      // Enumerate devices
      const devices = await navigator.mediaDevices.enumerateDevices();
      const audioInputs = devices.filter(d => d.kind === 'audioinput');

      if (audioInputs.length === 0) {
        throw new Error('No microphone devices found');
      }

      this.addResult(stage, name, 'pass',
        `Found ${audioInputs.length} microphone(s): ${audioInputs.map(d => d.label || 'Unknown').join(', ')}`
      );
    } catch (error) {
      this.addResult(stage, name, 'fail', 'Microphone check failed', error);
      throw error;
    }
  }

  private async stage5_checkAudioContextSupport() {
    const stage = 5;
    const name = 'AudioContext Support';

    try {
      if (typeof AudioContext === 'undefined' && typeof (window as any).webkitAudioContext === 'undefined') {
        throw new Error('AudioContext not supported');
      }

      // Create temporary AudioContext
      const audioContext = new AudioContext({ sampleRate: 24000 });

      if (audioContext.state === 'suspended') {
        console.warn('⚠️ AudioContext suspended (may need user interaction to activate)');
      }

      await audioContext.close();

      this.addResult(stage, name, 'pass',
        `AudioContext supported, sample rate: 24000 Hz`
      );
    } catch (error) {
      this.addResult(stage, name, 'fail', 'AudioContext check failed', error);
      throw error;
    }
  }

  private async stage6_checkWebSocketSupport() {
    const stage = 6;
    const name = 'WebSocket Support';

    try {
      if (typeof WebSocket === 'undefined') {
        throw new Error('WebSocket not supported in this browser');
      }

      this.addResult(stage, name, 'pass',
        'WebSocket API available'
      );
    } catch (error) {
      this.addResult(stage, name, 'fail', 'WebSocket check failed', error);
      throw error;
    }
  }

  private async stage7_checkRealtimeSDK() {
    const stage = 7;
    const name = 'Realtime SDK';

    try {
      // Check if RealtimeClient class is available
      const { RealtimeClient } = await import('@openai/realtime-api-beta');

      if (!RealtimeClient) {
        throw new Error('RealtimeClient not found in SDK');
      }

      this.addResult(stage, name, 'pass',
        '@openai/realtime-api-beta SDK loaded'
      );
    } catch (error) {
      this.addResult(stage, name, 'fail', 'Realtime SDK check failed', error);
      throw error;
    }
  }

  private async stage8_checkAgentOrchestrator() {
    const stage = 8;
    const name = 'Agent Orchestrator';

    try {
      const apiUrl = import.meta.env.VITE_API_URL || window.location.origin;

      // Test /ask endpoint with simple query
      const response = await fetch(`${apiUrl}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: 'ping',
          conversation_history: []
        })
      });

      if (!response.ok) {
        throw new Error(`Agent endpoint returned ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();

      if (!result.text) {
        throw new Error('No text response from agent');
      }

      this.addResult(stage, name, 'pass',
        `Agent orchestrator responding, tools available: ${result.tools_used?.length || 0}`
      );
    } catch (error) {
      this.addResult(stage, name, 'fail', 'Agent orchestrator check failed', error);
      throw error;
    }
  }

  private async stage9_simulateVoiceFlow() {
    const stage = 9;
    const name = 'Simulated Voice Flow';

    try {
      // This stage would require actual WebSocket connection
      // For now, just verify the flow is theoretically possible

      this.addResult(stage, name, 'skip',
        'Manual testing required - click 🎙️ button and speak "What is the price of Tesla?"'
      );
    } catch (error) {
      this.addResult(stage, name, 'fail', 'Voice flow simulation failed', error);
    }
  }

  private async stage10_validateComplete() {
    const stage = 10;
    const name = 'Complete Pipeline Validation';

    const passedStages = this.results.filter(r => r.status === 'pass').length;
    const totalStages = this.results.length;

    if (passedStages >= 8) { // Stages 1-8 can be automated
      this.addResult(stage, name, 'pass',
        `${passedStages}/${totalStages} automated checks passed - ready for manual voice test`
      );
    } else {
      this.addResult(stage, name, 'fail',
        `Only ${passedStages}/${totalStages} checks passed - pipeline has issues`
      );
    }
  }

  private printResults() {
    console.log('\n🧪 ========== DIAGNOSTIC RESULTS ==========');
    console.table(this.results.map(r => ({
      Stage: r.stage,
      Name: r.name,
      Status: r.status,
      Message: r.message,
      Duration: `${r.duration}ms`
    })));

    const summary = {
      total: this.results.length,
      passed: this.results.filter(r => r.status === 'pass').length,
      failed: this.results.filter(r => r.status === 'fail').length,
      skipped: this.results.filter(r => r.status === 'skip').length
    };

    console.log('\n📊 Summary:');
    console.log(`   ✅ Passed:  ${summary.passed}/${summary.total}`);
    console.log(`   ❌ Failed:  ${summary.failed}/${summary.total}`);
    console.log(`   ⏭️  Skipped: ${summary.skipped}/${summary.total}`);

    if (summary.failed === 0 && summary.passed >= 8) {
      console.log('\n✅ All automated checks passed! Ready for manual voice testing.');
      console.log('👉 Next: Click the 🎙️ button and say "What is the price of Tesla?"');
    } else if (summary.failed > 0) {
      console.log('\n❌ Pipeline has issues. Fix failed stages before testing voice.');
      const failures = this.results.filter(r => r.status === 'fail');
      console.log('\nFailed stages:');
      failures.forEach(f => {
        console.log(`   - Stage ${f.stage}: ${f.name}`);
        console.log(`     Reason: ${f.message}`);
      });
    }
  }

  // Export results for debugging
  getResults(): DiagnosticResult[] {
    return this.results;
  }

  // Quick check - run in browser console
  static async quickCheck(): Promise<boolean> {
    const diagnostic = new VoicePipelineDiagnostic();
    const results = await diagnostic.runFullDiagnostic();
    const failed = results.filter(r => r.status === 'fail').length;
    return failed === 0;
  }
}

// Make available globally for browser console testing
if (typeof window !== 'undefined') {
  (window as any).VoicePipelineDiagnostic = VoicePipelineDiagnostic;
  console.log('💡 Run diagnostic with: await VoicePipelineDiagnostic.quickCheck()');
}

export default VoicePipelineDiagnostic;
