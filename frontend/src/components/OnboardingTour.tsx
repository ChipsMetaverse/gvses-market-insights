import React, { useState, useEffect } from 'react';
import './OnboardingTour.css';

interface OnboardingTourProps {
  onComplete: () => void;
}

interface Step {
  id: number;
  title: string;
  description: string;
  target: string; // CSS selector for highlighting
  position: 'top' | 'bottom' | 'left' | 'right';
  action?: string; // Optional action text
}

const TOUR_STEPS: Step[] = [
  {
    id: 1,
    title: '👋 Welcome to GVSES Market Assistant!',
    description: 'Your AI-powered trading companion. Let me show you around in just 4 quick steps.',
    target: '.header-container',
    position: 'bottom'
  },
  {
    id: 2,
    title: '📊 Interactive Chart',
    description: 'Real-time candlestick charts with TradingView integration. Use timeframe buttons to zoom in/out. The AI can analyze patterns, draw support/resistance, and explain price action.',
    target: '.chart-container',
    position: 'left',
    action: 'Try asking: "What patterns do you see?"'
  },
  {
    id: 3,
    title: '📈 Technical Analysis Panel',
    description: 'View key trading levels with tooltips:\n• Sell High - Resistance level\n• Buy Low - Support level\n• BTD (Buy The Dip) - Strong accumulation zone\n\nPattern Detection shows AI-identified chart patterns.',
    target: '.left-panel',
    position: 'right',
    action: 'Hover over labels to learn more'
  },
  {
    id: 4,
    title: '🤖 G\'sves Trading Assistant',
    description: 'Ask anything! Examples:\n• "What\'s AAPL price?"\n• "Analyze TSLA chart"\n• "Show me tech stocks"\n• "Is there a bull flag forming?"\n\nUse voice or text - your choice!',
    target: '.chatkit-container',
    position: 'left',
    action: 'Click to start chatting'
  }
];

export const OnboardingTour: React.FC<OnboardingTourProps> = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isVisible, setIsVisible] = useState(true);
  const [highlightPosition, setHighlightPosition] = useState<DOMRect | null>(null);

  useEffect(() => {
    // Calculate highlight position for current step
    const step = TOUR_STEPS[currentStep];
    if (step) {
      const element = document.querySelector(step.target);
      if (element) {
        const rect = element.getBoundingClientRect();
        setHighlightPosition(rect);
      }
    }
  }, [currentStep]);

  const handleNext = () => {
    if (currentStep < TOUR_STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSkip = () => {
    handleComplete();
  };

  const handleComplete = () => {
    setIsVisible(false);
    // Store completion in localStorage
    localStorage.setItem('gvses_onboarding_completed', 'true');
    onComplete();
  };

  if (!isVisible) return null;

  const step = TOUR_STEPS[currentStep];
  const progress = ((currentStep + 1) / TOUR_STEPS.length) * 100;

  // Calculate tooltip position based on step position
  const getTooltipStyle = (): React.CSSProperties => {
    if (!highlightPosition) return {};

    const style: React.CSSProperties = {
      position: 'fixed',
      zIndex: 10002
    };

    switch (step.position) {
      case 'top':
        style.left = `${highlightPosition.left + highlightPosition.width / 2}px`;
        style.bottom = `${window.innerHeight - highlightPosition.top + 20}px`;
        style.transform = 'translateX(-50%)';
        break;
      case 'bottom':
        style.left = `${highlightPosition.left + highlightPosition.width / 2}px`;
        style.top = `${highlightPosition.bottom + 20}px`;
        style.transform = 'translateX(-50%)';
        break;
      case 'left':
        style.right = `${window.innerWidth - highlightPosition.left + 20}px`;
        style.top = `${highlightPosition.top + highlightPosition.height / 2}px`;
        style.transform = 'translateY(-50%)';
        break;
      case 'right':
        style.left = `${highlightPosition.right + 20}px`;
        style.top = `${highlightPosition.top + highlightPosition.height / 2}px`;
        style.transform = 'translateY(-50%)';
        break;
    }

    return style;
  };

  return (
    <>
      {/* Dark Overlay */}
      <div className="onboarding-overlay" onClick={handleSkip} />

      {/* Highlight Cutout */}
      {highlightPosition && (
        <div
          className="onboarding-highlight"
          style={{
            top: highlightPosition.top - 8,
            left: highlightPosition.left - 8,
            width: highlightPosition.width + 16,
            height: highlightPosition.height + 16
          }}
        />
      )}

      {/* Tooltip */}
      <div className="onboarding-tooltip" style={getTooltipStyle()}>
        <div className="tooltip-header">
          <h3>{step.title}</h3>
          <button className="close-btn" onClick={handleSkip} title="Skip tour">
            ✕
          </button>
        </div>

        <div className="tooltip-body">
          <p>{step.description}</p>
          {step.action && (
            <div className="tooltip-action">
              <span className="action-icon">💡</span>
              <span>{step.action}</span>
            </div>
          )}
        </div>

        <div className="tooltip-footer">
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>
          
          <div className="tooltip-controls">
            <span className="step-counter">
              {currentStep + 1} of {TOUR_STEPS.length}
            </span>
            
            <div className="button-group">
              {currentStep > 0 && (
                <button className="btn-secondary" onClick={handlePrevious}>
                  ← Back
                </button>
              )}
              <button className="btn-primary" onClick={handleNext}>
                {currentStep < TOUR_STEPS.length - 1 ? 'Next →' : 'Get Started! 🚀'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default OnboardingTour;

