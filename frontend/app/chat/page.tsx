'use client'

import { useState } from 'react'
import { useChat } from 'ai/react'
import { Navigation } from '@/components/navigation'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export default function Chat() {
  const [model, setModel] = useState('gpt-3.5-turbo')
  const { messages, input, handleInputChange, handleSubmit } = useChat({
    api: '/api/chat',
    body: { model },
  })

  return (
    <div className="flex flex-col min-h-screen">
      <Navigation />
      <main className="flex-grow container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <div className="mb-4">
            <Select onValueChange={(value) => setModel(value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select a model" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
                <SelectItem value="gpt-4">GPT-4</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="border rounded-lg p-4 h-[60vh] overflow-y-auto mb-4">
            {messages.map(m => (
              <div key={m.id} className={`mb-4 ${m.role === 'user' ? 'text-right' : 'text-left'}`}>
                <span className={`inline-block p-2 rounded-lg ${m.role === 'user' ? 'bg-blue-100' : 'bg-gray-100'}`}>
                  {m.content}
                </span>
              </div>
            ))}
          </div>
          <form onSubmit={handleSubmit} className="flex gap-2">
            <Input
              value={input}
              onChange={handleInputChange}
              placeholder="Ask a question..."
            />
            <Button type="submit">Send</Button>
          </form>
        </div>
      </main>
    </div>
  )
}

