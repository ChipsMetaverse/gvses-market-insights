"use client"

import React, { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Zap, 
  Database, 
  AlertTriangle,
  RefreshCw,
  Loader2,
  Activity,
  Clock,
  BarChart3
} from 'lucide-react'
import { hybridMarketDataService } from '@/services/hybridMarketDataService'
import { smartCache } from '@/services/smartCacheManager'
import { costOptimizer } from '@/services/costOptimizationService'
import { cn } from '@/lib/utils'

interface CacheAnalyticsProps {
  className?: string
  refreshInterval?: number
}

export function CacheAnalyticsDashboard({ 
  className,
  refreshInterval = 5000 // 5 seconds
}: CacheAnalyticsProps) {
  const [analytics, setAnalytics] = useState<any>(null)
  const [costReport, setCostReport] = useState<any>(null)
  const [budgetUsage, setBudgetUsage] = useState<any>(null)
  const [strategies, setStrategies] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  const loadAnalytics = async () => {
    try {
      setRefreshing(true)
      
      // Get cache analytics
      const cacheAnalytics = smartCache.getAnalytics()
      setAnalytics(cacheAnalytics)
      
      // Get cost report for current month
      const now = new Date()
      const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
      const report = costOptimizer.generateCostReport(startOfMonth, now)
      setCostReport(report)
      
      // Get budget usage
      const usage = costOptimizer.getBudgetUtilization()
      setBudgetUsage(usage)
      
      // Get optimization strategies
      const optimizationStrategies = costOptimizer.getOptimizationStrategies()
      setStrategies(optimizationStrategies)
      
      setLoading(false)
    } catch (error) {
      console.error('Error loading analytics:', error)
    } finally {
      setRefreshing(false)
    }
  }

  useEffect(() => {
    loadAnalytics()
    
    // Set up auto-refresh
    const interval = setInterval(loadAnalytics, refreshInterval)
    
    return () => clearInterval(interval)
  }, [refreshInterval])

  if (loading) {
    return (
      <Card className={className}>
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
        </CardContent>
      </Card>
    )
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 4
    }).format(amount)
  }

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num)
  }

  return (
    <div className={cn("space-y-4", className)}>
      {/* Budget Alert */}
      {budgetUsage && budgetUsage.percentage > 80 && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            API budget usage at {budgetUsage.percentage.toFixed(1)}% 
            ({formatCurrency(budgetUsage.used)} of {formatCurrency(budgetUsage.budget)})
          </AlertDescription>
        </Alert>
      )}

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Cache Hit Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {analytics ? (analytics.stats.hitRate * 100).toFixed(1) : 0}%
            </div>
            <Progress 
              value={analytics ? analytics.stats.hitRate * 100 : 0} 
              className="mt-2"
            />
            <p className="text-xs text-muted-foreground mt-1">
              {analytics ? formatNumber(analytics.stats.hits) : 0} hits / 
              {analytics ? formatNumber(analytics.stats.misses) : 0} misses
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Monthly Cost</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {budgetUsage ? formatCurrency(budgetUsage.used) : '$0'}
            </div>
            <Progress 
              value={budgetUsage ? budgetUsage.percentage : 0} 
              className="mt-2"
              color={budgetUsage && budgetUsage.percentage > 80 ? 'destructive' : 'default'}
            />
            <p className="text-xs text-muted-foreground mt-1">
              Projected: {budgetUsage ? formatCurrency(budgetUsage.projectedTotal) : '$0'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {analytics ? analytics.stats.avgResponseTime.toFixed(0) : 0}ms
            </div>
            <div className="flex items-center mt-2">
              <Activity className="w-4 h-4 text-green-500 mr-1" />
              <span className="text-xs text-muted-foreground">
                {analytics ? formatNumber(analytics.stats.entryCount) : 0} cached entries
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Cache Size</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {analytics ? (analytics.stats.cacheSize / 1024 / 1024).toFixed(1) : 0} MB
            </div>
            <div className="flex items-center mt-2">
              <Database className="w-4 h-4 text-blue-500 mr-1" />
              <span className="text-xs text-muted-foreground">
                {analytics ? formatNumber(analytics.stats.evictions) : 0} evictions
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Analytics */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Cache Analytics</CardTitle>
            <Button
              variant="ghost"
              size="icon"
              onClick={loadAnalytics}
              disabled={refreshing}
            >
              <RefreshCw className={cn("w-4 h-4", refreshing && "animate-spin")} />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="hot-keys" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="hot-keys">Hot Keys</TabsTrigger>
              <TabsTrigger value="expiring">Expiring Soon</TabsTrigger>
              <TabsTrigger value="cost-breakdown">Cost Breakdown</TabsTrigger>
              <TabsTrigger value="strategies">Optimization</TabsTrigger>
            </TabsList>

            <TabsContent value="hot-keys" className="space-y-2">
              <CardDescription>Most frequently accessed cache entries</CardDescription>
              <ScrollArea className="h-[200px]">
                {analytics?.hotKeys.map((item: any, index: number) => (
                  <div key={index} className="flex items-center justify-between py-2 px-3 hover:bg-muted/50 rounded">
                    <span className="text-sm font-medium">{item.key.replace('market-data:', '')}</span>
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary">{item.hitCount} hits</Badge>
                      <TrendingUp className="w-4 h-4 text-green-500" />
                    </div>
                  </div>
                ))}
              </ScrollArea>
            </TabsContent>

            <TabsContent value="expiring" className="space-y-2">
              <CardDescription>Cache entries expiring in the next minute</CardDescription>
              <ScrollArea className="h-[200px]">
                {analytics?.expiringKeys.map((item: any, index: number) => (
                  <div key={index} className="flex items-center justify-between py-2 px-3 hover:bg-muted/50 rounded">
                    <span className="text-sm font-medium">{item.key.replace('market-data:', '')}</span>
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4 text-orange-500" />
                      <span className="text-xs text-muted-foreground">
                        {Math.round(item.expiresIn / 1000)}s
                      </span>
                    </div>
                  </div>
                ))}
              </ScrollArea>
            </TabsContent>

            <TabsContent value="cost-breakdown" className="space-y-2">
              <CardDescription>API costs by provider</CardDescription>
              <ScrollArea className="h-[200px]">
                {costReport && Array.from(costReport.costByProvider.entries()).map(([provider, cost], index) => (
                  <div key={index} className="flex items-center justify-between py-2 px-3 hover:bg-muted/50 rounded">
                    <span className="text-sm font-medium">{provider}</span>
                    <div className="flex items-center gap-2">
                      <DollarSign className="w-4 h-4 text-green-500" />
                      <span className="text-sm">{formatCurrency(cost)}</span>
                    </div>
                  </div>
                ))}
              </ScrollArea>
              {costReport?.recommendations && costReport.recommendations.length > 0 && (
                <Alert className="mt-4">
                  <AlertDescription>
                    <strong>Recommendations:</strong>
                    <ul className="list-disc list-inside mt-2 space-y-1">
                      {costReport.recommendations.map((rec: string, index: number) => (
                        <li key={index} className="text-xs">{rec}</li>
                      ))}
                    </ul>
                  </AlertDescription>
                </Alert>
              )}
            </TabsContent>

            <TabsContent value="strategies" className="space-y-2">
              <CardDescription>Available optimization strategies</CardDescription>
              <ScrollArea className="h-[200px]">
                {strategies.map((strategy, index) => (
                  <div key={index} className="p-3 border rounded-lg mb-2">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-sm font-medium">{strategy.name}</h4>
                      <Badge variant="outline" className="text-xs">
                        Save {formatCurrency(strategy.estimatedSavings)}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground mb-2">{strategy.description}</p>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        hybridMarketDataService.applyOptimizationStrategy(strategy.name)
                        loadAnalytics()
                      }}
                    >
                      <Zap className="w-3 h-3 mr-1" />
                      Apply
                    </Button>
                  </div>
                ))}
              </ScrollArea>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Cache Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Cache Controls</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                smartCache.clearCache()
                loadAnalytics()
              }}
            >
              Clear All Cache
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                smartCache.invalidate({ tags: ['streaming'] })
                loadAnalytics()
              }}
            >
              Clear Streaming Cache
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                hybridMarketDataService.warmCache(['AAPL', 'TSLA', 'BTC', 'ETH'])
                loadAnalytics()
              }}
            >
              Warm Popular Symbols
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}