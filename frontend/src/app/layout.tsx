import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from '@/components/providers'
import { Toaster } from '@/components/ui/toaster'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AI Research Agent',
  description: 'An intelligent research agent that processes topics and returns structured insights',
  keywords: ['AI', 'research', 'agent', 'automation', 'data gathering'],
  authors: [{ name: 'AI Research Agent Team' }],
  viewport: 'width=device-width, initial-scale=1',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          <div className="min-h-screen bg-background">
            <header className="border-b">
              <div className="container mx-auto px-4 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                      <span className="text-primary-foreground font-bold text-sm">AI</span>
                    </div>
                    <h1 className="text-xl font-bold">Research Agent</h1>
                  </div>
                  <nav className="hidden md:flex items-center space-x-6">
                    <a href="/" className="text-sm font-medium hover:text-primary transition-colors">
                      Home
                    </a>
                    <a href="/research" className="text-sm font-medium hover:text-primary transition-colors">
                      Research
                    </a>
                    <a href="/docs" className="text-sm font-medium hover:text-primary transition-colors">
                      Docs
                    </a>
                  </nav>
                </div>
              </div>
            </header>
            <main className="container mx-auto px-4 py-8">
              {children}
            </main>
            <footer className="border-t mt-16">
              <div className="container mx-auto px-4 py-8">
                <div className="text-center text-sm text-muted-foreground">
                  <p>&copy; 2024 AI Research Agent. Built with Next.js and FastAPI.</p>
                </div>
              </div>
            </footer>
          </div>
          <Toaster />
        </Providers>
      </body>
    </html>
  )
}