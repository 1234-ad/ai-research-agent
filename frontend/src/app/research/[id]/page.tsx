'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { ScrollArea } from '@/components/ui/scroll-area'
import { 
  ArrowLeft, 
  Clock, 
  CheckCircle, 
  XCircle, 
  Loader, 
  ExternalLink,
  Brain,
  Database,
  Search,
  FileText,
  Tag
} from 'lucide-react'
import { researchApi } from '@/lib/api'
import { formatDistanceToNow, format } from 'date-fns'
import type { ResearchRequestDetail, WorkflowLog, Article } from '@/types/research'

export default function ResearchDetailPage() {
  const params = useParams()
  const router = useRouter()
  const [wsConnected, setWsConnected] = useState(false)
  const id = parseInt(params.id as string)

  const { data: research, isLoading, error, refetch } = useQuery({
    queryKey: ['research-detail', id],
    queryFn: () => researchApi.getResearchRequest(id),
    refetchInterval: (data) => {
      // Refetch every 2 seconds if still processing
      return data?.status === 'processing' ? 2000 : false
    }
  })

  // WebSocket connection for real-time updates
  useEffect(() => {
    if (!id || !research) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${process.env.NEXT_PUBLIC_API_URL?.replace(/^https?:\/\//, '') || 'localhost:8000'}/ws/research/${id}`
    
    const ws = new WebSocket(wsUrl)
    
    ws.onopen = () => {
      setWsConnected(true)
      console.log('WebSocket connected')
    }
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      console.log('WebSocket message:', data)
      // Refetch data when we get updates
      refetch()
    }
    
    ws.onclose = () => {
      setWsConnected(false)
      console.log('WebSocket disconnected')
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setWsConnected(false)
    }

    return () => {
      ws.close()
    }
  }, [id, research, refetch])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />
      case 'processing':
        return <Loader className="h-5 w-5 text-blue-500 animate-spin" />
      default:
        return <Clock className="h-5 w-5 text-yellow-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'processing':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      default:
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
    }
  }

  const getStepIcon = (step: string) => {
    switch (step) {
      case 'input_parsing':
        return <FileText className="h-4 w-4" />
      case 'data_gathering':
        return <Search className="h-4 w-4" />
      case 'processing':
        return <Brain className="h-4 w-4" />
      case 'result_persistence':
        return <Database className="h-4 w-4" />
      default:
        return <CheckCircle className="h-4 w-4" />
    }
  }

  const getStepName = (step: string) => {
    switch (step) {
      case 'input_parsing':
        return 'Input Parsing'
      case 'data_gathering':
        return 'Data Gathering'
      case 'processing':
        return 'Processing'
      case 'result_persistence':
        return 'Result Persistence'
      case 'return_results':
        return 'Return Results'
      default:
        return step.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
        </div>
        <div className="space-y-4">
          <div className="h-8 bg-gray-200 rounded animate-pulse" />
          <div className="h-32 bg-gray-200 rounded animate-pulse" />
          <div className="h-64 bg-gray-200 rounded animate-pulse" />
        </div>
      </div>
    )
  }

  if (error || !research) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
        </div>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center text-red-600">
              <XCircle className="h-12 w-12 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">Research Request Not Found</h3>
              <p className="text-sm text-muted-foreground">
                The research request you're looking for doesn't exist or has been deleted.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-2xl font-bold">Research Request #{research.id}</h1>
            <p className="text-sm text-muted-foreground">
              Created {formatDistanceToNow(new Date(research.created_at))} ago
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {wsConnected && (
            <Badge variant="outline" className="text-green-600 border-green-200">
              Live Updates
            </Badge>
          )}
          <Badge className={getStatusColor(research.status)}>
            {getStatusIcon(research.status)}
            <span className="ml-1 capitalize">{research.status}</span>
          </Badge>
        </div>
      </div>

      {/* Topic */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Research Topic
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-lg">{research.topic}</p>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Workflow Logs */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Workflow Progress
            </CardTitle>
            <CardDescription>
              Step-by-step execution logs
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-96">
              <div className="space-y-4">
                {research.logs?.map((log: WorkflowLog, index: number) => (
                  <div key={log.id} className="flex gap-3">
                    <div className="flex flex-col items-center">
                      <div className={`p-2 rounded-full ${
                        log.status === 'completed' ? 'bg-green-100' :
                        log.status === 'failed' ? 'bg-red-100' : 'bg-blue-100'
                      }`}>
                        {getStepIcon(log.step)}
                      </div>
                      {index < (research.logs?.length || 0) - 1 && (
                        <div className="w-px h-8 bg-gray-200 mt-2" />
                      )}
                    </div>
                    <div className="flex-1 pb-4">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-medium">{getStepName(log.step)}</h4>
                        <Badge variant="outline" size="sm" className={
                          log.status === 'completed' ? 'text-green-600 border-green-200' :
                          log.status === 'failed' ? 'text-red-600 border-red-200' : 
                          'text-blue-600 border-blue-200'
                        }>
                          {log.status}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">
                        {log.message}
                      </p>
                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <span>Started: {format(new Date(log.started_at), 'HH:mm:ss')}</span>
                        {log.completed_at && (
                          <span>Completed: {format(new Date(log.completed_at), 'HH:mm:ss')}</span>
                        )}
                        {log.duration_ms && (
                          <span>Duration: {log.duration_ms}ms</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Results Summary */}
        {research.results && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5" />
                Research Summary
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2">Key Insights</h4>
                  <p className="text-sm text-muted-foreground">
                    {research.results.summary || 'Analysis in progress...'}
                  </p>
                </div>
                
                {research.results.keywords && research.results.keywords.length > 0 && (
                  <div>
                    <h4 className="font-medium mb-2 flex items-center gap-2">
                      <Tag className="h-4 w-4" />
                      Top Keywords
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {research.results.keywords.slice(0, 10).map((keyword: string, index: number) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {keyword}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                <div>
                  <h4 className="font-medium mb-2">Statistics</h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Articles Found:</span>
                      <span className="ml-2 font-medium">{research.articles?.length || 0}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Processing Time:</span>
                      <span className="ml-2 font-medium">
                        {research.completed_at && research.created_at
                          ? `${Math.round((new Date(research.completed_at).getTime() - new Date(research.created_at).getTime()) / 1000)}s`
                          : 'In progress...'
                        }
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Articles */}
      {research.articles && research.articles.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Research Articles ({research.articles.length})
            </CardTitle>
            <CardDescription>
              Top articles found and analyzed
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {research.articles.map((article: Article, index: number) => (
                <div key={article.id}>
                  <div className="space-y-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-lg mb-1">{article.title}</h4>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground mb-2">
                          <Badge variant="outline" size="sm">
                            {article.source}
                          </Badge>
                          {article.relevance_score && (
                            <span>Relevance: {article.relevance_score}%</span>
                          )}
                          {article.published_at && (
                            <span>
                              Published: {format(new Date(article.published_at), 'MMM d, yyyy')}
                            </span>
                          )}
                        </div>
                      </div>
                      {article.url && (
                        <Button variant="outline" size="sm" asChild>
                          <a href={article.url} target="_blank" rel="noopener noreferrer">
                            <ExternalLink className="h-4 w-4 mr-2" />
                            View
                          </a>
                        </Button>
                      )}
                    </div>
                    
                    {article.summary && (
                      <div>
                        <h5 className="font-medium text-sm mb-1">Summary</h5>
                        <p className="text-sm text-muted-foreground">{article.summary}</p>
                      </div>
                    )}
                    
                    {article.keywords && article.keywords.length > 0 && (
                      <div>
                        <h5 className="font-medium text-sm mb-2">Keywords</h5>
                        <div className="flex flex-wrap gap-1">
                          {article.keywords.slice(0, 8).map((keyword: string, keywordIndex: number) => (
                            <Badge key={keywordIndex} variant="secondary" className="text-xs">
                              {keyword}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {index < research.articles.length - 1 && (
                    <Separator className="mt-6" />
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Message */}
      {research.error_message && (
        <Card className="border-red-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-600">
              <XCircle className="h-5 w-5" />
              Error Details
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-red-600">{research.error_message}</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}