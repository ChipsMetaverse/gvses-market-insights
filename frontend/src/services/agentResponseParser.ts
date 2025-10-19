/**
 * Agent Response Parser
 * Converts agent JSON responses to chart command format
 */

interface AgentDrawCommand {
  intent: string;
  action?: string;
  symbol?: string;
  start?: { date?: string; time?: string; price: number };
  end?: { date?: string; time?: string; price: number };
  price?: number;
  type?: string;
  timeframe?: string;
  confidence?: string;
}

export class AgentResponseParser {
  
  /**
   * Parse agent response and extract chart commands
   */
  static parseResponse(content: string): string[] {
    const commands: string[] = [];
    
    try {
      // Try to find JSON in the response
      const jsonMatches = content.match(/\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}/g);
      
      if (jsonMatches) {
        for (const jsonString of jsonMatches) {
          try {
            const parsed = JSON.parse(jsonString);
            const command = this.convertToChartCommand(parsed);
            if (command) {
              commands.push(command);
              console.log('[AgentParser] Converted agent command:', { parsed, command });
            }
          } catch (e) {
            // Not valid JSON, continue
            console.log('[AgentParser] Invalid JSON, skipping:', jsonString);
          }
        }
      }
      
      // Also check for direct TRENDLINE/SUPPORT/RESISTANCE commands
      const directCommands = this.extractDirectCommands(content);
      commands.push(...directCommands);
      
      return commands;
    } catch (error) {
      console.error('[AgentParser] Error parsing response:', error);
      return [];
    }
  }
  
  /**
   * Convert agent JSON to chart command format
   */
  private static convertToChartCommand(parsed: AgentDrawCommand): string | null {
    if (!parsed || typeof parsed !== 'object') {
      return null;
    }
    
    const intent = parsed.intent?.toLowerCase();
    const action = parsed.action?.toLowerCase();
    
    // Check for trendline commands in both intent and action fields
    if ((intent === 'draw_trendline' || action === 'draw_trendline' || intent === 'chart_command') && parsed.start && parsed.end) {
      // Convert dates/times to timestamps
      const startDateStr = parsed.start.date || parsed.start.time;
      const endDateStr = parsed.end.date || parsed.end.time;
      
      const startTime = this.dateToTimestamp(startDateStr);
      const endTime = this.dateToTimestamp(endDateStr);
      
      if (startTime && endTime) {
        return `TRENDLINE:${parsed.start.price}:${startTime}:${parsed.end.price}:${endTime}`;
      }
    }
    
    if ((intent === 'draw_support' || action === 'draw_support_line') && parsed.price) {
      return `SUPPORT:${parsed.price}`;
    }
    
    if ((intent === 'draw_resistance' || action === 'draw_resistance_line') && parsed.price) {
      return `RESISTANCE:${parsed.price}`;
    }
    
    if (intent === 'draw_horizontal_line' && parsed.price) {
      const type = parsed.type?.toLowerCase();
      if (type === 'support') {
        return `SUPPORT:${parsed.price}`;
      }
      if (type === 'resistance') {
        return `RESISTANCE:${parsed.price}`;
      }
    }
    
    return null;
  }
  
  /**
   * Extract direct commands that are already in correct format
   */
  private static extractDirectCommands(content: string): string[] {
    const commands: string[] = [];
    
    // Match TRENDLINE:price:time:price:time
    const trendlineMatches = content.match(/TRENDLINE:\d+(?:\.\d+)?:\d+:\d+(?:\.\d+)?:\d+/g);
    if (trendlineMatches) {
      commands.push(...trendlineMatches);
    }
    
    // Match SUPPORT:price
    const supportMatches = content.match(/SUPPORT:\d+(?:\.\d+)?/g);
    if (supportMatches) {
      commands.push(...supportMatches);
    }
    
    // Match RESISTANCE:price
    const resistanceMatches = content.match(/RESISTANCE:\d+(?:\.\d+)?/g);
    if (resistanceMatches) {
      commands.push(...resistanceMatches);
    }
    
    return commands;
  }
  
  /**
   * Convert date string to Unix timestamp
   */
  private static dateToTimestamp(dateString: string): number | null {
    try {
      if (!dateString) return null;
      
      let date: Date;
      const lowerDate = dateString.toLowerCase();
      
      // Handle relative dates
      if (lowerDate === 'today') {
        date = new Date();
      } else if (lowerDate === 'yesterday') {
        date = new Date();
        date.setDate(date.getDate() - 1);
      } else if (lowerDate === 'tomorrow') {
        date = new Date();
        date.setDate(date.getDate() + 1);
      } else {
        // Try to parse as regular date
        date = new Date(dateString);
      }
      
      if (isNaN(date.getTime())) {
        // If still invalid, try to get a reasonable default
        console.warn('[AgentParser] Invalid date:', dateString, 'using current time');
        date = new Date();
      }
      
      return Math.floor(date.getTime() / 1000); // Unix timestamp in seconds
    } catch (error) {
      console.error('[AgentParser] Error converting date:', dateString, error);
      return Math.floor(Date.now() / 1000); // Return current timestamp as fallback
    }
  }
  
  /**
   * Check if response contains drawing-related content
   */
  static containsDrawingCommands(content: string): boolean {
    const drawingKeywords = [
      'trendline', 'trend line', 'draw', 'support', 'resistance', 
      'line', 'level', 'fibonacci', 'fib', 'horizontal'
    ];
    
    const lowerContent = content.toLowerCase();
    return drawingKeywords.some(keyword => lowerContent.includes(keyword)) ||
           /TRENDLINE:|SUPPORT:|RESISTANCE:/.test(content);
  }
}

// Make parser globally available for testing and debugging
declare global {
  interface Window {
    AgentResponseParser: typeof AgentResponseParser;
  }
}

if (typeof window !== 'undefined') {
  window.AgentResponseParser = AgentResponseParser;
}