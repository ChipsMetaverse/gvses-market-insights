"use client"

import { useState, useEffect, useCallback } from 'react'
import { Volume2 } from 'lucide-react'
import { VoiceClient } from '@/components/voice/VoiceClient'
import { VoiceConnectionState, VoiceTranscript } from '@/types/voice'

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
  const [transcripts, setTranscripts] = useState<VoiceTranscript[]>([])
  const [connectionState, setConnectionState] = useState<VoiceConnectionState>('disconnected')
  const [aiAnalysis, setAiAnalysis] = useState<string>('')

  // Handle transcript updates from VoiceClient
  const handleTranscriptUpdate = useCallback((newTranscripts: VoiceTranscript[]) => {
    setTranscripts(newTranscripts)
    
    // Update AI analysis with the latest assistant response
    const lastAssistantMessage = newTranscripts
      .filter(t => t.role === 'assistant')
      .slice(-1)[0]
    
    if (lastAssistantMessage) {
      setAiAnalysis(lastAssistantMessage.content)
    }
  }, [])

  // Handle connection state changes
  const handleConnectionStateChange = useCallback((state: VoiceConnectionState) => {
    setConnectionState(state)
    
    // Update parent component's listening state after render
    setTimeout(() => {
      if (state === 'listening' && !isListening) {
        onVoiceToggle()
      } else if (state !== 'listening' && isListening) {
        onVoiceToggle()
      }
    }, 0)
  }, [])

  // Sync listening state with connection state
  useEffect(() => {
    if (connectionState === 'listening' && !isListening) {
      onVoiceToggle()
    } else if (connectionState !== 'listening' && isListening) {
      onVoiceToggle()
    }
  }, [connectionState, isListening, onVoiceToggle])

  // Handle errors
  const handleError = useCallback((error: string) => {
    console.error('Voice interface error:', error)
    setAiAnalysis(`Error: ${error}`)
  }, [])

  // Default AI analysis based on current symbol
  useEffect(() => {
    if (!aiAnalysis) {
      setAiAnalysis(
        `I can see a bullish flag pattern forming on the ${currentSymbol} chart. The price is consolidating near the ST level with decreasing volume, suggesting a potential breakout.`
      )
    }
  }, [currentSymbol, aiAnalysis])

  // Get connection status indicator
  const getConnectionStatus = () => {
    switch (connectionState) {
      case 'connected':
        return { text: 'Connected', color: 'text-green-600' }
      case 'connecting':
        return { text: 'Connecting...', color: 'text-yellow-600' }
      case 'listening':
        return { text: 'Listening...', color: 'text-blue-600' }
      case 'processing':
        return { text: 'Processing...', color: 'text-purple-600' }
      case 'error':
        return { text: 'Error', color: 'text-red-600' }
      default:
        return { text: 'Disconnected', color: 'text-gray-600' }
    }
  }

  const status = getConnectionStatus()

  return (
    <>
      {/* Voice Interface */}
      <div className="grid grid-cols-2 gap-6">
        <div className="text-center">
          <VoiceClient
            className="flex flex-col items-center"
            onTranscriptUpdate={handleTranscriptUpdate}
            onConnectionStateChange={handleConnectionStateChange}
            onError={handleError}
          />
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