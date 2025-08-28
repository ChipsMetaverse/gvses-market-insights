import type { Insight } from '../types'

interface ChartAnalysisProps {
  recentInsights: Insight[]
  currentSymbol: string
}

export function ChartAnalysis({ recentInsights, currentSymbol }: ChartAnalysisProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-medium text-gray-600 uppercase tracking-wide">Chart Analysis</h3>
      <div className="space-y-3">
        {recentInsights.map((insight, index) => (
          <div key={index} className="space-y-2 p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between">
              <span className="font-medium text-black">{insight.symbol}</span>
              <span className="text-xs text-gray-500">{insight.time}</span>
            </div>
            <p className="text-sm text-gray-700">{insight.insight}</p>
          </div>
        ))}
      </div>

      {/* Technical Indicators */}
      <div className="mt-6">
        <h3 className="text-sm font-medium text-gray-600 uppercase tracking-wide mb-3">Technical Levels</h3>
        <div className="space-y-2">
          <div className="flex justify-between items-center text-sm">
            <span className="text-gray-600">QE Level</span>
            <span className="font-medium text-green-600">$258.45</span>
          </div>
          <div className="flex justify-between items-center text-sm">
            <span className="text-gray-600">ST Level</span>
            <span className="font-medium text-yellow-600">$245.00</span>
          </div>
          <div className="flex justify-between items-center text-sm">
            <span className="text-gray-600">LTB Level</span>
            <span className="font-medium text-blue-600">$233.20</span>
          </div>
        </div>
      </div>

      {/* Pattern Recognition */}
      <div className="mt-6">
        <h3 className="text-sm font-medium text-gray-600 uppercase tracking-wide mb-3">Pattern Detection</h3>
        <div className="space-y-2">
          <div className="bg-green-50 border border-green-200 rounded-lg p-3">
            <p className="text-sm font-medium text-green-800">Bullish Flag</p>
            <p className="text-xs text-green-600">Confidence: 78%</p>
          </div>
        </div>
      </div>

      {/* Streaming Status */}
      <div className="mt-6">
        <h3 className="text-sm font-medium text-gray-600 uppercase tracking-wide mb-3">Real-Time Data</h3>
        <StreamingStatusIndicator 
          className="bg-white rounded-lg border border-gray-200 p-4"
          showDetails={true}
        />
      </div>
    </div>
  )
}