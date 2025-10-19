"use client"

import { useState, useEffect, useCallback } from 'react'
import { Volume2 } from 'lucide-react'

interface VoiceInterfaceProps {
  isListening: boolean
  currentSymbol: string
  onVoiceToggle: () => void
}

const voiceCommands = [
  'Show me Tesla\'s chart',
  'Switch to 4-hour timeframe',
  'Zoom in on the last week',
  'What do you see in this pattern?',
  'Get market data for AAPL',
  'Analyze the current trend',
  'What are the GVSES levels?',
  'Stream real-time price data',
]

export function VoiceInterface({ isListening, currentSymbol, onVoiceToggle }: VoiceInterfaceProps) {
  const [aiAnalysis, setAiAnalysis] = useState<string>('')

  // Default AI analysis based on current symbol
  useEffect(() => {
    setAiAnalysis(
      `I can see a bullish flag pattern forming on the ${currentSymbol} chart. The price is consolidating near the ST level with decreasing volume, suggesting a potential breakout.`
    )
  }, [currentSymbol])

  // Get connection status indicator
  const getConnectionStatus = () => {
    if (isListening) {
      return { text: 'Listening...', color: 'text-blue-600' }
    }
    return { text: 'Disconnected', color: 'text-gray-600' }
  }

  const status = getConnectionStatus()

  return (
    <>
      {/* Voice Interface */}
      <div className="grid grid-cols-2 gap-6">
        <div className="text-center">
          <div className="flex flex-col items-center">
            <button
              onClick={onVoiceToggle}
              className={`w-16 h-16 rounded-full flex items-center justify-center border-2 transition-colors ${
                isListening 
                  ? 'bg-red-500 border-red-500 text-white' 
                  : 'bg-gray-100 border-gray-300 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <Volume2 className="w-6 h-6" />
            </button>
          </div>
          <div className="mt-3">
            <h3 className="text-lg font-light text-black">Control the chart</h3>
            <p className={`text-sm mt-1 ${status.color}`}>
              {status.text}
            </p>
          </div>
        </div>

        <div>
          <div className="flex items-center space-x-2 mb-3">
            <Volume2 className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-600">AI Analysis</span>
          </div>
          <div className="bg-gray-50 rounded-lg px-4 py-3 max-h-40 overflow-y-auto">
            <p className="text-sm text-gray-900 leading-relaxed">
              {aiAnalysis}
            </p>
          </div>
        </div>
      </div>

      {/* Voice Commands */}
      <div>
        <h4 className="text-sm font-medium text-gray-600 mb-3">Try these voice commands:</h4>
        <div className="grid grid-cols-2 gap-2">
          {voiceCommands.map((command, index) => (
            <div
              key={index}
              className="bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 cursor-pointer hover:bg-gray-50"
            >
              "{command}"
            </div>
          ))}
        </div>
      </div>
    </>
  )
}