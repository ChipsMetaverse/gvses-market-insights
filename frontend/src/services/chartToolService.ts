/**
 * Chart Tool Service
 * ==================
 * Provides unified access to chart manipulation tools derived from knowledge base.
 * Integrates with voice commands and UI controls.
 */

export interface ChartTool {
  name: string
  description: string
  category: string
  topic: string
  parameters: Record<string, any>
  frontend_command: string
  knowledge_source?: Array<{
    doc_id: string
    source: string
    text_preview: string
  }>
}

export interface ChartToolsResponse {
  tools: ChartTool[]
  count: number
  categories: string[]
}

export interface ChartToolSearchResponse {
  query: string
  tools: ChartTool[]
  count: number
}

class ChartToolService {
  private baseUrl: string
  private toolsCache: Map<string, ChartTool>
  private cacheTimestamp: number | null

  constructor() {
    this.baseUrl = import.meta.env.VITE_API_URL || (typeof window !== 'undefined' ? window.location.origin : 'http://localhost:8000')
    this.toolsCache = new Map()
    this.cacheTimestamp = null
  }

  /**
   * Get all available chart tools
   */
  async getAllTools(): Promise<ChartToolsResponse> {
    // Cache for 5 minutes
    if (this.cacheTimestamp && Date.now() - this.cacheTimestamp < 5 * 60 * 1000) {
      return {
        tools: Array.from(this.toolsCache.values()),
        count: this.toolsCache.size,
        categories: Array.from(new Set(Array.from(this.toolsCache.values()).map(t => t.category)))
      }
    }

    try {
      const response = await fetch(`${this.baseUrl}/api/agent/tools/chart`)

      if (!response.ok) {
        throw new Error(`Failed to fetch chart tools: ${response.statusText}`)
      }

      const data: ChartToolsResponse = await response.json()

      // Update cache
      this.toolsCache.clear()
      data.tools.forEach(tool => {
        this.toolsCache.set(tool.name, tool)
      })
      this.cacheTimestamp = Date.now()

      return data
    } catch (error) {
      console.error('Error fetching chart tools:', error)
      throw error
    }
  }

  /**
   * Search for chart tools using semantic search
   */
  async searchTools(query: string, topK: number = 5): Promise<ChartToolSearchResponse> {
    try {
      const params = new URLSearchParams({
        query,
        top_k: topK.toString()
      })

      const response = await fetch(`${this.baseUrl}/api/agent/tools/chart/search?${params}`)

      if (!response.ok) {
        throw new Error(`Failed to search chart tools: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error searching chart tools:', error)
      throw error
    }
  }

  /**
   * Get a specific tool by name
   */
  getTool(name: string): ChartTool | undefined {
    return this.toolsCache.get(name)
  }

  /**
   * Get tools by category
   */
  getToolsByCategory(category: string): ChartTool[] {
    return Array.from(this.toolsCache.values())
      .filter(tool => tool.category === category)
  }

  /**
   * Execute a tool and return the frontend command
   */
  getCommandForTool(toolName: string, parameters: Record<string, any>): string | null {
    const tool = this.toolsCache.get(toolName)
    if (!tool) {
      console.warn(`Tool not found: ${toolName}`)
      return null
    }

    // For indicators, handle enable/disable
    if (tool.category.endsWith('_indicator')) {
      const enabled = parameters.enabled !== false
      if (enabled) {
        return tool.frontend_command
      } else {
        const indicatorName = tool.frontend_command.split(':')[1]
        return `HIDE:${indicatorName}`
      }
    }

    // For drawing tools, construct command with parameters
    if (tool.category === 'drawing_tool') {
      const paramStr = Object.entries(parameters)
        .map(([key, value]) => `${key}=${value}`)
        .join(',')
      return `${tool.frontend_command}:${paramStr}`
    }

    return tool.frontend_command
  }

  /**
   * Get indicator tools
   */
  getIndicatorTools(): ChartTool[] {
    return Array.from(this.toolsCache.values())
      .filter(tool => tool.category.includes('indicator'))
  }

  /**
   * Get drawing tools
   */
  getDrawingTools(): ChartTool[] {
    return Array.from(this.toolsCache.values())
      .filter(tool => tool.category === 'drawing_tool')
  }

  /**
   * Get knowledge context for a tool
   */
  getToolKnowledge(toolName: string): string | null {
    const tool = this.toolsCache.get(toolName)
    if (!tool || !tool.knowledge_source || tool.knowledge_source.length === 0) {
      return null
    }

    return tool.knowledge_source
      .map(source => `${source.source}: ${source.text_preview}`)
      .join('\n\n')
  }

  /**
   * Map voice command to tool execution
   * This bridges voice commands with knowledge-based tools
   */
  async mapVoiceCommandToTool(voiceCommand: string): Promise<{
    tool: ChartTool | null
    command: string | null
    parameters: Record<string, any>
  }> {
    try {
      // Use semantic search to find relevant tool
      const searchResult = await this.searchTools(voiceCommand, 1)

      if (searchResult.count === 0) {
        return { tool: null, command: null, parameters: {} }
      }

      const tool = searchResult.tools[0]

      // Infer parameters from voice command
      const parameters = this._inferParametersFromVoice(voiceCommand, tool)

      // Generate frontend command
      const command = this.getCommandForTool(tool.name, parameters)

      return { tool, command, parameters }
    } catch (error) {
      console.error('Error mapping voice command to tool:', error)
      return { tool: null, command: null, parameters: {} }
    }
  }

  /**
   * Infer tool parameters from natural language voice command
   */
  private _inferParametersFromVoice(
    voiceCommand: string,
    tool: ChartTool
  ): Record<string, any> {
    const params: Record<string, any> = {}
    const lowerCommand = voiceCommand.toLowerCase()

    // Check for enable/disable keywords for indicators
    if (tool.category.includes('indicator')) {
      if (lowerCommand.includes('show') || lowerCommand.includes('add') || lowerCommand.includes('enable')) {
        params.enabled = true
      } else if (lowerCommand.includes('hide') || lowerCommand.includes('remove') || lowerCommand.includes('disable')) {
        params.enabled = false
      } else {
        params.enabled = true  // Default to enabling
      }
    }

    // Extract numerical values for drawing tools
    if (tool.category === 'drawing_tool') {
      const numbers = lowerCommand.match(/\d+(\.\d+)?/g)
      if (numbers && tool.parameters.price) {
        params.price = parseFloat(numbers[0])
      }

      // Detect support/resistance type
      if (lowerCommand.includes('support')) {
        params.type = 'support'
      } else if (lowerCommand.includes('resistance')) {
        params.type = 'resistance'
      } else if (lowerCommand.includes('pivot')) {
        params.type = 'pivot'
      }
    }

    return params
  }

  /**
   * Initialize the service by loading all tools
   */
  async initialize(): Promise<void> {
    await this.getAllTools()
  }

  /**
   * Clear the cache
   */
  clearCache(): void {
    this.toolsCache.clear()
    this.cacheTimestamp = null
  }
}

// Singleton instance
export const chartToolService = new ChartToolService()

// Auto-initialize on module load (non-blocking)
chartToolService.initialize().catch(error => {
  console.error('Failed to initialize chart tool service:', error)
})
