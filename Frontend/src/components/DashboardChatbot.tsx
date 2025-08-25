import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { Button } from "./ui/button"
import { Input } from "./ui/input"
import { ScrollArea } from "./ui/scroll-area"
import { Badge } from "./ui/badge"
import { Send, Bot, User, Sparkles } from "lucide-react"

interface Message {
  id: number
  type: 'user' | 'bot'
  content: string
  timestamp: Date
}

const suggestedQuestions = [
  "Best performing project?",
  "Lead conversion trends?",
  "Top marketing channel?",
  "Growth opportunities?"
]

const botResponses: { [key: string]: string } = {
  "best performing project": "The E-commerce Platform project for Retail Co is performing excellently with 95% completion and a $65,000 budget. It's on track for early delivery.",
  "lead conversion trends": "Your conversion rate is 24.8% this month, down 2% from last month. However, lead quality has improved with more qualified prospects in the pipeline.",
  "top marketing channel": "Website leads are your top performer at 35% of total leads, followed by referrals at 25%. Consider investing more in SEO and content marketing.",
  "growth opportunities": "AI Integration Services show the highest opportunity score (85/100). The market demand for AI-powered solutions is growing rapidly across industries."
}

export function DashboardChatbot() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      type: 'bot',
      content: "Hello! I'm your AI business assistant. I can help analyze your dashboard data and provide actionable insights. What would you like to know?",
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState('')

  const handleSendMessage = (content: string) => {
    if (!content.trim()) return

    const userMessage: Message = {
      id: Date.now(),
      type: 'user',
      content,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])

    setTimeout(() => {
      const normalizedInput = content.toLowerCase()
      let response = "I'm analyzing your dashboard data to provide the best insights. Based on your current metrics, I can help you understand performance trends and identify opportunities for growth."
      
      for (const [key, value] of Object.entries(botResponses)) {
        if (normalizedInput.includes(key.toLowerCase())) {
          response = value
          break
        }
      }

      const botMessage: Message = {
        id: Date.now() + 1,
        type: 'bot',
        content: response,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, botMessage])
    }, 1000)

    setInputValue('')
  }

  const handleSuggestedQuestion = (question: string) => {
    handleSendMessage(question)
  }

  return (
    <Card className="h-[400px] flex flex-col border-0 shadow-sm bg-card/50 backdrop-blur-sm">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
            <Sparkles className="h-4 w-4 text-primary" />
          </div>
          <div>
            <div className="text-lg font-semibold">AI Assistant</div>
            <div className="text-sm text-muted-foreground font-normal">Ask about your business data</div>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col gap-4">
        <ScrollArea className="flex-1 pr-3">
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`flex gap-3 max-w-[85%] ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                  <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${
                    message.type === 'bot' ? 'bg-primary/10 text-primary' : 'bg-secondary text-secondary-foreground'
                  }`}>
                    {message.type === 'bot' ? <Bot className="h-3.5 w-3.5" /> : <User className="h-3.5 w-3.5" />}
                  </div>
                  <div className={`p-3 rounded-xl ${
                    message.type === 'bot' 
                      ? 'bg-muted/50 text-foreground border border-border/50' 
                      : 'bg-primary text-primary-foreground'
                  }`}>
                    <p className="text-sm leading-relaxed">{message.content}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>

        <div className="space-y-3">
          <div className="flex flex-wrap gap-2">
            {suggestedQuestions.map((question, index) => (
              <Badge
                key={index}
                variant="outline"
                className="cursor-pointer hover:bg-primary/10 hover:text-primary hover:border-primary/20 text-xs px-2 py-1 transition-colors"
                onClick={() => handleSuggestedQuestion(question)}
              >
                {question}
              </Badge>
            ))}
          </div>

          <div className="flex gap-2">
            <Input
              placeholder="Ask about your business metrics..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage(inputValue)}
              className="flex-1 bg-input-background border-border/50 focus:border-primary/50"
            />
            <Button
              size="sm"
              onClick={() => handleSendMessage(inputValue)}
              disabled={!inputValue.trim()}
              className="bg-primary hover:bg-primary/90 text-primary-foreground px-3"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}