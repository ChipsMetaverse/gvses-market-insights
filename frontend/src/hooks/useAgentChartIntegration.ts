/**
 * useAgentChartIntegration - Hook that connects agent voice responses to chart manipulation
 * Allows the agent to control the chart while speaking to users
 *
 * Streaming Chart Commands: Now supports listening to provider chartCommands events
 */

import { useEffect, useCallback, useRef } from 'react';
import { enhancedChartControl } from '../services/enhancedChartControl';
import type { ChatProvider } from '../providers/types';
import type { StructuredChartCommand } from '../services/agentOrchestratorService';

interface AgentResponse {
  text: string;
  indicators?: string[];
  commands?: string[];
}

interface ChartIntegrationOptions {
  provider?: ChatProvider;  // Optional provider to listen for streaming chart commands
}

export function useAgentChartIntegration(options: ChartIntegrationOptions = {}) {
  const { provider } = options;
  const processingRef = useRef(false);
  
  /**
   * Process agent's voice response and execute chart commands
   * This runs while the agent is speaking to the user
   */
  const processAgentResponse = useCallback(async (response: string, commandsFromApi?: {
    chart_commands?: string[];
    chart_commands_structured?: StructuredChartCommand[];
  }) => {
    if (processingRef.current) return;
    processingRef.current = true;
    
    try {
      // Extract and execute chart commands from agent's speech
      const legacyCommands = Array.isArray(commandsFromApi?.chart_commands)
        ? commandsFromApi?.chart_commands
        : [];
      const structuredCommands = Array.isArray(commandsFromApi?.chart_commands_structured)
        ? commandsFromApi.chart_commands_structured
        : [];

      const commands = await enhancedChartControl.processEnhancedResponse(
        response,
        legacyCommands,
        structuredCommands
      );
      
      // Log actions for debugging
      if (commands.length > 0) {
        console.log('Agent executed chart actions:', commands);
      }
      
      // Parse specific patterns in agent's speech
      const lowerResponse = response.toLowerCase();
      
      // Check for educational explanations
      if (lowerResponse.includes('let me show you') || lowerResponse.includes("i'll enable")) {
        // Agent is about to demonstrate something
        await new Promise(resolve => setTimeout(resolve, 500)); // Small delay for natural flow
      }
      
      // Check for analysis patterns
      if (lowerResponse.includes('notice how') || lowerResponse.includes('you can see')) {
        // Agent is pointing out patterns - maybe highlight them
        if (lowerResponse.includes('support')) {
          // Extract price if mentioned
          const priceMatch = lowerResponse.match(/\$?(\d+(?:\.\d+)?)/);
          if (priceMatch) {
            const price = parseFloat(priceMatch[1]);
            enhancedChartControl.highlightLevel(price, 'support');
          }
        }
      }
      
      // Handle preset demonstrations
      if (lowerResponse.includes('beginner') || lowerResponse.includes('start with basics')) {
        await enhancedChartControl.applyIndicatorPreset('basic');
      } else if (lowerResponse.includes('advanced trader') || lowerResponse.includes('pro analysis')) {
        await enhancedChartControl.applyIndicatorPreset('advanced');
      }
      
    } catch (error) {
      console.error('Error processing agent response:', error);
    } finally {
      processingRef.current = false;
    }
  }, []);

  /**
   * Streaming Chart Commands: Listen for provider chartCommands events
   * When the provider emits chart commands during streaming, process them immediately
   */
  useEffect(() => {
    if (!provider) return;

    const handleChartCommands = async (event: {
      legacy: string[];
      structured: StructuredChartCommand[];
      responseText: string;
    }) => {
      console.log('[useAgentChartIntegration] Received chart commands from streaming:', {
        legacyCount: event.legacy.length,
        structuredCount: event.structured.length,
      });

      // Process commands using existing logic
      await processAgentResponse(event.responseText, {
        chart_commands: event.legacy,
        chart_commands_structured: event.structured,
      });
    };

    provider.on('chartCommands', handleChartCommands);

    return () => {
      provider.off('chartCommands', handleChartCommands);
    };
  }, [provider, processAgentResponse]);

  /**
   * Handle agent's educational mode - walk through indicators step by step
   */
  const startEducationalWalkthrough = useCallback(async () => {
    const steps = [
      { 
        action: () => enhancedChartControl.toggleIndicator('ma20', true),
        narration: "First, let's add the 20-day moving average - this shows short-term trends"
      },
      {
        action: () => enhancedChartControl.toggleIndicator('ma50', true),
        narration: "Now the 50-day moving average for medium-term perspective"
      },
      {
        action: () => enhancedChartControl.toggleIndicator('bollinger bands', true),
        narration: "Bollinger Bands help identify when the stock is overbought or oversold"
      },
      {
        action: () => enhancedChartControl.toggleIndicator('rsi', true),
        narration: "RSI below 30 suggests oversold, above 70 suggests overbought"
      }
    ];
    
    // Execute steps with delays for natural pacing
    for (const step of steps) {
      step.action();
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    return "I've enabled key indicators for your analysis";
  }, []);
  
  /**
   * Quick analysis mode - instantly show relevant indicators
   */
  const quickAnalysis = useCallback(async (analysisType: 'bullish' | 'bearish' | 'neutral') => {
    switch (analysisType) {
      case 'bullish':
        await enhancedChartControl.applyIndicatorPreset('trend');
        return "Trend indicators show upward momentum";
        
      case 'bearish':
        await enhancedChartControl.applyIndicatorPreset('momentum');
        return "Momentum indicators reveal selling pressure";
        
      case 'neutral':
        await enhancedChartControl.applyIndicatorPreset('volatility');
        return "Volatility indicators show consolidation patterns";
        
      default:
        return "Analysis complete";
    }
  }, []);
  
  /**
   * Clear all drawings and indicators for fresh analysis
   */
  const resetChartForNewAnalysis = useCallback(() => {
    enhancedChartControl.clearDrawings();
    // Reset to default state
    if (window.enhancedChartControl) {
      window.enhancedChartControl.indicatorDispatch?.({ type: 'RESET_TO_DEFAULTS' });
    }
  }, []);
  
  /**
   * Connect to agent's message stream if available
   */
  useEffect(() => {
    // Check if we have access to the agent's message stream
    const checkForAgentMessages = () => {
      // This would connect to your ElevenLabs or OpenAI stream
      const agentElement = document.querySelector('.agent-response');
      if (agentElement) {
        // Set up observer to watch for agent responses
        const observer = new MutationObserver((mutations) => {
          mutations.forEach((mutation) => {
            if (mutation.type === 'childList') {
              const text = agentElement.textContent || '';
              if (text) {
                processAgentResponse(text);
              }
            }
          });
        });
        
        observer.observe(agentElement, { childList: true, subtree: true });
        return observer;
      }
      return null;
    };
    
    const observer = checkForAgentMessages();
    
    return () => {
      if (observer) {
        observer.disconnect();
      }
    };
  }, [processAgentResponse]);
  
  return {
    processAgentResponse,
    startEducationalWalkthrough,
    quickAnalysis,
    resetChartForNewAnalysis
  };
}

/**
 * Example agent responses that trigger chart actions:
 * 
 * "Let me show you the 50-day moving average" 
 * -> Enables MA50
 * 
 * "Notice the support level at $420"
 * -> Highlights support at $420
 * 
 * "Let's apply basic technical analysis"
 * -> Applies basic preset
 * 
 * "The RSI is showing oversold conditions"
 * -> Enables RSI if not already visible
 * 
 * "I'll enable Bollinger Bands to analyze volatility"
 * -> Enables Bollinger Bands
 */