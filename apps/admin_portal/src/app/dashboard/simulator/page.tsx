'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useAuth } from '@/contexts/AuthContext';
import { Bot, User, Send, RefreshCw, AlertCircle } from 'lucide-react';
import api from '@/lib/api';

type Message = {
  id: string;
  sender: 'user' | 'assistant' | 'system';
  text: string;
  action?: string;
};

export default function SimulatorPage() {
  const { payload, token } = useAuth();
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', sender: 'assistant', text: 'Hello! I am your AI receptionist. How can I help you today?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [callId, setCallId] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize a unique call ID for the session
  useEffect(() => {
    startNewSession();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const startNewSession = () => {
    setCallId(crypto.randomUUID());
    setMessages([
      { id: Date.now().toString(), sender: 'assistant', text: 'Hello! I am your AI receptionist. How can I help you today?' }
    ]);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userText = input.trim();
    setInput('');
    
    // Add user message to UI immediately
    const userMessage: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: userText
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      if (!payload?.org_id) throw new Error("Missing organization ID");
      
      const response = await fetch('/api/v1/engine/internal/conversation/turn', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          call_id: callId,
          organization_id: payload.org_id,
          token: token,
          user_text: userText
        })
      });

      if (!response.ok) {
        throw new Error(`Engine returned ${response.status}`);
      }

      const data = await response.json();
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        text: data.text || `[Action: ${data.action}]`,
        action: data.action
      };
      
      setMessages(prev => [...prev, assistantMessage]);

      if (data.action === 'escalate' || data.action === 'transfer' || data.action === 'hangup') {
        const systemMessage: Message = {
          id: (Date.now() + 2).toString(),
          sender: 'system',
          text: `Call ended: ${data.action} ${data.department_id ? `(Dept: ${data.department_id})` : ''} ${data.reason ? `(Reason: ${data.reason})` : ''}`
        };
        setMessages(prev => [...prev, systemMessage]);
      }
      
    } catch (err: any) {
      console.error(err);
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        sender: 'system',
        text: 'Error connecting to Conversation Engine. Ensure it is running on port 8000.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 h-full flex flex-col">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Conversation Behavior Simulator</h1>
          <p className="mt-1 text-sm text-slate-500">
            Chat with your configured AI receptionist to test knowledge base retrieval and routing logic.
          </p>
        </div>
        <Button variant="outline" onClick={startNewSession} className="gap-2">
          <RefreshCw className="h-4 w-4" />
          Reset Call
        </Button>
      </div>

      <Card className="flex-1 flex flex-col overflow-hidden border-slate-200 shadow-md">
        <CardHeader className="bg-slate-50 border-b py-4">
          <div className="flex items-center gap-3">
            <div className="bg-blue-100 p-2 rounded-full">
              <Bot className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <CardTitle className="text-lg">AI Receptionist</CardTitle>
              <CardDescription className="text-xs mt-0.5">Session ID: {callId.slice(0, 8)}...</CardDescription>
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/50">
          {messages.map((msg) => {
            if (msg.sender === 'system') {
              return (
                <div key={msg.id} className="flex justify-center my-4">
                  <div className="bg-slate-200 text-slate-600 text-xs px-3 py-1.5 rounded-full flex items-center gap-1.5">
                    <AlertCircle className="h-3.5 w-3.5" />
                    {msg.text}
                  </div>
                </div>
              );
            }

            const isUser = msg.sender === 'user';
            
            return (
              <div key={msg.id} className={`flex gap-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
                {!isUser && (
                  <div className="flex-shrink-0 mt-1">
                    <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center border border-blue-200 shadow-sm">
                      <Bot className="h-4 w-4 text-blue-600" />
                    </div>
                  </div>
                )}
                
                <div className={`flex flex-col max-w-[75%] ${isUser ? 'items-end' : 'items-start'}`}>
                  <div 
                    className={`px-4 py-3 rounded-2xl shadow-sm ${
                      isUser 
                        ? 'bg-blue-600 text-white rounded-tr-sm' 
                        : 'bg-white border border-slate-200 text-slate-800 rounded-tl-sm'
                    }`}
                  >
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.text}</p>
                    
                    {msg.action && msg.action !== 'speak' && (
                      <div className="mt-2 text-xs font-mono bg-slate-100 text-slate-600 px-2 py-1 rounded inline-block">
                        Action: {msg.action}
                      </div>
                    )}
                  </div>
                </div>
                
                {isUser && (
                  <div className="flex-shrink-0 mt-1">
                    <div className="h-8 w-8 rounded-full bg-slate-200 flex items-center justify-center border border-slate-300 shadow-sm">
                      <User className="h-4 w-4 text-slate-600" />
                    </div>
                  </div>
                )}
              </div>
            );
          })}
          
          {isLoading && (
            <div className="flex gap-4 justify-start">
              <div className="flex-shrink-0 mt-1">
                <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center border border-blue-200">
                  <Bot className="h-4 w-4 text-blue-600" />
                </div>
              </div>
              <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
                <div className="flex gap-1.5 items-center h-5">
                  <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                  <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                  <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce"></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </CardContent>
        
        <div className="p-4 bg-white border-t border-slate-200">
          <form onSubmit={handleSend} className="flex gap-3">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="flex-1"
              disabled={isLoading}
              autoFocus
            />
            <Button type="submit" disabled={!input.trim() || isLoading} className="gap-2">
              <Send className="h-4 w-4" />
              Send
            </Button>
          </form>
        </div>
      </Card>
    </div>
  );
}
