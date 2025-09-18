/**
 * Test suite for Enhanced Chart Control and Agent Integration
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { enhancedChartControl, EnhancedChartControl } from '../services/enhancedChartControl';

// Mock the chart API
const mockChart = {
  addSeries: vi.fn(),
  removeSeries: vi.fn(),
  getSeries: vi.fn(() => [mockSeries]),
  timeScale: vi.fn(() => ({
    subscribeVisibleLogicalRangeChange: vi.fn(),
    subscribeVisibleTimeRangeChange: vi.fn()
  })),
  subscribeCrosshairMove: vi.fn()
};

const mockSeries = {
  createPriceLine: vi.fn(),
  setData: vi.fn(),
  applyOptions: vi.fn()
};

const mockDispatch = vi.fn();

describe('Enhanced Chart Control', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  
  describe('Initialization', () => {
    it('should initialize with chart and dispatch', () => {
      const control = new EnhancedChartControl();
      control.initialize(mockChart as any, mockDispatch);
      expect(control).toBeDefined();
    });
  });
  
  describe('Indicator Control', () => {
    it('should toggle MA20 indicator', () => {
      const control = new EnhancedChartControl();
      control.initialize(mockChart as any, mockDispatch);
      
      const result = control.toggleIndicator('ma20', true);
      expect(result).toBe('ma20 enabled');
      expect(mockDispatch).toHaveBeenCalledWith({
        type: 'TOGGLE_INDICATOR',
        payload: { indicator: 'movingAverages', subIndicator: 'ma20' }
      });
    });
    
    it('should handle moving average aliases', () => {
      const control = new EnhancedChartControl();
      control.initialize(mockChart as any, mockDispatch);
      
      control.toggleIndicator('moving average 50', true);
      expect(mockDispatch).toHaveBeenCalledWith({
        type: 'TOGGLE_INDICATOR',
        payload: { indicator: 'movingAverages', subIndicator: 'ma50' }
      });
    });
    
    it('should enable RSI with oscillator pane', () => {
      const control = new EnhancedChartControl();
      control.initialize(mockChart as any, mockDispatch);
      
      control.toggleIndicator('rsi', true);
      expect(mockDispatch).toHaveBeenCalledTimes(2);
      expect(mockDispatch).toHaveBeenCalledWith({
        type: 'SET_OSCILLATOR_PANE',
        payload: { show: true, type: 'rsi' }
      });
    });
  });
  
  describe('Preset Application', () => {
    it('should apply basic preset', () => {
      const control = new EnhancedChartControl();
      control.initialize(mockChart as any, mockDispatch);
      
      const result = control.applyIndicatorPreset('basic');
      expect(result).toBe('Applied basic analysis (MA20, MA50)');
      expect(mockDispatch).toHaveBeenCalledWith({ type: 'RESET_TO_DEFAULTS' });
    });
    
    it('should apply advanced preset', () => {
      const control = new EnhancedChartControl();
      control.initialize(mockChart as any, mockDispatch);
      
      const result = control.applyIndicatorPreset('advanced');
      expect(result).toContain('advanced analysis');
      expect(mockDispatch).toHaveBeenCalled();
    });
    
    it('should apply momentum preset', () => {
      const control = new EnhancedChartControl();
      control.initialize(mockChart as any, mockDispatch);
      
      const result = control.applyIndicatorPreset('momentum');
      expect(result).toBe('Applied momentum indicators (RSI, MACD)');
    });
  });
  
  describe('Level Highlighting', () => {
    it('should highlight support level', () => {
      const control = new EnhancedChartControl();
      control.initialize(mockChart as any, mockDispatch);
      
      const result = control.highlightLevel(420, 'support', 'Key Support');
      expect(result).toContain('support level at $420');
      expect(mockSeries.createPriceLine).toHaveBeenCalledWith(
        expect.objectContaining({
          price: 420,
          color: '#22c55e'
        })
      );
    });
    
    it('should highlight resistance level', () => {
      const control = new EnhancedChartControl();
      control.initialize(mockChart as any, mockDispatch);
      
      const result = control.highlightLevel(450, 'resistance');
      expect(result).toContain('resistance level at $450');
      expect(mockSeries.createPriceLine).toHaveBeenCalledWith(
        expect.objectContaining({
          price: 450,
          color: '#ef4444'
        })
      );
    });
  });
  
  describe('Command Processing', () => {
    it('should process moving average commands', async () => {
      const control = new EnhancedChartControl();
      control.initialize(mockChart as any, mockDispatch);
      
      const result = await control.processIndicatorCommand(
        'Show me the 50-day moving average'
      );
      expect(result).toContain('ma50');
      expect(mockDispatch).toHaveBeenCalled();
    });
    
    it('should process Bollinger Bands command', async () => {
      const control = new EnhancedChartControl();
      control.initialize(mockChart as any, mockDispatch);
      
      const result = await control.processIndicatorCommand(
        'Add Bollinger Bands to the chart'
      );
      expect(result).toContain('bollinger bands enabled');
    });
    
    it('should process RSI command', async () => {
      const control = new EnhancedChartControl();
      control.initialize(mockChart as any, mockDispatch);
      
      const result = await control.processIndicatorCommand(
        'Show me the RSI indicator'
      );
      expect(result).toContain('rsi enabled');
    });
    
    it('should process preset commands', async () => {
      const control = new EnhancedChartControl();
      control.initialize(mockChart as any, mockDispatch);
      
      const result = await control.processIndicatorCommand(
        'Apply basic analysis'
      );
      expect(result).toContain('Applied basic analysis');
    });
    
    it('should process level highlighting commands', async () => {
      const control = new EnhancedChartControl();
      control.initialize(mockChart as any, mockDispatch);
      
      const result = await control.processIndicatorCommand(
        'There is support at $420'
      );
      expect(result).toContain('support level at $420');
    });
  });
  
  describe('Indicator Explanations', () => {
    it('should provide MA20 explanation', () => {
      const control = new EnhancedChartControl();
      const explanation = control.getIndicatorExplanation('ma20');
      expect(explanation).toContain('short-term trend');
    });
    
    it('should provide RSI explanation', () => {
      const control = new EnhancedChartControl();
      const explanation = control.getIndicatorExplanation('rsi');
      expect(explanation).toContain('overbought');
      expect(explanation).toContain('oversold');
    });
    
    it('should provide generic explanation for unknown indicators', () => {
      const control = new EnhancedChartControl();
      const explanation = control.getIndicatorExplanation('unknown');
      expect(explanation).toContain('analyze price movements');
    });
  });
  
  describe('Drawing Management', () => {
    it('should clear all drawings', () => {
      const control = new EnhancedChartControl();
      control.initialize(mockChart as any, mockDispatch);
      
      // Add some drawings first
      control.highlightLevel(420, 'support');
      control.highlightLevel(450, 'resistance');
      
      const result = control.clearDrawings();
      expect(result).toBe('Cleared all drawings');
    });
  });
  
  describe('Enhanced Response Processing', () => {
    it('should process multiple commands in response', async () => {
      const control = new EnhancedChartControl();
      control.initialize(mockChart as any, mockDispatch);
      
      const commands = await control.processEnhancedResponse(
        'Let me show you the 50-day moving average and add RSI for momentum analysis'
      );
      
      expect(commands).toHaveLength(1);
      expect(commands[0]).toHaveProperty('result');
    });
  });
});

describe('Agent Integration', () => {
  it('should be exposed to window object', () => {
    // This would be tested in the actual browser environment
    // Here we just verify the singleton exists
    expect(enhancedChartControl).toBeDefined();
  });
  
  it('should handle agent voice commands', async () => {
    const control = new EnhancedChartControl();
    control.initialize(mockChart as any, mockDispatch);
    
    // Simulate agent saying various commands
    const agentResponses = [
      "Let me show you the 20-day moving average",
      "Notice the support level at $420",
      "I'll enable Bollinger Bands to show volatility",
      "Let's apply basic analysis to start"
    ];
    
    for (const response of agentResponses) {
      const result = await control.processIndicatorCommand(response);
      expect(result).toBeTruthy();
    }
  });
});