/**
 * Test script demonstrating agent's ability to control technical indicators
 * while speaking to users about market analysis
 */

const agentResponses = [
  {
    speech: "Let me show you the moving averages on Tesla's chart. The 20-day moving average is trending upward.",
    expectedActions: [
      "Enable MA20 indicator",
      "Highlight trend direction"
    ]
  },
  {
    speech: "Now let's add the 50 and 200 day moving averages to see the longer term trend.",
    expectedActions: [
      "Enable MA50 indicator",
      "Enable MA200 indicator"
    ]
  },
  {
    speech: "Notice how the RSI indicator shows the stock is approaching overbought territory at 68.",
    expectedActions: [
      "Enable RSI indicator",
      "Open oscillator pane",
      "Highlight RSI level"
    ]
  },
  {
    speech: "The Bollinger Bands are squeezing, which often precedes a significant price movement.",
    expectedActions: [
      "Enable Bollinger Bands",
      "Draw attention to squeeze pattern"
    ]
  },
  {
    speech: "Let me apply advanced analysis to show you momentum indicators including MACD.",
    expectedActions: [
      "Apply advanced preset",
      "Show MACD in oscillator pane"
    ]
  },
  {
    speech: "I'll highlight the support level at $245 and resistance at $260.",
    expectedActions: [
      "Draw support line at $245",
      "Draw resistance line at $260",
      "Add price labels"
    ]
  },
  {
    speech: "Let's clear the drawings and look at a clean chart with just price action.",
    expectedActions: [
      "Clear all drawings",
      "Disable all indicators",
      "Show candlestick chart only"
    ]
  }
];

console.log("Agent Indicator Control Test Scenarios");
console.log("======================================\n");

agentResponses.forEach((scenario, index) => {
  console.log(`Scenario ${index + 1}:`);
  console.log(`Agent says: "${scenario.speech}"`);
  console.log("Expected actions:");
  scenario.expectedActions.forEach(action => {
    console.log(`  - ${action}`);
  });
  console.log("\n");
});

console.log("Implementation Notes:");
console.log("====================");
console.log("1. Agent can toggle any indicator while speaking");
console.log("2. Agent can apply analysis presets (basic, advanced, momentum, trend, volatility)");
console.log("3. Agent can draw trend lines and highlight support/resistance levels");
console.log("4. Agent can clear all drawings and reset view");
console.log("5. All actions happen in real-time as the agent speaks");
console.log("6. Users don't need to know how to use the controls - agent guides them");

console.log("\nVoice Command Examples:");
console.log("=======================");
const voiceCommands = [
  "Show me the moving averages",
  "Enable RSI indicator",
  "Add Bollinger Bands to the chart",
  "Apply momentum analysis",
  "Draw a trend line from the recent low",
  "Highlight support at 245",
  "Clear all indicators",
  "Show me MACD"
];

voiceCommands.forEach(command => {
  console.log(`• "${command}"`);
});

console.log("\nAgent Explanations:");
console.log("===================");
const explanations = {
  "MA20": "The 20-day moving average shows short-term trend direction",
  "MA50": "The 50-day moving average indicates medium-term trend",
  "MA200": "The 200-day moving average represents long-term trend",
  "Bollinger Bands": "Show volatility and potential support/resistance levels",
  "RSI": "Measures momentum - above 70 is overbought, below 30 is oversold",
  "MACD": "Shows the relationship between two moving averages, useful for trend changes",
  "Support": "Price level where buying interest typically emerges",
  "Resistance": "Price level where selling pressure typically increases"
};

Object.entries(explanations).forEach(([indicator, explanation]) => {
  console.log(`${indicator}: ${explanation}`);
});