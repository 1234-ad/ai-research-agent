'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Search, Brain, Database, Zap, ArrowRight, CheckCircle } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { researchApi } from '@/lib/api'

export default function HomePage() {
  const [topic, setTopic] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const router = useRouter()
  const { toast } = useToast()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!topic.trim()) {
      toast({
        title: "Error",
        description: "Please enter a research topic",
        variant: "destructive"
      })
      return
    }

    setIsSubmitting(true)
    
    try {
      const response = await researchApi.createResearch({ topic: topic.trim() })
      
      toast({
        title: "Research Started",
        description: "Your research request has been submitted successfully!",
      })
      
      // Redirect to research detail page
      router.push(`/research/${response.id}`)
      
    } catch (error) {
      console.error('Failed to submit research:', error)
      toast({
        title: "Error",
        description: "Failed to submit research request. Please try again.",
        variant: "destructive"
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const features = [
    {
      icon: Search,
      title: "Smart Data Gathering",
      description: "Automatically fetches relevant articles from Wikipedia and Hacker News"
    },
    {
      icon: Brain,
      title: "AI Processing",
      description: "Extracts key insights, summaries, and keywords from collected data"
    },
    {
      icon: Database,
      title: "Structured Results",
      description: "Organizes findings into actionable, structured research reports"
    },
    {
      icon: Zap,
      title: "Real-time Updates",
      description: "Track research progress with live workflow updates"
    }
  ]

  const workflowSteps = [
    "Input Parsing & Validation",
    "Data Gathering from APIs",
    "Content Processing & Analysis",
    "Result Persistence",
    "Structured Output Generation"
  ]

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="text-center space-y-6">
        <div className="space-y-4">
          <Badge variant="secondary" className="px-3 py-1">
            AI-Powered Research Assistant
          </Badge>
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
            Research Any Topic with
            <span className="text-primary"> AI Intelligence</span>
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Submit a research topic and get comprehensive, structured insights powered by 
            automated data gathering and AI analysis.
          </p>
        </div>

        {/* Research Form */}
        <Card className="max-w-2xl mx-auto">
          <CardHeader>
            <CardTitle>Start Your Research</CardTitle>
            <CardDescription>
              Enter any topic you'd like to research and our AI agent will gather and analyze relevant information
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="flex space-x-2">
                <Input
                  placeholder="e.g., Artificial Intelligence, Climate Change, Blockchain Technology..."
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  className="flex-1"
                  disabled={isSubmitting}
                />
                <Button type="submit" disabled={isSubmitting || !topic.trim()}>
                  {isSubmitting ? (
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <>
                      Research <ArrowRight className="ml-2 h-4 w-4" />
                    </>
                  )}
                </Button>
              </div>
              <p className="text-sm text-muted-foreground">
                Research typically takes 30-60 seconds to complete
              </p>
            </form>
          </CardContent>
        </Card>
      </section>

      {/* Features Section */}
      <section className="space-y-8">
        <div className="text-center space-y-4">
          <h2 className="text-3xl font-bold">How It Works</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Our AI research agent follows a structured 5-step workflow to deliver comprehensive insights
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <Card key={index} className="text-center">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <feature.icon className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-lg">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>{feature.description}</CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Workflow Section */}
      <section className="space-y-8">
        <div className="text-center space-y-4">
          <h2 className="text-3xl font-bold">Research Workflow</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Every research request follows our proven 5-step process for consistent, high-quality results
          </p>
        </div>

        <Card className="max-w-4xl mx-auto">
          <CardContent className="p-8">
            <div className="space-y-6">
              {workflowSteps.map((step, index) => (
                <div key={index} className="flex items-center space-x-4">
                  <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-primary-foreground font-bold text-sm">
                    {index + 1}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold">{step}</h3>
                  </div>
                  <CheckCircle className="h-5 w-5 text-green-500" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </section>

      {/* CTA Section */}
      <section className="text-center space-y-6 bg-muted/50 rounded-lg p-12">
        <h2 className="text-3xl font-bold">Ready to Start Researching?</h2>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          Join researchers, students, and professionals who use our AI agent to gather 
          comprehensive insights on any topic in minutes.
        </p>
        <div className="flex justify-center space-x-4">
          <Button size="lg" onClick={() => document.querySelector('input')?.focus()}>
            Start Research
          </Button>
          <Button variant="outline" size="lg" onClick={() => router.push('/research')}>
            View Past Research
          </Button>
        </div>
      </section>
    </div>
  )
}